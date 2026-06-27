(()=>{
'use strict';
const V='1.1.0-staging-transfer-store-universal-layout';
const DELETE_BUTTONS=new Set(['Reload Current','Test Current Page']);
const UNIVERSAL_OPTIONS=[
  ['source_bundle','Source Bundle'],
  ['extracted_source_text','Extracted Source Text'],
  ['source_identity_profile','Source Identity Profile'],
  ['rules_constraints','Rules / Constraints'],
  ['current_work_item','Current Work Item'],
  ['work_queue','Work Queue'],
  ['receipts_state','Receipts / State'],
  ['tests_acceptance','Tests / Acceptance'],
  ['permissions','Permissions'],
  ['proof_manifest','Proof / Manifest'],
  ['recovery_rollback','Recovery / Rollback'],
  ['project_profile','Project Profile / Registry Link'],
  ['custom_item','Custom Item'],
  ['transfer_pack','Transfer Pack'],
  ['packet_0','Packet 0'],
  ['packet_1','Packet 1'],
  ['packet_1_5_guide','Packet 1.5 Guide'],
  ['raw_packets','Raw Packets'],
  ['current_work_source','Current Work Source'],
  ['receipts_or_state','Receipts or State'],
  ['receiver_test_checklist','Receiver Test Checklist / Rules'],
  ['no_spend_rules','No-Spend / Permission Rules'],
  ['packet_queue','Packet / Work Queue'],
  ['helper_registry','Helper Registry'],
  ['rollback_points','Rollback Points'],
  ['other','Other Transfer Material']
];
function txt(s){return String(s||'').replace(/\s+/g,' ').trim()}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function renameTextNode(n){let s=n.nodeValue;if(!s)return;let r=s.replace(/Temporary Transfer Store/g,'Staging Transfer Store').replace(/temporary transfer store/g,'staging transfer store').replace(/PMP_CONTINUOUS_RUN_BANK_TEMPORARY_TRANSFER_STORE/g,'PMP_CONTINUOUS_RUN_BANK_STAGING_TRANSFER_STORE').replace(/PMP_TEMPORARY_TRANSFER_STORE/g,'PMP_STAGING_TRANSFER_STORE');if(r!==s)n.nodeValue=r}
function renameDeep(el){try{let w=el.ownerDocument.createTreeWalker(el,NodeFilter.SHOW_TEXT);let a=[];while(w.nextNode())a.push(w.currentNode);a.forEach(renameTextNode)}catch(e){}}
function setUniversalSelect(sel){if(!sel)return;let cur=sel.value||'source_bundle',html=UNIVERSAL_OPTIONS.map(([v,l])=>'<option value="'+esc(v)+'">'+esc(l)+'</option>').join('');if(sel.innerHTML!==html)sel.innerHTML=html;if(UNIVERSAL_OPTIONS.some(x=>x[0]===cur))sel.value=cur;sel.dataset.stagingUniversal='1'}
function deleteDebugButtons(bank){Array.from(bank.querySelectorAll('button,a')).forEach(b=>{let t=txt(b.textContent);if(DELETE_BUTTONS.has(t))b.remove()})}
function patchTransferBox(d){let box=d.querySelector('[data-temp-transfer-store]')||d.querySelector('[data-staging-transfer-store]');if(!box)return null;box.setAttribute('data-staging-transfer-store','');renameDeep(box);let heads=Array.from(box.querySelectorAll('h1,h2,h3,p,strong,div')).filter(x=>txt(x.textContent).includes('Engine runs only after short slots and App Packets source ZIP are verified.'));heads.forEach(x=>{x.textContent='Engine runs only after the selected source set, identity profile, rules, and current work item are verified.'});Array.from(box.querySelectorAll('select')).forEach(setUniversalSelect);if(!box.querySelector('[data-staging-universal-note]')){let note=d.createElement('div');note.setAttribute('data-staging-universal-note','');note.style.cssText='margin:14px 0;padding:12px;border:3px solid #cfcfcf;border-radius:18px;background:#fff;font-weight:800;line-height:1.25';note.textContent='Universal staging vault: ZIP Import fills this store, the Source Identity Profile says what this run is, the Project Registry names/organizes the project, and Work Intake receives only the current work item.';let firstForm=box.querySelector('label,select,input,textarea,button');if(firstForm&&firstForm.parentNode)firstForm.parentNode.insertBefore(note,firstForm);else box.insertBefore(note,box.firstChild)}return box}
function ensureZipHost(d,bank){let host=bank.querySelector('[data-lossless-zip-import-host]');if(!host){host=d.createElement('div');host.setAttribute('data-lossless-zip-import-host','');host.style.cssText='margin:10px 0;padding:10px;border-radius:14px;border:3px solid rgba(0,0,0,.22);background:rgba(255,255,255,.72)';}return host}
function reorderBank(d,bank,stage){let registry=bank.querySelector('[data-bank-project-registry-v1]'),zip=bank.querySelector('[data-zip-importer]');if(!registry&&!stage&&!zip)return;if(zip){let host=ensureZipHost(d,bank);if(zip.parentElement!==host){host.innerHTML='';host.appendChild(zip)}if(registry&&host.nextElementSibling!==registry)registry.parentNode.insertBefore(host,registry);else if(stage&&host.nextElementSibling!==stage)stage.parentNode.insertBefore(host,stage);else if(!host.parentNode){let anchor=bank.querySelector('h1')||bank.firstElementChild;anchor&&anchor.parentNode?anchor.parentNode.insertBefore(host,anchor.nextSibling):bank.insertBefore(host,bank.firstChild)}}if(registry&&stage&&registry.nextElementSibling!==stage){registry.parentNode.insertBefore(stage,registry.nextSibling)}if(zip&&registry&&zip.closest('[data-staging-transfer-store]')){let host=ensureZipHost(d,bank);host.appendChild(zip);registry.parentNode.insertBefore(host,registry)}}
function patchDoc(d){let bank=d.getElementById('bank');if(!bank)return;deleteDebugButtons(bank);renameDeep(bank);let stage=patchTransferBox(d);reorderBank(d,bank,stage)}
function scan(){docs(document).forEach(d=>{try{patchDoc(d)}catch(e){}})}
window.PMPStagingTransferStoreUniversalUIV1={version:V,scan,options:UNIVERSAL_OPTIONS.map(x=>({type:x[0],label:x[1]}))};
window.addEventListener('load',()=>[50,150,400,900,1800,3000,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);
scan();
})();
