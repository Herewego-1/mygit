"""S04-GPT-CrossVal: GPT 실패 시 Grok으로 자동 폴백"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S04-GPT-CrossVal: GPT-4o 교차분석 + 실패 시 Grok 폴백
const prev = $input.first().json;
const { rawContent, today, obsidianFilePath, backupFilePath, startTime } = prev;
const usdKrw = prev.usdKrw || 0;
const btcUsd  = prev.btcUsd  || 0;
const perpSuccess = prev.success !== false;

const systemPrompt = '당신은 한국 증권사 리서치센터 수석 퀀트·거시경제 애널리스트입니다. '
  + '주어진 날짜 기준 시장데이터를 분석하세요. 팩트와 정확도를 우선하고, '
  + '매 이슈의 인과관계를 체계적으로 분석하되 증권사 문체로 반드시 작성한다.';

const userPrompt = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC: ' + btcUsd + '\n\n'
  + '1. 미 증시 요약 (주요지수·대표주 전일비 표 형태로 표시)\n'
  + '2. 핵심 변화요인 인과관계 분석 (증권사 문체)\n'
  + '3. 섹터·테마별 동향 (반도체/소프트웨어/자동차/소비재/에너지)\n'
  + '4. 한국 증시 시사점 (환율·반도체·AI수혜·외국인)\n'
  + '5. FICC 요약\n'
  + '6. 리스크·기회 체크리스트 3가지\n\n'
  + '형식: 한국어, Markdown';

if (rawContent) {
  userPrompt += '\n\n## Perplexity 리서치\n' + rawContent;
}

let gptContent = null;
let gptSuccess = false;
let gptSource = null;

// 1차: GPT-4o 시도
const GPT_KEY = $env.OPENAI_API_KEY;
if (GPT_KEY && !GPT_KEY.includes('여기에')) {
  try {
    const resp = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + GPT_KEY
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
    const r = typeof resp === 'string' ? JSON.parse(resp) : resp;
    if (r?.choices?.[0]?.message?.content) {
      gptContent = r.choices[0].message.content;
      gptSuccess = true;
      gptSource = 'gpt-4o';
    }
  } catch (e) {
    // GPT 실패 → Grok 시도
  }
}

// 2차: Grok 폴백 (GPT 실패 시)
if (!gptSuccess) {
  const GROK_KEY = $env.GROK_API_KEY;
  if (GROK_KEY && !GROK_KEY.includes('여기에')) {
    try {
      const resp = await this.helpers.httpRequest({
        method: 'POST',
        url: 'https://api.x.ai/v1/chat/completions',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + GROK_KEY
        },
        body: JSON.stringify({
          model: 'grok-3',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user',   content: userPrompt }
          ],
          temperature: 0.3,
          max_tokens: 3000
        }),
        timeout: 45000
      });
      const r = typeof resp === 'string' ? JSON.parse(resp) : resp;
      if (r?.choices?.[0]?.message?.content) {
        gptContent = r.choices[0].message.content;
        gptSuccess = true;
        gptSource = 'grok-3';
      }
    } catch (e) {
      // Grok도 실패 → gptContent null로 계속
    }
  }
}

return [{ json: {
  rawContent,
  gptContent,
  gptSuccess,
  gptSource,
  perpSuccess,
  today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd,
  source: prev.source || 'perplexity',
  newsSource: gptSuccess ? ('perplexity+' + gptSource) : (prev.source || 'perplexity')
}}];
"""

for n in d['nodes']:
    if n['name'] == 'S04-GPT-CrossVal':
        n['parameters']['jsCode'] = new_code
        print('S04-GPT-CrossVal 업데이트 완료')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
