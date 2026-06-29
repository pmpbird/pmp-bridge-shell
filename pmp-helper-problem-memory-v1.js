(()=>{
'use strict';
const V='1.5.1-non-active-legacy-memory';
const TYPES='pmp_helper_problem_memory_types_v1',ACTIVE='pmp_helper_problem_memory_active_v1',STATE='pmp_helper_problem_memory_state_v1',EVID='pmp_helper_symptom_evidence_v1';
const CLEAN_TYPES='pmp_bug_bank_known_types_v1',CLEAN_EVID='pmp_bug_bank_symptom_evidence_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function load(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch(e){return f}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function types(){return load(TYPES,[]).filter(Boolean)}
function active(){return []}
function evidence(){return load(EVID,[]).filter(Boolean)}
function saveTypes(x){save(TYPES,(x||[]).slice(-100));mirror()}
function saveState(x){save(STATE,x||{})}
function normalize(list,section){return (Array.isArray(list)?list:[]).filter(Boolean).map((x,i)=>Object.assign({},x,{bug_bank_section:section,type:x.type||x.kind||x.problem||section+' '+(i+1),how_it_happens:x.how_it_happens||x.why||x.symptom||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function merge(a,b){let out=[],seen={};(Array.isArray(a)?a:[]).concat(Array.isArray(b)?b:[]).filter(Boolean).forEach(x=>{let k=String(x.signature||x.key||x.id||x.type||x.kind||JSON.stringify(x).slice(0,100));if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function mirror(){try{save(CLEAN_TYPES,normalize(merge(load(CLEAN_TYPES,[]),types()),'Known Bug Types').slice(-100));save(CLEAN_EVID,normalize(merge(load(CLEAN_EVID,[]),evidence()),'Symptom Evidence').slice(-100));save(ACTIVE,[])}catch(e){}}
function snapshot(){return{legacy_active_disabled:true,known:types().length,evidence:evidence().length}}
function learn(sym){let list=types(),sig=sym.signature||((sym.kind||sym.type)+'|'+(sym.where||'')),ex=list.find(x=>x.signature===sig);if(ex){ex.last_seen=sym.at||new Date().toISOString();ex.seen=(Number(ex.seen||1)||1)+1;ex.how_it_happens=sym.why||sym.how_it_happens||ex.how_it_happens;ex.detail=sym.detail||ex.detail;if(sym.fix_rule)ex.fix_rule=sym.fix_rule;saveTypes(list);return ex}let row={id:'type_'+Date.now(),auto:true,type:sym.kind||sym.type,how_it_happens:sym.why||sym.how_it_happens||'',signature:sig,where:sym.where||'',severity:sym.severity||'medium',created_at:sym.at||new Date().toISOString(),last_seen:sym.at||new Date().toISOString(),seen:1,detail:sym.detail||{}};if(sym.fix_rule)row.fix_rule=sym.fix_rule;list.push(row);saveTypes(list);return row}
function learnKnownProblems(reason,actions){return 0}
function smartFix(cb){mirror();cb&&cb('Legacy bug memory is headless. Active Bugs are owned by Bug Bank detectors.');return{actions:['legacy active detector disabled'],changed:0}}
function undoLastFix(){save(ACTIVE,[]);saveState({});mirror();return{actions:['cleared legacy active records']}}
function forget(){saveTypes([]);save(ACTIVE,[]);saveState({});save(EVID,[]);mirror()}
function removeOldVisible(d){try{let bank=d.getElementById('bank');if(!bank)return;let title=clean((bank.querySelector('[data-bank-detail-title]')||{}).textContent||'');if(title!=='Helper Bank')return;Array.from(bank.querySelectorAll('[data-helper-problem-memory-v1],[data-pm-smart-fix],[data-symptom-evidence-panel-v1]')).forEach(x=>x.remove())}catch(e){}}
function scan(){save(ACTIVE,[]);mirror();docs(T().document).forEach(removeOldVisible)}
window.PMPHelperProblemMemoryV1={version:V,scan,snapshot,learned:types,active,smartFix,undoLastFix,forget,learnKnownProblems,evidence};
window.addEventListener('load',()=>[700,1600,3000,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,3000);scan();
})();