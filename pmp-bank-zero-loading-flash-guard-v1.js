(()=>{
'use strict';
const V='2.0.0-read-only-owner-readiness-20260727A';
function isRealReady(screen){
  const home=screen&&screen.querySelector('[data-bank-home]'),buttons=screen&&screen.querySelector('[data-bank-buttons]'),router=screen&&screen.querySelector('[data-bank-router]');
  if(!home||!buttons)return false;
  const openers=buttons.querySelectorAll('[data-open-bank]').length,text=String(buttons.textContent||'').replace(/\s+/g,' ').trim(),route=String(router&&router.textContent||'');
  return openers>=10&&!!text&&!/^Loading/i.test(text)&&!/Router loading/i.test(route);
}
function inspect(){const screen=document.getElementById('bank');return{type:'PMP_BANK_ZERO_LOADING_FLASH_COMPATIBILITY_VIEW_V2',version:V,status:screen?(isRealReady(screen)?'OWNER_READY':'OWNER_NOT_READY'):'BANK_NOT_IN_THIS_FRAME',canonical_surface_owner:'pmp-master-bank-tab-v1.js',visibility_write:false,observer:false,recurring_timer:false}}
window.PMPBankZeroLoadingFlashGuardV1={version:V,inspect,scan:inspect,isRealReady,rule:'Read-only readiness diagnostic. The canonical Bank owner controls visibility and paint state.'};
})();
