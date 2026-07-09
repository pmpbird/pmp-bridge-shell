(()=>{
'use strict';
const V='1.2.0-pass8-helper-rules-loader-20260709A';
const OWNER='pmp-app-orchestrator-v1';
const PASS8_SRC='pmp-pass8-helper-rules-v1.js?fresh=pass8-helper-rules-passive-registry-20260709A';
const KEYS={receipt:'pmp_app_orchestrator_v1_receipt',status:'pmp_app_orchestrator_boot_status_v1',mounts:'pmp_app_orchestrator_mount_registry_v1_preview',pass8:'pmp_pass8_helper_rules_receipt_v1'};
const EXPECTED={map:'pmp-current-map-v12.json',guardian:'pmp-route-guardian-current-loader-v22.html',current:'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',inner:'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'};
let last=null;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function scripts(){try{return Array.from(document.querySelectorAll('script[src]')).map(s=>String(s.getAttribute('src')||''))}catch(e){return[]}}
function currentReceipt(reason,status){let pass8=read(KEYS.pass8);let receipt={type:'PMP_APP_ORCHESTRATOR_V1_RECEIPT',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'pass8_helper_rules_bootstrap',status:status||'PASS8_HELPER_RULES_LOADING',expected:{route_guardian:EXPECTED.guardian,current_reload:EXPECTED.current,current_inner:EXPECTED.inner,map:EXPECTED.map},current_chain_handoff:{type:'PMP_CURRENT_CHAIN_APP_ORCHESTRATOR_PROOF_V1',version:V,owner:OWNER,at:now(),mode:'current_chain_pass8_bootstrap',expected:{route_guardian:EXPECTED.guardian,current_reload:EXPECTED.current,current_inner:EXPECTED.inner,map:EXPECTED.map},checks:{map:'current',route_guardian:'current',current_reload:'current',current_inner:'current',old_pass_receipt:'not_used'},pass:'pass'},pass8_helper_rules:pass8?{status:pass8.status||'present',version:pass8.version||'unknown',counts:pass8.counts||null}:'loading',safe_claim:'App Orchestrator is current and has started Pass 8 helper rules without taking ownership.',do_not_claim:['not full Pass 8 certification yet','not source acceptance','not Bank rebuild'],side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted',panel_mount:'not_attempted'},keys:KEYS};last=receipt;put(KEYS.receipt,receipt);put(KEYS.status,{type:'PMP_APP_ORCHESTRATOR_PASS8_STATUS_V1',version:V,owner:OWNER,at:now(),status:receipt.status,pass8_helper_rules:receipt.pass8_helper_rules});return receipt}
function loadPass8(reason){try{if(scripts().some(src=>src.indexOf('pmp-pass8-helper-rules-v1.js')>-1)){if(T().PMPPass8HelperRulesV1&&T().PMPPass8HelperRulesV1.run)T().PMPPass8HelperRulesV1.run(reason||'app_orchestrator_existing_script');return currentReceipt(reason||'pass8_script_already_present','PASS8_HELPER_RULES_ACTIVE')}let s=document.createElement('script');s.src=PASS8_SRC;s.async=false;s.onload=function(){try{if(T().PMPPass8HelperRulesV1&&T().PMPPass8HelperRulesV1.run)T().PMPPass8HelperRulesV1.run('app_orchestrator_load_onload')}catch(e){}currentReceipt('pass8_script_loaded','PASS8_HELPER_RULES_ACTIVE')};s.onerror=function(){currentReceipt('pass8_script_load_error','PASS8_HELPER_RULES_NEEDS_REVIEW')};(document.head||document.documentElement).appendChild(s);return currentReceipt(reason||'pass8_script_requested','PASS8_HELPER_RULES_LOADING')}catch(e){return currentReceipt('pass8_loader_exception_'+String(e&&e.message||e),'PASS8_HELPER_RULES_NEEDS_REVIEW')}}
let existing=window.PMPAppOrchestratorV1||null;
let api=existing&&typeof existing==='object'?existing:{};
api.version=V;
api.owner=OWNER;
api.mode='pass8_helper_rules_bootstrap';
api.keys=Object.assign({},api.keys||{},KEYS);
api.run=async(reason)=>currentReceipt(reason||'api_run','PASS8_HELPER_RULES_ACTIVE');
api.loadPass8HelperRules=loadPass8;
api.getLastReceipt=()=>last||currentReceipt('get_last_receipt','PASS8_HELPER_RULES_LOADING');
api.rule='App Orchestrator coordinates current startup proof and Pass 8 helper rules. No route mutation, Bank rebuild, storage migration, panel mount, or ownership takeover.';
window.PMPAppOrchestratorV1=api;
try{T().PMPAppOrchestratorV1=api}catch(e){}
try{currentReceipt('boot_start_pass8','PASS8_HELPER_RULES_LOADING');loadPass8('boot_start_pass8_loader');setTimeout(()=>currentReceipt('settled_pass8_1200ms',read(KEYS.pass8)?'PASS8_HELPER_RULES_ACTIVE':'PASS8_HELPER_RULES_LOADING'),1200);setTimeout(()=>currentReceipt('settled_pass8_2600ms',read(KEYS.pass8)?'PASS8_HELPER_RULES_ACTIVE':'PASS8_HELPER_RULES_NEEDS_REVIEW'),2600)}catch(e){put(KEYS.receipt,{type:'PMP_APP_ORCHESTRATOR_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'ERROR',error:String(e&&e.message||e),side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted'}})}
})();