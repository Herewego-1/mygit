"""
S02c-BreakingNews 노드 추가:
- Finnhub 뉴스 API (general/forex/crypto/merger) - 이미 키 있음
- Reuters RSS, CNBC RSS, MarketWatch RSS (무료, 키 불필요)
- 최근 18시간 필터 (새벽 이슈까지 커버)
- 중요도 키워드 스코어링 → 상위 30건 추출
- S05-Claude에 breakingNewsText로 전달
"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# ─── 1. S02c-BreakingNews 노드 코드 ───────────────────────────────────────
news_code = r"""// S02c-BreakingNews: 글로벌 실시간 금융 뉴스 수집 (최근 18시간 — 새벽 이슈 포함)
const prev = $input.first().json;
const FINNHUB_KEY = $env.FINNHUB_API_KEY;

const headlines = [];
const errors = [];

// 최근 18시간 컷오프 (한국 기준 새벽 발생 이슈까지 커버)
const cutoffTime = Date.now() - (18 * 60 * 60 * 1000);

// ── 1. Finnhub 뉴스 API ──────────────────────────────────────────────────
if (FINNHUB_KEY && !FINNHUB_KEY.includes('여기에')) {
  for (const cat of ['general', 'forex', 'crypto', 'merger']) {
    try {
      const resp = await this.helpers.httpRequest({
        method: 'GET',
        url: `https://finnhub.io/api/v1/news?category=${cat}&token=${FINNHUB_KEY}`,
        headers: { 'User-Agent': 'Mozilla/5.0' },
        timeout: 12000
      });
      const news = typeof resp === 'string' ? JSON.parse(resp) : resp;
      for (const item of (Array.isArray(news) ? news : []).slice(0, 40)) {
        const ts = (item.datetime || 0) * 1000;
        if (ts >= cutoffTime) {
          headlines.push({
            source:   item.source || 'Finnhub',
            category: cat,
            headline: item.headline || '',
            summary:  (item.summary || '').substring(0, 300),
            time:     new Date(ts).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
            url:      item.url || '',
            ts
          });
        }
      }
    } catch(e) {
      errors.push(`Finnhub/${cat}: ${e.message}`);
    }
  }
}

// ── 2. RSS 피드 (무료 · 무제한) ──────────────────────────────────────────
const rssFeeds = [
  { url: 'https://feeds.reuters.com/reuters/businessNews',                         source: 'Reuters' },
  { url: 'https://www.cnbc.com/id/100003114/device/rss/rss.html',                  source: 'CNBC Markets' },
  { url: 'https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines',      source: 'MarketWatch' },
  { url: 'https://www.cnbc.com/id/100727362/device/rss/rss.html',                  source: 'CNBC World' },
  { url: 'https://feeds.bloomberg.com/markets/news.rss',                            source: 'Bloomberg' },
];

// RSS XML 파서 (내장 XML 파서 없으므로 정규식)
function parseRSS(xml, source) {
  const items = [];
  const blocks = xml.split('<item>').slice(1);
  for (const block of blocks.slice(0, 25)) {
    const getTag = (tag) => {
      const m = block.match(new RegExp(`<${tag}[^>]*>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?<\\/${tag}>`, 'i'));
      return m ? m[1].trim().replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"') : '';
    };
    const headline = getTag('title');
    const pubDate  = getTag('pubDate') || getTag('dc:date');
    const url      = getTag('link');
    if (!headline) continue;
    const ts = pubDate ? new Date(pubDate).getTime() : Date.now();
    items.push({ source, category: 'rss', headline, time: pubDate ? new Date(ts).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }) : '시간미상', url, ts });
  }
  return items;
}

for (const feed of rssFeeds) {
  try {
    const xml = await this.helpers.httpRequest({
      method: 'GET',
      url: feed.url,
      headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/rss+xml, application/xml, text/xml' },
      timeout: 12000
    });
    const items = parseRSS(typeof xml === 'string' ? xml : JSON.stringify(xml), feed.source);
    for (const item of items) {
      if (item.ts >= cutoffTime || item.time === '시간미상') headlines.push(item);
    }
  } catch(e) {
    errors.push(`RSS/${feed.source}: ${e.message}`);
  }
}

// ── 3. 중요도 스코어링 & 중복 제거 ─────────────────────────────────────
const HIGH_IMPACT = [
  // 통화정책
  'Fed','Federal Reserve','FOMC','Powell','rate cut','rate hike','interest rate','tapering',
  // 경제지표
  'inflation','CPI','PCE','GDP','NFP','nonfarm','unemployment','jobless',
  // 지정학
  'Iran','Russia','Ukraine','China','Taiwan','war','sanction','geopolit',
  // 에너지·원자재
  'oil','crude','OPEC','gold','wheat','commodity',
  // 시장 이벤트
  'crash','plunge','surge','rally','crisis','default','bubble','recession','bear','bull',
  // 기업
  'earnings','revenue','guidance','layoff','merger','acquisition','IPO','bankruptcy',
  // 기관
  'IMF','World Bank','ECB','BOJ','BIS','Treasury','Yellen',
  // 핵심 종목
  'NVIDIA','Apple','Tesla','Amazon','Meta','Google','Microsoft','Berkshire',
  // 암호화폐·달러
  'Bitcoin','Ethereum','crypto','dollar','DXY','yield','bond','tariff'
];

const seen = new Set();
const deduped = headlines.filter(h => {
  const key = h.headline.toLowerCase().replace(/\s+/g,'').substring(0, 60);
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});

