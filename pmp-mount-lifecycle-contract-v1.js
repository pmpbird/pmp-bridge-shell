(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&!root.PMPMountLifecycleContractV1)root.PMPMountLifecycleContractV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const CONTRACT_VERSION='PMP_MOUNT_LIFECYCLE_CONTRACT_V1';
  const REGISTRY_OWNER='mount_registry_owner';
  const ACTIVE_STATES=Object.freeze([
    'ROUTE_REQUESTED',
    'OWNER_RESOLVED',
    'MOUNT_STARTED',
    'MOUNTED',
    'READY'
  ]);
  const FAILURE_STATES=Object.freeze([
    'SLOW',
    'DEGRADED',
    'BLOCKED',
    'FAILED'
  ]);
  const STATES=Object.freeze(ACTIVE_STATES.concat(FAILURE_STATES));
  const TRUST_LEVELS=Object.freeze([
    'OWNER_ATTESTED',
    'OBSERVER_REPORTED',
    'INFERRED'
  ]);
  const TERMINAL_STATES=Object.freeze(['BLOCKED','FAILED']);
  const TRANSITIONS=Object.freeze({
    __START__:Object.freeze(['ROUTE_REQUESTED']),
    ROUTE_REQUESTED:Object.freeze(['OWNER_RESOLVED','BLOCKED','FAILED']),
    OWNER_RESOLVED:Object.freeze(['MOUNT_STARTED','BLOCKED','FAILED']),
    MOUNT_STARTED:Object.freeze(['MOUNTED','SLOW','DEGRADED','BLOCKED','FAILED']),
    SLOW:Object.freeze(['MOUNTED','DEGRADED','BLOCKED','FAILED']),
    DEGRADED:Object.freeze(['MOUNTED','READY','BLOCKED','FAILED']),
    MOUNTED:Object.freeze(['READY','SLOW','DEGRADED','BLOCKED','FAILED']),
    READY:Object.freeze(['DEGRADED','BLOCKED','FAILED']),
    BLOCKED:Object.freeze([]),
    FAILED:Object.freeze([])
  });
  const REQUIRED_FIELDS=Object.freeze([
    'contract_version',
    'operation_id',
    'monotonic_sequence',
    'owner',
    'source',
    'state',
    'reason_code',
    'observed_at',
    'trust'
  ]);
  const ALLOWED_FIELDS=Object.freeze(REQUIRED_FIELDS.concat(['details']));
  const ID=/^[a-z0-9][a-z0-9._-]{0,95}$/;
  const OPERATION_ID=/^pmp-mount:[a-z0-9][a-z0-9._-]{0,63}:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
  const REASON=/^[A-Z][A-Z0-9_]{0,95}$/;
  const RFC3339_UTC=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;

  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function clone(value){
    return value==null?value:JSON.parse(JSON.stringify(value));
  }
  function canonical(value){
    if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
    if(plain(value))return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  function validTime(value){
    return typeof value==='string'&&RFC3339_UTC.test(value)&&Number.isFinite(Date.parse(value));
  }
  function normalizeList(value){
    return Object.freeze(Array.from(new Set(Array.isArray(value)?value:[])));
  }
  function normalizePolicy(options){
    options=options||{};
    if(!ID.test(String(options.routeAuthority||'')))throw new Error('routeAuthority is required');
    const owners=normalizeList(options.allowedMountOwners);
    if(!owners.length||owners.some(x=>!ID.test(String(x))))throw new Error('allowedMountOwners is required');
    const sources=normalizeList(options.allowedSources||[options.routeAuthority].concat(owners));
    if(sources.some(x=>!ID.test(String(x))))throw new Error('allowedSources is invalid');
    const maxOperations=Number.isInteger(options.maxOperations)&&options.maxOperations>0?options.maxOperations:256;
    const maxEventsPerOperation=Number.isInteger(options.maxEventsPerOperation)&&options.maxEventsPerOperation>0?
      options.maxEventsPerOperation:64;
    return Object.freeze({
      routeAuthority:String(options.routeAuthority),
      allowedMountOwners:owners,
      allowedSources:sources,
      maxOperations,
      maxEventsPerOperation,
      retention:'REJECT_AT_CAPACITY_NO_EVIDENCE_DELETION',
      restart:'REPLAY_VALIDATED_SNAPSHOT_ONLY'
    });
  }
  function validateShape(event){
    if(!plain(event))return 'REJECTED_UNAVAILABLE';
    const keys=Object.keys(event);
    if(keys.some(k=>ALLOWED_FIELDS.indexOf(k)<0))return 'REJECTED_MALFORMED';
    if(REQUIRED_FIELDS.some(k=>!Object.prototype.hasOwnProperty.call(event,k)))return 'REJECTED_MALFORMED';
    if(event.contract_version!==CONTRACT_VERSION)return 'REJECTED_CONTRACT_VERSION';
    if(!OPERATION_ID.test(String(event.operation_id||'')))return 'REJECTED_OPERATION_ID';
    if(!Number.isInteger(event.monotonic_sequence)||event.monotonic_sequence<1)return 'REJECTED_SEQUENCE';
    if(!ID.test(String(event.owner||''))||!ID.test(String(event.source||'')))return 'REJECTED_AUTHORITY';
    if(STATES.indexOf(event.state)<0)return 'REJECTED_STATE';
    if(!REASON.test(String(event.reason_code||'')))return 'REJECTED_REASON_CODE';
    if(!validTime(event.observed_at))return 'REJECTED_TIME';
    if(TRUST_LEVELS.indexOf(event.trust)<0)return 'REJECTED_TRUST';
    if(event.details!==undefined){
      if(!plain(event.details))return 'REJECTED_DETAILS';
      let encoded='';
      try{encoded=canonical(event.details)}catch(_){return 'REJECTED_DETAILS';}
      if(encoded.length>4096||/__proto__|prototype|constructor/.test(encoded))return 'REJECTED_DETAILS';
    }
    return null;
  }
  function authorityCode(policy,event,operation){
    if(event.trust!=='OWNER_ATTESTED')return 'REJECTED_NON_AUTHORITATIVE_TRUST';
    if(policy.allowedSources.indexOf(event.source)<0)return 'REJECTED_SOURCE_AUTHORITY';
    const routeState=event.state==='ROUTE_REQUESTED'||event.state==='OWNER_RESOLVED';
    if(routeState){
      if(event.owner!==policy.routeAuthority||event.source!==policy.routeAuthority)return 'REJECTED_ROUTE_AUTHORITY';
      if(event.state==='OWNER_RESOLVED'){
        const resolved=event.details&&event.details.resolved_owner;
        if(policy.allowedMountOwners.indexOf(resolved)<0)return 'REJECTED_RESOLVED_OWNER';
      }
      return null;
    }
    const resolved=operation&&operation.resolved_owner;
    if(!resolved){
      if((event.state==='BLOCKED'||event.state==='FAILED')&&
          event.owner===policy.routeAuthority&&event.source===policy.routeAuthority)return null;
      return 'REJECTED_OWNER_NOT_RESOLVED';
    }
    if(event.owner!==resolved||event.source!==resolved)return 'REJECTED_MOUNT_OWNER';
    return null;
  }
  function createRegistry(options){
    const policy=normalizePolicy(options);
    const operations=new Map();
    const diagnostics={
      accepted:0,
      duplicates:0,
      rejected:0,
      rejection_counts:{},
      last_rejection:null
    };
    function reject(code,event){
      diagnostics.rejected++;
      diagnostics.rejection_counts[code]=(diagnostics.rejection_counts[code]||0)+1;
      diagnostics.last_rejection={
        code,
        operation_id:event&&event.operation_id||null,
        monotonic_sequence:event&&event.monotonic_sequence||null
      };
      return Object.freeze({accepted:false,mutated:false,code,registry_owner:REGISTRY_OWNER});
    }
    function result(code,event,mutated,state){
      return Object.freeze({
        accepted:true,
        mutated,
        code,
        registry_owner:REGISTRY_OWNER,
        operation_id:event.operation_id,
        monotonic_sequence:event.monotonic_sequence,
        current_state:state
      });
    }
    function apply(input){
      const shapeCode=validateShape(input);
      if(shapeCode)return reject(shapeCode,input);
      const event=clone(input);
      let operation=operations.get(event.operation_id);
      if(!operation){
        if(operations.size>=policy.maxOperations)return reject('REJECTED_RETENTION_CAPACITY',event);
        if(event.monotonic_sequence!==1)return reject('REJECTED_SEQUENCE_START',event);
        if(event.state!=='ROUTE_REQUESTED')return reject('REJECTED_MISSING_OPERATION',event);
        operation={
          operation_id:event.operation_id,
          state:'__START__',
          last_sequence:0,
          last_observed_at:null,
          resolved_owner:null,
          events:[]
        };
      }else{
        if(event.monotonic_sequence===operation.last_sequence){
          const last=operation.events[operation.events.length-1];
          if(canonical(last)===canonical(event)){
            diagnostics.duplicates++;
            return result('DUPLICATE_IGNORED',event,false,operation.state);
          }
          return reject('REJECTED_DUPLICATE_CONFLICT',event);
        }
        if(event.monotonic_sequence<operation.last_sequence)return reject('REJECTED_STALE_SEQUENCE',event);
        if(event.monotonic_sequence!==operation.last_sequence+1)return reject('REJECTED_SEQUENCE_GAP',event);
        if(Date.parse(event.observed_at)<Date.parse(operation.last_observed_at))return reject('REJECTED_TIME_REGRESSION',event);
      }
      if(operation.events.length>=policy.maxEventsPerOperation)return reject('REJECTED_EVENT_RETENTION_CAPACITY',event);
      const allowed=TRANSITIONS[operation.state]||[];
      if(allowed.indexOf(event.state)<0)return reject('REJECTED_INVALID_TRANSITION',event);
      const authority=authorityCode(policy,event,operation);
      if(authority)return reject(authority,event);
      if(event.state==='OWNER_RESOLVED')operation.resolved_owner=event.details.resolved_owner;
      operation.events.push(event);
      operation.state=event.state;
      operation.last_sequence=event.monotonic_sequence;
      operation.last_observed_at=event.observed_at;
      if(!operations.has(event.operation_id))operations.set(event.operation_id,operation);
      diagnostics.accepted++;
      return result('ACCEPTED',event,true,operation.state);
    }
    function snapshot(){
      return clone({
        type:'PMP_MOUNT_LIFECYCLE_REGISTRY_SNAPSHOT_V1',
        contract_version:CONTRACT_VERSION,
        implementation_version:VERSION,
        registry_owner:REGISTRY_OWNER,
        policy,
        operations:Array.from(operations.values()),
        diagnostics,
        storage_effects:'NONE_IN_P5_U2_PURE_CONTRACT',
        terminal_states:TERMINAL_STATES
      });
    }
    function operation(id){
      return clone(operations.get(id)||null);
    }
    return Object.freeze({
      version:VERSION,
      contractVersion:CONTRACT_VERSION,
      registryOwner:REGISTRY_OWNER,
      policy,
      apply,
      snapshot,
      operation
    });
  }
  function restoreSnapshot(snapshot,options){
    if(!plain(snapshot)||snapshot.type!=='PMP_MOUNT_LIFECYCLE_REGISTRY_SNAPSHOT_V1'||
       snapshot.contract_version!==CONTRACT_VERSION||!Array.isArray(snapshot.operations)){
      return Object.freeze({ok:false,code:'RESTORE_REJECTED_MALFORMED',registry:null});
    }
    let registry;
    try{registry=createRegistry(options);}catch(_){
      return Object.freeze({ok:false,code:'RESTORE_REJECTED_POLICY',registry:null});
    }
    for(const operation of snapshot.operations){
      if(!plain(operation)||!Array.isArray(operation.events)){
        return Object.freeze({ok:false,code:'RESTORE_REJECTED_OPERATION',registry:null});
      }
      for(const event of operation.events){
        const outcome=registry.apply(event);
        if(!outcome.accepted||outcome.code!=='ACCEPTED'){
          return Object.freeze({ok:false,code:'RESTORE_REJECTED_EVENT',registry:null});
        }
      }
    }
    return Object.freeze({ok:true,code:'RESTORE_ACCEPTED',registry});
  }
  function createLegacyAtlasFacade(legacyApi,lifecycleRegistry){
    if(!legacyApi||typeof legacyApi.registry!=='function'||typeof legacyApi.snapshot!=='function'||
       typeof legacyApi.scan!=='function')throw new Error('legacy atlas API is incomplete');
    if(!lifecycleRegistry||typeof lifecycleRegistry.snapshot!=='function')throw new Error('lifecycle registry is incomplete');
    return Object.freeze({
      version:legacyApi.version||null,
      legacyVersion:legacyApi.version||null,
      compatibilityMode:'ADDITIVE_NO_AUTOMATIC_SCAN_NO_STORAGE_MIGRATION',
      registry:legacyApi.registry.bind(legacyApi),
      snapshot:legacyApi.snapshot.bind(legacyApi),
      scan:legacyApi.scan.bind(legacyApi),
      atlasBuckets:legacyApi.atlasBuckets||null,
      keys:legacyApi.keys||null,
      lifecycleContractVersion:CONTRACT_VERSION,
      lifecycleRegistryOwner:REGISTRY_OWNER,
      lifecycleSnapshot:lifecycleRegistry.snapshot
    });
  }

  return Object.freeze({
    version:VERSION,
    contractVersion:CONTRACT_VERSION,
    registryOwner:REGISTRY_OWNER,
    states:STATES,
    activeStates:ACTIVE_STATES,
    failureStates:FAILURE_STATES,
    terminalStates:TERMINAL_STATES,
    trustLevels:TRUST_LEVELS,
    transitions:TRANSITIONS,
    requiredFields:REQUIRED_FIELDS,
    createRegistry,
    restoreSnapshot,
    createLegacyAtlasFacade
  });
});
