(()=>{
'use strict';
const V='3.0.0-stabilize-main-cleaner-owner';
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function clearOld(doc){try{let bank=doc.getElementById('bank');if(!bank||bank.getAttribute('data-delete-tools-stabilized')==='1')return;bank.setAttribute('data-delete-tools-stabilized','1');bank.querySelectorAll('[data-bank-delete-modes]').forEach(x=>x.remove());}catch(e){}}
function scan(){docs(document).forEach(clearOld);try{window.PMPBankScopedTestDataCleanerV1&&window.PMPBankScopedTestDataCleanerV1.scan&&window.PMPBankScopedTestDataCleanerV1.scan()}catch(e){}}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[50,250,900,1600,2600].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1600);scan();
})();