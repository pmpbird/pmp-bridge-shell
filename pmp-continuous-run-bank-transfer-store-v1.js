(()=>{
'use strict';
const V='1.1.0-inactive-read-only-compatibility-20260727A';
function current(){return window.PMPContinuousRunBankTransferStoreV1&&window.PMPContinuousRunBankTransferStoreV1.version!==V?window.PMPContinuousRunBankTransferStoreV1:null}
function readManifest(){const api=current();if(api&&typeof api.readManifest==='function')return api.readManifest();try{return JSON.parse(localStorage.getItem('pmp_continuous_run_bank_transfer_store_manifest_v1')||'null')}catch(e){return null}}
function receipts(){const api=current();if(api&&typeof api.receipts==='function')return api.receipts();try{return JSON.parse(localStorage.getItem('pmp_continuous_run_bank_transfer_store_receipts_v1')||'[]')}catch(e){return[]}}
const compatibility={version:V,owner:'bank_screen_owner',active_writer:false,readManifest,receipts,rule:'Historic V1 is an inactive read-only compatibility adapter. It never opens IndexedDB for writing and never writes the canonical manifest or receipt.'};
window.PMPContinuousRunBankTransferStoreLegacyV1=compatibility;
if(!window.PMPContinuousRunBankTransferStoreV1)window.PMPContinuousRunBankTransferStoreV1=compatibility;
})();
