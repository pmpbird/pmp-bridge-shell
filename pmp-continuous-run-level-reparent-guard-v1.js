(()=>{
'use strict';
const V='1.0.1-disabled';
function scan(){try{localStorage.setItem('pmp_continuous_run_level_reparent_guard_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_LEVEL_REPARENT_GUARD_V1',version:V,at:new Date().toISOString(),status:'disabled',reason:'DOM reparenting made Continuous Run layout worse. Future fix must use one layout owner, not a moving guard.'}))}catch(e){}}
window.PMPContinuousRunLevelReparentGuardV1={version:V,scan,disabled:true};
window.addEventListener('load',scan);
scan();
})();