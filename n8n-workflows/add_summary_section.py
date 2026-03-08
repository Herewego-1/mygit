"""S05-Claude 리포트 맨 아래 핵심 요약 섹션 추가"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    if n['name'] == 'S05-Claude':
        code = n['parameters']['jsCode']

        # 프롬프트 끝 부분의 마지막 섹션 뒤에 요약 섹션 삽입
        old_ending = """---`;"""

        new_ending = """---

## 💡 핵심 요약 (오늘 꼭 알아야 할 것)

> **한 줄 요약**: (오늘 시장 전체를 관통하는 핵심 메시지 1~2문장)

**📌 오늘의 투자 포인트**
| 구분 | 내용 |
|------|------|
| ✅ 긍정 | (상승 모멘텀·매수 관점) |
| ⚠️ 경계 | (리스크·주의 구간) |
| 👀 주목 | (오늘 확인해야 할 핵심 변수) |

**📅 이번 주 주요 일정**
- (날짜): (이벤트/지표 발표)
- (날짜): (이벤트/지표 발표)
- (날짜): (이벤트/지표 발표)

**🎯 단기 시나리오**
- **강세 시나리오**: (조건 + 예상 흐름)
- **약세 시나리오**: (조건 + 예상 흐름)

---`;"""

        if old_ending in code:
            n['parameters']['jsCode'] = code.replace(old_ending, new_ending)
            print('S05-Claude: 핵심 요약 섹션 추가 완료')
        else:
            print('WARNING: 삽입 위치를 찾지 못함')
            print('찾는 문자열:', repr(old_ending))
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
