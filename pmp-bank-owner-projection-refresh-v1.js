(()=>{
'use strict';
const VERSION='1.0.0-pass10-unit4-owner-refresh-20260726A';
const RECEIPT_VERSION='PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1';
const OWNER='bank_screen_owner';
const processed=new Set(),lastVersions=Object.create(null);
const stats={accepted_owner_events:0,denied_owner_events:0,duplicate_owner_events:0,stale_owner_events:0,projection_refreshes:0,last_decision:'NONE',last_code:'NONE',last_receipt_sha256:null,last_resource:null,last_version:0};
function B(){return window.PMPBankContinuousRunOwnerBoundaryV1||null}
function P(){return window.PMPBankInventoryReadonlyProjectionV1||null}
function clone(v){try{return JSON.parse(JSON.stringify(v))}catch(e){return v}}
function clean(v){return String(v==null?'':v).trim()}
function diagnostic(){return clone(Object.assign({type:'PMP_BANK_OWNER_PROJECTION_REFRESH_DIAGNOSTIC_V1',version:VERSION,owner:OWNER,attempt_limit:1,helper_registration_conveys_authority:false,active_tab_conveys_authority:false,direct_ui_event_conveys_authority:false,write_api_exposed:false,delete_api_exposed:false,migration_api_exposed:false},stats))}
function denied(code,kind){
  stats.denied_owner_events++;
  if(kind==='DUPLICATE')stats.duplicate_owner_events++;
  if(kind==='STALE')stats.stale_owner_events++;
  stats.last_decision='DENY';stats.last_code=code;
  return false
}
function receiptHashValid(boundary,receipt){
  if(!boundary||typeof boundary.sha256!=='function'||typeof boundary.canonical!=='function')return false;
  let body=clone(receipt),claimed=clean(body&&body.receipt_sha256);if(!/^[0-9a-f]{64}$/.test(claimed))return false;
  delete body.receipt_sha256;
  return boundary.sha256(boundary.canonical(body))===claimed
}
function recentReceiptValid(boundary,receipt){
  if(!boundary||typeof boundary.snapshot!=='function')return false;
  let snap=boundary.snapshot(),rows=snap&&Array.isArray(snap.recent_receipts)?snap.recent_receipts:[];
  return rows.some(row=>row&&row.receipt_sha256===receipt.receipt_sha256&&row.request_sha256===receipt.request_sha256&&row.operation_id===receipt.operation_id&&row.resource===receipt.resource&&row.resource_version_after===receipt.resource_version_after)
}
function onOwnerCommit(event){
  let detail=event&&event.detail,boundary=B(),projection=P();
  if(!detail||typeof detail!=='object'||!boundary||!projection||typeof projection.snapshot!=='function')return denied('DENIED_DEPENDENCY_OR_DETAIL');
  let resource=clean(detail.resource),version=Number(detail.version),receipt=detail.receipt;
  if(!resource.startsWith('bank:')||!Number.isInteger(version)||version<1||!receipt||typeof receipt!=='object')return denied('DENIED_MALFORMED_OWNER_EVENT');
  let hash=clean(receipt.receipt_sha256);
  if(receipt.receipt_version!==RECEIPT_VERSION||receipt.requester_owner!==OWNER||receipt.target_owner!==OWNER||receipt.decision!=='ALLOW'||receipt.code!=='COMMITTED')return denied('DENIED_WRONG_OWNER_OR_DECISION');
  if(processed.has(hash))return denied('DENIED_DUPLICATE_OWNER_RECEIPT','DUPLICATE');
  if(receipt.resource!==resource||receipt.resource_version_after!==version||receipt.resource_version_before!==version-1)return denied('DENIED_RECEIPT_EVENT_BINDING');
  if(typeof boundary.resourceVersion!=='function'||boundary.resourceVersion(resource)!==version)return denied('DENIED_STALE_BOUNDARY_VERSION','STALE');
  let prior=Number(lastVersions[resource]||0);
  if(version<=prior)return denied('DENIED_STALE_OWNER_EVENT','STALE');
  if(prior&&version!==prior+1)return denied('DENIED_NONSEQUENTIAL_OWNER_EVENT','STALE');
  if(!receiptHashValid(boundary,receipt)||!recentReceiptValid(boundary,receipt))return denied('DENIED_UNVERIFIED_OWNER_RECEIPT');
  processed.add(hash);if(processed.size>256)processed.delete(processed.values().next().value);
  lastVersions[resource]=version;
  let snapshot=projection.snapshot('accepted_bank_owner_commit:'+hash);
  stats.accepted_owner_events++;stats.projection_refreshes++;stats.last_decision='ALLOW';stats.last_code='REFRESHED_EXACTLY_ONCE';stats.last_receipt_sha256=hash;stats.last_resource=resource;stats.last_version=version;
  try{window.dispatchEvent(new CustomEvent('pmp:bank-inventory-projection-refreshed',{detail:{type:'PMP_BANK_INVENTORY_PROJECTION_REFRESHED_V1',source_version:VERSION,owner:OWNER,resource,version,receipt_sha256:hash,projection_status:snapshot&&snapshot.status||'UNKNOWN',projection_item_count:snapshot&&snapshot.summary&&snapshot.summary.items||0,raw_payload_exposed:false}}))}catch(e){}
  return true
}
const api=Object.freeze({version:VERSION,owner:OWNER,diagnostic,rule:'Only an exact accepted Bank-owner receipt present in the owner boundary may refresh the read-only projection once. Wrong-owner, duplicate, stale, malformed, Helper, active-tab, and direct UI events fail closed; no mutation API is exposed.'});
window.PMPBankOwnerProjectionRefreshV1=api;
window.addEventListener('pmp:bank-owner-write-committed',onOwnerCommit);
try{window.dispatchEvent(new CustomEvent('pmp:bank-owner-projection-refresh-ready',{detail:{version:VERSION,owner:OWNER}}))}catch(e){}
})();
