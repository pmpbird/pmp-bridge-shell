(()=>{
'use strict';
const V='3.2.0-mode1-allow-list-only';
const ALLOW=/pmp_packet_1_5|master inventory test records|\b(testing|test|placeholder|sample|todo|tbd)\b/i;
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function cleanText(t){return String(t||'').replace(/Test artifact:/ig,'').replace(/Saved packet:/ig,'').replace(/auto-selected/ig,'').replace(/\s+/g,' ').trim()}
function keep(label){return ALLOW.test(cleanText(label.textContent||''))}
function enforce(doc){try{doc.querySelectorAll('[data-bank-delete-modes]').forEach(box=>{if((box.getAttribute('data-mode')||'test')!=='test')return;box.querySelectorAll('[data-clean-list] label').forEach(label=>{if(!keep(label)){let input=label.querySelector('input');if(input)input.checked=false;label.remove();}})})}catch(e){}}
function resetOnce(doc){try{let bank=doc.getElementById('bank');if(!bank||bank.getAttribute('data-delete-tools-stabilized')==='1')return;bank.setAttribute('data-delete-tools-stabilized','1');bank.querySelectorAll('[data-bank-delete-modes]').forEach(x=>x.remove());}catch(e){}}
function scan(){docs(document).forEach(resetOnce);try{window.PMPBankScopedTestDataCleanerV1&&window.PMPBankScopedTestDataCleanerV1.scan&&window.PMPBankScopedTestDataCleanerV1.scan()}catch(e){}setTimeout(()=>docs(document).forEach(enforce),40)}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[50,250,900,1600,2600].forEach(t=>setTimeout(scan,t)));
setInterval(scan,500);scan();
})();