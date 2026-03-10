"""S05-Claude 시스템 프롬프트 전면 개편 — AI 언급 제거 + 리포트 포맷 고급화"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S05-Claude: 최종 데일리 리포트 생성 (claude-sonnet-4-6)
const d = $input.first().json;
const { rawContent, gptContent, gptSuccess, perpSuccess,
        today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd } = d;
const KEY = $env.CLAUDE_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: { ...d, success: false, source: 'claude', error: 'CLAUDE_API_KEY 미설정', rewrittenContent: null }}];
}

const systemPrompt = `당신은 국내 대형 증권사 리서치센터의 수석 매크로 애널리스트입니다.
매일 아침 기관투자자·PB·고액자산가를 위한 데일리 브리핑을 작성합니다.

[작성 원칙]
- 3인칭·객관적 서술. "~로 파악됐다", "~한 것으로 분석된다" 문체 유지
- 수치는 반드시 명시. 애매한 표현("다소", "약간") 대신 구체적 수치 사용
- 인과관계 명확히 서술: A → B → C 흐름으로 연결
- 과장·단정 금지: "~할 가능성", "~로 예상된다" 표현 사용
- AI·자동화 관련 언급 일절 금지

[리포트 포맷 — 반드시 아래 구조 그대로 출력]

## 📈 전일 미국 증시 요약

| 지수 | 종가 | 전일비 | 등락률 |
|------|------|--------|--------|
| 다우존스 | | | |
| S&P 500 | | | |
| 나스닥 | | | |
| VIX | | | |

**주요 종목**
| 종목 | 종가 | 등락률 | 비고 |
|------|------|--------|------|
(상위 5~7개)

---

## 🔍 핵심 변화 요인

### 1. [가장 중요한 이슈 제목]
(3~4문장 인과관계 분석)

### 2. [두 번째 이슈]
(3~4문장)

### 3. [세 번째 이슈]
(3~4문장)

---

## 🏭 섹터·테마별 동향

| 섹터 | 방향 | 핵심 내용 |
|------|------|-----------|
| 반도체 | ▲/▼/─ | |
| AI·소프트웨어 | | |
| 자동차·2차전지 | | |
| 바이오·헬스케어 | | |
| 에너지·원자재 | | |
| 금융 | | |

---

## 🇰🇷 한국 증시 시사점

> **핵심 메시지** (1~2문장 핵심 요약)

- **환율**: USD/KRW 동향 및 영향
- **외국인**: 수급 동향 및 방향성
- **수출주**: 반도체·자동차·조선 등 영향
- **테마주**: AI·2차전지·방산 등 당일 관심 테마

---

## 💹 FICC 요약

| 자산 | 현재 | 방향 | 코멘트 |
|------|------|------|--------|
| 미 국채 10Y | | ▲/▼ | |
| 달러인덱스 | | | |
| WTI 원유 | | | |
| 금 | | | |
| BTC | | | |

---

## ⚠️ 오늘의 체크포인트

> 🔴 **리스크**: (주요 하방 리스크 1가지)

> 🟡 **주목**: (오늘 주시해야 할 이벤트·지표)

> 🟢 **기회**: (잠재적 상방 요인 1가지)

---`;

const parts = [];
if (perpSuccess && rawContent) parts.push('=== 리서치 데이터 (팩트·출처) ===\n' + rawContent);
if (gptSuccess && gptContent) parts.push('=== 심층 분석 (인과관계·해석) ===\n' + gptContent);

if (parts.length === 0) {
  return [{ json: { ...d, success: false, source: 'claude', error: '리서치 데이터 없음', rewrittenContent: null }}];
}

const userContent = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC/USD: ' + btcUsd
  + '\n\n' + parts.join('\n\n')
  + '\n\n위 데이터를 바탕으로 지정된 포맷에 맞춰 데일리 리포트를 작성하세요.'
  + ' 표의 수치는 리서치 데이터에서 정확히 가져오고, 없는 수치는 [확인중]으로 표기하세요.'
  + ' 최소 3500자 이상 작성하세요.';

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
    ...d, success: true, source: 'claude',
    rewrittenContent: report,
    model: r.model, llmModel: r.model,
    newsSource: gptSuccess ? 'perplexity+gpt' : 'perplexity'
  }}];
} catch(e) {
  return [{ json: { ...d, success: false, source: 'claude', error: e.message, rewrittenContent: null }}];
}
"""

for n in d['nodes']:
    if n['name'] == 'S05-Claude':
        n['parameters']['jsCode'] = new_code
        print('S05-Claude: 프롬프트 전면 개편 완료')
        break

# S05b-Gemini, S07b-Grok도 같은 포맷 가이드 적용
gemini_patch = '당신은 한국 증권사 리서치센터 수석 애널리스트입니다. '
gemini_fmt = (
    '당신은 국내 대형 증권사 리서치센터 수석 매크로 애널리스트입니다. '
    'AI·자동화 관련 언급 없이, 3인칭 객관적 증권사 문체로 작성하세요. '
)

for n in d['nodes']:
    if n['name'] in ('S05b-Gemini', 'S07b-Grok'):
        code = n['parameters']['jsCode']
        if '당신은 한국 증권사 리서치센터 수석 애널리스트입니다.' in code:
            code = code.replace(
                '당신은 한국 증권사 리서치센터 수석 애널리스트입니다.',
                '당신은 국내 대형 증권사 리서치센터 수석 매크로 애널리스트입니다. AI·자동화 관련 언급 없이, 3인칭 객관적 증권사 문체로 작성하세요.'
            )
            n['parameters']['jsCode'] = code
            print(f'{n["name"]}: AI 언급 제거 패치 적용')

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
