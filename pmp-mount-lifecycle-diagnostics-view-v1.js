(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else if(root&&!root.PMPMountLifecycleDiagnosticsViewV1)root.PMPMountLifecycleDiagnosticsViewV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const TYPE='PMP_MOUNT_LIFECYCLE_DIAGNOSTICS_VIEW_V1';
  const MAX_VISIBLE_OPERATIONS=64;

  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function text(value,max){
    return typeof value==='string'?value.slice(0,max):null;
  }
  function dependencies(value){
    const input=plain(value)?value:{};
    return Object.freeze({
      contract_available:input.contract_available===true,
      legacy_atlas_available:input.legacy_atlas_available===true
    });
  }
  function sideEffects(){
    return Object.freeze({
      lifecycle_events_applied:0,
      registry_mutations:0,
      legacy_atlas_calls:0,
      mounts:0,
      repairs:0,
      route_assignments:0,
      storage_migrations:0,
      persisted_user_data_writes:0
    });
  }
  function unavailable(code,status){
    return Object.freeze({
      type:TYPE,
      version:VERSION,
      status:code,
      available:false,
      registry_owner:'mount_registry_owner',
      contract_version:null,
      dependencies:dependencies(status),
      operation_count:0,
      visible_operation_count:0,
      operations:Object.freeze([]),
      rejections:Object.freeze({total:0,counts:Object.freeze({}),last:null}),
      disclosure:Object.freeze({
        event_details_exposed:false,
        raw_event_payloads_exposed:false,
        maximum_visible_operations:MAX_VISIBLE_OPERATIONS
      }),
      side_effects:sideEffects()
    });
  }
  function rejectionView(input){
    const value=plain(input)?input:{};
    const rawCounts=plain(value.rejection_counts)?value.rejection_counts:{};
    const counts={};
    Object.keys(rawCounts).sort().forEach(key=>{
      if(/^[A-Z][A-Z0-9_]{0,95}$/.test(key)&&Number.isInteger(rawCounts[key])&&rawCounts[key]>=0){
        counts[key]=rawCounts[key];
      }
    });
    const last=plain(value.last_rejection)?Object.freeze({
      code:text(value.last_rejection.code,96),
      operation_present:typeof value.last_rejection.operation_id==='string',
      monotonic_sequence:Number.isInteger(value.last_rejection.monotonic_sequence)?
        value.last_rejection.monotonic_sequence:null
    }):null;
    return Object.freeze({
      total:Number.isInteger(value.rejected)&&value.rejected>=0?value.rejected:0,
      counts:Object.freeze(counts),
      last
    });
  }
  function operationView(input){
    if(!plain(input)||typeof input.operation_id!=='string'||typeof input.state!=='string'||
       !Number.isInteger(input.last_sequence)||!Array.isArray(input.events))return null;
    return Object.freeze({
      operation_id:text(input.operation_id,192),
      state:text(input.state,32),
      last_sequence:input.last_sequence,
      last_observed_at:text(input.last_observed_at,32),
      resolved_owner:text(input.resolved_owner,96),
      event_count:input.events.length,
      terminal:input.state==='BLOCKED'||input.state==='FAILED'
    });
  }
  function read(runtime){
    if(!runtime||typeof runtime!=='object'||runtime.available!==true||
       typeof runtime.lifecycleSnapshot!=='function'){
      return unavailable('LIFECYCLE_RUNTIME_UNAVAILABLE',runtime&&runtime.dependencyStatus);
    }
    let snapshot;
    try{snapshot=runtime.lifecycleSnapshot()}catch(_){
      return unavailable('LIFECYCLE_SNAPSHOT_ERROR',runtime.dependencyStatus);
    }
    if(!plain(snapshot)||snapshot.type!=='PMP_MOUNT_LIFECYCLE_REGISTRY_SNAPSHOT_V1'||
       !Array.isArray(snapshot.operations)||!plain(snapshot.policy)){
      return unavailable('LIFECYCLE_SNAPSHOT_MALFORMED',runtime.dependencyStatus);
    }
    const operations=snapshot.operations.map(operationView);
    if(operations.some(value=>value===null)){
      return unavailable('LIFECYCLE_SNAPSHOT_MALFORMED',runtime.dependencyStatus);
    }
    operations.sort((a,b)=>a.operation_id.localeCompare(b.operation_id));
    const visible=operations.slice(0,MAX_VISIBLE_OPERATIONS);
    return Object.freeze({
      type:TYPE,
      version:VERSION,
      status:operations.length?'READY_WITH_OPERATIONS':'READY_EMPTY',
      available:true,
      registry_owner:text(snapshot.registry_owner,96),
      contract_version:text(snapshot.contract_version,96),
      dependencies:dependencies(runtime.dependencyStatus),
      policy:Object.freeze({
        route_authority:text(snapshot.policy.routeAuthority,96),
        max_operations:Number.isInteger(snapshot.policy.maxOperations)?snapshot.policy.maxOperations:null,
        max_events_per_operation:Number.isInteger(snapshot.policy.maxEventsPerOperation)?
          snapshot.policy.maxEventsPerOperation:null,
        retention:text(snapshot.policy.retention,96),
        restart:text(snapshot.policy.restart,96)
      }),
      operation_count:operations.length,
      visible_operation_count:visible.length,
      operations:Object.freeze(visible),
      rejections:rejectionView(snapshot.diagnostics),
      disclosure:Object.freeze({
        event_details_exposed:false,
        raw_event_payloads_exposed:false,
        maximum_visible_operations:MAX_VISIBLE_OPERATIONS,
        operations_truncated:operations.length>MAX_VISIBLE_OPERATIONS
      }),
      side_effects:sideEffects()
    });
  }

  return Object.freeze({
    version:VERSION,
    type:TYPE,
    maximumVisibleOperations:MAX_VISIBLE_OPERATIONS,
    read
  });
});
