(()=>{
'use strict';
const VERSION='1.0.0-pass11-safety-no-deletion-20260727A';
const TYPE='PMP_SAFETY_NO_DELETION_GUARD_V1';
const POLICY='PMP_SAFETY_NO_DELETION_POLICY_V1';
const BANK_OWNER='bank_screen_owner';
const RECEIPT='PMP_SAFETY_OPERATION_RECEIPT_V1';
const DELETE_AUTHORITY='PMP_EXACT_DELETE_EXCEPTION_AUTHORITY_V1';
const consumedDeleteAuthorities=new Set();
const consumedArchiveOperations=new Set();
const operationReceipts=[];
let previousReceipt='0'.repeat(64);
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
function now(){return new Date().toISOString()}
function deny(code,action,input){return{ok:false,decision:'DENY',code,action:String(action||''),operation_id:String(input&&input.operation_id||''),effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}}}
function validOperationId(value){return/^op:p11:[A-Za-z0-9:._-]+$/.test(String(value||''))}
function validHash(value){return/^[0-9a-f]{64}$/.test(String(value||''))}
function receipt(action,input,code){
  let body={receipt_version:RECEIPT,operation_id:String(input.operation_id),action:String(action),requester_owner:String(input.requester_owner),target_owner:String(input.target_owner),resource:String(input.resource),record_id:String(input.record_id||''),decision:'ALLOW',code:String(code),payload_sha256:String(input.expected_payload_sha256||input.payload_sha256||''),previous_receipt_sha256:previousReceipt,at:now()};
  body.receipt_sha256=sha256(canonical(body));previousReceipt=body.receipt_sha256;operationReceipts.push(body);if(operationReceipts.length>256)operationReceipts.shift();return clone(body)
}
function authorizeArchive(input){
  input=input||{};let bank=String(input.owning_bank||'');
  if(input.action!=='ARCHIVE')return deny('DENIED_ACTION','ARCHIVE',input);
  if(!validOperationId(input.operation_id))return deny('DENIED_OPERATION_ID','ARCHIVE',input);
  if(input.requester_owner!==BANK_OWNER||input.target_owner!==BANK_OWNER)return deny('DENIED_OWNER','ARCHIVE',input);
  if(!/^bank:[A-Za-z0-9:._-]+$/.test(String(input.resource||'')))return deny('DENIED_RESOURCE','ARCHIVE',input);
  if(!String(input.record_id||''))return deny('DENIED_RECORD_ID','ARCHIVE',input);
  if(!validHash(input.expected_payload_sha256))return deny('DENIED_PAYLOAD_HASH','ARCHIVE',input);
  if(!Number.isInteger(input.payload_bytes)||input.payload_bytes<0)return deny('DENIED_PAYLOAD_BYTES','ARCHIVE',input);
  if(input.preservation!=='PRESERVE_EXACT_PAYLOAD_RECOVERABLE')return deny('DENIED_PRESERVATION','ARCHIVE',input);
  if(input.user_confirmed!==true)return deny('DENIED_USER_CONFIRMATION','ARCHIVE',input);
  if(input.capability!=='manual:'+BANK_OWNER+':archive_record:'+bank)return deny('DENIED_CAPABILITY','ARCHIVE',input);
  if(consumedArchiveOperations.has(input.operation_id))return deny('DENIED_ARCHIVE_OPERATION_REPLAY','ARCHIVE',input);
  consumedArchiveOperations.add(input.operation_id);
  let r=receipt('ARCHIVE',input,'ARCHIVE_AUTHORIZED_EXACT_PAYLOAD_PRESERVED');
  return{ok:true,decision:'ALLOW',code:'ARCHIVE_AUTHORIZED_EXACT_PAYLOAD_PRESERVED',receipt:r,effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}}
}
function authorityBody(authority){
  let body=clone(authority||{});delete body.receipt_sha256;return body
}
function authorizeDeleteException(input){
  input=input||{};let a=input.authority_receipt||{};
  if(input.action!=='DELETE_EXCEPTION')return deny('DELETE_DENIED_BY_DEFAULT','DELETE_EXCEPTION',input);
  if(!validOperationId(input.operation_id))return deny('DENIED_OPERATION_ID','DELETE_EXCEPTION',input);
  if(a.type!==DELETE_AUTHORITY||a.version!=='1.0.0')return deny('DENIED_EXACT_AUTHORITY_TYPE','DELETE_EXCEPTION',input);
  if(a.decision!=='ALLOW_DELETE_EXCEPTION'||a.single_use!==true||a.wildcards_allowed!==false)return deny('DENIED_EXACT_AUTHORITY_DECISION','DELETE_EXCEPTION',input);
  if(a.operation_id!==input.operation_id||a.requester_owner!==input.requester_owner||a.target_owner!==input.target_owner)return deny('DENIED_EXACT_AUTHORITY_OWNER','DELETE_EXCEPTION',input);
  if(a.record_id!==input.record_id||a.expected_payload_sha256!==input.expected_payload_sha256)return deny('DENIED_EXACT_AUTHORITY_RESOURCE','DELETE_EXCEPTION',input);
  if(!validHash(a.expected_payload_sha256)||!validHash(a.receipt_sha256))return deny('DENIED_EXACT_AUTHORITY_HASH','DELETE_EXCEPTION',input);
  if(a.user_confirmation_phrase!=='DELETE '+input.record_id||input.user_confirmation_phrase!==a.user_confirmation_phrase)return deny('DENIED_EXACT_USER_CONFIRMATION','DELETE_EXCEPTION',input);
  if(!Number.isFinite(Date.parse(a.issued_at))||!Number.isFinite(Date.parse(a.expires_at))||Date.parse(a.expires_at)<=Date.parse(a.issued_at)||Date.now()>Date.parse(a.expires_at))return deny('DENIED_EXACT_AUTHORITY_TIME','DELETE_EXCEPTION',input);
  if(sha256(canonical(authorityBody(a)))!==a.receipt_sha256)return deny('DENIED_EXACT_AUTHORITY_INTEGRITY','DELETE_EXCEPTION',input);
  if(consumedDeleteAuthorities.has(a.receipt_sha256))return deny('DENIED_EXACT_AUTHORITY_REPLAY','DELETE_EXCEPTION',input);
  consumedDeleteAuthorities.add(a.receipt_sha256);
  let r=receipt('DELETE_EXCEPTION',input,'DELETE_EXCEPTION_AUTHORIZED_ONCE');
  return{ok:true,decision:'ALLOW',code:'DELETE_EXCEPTION_AUTHORIZED_ONCE',receipt:r,effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false,authority_consumed:true}}
}
function planTransaction(input){
  input=input||{};
  if(!['TRANSACTIONAL_WRITE','ARCHIVE','QUARANTINE','ROLLBACK'].includes(input.action))return deny('DENIED_TRANSACTION_ACTION',input.action,input);
  if(!validOperationId(input.operation_id))return deny('DENIED_OPERATION_ID',input.action,input);
  if(!String(input.requester_owner||'')||input.requester_owner!==input.target_owner)return deny('DENIED_OWNER_SCOPE',input.action,input);
  if(!String(input.resource||''))return deny('DENIED_RESOURCE',input.action,input);
  if(!Number.isInteger(input.expected_version)||input.expected_version<0)return deny('DENIED_EXPECTED_VERSION',input.action,input);
  if(!validHash(input.payload_sha256)||!validHash(input.rollback_sha256))return deny('DENIED_TRANSACTION_HASH',input.action,input);
  if(!String(input.backup_ref||'').startsWith('backup:p11:'))return deny('DENIED_BACKUP_REF',input.action,input);
  if(input.append_only_receipt!==true)return deny('DENIED_APPEND_ONLY_RECEIPT',input.action,input);
  return{ok:true,decision:'ALLOW',code:'TRANSACTION_PLAN_AUTHORIZED',operation_id:input.operation_id,phases:['PREFLIGHT','EXACT_BACKUP','EXPECTED_VERSION_CHECK','BOUNDED_APPLY','VERIFY','APPEND_ONLY_RECEIPT','ROLLBACK_ON_ANY_FAILURE'],automatic_retry:false,storage_deletes_allowed:0,unrelated_bytes_policy:'PRESERVE_EXACTLY',receipt:receipt(input.action,input,'TRANSACTION_PLAN_AUTHORIZED'),effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}}
}
function snapshot(){
  return{type:TYPE,version:VERSION,policy_type:POLICY,status:'READY',owner:'safety_policy_owner',default_delete:'DENY',archive_policy:'PRESERVE_EXACT_PAYLOAD_RECOVERABLE',quarantine_policy:'PRESERVE_EXACT_BYTES',production_migration:'INACTIVE_GATE',archive_operations_consumed:consumedArchiveOperations.size,delete_exception:{authority_type:DELETE_AUTHORITY,single_use:true,wildcards_allowed:false,automatic_retry:false,consumed_count:consumedDeleteAuthorities.size},transaction_phases:['PREFLIGHT','EXACT_BACKUP','EXPECTED_VERSION_CHECK','BOUNDED_APPLY','VERIFY','APPEND_ONLY_RECEIPT','ROLLBACK_ON_ANY_FAILURE'],receipt_count:operationReceipts.length,receipt_head:previousReceipt,recent_receipts:clone(operationReceipts.slice(-32)),load_effects:{storage_reads:0,storage_writes:0,storage_deletes:0,persisted_user_data_changed:false}}
}
const api=Object.freeze({type:TYPE,version:VERSION,policy_type:POLICY,receipt_type:RECEIPT,delete_authority_type:DELETE_AUTHORITY,sha256,canonical,authorizeArchive,authorizeDeleteException,planTransaction,snapshot,rule:'Delete denies by default. Archive and quarantine preserve exact recoverable payloads. Transactions require exact backup, rollback, expected version, owner scope, and append-only receipt. Exceptional deletion requires one exact single-use receipt and cannot retry.'});
window.PMPSafetyNoDeletionGuardV1=api;
try{window.dispatchEvent(new CustomEvent('pmp:safety-no-deletion-guard-ready',{detail:{version:VERSION}}))}catch(e){}
})();
