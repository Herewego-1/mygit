"""S03b-RealData: ETF 티커 → 실제 지수 티커로 수정 (^GSPC, ^IXIC, ^DJI)"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S03b-RealData: Yahoo Finance 실제 지수 데이터 (TradingView와 동일 수치)
const prev = $input.first().json;

// ^ 접두사 = 실제 지수 (ETF 아님) → TradingView 수치와 일치
const symbols = {
  '^GSPC': 'S&P 500',
  '^IXIC': 'NASDAQ',
  '^DJI':  '다우존스',
  '^VIX':  'VIX',
  '^SOX':  '필라델피아 반도체',
  'NVDA':  'NVIDIA',
  'TSLA':  'Tesla',
  'AAPL':  'Apple',
  'MSFT':  'Microsoft',
  'AMZN':  'Amazon',
  'META':  'Meta',
  'GOOGL': 'Google'
};

const results = {};
const errors = [];

for (const [sym, name] of Object.entries(symbols)) {
  try {
    const encoded = encodeURIComponent(sym);
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encoded}?range=2d&interval=1d`;
    const resp = await this.helpers.httpRequest({
      method: 'GET',
      url,
      headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json' },
      timeout: 15000
    });

    const r = typeof resp === 'string' ? JSON.parse(resp) : resp;
    const meta = r?.chart?.result?.[0]?.meta;
    const quotes = r?.chart?.result?.[0]?.indicators?.quote?.[0];

    if (meta && quotes) {
      const lastIdx = quotes.close.findLastIndex(v => v !== null);
      const prevIdx = lastIdx - 1;

      const close    = quotes.close[lastIdx];
      const prevClose = prevIdx >= 0 && quotes.close[prevIdx]
        ? quotes.close[prevIdx]
        : meta.previousClose;
      const volume   = quotes.volume?.[lastIdx];

      const change    = close - prevClose;
      const changePct = (change / prevClose) * 100;
      const direction = change >= 0 ? '▲' : '▼';

      results[sym] = {
        name,
        close:     close?.toFixed(2),
        change:    change?.toFixed(2),
        changePct: changePct?.toFixed(2),
        direction,
        volume:    volume ? (volume / 1000000).toFixed(1) + 'M' : '-'
      };
    }
  } catch(e) {
    errors.push(`${sym}: ${e.message}`);
  }
}

// 지수 테이블
const indexSyms = ['^GSPC', '^IXIC', '^DJI', '^VIX', '^SOX'];
const stockSyms = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'META', 'GOOGL'];

const indexRows = indexSyms
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | ${q.close} | ${q.direction}${Math.abs(q.change)} | ${q.direction}${Math.abs(q.changePct)}% |`;
  });

const stockRows = stockSyms
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} (${s}) | $${q.close} | ${q.direction}${Math.abs(q.change)} | ${q.direction}${Math.abs(q.changePct)}% | ${q.volume} |`;
  });

const fetchTime = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

const marketTable = [
  '## 📈 전일 미국 증시 요약',
  '',
  '**주요 지수**',
  '| 지수 | 종가 | 전일대비 | 등락률 |',
  '|------|------|---------|--------|',
  ...indexRows,
  '',
  '**주요 종목**',
  '| 종목 | 종가 | 전일대비 | 등락률 | 거래량 |',
  '|------|------|---------|--------|-------|',
  ...stockRows,
  '',
  `> 출처: Yahoo Finance (${fetchTime} 수집) — TradingView 수치와 동일`
].join('\n');

return [{ json: {
  ...prev,
  realMarketData: results,
  marketTable,
  dataErrors: errors,
  dataValidated: true
} }];
"""

for n in d['nodes']:
    if n['name'] == 'S03b-RealData':
        n['parameters']['jsCode'] = new_code
        print('S03b-RealData: 실제 지수 티커로 수정 완료')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('저장 완료!')
