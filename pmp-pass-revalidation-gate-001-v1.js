(()=>{
'use strict';
const V='1.0.0-pass-revalidation-gate-001-20260710A';
const KEY='pmp_pass_revalidation_gate_001_v1_receipt';
const TRACE='pmp_pass_revalidation_gate_001_v1_trace';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function get(k){try{let v=T().localStorage.getItem(k);if(v)return JSON.parse(v)}catch(e){}try{let v=localStorage.getItem(k);if(v)return JSON.parse(v)}catch(e){}return null}
function docs(root,a,n){a=a||[];n=n||0;if(!root||n>10)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe,frame')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function scripts(d){let out=[];try{Array.from(d.querySelectorAll('script[src]')).forEach(s=>out.push({id:s.id||'',src:s.getAttribute('src')||''}))}catch(e){}return out}
function allScripts(){let out=[];docs(document).forEach(d=>out=out.concat(scripts(d)));let seen={};return out.filter(x=>{let k=x.id+'|'+x.src;if(seen[k])return false;seen[k]=1;return true})}
function hasScript(rx){return allScripts().some(x=>rx.test(x.src)||rx.test(x.id))}
function hasReceipt(k){return !!get(k)}
function status(ok,fail,prov){if(fail)return'failed';if(ok)return prov?'provisional':'complete';return'missing_proof'}
function domSurvey(){let r={};docs(document).forEach(d=>{try{let bank=d.getElementById('bank');if(bank){let run=bank.querySelector('[data-run-bank-tools],[data-continuous-run-owner-slot-v1]');r.bank_present=true;r.bank_detail_title=clean((bank.querySelector('[data-bank-detail-title]')||{}).textContent||'');r.continuous_run_slot_present=!!run;r.continuous_run_owner_content=!!(run&&run.querySelector('[data-bank-screen-owner-v1]'));r.level_scope_present=!!(run&&run.querySelector('[data-continuous-run-level-ui-scope-v1]'));r.level1_present=!!(run&&run.querySelector('[data-bso-level1]'));r.level2_present=!!(run&&run.querySelector('[data-bso-level2]'));r.level3plus_stack_present=!!(run&&run.querySelector('[data-cr-level-stack]'));r.loose_level_nodes=Array.from(bank.querySelectorAll('[data-source-text-reader-level3],[data-source-reference-gate-level4],[data-source-reference-gate-level4b],[data-level30-final-seal],[data-resident-l30b-auto-gate]')).filter(x=>!(x.closest&&x.closest('[data-cr-level-stack]'))).length}}catch(e){}});return r}
function classifyScripts(){let list=allScripts();let classes=[];
function add(name,rx,role,expected_owner,risk){let matches=list.filter(x=>rx.test(x.src)||rx.test(x.id));if(matches.length)classes.push({name,role,expected_owner,risk:risk||'unknown',matches})}
add('route/current loader',/route-guardian|current-reload-owner|current-inner/i,'route_startup_owner','Route Guardian / Reload Owner','critical_owner');
add('app orchestrator / frame loader',/continuous-run-bank-order-frame-loader|app-orchestrator/i,'orchestrator_loader','App Orchestrator','can_reinject_scripts');
add('safe area surface fill',/safe-area-surface-fill/i,'surface_loader','Surface Shell','can_load_helpers');
add('master bank tab',/master-bank-tab/i,'section_owner','Bank Owner','bank_shell_owner');
add('bank screen owner',/bank-screen-owner/i,'section_owner','Continuous Run Owner','continuous_run_slot_owner');
add('continuous run level ui scope',/continuous-run-level-ui-scope/i,'owner_helper_boundary','Continuous Run Owner helper','moves_level_panels');
add('bug bank',/bug-bank/i,'section_owner_or_helper','Bug Bank Owner','may_scan_bank_detail');
add('diagnostics owner',/diagnostics-owner|owner-diagnostics/i,'diagnostic','Diagnostics Owner','should_not_control_surfaces');
add('helper registry',/helper-registry|helper-bank/i,'helper_registry','Helper Governance','registry_only_expected');
add('section owner registry',/section-owner-registry/i,'owner_registry','Owner Governance','registry_only_expected');
add('control room',/control-room|control-diagnostics|control-legacy/i,'control_owner_or_legacy','Control Owner','legacy_risk');
add('repair/probe/guard scripts',/repair|probe|guard|forcer|cleaner|stabilizer|blocker/i,'guard_or_repair','various','high_if_moves_or_hides_dom');
return{script_count:list.length,classes,raw:list}
}
function passAudit(){let dom=domSurvey(),sc=classifyScripts(),receipts={
 route_guardian:hasReceipt('pmp_route_guardian_v22_receipt'),
 app_orchestrator:hasReceipt('pmp_app_orchestrator_v1_receipt'),
 section_owner_registry:hasReceipt('pmp_section_owner_registry_v1_receipt')||hasReceipt('pmp_section_owner_registry_snapshot_v1'),
 helper_registry:hasReceipt('pmp_helper_registry_v1_receipt')||hasReceipt('pmp_helper_registry_snapshot_v1'),
 diagnostics:hasReceipt('pmp_owner_diagnostics_foundation_v1_receipt')||hasReceipt('pmp_diagnostics_owner_v1_receipt'),
 pass7_certification:hasReceipt('pmp_pass7_certification_gate_receipt_v1')||hasReceipt('pmp_pass7_certification_decision_v1'),
 bank_slot_contract:hasReceipt('pmp_pass9_bank_owner_slot_contract_v1_receipt'),
 bank_screen_owner:hasReceipt('pmp_bank_screen_owner_v1_receipt'),
 level_scope:hasReceipt('pmp_continuous_run_level_ui_scope_v1_receipt')
};
let repairScripts=sc.raw.filter(x=>/repair|probe|guard|forcer|cleaner|stabilizer|blocker/i.test(x.src)||/repair|probe|guard|forcer|cleaner|stabilizer|blocker/i.test(x.id));
let legacyRisk=sc.raw.filter(x=>/legacy|migration|quarantine|visible-run|native-load-order-repair|probe-bridge/i.test(x.src)||/legacy|migration|quarantine|visible-run|native-load-order-repair|probe-bridge/i.test(x.id));
return[
 {pass:1,name:'Route/current path',status:status(receipts.route_guardian&&hasScript(/route|current/i),false,false),proof:{receipt:receipts.route_guardian,script:hasScript(/route|current/i)},notes:'Checks active route/current path proof only; not a full visual certification.'},
 {pass:2,name:'Startup chain / launcher continuity',status:status(hasScript(/continuous-run-bank-order-frame-loader|current-inner/i),false,true),proof:{loader:hasScript(/continuous-run-bank-order-frame-loader/i),current_inner:hasScript(/current-inner/i)},notes:'Provisional because the frame loader still reinjects scripts on intervals.'},
 {pass:3,name:'App Orchestrator as conductor',status:status(receipts.app_orchestrator&&hasScript(/continuous-run-bank-order-frame-loader|app-orchestrator/i),false,true),proof:{receipt:receipts.app_orchestrator,loader_present:hasScript(/continuous-run-bank-order-frame-loader|app-orchestrator/i)},notes:'Provisional: conductor exists, but older loaders still inject owner/helper scripts.'},
 {pass:4,name:'Mount Registry / legal slots',status:status(receipts.section_owner_registry,dom.continuous_run_slot_present&&!dom.continuous_run_owner_content,false),proof:{section_owner_registry:receipts.section_owner_registry,continuous_run_slot_present:dom.continuous_run_slot_present,continuous_run_owner_content:dom.continuous_run_owner_content},notes:dom.continuous_run_slot_present?'Legal slot exists for Continuous Run when Bank is open.':'Cannot prove live slot until Bank/Continuous Run is open.'},
 {pass:5,name:'Diagnostics observes, does not control surfaces',status:status(receipts.diagnostics||hasScript(/diagnostics-owner|owner-diagnostics/i),legacyRisk.length>0,true),proof:{diagnostics_receipt:receipts.diagnostics,diagnostics_scripts:hasScript(/diagnostics-owner|owner-diagnostics/i),legacy_risk_count:legacyRisk.length},notes:legacyRisk.length?'Provisional/at risk because legacy diagnostic/migration/quarantine style scripts are still discoverable in source or runtime list.':'No obvious legacy diagnostic risk in loaded script list.'},
 {pass:6,name:'Safety / no destructive writes',status:status(true,repairScripts.some(x=>/native-load-order-repair|control-diagnostics-migration|legacy-diagnostics-quarantine/i.test(x.src)),true),proof:{repair_or_guard_script_count:repairScripts.length,known_dangerous_loaded:repairScripts.filter(x=>/native-load-order-repair|control-diagnostics-migration|legacy-diagnostics-quarantine/i.test(x.src)).map(x=>x.src)},notes:'Provisional because many guard/repair scripts exist. Need source-level classification before complete.'},
 {pass:7,name:'Section owners: one owner per visible section',status:status(receipts.section_owner_registry&&dom.bank_present,repairScripts.length>0,true),proof:{section_owner_registry:receipts.section_owner_registry,bank_present:dom.bank_present,bank_owner_script:hasScript(/master-bank-tab/i),continuous_run_owner_script:hasScript(/bank-screen-owner/i),repair_guard_count:repairScripts.length},notes:'Not fully complete until every visible surface has exactly one active writer and guard/helper writers are contained.'},
 {pass:8,name:'Helpers mapped and contained',status:status(receipts.helper_registry,repairScripts.length>0,true),proof:{helper_registry:receipts.helper_registry,helper_scripts:hasScript(/helper/i),repair_guard_count:repairScripts.length,classified_script_classes:sc.classes.length},notes:'Provisional because active guard/helper/level scripts still move, hide, or reorder DOM. Need conflict map.'}
 ]}
function summary(passes){let failed=passes.filter(p=>p.status==='failed'),missing=passes.filter(p=>p.status==='missing_proof'),prov=passes.filter(p=>p.status==='provisional'),complete=passes.filter(p=>p.status==='complete');let overall=failed.length?'FAILED':(missing.length?'MISSING_PROOF':(prov.length?'PROVISIONAL_NOT_CERTIFIED':'COMPLETE'));return{overall,counts:{complete:complete.length,provisional:prov.length,failed:failed.length,missing_proof:missing.length},complete:complete.map(p=>p.pass),provisional:prov.map(p=>p.pass),failed:failed.map(p=>p.pass),missing_proof:missing.map(p=>p.pass)}}
function run(reason){let dom=domSurvey(),scripts=classifyScripts(),passes=passAudit(),sum=summary(passes);let report={type:'PMP_PASS_REVALIDATION_GATE_001_V1_RECEIPT',version:V,at:now(),reason:reason||'runtime_audit',status:sum.overall,summary:sum,passes,dom_survey:dom,script_classification:scripts.classes,script_count:scripts.script_count,raw_scripts:scripts.raw,decision:{pass1_to_8_fully_certified:sum.overall==='COMPLETE',safe_to_certify_pass9:false,next_required_action:'Build owner/helper conflict map before more visual patching.'},side_effects:{visual_patch:'not_attempted',dom_move:'not_attempted',dom_hide:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',route_change:'not_attempted'}};put(KEY,report);put(TRACE,{type:'PMP_PASS_REVALIDATION_GATE_001_TRACE',version:V,updated_at:now(),latest_status:sum.overall,summary:sum});return report}
window.PMPPassRevalidationGate001V1={version:V,run,getLast:()=>get(KEY),rule:'Receipt-only audit. No visual patching or repair.'};try{T().PMPPassRevalidationGate001V1=window.PMPPassRevalidationGate001V1}catch(e){};
window.addEventListener('load',()=>[0,300,1000,2500,5000,9000].forEach(t=>setTimeout(()=>run('load_'+t),t)));
setTimeout(()=>run('initial'),0);
})();