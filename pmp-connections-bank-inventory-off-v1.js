(()=>{
'use strict';
const V='1.0.1-omit-button',OWNER='pmp-connections-bank-inventory-off-v1';
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function text(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function cleanDoc(d){try{Array.from(d.querySelectorAll('button')).forEach(b=>{if(/bank inventory/i.test(text(b))){b.replaceWith(d.createTextNode(''))}})}catch(e){}}
function patchWin(w){try{if(!w)return;w.openBankInventoryProtectedRegistry=function(){return false};w.renderBankInventory=function(){return false};w.injectBankInventoryButton=function(){return false};if(w.__pmpBridgePanelToggleFixV3&&w.__pmpBridgePanelToggleFixV3.active==='bankInventory')w.__pmpBridgePanelToggleFixV3.active='connections'}catch(e){}}
function scan(){docs(document).forEach(d=>{cleanDoc(d);try{patchWin(d.defaultView)}catch(e){}})}
window.PMPConnectionsBankInventoryOffV1={version:V,owner:OWNER,scan};window.addEventListener('load',()=>[50,150,400,900,1800].forEach(t=>setTimeout(scan,t)));setInterval(scan,350);scan();
})();
