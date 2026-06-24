(()=>{
'use strict';
const V='3.1.0-strict-connections-visible-mode1';
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function keyText(t){return String(t||'').replace(/Test artifact:/ig,'').replace(/Saved packet:/ig,'').replace(/auto-selected/ig,'').replace(/\s+/g,' ').trim()}
function allowedConnectionsMode1(t){let k=keyText(t);if(/master inventory test records/i.test(k))return true;if(/pmp_packet_1_5/i.test(k))return true;if(/\b(testing|test|placeholder|sample|todo|tbd)\b/i.test(k))return true;return false}
function forbiddenConnectionsMode1(t){let k=keyText(t);return /raw_addon|field_registry|single_resident|connection_bank_inventory|resident_xray|current_resident|route_guardian|packet_engine|chat_memory_deposit_current/i.test(k)&&!/\b(testing|test|placeholder|sample|todo|tbd)\b/i.test(k)&&!/pmp_packet_1_5/i.test(k)}
function enforce(doc){try{doc.querySelectorAll('[data-bank-delete-modes][data-bank-scope="connections"]').forEach(box=>{let mode=box.getAttribute('data-mode')||'test';if(mode!=='test')return;box.querySelectorAll('[data-clean-list] label').forEach(label=>{let txt=label.textContent||'';if(forbiddenConnectionsMode1(txt)||!allowedConnectionsMode1(txt)){let input=label.querySelector('input');if(input)input.checked=false;label.remove();}})})}catch(e){}}
function clearOld(doc){try{let bank=doc.getElementById('bank');if(!bank||bank.getAttribute('data-delete-tools-stabilized')==='1')return;bank.setAttribute('data-delete-tools-stabilized','1');bank.querySelectorAll('[data-bank-delete-modes]').forEach(x=>x.remove());}catch(e){}}
function scan(){docs(document).forEach(clearOld);try{window.PMPBankScopedTestDataCleanerV1&&window.PMPBankScopedTestDataCleanerV1.scan&&window.PMPBankScopedTestDataCleanerV1.scan()}catch(e){}setTimeout(()=>docs(document).forEach(enforce),30)}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[50,250,900,1600,2600].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);scan();
})();