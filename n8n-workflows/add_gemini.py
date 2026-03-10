"""Gemini를 Claude 실패 시 폴백으로 추가"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# 1. Gemini 코드
gemini_code = r"""// S05b-Gemini: Claude 실패 시 폴백 — Gemini 1.5 Pro
const prev = $input.first().json;
const { rawContent, gptContent, today, obsidianFilePath, backupFilePath,
        startTime, usdKrw, btcUsd, newsSource } = prev;
const KEY = $env.GEMINI_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: { ...prev, success: false, source: 'gemini',
    error: 'GEMINI_API_KEY 미설정', rewrittenContent: null } }];
}

const systemInstruction = '당신은 한국 증권사 리서치센터 수석 애널리스트입니다. '
  + 'Perplexity(팩트·출처)와 GPT(인과관계·해석)의 리서치를 통합 데일리 리포트로 작성하세요.\n\n'
  + '[리포트 구조] 1.전일 미 증시 요약(표) 2.핵심 변화요인 3.섹터·테마별 동향 '
  + '4.한국 증시 시사점 5.FICC 요약 6.리스크·기회 체크포인트 3가지\n'
  + '[형식] 한국어, 증권사 문체, Markdown, 최소 3500자';

const parts = [];
if (rawContent) parts.push('## Perplexity 리서치\n' + rawContent);
if (gptContent) parts.push('## GPT 분석\n' + gptContent);
if (!parts.length) {
  return [{ json: { ...prev, success: false, source: 'gemini',
    error: '리서치 데이터 없음', rewrittenContent: null } }];
}
const userPrompt = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC: ' + btcUsd
  + '\n\n' + parts.join('\n\n') + '\n\n통합 데일리 리포트를 작성하세요.';

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=' + KEY,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      system_instruction: { parts: [{ text: systemInstruction }] },
      contents: [{ role: 'user', parts: [{ text: userPrompt }] }],
      generationConfig: { temperature: 0.3, maxOutputTokens: 8192 }
    }),
    timeout: 90000
  });
  const r = typeof response === 'string' ? JSON.parse(response) : response;
  const report = r?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!report) throw new Error('Gemini 응답 비어있음');
  return [{ json: {
    ...prev, success: true, source: 'gemini', rewrittenContent: report,
    llmModel: 'gemini-1.5-pro', newsSource: newsSource || 'perplexity'
  } }];
} catch(e) {
  return [{ json: { ...prev, success: false, source: 'gemini',
    error: e.message, rewrittenContent: null } }];
}
"""

# 2. 기존 노드 위치 파악
pos = {n['name']: n.get('position', [0, 0]) for n in d['nodes']}
claude_pos = pos.get('S05-Claude', [800, 300])
qwen_pos   = pos.get('S07-Qwen-Fallback', [1200, 300])
gemini_x = claude_pos[0] + 300
gemini_y = claude_pos[1] + 250

# 3. 새 노드 추가
d['nodes'].append({
    "id": "node-05b-gemini", "name": "S05b-Gemini",
    "type": "n8n-nodes-base.code", "typeVersion": 2,
    "position": [gemini_x, gemini_y],
    "parameters": {"mode": "runOnceForAllItems", "jsCode": gemini_code}
})
d['nodes'].append({
    "id": "node-06b-if-gemini", "name": "S06b-IfGemini",
    "type": "n8n-nodes-base.if", "typeVersion": 2,
    "position": [gemini_x + 240, gemini_y],
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "cg1", "leftValue": "={{ $json.success }}",
                           "rightValue": True, "operator": {"type": "boolean", "operation": "true"}}],
            "combinator": "and"
        }, "options": {}
    }
})

# 4. 연결 수정
# S06-IfClaude False → 기존 S07-Qwen → 새로 S05b-Gemini
d['connections']['S06-IfClaude']['main'][1] = [
    {"node": "S05b-Gemini", "type": "main", "index": 0}
]
# S05b-Gemini → S06b-IfGemini
d['connections']['S05b-Gemini'] = {
    "main": [[{"node": "S06b-IfGemini", "type": "main", "index": 0}]]
}
# S06b-IfGemini True → S10-Markdown, False → S07-Qwen-Fallback
d['connections']['S06b-IfGemini'] = {
    "main": [
        [{"node": "S10-Markdown", "type": "main", "index": 0}],
        [{"node": "S07-Qwen-Fallback", "type": "main", "index": 0}]
    ]
}

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# 검증
with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)
print('총 노드 수:', len(d2['nodes']))
print('S06-IfClaude False →', d2['connections']['S06-IfClaude']['main'][1])
print('S05b-Gemini →', d2['connections'].get('S05b-Gemini'))
print('S06b-IfGemini →', d2['connections'].get('S06b-IfGemini'))
print('완료!')
