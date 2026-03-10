"""S04-GPT-CrossVal: gpt-4o-mini 단독 사용 (구독 불필요)"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S04-GPT-CrossVal: GPT-4o-mini 교차분석
const prev = $input.first().json;
const { rawContent, today, obsidianFilePath, backupFilePath, startTime } = prev;
const usdKrw = prev.usdKrw || 0;
const btcUsd  = prev.btcUsd  || 0;
const perpSuccess = prev.success !== false;
const KEY = $env.OPENAI_API_KEY;

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
  + '형식: 한국어, Markdown'
  + (rawContent ? '\n\n## Perplexity 리서치\n' + rawContent : '');

let gptContent = null;
let gptSuccess = false;

if (KEY && !KEY.includes('여기에')) {
  try {
    const resp = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + KEY
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
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
    }
  } catch (e) {
    // GPT 실패 시 gptContent null로 계속 진행
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

for n in d['nodes']:
    if n['name'] == 'S04-GPT-CrossVal':
        n['parameters']['jsCode'] = new_code
        print('S04-GPT-CrossVal -> gpt-4o-mini 단독으로 업데이트')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
