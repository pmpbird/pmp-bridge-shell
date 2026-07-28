(()=>{
'use strict';
const V='2.0.0-read-only-compatibility-20260727A';
function read(){try{return JSON.parse((window.top||window).localStorage.getItem('pmp_continuous_run_bank_transfer_store_manifest_v1')||'{}')}catch(e){return{}}}
function state(){const m=read(),zip=m.must_reference_source_zip||{};return{type:'PMP_LONG_PACKET_OPTION_COMPATIBILITY_VIEW_V2',version:V,status:zip.present?'SOURCE_ZIP_PRESENT':'SOURCE_ZIP_MISSING',present:!!zip.present,mode:zip.present?'SOURCE ZIP PRESENT':'MISSING',canonical_writer:'pmp-continuous-run-bank-transfer-store-v2.js',manifest_write:false}}
window.PMPLongPacketOptionV1={version:V,state,scan:state,rule:'Read-only compatibility view. The transfer-store owner alone commits long-source state.'};
})();
