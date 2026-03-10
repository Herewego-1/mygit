import json, sys

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# ===== S03-Perplexity =====
CODE_S03 = r"""// S03-Perplexity: sonar-pro — 종합 글로벌 금융 브리핑
const inp = $input.first().json;
const { today, obsidianFilePath, backupFilePath, startTime } = inp;
const usdKrw = inp.usdKrw || 0;
const btcUsd  = inp.btcUsd  || 0;
const KEY = $env.PERPLEXITY_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: {
    success: false, source: 'perplexity',
    error: 'PERPLEXITY_API_KEY 미설정',
    rawContent: null,
    today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd
  }}];
}

const systemPrompt = 'You are a senior Wall Street veteran analyst with 30+ years at Goldman Sachs, Bridgewater Associates, and JPMorgan. Expert in global macro, institutional research synthesis, and Korean market impacts.\n\nABSOLUTE RULES:\n1. Every number MUST have source citation (URL or [Publication Name, Date])\n2. If data unverifiable for today, write [미확인] — NEVER fabricate\n3. Cover ALL 6 sections completely\n4. Include legendary investor views (Buffett, Dalio, Burry)\n5. Minimum 5 verified data points per section\n6. Aim for 4000+ words total';

const userPrompt = 'Date: ' + today + ' (KST). Provide comprehensive verified financial morning briefing. CITE source URL for EVERY number.\n\n[SECTION 1: WORLD MARKETS]\nUS Indices (S&P500, NASDAQ, Dow, Russell 2000 exact levels & %). European markets (Stoxx600, DAX, FTSE, CAC). Asian markets (Nikkei, HSI, CSI300, ASX). CNN Fear & Greed index. Top overnight catalyst.\n\n[SECTION 2: US MARKET DEEP]\nAll 11 S&P sectors (XLK,XLF,XLV,XLY,XLP,XLE,XLI,XLB,XLU,XLRE,XLC) % change. NYSE advance/decline. Treasury yields 2Y/10Y/30Y exact% + spread bps. Fed rate/FOMC date/CME FedWatch%. DXY and VIX exact levels.\n\n[SECTION 3: KOREAN MARKET]\nKOSPI exact close & %. KOSDAQ exact & %. Foreign net buy/sell KRW billions. Samsung(005930), SK Hynix(000660), NAVER prices & %. USD/KRW exact, BOK rate, next BOK meeting.\n\n[SECTION 4: CRYPTO & ALTERNATIVES]\nBTC/USD exact + 24h%. ETH/USD exact + 24h%. Total crypto market cap. Gold XAU/USD exact. WTI & Brent exact prices & key driver.\n\n[SECTION 5: GLOBAL MACRO]\nLatest US CPI/PPI/PCE/NFP/unemployment. China PMI/exports/PBOC. ECB/BOJ rate status. EUR/USD, JPY/USD. Active geopolitical risks with market impact.\n\n[SECTION 6: RISK & OPPORTUNITY]\nTop 3 tail risks this week. Top 3 opportunities. Buffett/Dalio/Burry recent views. GS/JPM/BlackRock latest research. Key events next 5 days.';

const rtPrices = [];
if (usdKrw > 0) rtPrices.push('- USD/KRW: EXACTLY ' + usdKrw.toLocaleString() + ' KRW (real-time ECB)');
if (btcUsd  > 0) rtPrices.push('- BTC/USD: EXACTLY $' + btcUsd.toLocaleString() + ' (real-time CoinGecko)');
const verifiedNote = rtPrices.length > 0
  ? '\n\nMANDATORY PRICE OVERRIDE:\n' + rtPrices.join('\n')
  : '';
const finalPrompt = userPrompt + verifiedNote;

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.perplexity.ai/chat/completions',
    headers: {
      'Authorization': 'Bearer ' + KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'sonar-pro',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user',   content: finalPrompt }
      ],
      temperature: 0.1,
      max_tokens: 6000,
      return_citations: true
    }),
    timeout: 60000
  });

  const r = typeof response === 'string' ? JSON.parse(response) : response;
  const content = r?.choices?.[0]?.message?.content;
  if (!content || content.trim().length < 200)
    throw new Error('응답 부실 (' + (content?.length || 0) + '자)');

  return [{ json: {
    success: true, source: 'perplexity',
    rawContent: content,
    today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd
  }}];
} catch(e) {
  return [{ json: {
    success: false, source: 'perplexity',
    error: e.message,
    rawContent: null,
    today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd
  }}];
}
"""

