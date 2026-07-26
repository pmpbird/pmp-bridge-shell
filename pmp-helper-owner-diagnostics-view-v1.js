(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else if(root&&!root.PMPHelperOwnerDiagnosticsViewV1)root.PMPHelperOwnerDiagnosticsViewV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const VERSION='1.0.0';
  const TYPE='PMP_HELPER_OWNER_DIAGNOSTICS_VIEW_V1';
  const MAX_VISIBLE_EVENTS=128;
  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function text(value,max){return typeof value==='string'?value.slice(0,max):null}
  function sideEffects(){
    return Object.freeze({
      helper_events_applied:0,section_owner_events_applied:0,
      registry_mutations:0,mounts:0,repairs:0,route_assignments:0,
      bank_mutations:0,storage_migrations:0,persisted_user_data_writes:0,
      helper_behavior_activations:0,production_activations:0
    });
  }
  function unavailable(code){
    return Object.freeze({
      type:TYPE,version:VERSION,status:code,available:false,
      registered_count:0,pending_growth_count:0,revoked_count:0,
      held_declared_count:0,unknown_source_count:0,visible_event_count:0,
      registered:Object.freeze([]),pending_growth:Object.freeze([]),
      revoked:Object.freeze([]),held_declared:Object.freeze([]),
      unknown_sources:Object.freeze([]),events:Object.freeze([]),
      disclosure:Object.freeze({
        capability_ids_exposed:false,helper_source_hashes_exposed:false,
        raw_authority_payloads_exposed:false,source_versions_exposed:false,
        maximum_visible_events:MAX_VISIBLE_EVENTS
      }),
      side_effects:sideEffects()
    });
  }
  function helperRow(row,pending){
    if(!plain(row)||typeof row.helper_id!=='string'||
       typeof row.canonical_owner_id!=='string'||typeof row.section_id!=='string'||
       typeof row.slot!=='string')return null;
    return Object.freeze({
      helper_id:text(row.helper_id,192),
      canonical_owner_id:text(row.canonical_owner_id,128),
      section_id:text(row.section_id,128),slot:text(row.slot,192),
      status:text(row.status,96),
      guard_requirement_count:Number.isInteger(row.guard_requirement_count)?
        row.guard_requirement_count:0,
      authority_granted:false,behavior_authorized:false,
      growth_pending:pending===true
    });
  }
  function eventRow(row){
    if(!plain(row)||typeof row.operation_id!=='string'||
       typeof row.event_id!=='string'||typeof row.helper_id!=='string'||
       typeof row.canonical_owner_id!=='string'||typeof row.section_id!=='string'||
       typeof row.slot!=='string'||typeof row.event_type!=='string')return null;
    return Object.freeze({
      operation_id:text(row.operation_id,192),event_id:text(row.event_id,192),
      helper_id:text(row.helper_id,192),
      canonical_owner_id:text(row.canonical_owner_id,128),
      section_id:text(row.section_id,128),slot:text(row.slot,192),
      event_type:text(row.event_type,96),result:text(row.result,128),
      capability_present:row.capability_present===true,
      authority_granted:false,behavior_authorized:false
    });
  }
  function read(runtime){
    if(!runtime||runtime.available!==true||typeof runtime.snapshot!=='function'){
      return unavailable('HELPER_OWNER_RUNTIME_UNAVAILABLE');
    }
    let snapshot;
    try{snapshot=runtime.snapshot()}catch(_){
      return unavailable('HELPER_OWNER_SNAPSHOT_ERROR');
    }
    if(!plain(snapshot)||snapshot.type!=='PMP_HELPER_OWNER_SNAPSHOT_V1'||
       !Array.isArray(snapshot.registered)||!Array.isArray(snapshot.pending_growth)||
       !plain(snapshot.revoked)||!Array.isArray(snapshot.held_declared)||
       !Array.isArray(snapshot.unknown_sources)||!Array.isArray(snapshot.diagnostics)){
      return unavailable('HELPER_OWNER_SNAPSHOT_MALFORMED');
    }
    const registered=snapshot.registered.map(row=>helperRow(row,false));
    const pending=snapshot.pending_growth.map(row=>helperRow(row,true));
    const held=snapshot.held_declared.map(row=>{
      if(!plain(row)||typeof row.helper_id!=='string'||typeof row.disposition!=='string')return null;
      return Object.freeze({
        helper_id:text(row.helper_id,192),status:text(row.disposition,96),
        authority_granted:false,behavior_authorized:false
      });
    });
    const unknown=snapshot.unknown_sources.map(row=>{
      if(!plain(row)||typeof row.file!=='string'||typeof row.status!=='string')return null;
      return Object.freeze({
        file:text(row.file,256),status:text(row.status,96),
        authority_granted:false,behavior_authorized:false
      });
    });
    const events=snapshot.diagnostics.map(eventRow);
    if(registered.concat(pending,held,unknown,events).some(row=>row===null)){
      return unavailable('HELPER_OWNER_SNAPSHOT_MALFORMED');
    }
    registered.sort((a,b)=>a.helper_id.localeCompare(b.helper_id));
    pending.sort((a,b)=>a.helper_id.localeCompare(b.helper_id));
    held.sort((a,b)=>a.helper_id.localeCompare(b.helper_id));
    unknown.sort((a,b)=>a.file.localeCompare(b.file));
    const revoked=Object.keys(snapshot.revoked).sort().map(helperId=>Object.freeze({
      helper_id:text(helperId,192),status:'REVOKED_STATIC_EVENT_ONLY',
      authority_granted:false,behavior_authorized:false
    }));
    const visible=events.slice(-MAX_VISIBLE_EVENTS);
    return Object.freeze({
      type:TYPE,version:VERSION,
      status:pending.length?'READY_WITH_PENDING_GROWTH':(
        registered.length?'READY_WITH_REGISTERED_HELPERS':'READY_EMPTY'
      ),
      available:true,
      event_version:text(snapshot.event_version,96),
      journal_version:text(snapshot.journal_version,96),
      capability_contract_version:text(snapshot.capability_contract_version,96),
      registered_count:registered.length,pending_growth_count:pending.length,
      revoked_count:revoked.length,held_declared_count:held.length,
      unknown_source_count:unknown.length,visible_event_count:visible.length,
      registered:Object.freeze(registered),pending_growth:Object.freeze(pending),
      revoked:Object.freeze(revoked),held_declared:Object.freeze(held),
      unknown_sources:Object.freeze(unknown),events:Object.freeze(visible),
      counts:Object.freeze({
        eligible_static:Number.isInteger(snapshot.counts&&snapshot.counts.eligible_static)?
          snapshot.counts.eligible_static:0,
        accepted:Number.isInteger(snapshot.counts&&snapshot.counts.accepted)?
          snapshot.counts.accepted:0,
        rejected:Number.isInteger(snapshot.counts&&snapshot.counts.rejected)?
          snapshot.counts.rejected:0,
        duplicates:Number.isInteger(snapshot.counts&&snapshot.counts.duplicates)?
          snapshot.counts.duplicates:0
      }),
      disclosure:Object.freeze({
        capability_ids_exposed:false,helper_source_hashes_exposed:false,
        raw_authority_payloads_exposed:false,source_versions_exposed:false,
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
