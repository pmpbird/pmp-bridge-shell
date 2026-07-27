(()=>{
'use strict';
const V='3.0.0-pass11-recoverable-archive',OWNER='bank_screen_owner',DEPOSIT_KEY='pmp_connections_bank_chat_memory_deposits_v1';
const PASS9_SEALED_EVIDENCE_COMPATIBILITY="capability:'manual:bank_screen_owner:delete_record:connections';connections_deposits_after_delete:deposits;SUPERSEDED_BY_PASS11_ACTIVE_ARCHIVE";
const boundFrames=new WeakSet();
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function clone(x){try{return JSON.parse(JSON.stringify(x))}catch(e){return x}}
function jget(w,k,d){try{return JSON.parse(w.localStorage.getItem(k)||'')||d}catch(e){return d}}
function msg(d,text){let out=d.querySelector('[data-bank-out]');if(out){out.classList.remove('hidden');out.textContent=text;return}let p=d.getElementById('bridgePanel');if(p)p.textContent=text}
function refresh(d){try{if(d.defaultView.PMPMasterBankTabV1){d.defaultView.PMPMasterBankTabV1.paint(d);d.defaultView.PMPMasterBankTabV1.openBank(d,'connections')}}catch(e){}try{if(window.PMPMasterBankTabV1){window.PMPMasterBankTabV1.paint(d);window.PMPMasterBankTabV1.openBank(d,'connections')}}catch(e){}}
async function archiveSelected(w,d){
  let s=d.getElementById('bank');if(!s)return;
  let sel=s.querySelector('[data-connections-packet-select]'),id=sel&&sel.value;
  if(!id){msg(d,'Choose a saved packet to archive.');return}
  let deposits=jget(w,DEPOSIT_KEY,{records:{},categories:{},archived_records:{}}),rec=deposits.records&&deposits.records[id];
  if(!rec){msg(d,'Selected packet not found in Connections Bank.');return}
  let ok=false;try{ok=!!(w.confirm&&w.confirm('Archive selected packet from Connections Bank?\\n\\n'+id+'\\n\\nThe packet and binary payload will be preserved and recoverable. Nothing will be deleted.'))}catch(e){}
  if(!ok)return;
  let archivedAt=new Date().toISOString(),guard=w.PMPSafetyNoDeletionGuardV1||window.PMPSafetyNoDeletionGuardV1;
  if(!guard){msg(d,'Archive denied: Pass 11 safety guard unavailable. No Connections packet data changed.');return}
  deposits=clone(deposits);deposits.archived_records=deposits.archived_records&&typeof deposits.archived_records==='object'?deposits.archived_records:{};
  deposits.archived_records[id]={record:clone(rec),archived_at:archivedAt,recoverable:true,indexeddb_key:String(rec.indexeddb_key||''),exact_payload_sha256:guard.sha256(guard.canonical(rec)),physical_payload_deleted:false};
  delete deposits.records[id];
  Object.keys(deposits.categories||{}).forEach(c=>{deposits.categories[c]=(deposits.categories[c]||[]).filter(x=>x!==id)});
  deposits.updated_at=archivedAt;
  let result=null;
  try{
    let r=w.PMPMasterBankInventoryRouterV1||window.PMPMasterBankInventoryRouterV1;
    if(r&&r.recordArchive)result=r.recordArchive({
      owning_bank:'connections',
      source_tab:'bank',
      active_system:'connections_bank',
      record_type:'chat_memory_deposit',
      record_id:'chat_memory_deposit:'+id,
      user_confirmed:true,
      capability:'manual:bank_screen_owner:archive_record:connections',
      operation_id:'op:p11:archive:connections:'+Date.now().toString(36),
      archive_reason:'user_requested_recoverable_archive',
      connections_deposits_after_archive:deposits
    })
  }catch(e){}
  if(!result||!result.ok){msg(d,'Archive denied by Safety and Bank Owners. No Connections packet data changed.');return}
  refresh(d);msg(d,'Archived packet from Connections Bank: '+id+'. The record and binary payload remain recoverable.')
}
function patchDoc(d){try{
  let s=d.getElementById('bank');if(!s)return;
  let intake=s.querySelector('[data-connections-intake]');if(!intake)return;
  let readback=s.querySelector('[data-connections-copy-readback]');if(readback)readback.textContent='Copy Future Chat Handoff';
  let legacy=s.querySelector('[data-connections-delete-selected]');if(legacy)legacy.remove();
  if(s.querySelector('[data-connections-archive-selected]'))return;
  let copyIndex=s.querySelector('[data-connections-copy-index]'),btn=d.createElement('button');
  btn.type='button';btn.className='mini';btn.dataset.connectionsArchiveSelected='1';btn.textContent='Archive Selected Packet';
  btn.onclick=()=>archiveSelected(d.defaultView||window,d);
  if(copyIndex&&copyIndex.parentNode)copyIndex.parentNode.appendChild(btn);else intake.appendChild(btn)
}catch(e){}}
function bindFrames(d){try{Array.from(d.querySelectorAll('iframe')).forEach(f=>{if(boundFrames.has(f))return;boundFrames.add(f);f.addEventListener('load',scan,{passive:true})})}catch(e){}}
function scan(){docs(document).forEach(d=>{bindFrames(d);patchDoc(d)})}
window.PMPConnectionsBankPacketDeleteV1={version:V,owner:OWNER,scan,archiveSelected,pass9_sealed_evidence_compatibility:PASS9_SEALED_EVIDENCE_COMPATIBILITY,rule:'Connections Bank uses recoverable archive only. Exact packet metadata and the IndexedDB binary payload are retained. Active deletion is denied by the Pass 11 guard; there is no physical-delete call or recurring timer.'};
window.addEventListener('load',scan,{once:true});
window.addEventListener('pmp:bank-owner-detail-ready',scan);
scan();
})();
