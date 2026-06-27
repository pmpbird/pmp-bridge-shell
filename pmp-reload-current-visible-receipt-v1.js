(()=>{
  const V='2.6.0-quiet-reload-no-visible-receipt';
  const UI='data-pmp-reload-current-visible-receipt-v1';
  const BTN='data-pmp-route-code-map-copy-suggestions-v1';
  const PREVIEW_BTN='data-pmp-route-code-map-copy-preview-v1';
  const CHECKLIST_BTN='data-pmp-route-code-map-copy-checklist-v1';
  function T(){try{return top||window}catch(e){return window}}
  function docs(d,a,n){a=a||[];n=n||0;if(!d||n>10)return a;try{a.push(d);d.querySelectorAll('iframe').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
  function removeOne(x){try{x.remove()}catch(e){try{x.parentNode&&x.parentNode.removeChild(x)}catch(_){}}}
  function quiet(d){try{d.querySelectorAll('['+UI+']').forEach(removeOne);d.querySelectorAll('['+BTN+'],['+PREVIEW_BTN+'],['+CHECKLIST_BTN+']').forEach(b=>{let box=b.parentNode;if(box&&(box.querySelector('['+BTN+']')||box.querySelector('['+PREVIEW_BTN+']')||box.querySelector('['+CHECKLIST_BTN+']')))removeOne(box);else removeOne(b)})}catch(e){}}
  function scan(){try{docs(T().document).forEach(quiet)}catch(e){}}
  function summary(){return 'Quiet reload mode: no visible receipt; Reload Current still captures/restores the current page and cache-busts the shell.'}
  T().PMPReloadCurrentVisibleReceiptV1={version:V,mode:'quiet_no_visible_receipt',scan,summary};
  addEventListener('load',()=>[100,400,1000,2500,5000].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,1500);
  scan();
})();
