(()=>{
'use strict';
const VERSION='1.0.0-pass9-unit3-owner-boundary-20260726A';
const CONTRACT='PMP_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_V1';
const RECEIPT='PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1';
const BANK_OWNER='bank_screen_owner';
const RUN_OWNER='continuous_run_level_owner';
const BANK_KEYS=new Set(['pmp_master_bank_inventory_v1','pmp_source_bank_router_receipts_v1','pmp_helper_bank_index_v1','pmp_connections_bank_chat_memory_deposits_v1']);
const RUN_KEYS=new Set(['pmp_continuous_run_state_bank_v1','pmp_continuous_run_state_receipts_v1','pmp_continuous_run_state_manifest_v1','pmp_bank_project_registry_v1','pmp_bank_project_registry_v1_receipt']);
const REQUEST_FIELDS=['contract_version','operation_id','request_id','requester_owner','target_owner','action','resource','expected_version','payload_sha256','issued_at','expires_at','cancellation_epoch','capability'];
const versions=Object.create(null),cancellationEpochs=Object.create(null),operations=new Map(),receipts=[];
let previousReceipt='0'.repeat(64),sequence=0;
function rightRotate(v,n){return(v>>>n)|(v<<(32-n))}
function sha256(value){
  let s=unescape(encodeURIComponent(String(value==null?'':value))),maxWord=Math.pow(2,32),words=[],asciiBitLength=s.length*8;
  let hash=sha256.h=sha256.h||[],k=sha256.k=sha256.k||[],primeCounter=k.length,isComposite={};
  for(let candidate=2;primeCounter<64;candidate++){if(!isComposite[candidate]){for(let i=0;i<313;i+=candidate)isComposite[i]=candidate;hash[primeCounter]=(Math.pow(candidate,.5)*maxWord)|0;k[primeCounter++]=(Math.pow(candidate,1/3)*maxWord)|0}}
  s+='\x80';while(s.length%64-56)s+='\x00';
  for(let i=0;i<s.length;i++){let j=s.charCodeAt(i);if(j>>8)return'';words[i>>2]|=j<<((3-i)%4)*8}
  words[words.length]=(asciiBitLength/maxWord)|0;words[words.length]=asciiBitLength;
  for(let j=0;j<words.length;){let w=words.slice(j,j+=16),oldHash=hash.slice(0);hash=hash.slice(0,8);
    for(let i=0;i<64;i++){let w15=w[i-15],w2=w[i-2],a=hash[0],e=hash[4];
      let temp1=hash[7]+(rightRotate(e,6)^rightRotate(e,11)^rightRotate(e,25))+((e&hash[5])^((~e)&hash[6]))+k[i]+(w[i]=(i<16)?w[i]:((w[i-16]+(rightRotate(w15,7)^rightRotate(w15,18)^(w15>>>3))+w[i-7]+(rightRotate(w2,17)^rightRotate(w2,19)^(w2>>>10)))|0));
      let temp2=(rightRotate(a,2)^rightRotate(a,13)^rightRotate(a,22))+((a&hash[1])^(a&hash[2])^(hash[1]&hash[2]));
      hash=[(temp1+temp2)|0].concat(hash);hash[4]=(hash[4]+temp1)|0;hash.pop()}
    for(let i=0;i<8;i++)hash[i]=(hash[i]+oldHash[i])|0}
  let out='';for(let i=0;i<8;i++)for(let j=3;j+1;j--){let b=(hash[i]>>(j*8))&255;out+=(b<16?'0':'')+b.toString(16)}return out
}
function canonical(v){if(Array.isArray(v))return'['+v.map(canonical).join(',')+']';if(v&&typeof v==='object')return'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';return JSON.stringify(v)}
function clone(v){try{return JSON.parse(JSON.stringify(v))}catch(e){return v}}
function storage(){try{return window.localStorage}catch(e){return null}}
function readRaw(key){try{let s=storage();return s?s.getItem(String(key)):null}catch(e){return null}}
function readJSON(key,fallback){let raw=readRaw(key);if(raw==null)return clone(fallback);try{return JSON.parse(raw)}catch(e){return clone(fallback)}}
function now(){return new Date().toISOString()}
function id(prefix){sequence++;return prefix+Date.now().toString(36)+':'+sequence.toString(36)}
function resourceVersion(resource){return Number(versions[String(resource)]||0)}
function requestFor(input){
  input=input||{};let issued=input.issued_at||now(),resource=String(input.resource||''),owner=String(input.requester_owner||'');
  let target=BANK_OWNER,action=String(input.action||'COMMIT_WRITE');
  return{contract_version:CONTRACT,operation_id:String(input.operation_id||id('op:p9u3:')),request_id:String(input.request_id||id('req:p9u3:')),requester_owner:owner,target_owner:target,action,resource,expected_version:Number(input.expected_version==null?resourceVersion(resource):input.expected_version),payload_sha256:String(input.payload_sha256||''),issued_at:issued,expires_at:String(input.expires_at||new Date(Date.parse(issued)+300000).toISOString()),cancellation_epoch:Number(input.cancellation_epoch||0),capability:String(input.capability||((owner===BANK_OWNER?'internal:':'request:')+BANK_OWNER+':'+action+':'+resource))}
}
function deny(code,request){return{ok:false,decision:'DENY',code,request:clone(request),effects:{storage_writes:0,storage_deletes:0,persisted_user_data_changed:false}}}
function authorize(request){
  if(!request||typeof request!=='object'||!REQUEST_FIELDS.every(k=>Object.prototype.hasOwnProperty.call(request,k)))return deny('DENIED_MALFORMED',request);
  if(request.contract_version!==CONTRACT)return deny('DENIED_CONTRACT_VERSION',request);
  if(!/^op:[A-Za-z0-9:._-]+$/.test(request.operation_id))return deny('DENIED_OPERATION_ID',request);
  if(!/^req:[A-Za-z0-9:._-]+$/.test(request.request_id))return deny('DENIED_REQUEST_ID',request);
  if(![BANK_OWNER,RUN_OWNER].includes(request.requester_owner)||request.target_owner!==BANK_OWNER)return deny('DENIED_OWNER',request);
  if(request.action!=='COMMIT_WRITE')return deny('DENIED_ACTION',request);
  if(!String(request.resource).startsWith('bank:'))return deny('DENIED_RESOURCE',request);
  if(!Number.isInteger(request.expected_version)||request.expected_version!==resourceVersion(request.resource))return deny('DENIED_EXPECTED_VERSION',request);
  if(!/^[0-9a-f]{64}$/.test(request.payload_sha256))return deny('DENIED_PAYLOAD_HASH',request);
  if(!Number.isFinite(Date.parse(request.issued_at))||!Number.isFinite(Date.parse(request.expires_at))||Date.parse(request.expires_at)<=Date.parse(request.issued_at))return deny('DENIED_TIME',request);
  if(Date.now()>Date.parse(request.expires_at))return deny('DENIED_EXPIRED',request);
  let exact=request.requester_owner===BANK_OWNER?'internal:'+BANK_OWNER+':COMMIT_WRITE:'+request.resource:'request:'+BANK_OWNER+':COMMIT_WRITE:'+request.resource;
  if(request.capability!==exact)return deny('DENIED_CAPABILITY',request);
  let currentEpoch=Number(cancellationEpochs[request.resource]||0);
  if(!Number.isInteger(request.cancellation_epoch)||request.cancellation_epoch<currentEpoch)return deny('DENIED_STALE_CANCELLATION',request);
  if(request.cancellation_epoch>currentEpoch+1)return deny('DENIED_CANCELLATION_ADVANCE',request);
  return{ok:true,decision:'ALLOW',code:'AUTHORIZED_COMMIT'}
}
function makeReceipt(request,decision,code,before,after,requestHash){
  let body={receipt_version:RECEIPT,operation_id:request.operation_id,request_id:request.request_id,requester_owner:request.requester_owner,target_owner:request.target_owner,action:request.action,resource:request.resource,decision,code,resource_version_before:before,resource_version_after:after,cancellation_epoch:request.cancellation_epoch,request_sha256:requestHash,previous_receipt_sha256:previousReceipt};
  body.receipt_sha256=sha256(canonical(body));previousReceipt=body.receipt_sha256;receipts.push(body);if(receipts.length>256)receipts.shift();return body
}
function keysAllowed(owner,writes){
  if(!Array.isArray(writes)||!writes.length)return false;
  return writes.every(row=>row&&typeof row.key==='string'&&Object.prototype.hasOwnProperty.call(row,'value')&&(owner===BANK_OWNER?BANK_KEYS.has(row.key):(RUN_KEYS.has(row.key))));
}
function commitBundle(input){
  input=input||{};let writes=clone(input.writes||[]),owner=String(input.requester_owner||''),resource=String(input.resource||'');
  let payloadHash=sha256(canonical(writes)),request=requestFor(Object.assign({},input,{requester_owner:owner,resource,payload_sha256:input.payload_sha256||payloadHash}));
  let requestHash=sha256(canonical(request)),prior=operations.get(request.operation_id);
  if(prior){if(prior.request_sha256===requestHash)return clone(prior.result);return deny('DENIED_DUPLICATE_CONFLICT',request)}
  let auth=authorize(request);if(!auth.ok){operations.set(request.operation_id,{request_sha256:requestHash,result:auth});return auth}
  if(request.payload_sha256!==payloadHash){let d=deny('DENIED_PAYLOAD_BINDING',request);operations.set(request.operation_id,{request_sha256:requestHash,result:d});return d}
  if(!keysAllowed(owner,writes)){let d=deny('DENIED_STORAGE_SCOPE',request);operations.set(request.operation_id,{request_sha256:requestHash,result:d});return d}
  let s=storage();if(!s){let d=deny('DENIED_STORAGE_UNAVAILABLE',request);operations.set(request.operation_id,{request_sha256:requestHash,result:d});return d}
  let before=resourceVersion(resource),snapshots=writes.map(row=>({key:row.key,raw:readRaw(row.key)}));
  try{writes.forEach(row=>s.setItem(row.key,JSON.stringify(row.value,null,2)))}catch(error){try{snapshots.forEach(row=>row.raw==null?s.removeItem(row.key):s.setItem(row.key,row.raw))}catch(e){}let d=deny('DENIED_ATOMIC_WRITE_FAILED',request);operations.set(request.operation_id,{request_sha256:requestHash,result:d});return d}
  versions[resource]=before+1;cancellationEpochs[resource]=request.cancellation_epoch;let receipt=makeReceipt(request,'ALLOW','COMMITTED',before,before+1,requestHash);
  let result={ok:true,decision:'ALLOW',code:'COMMITTED',receipt,effects:{storage_writes:writes.length,storage_deletes:0,persisted_user_data_changed:true}};
  operations.set(request.operation_id,{request_sha256:requestHash,result:clone(result)});
  try{window.dispatchEvent(new CustomEvent('pmp:bank-owner-write-committed',{detail:{resource,version:before+1,receipt:clone(receipt)}}))}catch(e){}
  return result
}
function manualDeleteAuthority(input,bankKey){
  return !!(input&&input.user_confirmed===true&&input.capability==='manual:'+BANK_OWNER+':delete_record:'+bankKey)
}
function snapshot(){
  return{type:'PMP_BANK_CONTINUOUS_RUN_OWNER_BOUNDARY_SNAPSHOT_V1',version:VERSION,status:'READY',contract_version:CONTRACT,bank_owner:BANK_OWNER,continuous_run_owner:RUN_OWNER,request_fields:REQUEST_FIELDS.slice(),resource_versions:clone(versions),cancellation_epochs:clone(cancellationEpochs),receipt_count:receipts.length,receipt_head:previousReceipt,recent_receipts:receipts.slice(-32).map(r=>({receipt_version:r.receipt_version,operation_id:r.operation_id,request_id:r.request_id,requester_owner:r.requester_owner,target_owner:r.target_owner,action:r.action,resource:r.resource,decision:r.decision,code:r.code,resource_version_before:r.resource_version_before,resource_version_after:r.resource_version_after,cancellation_epoch:r.cancellation_epoch,request_sha256:r.request_sha256,previous_receipt_sha256:r.previous_receipt_sha256,receipt_sha256:r.receipt_sha256})),storage_keys:{bank:Array.from(BANK_KEYS),continuous_run:Array.from(RUN_KEYS)},load_effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false},rules:{active_tab_conveys_ownership:false,filename_conveys_authority:false,copied_cross_frame_api_conveys_authority:false,delete_or_clear_default:'DENY',storage_migration:'FORBIDDEN',receipt_integrity:'SHA-256_CHAINED',duplicate_policy:'IDENTICAL_REPLAY_OR_CONFLICT_DENY',cancellation_epoch:'MONOTONIC_NO_GAPS'}}
}
const api=Object.freeze({version:VERSION,contract_version:CONTRACT,receipt_version:RECEIPT,owners:Object.freeze({bank:BANK_OWNER,continuous_run:RUN_OWNER}),request_fields:Object.freeze(REQUEST_FIELDS.slice()),sha256,canonical,readRaw,readJSON,resourceVersion,requestFor,authorize,commitBundle,manualDeleteAuthority,snapshot,rule:'Bank Owner is the only durable writer. Continuous Run owns lifecycle and requests exact Bank commits. Load is read-only; clear/delete deny by default; no storage migration.'});
window.PMPBankContinuousRunOwnerBoundaryV1=api;
try{window.dispatchEvent(new CustomEvent('pmp:bank-continuous-run-owner-boundary-ready',{detail:{version:VERSION}}))}catch(e){}
})();
