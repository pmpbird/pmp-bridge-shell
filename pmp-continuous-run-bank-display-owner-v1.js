(()=>{
'use strict';
const V='1.0.1-disabled-black-buttons';
function scan(){try{localStorage.setItem('pmp_cr_display_owner_show_native_v1','1');localStorage.setItem('pmp_continuous_run_bank_display_owner_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_BANK_DISPLAY_OWNER_V1',version:V,at:new Date().toISOString(),status:'disabled',reason:'Single-owner black button display was visually wrong. It must not render or hide native Continuous Run panels.'}))}catch(e){}try{document.querySelectorAll('[data-cr-display-owner-v1]').forEach(x=>x.remove());document.querySelectorAll('[data-cr-display-owner-hidden]').forEach(x=>{x.style.removeProperty('display');x.removeAttribute('data-cr-display-owner-hidden')})}catch(e){}}
window.PMPContinuousRunBankDisplayOwnerV1={version:V,scan,disabled:true};
window.addEventListener('load',scan);
setTimeout(scan,100);
setTimeout(scan,600);
setTimeout(scan,2000);
scan();
})();