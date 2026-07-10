(()=>{
'use strict';
const V='1.0.2-disabled-flicker-rollback-20260710A';
const OWNER='pmp-bank-native-load-order-repair-v1';
const KEY='pmp_bank_native_load_order_repair_v1_receipt';
const REPORT='pmp_bank_native_load_order_repair_v1_report';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function run(reason){let r={type:'PMP_BANK_NATIVE_LOAD_ORDER_REPAIR_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'DISABLED_FLICKER_ROLLBACK',reason:reason||'run',rule:'Disabled because repeated native Bank repair caused owner/helper repaint contention. Pass 9 should resolve Bank ownership instead of using an active repaint helper.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_records_change:'not_attempted',bank_dom_patch:'not_attempted',panel_move:'not_attempted',panel_hide:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',other_tabs:'not_touched'}};put(KEY,r);put(REPORT,Object.assign({type:'PMP_BANK_NATIVE_LOAD_ORDER_REPAIR_V1_REPORT'},r));return r}
function hookTabs(){return run('disabled_hookTabs_noop')}
window.PMPBankNativeLoadOrderRepairV1={version:V,owner:OWNER,run,hookTabs,rule:'Disabled rollback version. No repaint loop and no DOM patching.'};try{T().PMPBankNativeLoadOrderRepairV1=window.PMPBankNativeLoadOrderRepairV1}catch(e){};
run('script_load_disabled');
})();