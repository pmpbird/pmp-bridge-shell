(()=>{
'use strict';
const V='2.0.0-read-only-gate-compatibility-20260727A';
function api(){return window.PMPContinuousRunBankTransferStoreV1||null}
function scan(){const owner=api(),gate=owner&&typeof owner.engineGate==='function'?owner.engineGate():{ok:false,reason:'owner_not_ready'};return{type:'PMP_SOURCE_ZIP_GATE_COMPATIBILITY_VIEW_V2',version:V,status:gate.ok?'PASS':'BLOCKED',gate,canonical_writer:'pmp-continuous-run-bank-transfer-store-v2.js',manifest_write:false,dom_write:false}}
window.PMPSourceZipGateFixV1={version:V,scan,rule:'Read-only compatibility view. No API wrapping, manifest rewrite, timer, or DOM patch.'};
})();
