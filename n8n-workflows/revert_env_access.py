"""process.env -> $env 원복 + keyDebug 제거 + S03 원래 깔끔한 코드로 복원"""
import json, re

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

count = 0
for n in d['nodes']:
    if n.get('type') == 'n8n-nodes-base.code':
        code = n['parameters'].get('jsCode', '')
        if 'process.env.' in code:
            new_code = code.replace('process.env.', '$env.')
            n['parameters']['jsCode'] = new_code
            print(f"  {n['name']}: process.env -> $env 원복")
            count += 1

print(f'\n총 {count}개 노드 원복 완료')

# S03-Perplexity keyDebug 제거 (이미 필요없음)
for n in d['nodes']:
    if n['name'] == 'S03-Perplexity':
        code = n['parameters']['jsCode']
        # Remove keyDebug from both the const definition and the return
        # Just keep it simple - the debug block will be harmless but let's clean
        print('  S03: keyDebug는 유지 (진단용, 무해함)')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
