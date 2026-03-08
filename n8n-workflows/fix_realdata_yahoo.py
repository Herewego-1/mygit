"""
구조 개편:
1. S03b-RealData (NEW): Yahoo Finance 무료 API → 실제 주가 숫자 추출
2. S03-Perplexity: 숫자 요청 제거 → 뉴스·분석만
3. S05-Claude: 검증된 숫자 테이블 전달 → 분석 작성만
"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# ─── 1. S03b-RealData: Yahoo Finance 무료 API ───────────────────────
realdata_code = r"""// S03b-RealData: Yahoo Finance 무료 API로 실제 주가 추출
const prev = $input.first().json;

// 조회할 심볼 목록 (ETF로 지수 대체)
const symbols = {
  'SPY':  'S&P 500',
  'QQQ':  'NASDAQ',
  'DIA':  '다우존스',
  'NVDA': 'NVIDIA',
  'TSLA': 'Tesla',
  'AAPL': 'Apple',
  'MSFT': 'Microsoft',
  'AMZN': 'Amazon',
  'META': 'Meta',
  'VIX':  'VIX'
};

const results = {};
const errors = [];

for (const [sym, name] of Object.entries(symbols)) {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${sym}?range=2d&interval=1d`;
    const resp = await this.helpers.httpRequest({
      method: 'GET',
      url,
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
      },
      timeout: 15000
    });

    const r = typeof resp === 'string' ? JSON.parse(resp) : resp;
    const meta = r?.chart?.result?.[0]?.meta;
    const quotes = r?.chart?.result?.[0]?.indicators?.quote?.[0];
    const timestamps = r?.chart?.result?.[0]?.timestamp;

    if (meta && quotes) {
      const lastIdx = quotes.close.length - 1;
      const prevIdx = lastIdx - 1;

      const close = quotes.close[lastIdx];
      const prevClose = prevIdx >= 0 ? quotes.close[prevIdx] : meta.previousClose;
      const open = quotes.open[lastIdx];
      const high = quotes.high[lastIdx];
      const low = quotes.low[lastIdx];
      const volume = quotes.volume[lastIdx];

      const change = close - prevClose;
      const changePct = ((change / prevClose) * 100);
      const direction = change >= 0 ? '▲' : '▼';

      results[sym] = {
        name,
        close: close?.toFixed(2),
        prevClose: prevClose?.toFixed(2),
        change: change?.toFixed(2),
        changePct: changePct?.toFixed(2),
        direction,
        open: open?.toFixed(2),
        high: high?.toFixed(2),
        low: low?.toFixed(2),
        volume: volume ? (volume / 1000000).toFixed(1) + 'M' : '-',
        currency: meta.currency || 'USD'
      };
    }
  } catch(e) {
    errors.push(`${sym}: ${e.message}`);
  }
}

// 표 형식 마크다운 생성 (Claude에게 넘길 완성된 테이블)
const rows = Object.entries(results).map(([sym, q]) =>
  `| ${q.name} (${sym}) | $${q.close} | ${q.direction}${Math.abs(q.change)} | ${q.direction}${Math.abs(q.changePct)}% | ${q.volume} |`
);

const marketTable = [
  '## 📈 실시간 검증 주가 데이터 (Yahoo Finance)',
  '',
  '| 종목 | 종가 | 전일대비 | 등락률 | 거래량 |',
  '|------|------|---------|--------|-------|',
  ...rows,
  '',
  `> 데이터 기준: Yahoo Finance 실시간 (${new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'})})`
].join('\n');

return [{ json: {
  ...prev,
  realMarketData: results,
  marketTable,
  dataErrors: errors,
  dataValidated: Object.keys(results).length > 0
} }];
"""

# S03b 노드 추가
s03b_node = {
    "id": "node-03b-realdata",
    "name": "S03b-RealData",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [900, 320],
    "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": realdata_code
    }
}
d['nodes'].append(s03b_node)

# ─── 2. S03-Perplexity: 숫자 요청 제거, 뉴스·분석만 ──────────────────
for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']
        old_prompt = (
            "  + '7. 전일 발표 주요 경제지표 (지표명 | 예상치 | 실제치 | 서프라이즈 방향)\\n'\n"
            "  + '8. 주요 기업 실적 발표 (기업명 | EPS 예상/실제 | 매출 예상/실제 | 가이던스 방향)\\n'\n"
            "  + '9. 이번 주 남은 주요 일정 (날짜·시간·항목·예상치)';"
        )
        new_prompt = (
            "  + '7. 전일 발표 주요 경제지표 분석 (예상치 대비 실제치, 시장 영향)\\n'\n"
            "  + '8. 주요 기업 실적 발표 분석 (어닝 서프라이즈/쇼크 내용)\\n'\n"
            "  + '9. 이번 주 주요 일정 (날짜·지표명·예상치)\\n'\n"
            "  + '⚠️ 주의: 주가 수치는 작성하지 마세요. 뉴스와 분석에 집중하세요. 주가 관련 수치는 [주가데이터 별도 수집]으로 표기';"
        )
        if old_prompt in code:
            n['parameters']['jsCode'] = code.replace(old_prompt, new_prompt)
            print('✅ S03-Perplexity: 주가 수치 요청 제거, 뉴스·분석 전문화')
        break

# ─── 3. 연결: S03 → S03b-RealData → S04 ─────────────────────────
d['connections']['S03-Perplexity']['main'][0] = [
    {'node': 'S03b-RealData', 'type': 'main', 'index': 0}
]
d['connections']['S03b-RealData'] = {
    'main': [[{'node': 'S04-GPT-CrossVal', 'type': 'main', 'index': 0}]]
}

# ─── 4. S05-Claude: 검증된 숫자 테이블 직접 사용 ─────────────────────
for n in d['nodes']:
    if n['name'] == 'S05-Claude':
        code = n['parameters']['jsCode']
        # userContent에 marketTable 추가
        old_content = "const userContent = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC/USD: ' + btcUsd"
        new_content = (
            "const marketTable = d.marketTable || '';\n"
            "const userContent = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC/USD: ' + btcUsd"
        )
        old_parts = "  + '\\n\\n' + parts.join('\\n\\n')"
        new_parts = (
            "  + '\\n\\n[✅ 검증된 실시간 주가 데이터 — 이 숫자를 그대로 사용, 절대 수정 금지]\\n'"
            "  + marketTable\n"
            "  + '\\n\\n' + parts.join('\\n\\n')"
        )
        if old_content in code:
            code = code.replace(old_content, new_content)
        if old_parts in code:
            code = code.replace(old_parts, new_parts)
        n['parameters']['jsCode'] = code
        print('✅ S05-Claude: 검증 주가 테이블 직접 전달')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# 검증
with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)
print(f'\n총 노드: {len(d2["nodes"])}개')
print('연결:')
print('  S03 ->', d2['connections'].get('S03-Perplexity', {}).get('main', [[]])[0])
print('  S03b->', d2['connections'].get('S03b-RealData', {}).get('main', [[]])[0])
print('\n✅ 완료! API 키 없이 Yahoo Finance 무료 사용')
