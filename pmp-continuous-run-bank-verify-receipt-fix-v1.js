(()=>{
'use strict';
const V='2.0.0-owner-delegating-event-driven-20260727A';
function owner(){return window.PMPContinuousRunBankTransferStoreV1||null}
function check(){const api=owner();return api&&typeof api.verifyStore==='function'?api.verifyStore(false):{status:'OWNER_NOT_READY',manifest_write:false}}
function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>8)return out;try{out.push(root);root.querySelectorAll('iframe').forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function patch(d){
  const box=d.querySelector('[data-temp-transfer-store]');if(!box)return;
  const button=box.querySelector('[data-tts-verify]');if(!button||button.dataset.ownerDelegating==='1')return;
  button.dataset.ownerDelegating='1';
  button.addEventListener('click',()=>{
    const api=owner(),out=d.querySelector('[data-bank-out]');
    if(!api||typeof api.verifyStore!=='function'){if(out){out.classList.remove('hidden');out.textContent='Transfer-store owner is not ready.'}return}
    const result=api.verifyStore(true);
    if(out){out.classList.remove('hidden');out.textContent=result.lossless_verified?'Lossless verification passed.':'Verification complete; required items are still missing.'}
  });
}
function scan(){docs(document).forEach(patch);return{status:'EVENT_DRIVEN_OWNER_DELEGATION',canonical_write:false}}
window.PMPVerifyStoreReceiptFixV1={version:V,owner:'bank_screen_owner',role:'compatibility_event_delegate',scan,check,rule:'No timer, no direct manifest or receipt write, and no independent verification schema. The canonical transfer-store owner performs verification.'};
window.addEventListener('load',scan,{once:true});scan();
})();
