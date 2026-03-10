"""S03-Perplexity 검색 강화 + S03b-ValidateData 추가 (Finnhub 실시간 검증)"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# ─── 1. S03-Perplexity 시스템 프롬프트 극도 강화 ───────────────────
for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']

        old_system = (
            "const systemPrompt = 'You are a senior Wall Street veteran analyst with 30+ years at Goldman Sachs, '"
            "  + 'Bridgewater Associates, and JPMorgan. Expert in global macro, institutional research synthesis, '"
            "  + 'and Korean market impacts.\\n\\nABSOLUTE RULES:\\n'"
            "  + '1. Every number MUST have source citation (URL or [Publication Name, Date])\\n'"
            "  + '2. If data unverifiable for today, write [미확인] — NEVER fabricate\\n'"
            "  + '3. Cover ALL 6 sections completely\\n'"
            "  + '4. Include legendary investor views (Buffett, Dalio, Burry)\\n'"
            "  + '5. Minimum 5 verified data points per section\\n'"
            "  + '6. Aim for 4000+ words total';"
        )

        new_system = (
            "const systemPrompt = 'You are a senior Wall Street veteran analyst with 30+ years at Goldman Sachs, '"
            "  + 'Bridgewater Associates, and JPMorgan. Expert in global macro, institutional research synthesis, '"
            "  + 'and Korean market impacts.\\n\\n[데이터 정확성 — 필수 준수]\\n'"
            "  + '⚠️ 금융 수치는 생사가 걸린 만큼 극도로 신중하게\\n'"
            "  + '1. 모든 수치에 출처 명시 (URL 또는 [매체명, 시간])\\n'"
            "  + '2. 확인 안 된 수치는 절대 작성 금지 → [미확인] 표기\\n'"
            "  + '3. 전일 종가/지수는 공식 거래소(NYSE, NASDAQ) 데이터만\\n'"
            "  + '4. 의심스러운 수치는 \"다만 [출처명]에서는 X로 보도\"라고 명확히 표기\\n'"
            "  + '5. 실시간·추정치는 \"~로 추정된다\"/\"~로 보인다\" 조건부 표현\\n'"
            "  + '6. 최소 5개 검증된 팩트, 최소 4000자\\n'"
            "  + '[차트·테이블 규칙]\\n'"
            "  + '- S&P 500, NASDAQ, Dow, VIX는 필수 포함\\n'"
            "  + '- 개별주: 최소 6개, 종가·전일비·거래량 필수\\n'"
            "  + '- 오차범위: ±0.5% 초과시 경고\\n'"
            "  + '[할루시네이션 금지]\\n'"
            "  + '- 어제 데이터 없으면 표는 공란 두고 \"[미확인]\" 표기\\n'"
            "  + '- 절대 숫자 추측하거나 평균 내지 말 것'"
        )

        if old_system in code:
            n['parameters']['jsCode'] = code.replace(old_system, new_system)
            print('✅ S03-Perplexity: 검색 프롬프트 극도 강화됨')
        break

# ─── 2. S03b-ValidateData 노드 추가 (Finnhub로 검증) ───────────────
validate_code = r"""// S03b-ValidateData: Perplexity 데이터 vs Finnhub 실시간 주가 비교
const prev = $input.first().json;
const { today, rawContent } = prev;
const FINNHUB_KEY = $env.FINNHUB_API_KEY;

// Finnhub 키 없으면 경고만 하고 통과
let validationResult = {
  status: 'unchecked',
  message: 'Finnhub API key not set — data validation skipped',
  warnings: []
};

if (FINNHUB_KEY && !FINNHUB_KEY.includes('여기에')) {
  const symbols = ['SPY', 'QQQ', 'DIA', 'NVDA', 'TSLA', 'AAPL', 'MSFT'];
  const errors = [];

  try {
    for (const sym of symbols) {
      const resp = await this.helpers.httpRequest({
        method: 'GET',
        url: `https://finnhub.io/api/v1/quote?symbol=${sym}&token=${FINNHUB_KEY}`,
        timeout: 10000
      });

      const r = typeof resp === 'string' ? JSON.parse(resp) : resp;
      const realtimePrice = r.c; // current price
      const change = r.d;        // change
      const changePercent = r.dp; // change percent

      // rawContent에서 같은 ticker 찾아서 비교
      const priceMatch = rawContent.match(new RegExp(sym + '[^0-9]+(\\d+\\.\\d+)', 'i'));
      if (priceMatch) {
        const reportedPrice = parseFloat(priceMatch[1]);
        const priceDiff = Math.abs(reportedPrice - realtimePrice);
        const percentDiff = (priceDiff / realtimePrice) * 100;

        if (percentDiff > 1.0) {
          errors.push(`${sym}: 리포트 $${reportedPrice} vs 실시간 $${realtimePrice} (차이: ${percentDiff.toFixed(2)}%)`);
        }
      }
    }

    if (errors.length > 0) {
      validationResult = {
        status: 'warning',
        message: `⚠️ ${errors.length}개 데이터 불일치 발견`,
        warnings: errors
      };
    } else {
      validationResult = { status: 'passed', message: '✅ 모든 주가 검증 완료' };
    }
  } catch(e) {
    validationResult = { status: 'error', message: `Finnhub API 오류: ${e.message}` };
  }
}

return [{ json: {
  ...prev,
  validationResult,
  validationStatus: validationResult.status,
  validationWarnings: validationResult.warnings || []
} }];
"""

# 노드 추가
s03b_node = {
    "id": "node-03b-validate",
    "name": "S03b-ValidateData",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [920, 320],
    "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": validate_code
    }
}

d['nodes'].append(s03b_node)

# ─── 3. 연결 수정: S03 → S03b → S04 ───────────────────────────────
# S03-Perplexity → S03b-ValidateData
if 'S03-Perplexity' not in d['connections']:
    d['connections']['S03-Perplexity'] = {'main': [[]]}
d['connections']['S03-Perplexity']['main'][0] = [
    {'node': 'S03b-ValidateData', 'type': 'main', 'index': 0}
]

# S03b-ValidateData → S04-GPT-CrossVal
d['connections']['S03b-ValidateData'] = {
    'main': [[{'node': 'S04-GPT-CrossVal', 'type': 'main', 'index': 0}]]
}

# S04-GPT는 기존 S03 연결 제거 (S03b로 대체)
d['connections']['S04-GPT-CrossVal']['main'] = [[{'node': 'S05-Claude', 'type': 'main', 'index': 0}]]

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('✅ S03b-ValidateData 노드 추가 완료')
print('\n⚠️ 다음 단계:')
print('1. finnhub.io 무료 가입 → API 키 받기')
print('2. .env에 FINNHUB_API_KEY=<key> 추가')
print('3. n8n 재시작')
print('\n저장 완료!')
