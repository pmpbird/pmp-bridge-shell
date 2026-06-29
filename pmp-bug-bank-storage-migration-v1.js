(()=>{
'use strict';
const V='1.0.1-dedupe-and-active-clear';
const MAP={known:{old:'pmp_helper_problem_memory_types_v1',clean:'pmp_bug_bank_known_types_v1'},evidence:{old:'pmp_helper_symptom_evidence_v1',clean:'pmp_bug_bank_symptom_evidence_v1'},active:{old:'pmp_helper_problem_memory_active_v1',clean:'pmp_bug_bank_active_bugs_v1'},state:{old:'pmp_helper_problem_memory_state_v1',clean:'pmp_bug_bank_state_v1'},last_fix:{old:'pmp_helper_problem_last_fix_v1',clean:'pmp_bug_bank_last_fix_v1'}};
const RECEIPT='pmp_bug_bank_storage_migration_v1_receipt',CLEAR='pmp_bug_bank_active_clear_until_v1';
function load(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch(e){return f}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function arr(x){return Array.isArray(x)?x.filter(Boolean):[]}
function normText(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function canonical(x){return [normText(x.signature),normText(x.type||x.kind||x.problem),normText(x.where||x.where_seen),normText(x.fix_rule)].filter(Boolean).join('|')||normText(JSON.stringify(x).slice(0,160))}
function merge(){let out=[],seen={};Array.from(arguments).forEach(list=>arr(list).forEach(x=>{let k=canonical(x);if(seen[k]){let old=seen[k];Object.assign(old,x,{seen:Math.max(Number(old.seen||1),Number(x.seen||1)),last_seen:x.last_seen||old.last_seen})}else{seen[k]=Object.assign({},x);out.push(seen[k])}}));return out}
function normalize(list,section){return arr(list).map((x,i)=>Object.assign({},x,{bug_bank_section:section,type:x.type||x.kind||x.problem||(section+' '+(i+1)),how_it_happens:x.how_it_happens||x.why||x.symptom||'',where:x.where||x.where_seen||'',where_seen:x.where_seen||x.where||'',fix_rule:x.fix_rule||''}))}
function activeSuppressed(){return Number(load(CLEAR,0)||0)>Date.now()}
function migrate(){let known=normalize(merge(load(MAP.known.clean,[]),load(MAP.known.old,[])),'Known Bug Types').slice(-80);let evidence=normalize(merge(load(MAP.evidence.clean,[]),load(MAP.evidence.old,[])),'Symptom Evidence').slice(-80);let active=activeSuppressed()?[]:normalize(merge(load(MAP.active.clean,[]),load(MAP.active.old,[])),'Active Bugs Found').slice(0,40);save(MAP.known.clean,known);save(MAP.evidence.clean,evidence);save(MAP.active.clean,active);if(activeSuppressed())save(MAP.active.old,[]);let st=load(MAP.state.clean,null)||load(MAP.state.old,{});save(MAP.state.clean,st||{});let lf=load(MAP.last_fix.clean,null)||load(MAP.last_fix.old,null);if(lf)save(MAP.last_fix.clean,lf);let rec={type:'PMP_BUG_BANK_STORAGE_MIGRATION_V1',version:V,at:new Date().toISOString(),active_suppressed:activeSuppressed(),clean_keys:{known:MAP.known.clean,evidence:MAP.evidence.clean,active:MAP.active.clean,state:MAP.state.clean,last_fix:MAP.last_fix.clean},counts:{known:known.length,evidence:evidence.length,active:active.length},safe_claim:'Clean Bug Bank keys are deduped and active records stay cleared during fix cooldown.',do_not_claim:'Known Bug Types are not deleted; duplicate rows are merged by canonical bug identity.'};save(RECEIPT,rec);return rec}
window.PMPBugBankStorageMigrationV1={version:V,keys:MAP,migrate,canonical};
window.addEventListener('load',()=>[120,800,2500,5000].forEach(t=>setTimeout(migrate,t)));
setInterval(migrate,4000);migrate();
})();