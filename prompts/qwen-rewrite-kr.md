# Qwen2.5:7B 한국어 리라이팅 프롬프트 템플릿
> **태스크 2** (Day 4~6) | v1.0 | 2026-03-05

---

## 개요

Perplexity/Gemini 영문 금융 뉴스 → Qwen2.5:7B 로컬 모델 → 한국어 브리핑 변환

---

## 🔧 Ollama 호출 설정

```
엔드포인트 : http://localhost:11434/api/generate
모델       : qwen2.5:7b
stream     : false
temperature: 0.3
num_predict: 3000
top_k      : 40
top_p      : 0.9
repeat_pen : 1.1
timeout    : 120,000ms (2분)
```

---

## 📌 시스템 프롬프트

```
당신은 전문 금융 저널리스트입니다.
영문 금융 뉴스를 한국 독자를 위한 자연스러운 한국어 브리핑으로 변환합니다.

[반드시 지킬 규칙]
1. 한국어만 사용 (고유명사·수치·단위 제외)
2. 비존댓말: ~다, ~음, ~함 (뉴스레터 스타일, 존댓말 금지)
3. 각 항목 150~200자 이내
4. 수치: $, %, bp 그대로 표시 (원화 환산 불필요)
5. 마크다운 형식만 사용 (## ### - > 등)
6. 절대 금지: 중국어 혼용, 번역투, ~습니다 존댓말
```

---

## 📝 유저 프롬프트 템플릿

> `{{today}}` = 오늘 날짜
> `{{rawContent}}` = Perplexity/Gemini 영문 원문

```
오늘은 {{today}}입니다. 아래 영문 금융 뉴스를 한국어 브리핑으로 변환해주세요.

## 변환 대상
{{rawContent}}

## 출력 형식 (반드시 준수)

### 🌐 글로벌 시장 (5개 항목)
각 항목:
#### [번호]. [제목]
- **상황**: 무슨 일이 일어났는지
- **수치**: 핵심 숫자/퍼센트
- **의미**: 투자자에게 어떤 영향인지

### 🇰🇷 국내 시장 (3개 항목)
(동일 형식)

### 📈 ETF 동향 (2개 항목)
(동일 형식)

### 💡 오늘의 핵심 포인트
- 가장 중요한 흐름 3가지 (한 문장씩)
```

---

## 🔤 n8n용 ChatML 완성 형식

```javascript
// n8n Code 노드의 prompt 필드
const prompt =
  `<|im_start|>system\n${systemPrompt}<|im_end|>\n` +
  `<|im_start|>user\n${userPrompt}<|im_end|>\n` +
  `<|im_start|>assistant\n`;
```

---

## ⚠️ 에러 처리

### 중국어 혼용 감지
```javascript
const zhChars = (rewritten.match(/[\u4e00-\u9fff]/g) || []).length;
if (zhChars > 15) throw new Error(`중국어 ${zhChars}자 감지`);
```
**해결**: `repeat_penalty` 1.2로 올리거나 Llama Fallback

### 응답 너무 짧음 (300자 미만)
**해결**: `num_predict` 3000 → 4000

### 번역투 ("~하였습니다")
시스템 프롬프트 예시 추가:
```
[좋은 예] "연준이 금리를 0.25bp 인상했다"
[나쁜 예] "연준이 금리를 인상하였습니다" ← 금지
```

### 타임아웃 (2분 초과)
**해결**: `num_predict` 2000으로 줄이기

---

## 📊 입출력 JSON 스키마

### 입력
```json
{
  "today": "2026-03-05",
  "rawContent": "Title: Fed Holds Rates...\nData: 5.25%-5.5%...",
  "obsidianFilePath": "D:\\Obsidian\\경제브리핑\\2026-03-05.md",
  "newsSource": "perplexity"
}
```

### 출력 (성공)
```json
{
  "success": true,
  "source": "qwen",
  "model": "qwen2.5:7b",
  "rewrittenContent": "### 🌐 글로벌 시장...",
  "rawContent": "(원문 보존)"
}
```

### 출력 (실패)
```json
{
  "success": false,
  "source": "qwen",
  "error": "중국어 23자 감지 — Llama Fallback 필요",
  "rawContent": "(원문 보존 — Llama에서 재사용)"
}
```

---

## 🧪 터미널 수동 테스트

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "<|im_start|>system\n당신은 금융 저널리스트. 비존댓말로.<|im_end|>\n<|im_start|>user\n\"Fed holds rates at 5.25%\" 한국어로 변환.<|im_end|>\n<|im_start|>assistant\n",
  "stream": false,
  "options": {"temperature": 0.3, "num_predict": 100}
}' | python -m json.tool | grep response
```

**기대 출력**: `"response": "연준이 5.25% 금리를 동결했다..."`

---

*Phase 1 Day 4~6 — 태스크 2 완료*
