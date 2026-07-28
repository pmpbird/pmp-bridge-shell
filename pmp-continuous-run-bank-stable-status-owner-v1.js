(()=>{
'use strict';
const V='2.0.0-read-only-compatibility-20260727A';
function inspect(){let manifest=null;try{manifest=JSON.parse((window.top||window).localStorage.getItem('pmp_continuous_run_bank_transfer_store_manifest_v1')||'null')}catch(e){}return{type:'PMP_STABLE_STATUS_COMPATIBILITY_VIEW_V2',version:V,status:'INACTIVE_READ_ONLY',manifest_present:!!manifest,canonical_surface_owner:'pmp-bank-screen-owner-v1.js',status_clone:false,original_hide:false,dom_write:false,recurring_timer:false}}
window.PMPStableStatusOwnerV1={version:V,inspect,patch:inspect,rule:'Historic status cloner is inert. The Bank Screen Owner renders the one canonical status surface.'};
})();
