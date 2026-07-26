(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){
    if(!root.PMPSectionOwnerMountIntegrationV1)root.PMPSectionOwnerMountIntegrationV1=api;
    api.install(root);
  }
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const TYPE='PMP_SECTION_OWNER_MOUNT_INTEGRATION_V1';
  const EVENT_VERSION='PMP_SECTION_OWNER_REGISTRATION_EVENT_V1';
  const CAPABILITY_VERSION='PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1';
  const REGISTRY_OWNER='mount_registry_owner';
  const ROOT_AUTHORITY='app_orchestrator_owner';
  const EVENTS=Object.freeze([
    'OWNER_REGISTERED','OWNER_UPDATED','OWNER_REMOVED','OWNER_GROWTH_OBSERVED'
  ]);
  const OWNERS=Object.freeze({
    app_orchestrator_owner:'app_orchestrator',
    reload_current_owner:'current_reload',
    mount_registry_owner:'mount_registry',
    bank_screen_owner:'bank',
    continuous_run_level_owner:'continuous_run',
    resident_30b_owner:'resident_30b',
    source_gate_owner:'source_gate',
    diagnostics_owner:'diagnostics'
  });
  const ID=/^[a-z0-9][a-z0-9._:-]{0,127}$/;
  const TIME=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
  const DIGEST=/^[0-9a-f]{64}$/;
  function ownerCapability(owner){return 'cap:p7u3:'+owner}

  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function clone(value){return value==null?value:JSON.parse(JSON.stringify(value))}
  function canonical(value){
    if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
    if(plain(value))return '{'+Object.keys(value).sort().map(
      key=>JSON.stringify(key)+':'+canonical(value[key])
    ).join(',')+'}';
    return JSON.stringify(value);
  }
  function eventDigest(value){
    let input=canonical(value),hash=2166136261;
    for(let i=0;i<input.length;i++){
      hash^=input.charCodeAt(i);
      hash=Math.imul(hash,16777619);
    }
    const word=(hash>>>0).toString(16).padStart(8,'0');
    return (word+word+word+word+word+word+word+word).slice(0,64);
  }
  function sideEffects(){
    return Object.freeze({
      mount_lifecycle_events:0,
      legacy_atlas_calls:0,
      mounts:0,
      repairs:0,
      route_assignments:0,
      bank_mutations:0,
      storage_migrations:0,
      persisted_user_data_writes:0,
      production_activations:0
    });
  }
  function dependencyStatus(mountRuntime){
    return Object.freeze({
      mount_lifecycle_runtime_available:!!(
        mountRuntime&&mountRuntime.available===true&&
        mountRuntime.registryOwner===REGISTRY_OWNER
      ),
      mount_registry_owner:REGISTRY_OWNER
    });
  }
  function shape(event){
    if(!plain(event))return 'REJECTED_MALFORMED_EVENT';
    const required=[
      'event_version','event_id','operation_id','monotonic_sequence','registry_epoch',
      'event_type','owner_id','section_id','source_version','observed_at',
      'previous_event_digest','authority'
    ];
    if(Object.keys(event).length!==required.length||
       required.some(key=>!Object.prototype.hasOwnProperty.call(event,key))){
      return 'REJECTED_MALFORMED_EVENT';
    }
    if(event.event_version!==EVENT_VERSION)return 'REJECTED_EVENT_VERSION';
    if(!ID.test(event.event_id)||!ID.test(event.operation_id)||!ID.test(event.owner_id)||
       !ID.test(event.section_id)||!ID.test(event.source_version))return 'REJECTED_IDENTITY';
    if(!Number.isInteger(event.monotonic_sequence)||event.monotonic_sequence<1){
      return 'REJECTED_SEQUENCE';
    }
    if(!Number.isInteger(event.registry_epoch)||event.registry_epoch<1)return 'REJECTED_EPOCH';
    if(EVENTS.indexOf(event.event_type)<0)return 'REJECTED_EVENT_TYPE';
    if(!TIME.test(event.observed_at))return 'REJECTED_TIME';
    if(event.previous_event_digest!==null&&!DIGEST.test(event.previous_event_digest)){
      return 'REJECTED_PREVIOUS_DIGEST';
    }
    if(!plain(event.authority))return 'REJECTED_AUTHORITY_SHAPE';
    const authorityFields=[
      'contract_version','authorizer','subject_id','capability_id','decision','action'
    ];
    if(Object.keys(event.authority).length!==authorityFields.length||
       authorityFields.some(key=>typeof event.authority[key]!=='string'||!event.authority[key])){
      return 'REJECTED_AUTHORITY_SHAPE';
    }
    return null;
  }
  function create(mountRuntime){
    const dependencies=dependencyStatus(mountRuntime);
    const registered=new Map();
    const pending=new Map();
    const lastByOwner=new Map();
    const eventsById=new Map();
    const operations=new Set();
    const journal=[];
    const diagnostics=[];
    const rejectionCounts={};
    let rejected=0,duplicates=0;

    function deny(code,event){
      rejected++;
      rejectionCounts[code]=(rejectionCounts[code]||0)+1;
      return Object.freeze({
        accepted:false,mutated:false,authority_granted:false,code,
        event_id:event&&event.event_id||null,
        operation_id:event&&event.operation_id||null,
        registry_owner:REGISTRY_OWNER
      });
    }
    function accept(code,event,mutated){
      return Object.freeze({
        accepted:true,mutated,authority_granted:false,code,
        event_id:event.event_id,operation_id:event.operation_id,
        registry_owner:REGISTRY_OWNER
      });
    }
    function applyOwnerEvent(input){
      const invalid=shape(input);
      if(invalid)return deny(invalid,input);
      const event=clone(input);
      const digest=eventDigest(event);
      if(eventsById.has(event.event_id)){
        if(eventsById.get(event.event_id)===digest){
          duplicates++;
          return accept('DUPLICATE_EVENT_IGNORED',event,false);
        }
        return deny('REJECTED_DUPLICATE_EVENT_CONFLICT',event);
      }
      if(operations.has(event.operation_id))return deny('REJECTED_DUPLICATE_OPERATION',event);
      const authority=event.authority;
      if(authority.contract_version!==CAPABILITY_VERSION){
        return deny('REJECTED_CAPABILITY_CONTRACT_VERSION',event);
      }
      const knownSection=OWNERS[event.owner_id];
      const growth=event.event_type==='OWNER_GROWTH_OBSERVED';
      if(!knownSection&&!growth)return deny('REJECTED_UNDECLARED_OWNER',event);
      if(knownSection&&event.section_id!==knownSection){
        return deny('REJECTED_OWNER_SECTION_MISMATCH',event);
      }
      if(growth){
        if(authority.authorizer!=='diagnostics_owner'||
           authority.subject_id!=='diagnostics_owner'||
           authority.capability_id!=='cap:p7u3:growth-observer'||
           authority.decision!=='OBSERVED_ONLY_NO_AUTHORITY'||
           authority.action!=='observe_owner_growth'){
          return deny('REJECTED_GROWTH_OBSERVER_AUTHORITY',event);
        }
      }else{
        const action={
          OWNER_REGISTERED:'register_owner',
          OWNER_UPDATED:'update_owner',
          OWNER_REMOVED:'remove_owner'
        }[event.event_type];
        if(authority.authorizer!==ROOT_AUTHORITY||
           authority.subject_id!==event.owner_id||
           authority.decision!=='AUTHORIZED'||authority.action!==action||
           authority.capability_id!==ownerCapability(event.owner_id)){
          return deny('REJECTED_REGISTRATION_AUTHORITY',event);
        }
      }
      const prior=lastByOwner.get(event.owner_id);
      if(!prior){
        if(event.monotonic_sequence!==1||event.previous_event_digest!==null){
          return deny('REJECTED_SEQUENCE_START',event);
        }
      }else{
        if(event.registry_epoch<prior.registry_epoch)return deny('REJECTED_STALE_EPOCH',event);
        if(event.registry_epoch>prior.registry_epoch+1)return deny('REJECTED_EPOCH_GAP',event);
        if(event.monotonic_sequence<=prior.monotonic_sequence){
          return deny('REJECTED_STALE_SEQUENCE',event);
        }
        if(event.monotonic_sequence!==prior.monotonic_sequence+1){
          return deny('REJECTED_SEQUENCE_GAP',event);
        }
        if(event.previous_event_digest!==prior.event_digest){
          return deny('REJECTED_EVENT_CHAIN',event);
        }
        if(event.observed_at<prior.observed_at)return deny('REJECTED_TIME_REGRESSION',event);
      }
      let code='';
      if(event.event_type==='OWNER_REGISTERED'){
        if(registered.has(event.owner_id))return deny('REJECTED_DUPLICATE_OWNER',event);
        registered.set(event.owner_id,{
          owner_id:event.owner_id,section_id:event.section_id,
          source_version:event.source_version,registry_epoch:event.registry_epoch,
          status:'REGISTERED_CAPABILITY_BOUND'
        });
        code='OWNER_REGISTERED';
      }else if(event.event_type==='OWNER_UPDATED'){
        if(!registered.has(event.owner_id))return deny('REJECTED_OWNER_NOT_REGISTERED',event);
        const row=registered.get(event.owner_id);
        row.source_version=event.source_version;
        row.registry_epoch=event.registry_epoch;
        code='OWNER_UPDATED';
      }else if(event.event_type==='OWNER_REMOVED'){
        if(!registered.has(event.owner_id))return deny('REJECTED_OWNER_NOT_REGISTERED',event);
        registered.delete(event.owner_id);
        code='OWNER_REMOVED';
      }else{
        pending.set(event.owner_id,{
          owner_id:event.owner_id,section_id:event.section_id,
          source_version:event.source_version,status:'OBSERVED_PENDING_NO_AUTHORITY',
          authority_granted:false
        });
        code='OWNER_GROWTH_RECORDED_NO_AUTHORITY';
      }
      const normalized=clone(event);
      normalized.event_digest=digest;
      lastByOwner.set(event.owner_id,normalized);
      eventsById.set(event.event_id,digest);
      operations.add(event.operation_id);
      journal.push(normalized);
      diagnostics.push({
        operation_id:event.operation_id,event_id:event.event_id,owner_id:event.owner_id,
        section_id:event.section_id,event_type:event.event_type,result:code,
        capability_present:typeof authority.capability_id==='string',
        authority_granted:false
      });
      return accept(code,event,true);
    }
    function snapshot(){
      return clone({
        type:'PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1',
        version:VERSION,event_version:EVENT_VERSION,
        capability_contract_version:CAPABILITY_VERSION,
        registry_owner:REGISTRY_OWNER,dependencies,
        registered:Array.from(registered.values()).sort((a,b)=>a.owner_id.localeCompare(b.owner_id)),
        pending_growth:Array.from(pending.values()).sort((a,b)=>a.owner_id.localeCompare(b.owner_id)),
        journal,diagnostics,
        counts:{
          registered:registered.size,pending_growth:pending.size,
          accepted:journal.length,rejected,duplicates
        },
        disclosure:{
          capability_ids_exposed_to_diagnostics:false,
          raw_authority_payloads_exposed:false
        },
        side_effects:sideEffects()
      });
    }
    return Object.freeze({
      type:TYPE,version:VERSION,available:true,mode:'PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY',
      registryOwner:REGISTRY_OWNER,eventVersion:EVENT_VERSION,
      capabilityContractVersion:CAPABILITY_VERSION,dependencies,
      applyOwnerEvent,snapshot,sideEffects:sideEffects()
    });
  }
  function restore(mountRuntime,journal){
    const empty=create(mountRuntime);
    function rejected(code,index,outcome){
      return Object.freeze({
        restored:false,mutated:false,authority_granted:false,code,
        rejected_index:Number.isInteger(index)?index:null,
        rejected_code:outcome&&outcome.code||null,
        operation_ids:Object.freeze([]),
        runtime:empty,
        side_effects:sideEffects()
      });
    }
    if(!Array.isArray(journal))return rejected('RESTART_REJECTED_MALFORMED_JOURNAL',null,null);
    const candidate=create(mountRuntime);
    const operationIds=[];
    for(let index=0;index<journal.length;index++){
      const event=clone(journal[index]);
      if(!plain(event)||!Object.prototype.hasOwnProperty.call(event,'event_digest')){
        return rejected(
          'RESTART_REJECTED_JOURNAL_EVENT',index,
          {code:'REJECTED_STORED_EVENT_DIGEST'}
        );
      }
      const storedDigest=event.event_digest;
      delete event.event_digest;
      if(!DIGEST.test(storedDigest)||storedDigest!==eventDigest(event)){
        return rejected(
          'RESTART_REJECTED_JOURNAL_EVENT',index,
          {code:'REJECTED_STORED_EVENT_DIGEST'}
        );
      }
      const outcome=candidate.applyOwnerEvent(event);
      if(!outcome.accepted||!outcome.mutated){
        return rejected('RESTART_REJECTED_JOURNAL_EVENT',index,outcome);
      }
      operationIds.push(outcome.operation_id);
    }
    return Object.freeze({
      restored:true,mutated:journal.length>0,authority_granted:false,
      code:'RESTART_REPLAY_ACCEPTED',rejected_index:null,rejected_code:null,
      operation_ids:Object.freeze(operationIds.slice()),
      runtime:candidate,
      side_effects:sideEffects()
    });
  }
  function install(target){
    const host=target&&typeof target==='object'?target:null;
    if(!host)return null;
    const existing=host.PMPSectionOwnerMountRuntimeV1;
    if(existing&&existing.type===TYPE)return existing;
    const runtime=create(host.PMPMountLifecycleRuntimeV1);
    host.PMPSectionOwnerMountRuntimeV1=runtime;
    return runtime;
  }
  return Object.freeze({
    type:TYPE,version:VERSION,eventVersion:EVENT_VERSION,
    capabilityContractVersion:CAPABILITY_VERSION,registryOwner:REGISTRY_OWNER,
    owners:OWNERS,create,restore,install,eventDigest
  });
});