const scored = deduped.map(h => {
  const text = (h.headline + ' ' + (h.summary || '')).toLowerCase();
  let score = 0;
  for (const kw of HIGH_IMPACT) if (text.includes(kw.toLowerCase())) score += 2;
  // 최신성 보너스 (6시간 이내 +3점)
  if (Date.now() - h.ts < 6 * 60 * 60 * 1000) score += 3;
  return { ...h, score };
});

// 중요도 높은 순 → 최신 순 정렬
scored.sort((a, b) => b.score - a.score || b.ts - a.ts);
const top = scored.slice(0, 30);

// ── 4. 마크다운 뉴스 요약 생성 ───────────────────────────────────────────
const fetchTime = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

// 카테고리별 구분
const urgentNews  = top.filter(n => n.score >= 6);
const normalNews  = top.filter(n => n.score < 6);

const fmtLine = (n, i) =>
  `${i+1}. **[${n.source}]** ${n.headline}\n   *(${n.time}${n.summary ? ' — ' + n.summary.substring(0,120) + '...' : ''})*`;

const breakingNewsText = [
  '## 🔴 글로벌 주요 뉴스 (최근 18시간 — 새벽 이슈 포함)',
  '',
  urgentNews.length > 0 ? '### ⚡ 高임팩트 헤드라인' : '',
  ...urgentNews.map(fmtLine),
  urgentNews.length > 0 && normalNews.length > 0 ? '\n### 📰 주요 뉴스' : '',
  ...normalNews.map((n, i) => fmtLine(n, urgentNews.length + i)),
  '',
  `> 수집시각: ${fetchTime} | 총 ${top.length}건 | 오류: ${errors.length}건${errors.length ? ' (' + errors.slice(0,3).join(', ') + ')' : ''}`
].filter(l => l !== '').join('\n');

return [{ json: {
  ...prev,
  breakingNews:     top,
  breakingNewsText,
  newsErrors:       errors,
  newsCount:        top.length,
  urgentCount:      urgentNews.length
} }];
"""

# ─── 2. 노드 객체 생성 ────────────────────────────────────────────────────
s02c_node = {
    "id": "node-02c-breaking-news",
    "name": "S02c-BreakingNews",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [700, 320],
    "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": news_code
    }
}

# 중복 체크
existing = [n['name'] for n in d['nodes']]
if 'S02c-BreakingNews' not in existing:
    d['nodes'].append(s02c_node)
    print('S02c-BreakingNews 노드 추가')
else:
    for n in d['nodes']:
        if n['name'] == 'S02c-BreakingNews':
            n['parameters']['jsCode'] = news_code
    print('S02c-BreakingNews 노드 업데이트')

# ─── 3. 연결 수정: S02b → S02c → S03-Perplexity ─────────────────────────
# S02b 다음을 S02c로 변경
for src, conn in d['connections'].items():
    if 'main' in conn and conn['main']:
        for link_list in conn['main']:
            for link in link_list:
                if link.get('node') == 'S03-Perplexity' and src == 'S02b-FX':
                    link['node'] = 'S02c-BreakingNews'
                    print(f'연결 변경: {src} → S02c-BreakingNews')

# S02c → S03-Perplexity
d['connections']['S02c-BreakingNews'] = {
    'main': [[{'node': 'S03-Perplexity', 'type': 'main', 'index': 0}]]
}
print('연결 추가: S02c-BreakingNews → S03-Perplexity')

# ─── 4. S05-Claude: breakingNewsText를 userContent에 추가 ──────────────
for n in d['nodes']:
    if n['name'] == 'S05-Claude':
        code = n['parameters']['jsCode']

        # breakingNewsText 변수 추출 추가
        old_content = "const marketTable = d.marketTable || '';\nconst userContent = '날짜: ' + today"
        new_content = (
            "const marketTable = d.marketTable || '';\n"
            "const breakingNews = d.breakingNewsText || '';\n"
            "const userContent = '날짜: ' + today"
        )

        # userContent 조립에 뉴스 섹션 추가
        old_parts = (
            "  + '\\n\\n[✅ 검증된 실시간 주가 데이터 — 이 숫자를 그대로 사용, 절대 수정 금지]\\n'"
            "  + marketTable\n"
            "  + '\\n\\n' + parts.join('\\n\\n')"
        )
        new_parts = (
            "  + '\\n\\n[✅ 검증된 실시간 주가 데이터 — 이 숫자를 그대로 사용, 절대 수정 금지]\\n'"
            "  + marketTable\n"
            "  + '\\n\\n[📰 글로벌 실시간 뉴스 — 새벽 이슈 포함, 핵심 변화요인 분석에 활용]\\n'"
            "  + breakingNews\n"
            "  + '\\n\\n' + parts.join('\\n\\n')"
        )

        changed = False
        if old_content in code:
            code = code.replace(old_content, new_content)
            changed = True
            print('S05-Claude: breakingNewsText 변수 추가')
        if old_parts in code:
            code = code.replace(old_parts, new_parts)
            changed = True
            print('S05-Claude: userContent에 뉴스 섹션 추가')
        if not changed:
            print('WARNING S05: 삽입 위치 찾지 못함')

        n['parameters']['jsCode'] = code
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('\n저장 완료!')
print('\n=== 업데이트 요약 ===')
print('파이프라인: S01 → S02 → S02b → S02c-BreakingNews → S03-Perplexity → S03b-RealData → S04 → S05-Claude')
print('뉴스 소스: Finnhub(general/forex/crypto/merger) + Reuters + CNBC + MarketWatch + Bloomberg RSS')
print('시간 범위: 최근 18시간 (새벽 이슈 커버)')
print('필터: 중요도 키워드 스코어링 → 상위 30건')
