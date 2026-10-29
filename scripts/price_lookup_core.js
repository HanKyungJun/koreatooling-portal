/* 재연마 정가 조회 — 해석 · 조회 로직 (2026-10-27 Cowork)
 * scripts/price_lookup.py 와 같은 규칙. 데이터는 window.PRICE_DATA(price-data.js) 를 읽는다.
 * 사용: PriceLookup.answer("10파이 2날 볼 고경도") → {q, rows:[{name,status,price,src}]}
 * 정가만 다룬다(할인율 · 거래처 단가 없음). status 가 OK 가 아니면 값을 보여 주지 않는다.
 */
(function(root){
var DATA=root.PRICE_DATA;
var _conf=null;function conf(){if(!_conf)_conf=new Set(DATA.conflict);return _conf}
const BLOCK_SHAPES=['평','볼','코너','라핑평','라핑볼','라핑코너','리머'];
const SHAPES=[[/라핑\s*(?:볼|ball)/,'라핑볼'],[/라핑\s*(?:코너|cr|레디우스|radius)/,'라핑코너'],[/라핑\s*(?:평|플랫|flat|스퀘어|square)?/,'라핑평'],
 [/테이퍼\s*드릴/,'테이퍼드릴'],[/테이퍼\s*(?:볼|ball)/,'테이퍼볼'],[/테이퍼\s*(?:코너|cr)/,'테이퍼코너'],[/테이퍼\s*(?:평|플랫|flat)?/,'테이퍼평'],[/스[탭텝]\s*드릴/,'스탭드릴'],
 [/리머|reamer/,'리머'],[/드릴|drill/,'드릴'],[/챔퍼|면취|chamfer/,'챔퍼'],[/카운터\s*보[어아]/,'카운터보어'],[/카운터\s*싱크/,'카운터싱크'],
 [/코너\s*r?|레디우스|radius|\bcr\b|코너알/,'코너'],[/볼|ball|\bbe\b/,'볼'],[/평|플랫|flat|스퀘어|square|\bfe\b/,'평']];
const PARTS=[[/밑\s*(?:옆날|외경|골수리)/,'밑옆날'],[/밑날\s*\+\s*외경|밑날외경/,'밑옆날'],[/골\s*수리/,'골수리'],[/밑날|선단|바닥날|엔드날|end/,'밑날'],[/옆날|외경|side/,'옆날']];
const COATS=[[/비\s*코팅|무\s*코팅|노\s*코팅|코팅\s*(?:없|안|x)|non[\s-]*coat/,'비코팅'],[/고경도/,'고경도코팅'],[/일반\s*코팅|일반|코팅/,'일반코팅']];
const MATS=[[/초경|카바이드|carbide|초경합금/,'초경'],[/hss|하이스|고속도강|하이스피드/,'HSS']];
const BW={'한':1,'두':2,'세':3,'네':4,'다섯':5,'여섯':6};
const COAT_LABEL={'비코팅':'비코팅','일반코팅':'일반 코팅','고경도코팅':'고경도 코팅'};
function cut(t,m){return t.slice(0,m.index)+' '+t.slice(m.index+m[0].length)}
function parseQuery(text){
 let t=' '+String(text).toLowerCase().replace(/[ØΦφ]/g,'ø')+' ';t=t.replace(/([가-힣])(\d)/g,'$1 $2');
 const q={},assumed=[];
 if((text.match(/\//g)||[]).length>=5){const p=text.split('/').map(s=>s.trim());const b=p[0].match(/^(\d+)/),d=p[2].match(/^([\d.]+)/);
  if(b&&d){Object.assign(q,{blade:+b[1],shape:p[1]==='라핑'?'라핑평':p[1],dia:+d[1],mat:p[3].toLowerCase()==='hss'?'HSS':p[3],part:p[4],coat:p[5].replace(/\s/g,'')});return finish(q,assumed)}}
 let m=t.match(/(?<![\d.])(\d{1,2})\s*(?:날|f\b|flute|fl\b|낭)/)||t.match(/(한|두|세|네|다섯|여섯)\s*날/);
 if(m){q.blade=/\d/.test(m[1])?+m[1]:BW[m[1]];t=cut(t,m)}
 const rr=t.match(/\br\s*(\d+(?:\.\d+)?)/);if(rr){q.r=+rr[1];t=cut(t,rr)}
 m=t.match(/(?:ø|파이|phi|\bd)\s*(\d+(?:\.\d+)?)/)||t.match(/(\d+(?:\.\d+)?)\s*(?:mm|파이|ø|phi)/)||t.match(/(\d+(?:\.\d+)?)/);
 if(m){q.dia=+m[1];t=cut(t,m)}
 for(const s of DATA.extra_shapes){if(t.includes(s.toLowerCase())){q.shape=s;break}}
 for(const [pats,key] of [[SHAPES,'shape'],[PARTS,'part'],[COATS,'coat'],[MATS,'mat']]){if(key in q)continue;for(const [re,v] of pats){if(re.test(t)){q[key]=v;break}}}
 if(!q.shape&&q.r!=null)q.shape='코너';
 return finish(q,assumed)}
function finish(q,assumed){if(!q.mat){q.mat='초경';assumed.push('재질 = 초경(입력 없음)')}if(!q.part){q.part='밑날';assumed.push('가공부 = 밑날(입력 없음)')}
 q.missing=['shape','dia'].filter(k=>q[k]==null);q.assumed=assumed;return q}
const g=x=>String(+(+x).toFixed(4));
function stdName(b,s,d,m,p,c){return `${b}날/${s}/${g(d)}mm/${m}/${p}/${COAT_LABEL[c]||c}`}
function key(nm){const p=String(nm).split('/').map(s=>s.trim());if(p.length<6)return String(nm).replace(/\s+/g,'').toLowerCase();
 const dm=p[2].match(/^([\d.]+)/);const dia=dm?g(dm[1]):p[2].toLowerCase();const shape=p[1]==='라핑'?'라핑평':p[1];let part=p[4].replace(/ /g,'');
 if(['밑골수리','밑옆날','밑골수리날'].includes(part))part='밑옆날';
 return [p[0].replace(/\s+/g,''),shape,dia,p[3].toLowerCase(),part,p[5].replace(/ /g,'')].join('/').toLowerCase()}
function band(runs,d){const st=DATA.step;for(const [a,b,v] of runs){if(d>a-st+1e-9&&d<=b+1e-9)return v}return null}
function calcPrice(b,s,d,m,p,c){
 let pk=p;if(['밑골수리','밑옆날','밑골수리날'].includes(pk))pk='밑옆날';
 if(s==='드릴'){if(pk!=='밑날'||b!==2)return null;   /* 2026-10-29: 26.10 정가표부터 드릴 고경도 열 있음 — 값 없으면 combos 에 없어 null */
 const r=DATA.combos[[m,'드릴','밑날',c,'2'].join('|')];return r?band(r,d):null}
 if(!BLOCK_SHAPES.includes(s))return null;const r=DATA.combos[[m,s,pk,c,b===2?'2':'4'].join('|')];return r?band(r,d):null}

function nearest(k){const p=k.split('/');if(p.length<6)return '';const d=+p[2];const c=[];
 for(const kk in DATA.registered){const q=kk.split('/');if(q.length>=6&&q[0]===p[0]&&q[1]===p[1]&&q.slice(3).join('/')===p.slice(3).join('/'))c.push([Math.abs(+q[2]-d),+q[2]])}
 return c.sort((a,b)=>a[0]-b[0]).slice(0,2).map(x=>'Ø'+g(x[1])).join(' · ')}
function priceOne(b,s,d,m,p,c){const name=stdName(b,s,d,m,p,c),k=key(name);const calc=calcPrice(b,s,d,m,p,c);const reg=DATA.registered[k];
 if(conf().has(k))return{name,status:'확인 필요',price:null,src:'사업장 파일끼리 등록 정가가 다름'};
 if(calc!=null&&reg!=null&&Math.abs(calc-reg)>0.5)return{name,status:'확인 필요',price:null,src:'정가표 계산값과 등록 정가가 다름'};
 if(calc!=null)return{name,status:'OK',price:calc,src:`${DATA.sheet}`+(reg!=null?' · 등록 품목':' · 미등록 규격')};
 if(reg!=null)return{name,status:'OK',price:reg,src:'등록 품목 정가'};
 const n=nearest(k);return{name,status:'없음',price:null,src:'정가표·등록 품목에 없음 — 담당자 확인'+(n?` (가까운 등록 규격: ${n})`:'')}}
function answer(text){const q=parseQuery(text);const res={query:text,q,rows:[]};if(q.missing.length)return res;
 const bl=q.blade?[q.blade]:[2,4],co=q.coat?[q.coat]:['비코팅','일반코팅','고경도코팅'];
 if(!q.blade)q.assumed.push('날수 입력 없음 → 2날 · 4날(3날 이상 같은 값) 모두 표시');if(!q.coat)q.assumed.push('코팅 입력 없음 → 세 가지 모두 표시');
 for(const b of bl)for(const c of co)res.rows.push(priceOne(b,q.shape,q.dia,q.mat,q.part,c));return res}

root.PriceLookup={answer:answer,parseQuery:parseQuery,priceOne:priceOne,key:key,COAT_LABEL:COAT_LABEL,g:g,data:function(){return DATA}};
})(typeof window!=='undefined'?window:globalThis);
