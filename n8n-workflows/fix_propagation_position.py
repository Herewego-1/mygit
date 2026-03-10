"""
버그 수정:
1. S03-Perplexity: breakingNewsText 소실 버그 수정 (return에 ...inp spread 추가)
2. S02c-BreakingNews: 노드 위치 [700→560] 으로 수정
   현재: S02b(440) → S02c(700) → S03(680) — 시각적으로 S02c가 S03 뒤에 있어 겹침
   수정: S02b(440) → S02c(560) → S03(680) — 올바른 순서
"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

fixed = []

for node in d['nodes']:
    # ── Fix 1: S03-Perplexity return에 ...inp spread 추가 ──────────────────
    if node['name'] == 'S03-Perplexity':
        code = node['parameters']['jsCode']
        old_return = (
            "return [{ json: {\n"
            "  success, source: 'perplexity', error: errorMsg,\n"
            "  rawContent,\n"
            "  today, obsidianFilePath, backupFilePath, startTime,\n"
            "  usdKrw, btcUsd, btcKrw: inp.btcKrw || 0\n"
            "} }];"
        )
        new_return = (
            "return [{ json: {\n"
            "  ...inp,\n"
            "  success, source: 'perplexity', error: errorMsg,\n"
            "  rawContent,\n"
            "  usdKrw, btcUsd, btcKrw: inp.btcKrw || 0\n"
            "} }];"
        )
        if old_return in code:
            node['parameters']['jsCode'] = code.replace(old_return, new_return)
            fixed.append('S03-Perplexity: breakingNewsText propagation 수정')
        else:
            fixed.append('WARNING S03-Perplexity: return 패턴 찾지 못함 (이미 수정됐거나 변경됨)')

    # ── Fix 2: S02c-BreakingNews 위치 [700, 320] → [560, 320] ─────────────
    if node['name'] == 'S02c-BreakingNews':
        if node['position'] == [700, 320]:
            node['position'] = [560, 320]
            fixed.append('S02c-BreakingNews: 위치 [700, 320] → [560, 320] 수정')
        else:
            fixed.append(f'S02c-BreakingNews: 위치가 이미 {node["position"]}로 되어 있음 (수정 불필요)')

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('저장 완료!')
print()
for msg in fixed:
    print(f'  ✓ {msg}')

print()
print('노드 위치 (수정 후):')
pos_nodes = ['S02b-Realtime', 'S02c-BreakingNews', 'S03-Perplexity', 'S03b-RealData']
for node in d['nodes']:
    if node['name'] in pos_nodes:
        print(f'  {node["name"]}: x={node["position"][0]}')
