#!/usr/bin/env node
'use strict';
const crypto=require('crypto');
const fs=require('fs');
const path=require('path');
const p8u2=require('./run_pass8_unit2_helper_capability_contract_v1.js');
const ROOT=path.resolve(__dirname,'..');
const RECORD='audit/pass8/pass8-helper-unit3-registration-events-v1.json';
const RESULT_TYPE='PMP_PASS8_UNIT3_HELPER_REGISTRATION_RESULT_V1';
const EVENT_VERSION='PMP_HELPER_REGISTRATION_EVENT_V1';
const JOURNAL_VERSION='PMP_HELPER_REGISTRATION_JOURNAL_V1';
const VERSION='1.0.0';
const ID=/^[a-z0-9][a-z0-9._:-]{0,191}$/;
const TIME=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const EVENT_TYPES=new Set([
  'HELPER_REGISTERED','HELPER_UPDATED','HELPER_REVOKED',
  'HELPER_REMOVED','HELPER_GROWTH_OBSERVED'
]);
const REQUIRED_FIELDS=[
  'event_version','event_id','operation_id','monotonic_sequence','registry_epoch',
  'event_type','helper_id','helper_source_sha256','canonical_owner_id','section_id',
  'slot','source_version','growth_source','observed_at','previous_event_digest',
  'authority'
];
const AUTHORITY_FIELDS=[
  'contract_version','authorizer','capability_id','decision','action','revocation_epoch'
];
function stable(value){
  if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
  if(value&&typeof value==='object'){
    return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
  }
  return JSON.stringify(value);
}
function digest(value){
  return crypto.createHash('sha256').update(Buffer.from(stable(value))).digest('hex');
}
function clone(value){return JSON.parse(JSON.stringify(value))}
function eventContract(){
  return JSON.parse(fs.readFileSync(path.join(ROOT,RECORD),'utf8')).registration_contract;
}
function helperRows(){
  return p8u2.inventory().declared;
}
function helper(helperId){return helperRows().find(row=>row.helper_id===helperId)}
function actionFor(type){
  return {
    HELPER_REGISTERED:'register_helper',
    HELPER_UPDATED:'update_helper',
    HELPER_REVOKED:'revoke_helper',
    HELPER_REMOVED:'remove_helper',
    HELPER_GROWTH_OBSERVED:'observe_helper_growth'
  }[type];
}
function authorityFor(helperId,type,overrides={}){
  const policy=p8u2.contract();
  const growth=type==='HELPER_GROWTH_OBSERVED';
  return Object.assign({
    contract_version:policy.contract_version,
    authorizer:growth?'diagnostics_owner':policy.root_grant_authority,
    capability_id:`cap:p8u2:${helperId}`,
    decision:growth?'OBSERVED_ONLY_NO_AUTHORITY':'AUTHORIZED_STATIC_EVENT',
    action:actionFor(type),
    revocation_epoch:0
  },clone(overrides));
}
function makeEvent(helperId,type,sequence,overrides={}){
  const row=helper(helperId);
  if(!row)throw new Error(`unknown helper ${helperId}`);
  return Object.assign({
    event_version:EVENT_VERSION,
    event_id:`evt:p8u3:${helperId}:${sequence}`,
    operation_id:`op:p8u3:${helperId}:${sequence}`,
    monotonic_sequence:sequence,
    registry_epoch:1,
    event_type:type,
    helper_id:helperId,
    helper_source_sha256:row.helper_source_sha256,
    canonical_owner_id:row.canonical_owner_id,
    section_id:row.section_id,
    slot:row.slot,
    source_version:'source:v1',
    growth_source:row.growth_source,
    observed_at:`2026-07-27T00:00:${String(sequence).padStart(2,'0')}Z`,
    previous_event_digest:null,
    authority:authorityFor(helperId,type)
  },clone(overrides));
}
function withPrevious(eventValue,prior){
  const out=clone(eventValue);
  out.previous_event_digest=prior?digest(prior):null;
  return out;
}
function deny(code,eventValue){
  return {
    accepted:false,mutated:false,authority_granted:false,code,
    event_id:eventValue&&eventValue.event_id||null,
    operation_id:eventValue&&eventValue.operation_id||null
  };
}
function accept(code,eventValue,mutated){
  return {
    accepted:true,mutated,authority_granted:false,code,
    event_id:eventValue.event_id,operation_id:eventValue.operation_id
  };
}
function shape(eventValue){
  if(!eventValue||typeof eventValue!=='object'||Array.isArray(eventValue))return 'REJECTED_MALFORMED_EVENT';
  if(stable(Object.keys(eventValue).sort())!==stable(REQUIRED_FIELDS.slice().sort()))return 'REJECTED_MALFORMED_EVENT';
  if(eventValue.event_version!==EVENT_VERSION)return 'REJECTED_EVENT_VERSION';
  for(const key of ['event_id','operation_id','helper_id','canonical_owner_id','section_id','slot','source_version']){
    if(!ID.test(String(eventValue[key]||'')))return 'REJECTED_IDENTITY';
  }
  if(!Number.isInteger(eventValue.monotonic_sequence)||eventValue.monotonic_sequence<1)return 'REJECTED_SEQUENCE';
  if(!Number.isInteger(eventValue.registry_epoch)||eventValue.registry_epoch<1)return 'REJECTED_EPOCH';
  if(!EVENT_TYPES.has(eventValue.event_type))return 'REJECTED_EVENT_TYPE';
  if(!/^[0-9a-f]{64}$/.test(String(eventValue.helper_source_sha256||'')))return 'REJECTED_SOURCE_HASH';
  if(!TIME.test(String(eventValue.observed_at||'')))return 'REJECTED_TIME';
  if(eventValue.previous_event_digest!==null&&!/^[0-9a-f]{64}$/.test(String(eventValue.previous_event_digest)))return 'REJECTED_PREVIOUS_DIGEST';
  const authority=eventValue.authority;
  if(!authority||typeof authority!=='object'||Array.isArray(authority))return 'REJECTED_AUTHORITY_SHAPE';
  if(stable(Object.keys(authority).sort())!==stable(AUTHORITY_FIELDS.slice().sort()))return 'REJECTED_AUTHORITY_SHAPE';
  return null;
}
function evaluate(events){
  const policy=eventContract();
  const capabilityPolicy=p8u2.contract();
  const helpers=new Map(helperRows().map(row=>[row.helper_id,row]));
  const registered=new Map();
  const pendingGrowth=new Map();
  const revoked=new Map();
  const eventDigests=new Map();
  const operationIds=new Set();
  const journal=[];
  const diagnostics=[];
  const outcomes=[];
  let last=null;
  for(const raw of events){
    const current=clone(raw);
    const invalid=shape(current);
    if(invalid){outcomes.push(deny(invalid,current));continue}
    const eventDigest=digest(current);
    if(eventDigests.has(current.event_id)){
      outcomes.push(eventDigests.get(current.event_id)===eventDigest
        ?accept('DUPLICATE_EVENT_IGNORED',current,false)
        :deny('REJECTED_DUPLICATE_EVENT_CONFLICT',current));
      continue;
    }
    if(operationIds.has(current.operation_id)){
      outcomes.push(deny('REJECTED_DUPLICATE_OPERATION',current));continue;
    }
    const row=helpers.get(current.helper_id);
    if(!row){outcomes.push(deny('REJECTED_UNKNOWN_HELPER',current));continue}
    if(row.disposition==='HELD_LEGACY'){
      outcomes.push(deny('REJECTED_LEGACY_HELPER_HELD',current));continue;
    }
    if(row.disposition!=='ELIGIBLE_STATIC_CAPABILITY'){
      outcomes.push(deny('REJECTED_HELPER_CONFLICT_HELD',current));continue;
    }
    if(current.helper_source_sha256!==row.helper_source_sha256){
      outcomes.push(deny('REJECTED_SOURCE_HASH',current));continue;
    }
    if(current.canonical_owner_id!==row.canonical_owner_id||current.section_id!==row.section_id){
      outcomes.push(deny('REJECTED_OWNER_BINDING',current));continue;
    }
    if(current.slot!==row.slot){
      outcomes.push(deny('REJECTED_SLOT_BINDING',current));continue;
    }
    if(current.growth_source!==row.growth_source){
      outcomes.push(deny('REJECTED_GROWTH_SOURCE',current));continue;
    }
    const growth=current.event_type==='HELPER_GROWTH_OBSERVED';
    const expectedAuthority=authorityFor(current.helper_id,current.event_type);
    if(!growth)expectedAuthority.revocation_epoch=current.authority.revocation_epoch;
    const priorRevocationEpoch=revoked.get(current.helper_id)||0;
    if(!growth&&current.event_type!=='HELPER_REVOKED'&&
      current.authority.revocation_epoch!==priorRevocationEpoch){
      outcomes.push(deny('REJECTED_REVOCATION_EPOCH',current));continue;
    }
    if(!growth&&(
      current.authority.contract_version!==capabilityPolicy.contract_version||
      current.authority.authorizer!==capabilityPolicy.root_grant_authority||
      current.authority.capability_id!==`cap:p8u2:${current.helper_id}`||
      current.authority.decision!=='AUTHORIZED_STATIC_EVENT'||
      current.authority.action!==actionFor(current.event_type)
    )){
      outcomes.push(deny('REJECTED_REGISTRATION_AUTHORITY',current));continue;
    }
    if(growth&&(
      row.growth_source==='none'||
      current.authority.contract_version!==capabilityPolicy.contract_version||
      current.authority.authorizer!=='diagnostics_owner'||
      current.authority.capability_id!==`cap:p8u2:${current.helper_id}`||
      current.authority.decision!=='OBSERVED_ONLY_NO_AUTHORITY'||
      current.authority.action!=='observe_helper_growth'||
      current.authority.revocation_epoch!==0
    )){
      outcomes.push(deny('REJECTED_GROWTH_OBSERVER_AUTHORITY',current));continue;
    }
    if(last===null){
      if(current.monotonic_sequence!==1||current.registry_epoch!==1||current.previous_event_digest!==null){
        outcomes.push(deny('REJECTED_JOURNAL_START',current));continue;
      }
    }else{
      if(current.monotonic_sequence<=last.monotonic_sequence){
        outcomes.push(deny('REJECTED_STALE_SEQUENCE',current));continue;
      }
      if(current.monotonic_sequence!==last.monotonic_sequence+1){
        outcomes.push(deny('REJECTED_SEQUENCE_GAP',current));continue;
      }
      if(current.registry_epoch<last.registry_epoch){
        outcomes.push(deny('REJECTED_STALE_EPOCH',current));continue;
      }
      if(current.registry_epoch>last.registry_epoch+1){
        outcomes.push(deny('REJECTED_EPOCH_GAP',current));continue;
      }
      if(current.previous_event_digest!==last.event_digest){
        outcomes.push(deny('REJECTED_EVENT_CHAIN',current));continue;
      }
      if(current.observed_at<last.observed_at){
        outcomes.push(deny('REJECTED_TIME_REGRESSION',current));continue;
      }
    }
    let code;
    if(current.event_type==='HELPER_REGISTERED'){
      if(registered.has(current.helper_id)){outcomes.push(deny('REJECTED_DUPLICATE_HELPER',current));continue}
      if(revoked.has(current.helper_id)){outcomes.push(deny('REJECTED_HELPER_REVOKED',current));continue}
      registered.set(current.helper_id,{
        helper_id:current.helper_id,helper_source_sha256:current.helper_source_sha256,
        canonical_owner_id:current.canonical_owner_id,section_id:current.section_id,
        slot:current.slot,source_version:current.source_version,
        growth_source:current.growth_source,registry_epoch:current.registry_epoch,
        status:'REGISTERED_STATIC_EVENT_ONLY'
      });
      code='HELPER_REGISTERED';
    }else if(current.event_type==='HELPER_UPDATED'){
      if(!registered.has(current.helper_id)){outcomes.push(deny('REJECTED_HELPER_NOT_REGISTERED',current));continue}
      registered.get(current.helper_id).source_version=current.source_version;
      registered.get(current.helper_id).registry_epoch=current.registry_epoch;
      code='HELPER_UPDATED';
    }else if(current.event_type==='HELPER_REVOKED'){
      if(!registered.has(current.helper_id)){outcomes.push(deny('REJECTED_HELPER_NOT_REGISTERED',current));continue}
      const nextEpoch=current.authority.revocation_epoch;
      if(!Number.isInteger(nextEpoch)||nextEpoch<=priorRevocationEpoch){
        outcomes.push(deny('REJECTED_STALE_REVOCATION',current));continue;
      }
      revoked.set(current.helper_id,nextEpoch);
      registered.get(current.helper_id).status='REVOKED_STATIC_EVENT_ONLY';
      code='HELPER_REVOKED';
    }else if(current.event_type==='HELPER_REMOVED'){
      if(!registered.has(current.helper_id)){outcomes.push(deny('REJECTED_HELPER_NOT_REGISTERED',current));continue}
      registered.delete(current.helper_id);
      code='HELPER_REMOVED';
    }else{
      pendingGrowth.set(current.helper_id,{
        helper_id:current.helper_id,canonical_owner_id:current.canonical_owner_id,
        section_id:current.section_id,slot:current.slot,
        growth_source:current.growth_source,status:'OBSERVED_PENDING_NO_AUTHORITY',
        authority_granted:false
      });
      code='HELPER_GROWTH_RECORDED_NO_AUTHORITY';
    }
    const normalized=clone(current);
    normalized.event_digest=eventDigest;
    last=normalized;
    journal.push(normalized);
    eventDigests.set(current.event_id,eventDigest);
    operationIds.add(current.operation_id);
    diagnostics.push({
      operation_id:current.operation_id,event_id:current.event_id,
      helper_id:current.helper_id,event_type:current.event_type,
      result:code,authority_granted:false
    });
    outcomes.push(accept(code,current,true));
  }
  const result={
    type:RESULT_TYPE,version:VERSION,status:'PASS',event_version:EVENT_VERSION,
    outcomes,
    snapshot:{
      registered:Array.from(registered.values()).sort((a,b)=>a.helper_id.localeCompare(b.helper_id)),
      pending_growth:Array.from(pendingGrowth.values()).sort((a,b)=>a.helper_id.localeCompare(b.helper_id)),
      revoked:Object.fromEntries(Array.from(revoked.entries()).sort()),
      journal,diagnostics
    },
    summary:{
      events:events.length,
      accepted:outcomes.filter(row=>row.accepted).length,
      mutated:outcomes.filter(row=>row.mutated).length,
      rejected:outcomes.filter(row=>!row.accepted).length,
      registered_helpers:registered.size,
      pending_growth:pendingGrowth.size,
      revoked_helpers:revoked.size,
      authority_grants:0,
      shared_operation_identities:stable(journal.map(row=>row.operation_id))===stable(diagnostics.map(row=>row.operation_id))
    },
    effects:{
      production_files_changed:false,browser_launched:false,network_requests:false,
      storage_writes:false,route_changes:false,mounts:false,bank_mutations:false,
      helper_ownership_changes:false,persisted_user_data_changed:false,
      live_observation_performed:false,formal_proof_performed:false
    },
    claim_ceiling:'Pure static event-contract evaluation only. Registration and growth are in-memory evidence; no production Helper is registered, mounted, activated, or granted authority.'
  };
  result.result_sha256=digest(result);
  return result;
}
function packageJournal(result){
  const entries=clone(result.snapshot.journal);
  return {
    type:JOURNAL_VERSION,version:VERSION,
    entry_count:entries.length,
    head_event_digest:entries.length?entries[entries.length-1].event_digest:null,
    snapshot_sha256:digest({
      registered:result.snapshot.registered,
      pending_growth:result.snapshot.pending_growth,
      revoked:result.snapshot.revoked
    }),
    entries
  };
}
function emptyRestore(code){
  const result=evaluate([]);
  return {status:'FAIL_CLOSED_EMPTY',code,restored:false,result};
}
function restoreJournal(packageValue){
  try{
    if(!packageValue||packageValue.type!==JOURNAL_VERSION||packageValue.version!==VERSION)return emptyRestore('REJECTED_JOURNAL_PACKAGE');
    if(!Array.isArray(packageValue.entries)||packageValue.entry_count!==packageValue.entries.length)return emptyRestore('REJECTED_JOURNAL_COUNT');
    const raw=packageValue.entries.map(row=>{
      const copy=clone(row);
      const expected=copy.event_digest;
      delete copy.event_digest;
      if(expected!==digest(copy))throw new Error('digest');
      return copy;
    });
    const result=evaluate(raw);
    if(result.summary.rejected!==0||result.snapshot.journal.length!==raw.length)return emptyRestore('REJECTED_JOURNAL_REPLAY');
    const repack=packageJournal(result);
    if(repack.head_event_digest!==packageValue.head_event_digest)return emptyRestore('REJECTED_JOURNAL_HEAD');
    if(repack.snapshot_sha256!==packageValue.snapshot_sha256)return emptyRestore('REJECTED_JOURNAL_SNAPSHOT');
    return {status:'RESTORED',code:'JOURNAL_RESTORED',restored:true,result};
  }catch(_){return emptyRestore('REJECTED_JOURNAL_DIGEST')}
}
function verifyResultHash(result){
  if(!result||typeof result.result_sha256!=='string')return false;
  const copy=clone(result),expected=copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy)===expected;
}
function scenarioResult(){
  const register=makeEvent('pass2_atlas_adapter','HELPER_REGISTERED',1);
  const update=withPrevious(makeEvent('pass2_atlas_adapter','HELPER_UPDATED',2,{registry_epoch:2,source_version:'source:v2'}),register);
  const growth=withPrevious(makeEvent('continuous_run_bank_order_frame_loader','HELPER_GROWTH_OBSERVED',3,{registry_epoch:2}),update);
  const result=evaluate([register,update,growth]);
  return {status:'PASS',result,journal_package:packageJournal(result),restore:restoreJournal(packageJournal(result))};
}
if(require.main===module)process.stdout.write(JSON.stringify(scenarioResult(),null,2)+'\n');
module.exports={
  EVENT_VERSION,JOURNAL_VERSION,REQUIRED_FIELDS,AUTHORITY_FIELDS,EVENT_TYPES,
  digest,eventContract,helperRows,authorityFor,makeEvent,withPrevious,evaluate,
  packageJournal,restoreJournal,verifyResultHash,scenarioResult
};
