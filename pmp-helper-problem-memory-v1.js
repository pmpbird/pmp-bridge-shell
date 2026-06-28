(()=>{
'use strict';
const V='1.5.0-headless-bug-bank-writer';
const TYPES='pmp_helper_problem_memory_types_v1';
const ACTIVE='pmp_helper_problem_memory_active_v1';
const STATE='pmp_helper_problem_memory_state_v1';
const EVID='pmp_helper_symptom_evidence_v1';
const CLEAN_TYPES='pmp_bug_bank_known_types_v1';
const CLEAN_ACTIVE='pmp_bug_bank_active_bugs_v1';
const CLEAN_EVID='pmp_bug_bank_symptom_evidence_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function load(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch(e){return f}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function visible(el){try{let w=el.ownerDocument.defaultView||window,cs=w.getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0}catch(e){return false}}
function types(){return load(TYPES,[]).filter(Boolean)}
function active(){return load(ACTIVE,[]).filter(Boolean)}
function evidence(){return load(EVID,[]).filter(Boolean)}
function saveTypes(x){save(TYPES,(x||[]).slice(-80));mirror()}
function saveActive(x){save(ACTIVE,(x||[]).slice(0,40));mirror()}
function saveState(x){save(STATE,x||{})}
function normalize(list,section){return (Array.isArray(list)?list:[]).filter(Boolean).map((x,i)=>Object.assign({},x,{bug_bank_section:section,type:x.type||x.kind||x.problem||section+' '+(i+1),how_it_happens:x.how_it_happens||x.why||x.symptom||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function merge(a,b){let out=[],seen={};(Array.isArray(a)?a:[]).concat(Array.isArray(b)?b:[]).filter(Boolean).forEach(x=>{let k=String(x.signature||x.key||x.id||x.type||x.kind||JSON.stringify(x).slice(0,100));if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function mirror(){try{save(CLEAN_TYPES,normalize(merge(load(CLEAN_TYPES,[]),types()),'Known Bug Types').slice(-80));save(CLEAN_EVID,normalize(merge(load(CLEAN_EVID,[]),evidence()),'Symptom Evidence').slice(-80));save(CLEAN_ACTIVE,normalize(merge(load(CLEAN_ACTIVE,[]),active()),'Active Bugs Found').slice(0,40))}catch(e){}}
function metrics(){let m={overflow:0,blank_buttons:0,height:0,width:0};docs(T().document).forEach(doc=>{try{let bank=doc.getElementById('bank');if(!bank)return;let title=clean((bank.querySelector('[data-bank-detail-title]')||{}).textContent||'');if(title==='Bug Bank')return;let r=bank.getBoundingClientRect();m.height=Math.max(m.height,Math.round(r.height||0));m.width=Math.max(m.width,Math.round(r.width||0));Array.from(bank.querySelectorAll('*')).forEach(el=>{try{if(el.closest&&el.closest('[data-helper-bank-live-inspector-v2],[data-bug-bank-owner-v1]'))return;if(!visible(el))return;if(el.scrollWidth>el.clientWidth+8)m.overflow++}catch(e){}});Array.from(bank.querySelectorAll('button')).forEach(b=>{try{if(visible(b)&&!clean(b.textContent))m.blank_buttons++}catch(e){}})}catch(e){}});return m}
function symptom(kind,where,why,severity,detail){return{kind,type:kind,where,why,how_it_happens:why,severity:severity||'medium',signature:kind+'|'+where,detail:detail||{},at:new Date().toISOString()}}
function learn(sym){let list=types(),sig=sym.signature||((sym.kind||sym.type)+'|'+(sym.where||'')),ex=list.find(x=>x.signature===sig);if(ex){ex.last_seen=sym.at||new Date().toISOString();ex.seen=(Number(ex.seen||1)||1)+1;ex.how_it_happens=sym.why||sym.how_it_happens||ex.how_it_happens;ex.detail=sym.detail||ex.detail;if(sym.fix_rule)ex.fix_rule=sym.fix_rule;saveTypes(list);return ex}let row={id:'type_'+Date.now(),auto:true,type:sym.kind||sym.type,how_it_happens:sym.why||sym.how_it_happens||'',signature:sig,where:sym.where||'',severity:sym.severity||'medium',created_at:sym.at||new Date().toISOString(),last_seen:sym.at||new Date().toISOString(),seen:1,detail:sym.detail||{}};if(sym.fix_rule)row.fix_rule=sym.fix_rule;list.push(row);saveTypes(list);return row}
function currentSymptoms(){let m=metrics(),out=[];if(m.overflow>0)out.push(symptom('Auto-detected overflow/clipping','Bank screen','A visible screen part is wider than its box.','medium',{overflow:m.overflow}));if(m.blank_buttons>0)out.push(symptom('Auto-detected blank button','Bank screen','A visible button has no label.','medium',{blank_buttons:m.blank_buttons}));return out}
function tick(){let syms=currentSymptoms();syms.forEach(learn);saveActive(syms);return syms}
function snapshot(){return metrics()}
function learnKnownProblems(reason,actions){let learned=0;try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2,d=api&&api.live?api.live():{checks:[]};(d.checks||[]).filter(c=>c&&/^(review|risk)$/i.test(String(c.status||''))).forEach(c=>{learn(symptom(c.check||'Known bug check',c.where||'App',c.why||'A known check was active.',c.severity||'medium',{reason,actions}));learned++})}catch(e){}return learned}
function smartFix(cb){learnKnownProblems('headless save only',[]);mirror();cb&&cb('Saved to Bug Bank. No visible Helper Bank fix UI.');return{actions:['saved to Bug Bank'],changed:0}}
function undoLastFix(){saveActive([]);saveState({});mirror();return{actions:['cleared active bug records']}}
function forget(){saveTypes([]);saveActive([]);saveState({});save(EVID,[]);mirror()}
function removeOldVisible(d){try{let bank=d.getElementById('bank');if(!bank)return;let title=clean((bank.querySelector('[data-bank-detail-title]')||{}).textContent||'');if(title!=='Helper Bank')return;Array.from(bank.querySelectorAll('[data-helper-problem-memory-v1],[data-pm-smart-fix],[data-symptom-evidence-panel-v1]')).forEach(x=>x.remove())}catch(e){}}
function scan(){tick();mirror();docs(T().document).forEach(removeOldVisible)}
window.PMPHelperProblemMemoryV1={version:V,scan,snapshot,learned:types,active,smartFix,undoLastFix,forget,learnKnownProblems,evidence};
window.addEventListener('load',()=>[700,1600,3000,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,3000);scan();
})();