"""Update Gemini model from 1.5 Pro to 3.1 Pro Preview"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    if n['name'] == 'S05b-Gemini':
        code = n['parameters']['jsCode']
        code = code.replace(
            'gemini-1.5-pro:generateContent',
            'gemini-3.1-pro-preview:generateContent'
        ).replace(
            "llmModel: 'gemini-1.5-pro'",
            "llmModel: 'gemini-3.1-pro-preview'"
        ).replace(
            'Gemini 1.5 Pro',
            'Gemini 3.1 Pro'
        )
        n['parameters']['jsCode'] = code
        print('Updated node S05b-Gemini')
        print('gemini-3.1-pro-preview in code:', 'gemini-3.1-pro-preview' in code)
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('Saved!')
