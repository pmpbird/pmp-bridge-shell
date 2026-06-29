(()=>{
'use strict';
const V='1.0.1-known-fix-rule';
const ACTIVE_KEYS=['pmp_bug_bank_active_bugs_v1','pmp_helper_problem_memory_active_v1'];
const KNOWN='pmp_bug_bank_known_types_v1',EVID='pmp_bug_bank_symptom_evidence_v1';
function read(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function broadOverflow(x){let t=String((x&&x.type)||(x&&x.kind)||(x&&x.problem)||'');let w=String((x&&x.where)||(x&&x.where_seen)||'');return t==='Auto-detected overflow/clipping'&&w==='Bank screen'}
function key(x){return String((x&&x.type)||'')+'|'+String((x&&x.where)||x&&x.where_seen||'')+'|'+String((x&&x.fix_rule)||'')}
function upsert(k,row){let a=read(k,[]);if(!Array.isArray(a))a=[];let hit=a.find(x=>key(x)===key(row));if(hit)Object.assign(hit,row,{last_seen:new Date().toISOString(),seen:Number(hit.seen||1)+1});else a.push(Object.assign({seen:1,created_at:new Date().toISOString()},row));write(k,a.slice(-100))}
function seed(){let row={type:'Auto-detected overflow/clipping',where:'Bank screen',where_seen:'Bank screen',severity:'retired-active-detector',signature:'Auto-detected overflow/clipping|Bank screen|retired',how_it_happens:'Legacy detector reported broad Bank-screen overflow without naming the exact failing element.',fix_rule:'Do not allow this broad legacy record in Active Bugs. Replace it with a specific named bug that identifies the owning bank, surface, and failing element.',bug_bank_section:'Known Bug Types',last_seen:new Date().toISOString(),source:'legacy-overflow-active-blocker'};upsert(KNOWN,row);upsert(EVID,Object.assign({},row,{bug_bank_section:'Symptom Evidence',evidence_source:'retired legacy detector'}))}
function run(){let removed=0;ACTIVE_KEYS.forEach(k=>{let a=read(k,[]);if(!Array.isArray(a))a=[];let b=a.filter(x=>!broadOverflow(x));removed+=a.length-b.length;write(k,b)});seed();try{localStorage.setItem('pmp_bug_bank_legacy_overflow_active_blocker_v1_receipt',JSON.stringify({type:'PMP_BUG_BANK_LEGACY_OVERFLOW_ACTIVE_BLOCKER_V1',version:V,at:new Date().toISOString(),removed,rule:'Broad Bank-screen overflow is known and has a fix rule, but is blocked from Active Bugs.'}))}catch(e){}return removed}
window.PMPBugBankLegacyOverflowActiveBlockerV1={version:V,scan:run};
window.addEventListener('load',()=>[50,250,900,2000,5000].forEach(t=>setTimeout(run,t)));
setInterval(run,750);run();
})();