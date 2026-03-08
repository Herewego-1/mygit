const fs = require('fs');
const FILE = 'D:/git 클로드코드/n8n-workflows/daily-briefing.json';

const NEW_NODE08_CODE = `// ============================================================
// 노드 8: Qwen2.5:7B 한국어 리라이팅 (Ollama 로컬)
// 8개 섹션 심층 분석 / 최소 3500자 / 월가+유명투자자 관점
// ============================================================
const prev = $input.first().json;
const { rawContent, today, obsidianFilePath, backupFilePath, startTime } = prev;
const newsSource = prev.source || prev.newsSource;
const HOST  = 'http://127.0.0.1:11434';
const MODEL = 'qwen2.5:7b';
const pass = { today, obsidianFilePath, backupFilePath, startTime, newsSource };

const sys = \`당신은 골드만삭스·브리지워터·JP모건 출신 30년 경력의 월가 베테랑 애널리스트입니다.
한국 기관투자자와 개인투자자를 위한 최고 수준의 심층 경제 브리핑을 작성합니다.

[절대 규칙]
1. 한국어만 사용 (고유명사·수치·단위·기관명·ETF 티커 제외)
2. 문체: ~다, ~음, ~임 (뉴스레터 스타일, 존댓말 절대 금지)
3. 수치: $, %, bp, 원 단위 원문 그대로 유지
4. 마크다운 엄수: ### #### - > ** 등
5. 절대 금지: 중국어 혼용, 번역투, 내용 생략, 데이터 추가 생성
6. 최소 3500자 이상 (각 섹션 충분히 상세하게)
7. 원문에 없는 데이터 절대 추가 금지 (hallucination 방지)
8. 유명 투자자 견해 반드시 포함 (버핏·달리오·버리 등)\`;

const usr = \`오늘은 \${today}입니다. 아래 영문 금융 데이터를 월가 베테랑 관점의 심층 한국어 브리핑으로 작성하세요. 반드시 3500자 이상. 원문에 있는 정보만 활용하세요.

## 원문 데이터
\${rawContent}

## 출력 형식 (8개 섹션 모두 필수)

### 🌍 세계 시장 동향
#### 미국 증시
- **현황**: S&P500·나스닥·다우·러셀2000 수치와 변동폭
- **섹터 흐름**: 11개 섹터 중 상승/하락 주도 섹터
- **월가 시각**: 주요 기관 평가

#### 유럽·아시아 시장
- 유럽 주요 지수 (STOXX600·DAX·FTSE100·CAC40)
- 아시아 주요 지수 (닛케이·항셍·CSI300·ASX200)
- 글로벌 센티먼트 지표

---

### 🇺🇸 미국 시장 심층 분석
#### 금리·채권
- **국채 수익률 곡선**: 2년물/10년물/30년물 수준, 정상/역전 여부 해석
- **연준(Fed)**: 현재 금리, 다음 FOMC 일정, 인하 확률 (CME FedWatch)

#### 공포·탐욕 지표
- **VIX**: 현재 수준과 의미 (15↓안정, 15-25보통, 25↑경계, 35↑공황)
- **DXY**: 달러 인덱스 수준과 신흥국/원화 영향

---

### 🇰🇷 국내 시장 분석
#### KOSPI·KOSDAQ
- 지수 수준, 등락폭, 주요 섹터
- 외국인·기관·개인 순매수/순매도

#### 주요 종목
- 삼성전자·SK하이닉스·NAVER 등 핵심 종목 동향

#### 원/달러 환율
- 현재 환율, 추세, 한국은행 기준금리 현황

---

### 📈 ETF·채권 동향
#### 미국 ETF
- SPY·QQQ·VTI·IWM — 등락폭과 거래량 특이사항
- 섹터 ETF 중 주목할 움직임

#### 채권 ETF
- AGG·TLT — 등락폭, 10년물 국채 금리와의 관계

---

### 📊 버핏 지표 & 핵심 거시 지표
#### 밸류에이션 지표
- **버핏 지표** (시총/GDP): 현재 수준과 과열/저평가 해석
- **쉴러 CAPE P/E**: 현재 수준 vs 역사적 평균(16.8), 향후 10년 수익률 시사점

#### 경기 지표
- **ISM PMI**: 제조업·서비스업 PMI (50 기준 확장/수축 판단)
- **고용·물가**: 비농업 고용·초기실업수당·CPI·PCE 최신 수치
- **신용 스프레드**: IG·HY 스프레드 — 리스크 온/오프 신호

---

### 🏆 유명 투자자 & 기관 리서치
#### 워렌 버핏 / 버크셔 해서웨이
- 최근 13F 포지션, 매수/매도 종목, 현금 보유액, 최근 발언

#### 레이 달리오 / 브리지워터
- 최신 매크로 견해, 올웨더 포트폴리오 스탠스, 발표 자료

#### 마이클 버리 / Scion
- 최근 13F 포지션, 현재 투자 테마

#### 골드만삭스 / JP모건 / 모건스탠리
- S&P500 연말 목표가, 섹터 추천, 핵심 매크로 전망
- 주요 애널리스트 액션 (업그레이드/다운그레이드)

---

### 💡 오늘의 핵심 인사이트
> 월가 베테랑 관점에서 오늘 가장 중요한 5가지 흐름

1. **[첫째]**: [구체적 수치 포함한 핵심 포인트]
2. **[둘째]**: [구체적 수치 포함]
3. **[셋째]**: [구체적 수치 포함]
4. **[넷째]**: [구체적 수치 포함]
5. **[다섯째]**: [구체적 수치 포함]

---

### ⚠️ 리스크 & 기회 요인
#### 단기 리스크
- 주의해야 할 구체적 위험 요소 (지정학·금리·기업실적 등)
- 한국 투자자에게 특히 중요한 리스크

#### 기회 요인
- 현재 시장에서 주목할 만한 섹터/자산/전략
- 유명 투자자들이 보는 기회 포인트\`;

try {
  const r = await this.helpers.httpRequest({
    method: 'POST',
    url: \`\${HOST}/api/generate\`,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL,
      prompt: \`<|im_start|>system\n\${sys}<|im_end|>\n<|im_start|>user\n\${usr}<|im_end|>\n<|im_start|>assistant\n\`,
      stream: false,
      options: { temperature: 0.3, num_predict: 6000, top_k: 40, top_p: 0.9, repeat_penalty: 1.05 }
    }),
    timeout: 120000
  });

  const rewritten = r.response;
  if (!rewritten || rewritten.trim().length < 1000)
    throw new Error(\`응답 부실 (\${rewritten?.length || 0}자)\`);

  const zhChars = (rewritten.match(/[\u4e00-\u9fff]/g) || []).length;
  if (zhChars > 15) throw new Error(\`중국어 \${zhChars}자 감지 — Llama Fallback 필요\`);

  return [{ json: {
    success: true, source: 'qwen', model: MODEL,
    rewrittenContent: rewritten, rawContent, ...pass
  }}];

} catch(e) {
  return [{ json: { success: false, source: 'qwen', error: e.message, rawContent, ...pass } }];
}`;

