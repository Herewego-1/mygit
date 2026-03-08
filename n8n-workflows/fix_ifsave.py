import json, sys

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    # Fix 1: S12-IfSave -> saveSuccess 기준으로 변경
    if n['id'] == 'node-12-if-save':
        old = n['parameters']['conditions']['conditions'][0]['leftValue']
        n['parameters']['conditions']['conditions'][0]['leftValue'] = r'={{ $json.saveSuccess }}'
        print('[Fix 1] S12-IfSave:', old, '->', r'={{ $json.saveSuccess }}')

    # Fix 2: Claude 모델명 수정
    if n['id'] == 'node-05-claude':
        code = n['parameters']['jsCode']
        if "'claude-sonnet-4-6'" in code:
            code = code.replace("'claude-sonnet-4-6'", "'claude-sonnet-4-5'")
            n['parameters']['jsCode'] = code
            print('[Fix 2] S05-Claude: claude-sonnet-4-6 -> claude-sonnet-4-5')
        else:
            for line in code.split('\n'):
                if 'model' in line and 'claude' in line.lower():
                    print('[Info] S05 current model line:', line.strip())

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('Done - saved OK')
