"""S10-Markdown: 자동생성 메타데이터 라인 + 생성정보 테이블 제거"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S10-Markdown: 최종 마크다운 생성
const data = $input.first().json;
const { today, obsidianFilePath, backupFilePath, startTime } = data;
const rewrittenContent = data.rewrittenContent;
const newsSource = data.newsSource || data.source || 'unknown';
const llmModel   = data.model || data.llmModel || 'unknown';

const endTime = new Date();
const durationSec = startTime
  ? Math.round((endTime - new Date(startTime)) / 1000)
  : 0;

const [year, month] = today.split('-');
const monthMap = {
  '01':'1월','02':'2월','03':'3월','04':'4월','05':'5월','06':'6월',
  '07':'7월','08':'8월','09':'9월','10':'10월','11':'11월','12':'12월'
};

// YAML frontmatter (Obsidian 메타데이터 — 숨겨진 영역, 본문에 미표시)
const fm = [
  '---',
  `title: "${today} 경제브리핑"`,
  `date: ${today}`,
  'tags:',
  '  - 경제브리핑',
  `  - ${year}년`,
  `  - ${monthMap[month] || month + '월'}`,
  'category: 경제브리핑',
  `source: ${newsSource}`,
  `llm_model: ${llmModel}`,
  `created: ${endTime.toISOString()}`,
  `duration_sec: ${durationSec}`,
  '---',
  ''
].join('\n');

const header = [
  `# 📊 ${today} 경제브리핑`,
  '',
  '---',
  ''
].join('\n');

const finalMarkdown = fm + header + rewrittenContent;

return [{ json: {
  finalMarkdown, today, obsidianFilePath, backupFilePath,
  wordCount: finalMarkdown.length, newsSource, llmModel, durationSec, startTime
}}];
"""

for n in d['nodes']:
    if n['name'] == 'S10-Markdown':
        n['parameters']['jsCode'] = new_code
        print('S10-Markdown: 메타데이터 라인 + 생성정보 테이블 제거 완료')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
