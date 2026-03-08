import json, sys

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    old = json.load(f)

def get_node(nid):
    return next((n for n in old['nodes'] if n['id'] == nid), None)

CODE_GPT_CROSSVAL = """// ============================================================
// 노드 4: GPT-4o 독립 분석 + 교차검증 데이터 정리
// Perplexity(팩트) 결과 받은 후, GPT-4o 독립 분석 호출
// 두 결과를 Claude에 전달할 형식으로 정리
// ============================================================
const prev = $input.first().json;
const { rawContent, today, obsidianFilePath, backupFilePath, startTime } = prev;
const usdKrw = prev.usdKrw || '';
const btcUsd  = prev.btcUsd  || '';
const perpSuccess = prev.success !== false;
const KEY = $vars.OPENAI_API_KEY;

const systemPrompt = `당신은 한국 기관투자자를 위한 글로벌 매크로·주식 애널리스트다.
오늘 날짜 기준, 아래 주제를 독립적으로 분석·요약한다.
- 사실과 추론을 명확히 구분해 작성한다 (예: "확인된 사실:", "해석/추정:").
- 수치는 보수적으로 기술하고, 출처를 명시하기 어려운 경우 "추정치" 표기.
- 각 이슈의 원인→결과 체인을 문장으로 반드시 연결한다.`;

const userPrompt = `오늘 날짜: ${today} (KST) | USD/KRW: ${usdKrw} | BTC: ${btcUsd}

[아웃풋 구조]
1. 미 증시 요약 (지수·섹터·대표 종목 수익률 표)
2. 핵심 변화요인 인과 분석 (원인→결과 체인)
3. 섹터·테마별 임팩트 분석 (반도체, 소프트웨어, 자동차, 온라인소비, 비트코인)
4. 한국 증시 시사점 (에너지 의존도, AI 칩 규제, 환율, 반도체 변동성)
5. FICC 요약 (원유/달러·환율/금리/귀금속)
6. 리스크·기회 체크포인트 (bullet 3개 이내)

형식: 한국어, Markdown`;

let gptContent = null;
let gptSuccess = false;

if (KEY && !KEY.includes('여기에')) {
  try {
    const resp = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user',   content: userPrompt }
        ],
        temperature: 0.3,
        max_tokens: 3000
      })
    });
    if (resp.ok) {
      const result = await resp.json();
      gptContent = result.choices[0].message.content;
      gptSuccess = true;
    }
  } catch (e) {
    // GPT 실패 시 Perplexity 단독으로 진행
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

CODE_CLAUDE = """// ============================================================
// 노드 5: Claude API — 교차검증 기반 최종 리포트 생성
// 모델: claude-sonnet-4-6
// Perplexity(팩트·출처) + GPT-4o(인과관계·해석) 통합
// ============================================================
const d = $input.first().json;
const { rawContent, gptContent, gptSuccess, perpSuccess,
        today, obsidianFilePath, backupFilePath, startTime, usdKrw, btcUsd } = d;
const KEY = $vars.CLAUDE_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: {
    ...d, success: false, source: 'claude',
    error: 'CLAUDE_API_KEY 미설정', rewrittenContent: null
  }}];
}

const systemPrompt = `당신은 한국 증권사 리서치센터 수석 애널리스트다.
Perplexity(팩트·출처 중심)와 GPT(인과관계·해석 중심)가 독립적으로 작성한
리서치 초안을 받아, 하나의 통합 데일리 리포트를 작성한다.

[교차검증 처리 규칙]
1. 공통 사실 → 코어 시나리오로 채택, 확정적으로 서술
2. Perplexity만 언급 → 출처 기반 참고 이슈로 서술, 인용 URL 병기
3. GPT만 언급 → 추정/시나리오 수준으로 conditional 서술
4. 상충 → 양측 견해 모두 제시, 더 신뢰할 근거 쪽 우선
5. 과장·단정 문장은 반드시 "~할 수 있다 / ~가능성" 등으로 완화

[최종 리포트 구조]
1. 전일 미 증시 요약 (표: 주요 지수·섹터·유가·금리·환율)
2. 핵심 변화요인 (국제유가 / 금리·달러 / 정책·규제)
3. 섹터·테마별 동향 (반도체/소프트웨어/자동차·배터리/온라인소비/테마)
4. 한국 증시 시사점 (개장 방향·당일 포인트·종목 방향)
5. FICC (원유/달러·환율/국채금리/귀금속/농산물)
6. 교차분석 코멘트 (견해 차이·불확실 구간)
7. 오늘의 체크포인트 (리스크·기회 bullet 3개)

[출력 형식] 한국어, 증권사 리서치 문체, Markdown, 최소 3500자`;

