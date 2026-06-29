(()=>{
'use strict';
const V='1.0.1-disabled-no-move';
function scan(){try{localStorage.setItem('pmp_continuous_run_helper_conflict_blocker_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_HELPER_CONFLICT_BLOCKER_V1',version:V,at:new Date().toISOString(),status:'disabled_no_move',rule:'No helper blocker may move DOM panels. Conflict must be fixed by the owning layout only.'}))}catch(e){}}
window.PMPContinuousRunHelperConflictBlockerV1={version:V,scan,disabled:true};
window.addEventListener('load',scan);
scan();
})();