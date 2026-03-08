"""Grok을 Gemini 실패 시 폴백으로 추가 (Claude→Gemini→Grok→Qwen→Llama)"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# 1. Grok 코드 (xAI OpenAI-compatible API)
grok_code = r"""// S07b-Grok: Gemini 실패 시 폴백 — Grok 3
const prev = $input.first().json;
const { rawContent, gptContent, today, obsidianFilePath, backupFilePath,
        startTime, usdKrw, btcUsd, newsSource } = prev;
const KEY = $env.GROK_API_KEY;

if (!KEY || KEY.includes('여기에')) {
  return [{ json: { ...prev, success: false, source: 'grok',
    error: 'GROK_API_KEY 미설정', rewrittenContent: null } }];
}

const systemPrompt = '당신은 한국 증권사 리서치센터 수석 애널리스트입니다. '
  + 'Perplexity(팩트·출처)와 GPT(인과관계·해석)의 리서치를 통합 데일리 리포트로 작성하세요.\n\n'
  + '[리포트 구조] 1.전일 미 증시 요약(표) 2.핵심 변화요인 3.섹터·테마별 동향 '
  + '4.한국 증시 시사점 5.FICC 요약 6.리스크·기회 체크포인트 3가지\n'
  + '[형식] 한국어, 증권사 문체, Markdown, 최소 3500자';

const parts = [];
if (rawContent) parts.push('## Perplexity 리서치\n' + rawContent);
if (gptContent) parts.push('## GPT 분석\n' + gptContent);
if (!parts.length) {
  return [{ json: { ...prev, success: false, source: 'grok',
    error: '리서치 데이터 없음', rewrittenContent: null } }];
}
const userPrompt = '날짜: ' + today + ' | USD/KRW: ' + usdKrw + ' | BTC: ' + btcUsd
  + '\n\n' + parts.join('\n\n') + '\n\n통합 데일리 리포트를 작성하세요.';

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.x.ai/v1/chat/completions',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + KEY
    },
    body: JSON.stringify({
      model: 'grok-3',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3,
      max_tokens: 8192
    }),
    timeout: 90000
  });
  const r = typeof response === 'string' ? JSON.parse(response) : response;
  const report = r?.choices?.[0]?.message?.content;
  if (!report) throw new Error('Grok 응답 비어있음');
  return [{ json: {
    ...prev, success: true, source: 'grok', rewrittenContent: report,
    llmModel: 'grok-3', newsSource: newsSource || 'perplexity'
  } }];
} catch(e) {
  return [{ json: { ...prev, success: false, source: 'grok',
    error: e.message, rewrittenContent: null } }];
}
"""

# 2. 기존 노드 위치 파악
pos = {n['name']: n.get('position', [0, 0]) for n in d['nodes']}
gemini_pos = pos.get('S05b-Gemini', [1460, 570])
if_gemini_pos = pos.get('S06b-IfGemini', [1700, 570])

grok_x = if_gemini_pos[0] + 240
grok_y = if_gemini_pos[1] + 150
if_grok_x = grok_x + 240

# 3. 새 노드 추가
d['nodes'].append({
    "id": "node-07b-grok", "name": "S07b-Grok",
    "type": "n8n-nodes-base.code", "typeVersion": 2,
    "position": [grok_x, grok_y],
    "parameters": {"mode": "runOnceForAllItems", "jsCode": grok_code}
})
d['nodes'].append({
    "id": "node-08b-if-grok", "name": "S08b-IfGrok",
    "type": "n8n-nodes-base.if", "typeVersion": 2,
    "position": [if_grok_x, grok_y],
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "cg2", "leftValue": "={{ $json.success }}",
                           "rightValue": True, "operator": {"type": "boolean", "operation": "true"}}],
            "combinator": "and"
        }, "options": {}
    }
})

# 4. 연결 수정
# S06b-IfGemini False → 기존 S07-Qwen → 새로 S07b-Grok
d['connections']['S06b-IfGemini']['main'][1] = [
    {"node": "S07b-Grok", "type": "main", "index": 0}
]
# S07b-Grok → S08b-IfGrok
d['connections']['S07b-Grok'] = {
    "main": [[{"node": "S08b-IfGrok", "type": "main", "index": 0}]]
}
# S08b-IfGrok True → S10-Markdown, False → S07-Qwen-Fallback
d['connections']['S08b-IfGrok'] = {
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
print('S06b-IfGemini False ->', d2['connections']['S06b-IfGemini']['main'][1])
print('S07b-Grok ->', d2['connections'].get('S07b-Grok'))
print('S08b-IfGrok ->', d2['connections'].get('S08b-IfGrok'))
print('완료!')
