# WEGO AI 자동화 시스템
> 경제 브리핑 → 유튜브 → 블로그 → ETF 분석 자동 파이프라인

**현재 단계**: Phase 1 — 경제브리핑 자동화 **v3** (Perplexity + GPT-4o + Claude 교차검증)

---

## 📁 프로젝트 구조

```
D:\git 클로드코드\
├── n8n-workflows\
│   └── daily-briefing.json   ← ✅ v3 완성 (16노드, 3단계 AI 파이프라인)
├── prompts\
│   ├── perplexity-briefing.md  ← Perplexity 리서치 프롬프트
│   └── qwen-rewrite-kr.md      ← Qwen 폴백 프롬프트
├── .env.example              ← API 키 템플릿
└── README.md

D:\Obsidian\                  ← Vault 폴더
├── 경제브리핑\  (일간 자동저장)
├── 유튜브스크립트\
├── 블로그포스트\
├── ETF분석\
└── 혜택리서치\
```

---

## 🏗 v3 아키텍처 (PDF 인계 기반)

```
📅 스케줄 (평일 7:30AM KST)
    ↓
📋 날짜·경로 변수 세팅
    ↓
📡 실시간 가격 수집 (USD/KRW, BTC/USD)
    ↓
🔍 STEP 1A: Perplexity sonar-pro
   팩트·출처 중심 리서치 (6섹션)
    ↓
🤖 STEP 1B: GPT-4o 독립 분석 (OPENAI_API_KEY 있을 때)
   인과관계·시나리오 해석 중심
   (없으면 Perplexity 단독으로 진행)
    ↓
✨ STEP 2: Claude sonnet-4-6 교차검증 최종 리포트
   - 공통사실 → 확정 서술
   - Perplexity만 → 출처 기반 참고
   - GPT만 → 추정/시나리오
   - 상충 → 양론 병기
   최소 3500자 한국어 리포트
    ↓
✅ Claude 성공?
    │ YES → 📝 최종 마크다운 생성
    │ NO  ↓
    │  🔄 Qwen2.5:7b 로컬 폴백
    │      ↓
    │  ✅ Qwen 성공?
    │      │ YES → 📝 최종 마크다운 생성
    │      │ NO  → 🔄 Llama3.1 폴백 → 📝 마크다운
    ↓
💾 Obsidian 파일 저장 (D:\Obsidian\경제브리핑\YYYY-MM-DD.md)
    ↓
✅ 저장 성공?
    YES → 📱 Telegram 성공 알림
    NO  → 📱 Telegram 에러 알림
    ↓
📊 실행 로그 기록 (JSON)
```

---

## ⚡ n8n 워크플로 가져오기

### 1단계: n8n 변수 등록 (`$vars`)

`http://localhost:5678` → **Settings → Variables** 에서 등록:

| 변수명 | 값 | 필수 |
|--------|---|------|
| `PERPLEXITY_API_KEY` | `pplx-xxxxx` | ✅ 필수 |
| `OBSIDIAN_VAULT_PATH` | `D:\Obsidian` | ✅ 필수 |
| `CLAUDE_API_KEY` | `sk-ant-xxxxx` | ✅ 권장 (없으면 Qwen 폴백) |
| `OPENAI_API_KEY` | `sk-xxxxx` | 선택 (없으면 Perplexity 단독) |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | 선택 (폴백용) |
| `OLLAMA_MODEL` | `qwen2.5:7b` | 선택 |
| `TELEGRAM_BOT_TOKEN` | `봇토큰` | 선택 |
| `TELEGRAM_CHAT_ID` | `채팅ID` | 선택 |

### 2단계: 워크플로 가져오기
1. n8n 왼쪽 메뉴 → **Workflows**
2. 우측 상단 **"..."** → **Import from file**
3. `D:\git 클로드코드\n8n-workflows\daily-briefing.json` 선택
4. **Import** 클릭

### 3단계: 수동 테스트
1. 가져온 워크플로 열기
2. 좌측 상단 **"Test workflow"** 클릭
3. S05-Claude 노드 출력에서 `rewrittenContent` 확인
4. `D:\Obsidian\경제브리핑\` 폴더에 파일 생성 확인

### 4단계: 스케줄 활성화
워크플로 우측 상단 토글 → **Active** 전환 → 다음 평일 7:30AM 자동 실행

---

## 🛠 트러블슈팅

### Claude API 오류
```
CLAUDE_API_KEY 미설정 → Qwen 폴백 자동 실행
→ n8n Settings > Variables에서 CLAUDE_API_KEY 등록
```

### GPT-4o 연결 안 됨
```
OPENAI_API_KEY 미설정 → Perplexity 단독으로 자동 진행 (정상)
→ GPT 추가하려면 Variables에 OPENAI_API_KEY 등록
```

### Ollama 응답 없음 (Claude 폴백 시)
```bash
curl http://localhost:11434/api/tags
ollama list | grep qwen
# 없으면: ollama pull qwen2.5:7b
```

### Obsidian 저장 실패
```
→ D:\Obsidian\경제브리핑\ 폴더 존재 여부 확인
→ C:\temp\wego-backup-날짜.md 백업 자동 생성됨
```

---

## 📅 90일 로드맵

| Phase | 기간 | 목표 | 상태 |
|-------|------|------|------|
| **1** | Day 1~30 | 경제브리핑 자동화 | 🟡 진행중 |
| **2** | Day 31~60 | 유튜브 스크립트 | ⬜ 예정 |
| **3** | Day 61~75 | 블로그 & SNS | ⬜ 예정 |
| **4** | Day 76~85 | ETF 주간 분석 | ⬜ 예정 |
| **5** | Day 86~90 | 주간 혜택 리서치 | ⬜ 예정 |

---

## ✅ Phase 1 체크리스트

- [x] n8n 경제브리핑 워크플로 JSON v3 (16노드)
- [x] Perplexity sonar-pro 리서치 (6섹션)
- [x] GPT-4o 독립 분석 노드 (교차검증 Step 1B)
- [x] Claude API 교차검증 최종 리포트 (Step 2)
- [x] Qwen/Llama 3중 폴백 체계
- [x] Obsidian Vault 폴더 구조
- [x] .env.example 파일
- [ ] n8n Variables 등록 (수동 - 위 1단계 참고)
- [ ] 수동 테스트 실행 5회
- [ ] Telegram 봇 생성 (@BotFather)
- [ ] 7일 연속 자동 실행 성공 확인
