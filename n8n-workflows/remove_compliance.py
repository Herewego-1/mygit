"""S03-Perplexity: rawContent에서 Compliance Notice 자동 제거"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']
        # rawContent 설정 후 compliance 제거 로직 삽입
        old = "    rawContent = r.choices[0].message.content;\n    success = true;"
        new = r"""    rawContent = r.choices[0].message.content;
    // Compliance Notice / 면책문구 자동 제거
    rawContent = rawContent
      .replace(/\*?\*?Compliance Notice\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?Disclaimer\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?면책\s*고지\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/\*?\*?투자\s*유의\s*사항\*?\*?[\s\S]*?(?=\n#|\n\*\*|$)/gi, '')
      .replace(/This (information|report|content) is (for|provided for) (informational|educational)[\s\S]*?(?=\n#|\n\*\*|\n\n\n|$)/gi, '')
      .trim();
    success = true;"""
        if old in code:
            n['parameters']['jsCode'] = code.replace(old, new)
            print('S03-Perplexity: Compliance Notice 제거 로직 추가됨')
        else:
            print('WARNING: 삽입 위치를 찾지 못함')
            print('찾는 문자열:', repr(old[:50]))
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
