# Perplexity 경제브리핑 리서치 프롬프트
> Day 1~3 | v1.0 | 2026-03-05

---

## 개요

n8n 노드 3 (`🔍 Perplexity 뉴스 수집`)에서 사용하는
Perplexity sonar 모델 호출용 프롬프트 템플릿.

---

## 🔧 API 설정

```
엔드포인트: https://api.perplexity.ai/chat/completions
모델      : sonar  (실시간 웹검색 특화)
temperature: 0.2   (낮을수록 팩트 중심)
max_tokens : 3000
citations  : true  (출처 자동 포함)
timeout    : 10,000ms (10초)
```

---

## 📌 시스템 프롬프트

```
You are a professional financial news analyst specializing in global markets
and Korean investors.
Provide accurate, data-driven summaries.
Always include specific numbers: prices, %, basis points, index levels.
```

---

## 📝 유저 프롬프트 템플릿

> `{{today}}` = 오늘 날짜 (예: 2026-03-05)

```
Today is {{today}} (KST). Provide:

[GLOBAL MARKETS — 5 items]
1. US markets: S&P500, NASDAQ, Dow — index levels & % change
2. Federal Reserve / interest rate news or expectations
3. Economic indicators: CPI, employment, PMI, GDP
4. Geopolitical events impacting markets
5. Commodities: crude oil (WTI/Brent), gold spot, BTC

[KOREAN MARKETS — 3 items]
1. KOSPI / KOSDAQ — index level & % change
2. KRW/USD exchange rate — current level & trend
3. Top moving Korean stocks or notable sectors (e.g. semiconductors, EV)

[ETF WATCH — 2 items]
1. SPY, QQQ, VTI — weekly performance & notable flows
2. AGG, EEM — notable moves or inflows/outflows

For EACH item use EXACTLY this format:
Title: [concise English title]
Data: [key numbers and figures]
Summary: [2-3 sentence factual summary]
Impact: [what this means for Korean retail investors]
Source: [publication or data source name]
```

---

## 🎯 Perplexity 응답 파싱 로직

```javascript
// n8n Code 노드에서 응답 추출
const content = response?.choices?.[0]?.message?.content;

// 품질 검사
if (!content || content.trim().length < 200) {
  throw new Error(`응답 부실: ${content?.length || 0}자`);
}

// 섹션 분리 (선택 사항)
const globalSection  = content.match(/\[GLOBAL MARKETS[\s\S]*?\[KOREAN/)?.[0];
const koreanSection  = content.match(/\[KOREAN MARKETS[\s\S]*?\[ETF/)?.[0];
const etfSection     = content.match(/\[ETF WATCH[\s\S]*/)?.[0];
```

---

## 📊 예상 응답 구조

```
[GLOBAL MARKETS — 5 items]

Title: S&P 500 Closes Flat Amid Fed Uncertainty
Data: S&P 500: 5,842 (+0.02%), NASDAQ: 18,305 (-0.3%)
Summary: US equities traded in a narrow range as investors awaited...
Impact: 미국 시장 보합세는 한국 수출주에 단기 영향 제한적...
Source: Bloomberg, Reuters

Title: Fed Officials Signal Cautious Approach to Rate Cuts
...
```

---

## 🔄 Fallback 쿼리 (Gemini용)

Perplexity 실패 시 Gemini에 전달하는 단순화 버전:

```
Today is {{today}} (KST). Financial news summary:

[GLOBAL-5] US markets(S&P500/NASDAQ/Dow levels+%), Fed/rates,
CPI/jobs/PMI, Geopolitics, Oil(WTI)/Gold/BTC

[KOREAN-3] KOSPI/KOSDAQ index+%, KRW/USD rate,
Top Korean stocks/sectors

[ETF-2] SPY/QQQ/VTI week performance, AGG/EEM notable moves

Format: Title | Data(numbers) | Summary(2-3s) | Korean investor impact
```

---

## 📅 Phase 1 꼬리질문 대응

| 질문 | 해결책 |
|------|--------|
| 응답이 중국어/영어 혼합? | Qwen 프롬프트에 "한국어만" 재강조 |
| 주말에 실행 안 하려면? | Cron `0 7 * * 1-5` 유지 (이미 설정됨) |
| 하루 2회 생성? | Cron `0 7,15 * * 1-5` 로 변경 |
| API 비용 초과? | n8n에서 일일 실행 카운터 추가 |

---

*Phase 1 Day 1~3 — 태스크 1 참조 프롬프트*
