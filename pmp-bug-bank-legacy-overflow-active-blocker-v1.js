(()=>{
'use strict';
const V='1.0.0';
const KEYS=['pmp_bug_bank_active_bugs_v1','pmp_helper_problem_memory_active_v1'];
function read(k){try{return JSON.parse(localStorage.getItem(k)||'[]')}catch(e){return[]}}
function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function broadOverflow(x){let t=String((x&&x.type)||(x&&x.kind)||(x&&x.problem)||'');let w=String((x&&x.where)||(x&&x.where_seen)||'');return t==='Auto-detected overflow/clipping'&&w==='Bank screen'}
function run(){let removed=0;KEYS.forEach(k=>{let a=read(k);if(!Array.isArray(a))a=[];let b=a.filter(x=>!broadOverflow(x));removed+=a.length-b.length;write(k,b)});try{localStorage.setItem('pmp_bug_bank_legacy_overflow_active_blocker_v1_receipt',JSON.stringify({type:'PMP_BUG_BANK_LEGACY_OVERFLOW_ACTIVE_BLOCKER_V1',version:V,at:new Date().toISOString(),removed,rule:'Broad Bank-screen overflow is removed from Active Bugs. Specific named visual bugs remain active.'}))}catch(e){}return removed}
window.PMPBugBankLegacyOverflowActiveBlockerV1={version:V,scan:run};
window.addEventListener('load',()=>[50,250,900,2000,5000].forEach(t=>setTimeout(run,t)));
setInterval(run,750);run();
})();