// JSON 파일 로드 및 수정
const raw = fs.readFileSync(FILE, 'utf8');
const data = JSON.parse(raw);

let updated = false;
for (const node of data.nodes) {
  if (node.id === 'node-08-qwen') {
    node.parameters.jsCode = NEW_NODE08_CODE;
    node.notes = 'Ollama Qwen2.5:7B 로컬 호출 (비용 0원)\n8개 섹션: 세계/미국/한국/ETF/버핏지표/유명투자자/인사이트/리스크\n최소 3500자 / num_predict: 6000';
    updated = true;
    console.log('✅ node-08 업데이트 완료');
    console.log('HOST 포함:', NEW_NODE08_CODE.includes("'http://127.0.0.1:11434'"));
    console.log('MODEL 포함:', NEW_NODE08_CODE.includes("'qwen2.5:7b'"));
    console.log('const HOST:', NEW_NODE08_CODE.includes('const HOST'));
    console.log('코드 길이:', NEW_NODE08_CODE.length);
  }
}

if (!updated) {
  console.error('ERROR: node-08-qwen를 찾지 못함');
  process.exit(1);
}

fs.writeFileSync(FILE, JSON.stringify(data, null, 2), 'utf8');
console.log('✅ 파일 저장 완료');

// 검증
const verify = JSON.parse(fs.readFileSync(FILE, 'utf8'));
const n = verify.nodes.find(n => n.id === 'node-08-qwen');
console.log('검증 - const HOST:', n.parameters.jsCode.includes('const HOST'));
console.log('검증 - 127.0.0.1:', n.parameters.jsCode.includes('127.0.0.1'));
console.log('검증 - JP모건:', n.parameters.jsCode.includes('JP모건'));
console.log('검증 - 버핏:', n.parameters.jsCode.includes('버핏'));
