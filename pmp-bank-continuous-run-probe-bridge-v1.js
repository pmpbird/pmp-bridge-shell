(()=>{
'use strict';
const V='1.0.1-disabled-rollback-20260710A';
const OWNER='pmp-bank-continuous-run-probe-bridge-v1';
const KEY='pmp_bank_continuous_run_probe_bridge_v1_receipt';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function run(){let r={type:'PMP_BANK_CONTINUOUS_RUN_PROBE_BRIDGE_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'DISABLED_ROLLBACK',rule:'Rollback: this bridge no longer intercepts the Diagnostics probe button. The Bank load problem is in the Bank tab, not the probe path.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',panel_move:'not_attempted',panel_hide:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted'}};put(KEY,r);return r}
window.PMPBankContinuousRunProbeBridgeV1={version:V,owner:OWNER,run,rule:'Disabled rollback version. No interception.'};try{T().PMPBankContinuousRunProbeBridgeV1=window.PMPBankContinuousRunProbeBridgeV1}catch(e){};
run();
})();