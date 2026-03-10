"""경제지표·기업실적 섹션 추가
1. S03-Perplexity: 검색 범위에 경제지표·실적 추가
2. S05-Claude: 리포트에 경제지표·실적 섹션 추가
"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# ─── 1. S03-Perplexity 유저 프롬프트 확장 ───────────────────────────────
for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']
        old_prompt = (
            "  + '형식: 한국어, 증권사 문체, Markdown, 최소 3500자';"
        )
        new_prompt = (
            "  + '형식: 한국어, 증권사 문체, Markdown, 최소 3500자\\n\\n'\n"
            "  + '7. 전일 발표 주요 경제지표 (지표명 | 예상치 | 실제치 | 서프라이즈 방향)\\n'\n"
            "  + '8. 주요 기업 실적 발표 (기업명 | EPS 예상/실제 | 매출 예상/실제 | 가이던스 방향)\\n'\n"
            "  + '9. 이번 주 남은 주요 일정 (날짜·시간·항목·예상치)';"
        )
        if old_prompt in code:
            n['parameters']['jsCode'] = code.replace(old_prompt, new_prompt)
            print('S03-Perplexity: 경제지표·실적 검색 요청 추가됨')
        else:
            print('WARNING S03: 삽입 위치 못 찾음')
        break

# ─── 2. S05-Claude 프롬프트에 새 섹션 추가 ───────────────────────────────
for n in d['nodes']:
    if n['name'] == 'S05-Claude':
        code = n['parameters']['jsCode']

        # ⚠️ 오늘의 체크포인트 섹션 앞에 두 섹션 삽입
        old_section = "## ⚠️ 오늘의 체크포인트"
        new_sections = """## 📊 주요 경제지표 발표

| 지표 | 기간 | 예상치 | 실제치 | 서프라이즈 |
|------|------|--------|--------|-----------|
| (예: CPI YoY) | | | | ▲상회/▼하회/─부합 |
| (예: 실업률) | | | | |
| (예: ISM 제조업) | | | | |

> **시장 반응**: (지표 발표 후 시장 반응 1~2문장 서술)

---

## 📋 주요 기업 실적

| 기업 | EPS 예상 | EPS 실제 | 매출 예상 | 매출 실제 | 가이던스 |
|------|---------|---------|---------|---------|---------|
| | | | | | ▲상향/▼하향/─유지 |

> **실적 시즌 흐름**: (전반적인 실적 시즌 평가 1~2문장)

---

## ⚠️ 오늘의 체크포인트"""

        if old_section in code:
            n['parameters']['jsCode'] = code.replace(old_section, new_sections)
            print('S05-Claude: 경제지표·실적 섹션 추가됨')
        else:
            print('WARNING S05: 삽입 위치 못 찾음')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
