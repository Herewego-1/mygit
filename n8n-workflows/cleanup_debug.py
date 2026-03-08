"""S03-Perplexity keyDebug 제거 — 진단 완료, 클린업"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S03-Perplexity: sonar — 종합 글로벌 금융 브리핑
const inp = $input.first().json;
const { today, obsidianFilePath, backupFilePath, startTime } = inp;
const usdKrw = inp.usdKrw || 0;
const btcUsd  = inp.btcUsd  || 0;
const KEY = $env.PERPLEXITY_API_KEY;

if (!KEY || typeof KEY !== 'string' || KEY.length < 10) {
  return [{ json: {
    success: false, source: 'perplexity',
    error: 'PERPLEXITY_API_KEY 미설정',
    rawContent: null,
    today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd,
    btcKrw: inp.btcKrw || 0
  }}];
}

const systemPrompt = 'You are a senior Wall Street veteran analyst with 30+ years at Goldman Sachs, '
  + 'Bridgewater Associates, and JPMorgan. Expert in global macro, institutional research synthesis, '
  + 'and Korean market impacts.\n\nABSOLUTE RULES:\n'
  + '1. Every number MUST have source citation (URL or [Publication Name, Date])\n'
  + '2. If data unverifiable for today, write [미확인] — NEVER fabricate\n'
  + '3. Cover ALL 6 sections completely\n'
  + '4. Include legendary investor views (Buffett, Dalio, Burry)\n'
  + '5. Minimum 5 verified data points per section\n'
  + '6. Aim for 4000+ words total';

const userPrompt = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC/USD: ' + btcUsd + '\n\n'
  + '다음 6개 섹션으로 구성된 한국어 증권사 데일리 리포트를 작성하세요:\n\n'
  + '1. 전일 미 증시 요약 (주요지수·대표종목 전일비 표 형식)\n'
  + '2. 핵심 변화요인 심층 분석 (인과관계, 섹터 영향)\n'
  + '3. 섹터·테마별 동향 (반도체/소프트웨어/자동차/소비재/에너지)\n'
  + '4. 한국 증시 시사점 (환율·외국인·수출주·AI 수혜)\n'
  + '5. FICC 요약 (채권·원자재·달러·암호화폐)\n'
  + '6. 리스크·기회 체크포인트 3가지\n\n'
  + '형식: 한국어, 증권사 문체, Markdown, 최소 3500자';

let rawContent = null;
let success = false;
let errorMsg = null;

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.perplexity.ai/chat/completions',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + KEY
    },
    body: JSON.stringify({
      model: 'sonar',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user',   content: userPrompt }
      ],
      temperature: 0.1,
      max_tokens: 8000,
      return_citations: true,
      search_recency_filter: 'day'
    }),
    timeout: 90000
  });
  const r = typeof response === 'string' ? JSON.parse(response) : response;
  if (r?.choices?.[0]?.message?.content) {
    rawContent = r.choices[0].message.content;
    success = true;
  } else {
    throw new Error('Perplexity 응답이 비어있음');
  }
} catch (e) {
  errorMsg = e.message;
}

return [{ json: {
  success, source: 'perplexity', error: errorMsg,
  rawContent,
  today, obsidianFilePath, backupFilePath, startTime,
  usdKrw, btcUsd, btcKrw: inp.btcKrw || 0
} }];
"""

for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        n['parameters']['jsCode'] = new_code
        print('S03-Perplexity: keyDebug 제거 완료')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
