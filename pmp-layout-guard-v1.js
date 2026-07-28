(()=>{
'use strict';
const V='5.0.0-read-only-compatibility-20260727A';
function inspect(){let manifest=null;try{manifest=JSON.parse((window.top||window).localStorage.getItem('pmp_continuous_run_bank_transfer_store_manifest_v1')||'null')}catch(e){}return{type:'PMP_LAYOUT_GUARD_COMPATIBILITY_VIEW_V5',version:V,status:'INACTIVE_READ_ONLY',manifest_present:!!manifest,canonical_surface_owner:'pmp-bank-screen-owner-v1.js',dom_write:false,script_load:false,recurring_timer:false}}
window.PMPLayoutGuardV4={version:V,inspect,scan:inspect,rule:'Historic layout guard is inert. Bank Screen Owner and Continuous Run Level UI Scope own the approved one-card presentation.'};
})();
