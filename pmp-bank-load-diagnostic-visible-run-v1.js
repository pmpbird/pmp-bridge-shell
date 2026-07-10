(()=>{
'use strict';
const V='1.0.1-disabled-rollback-20260710A';
const OWNER='pmp-bank-load-diagnostic-visible-run-v1';
const RECEIPT='pmp_bank_load_diagnostic_visible_run_v1_receipt';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function run(){let r={type:'PMP_BANK_LOAD_DIAGNOSTIC_VISIBLE_RUN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'DISABLED_ROLLBACK',rule:'Rollback: this script no longer intercepts Bank Load Diagnostic buttons. It does not touch Bank, Diagnostics buttons, routes, storage, IndexedDB, or DOM.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',button_intercept:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted'}};put(RECEIPT,r);return r}
window.PMPBankLoadDiagnosticVisibleRunV1={version:V,owner:OWNER,run,rule:'Disabled rollback version. No interception.'};try{T().PMPBankLoadDiagnosticVisibleRunV1=window.PMPBankLoadDiagnosticVisibleRunV1}catch(e){};
run();
})();