(()=>{
'use strict';
const V='1.0.1-data-only-bank-screen-owner';
function scan(){return false}
function run(){return false}
function test(){return {type:'PMP_CURRENT_PAGE_SNAPSHOT_TEST_LAUNCHER_V1_RECEIPT',version:V,status:'DATA_ONLY_NO_SCREEN_BUTTON',pass:true}}
function receipt(){try{return JSON.parse((top||window).localStorage.getItem('pmp_current_page_snapshot_test_launcher_v1_receipt')||'null')}catch(e){return null}}
window.PMPCurrentPageSnapshotTestLauncherV1={version:V,data_only:true,run,test,receipt,scan};
})();
