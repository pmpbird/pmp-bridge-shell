(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else if(root&&!root.PMPSectionOwnerDiagnosticsViewV1)root.PMPSectionOwnerDiagnosticsViewV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const TYPE='PMP_SECTION_OWNER_DIAGNOSTICS_VIEW_V1';
  const MAX_VISIBLE_EVENTS=128;
  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function text(value,max){return typeof value==='string'?value.slice(0,max):null}
  function sideEffects(){
    return Object.freeze({
      owner_events_applied:0,
      registry_mutations:0,
      mounts:0,
      repairs:0,
      route_assignments:0,
      bank_mutations:0,
      storage_migrations:0,
      persisted_user_data_writes:0
    });
  }
  function unavailable(code){
    return Object.freeze({
      type:TYPE,version:VERSION,status:code,available:false,
      registry_owner:'mount_registry_owner',registered_count:0,pending_growth_count:0,
      visible_event_count:0,registered:Object.freeze([]),
      pending_growth:Object.freeze([]),events:Object.freeze([]),
      disclosure:Object.freeze({
        capability_ids_exposed:false,raw_authority_payloads_exposed:false,
        source_versions_exposed:false,maximum_visible_events:MAX_VISIBLE_EVENTS
      }),
      side_effects:sideEffects()
    });
  }
  function ownerRow(row,pending){
    if(!plain(row)||typeof row.owner_id!=='string'||typeof row.section_id!=='string')return null;
    return Object.freeze({
      owner_id:text(row.owner_id,128),section_id:text(row.section_id,128),
      status:text(row.status,64),
      authority_granted:pending?false:null
    });
  }
  function eventRow(row){
    if(!plain(row)||typeof row.operation_id!=='string'||typeof row.event_id!=='string'||
       typeof row.owner_id!=='string'||typeof row.section_id!=='string'||
       typeof row.event_type!=='string')return null;
    return Object.freeze({
      operation_id:text(row.operation_id,128),
      event_id:text(row.event_id,128),
      owner_id:text(row.owner_id,128),
      section_id:text(row.section_id,128),
      event_type:text(row.event_type,64),
      result:text(row.result,96),
      capability_present:row.capability_present===true,
      authority_granted:false
    });
  }
  function read(runtime){
    if(!runtime||runtime.available!==true||typeof runtime.snapshot!=='function'){
      return unavailable('SECTION_OWNER_RUNTIME_UNAVAILABLE');
    }
    let snapshot;
    try{snapshot=runtime.snapshot()}catch(_){
      return unavailable('SECTION_OWNER_SNAPSHOT_ERROR');
    }
    if(!plain(snapshot)||snapshot.type!=='PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1'||
       !Array.isArray(snapshot.registered)||!Array.isArray(snapshot.pending_growth)||
       !Array.isArray(snapshot.diagnostics)){
      return unavailable('SECTION_OWNER_SNAPSHOT_MALFORMED');
    }
    const registered=snapshot.registered.map(row=>ownerRow(row,false));
    const pending=snapshot.pending_growth.map(row=>ownerRow(row,true));
    const events=snapshot.diagnostics.map(eventRow);
    if(registered.concat(pending,events).some(row=>row===null)){
      return unavailable('SECTION_OWNER_SNAPSHOT_MALFORMED');
    }
    registered.sort((a,b)=>a.owner_id.localeCompare(b.owner_id));
    pending.sort((a,b)=>a.owner_id.localeCompare(b.owner_id));
    const visible=events.slice(-MAX_VISIBLE_EVENTS);
    return Object.freeze({
      type:TYPE,version:VERSION,
      status:pending.length?'READY_WITH_PENDING_GROWTH':(
        registered.length?'READY_WITH_REGISTERED_OWNERS':'READY_EMPTY'
      ),
      available:true,
      registry_owner:text(snapshot.registry_owner,96),
      event_version:text(snapshot.event_version,96),
      capability_contract_version:text(snapshot.capability_contract_version,96),
      registered_count:registered.length,
      pending_growth_count:pending.length,
      visible_event_count:visible.length,
      registered:Object.freeze(registered),
      pending_growth:Object.freeze(pending),
      events:Object.freeze(visible),
      counts:Object.freeze({
        accepted:Number.isInteger(snapshot.counts&&snapshot.counts.accepted)?
          snapshot.counts.accepted:0,
        rejected:Number.isInteger(snapshot.counts&&snapshot.counts.rejected)?
          snapshot.counts.rejected:0,
        duplicates:Number.isInteger(snapshot.counts&&snapshot.counts.duplicates)?
          snapshot.counts.duplicates:0
      }),
      disclosure:Object.freeze({
        capability_ids_exposed:false,
        raw_authority_payloads_exposed:false,
        source_versions_exposed:false,
        maximum_visible_events:MAX_VISIBLE_EVENTS,
        events_truncated:events.length>MAX_VISIBLE_EVENTS
      }),
      side_effects:sideEffects()
    });
  }
  return Object.freeze({
    type:TYPE,version:VERSION,maximumVisibleEvents:MAX_VISIBLE_EVENTS,read
  });
});
