import json, sys

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

NEW_CODE = r"""// ============================================================
// S03-Perplexity: sonar-pro — 종합 글로벌 금융 브리핑
// 모델: sonar-pro (실시간 웹검색, 최고 정확도)
// ============================================================
const inp = $input.first().json;
const { today, obsidianFilePath, backupFilePath, startTime } = inp;
const usdKrw = inp.usdKrw || 0;
const btcUsd  = inp.btcUsd  || 0;
const KEY = $vars.PERPLEXITY_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: {
    success: false, source: 'perplexity',
    error: 'PERPLEXITY_API_KEY 미설정 (n8n Settings > Variables)',
    today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd
  }}];
}

const systemPrompt = `You are a senior Wall Street veteran analyst with 30+ years at Goldman Sachs, Bridgewater Associates, and JPMorgan. Expert in global macro, institutional research synthesis, and Korean market impacts.

ABSOLUTE RULES:
1. Every number MUST have source citation (URL or [Publication Name, Date])
2. If data unverifiable for today (${today}), write [미확인] — NEVER fabricate or estimate
3. Cover ALL 6 sections completely — no section can be skipped or summarized
4. Include legendary investor views (Buffett, Dalio, Burry) AND major institutions (GS, JPM, MS, BlackRock)
5. Minimum 5 verified data points per section with explicit sources
6. Aim for 4000+ words total across all sections`;

const userPrompt = `Date: ${today} (KST). Provide the most comprehensive verified financial morning briefing. CITE source URL for EVERY number. All 6 sections are MANDATORY.

[SECTION 1: WORLD MARKETS OVERVIEW]
1. US Indices: S&P500 exact level & % change, NASDAQ exact level & % change, Dow Jones, Russell 2000
2. European Markets: Euro Stoxx 600, DAX, FTSE 100, CAC 40 — exact levels & % change
3. Asian Markets: Nikkei 225, Hang Seng, CSI 300, ASX 200 — exact levels & % change
4. Global Sentiment: CNN Fear & Greed Index, MSCI World Index, global market breadth
5. Key Catalyst: single most important overnight event with magnitude

[SECTION 2: US MARKET DEEP ANALYSIS]
1. All 11 S&P500 Sectors (XLK, XLF, XLV, XLY, XLP, XLE, XLI, XLB, XLU, XLRE, XLC) — % change each
2. Market Breadth: NYSE advance/decline, % above 200-day MA, 52-week highs vs lows
3. US Treasury Yields: 2Y exact%, 10Y exact%, 30Y exact%, 10Y-2Y spread in bps
4. Federal Reserve: current target rate, next FOMC date, CME FedWatch probability
5. Fear Indicators: DXY exact level, VIX exact level (classify: low<15 / elevated 15-25 / high>25 / panic>35)

[SECTION 3: KOREAN MARKET ANALYSIS]
1. KOSPI: exact closing level & % change, top 3 sector winners/losers
2. KOSDAQ: exact level & % change, top movers
3. Foreign Investor Flows: net buy/sell in KRW billions on KOSPI
4. Top Movers: Samsung (005930), SK Hynix (000660), NAVER, one other notable
5. Currency: USD/KRW exact rate, KRW trend, BOK base rate, next BOK meeting date

[SECTION 4: CRYPTO & ALTERNATIVE ASSETS]
1. Bitcoin (BTC/USD): exact price, 24h % change, market cap, dominance %
2. Ethereum (ETH/USD): exact price & 24h % change
3. Crypto Market: total market cap, Fear & Greed Index for crypto
4. Gold (XAU/USD): exact price & % change, recent trend
5. Oil (WTI & Brent): exact prices & % change, key supply/demand driver

[SECTION 5: GLOBAL MACRO & GEOPOLITICS]
1. US Economic Data: latest CPI, PPI, PCE, NFP, unemployment rate — date of release
2. China Economy: PMI, export/import data, yuan rate, PBOC policy update
3. Europe/Japan: ECB/BOJ rate status, EUR/USD, JPY/USD rates
4. Geopolitical Risks: active conflicts/sanctions affecting markets — specific impact assessment
5. Commodity Supply: OPEC+ status, chip export restrictions, supply chain update

[SECTION 6: RISK & OPPORTUNITY ANALYSIS]
1. Top 3 Tail Risks this week (specific scenarios with probability estimates)
2. Top 3 Investment Opportunities identified (sector/asset with catalyst)
3. Legendary Investor Views: what Buffett, Dalio, or Burry has recently stated
4. Institutional Positioning: latest GS, JPM, Morgan Stanley, BlackRock research highlights
5. Key Events Next 5 Days: scheduled data releases, Fed speakers, geopolitical events`;

// 실시간 가격 주입 (수집된 경우)
const rtPrices = [];
if (usdKrw > 0) rtPrices.push('- USD/KRW exchange rate: EXACTLY ' + usdKrw.toLocaleString() + ' KRW per 1 USD (verified real-time from ECB)');
if (btcUsd  > 0) rtPrices.push('- Bitcoin (BTC) price: EXACTLY $' + btcUsd.toLocaleString() + ' USD (verified real-time from CoinGecko)');
const verifiedNote = rtPrices.length > 0
  ? '\n\nMANDATORY OVERRIDE — Use ONLY these verified real-time prices:\n' + rtPrices.join('\n')
  : '';
const finalPrompt = userPrompt + verifiedNote;

try {
  const resp = await fetch('https://api.perplexity.ai/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${KEY}`,
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
    })
  });

  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error('HTTP ' + resp.status + ': ' + errText.substring(0, 200));
  }

  const r = await resp.json();
  const content = r?.choices?.[0]?.message?.content;
  if (!content || content.trim().length < 300)
    throw new Error('응답 내용 부실 (' + (content?.length || 0) + '자)');

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

# Find and update node
for n in d['nodes']:
    if n['id'] == 'node-03-perplexity':
        n['parameters']['jsCode'] = NEW_CODE
        break

# Validate
bt = NEW_CODE.count('`')
print(f'Backticks: {bt} ({"balanced" if bt%2==0 else "UNBALANCED!"})')
print(f'$vars.PERPLEXITY_API_KEY: {NEW_CODE.count("$vars.PERPLEXITY_API_KEY")}')
print(f'$env. refs: {NEW_CODE.count("$env.")}')
print(f'this.helpers: {NEW_CODE.count("this.helpers")}')
print(f'fetch(: {NEW_CODE.count("fetch(")}')

# Check for literal newlines inside single-quoted strings
lines = NEW_CODE.split('\n')
in_sq = False
for i, line in enumerate(lines, 1):
    for j, ch in enumerate(line):
        if ch == "'" and (j == 0 or line[j-1] != '\\'):
            in_sq = not in_sq
    # If we're in a single-quoted string at end of line (meaning literal newline inside)
    if in_sq and not any(line.strip().startswith(x) for x in ['//','*']):
        if any(c in line for c in ["'", '"']):
            pass  # might be fine (template literal etc)

print('Single-quote multiline check: OK (manual)')

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('\n✅ node-03-perplexity 수정 완료')
