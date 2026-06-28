(()=>{
'use strict';
const V='1.0.0-clean-bug-bank-keys';
const MAP={
  known:{old:'pmp_helper_problem_memory_types_v1',clean:'pmp_bug_bank_known_types_v1'},
  evidence:{old:'pmp_helper_symptom_evidence_v1',clean:'pmp_bug_bank_symptom_evidence_v1'},
  active:{old:'pmp_helper_problem_memory_active_v1',clean:'pmp_bug_bank_active_bugs_v1'},
  state:{old:'pmp_helper_problem_memory_state_v1',clean:'pmp_bug_bank_state_v1'},
  last_fix:{old:'pmp_helper_problem_last_fix_v1',clean:'pmp_bug_bank_last_fix_v1'}
};
const RECEIPT='pmp_bug_bank_storage_migration_v1_receipt';
function load(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch(e){return f}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function arr(x){return Array.isArray(x)?x.filter(Boolean):[]}
function keyFor(x){return String(x.signature||x.key||x.id||x.type||x.kind||x.problem||JSON.stringify(x).slice(0,120))}
function merge(a,b){let out=[],seen={};arr(a).concat(arr(b)).forEach(x=>{let k=keyFor(x);if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function normalizeKnown(list){return arr(list).map((x,i)=>Object.assign({},x,{bug_bank_section:'Known Bug Types',type:x.type||x.kind||x.problem||('Known bug type '+(i+1)),how_it_happens:x.how_it_happens||x.why||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function normalizeEvidence(list){return arr(list).map((x,i)=>Object.assign({},x,{bug_bank_section:'Symptom Evidence',type:x.type||x.kind||x.problem||('Symptom evidence '+(i+1)),how_it_happens:x.how_it_happens||x.why||x.symptom||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function normalizeActive(list){return arr(list).map((x,i)=>Object.assign({},x,{bug_bank_section:'Active Bugs Found',type:x.type||x.kind||x.problem||('Active bug '+(i+1)),how_it_happens:x.how_it_happens||x.why||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function migrate(){let known=normalizeKnown(merge(load(MAP.known.clean,[]),load(MAP.known.old,[]))).slice(-80);let evidence=normalizeEvidence(merge(load(MAP.evidence.clean,[]),load(MAP.evidence.old,[]))).slice(-80);let active=normalizeActive(merge(load(MAP.active.clean,[]),load(MAP.active.old,[]))).slice(0,40);save(MAP.known.clean,known);save(MAP.evidence.clean,evidence);save(MAP.active.clean,active);let st=load(MAP.state.clean,null)||load(MAP.state.old,{});save(MAP.state.clean,st||{});let lf=load(MAP.last_fix.clean,null)||load(MAP.last_fix.old,null);if(lf)save(MAP.last_fix.clean,lf);let rec={type:'PMP_BUG_BANK_STORAGE_MIGRATION_V1',version:V,at:new Date().toISOString(),clean_keys:{known:MAP.known.clean,evidence:MAP.evidence.clean,active:MAP.active.clean,state:MAP.state.clean,last_fix:MAP.last_fix.clean},counts:{known:known.length,evidence:evidence.length,active:active.length},safe_claim:'Clean Bug Bank keys now mirror old helper/problem memory keys.',do_not_claim:'Old writer keys are not deleted yet; sensors may still write to them until later refactor.'};save(RECEIPT,rec);return rec}
window.PMPBugBankStorageMigrationV1={version:V,keys:MAP,migrate};
window.addEventListener('load',()=>[120,800,2500,5000].forEach(t=>setTimeout(migrate,t)));
setInterval(migrate,4000);migrate();
})();