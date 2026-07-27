(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PMPMigrationInactiveGateV1=api;
})(typeof window!=='undefined'?window:globalThis,function(){
  'use strict';
  const TYPE='PMP_MIGRATION_INACTIVE_GATE_V1';
  const VERSION='1.0.0-pass12';
  const PLAN_TYPE='PMP_MIGRATION_PLAN_V1';
  const AUTHORITY_TYPE='PMP_EXACT_PRODUCTION_MIGRATION_AUTHORITY_V1';
  const INACTIVE='PRODUCTION_GATE_INACTIVE';
  const textEncoder=typeof TextEncoder!=='undefined'?new TextEncoder():null;

  function clone(value){return JSON.parse(JSON.stringify(value));}
  function canonical(value){
    if(value===null||typeof value!=='object')return JSON.stringify(value);
    if(Array.isArray(value))return'['+value.map(canonical).join(',')+']';
    return'{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
  }
  function utf8(value){
    const text=String(value);
    if(textEncoder)return textEncoder.encode(text);
    if(typeof Buffer!=='undefined')return Uint8Array.from(Buffer.from(text,'utf8'));
    throw new Error('UTF8_ENCODER_UNAVAILABLE');
  }
  function rotr(n,x){return(x>>>n)|(x<<(32-n));}
  function sha256(value){
    const input=utf8(value),length=input.length,bitLength=length*8;
    const withOne=length+1,total=Math.ceil((withOne+8)/64)*64,bytes=new Uint8Array(total);
    bytes.set(input);bytes[length]=0x80;
    const high=Math.floor(bitLength/0x100000000),low=bitLength>>>0;
    for(let i=0;i<4;i++){bytes[total-8+i]=(high>>>(24-i*8))&255;bytes[total-4+i]=(low>>>(24-i*8))&255;}
    const h=new Uint32Array([0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]);
    const k=new Uint32Array([0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]);
    const w=new Uint32Array(64);
    for(let offset=0;offset<total;offset+=64){
      for(let i=0;i<16;i++){const p=offset+i*4;w[i]=((bytes[p]<<24)|(bytes[p+1]<<16)|(bytes[p+2]<<8)|bytes[p+3])>>>0;}
      for(let i=16;i<64;i++){const x=w[i-15],y=w[i-2],s0=(rotr(7,x)^rotr(18,x)^(x>>>3))>>>0,s1=(rotr(17,y)^rotr(19,y)^(y>>>10))>>>0;w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;}
      let a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
      for(let i=0;i<64;i++){const s1=(rotr(6,e)^rotr(11,e)^rotr(25,e))>>>0,ch=((e&f)^((~e)&g))>>>0,t1=(hh+s1+ch+k[i]+w[i])>>>0,s0=(rotr(2,a)^rotr(13,a)^rotr(22,a))>>>0,maj=((a&b)^(a&c)^(b&c))>>>0,t2=(s0+maj)>>>0;hh=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
      h[0]=(h[0]+a)>>>0;h[1]=(h[1]+b)>>>0;h[2]=(h[2]+c)>>>0;h[3]=(h[3]+d)>>>0;h[4]=(h[4]+e)>>>0;h[5]=(h[5]+f)>>>0;h[6]=(h[6]+g)>>>0;h[7]=(h[7]+hh)>>>0;
    }
    return Array.from(h).map(x=>x.toString(16).padStart(8,'0')).join('');
  }
  function deny(code,detail){
    return{ok:false,decision:'DENY',code:String(code),detail:String(detail||''),effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  function validatePlan(plan){
    if(!plan||plan.type!==PLAN_TYPE)return deny('DENIED_PLAN_TYPE');
    if(plan.mode!=='INACTIVE_NONPRODUCTION_PLAN'||plan.default_decision!=='DENY')return deny('DENIED_PLAN_MODE');
    if(!plan.target||plan.target.activation!=='INACTIVE'||plan.target.production_commit_available!==false)return deny('DENIED_TARGET_ACTIVE');
    if(!plan.authority_gate||plan.authority_gate.state!=='INACTIVE'||plan.authority_gate.production_migration_authorized!==false)return deny('DENIED_AUTHORITY_GATE');
    if(!Array.isArray(plan.inventory)||plan.inventory.length<1)return deny('DENIED_EMPTY_INVENTORY');
    const ids=new Set(),owners=new Set();
    for(const row of plan.inventory){
      if(!row||!String(row.id||'')||!String(row.owner||''))return deny('DENIED_INVENTORY_ROW');
      if(ids.has(row.id))return deny('DENIED_DUPLICATE_INVENTORY_ID',row.id);
      ids.add(row.id);owners.add(row.owner);
    }
    return{ok:true,decision:'ALLOW_STATIC_ONLY',code:'INACTIVE_PLAN_VALID',plan_sha256:sha256(canonical(plan)),inventory_count:ids.size,owner_count:owners.size,effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  function recordIdentity(record){return String(record.owner||'')+'\u0000'+String(record.record_id||'');}
  function validateRecord(record,allowedOwners){
    if(!record||typeof record!=='object'||Array.isArray(record))return deny('DENIED_RECORD_SHAPE');
    if(!String(record.owner||'')||!String(record.record_id||''))return deny('DENIED_RECORD_IDENTITY');
    if(!Number.isInteger(record.schema_version)||record.schema_version<1)return deny('DENIED_RECORD_SCHEMA');
    if(!Object.prototype.hasOwnProperty.call(record,'payload'))return deny('DENIED_RECORD_PAYLOAD');
    const payloadHash=sha256(canonical(record.payload));
    if(record.payload_sha256!==payloadHash)return deny('DENIED_RECORD_PAYLOAD_HASH',recordIdentity(record));
    if(!allowedOwners.has(record.owner))return deny('QUARANTINE_UNKNOWN_OWNER',recordIdentity(record));
    return{ok:true,payload_sha256:payloadHash};
  }
  function sourceSnapshot(records){
    const sorted=clone(records).sort((a,b)=>recordIdentity(a).localeCompare(recordIdentity(b),'en',{sensitivity:'variant'}));
    const identities=sorted.map(recordIdentity);
    return{record_count:sorted.length,identities,records_sha256:sha256(canonical(sorted)),source_bytes:utf8(canonical(sorted)).length};
  }
  function migrationId(planHash,snapshotHash){return sha256(TYPE+'\u0000'+planHash+'\u0000'+snapshotHash);}
  function dryRun(plan,records,options){
    options=options||{};
    if(options.fixture_scope!=='DISPOSABLE_FIXTURE')return deny('DENIED_NONDISPOSABLE_SCOPE');
    const planResult=validatePlan(plan);if(!planResult.ok)return planResult;
    if(!Array.isArray(records))return deny('DENIED_RECORD_SET');
    const allowedOwners=new Set(plan.inventory.map(row=>row.owner)),seen=new Set(),quarantine=[],accepted=[];
    for(const original of records){
      const record=clone(original),result=validateRecord(record,allowedOwners);
      if(!result.ok&&result.code!=='QUARANTINE_UNKNOWN_OWNER')return result;
      const identity=recordIdentity(record);
      if(result.code==='QUARANTINE_UNKNOWN_OWNER'){quarantine.push({identity,exact_record:record,record_sha256:sha256(canonical(record))});continue;}
      if(seen.has(identity))return deny('DENIED_DUPLICATE_IDENTITY',identity);
      seen.add(identity);accepted.push(record);
    }
    accepted.sort((a,b)=>recordIdentity(a).localeCompare(recordIdentity(b),'en',{sensitivity:'variant'}));
    quarantine.sort((a,b)=>a.identity.localeCompare(b.identity,'en',{sensitivity:'variant'}));
    const snapshot=sourceSnapshot(accepted),id=migrationId(planResult.plan_sha256,snapshot.records_sha256);
    const staged=accepted.map(record=>{
      const sourceHash=sha256(canonical(record));
      const target={migration_id:id,owner:record.owner,record_id:record.record_id,source_schema_version:record.schema_version,target_schema_version:plan.target.schema_version,payload:clone(record.payload),payload_sha256:record.payload_sha256,source_record_sha256:sourceHash};
      target.migration_receipt=sha256(canonical({migration_id:id,owner:target.owner,record_id:target.record_id,source_record_sha256:sourceHash,payload_sha256:target.payload_sha256}));
      return target;
    });
    const targetManifest={record_count:staged.length,identities:staged.map(recordIdentity),records_sha256:sha256(canonical(staged)),payload_aggregate_sha256:sha256(canonical(staged.map(row=>row.payload_sha256)))};
    const result={ok:true,decision:'ALLOW_DISPOSABLE_FIXTURE_ONLY',code:'DRY_RUN_COMPLETE',migration_id:id,plan_sha256:planResult.plan_sha256,source_snapshot:snapshot,target_manifest:targetManifest,staged_records:staged,quarantine,quarantine_count:quarantine.length,reconciliation:{source_count:snapshot.record_count,target_count:staged.length,identity_match:canonical(snapshot.identities)===canonical(targetManifest.identities),payload_hashes_match:staged.every(row=>row.payload_sha256===sha256(canonical(row.payload))),unrelated_storage_policy:'PRESERVE_EXACTLY'},effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
    result.result_sha256=sha256(canonical(result));return result;
  }
  function shadowCompare(sourceRecords,stagedRecords){
    if(!Array.isArray(sourceRecords)||!Array.isArray(stagedRecords))return deny('DENIED_SHADOW_INPUT');
    const source=sourceRecords.slice().sort((a,b)=>recordIdentity(a).localeCompare(recordIdentity(b)));
    const target=stagedRecords.slice().sort((a,b)=>recordIdentity(a).localeCompare(recordIdentity(b)));
    const sourceRows=source.map(row=>({identity:recordIdentity(row),payload_sha256:row.payload_sha256}));
    const targetRows=target.map(row=>({identity:recordIdentity(row),payload_sha256:row.payload_sha256}));
    return{ok:canonical(sourceRows)===canonical(targetRows),decision:'PURE_COMPARE_ONLY',code:canonical(sourceRows)===canonical(targetRows)?'SHADOW_MATCH':'SHADOW_MISMATCH',source_count:sourceRows.length,target_count:targetRows.length,source_sha256:sha256(canonical(sourceRows)),target_sha256:sha256(canonical(targetRows)),effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  function buildRollbackPlan(dryRunResult,sourceRecords,unrelatedStorage){
    if(!dryRunResult||dryRunResult.code!=='DRY_RUN_COMPLETE'||!Array.isArray(sourceRecords))return deny('DENIED_ROLLBACK_INPUT');
    const exactSource=clone(sourceRecords),unrelated=clone(unrelatedStorage===undefined?null:unrelatedStorage);
    const body={type:'PMP_MIGRATION_ROLLBACK_PLAN_V1',migration_id:dryRunResult.migration_id,action:'DISCARD_STAGED_TARGET_AND_RETAIN_SOURCE',source_snapshot_sha256:sha256(canonical(exactSource)),source_record_count:exactSource.length,exact_source_records:exactSource,unrelated_storage:unrelated,unrelated_storage_sha256:sha256(canonical(unrelated)),automatic_retry:false,source_delete_allowed:false,target_partial_discard_required:true};
    body.rollback_plan_sha256=sha256(canonical(body));return{ok:true,decision:'ALLOW_PLAN_ONLY',code:'ROLLBACK_PLAN_READY',plan:body,effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  function simulateBoundedStage(dryRunResult,failAfter){
    if(!dryRunResult||dryRunResult.code!=='DRY_RUN_COMPLETE')return deny('DENIED_STAGE_INPUT');
    const target=[],limit=Number.isInteger(failAfter)?failAfter:dryRunResult.staged_records.length;
    for(let i=0;i<dryRunResult.staged_records.length;i++){
      if(i===limit)return{ok:false,decision:'ROLLBACK',code:'INJECTED_PARTIAL_STAGE_FAILURE',staged_before_failure:target.length,staged_after_rollback:0,rollback_complete:true,source_changed:false,automatic_retry:false,effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
      target.push(clone(dryRunResult.staged_records[i]));
    }
    return{ok:true,decision:'STAGED_DISPOSABLE_ONLY',code:'DISPOSABLE_STAGE_COMPLETE',staged_count:target.length,target_manifest_sha256:sha256(canonical(target)),source_changed:false,effects:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  function requestProductionMigration(input){
    const authority=input&&input.authority_receipt;
    const detail=authority&&authority.type===AUTHORITY_TYPE?'exact authority cannot activate an inactive build':'exact production authority absent';
    return deny(INACTIVE,detail);
  }
  function snapshot(){
    return{type:TYPE,version:VERSION,status:INACTIVE,production_commit_available:false,production_storage_api_present:false,network_api_present:false,automatic_retry:false,allowed_scope:'DISPOSABLE_FIXTURE_AND_PURE_DATA_ONLY',effects_on_load:{production_storage_reads:0,production_storage_writes:0,production_storage_deletes:0,persisted_user_data_changed:false,authority_consumed:false}};
  }
  return Object.freeze({type:TYPE,version:VERSION,plan_type:PLAN_TYPE,authority_type:AUTHORITY_TYPE,canonical,sha256,validatePlan,dryRun,shadowCompare,buildRollbackPlan,simulateBoundedStage,requestProductionMigration,snapshot});
});
