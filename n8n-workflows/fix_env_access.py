"""$env.XXX → process.env.XXX 전체 노드에서 일괄 교체"""
import json, re

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

count = 0
for n in d['nodes']:
    if n.get('type') == 'n8n-nodes-base.code':
        code = n['parameters'].get('jsCode', '')
        if '$env.' in code:
            new_code = code.replace('$env.', 'process.env.')
            n['parameters']['jsCode'] = new_code
            replaced = len(re.findall(r'process\.env\.', new_code)) - len(re.findall(r'process\.env\.', code))
            print(f"  {n['name']}: $env -> process.env 교체")
            count += 1

print(f'\n총 {count}개 노드 수정 완료')

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