const parts = [];
if (perpSuccess && rawContent) {
  parts.push('=== PERPLEXITY SONAR-PRO (팩트·출처 중심) ===\\n' + rawContent);
}
if (gptSuccess && gptContent) {
  parts.push('=== GPT-4o (인과관계·해석 중심) ===\\n' + gptContent);
}
if (parts.length === 0) {
  return [{ json: {
    ...d, success: false, source: 'claude',
    error: '리서치 데이터 없음 (Perplexity+GPT 모두 실패)',
    rewrittenContent: null
  }}];
}

const dataSources = [perpSuccess ? 'Perplexity' : null, gptSuccess ? 'GPT-4o' : null].filter(Boolean).join('+');
const userContent = '날짜: ' + today + ' (KST) | USD/KRW: ' + usdKrw + ' | BTC/USD: ' + btcUsd + '\\n데이터 출처: ' + dataSources + '\\n\\n' + parts.join('\\n\\n') + '\\n\\n위 리서치 초안을 교차검증하여 하나의 통합 데일리 리포트를 작성해주세요.';

try {
  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
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
    })
  });

  if (!resp.ok) {
    const err = await resp.text();
    return [{ json: { ...d, success: false, source: 'claude', error: err, rewrittenContent: null }}];
  }

  const result = await resp.json();
  const report = result.content[0].text;

  return [{ json: {
    ...d,
    success: true,
    source: 'claude',
    rewrittenContent: report,
    model: result.model,
    llmModel: result.model,
    newsSource: gptSuccess ? 'perplexity+gpt+claude' : 'perplexity+claude'
  }}];
} catch (e) {
  return [{ json: { ...d, success: false, source: 'claude', error: e.message, rewrittenContent: null }}];
}
"""

def make_if(nid, name, pos):
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{"id": "c1", "leftValue": "={{ $json.success }}", "rightValue": True,
                                "operator": {"type": "boolean", "operation": "true"}}],
                "combinator": "and"
            },
            "options": {}
        },
        "id": nid, "name": name,
        "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": pos
    }

n01  = get_node('node-01-schedule')
n02  = get_node('node-02-setdate')
n02b = get_node('node-02b-realtime')
n03  = get_node('node-03-perplexity')
code_qwen     = get_node('node-08-qwen')['parameters']['jsCode']
code_llama    = get_node('node-10-llama')['parameters']['jsCode']
code_markdown = get_node('node-11-markdown')['parameters']['jsCode']
code_save     = get_node('node-12-save')['parameters']['jsCode']
code_tg_ok    = get_node('node-14-tg-ok')['parameters']['jsCode']
code_tg_err   = get_node('node-15-tg-err')['parameters']['jsCode']
code_log      = get_node('node-16-log')['parameters']['jsCode']

workflow = {
    "name": "WEGO 일간 경제브리핑 v3 (Perplexity+GPT+Claude)",
    "nodes": [
        {"parameters": n01['parameters'], "id": "node-01-schedule",
         "name": "S01-Schedule", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.1, "position": [0, 320]},
        {"parameters": n02['parameters'], "id": "node-02-setdate",
         "name": "S02-SetDate", "type": "n8n-nodes-base.set",
         "typeVersion": 3.4, "position": [220, 320]},
        {"parameters": n02b['parameters'], "id": "node-02b-realtime",
         "name": "S02b-Realtime", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [440, 320]},
        {"parameters": n03['parameters'], "id": "node-03-perplexity",
         "name": "S03-Perplexity", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [680, 320]},
        {"parameters": {"jsCode": CODE_GPT_CROSSVAL}, "id": "node-04-gpt",
         "name": "S04-GPT-CrossVal", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [920, 320],
         "notes": "GPT-4o 독립 분석 + 교차검증\nOPENAI_API_KEY 없으면 Perplexity 단독"},
        {"parameters": {"jsCode": CODE_CLAUDE}, "id": "node-05-claude",
         "name": "S05-Claude", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [1160, 320],
         "notes": "claude-sonnet-4-6 교차검증 최종 리포트\nCLAUDE_API_KEY 필요"},
        make_if("node-06-if-claude", "S06-IfClaude", [1400, 320]),
        {"parameters": {"jsCode": code_qwen}, "id": "node-07-qwen",
         "name": "S07-Qwen-Fallback", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [1640, 500]},
        make_if("node-08-if-qwen", "S08-IfQwen", [1880, 500]),
        {"parameters": {"jsCode": code_llama}, "id": "node-09-llama",
         "name": "S09-Llama-Fallback", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [2120, 680]},
        {"parameters": {"jsCode": code_markdown}, "id": "node-10-markdown",
         "name": "S10-Markdown", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [2340, 320]},
        {"parameters": {"jsCode": code_save}, "id": "node-11-save",
         "name": "S11-Save", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [2580, 320]},
        make_if("node-12-if-save", "S12-IfSave", [2820, 320]),
        {"parameters": {"jsCode": code_tg_ok}, "id": "node-13-tg-ok",
         "name": "S13-TgOK", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [3060, 160]},
        {"parameters": {"jsCode": code_tg_err}, "id": "node-14-tg-err",
         "name": "S14-TgErr", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [3060, 500]},
        {"parameters": {"jsCode": code_log}, "id": "node-15-log",
         "name": "S15-Log", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [3300, 320]},
    ],
    "connections": {
        "S01-Schedule":     {"main": [[{"node": "S02-SetDate",      "type": "main", "index": 0}]]},
        "S02-SetDate":      {"main": [[{"node": "S02b-Realtime",    "type": "main", "index": 0}]]},
        "S02b-Realtime":    {"main": [[{"node": "S03-Perplexity",   "type": "main", "index": 0}]]},
        "S03-Perplexity":   {"main": [[{"node": "S04-GPT-CrossVal", "type": "main", "index": 0}]]},
        "S04-GPT-CrossVal": {"main": [[{"node": "S05-Claude",       "type": "main", "index": 0}]]},
        "S05-Claude":       {"main": [[{"node": "S06-IfClaude",     "type": "main", "index": 0}]]},
        "S06-IfClaude": {"main": [
            [{"node": "S10-Markdown",     "type": "main", "index": 0}],
            [{"node": "S07-Qwen-Fallback","type": "main", "index": 0}]
        ]},
        "S07-Qwen-Fallback": {"main": [[{"node": "S08-IfQwen", "type": "main", "index": 0}]]},
        "S08-IfQwen": {"main": [
            [{"node": "S10-Markdown",     "type": "main", "index": 0}],
            [{"node": "S09-Llama-Fallback","type": "main", "index": 0}]
        ]},
        "S09-Llama-Fallback": {"main": [[{"node": "S10-Markdown", "type": "main", "index": 0}]]},
        "S10-Markdown": {"main": [[{"node": "S11-Save",    "type": "main", "index": 0}]]},
        "S11-Save":     {"main": [[{"node": "S12-IfSave",  "type": "main", "index": 0}]]},
        "S12-IfSave": {"main": [
            [{"node": "S13-TgOK",  "type": "main", "index": 0}],
            [{"node": "S14-TgErr", "type": "main", "index": 0}]
        ]},
        "S13-TgOK":  {"main": [[{"node": "S15-Log", "type": "main", "index": 0}]]},
        "S14-TgErr": {"main": [[{"node": "S15-Log", "type": "main", "index": 0}]]},
    },
    "active": False,
    "settings": {"executionOrder": "v1", "saveManualExecutions": True},
    "versionId": "3",
    "meta": {"templateCredsSetupCompleted": True},
    "pinData": {}
}

out = 'D:/git 클로드코드/n8n-workflows/daily-briefing.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("OK nodes:", len(workflow['nodes']))
for n in workflow['nodes']:
    print(f"  {n['id']:25} {n['name']}")
