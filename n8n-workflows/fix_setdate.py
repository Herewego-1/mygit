import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for n in d['nodes']:
    if n['id'] == 'node-02-setdate':
        for a in n['parameters']['assignments']['assignments']:
            if a['id'] == 'v4':
                # r"..." 로 백슬래시 정확히 처리
                # JS 표현식 안에서: 'D:\\Obsidian\\경제브리핑\\' 로 보여야
                # → Python raw string 으로 저장하면 json.dump 가 알아서 이스케이프
                a['value'] = r"={{ 'D:\\Obsidian\\경제브리핑\\' + $now.setZone('Asia/Seoul').toFormat('yyyy-MM-dd') + '.md' }}"
                print('v4 obsidianFilePath 수정완료')
                print('  값:', repr(a['value']))
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# 검증
with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)
for n in d2['nodes']:
    if n['id'] == 'node-02-setdate':
        for a in n['parameters']['assignments']['assignments']:
            print(f'  [{a["id"]}] {a["name"]}: {repr(a["value"])}')
        break

print('\n저장 완료')
