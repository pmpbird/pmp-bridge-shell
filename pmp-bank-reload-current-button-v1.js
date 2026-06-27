(()=>{
'use strict';
const V='1.4.1-disabled-after-bank-screen-conflict';
function run(){return false}
function restore(){return false}
function capture(){return null}
function verify(){return false}
function clear(){try{localStorage.removeItem('pmp_reload_current_live_snapshot_v12');localStorage.removeItem('pmp_reload_current_v1_temp_snapshot')}catch(e){}return true}
function scan(){clear();return false}
window.PMPLiveReloadRestoreV12={version:V,disabled:true,run,restore,capture,verify,clear,lastSnapshot:()=>null,lastTest:()=>null};
window.PMPBankReloadCurrentButtonV1=window.PMPLiveReloadRestoreV12;
})();
