"""Compliance Notice 제거 후 한국 증권사 표준 면책문구로 교체"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']

        old = r"""    rawContent = r.choices[0].message.content;
    // Compliance Notice / 면책문구 자동 제거
    rawContent = rawContent
      .replace(/\*?\*?Compliance Notice\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?Disclaimer\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?면책\s*고지\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?투자\s*유의\s*사항\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/This (information|report|content) is (for|provided for) (informational|educational)[\s\S]*?(?=\n#|\n\*\*|\n\n\n|$)/gi, '')
      .trim();
    success = true;"""

        new = r"""    rawContent = r.choices[0].message.content;
    // Compliance Notice / 외부 면책문구 제거 후 증권사 표준 문구로 교체
    rawContent = rawContent
      .replace(/\*?\*?Compliance Notice\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?Disclaimer\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?면책\s*고지\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?투자\s*유의\s*사항\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/This (information|report|content) is (for|provided for) (informational|educational)[\s\S]*?(?=\n#|\n\*\*|\n\n\n|$)/gi, '')
      .trim();
    // 증권사 표준 면책문구 추가
    rawContent += '\n\n---\n'
      + '> **[투자유의사항]** 본 자료는 투자자의 투자 판단을 돕기 위한 참고 자료이며, '
      + '당사의 공식 의견이 아닙니다. 본 자료에 수록된 내용은 신뢰할 수 있는 출처로부터 '
      + '작성되었으나 그 정확성·완전성을 보장하지 않습니다. '
      + '**투자의 최종 판단 및 책임은 전적으로 투자자 본인에게 있으며**, '
      + '본 자료는 어떠한 경우에도 투자 결과에 대한 법적 책임의 근거로 사용될 수 없습니다.';
    success = true;"""

        if old in code:
            n['parameters']['jsCode'] = code.replace(old, new)
            print('S03-Perplexity: 표준 면책문구로 교체 완료')
        else:
            print('WARNING: 삽입 위치 못 찾음, 직접 확인 필요')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
