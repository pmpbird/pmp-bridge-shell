(function(){
'use strict';
function textOf(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim();}
function applyCleanup(doc){
  if(!doc)return;
  Array.from(doc.querySelectorAll('button')).forEach(function(button){
    var text=textOf(button);
    if(text.indexOf('Automatic App Update')!==-1 || text.indexOf('Open Code Safety')!==-1){
      button.dataset.pmpControlRoomCleanup='route-guardian-owned';
      button.style.display='none';
    }
  });
}
window.PMPControlRoomCleanupV1={apply:applyCleanup};
})();
