#!/usr/bin/env node
'use strict';
const crypto=require('crypto');
const fs=require('fs');
const path=require('path');
const vm=require('vm');
const {execFileSync}=require('child_process');
const ROOT=path.resolve(__dirname,'..');
const RECORD='audit/pass8/pass8-helper-unit2-capability-contract-v1.json';
const RULES='pmp-pass8-helper-rules-v1.js';
const RESULT_TYPE='PMP_PASS8_UNIT2_HELPER_CAPABILITY_RESULT_V1';
const VERSION='1.0.0';
const ID=/^[a-z0-9][a-z0-9._:-]{0,191}$/;
const TIME=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;

function stable(value){
  if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
  if(value&&typeof value==='object'){
    return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
  }
  return JSON.stringify(value);
}
function digest(value){
  return crypto.createHash('sha256').update(
    Buffer.isBuffer(value)?value:Buffer.from(stable(value))
  ).digest('hex');
}
function shaFile(relative){
  const local=path.join(ROOT,relative);
  const payload=fs.existsSync(local)
    ?fs.readFileSync(local)
    :execFileSync('git',['show',`HEAD:${relative}`],{cwd:ROOT,encoding:null});
  return crypto.createHash('sha256').update(payload).digest('hex');
}
function clone(value){return JSON.parse(JSON.stringify(value))}
function contract(){
  return JSON.parse(fs.readFileSync(path.join(ROOT,RECORD),'utf8')).helper_contract;
}
function declarations(){
  const rows=new Map();
  const storage={
    setItem(key,value){rows.set(String(key),String(value))},
    getItem(key){return rows.has(String(key))?rows.get(String(key)):null},
    removeItem(key){rows.delete(String(key))}
  };
  const document={querySelectorAll(){return []}};
  const host={localStorage:storage,document};
  host.top=host;
  host.window=host;
  vm.runInNewContext(fs.readFileSync(path.join(ROOT,RULES),'utf8'),{
    window:host,localStorage:storage,document,
    setTimeout(){return 0},clearTimeout(){},
    console:{log(){},warn(){},error(){}},
    Date,JSON,Array,Object,String,Number,Boolean,RegExp,Math
  },{filename:RULES,timeout:1000});
  if(!host.PMPPass8HelperRulesV1)throw new Error('Pass 8 Helper rules API unavailable');
  return clone(host.PMPPass8HelperRulesV1.getRegistry());
}
function resourcesFor(helper,canonicalOwner){
  return [
    `helper:${helper.id}`,
    `owner:${canonicalOwner}:slot:${helper.slot}`,
    ...(helper.storage||[]).map(key=>`storage:${key}`),
    ...(helper.panels||[]).map(panel=>`panel:${panel}`)
  ];
}
function describe(helper,policy){
  const binding=policy.owner_bindings[helper.owner];
  if(!binding)throw new Error(`missing owner binding ${helper.owner}`);
  let disposition='ELIGIBLE_STATIC_CAPABILITY';
  let hold_reason=null;
  if(helper.registration==='legacy'){
    disposition='HELD_LEGACY';
    hold_reason='LEGACY_DECLARATION_NO_ACTIVE_CAPABILITY';
  }
  const explicit=policy.explicit_helper_holds[helper.id];
  if(explicit){
    disposition='HELD_CONTRACT_CONFLICT';
    hold_reason=explicit;
  }
  return {
    helper_id:helper.id,
    helper_file:helper.file,
    helper_source_sha256:shaFile(helper.file),
    declared_owner_label:helper.owner,
    binding_kind:binding.binding_kind,
    canonical_owner_id:binding.canonical_owner_id,
    section_id:binding.section_id,
    slot:helper.slot,
    registration:helper.registration,
    actions:clone(helper.allowed),
    resources:resourcesFor(helper,binding.canonical_owner_id),
    guard_requirements:clone(binding.guard_requirements),
    growth_source:helper.growth_source,
    disposition,
    hold_reason
  };
}
function inventory(policy=contract()){
  const declared=declarations().map(row=>describe(row,policy));
  const unknown=clone(policy.unknown_helper_sources).map(file=>({
    file,disposition:'HELD_UNDECLARED_SOURCE',reason:'UNDECLARED_SOURCE_NO_CAPABILITY'
  }));
  return {
    declared,
    unknown,
    counts:{
      declared_helpers:declared.length,
      eligible_helpers:declared.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY').length,
      held_declared_helpers:declared.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY').length,
      owner_bindings:Object.keys(policy.owner_bindings).length,
      guarded_helpers:declared.filter(row=>row.guard_requirements.length>0).length,
      growth_helpers:declared.filter(row=>row.growth_source!=='none').length,
      legacy_helpers:declared.filter(row=>row.registration==='legacy').length,
      unknown_helper_sources:unknown.length
    }
  };
}
function capabilityFor(helperId,overrides={},policy=contract()){
  const row=inventory(policy).declared.find(item=>item.helper_id===helperId);
  if(!row)throw new Error(`unknown helper ${helperId}`);
  return Object.assign({
    contract_version:policy.contract_version,
    capability_id:`cap:p8u2:${row.helper_id}`,
    helper_id:row.helper_id,
    helper_file:row.helper_file,
    helper_source_sha256:row.helper_source_sha256,
    declared_owner_label:row.declared_owner_label,
    canonical_owner_id:row.canonical_owner_id,
    section_id:row.section_id,
    slot:row.slot,
    registration:row.registration,
    actions:clone(row.actions),
    resources:clone(row.resources),
    guard_requirements:clone(row.guard_requirements),
    growth_source:row.growth_source,
    granted_by:policy.root_grant_authority,
    issued_at:'2026-07-26T17:50:00Z',
    expires_at:'2026-08-02T17:50:00Z',
    revocation_epoch:0
  },clone(overrides));
}
function event(type,operationId,fields={}){
  return Object.assign({
    type,
    operation_id:operationId,
    observed_at:'2026-07-27T00:00:00Z'
  },clone(fields));
}
function deny(code,operationId){
  return {accepted:false,authorized:false,mutated:false,code,operation_id:operationId||null};
}
function accept(code,operationId,authorized=false){
  return {
    accepted:true,
    authorized,
    mutated:code==='CAPABILITY_GRANTED'||code==='CAPABILITY_REVOKED',
    code,
    operation_id:operationId
  };
}
function same(a,b){return stable(a)===stable(b)}
function shape(eventValue){
  if(!eventValue||typeof eventValue!=='object'||Array.isArray(eventValue))return 'REJECTED_MALFORMED';
  if(!ID.test(String(eventValue.operation_id||'')))return 'REJECTED_OPERATION_ID';
  if(!TIME.test(String(eventValue.observed_at||'')))return 'REJECTED_TIME';
  if(!['GRANT','AUTHORIZE','REVOKE'].includes(eventValue.type))return 'REJECTED_EVENT_TYPE';
  return null;
}
function evaluate(events,policy=contract()){
  const observed=inventory(policy);
  const helpers=new Map(observed.declared.map(row=>[row.helper_id,row]));
  const unknown=new Set(policy.unknown_helper_sources);
  const capabilities=new Map();
  const revoked=new Map();
  const operations=new Set();
  const outcomes=[];
  for(const raw of events){
    const current=clone(raw);
    const error=shape(current);
    if(error){outcomes.push(deny(error,current&&current.operation_id));continue}
    const operationId=current.operation_id;
    if(operations.has(operationId)){outcomes.push(deny('REJECTED_DUPLICATE_OPERATION',operationId));continue}
    operations.add(operationId);
    if(current.type==='GRANT'){
      const cap=current.capability;
      if(!cap||typeof cap!=='object'||Array.isArray(cap)){
        outcomes.push(deny('REJECTED_CAPABILITY_SHAPE',operationId));continue;
      }
      const expectedFields=policy.required_capability_fields;
      if(!same(Object.keys(cap).sort(),expectedFields.slice().sort())){
        outcomes.push(deny('REJECTED_CAPABILITY_SHAPE',operationId));continue;
      }
      if(cap.contract_version!==policy.contract_version){
        outcomes.push(deny('REJECTED_CONTRACT_VERSION',operationId));continue;
      }
      if(!ID.test(String(cap.capability_id||''))){
        outcomes.push(deny('REJECTED_CAPABILITY_ID',operationId));continue;
      }
      if(capabilities.has(cap.capability_id)||revoked.has(cap.capability_id)){
        outcomes.push(deny('REJECTED_DUPLICATE_CAPABILITY',operationId));continue;
      }
      const helper=helpers.get(cap.helper_id);
      if(!helper){
        const code=unknown.has(cap.helper_file)?'REJECTED_UNDECLARED_SOURCE':'REJECTED_UNKNOWN_HELPER';
        outcomes.push(deny(code,operationId));continue;
      }
      if(helper.disposition==='HELD_LEGACY'){
        outcomes.push(deny('REJECTED_LEGACY_HELPER_HELD',operationId));continue;
      }
      if(helper.disposition!=='ELIGIBLE_STATIC_CAPABILITY'){
        outcomes.push(deny('REJECTED_HELPER_CONFLICT_HELD',operationId));continue;
      }
      if(cap.helper_file!==helper.helper_file){
        outcomes.push(deny('REJECTED_HELPER_FILE_BINDING',operationId));continue;
      }
      if(cap.helper_source_sha256!==helper.helper_source_sha256){
        outcomes.push(deny('REJECTED_SOURCE_HASH',operationId));continue;
      }
      if(cap.declared_owner_label!==helper.declared_owner_label){
        outcomes.push(deny('REJECTED_OWNER_ALIAS',operationId));continue;
      }
      if(cap.canonical_owner_id!==helper.canonical_owner_id||cap.section_id!==helper.section_id){
        outcomes.push(deny('REJECTED_OWNER_BINDING',operationId));continue;
      }
      if(cap.slot!==helper.slot){
        outcomes.push(deny('REJECTED_SLOT_BINDING',operationId));continue;
      }
      if(cap.registration!==helper.registration){
        outcomes.push(deny('REJECTED_REGISTRATION_BINDING',operationId));continue;
      }
      if(!same(cap.actions,helper.actions)){
        outcomes.push(deny('REJECTED_ACTION_BINDING',operationId));continue;
      }
      if(!same(cap.resources,helper.resources)){
        outcomes.push(deny('REJECTED_RESOURCE_BINDING',operationId));continue;
      }
      if(!same(cap.guard_requirements,helper.guard_requirements)){
        outcomes.push(deny('REJECTED_GUARD_BINDING',operationId));continue;
      }
      if(cap.growth_source!==helper.growth_source){
        outcomes.push(deny('REJECTED_GROWTH_SOURCE',operationId));continue;
      }
      if(cap.granted_by!==policy.root_grant_authority){
        outcomes.push(deny('REJECTED_ROOT_GRANT_AUTHORITY',operationId));continue;
      }
      if(!TIME.test(String(cap.issued_at||''))||!TIME.test(String(cap.expires_at||''))){
        outcomes.push(deny('REJECTED_TIME',operationId));continue;
      }
      if(cap.issued_at>=cap.expires_at){
        outcomes.push(deny('REJECTED_EXPIRY',operationId));continue;
      }
      if(!Number.isInteger(cap.revocation_epoch)||cap.revocation_epoch<0){
        outcomes.push(deny('REJECTED_REVOCATION_EPOCH',operationId));continue;
      }
      capabilities.set(cap.capability_id,clone(cap));
      outcomes.push(accept('CAPABILITY_GRANTED',operationId));continue;
    }
    const cap=capabilities.get(current.capability_id);
    if(!cap){outcomes.push(deny('REJECTED_CAPABILITY_MISSING',operationId));continue}
    if(current.type==='REVOKE'){
      if(current.actor_id!==policy.root_grant_authority){
        outcomes.push(deny('REJECTED_REVOCATION_AUTHORITY',operationId));continue;
      }
      const prior=revoked.has(current.capability_id)?revoked.get(current.capability_id):cap.revocation_epoch;
      if(!Number.isInteger(current.revocation_epoch)||current.revocation_epoch<=prior){
        outcomes.push(deny('REJECTED_STALE_REVOCATION',operationId));continue;
      }
      revoked.set(current.capability_id,current.revocation_epoch);
      outcomes.push(accept('CAPABILITY_REVOKED',operationId));continue;
    }
    if(revoked.has(current.capability_id)){
      outcomes.push(deny('REJECTED_CAPABILITY_REVOKED',operationId));continue;
    }
    if(current.observed_at<cap.issued_at){
      outcomes.push(deny('REJECTED_NOT_YET_VALID',operationId));continue;
    }
    if(current.observed_at>=cap.expires_at){
      outcomes.push(deny('REJECTED_EXPIRED',operationId));continue;
    }
    if(current.helper_id!==cap.helper_id){
      outcomes.push(deny('REJECTED_HELPER_IDENTITY',operationId));continue;
    }
    if(current.canonical_owner_id!==cap.canonical_owner_id||current.section_id!==cap.section_id){
      outcomes.push(deny('REJECTED_OWNER_BINDING',operationId));continue;
    }
    if(current.slot!==cap.slot){
      outcomes.push(deny('REJECTED_SLOT_BINDING',operationId));continue;
    }
    if(current.revocation_epoch!==cap.revocation_epoch){
      outcomes.push(deny('REJECTED_REVOCATION_EPOCH',operationId));continue;
    }
    if(!cap.actions.includes(current.action)){
      outcomes.push(deny('REJECTED_ACTION_NOT_GRANTED',operationId));continue;
    }
    if(!cap.resources.includes(current.resource)){
      outcomes.push(deny('REJECTED_RESOURCE_NOT_GRANTED',operationId));continue;
    }
    if(!same(current.guard_evidence||[],cap.guard_requirements)){
      outcomes.push(deny('REJECTED_GUARD_REQUIREMENTS',operationId));continue;
    }
    if(cap.growth_source!=='none'&&current.growth_source!==cap.growth_source){
      outcomes.push(deny('REJECTED_GROWTH_SOURCE',operationId));continue;
    }
    outcomes.push(accept('AUTHORIZED',operationId,true));
  }
  const result={
    type:RESULT_TYPE,
    version:VERSION,
    status:'PASS',
    contract_version:policy.contract_version,
    inventory:observed,
    outcomes,
    summary:{
      events:events.length,
      accepted:outcomes.filter(row=>row.accepted).length,
      authorized:outcomes.filter(row=>row.authorized).length,
      rejected:outcomes.filter(row=>!row.accepted).length,
      capabilities_retained:capabilities.size,
      capabilities_revoked:revoked.size
    },
    state:{
      capability_ids:Array.from(capabilities.keys()).sort(),
      revoked:Object.fromEntries(Array.from(revoked.entries()).sort())
    },
    effects:{
      production_files_changed:false,
      browser_launched:false,
      network_requests:false,
      storage_writes:false,
      route_changes:false,
      mounts:false,
      bank_mutations:false,
      helper_ownership_changes:false,
      persisted_user_data_changed:false,
      live_observation_performed:false,
      formal_proof_performed:false
    },
    claim_ceiling:'Pure static Helper capability evaluation only. No Helper is registered, mounted, activated, delegated in production, allowed to mutate Bank or routes, or granted runtime authority.'
  };
  result.result_sha256=digest(result);
  return result;
}
function verifyResultHash(result){
  if(!result||typeof result.result_sha256!=='string')return false;
  const copy=clone(result);
  const expected=copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy)===expected;
}
if(require.main===module)process.stdout.write(JSON.stringify(evaluate([]),null,2)+'\n');
module.exports={
  contract,declarations,inventory,capabilityFor,event,evaluate,verifyResultHash,digest,shaFile
};
