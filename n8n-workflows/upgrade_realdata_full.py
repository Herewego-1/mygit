"""
S03b-RealData 전체 업그레이드:
- 지수: ^GSPC, ^NDX(NASDAQ-100), ^DJI, ^VIX, ^SOX
- 개별주: NVDA, TSLA, AAPL, MSFT, AMZN, META, GOOGL
- 원자재: GC=F(Gold), CL=F(WTI), BZ=F(Brent), SI=F(Silver), HG=F(Copper)
- 채권: ^TNX(미국10Y), ^TYX(미국30Y)
- 환율: KRW=X(USD/KRW), EURUSD=X, JPY=X
- 암호화폐: BTC-USD, ETH-USD, SOL-USD
"""
import json

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

new_code = r"""// S03b-RealData: Yahoo Finance 전체 시장 데이터 (지수·종목·원자재·채권·환율·암호화폐)
const prev = $input.first().json;

const symbols = {
  // 주요 지수 (실제 지수 티커)
  '^GSPC': { name: 'S&P 500',          cat: 'index' },
  '^NDX':  { name: 'NASDAQ-100',        cat: 'index' },
  '^DJI':  { name: '다우존스',           cat: 'index' },
  '^VIX':  { name: 'VIX (공포지수)',     cat: 'index' },
  '^SOX':  { name: '필라델피아 반도체',   cat: 'index' },

  // 주요 종목
  'NVDA':  { name: 'NVIDIA',   cat: 'stock' },
  'TSLA':  { name: 'Tesla',    cat: 'stock' },
  'AAPL':  { name: 'Apple',    cat: 'stock' },
  'MSFT':  { name: 'Microsoft', cat: 'stock' },
  'AMZN':  { name: 'Amazon',   cat: 'stock' },
  'META':  { name: 'Meta',     cat: 'stock' },
  'GOOGL': { name: 'Google',   cat: 'stock' },

  // 원자재
  'GC=F':  { name: '금 (Gold)',          cat: 'commodity', unit: '$/oz' },
  'CL=F':  { name: 'WTI 원유',           cat: 'commodity', unit: '$/배럴' },
  'BZ=F':  { name: 'Brent 원유',         cat: 'commodity', unit: '$/배럴' },
  'SI=F':  { name: '은 (Silver)',         cat: 'commodity', unit: '$/oz' },
  'HG=F':  { name: '구리 (Copper)',       cat: 'commodity', unit: '$/lb' },

  // 채권 금리 (%)
  '^TNX':  { name: '미국 10Y 국채금리',   cat: 'bond', unit: '%' },
  '^TYX':  { name: '미국 30Y 국채금리',   cat: 'bond', unit: '%' },

  // 환율
  'KRW=X':    { name: 'USD/KRW',  cat: 'fx' },
  'EURUSD=X': { name: 'EUR/USD',  cat: 'fx' },
  'JPY=X':    { name: 'USD/JPY',  cat: 'fx' },

  // 암호화폐
  'BTC-USD': { name: 'Bitcoin',  cat: 'crypto' },
  'ETH-USD': { name: 'Ethereum', cat: 'crypto' },
  'SOL-USD': { name: 'Solana',   cat: 'crypto' },
};

const results = {};
const errors = [];

for (const [sym, info] of Object.entries(symbols)) {
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
      const closes = (quotes.close || []).filter(v => v !== null && v !== undefined);
      let close, prevClose;

      if (closes.length >= 2) {
        close = closes[closes.length - 1];
        prevClose = closes[closes.length - 2];
      } else if (closes.length === 1) {
        close = closes[0];
        prevClose = meta.previousClose || meta.chartPreviousClose || meta.regularMarketPreviousClose || close;
      } else {
        close = meta.regularMarketPrice || 0;
        prevClose = meta.previousClose || meta.chartPreviousClose || close;
      }

      const volume = quotes.volume?.[quotes.volume.length - 1];
      const change = close - prevClose;
      const changePct = prevClose !== 0 ? (change / prevClose) * 100 : 0;
      const direction = change >= 0 ? '▲' : '▼';

      // 소수점 자릿수 결정
      let decimals = 2;
      if (info.cat === 'fx' && sym !== 'KRW=X') decimals = 4;
      if (info.cat === 'bond') decimals = 3;
      if (info.cat === 'crypto') decimals = 2;

      results[sym] = {
        ...info,
        close:     close?.toFixed(decimals),
        change:    change?.toFixed(decimals),
        changePct: changePct?.toFixed(2),
        direction,
        volume: volume ? (volume >= 1e9 ? (volume/1e9).toFixed(1)+'B' : volume >= 1e6 ? (volume/1e6).toFixed(1)+'M' : volume >= 1e3 ? (volume/1e3).toFixed(1)+'K' : volume.toString()) : '-'
      };
    }
  } catch(e) {
    errors.push(`${sym}: ${e.message}`);
  }
}

// ── 섹션별 마크다운 테이블 생성 ──

const fmt = (q) => `${q.direction}${Math.abs(parseFloat(q.change)).toFixed(q.change.includes('.') ? q.change.split('.')[1].length : 2)}`;
const fmtPct = (q) => `${q.direction}${Math.abs(parseFloat(q.changePct)).toFixed(2)}%`;

// 1. 주요 지수
const indexRows = ['^GSPC', '^NDX', '^DJI', '^VIX', '^SOX']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | ${q.close} | ${fmt(q)} | ${fmtPct(q)} |`;
  });

// 2. 개별 종목
const stockRows = ['NVDA','TSLA','AAPL','MSFT','AMZN','META','GOOGL']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} (${s}) | $${q.close} | ${fmt(q)} | ${fmtPct(q)} | ${q.volume} |`;
  });

// 3. 원자재
const commodityRows = ['GC=F','CL=F','BZ=F','SI=F','HG=F']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | ${q.close} ${q.unit||''} | ${fmt(q)} | ${fmtPct(q)} |`;
  });

// 4. 채권
const bondRows = ['^TNX','^TYX']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | ${q.close}% | ${fmt(q)}bp | ${fmtPct(q)} |`;
  });

// 5. 환율
const fxRows = ['KRW=X','EURUSD=X','JPY=X']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | ${q.close} | ${fmt(q)} | ${fmtPct(q)} |`;
  });

// 6. 암호화폐
const cryptoRows = ['BTC-USD','ETH-USD','SOL-USD']
  .filter(s => results[s])
  .map(s => {
    const q = results[s];
    return `| ${q.name} | $${q.close} | ${fmt(q)} | ${fmtPct(q)} | ${q.volume} |`;
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
  '**원자재**',
  '| 종목 | 가격 | 전일대비 | 등락률 |',
  '|------|------|---------|--------|',
  ...commodityRows,
  '',
  '**채권 금리**',
  '| 종목 | 금리 | 전일대비 | 등락률 |',
  '|------|------|---------|--------|',
  ...bondRows,
  '',
  '**환율 (FX)**',
  '| 통화쌍 | 환율 | 전일대비 | 등락률 |',
  '|--------|------|---------|--------|',
  ...fxRows,
  '',
  '**암호화폐**',
  '| 종목 | 가격 | 전일대비 | 등락률 | 거래량 |',
  '|------|------|---------|--------|-------|',
  ...cryptoRows,
  '',
  `> 출처: Yahoo Finance (${fetchTime} 수집) — 실제 지수·선물·현물 데이터`
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
        print('✅ S03b-RealData: 전체 업그레이드 완료')
        print('   - ^IXIC → ^NDX (NASDAQ-100, TradingView 일치)')
        print('   - 원자재 추가: 금/WTI/Brent/은/구리')
        print('   - 채권 추가: 미국 10Y/30Y 국채금리')
        print('   - 환율 추가: USD/KRW, EUR/USD, USD/JPY')
        print('   - 암호화폐 추가: BTC/ETH/SOL')
        break

with open('D:/git 클로드코드/n8n-workflows/daily-briefing.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('✅ 저장 완료!')
