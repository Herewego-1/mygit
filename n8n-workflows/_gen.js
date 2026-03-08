var fs=require("fs");
var FILE="D:/git 클로드코드/n8n-workflows/daily-briefing.json";
var TARGET="D:/git 클로드코드/n8n-workflows/rebuild_pipeline.js";
var data=JSON.parse(fs.readFileSync(FILE,"utf8"));
var n03old=data.nodes.find(function(n){return n.id==="node-03-perplexity";});
console.log("=== DIAGNOSING node-03 SyntaxError ===");
try{new Function(",",n03old.parameters.jsCode);console.log("node-03: SYNTAX OK");}
catch(e){console.log("node-03 ERROR:",e.message);}
// Build NODE03
var c03=[];
c03.push("// NODE-03: Perplexity Sonar Pro (STEP 1-A)");
c03.push("var d=.first().json;");
c03.push("var today=d.today,obsidianFilePath=d.obsidianFilePath,backupFilePath=d.backupFilePath,startTime=d.startTime;");
c03.push("var usdKrw=d.usdKrw||0,btcUsd=d.btcUsd||0;");
c03.push("var KEY=.PERPLEXITY_API_KEY;");
c03.push("if(!KEY||KEY.includes("여기에")){return [{json:{success:false,source:"perplexity",error:"PERPLEXITY_API_KEY 미설정",today,obsidianFilePath,backupFilePath,startTime,usdKrw,btcUsd}}];}");
c03.push("var SL=[");
c03.push(""당신은 글로벌 매크로-주식 전문 리서치 에이전트다.",");
c03.push(""오늘 날짜 기준, 아래 항목에 대해 팥트 중심으로 리서치하고 정리한다.",");
c03.push(""수치는 반드시 검증된 최신값만 사용한다.",");
c03.push(""[CRITICAL RULES]","1. NEVER fabricate numbers","2. Every number MUST have source URL"");
c03.push("];var sysP=SL.join("
");");
var NODE03="// NODE-03: Perplexity Sonar Pro (STEP 1-A)\nvar d=.first().json;\nvar today=d.today,obsidianFilePath=d.obsidianFilePath,backupFilePath=d.backupFilePath,startTime=d.startTime;\nvar usdKrw=d.usdKrw||0,btcUsd=d.btcUsd||0;\nvar KEY=.PERPLEXITY_API_KEY;\nif(!KEY||KEY.includes(\"여기에\")){return [{json:{success:false,source:\"perplexity\",error:\"PERPLEXITY_API_KEY 미설정\",today,obsidianFilePath,backupFilePath,startTime,usdKrw,btcUsd}}];}\nvar SL=[\"당신은 글로벌 매크로-주식 전문 리서치 에이전트다.\",\"오늘 날짜 기준, 팥트 중심으로 리서치하고 정리한다.\",\"- 각 수치마다 반드시 출처 URL을 병기한다.\",\"- 불확실한 부분은 [불확실: ~] 태그를 달아 표시한다.\",\"- 수치는 반드시 검증된 최신값만 사용한다.\",\"\",\"[CRITICAL RULES]\",\"1. NEVER fabricate numbers\",\"2. Every number MUST have source URL\",\"3. Conflicting reports must BOTH be shown\"];\nvar sysP=SL.join(\"\n\");\nvar rl=[];if(usdKrw>0)rl.push(\"- USD/KRW: \"+usdKrw.toLocaleString()+\"월 (Frankfurter ECB 실시간)\");if(btcUsd>0)rl.push(\"- BTC: $\"+btcUsd.toLocaleString()+\" (CoinGecko 실시간)\");\nvar RTN=rl.length>0?\"\n\n[MANDATORY 검증 가격]\n\"+rl.join(\"\n\"):\"\";\nvar UL=[\"날짜: \"+today+\" (KST). 아래 6개 섹션을 팥트 중심으로 리서치하라. 각 수치마다 출처 URL 병기 필수.\"+RTN,\"\",\"## 1. 미 증시 요약\",\"- 주요 지수: S&P500, NASDAQ, Dow Jones, Russell 2000 (정확한 수치 + % 변동 + 출처)\",\"- 11개 섹터 ETF 등락률 표: XLK, XLF, XLV, XLY, XLP, XLE, XLI, XLB, XLU, XLRE, XLC\",\"- 시장 breadth: NYSE advance/decline, 200일 MA 상회 비율%, 52주 신고저 수\",\"- 대표 종목 수익률 표 (시가총액 상위 10개)\",\"\",\"## 2. 핵심 변화요인\",\"- 국제유가: WTI/Brent 정확한 가격, OPEC+ 최신 결정 (출처 URL)\",\"- 금리/달러: 2Y/10Y/30Y 국체금리, DXY, VIX (정확한 수치 + 출처)\",\"- 연준(Fed): 현재 금리, 다음 FOMC 일정, CME FedWatch 인하 확률% (출처)\",\"- 정책/규제: 오늘 발표된 주요 정책\",\"\",\"## 3. 섹터/테마별 동향\",\"- 반도체(장비/스토리지/파운드리), 소프트웨어/플랫폼, 자동차/배터리/리티움\",\"- 온라인소비/여행, 테마(양자컴/원자력/로봇/우주), 비트코인/크립토\",\"- 각 섹터 핵심 뉴스 + 주요 종목 등락 (출처 URL 포함)\",\"\",\"## 4. 한국 증시 시사점\",\"- KOSPI/KOSDAQ 지수/등락/외국인 순매수 (KRW 억원, 출처: KRX)\",\"- 삼성전자(005930)/SK하이닉스(000660)/NAVER 시세 및 % 변동\",\"- USD/KRW 환율 추세, BOK 기준금리, 다음 금통위 일정\",\"- MSCI Korea 지수, 코스피 야간선물 (해당 시)\",\"\",\"## 5. FICC 요약\",\"- 월유: WTI/Brent 가격/방향, 재고 변화 (EIA)\",\"- 달러/환율: DXY 수준, USD/KRW/JPY/EUR 주요 환율\",\"- 국체금리: 2Y/10Y/30Y + yield curve 형태(정상/역전)\",\"- 귀금속/산업금속: 금/은/구리 가격 (출처)\",\"- 버핑지표(시총/GDP)/쉘러 CAPE P/E/IG-HY 신용 스프레드 (출처)\",\"\",\"## 6. 인용 링크 목록\",\"위 모든 수치의 출처 URL 목록 (형식: [섹션]: [URL])\"];\nvar usrP=UL.join(\"\n\");\ntry{var r=await this.helpers.httpRequest({method:\"POST\",url:\"https://api.perplexity.ai/chat/completions\",headers:{\"Authorization\":\"Bearer \"+KEY,\"Content-Type\":\"application/json\"},body:JSON.stringify({model:\"sonar-pro\",messages:[{role:\"system\",content:sysP},{role:\"user\",content:usrP}],temperature:0.1,max_tokens:4000,return_citations:true}),timeout:45000});\nvar cnt=r&&r.choices&&r.choices[0]&&r.choices[0].message&&r.choices[0].message.content;\nif(!cnt||cnt.trim().length<200){throw new Error(\"응답 부실 (\"+(cnt?cnt.length:0)+\"자)\");}\nreturn [{json:{success:true,source:\"perplexity\",perplexityResult:cnt,rawContent:cnt,today,obsidianFilePath,backupFilePath,startTime,usdKrw,btcUsd}}];}\ncatch(e){return [{json:{success:false,source:\"perplexity\",error:e.message,today,obsidianFilePath,backupFilePath,startTime,usdKrw,btcUsd}}];}";
var NODE03B="// NODE-03b: GPT Pro (STEP 1-B)\nvar prev=.first().json;\nvar today=prev.today,usdKrw=prev.usdKrw||0,btcUsd=prev.btcUsd||0;\nvar KEY=.OPENAI_API_KEY;\nif(!KEY||KEY.includes(\"여기에\")||KEY===\"\"||KEY===\"undefined\"){return [{json:Object.assign({},prev,{gptResult:null,gptSkipped:true,gptNote:\"OPENAI_API_KEY 미설정 - GPT 분석 생략\"})}];}\nvar SL=[\"당신은 한국 기관투자자를 위한 글로벌 매크로-주식 애널리스트다.\",\"오늘 날짜 기준, 아래 주제를 독립적으로 분석-요약한다.\",\"- 사실과 추론을 명확히 구분해 작성한다.\",\"- 각 이슈의 원인-결과 체인을 문장으로 반드시 연결한다.\",\"- 불확실 구간은 conditional로 기술.\"];\nvar sysP=SL.join(\"\n\");\nvar rh=[];if(usdKrw>0)rh.push(\"USD/KRW: \"+usdKrw.toLocaleString()+\"원\");if(btcUsd>0)rh.push(\"BTC: $\"+btcUsd.toLocaleString());\nvar RT=rh.length>0?\"\n[참고 실시간 가격: \"+rh.join(\", \")+\"]\n\":\"\";\nvar UL=[\"날짜: \"+today+\" (KST).\"+RT,\"아래 6개 섹션을 인과관계/시나리오 해석 중심으로 독립 분석하라.\",\"\",\"## 1. 미 증시 요약\",\"지수/섹터/대표 종목 수익률 표, 시장 흐름 해석\",\"\",\"## 2. 핵심 변화요인 인과 분석\",\"원인->결과 체인 형식으로 서술\",\"\",\"## 3. 섹터/테마별 임팩트 분석\",\"반도체/소프트웨어/자동차-배터리, 온라인소비/테마/비트코인\",\"\",\"## 4. 한국 증시 시사점\",\"에너지 의존도, AI 칩 규제, 환율, 반도체 변동성 관점에서 분석\",\"\",\"## 5. FICC 요약\",\"원유/달러/국체금리/귀금속 주요 움직임 해석\",\"\",\"## 6. 리스크-기회 체크포인트\",\"리스크 bullet 2개, 기회 bullet 1개 (총 3개)\"];\nvar usrP=UL.join(\"\n\");\ntry{var r=await this.helpers.httpRequest({method:\"POST\",url:\"https://api.openai.com/v1/chat/completions\",headers:{\"Authorization\":\"Bearer \"+KEY,\"Content-Type\":\"application/json\"},body:JSON.stringify({model:\"gpt-4o\",messages:[{role:\"system\",content:sysP},{role:\"user\",content:usrP}],temperature:0.2,max_tokens:3000}),timeout:45000});\nvar cnt=r&&r.choices&&r.choices[0]&&r.choices[0].message&&r.choices[0].message.content;\nif(!cnt||cnt.trim().length<100)throw new Error(\"GPT 응답 부실\");\nreturn [{json:Object.assign({},prev,{gptResult:cnt,gptSkipped:false})}];}\ncatch(e){return [{json:Object.assign({},prev,{gptResult:null,gptSkipped:true,gptNote:\"GPT 호출 실패: \"+e.message})}];}";
var NODE03C="// NODE-03c: 교차검증 데이터 정리 (STEP 2)\nvar prev=.first().json;\nvar today=prev.today;\nvar pR=prev.perplexityResult||prev.rawContent||\"\";\nvar gR=prev.gptResult||null;\nvar gS=prev.gptSkipped!==false;\nif(gS||!gR){return [{json:Object.assign({},prev,{success:true,rawContent:pR,crossValidated:false,crossNote:\"Perplexity 단독 모드 (GPT 결과 없음)\"})}];}\nvar cs={date:today,report_type:\"daily_us_market\",sources:{perplexity:{role:\"팥트/출처 중심 수집\",length:pR.length},gpt:{role:\"인과관계/시나리오 해석\",length:gR.length}},cross_validation_rules:{consensus:\"perplexity와 gpt 양측 동의 -> 확정적 서술\",perplexity_only:\"출처 기반 참고, URL 병기\",gpt_only:\"추정/시나리오 conditional\",conflict:\"양측 견해 모두 제시\"}};\nvar sec=[\"=====================================\",\"[STEP 1-A] PERPLEXITY SONAR PRO\",\"=====================================\",pR,\"\",\"=====================================\",\"[STEP 1-B] GPT PRO\",\"=====================================\",gR,\"\",\"=====================================\",\"[STEP 2] 교차검증 처리 지침\",\"=====================================\",JSON.stringify(cs,null,2)];\nvar rawContent=sec.join(\"\n\");\nreturn [{json:Object.assign({},prev,{success:true,rawContent:rawContent,crossValidated:true,crossValidationJson:cs})}];";
var NODE05="// NODE-05: Perplexity 재시도 (sonar-pro)\nvar prev=.first().json;\nvar pt={today:prev.today,obsidianFilePath:prev.obsidianFilePath,backupFilePath:prev.backupFilePath,startTime:prev.startTime,usdKrw:prev.usdKrw||0,btcUsd:prev.btcUsd||0,btcKrw:prev.btcKrw||0};\nvar firstError=prev.error||\"Perplexity 1차 실패\";\nvar KEY=.PERPLEXITY_API_KEY;\nvar usdKrw=pt.usdKrw,btcUsd=pt.btcUsd;\nif(!KEY||KEY.includes(\"여기에\")){return [{json:Object.assign({},pt,{success:false,source:\"perplexity_retry\",error:\"PERPLEXITY_API_KEY 미설정\",firstError})}];}\nvar rl=[];if(usdKrw>0)rl.push(\"USD/KRW: \"+usdKrw.toLocaleString()+\"원 (verified)\");if(btcUsd>0)rl.push(\"BTC: $\"+btcUsd.toLocaleString()+\" (verified)\");\nvar RTH=rl.length>0?\"\n[검증 가격: \"+rl.join(\", \")+\"]\n\":\"\";\nvar PL=[\"날짜: \"+prev.today+\" (KST). 월가 애널리스트 아침 브리핑 - 실제 검증된 데이터, 각 수치마다 출처 URL 필수.\"+RTH,\"\",\"아래 10개 항목 모두 제공 (출처 URL 포함):\",\"1. S&P500, NASDAQ, Dow, Russell 2000 - 정확한 수치 및 % 변동\",\"2. KOSPI, KOSDAQ - 정확한 수치, % 변동, 외국인 순매수 KRW 억원\",\"3. Fed 기준금리, 다음 FOMC 일정, 인하 확률% (CME FedWatch)\",\"4. 오늘 발생한 지정학적 이벤트: 구체적 국가명/사건명 명시\",\"5. WTI 유가/금 가격 - 정확한 수치 및 % 변동\",\"6. 미 10Y 국체금리 수치%, 2Y 수치%, 스프레드 방향\",\"7. VIX 수치, DXY 수치\",\"8. Goldman Sachs 또는 JPMorgan: 이번 주 리서치 노트 (제목 인용)\",\"9. Warren Buffett/Berkshire: 이번 주 관련 뉴스\",\"10. 한국 투자자 최대 리스크 1개 + 기회 요인 1개\",\"\",\"형식: [번호]. [주제] | [데이터 - 출처: URL] | [한국 투자자 영향 1문장]\"];\nvar prm=PL.join(\"\n\");\ntry{var r=await this.helpers.httpRequest({method:\"POST\",url:\"https://api.perplexity.ai/chat/completions\",headers:{\"Authorization\":\"Bearer \"+KEY,\"Content-Type\":\"application/json\"},body:JSON.stringify({model:\"sonar-pro\",messages:[{role:\"system\",content:\"실시간 금융 데이터 리포터. 검증된 데이터만 사용. 모든 수치에 출처 URL 필수. 날조 금지.\"},{role:\"user\",content:prm}],temperature:0.1,max_tokens:3000,return_citations:true}),timeout:50000});\nvar cnt=r&&r.choices&&r.choices[0]&&r.choices[0].message&&r.choices[0].message.content;\nif(!cnt||cnt.trim().length<150){throw new Error(\"재시도 응답 부실 (\"+(cnt?cnt.length:0)+\"자)\");}\nreturn [{json:Object.assign({},pt,{success:true,source:\"perplexity_retry\",perplexityResult:cnt,rawContent:cnt,firstError})}];}\ncatch(e){return [{json:Object.assign({},pt,{success:false,source:\"perplexity_retry\",error:e.message,firstError})}];}";
// 3. node-03 update
var n03=data.nodes.find(function(n){return n.id==="node-03-perplexity";});
n03.parameters.jsCode=NODE03;
n03.notes="Perplexity sonar-pro (STEP 1-A) - 팥트 수집 / 6섹션 / string array";
console.log("✅ node-03 업데이트 완료");
// 4. node-05 update
var n05=data.nodes.find(function(n){return n.id==="node-05-gemini";});
n05.parameters.jsCode=NODE05;
n05.notes="Perplexity sonar-pro 재시도 / timeout: 50s / string array";
console.log("✅ node-05 업데이트 완료");
// 5. Add node-03b
data.nodes.push({parameters:{jsCode:NODE03B},id:"node-03b-gpt",name:"🤖 GPT Pro 독립 분석",type:"n8n-nodes-base.code",typeVersion:2,position:[1120,200],notes:"GPT Pro (STEP 1-B) / OPENAI_API_KEY 미설정 시 자동 스� / gpt-4o"});
console.log("✅ node-03b (GPT Pro) 추가 완료");
// 6. Add node-03c
data.nodes.push({parameters:{jsCode:NODE03C},id:"node-03c-crossval",name:"🔀 교차검증 데이터 정리",type:"n8n-nodes-base.code",typeVersion:2,position:[1340,200],notes:"교차검증 STEP 2"});
console.log("✅ node-03c (교차검증) 추가 완료");
// 7. Connections
data.connections["✅ Perplexity 성공?"].main[0]=[{node:"🤖 GPT Pro 독립 분석",type:"main",index:0}];
data.connections["🤖 GPT Pro 독립 분석"]={main:[[{node:"🔀 교차검증 데이터 정리",type:"main",index:0}]]};
data.connections["🔀 교차검증 데이터 정리"]={main:[[{node:"🤖 Qwen 한국어 리라이팅",type:"main",index:0}]]};
console.log("✅ 연결(Connections) 업데이트 완료");
console.log("   Perplexity 성공? -> GPT Pro -> 교차검증 -> Qwen");
// 8. Save
fs.writeFileSync("D:/git 클로드코드/n8n-workflows/daily-briefing.json",JSON.stringify(data,null,2),"utf8");
console.log("✅ 파일 저장 완료");
// 9. Verify
var saved=JSON.parse(fs.readFileSync("D:/git 클로드코드/n8n-workflows/daily-briefing.json","utf8"));
var allOk=true;
var toCheck=["node-03-perplexity","node-03b-gpt","node-03c-crossval","node-05-gemini"];
for(var i=0;i<toCheck.length;i++){
  var nid=toCheck[i];
  var nd=saved.nodes.find(function(n){return n.id===nid;});
  if(!nd){console.error("ERROR: "+nid+" not found");allOk=false;continue;}
  try{new Function("$input","$env",nd.parameters.jsCode);console.log("✅ SYNTAX OK: "+nid+" ("+nd.parameters.jsCode.length+"자)");}
  catch(e){console.error("❌ SYNTAX ERROR: "+nid+" - "+e.message);allOk=false;}
}
console.log("");
console.log("=== 최종 결과 ===");
console.log("총 노드 수:",saved.nodes.length);
console.log("모든 문법 검증:",allOk?"✅ 통과":"❌ 오류 있음");
console.log("새 파이프라인: Perplexity -> GPT Pro -> 교차검증 -> Qwen");