# ===== S04-GPT-CrossVal =====
CODE_S04 = r"""// S04-GPT-CrossVal: GPT-4o 독립 분석 + 교차검증 정리
const prev = $input.first().json;
const { rawContent, today, obsidianFilePath, backupFilePath, startTime } = prev;
const usdKrw = prev.usdKrw || 0;
const btcUsd  = prev.btcUsd  || 0;
const perpSuccess = prev.success !== false;
const KEY = $env.OPENAI_API_KEY;

const systemPrompt = '당신은 한국 기관투자자를 위한 글로벌 매크로·주식 애널리스트다. 오늘 날짜 기준 독립적으로 분석·요약한다. 사실과 추론을 명확히 구분하고, 각 이슈의 원인→결과 체인을 반드시 연결한다.';

const userPrompt = '오늘: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC: ' + btcUsd + '\n\n1. 미 증시 요약 (지수·섹터·대표 종목 수익률 표)\n2. 핵심 변화요인 인과 분석 (원인→결과 체인)\n3. 섹터·테마별 임팩트 (반도체/소프트웨어/자동차/온라인소비/비트코인)\n4. 한국 증시 시사점 (환율·반도체·AI규제·개장방향)\n5. FICC 요약\n6. 리스크·기회 체크포인트 3가지\n\n형식: 한국어, Markdown';

let gptContent = null;
let gptSuccess = false;

if (KEY && !KEY.includes('여기에')) {
  try {
    const response = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + KEY
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user',   content: userPrompt }
        ],
        temperature: 0.3,
        max_tokens: 3000
      }),
      timeout: 45000
    });
    const r = typeof response === 'string' ? JSON.parse(response) : response;
    if (r?.choices?.[0]?.message?.content) {
      gptContent = r.choices[0].message.content;
      gptSuccess = true;
    }
  } catch (e) {
    // GPT 실패 시 Perplexity 단독 진행
  }
}

return [{ json: {
  rawContent,
  gptContent,
  gptSuccess,
  perpSuccess,
  today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd,
  source: prev.source || 'perplexity',
  newsSource: gptSuccess ? 'perplexity+gpt' : (prev.source || 'perplexity')
}}];
"""

# ===== S05-Claude =====
CODE_S05 = r"""// S05-Claude: 교차검증 기반 최종 리포트 생성 (claude-sonnet-4-6)
const d = $input.first().json;
const { rawContent, gptContent, gptSuccess, perpSuccess,
        today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd } = d;
const KEY = $env.CLAUDE_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: {
    ...d, success: false, source: 'claude',
    error: 'CLAUDE_API_KEY 미설정', rewrittenContent: null
  }}];
}

const systemPrompt = '당신은 한국 증권사 리서치센터 수석 애널리스트다.\nPerplexity(팩트·출처)와 GPT(인과관계·해석)의 리서치 초안을 받아 통합 데일리 리포트를 작성한다.\n\n[교차검증 규칙]\n1. 공통 사실 → 확정 서술\n2. Perplexity만 언급 → 출처 기반 참고, URL 병기\n3. GPT만 언급 → 추정/시나리오로 conditional 서술\n4. 상충 → 양측 병기, 신뢰도 높은 쪽 우선\n5. 과장·단정 → "~할 수 있다/가능성" 으로 완화\n\n[리포트 구조]\n1. 전일 미 증시 요약 (표)\n2. 핵심 변화요인\n3. 섹터·테마별 동향\n4. 한국 증시 시사점\n5. FICC\n6. 교차분석 코멘트\n7. 오늘의 체크포인트 (bullet 3개)\n\n[형식] 한국어, 증권사 문체, Markdown, 최소 3500자';

const parts = [];
if (perpSuccess && rawContent) {
  parts.push('=== PERPLEXITY SONAR-PRO (팩트·출처) ===\n' + rawContent);
}
if (gptSuccess && gptContent) {
  parts.push('=== GPT-4o (인과관계·해석) ===\n' + gptContent);
}
if (parts.length === 0) {
  return [{ json: {
    ...d, success: false, source: 'claude',
    error: '리서치 데이터 없음', rewrittenContent: null
  }}];
}

const userContent = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC: ' + btcUsd + '\n\n' + parts.join('\n\n') + '\n\n위 초안을 교차검증하여 통합 데일리 리포트를 작성해주세요.';

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.anthropic.com/v1/messages',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 8000,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    }),
    timeout: 90000
  });

  const r = typeof response === 'string' ? JSON.parse(response) : response;
  const report = r?.content?.[0]?.text;
  if (!report) throw new Error('Claude 응답 비어있음');

  return [{ json: {
    ...d,
    success: true,
    source: 'claude',
    rewrittenContent: report,
    model: r.model,
    llmModel: r.model,
    newsSource: gptSuccess ? 'perplexity+gpt+claude' : 'perplexity+claude'
  }}];
} catch(e) {
  return [{ json: {
    ...d, success: false, source: 'claude',
    error: e.message, rewrittenContent: null
  }}];
}
"""

# Apply fixes
for n in d['nodes']:
    if n['id'] == 'node-03-perplexity':
        n['parameters']['jsCode'] = CODE_S03
        print('S03-Perplexity: updated')
    elif n['id'] == 'node-04-gpt':
        n['parameters']['jsCode'] = CODE_S04
        print('S04-GPT-CrossVal: updated')
    elif n['id'] == 'node-05-claude':
        n['parameters']['jsCode'] = CODE_S05
        print('S05-Claude: updated')

# Verify no fetch()
all_code = CODE_S03 + CODE_S04 + CODE_S05
print('fetch() calls:', all_code.count('await fetch('))
print('httpRequest calls:', all_code.count('httpRequest'))
for label, code in [('S03', CODE_S03), ('S04', CODE_S04), ('S05', CODE_S05)]:
    bt = code.count('`')
    print(label + ' backticks:', bt, '(OK)' if bt % 2 == 0 else '(UNBALANCED!)')

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('Saved OK')
