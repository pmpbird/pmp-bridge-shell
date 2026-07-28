(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){
    if(!root.PMPHelperOwnerIntegrationV1)root.PMPHelperOwnerIntegrationV1=api;
    api.install(root);
  }
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const TYPE='PMP_HELPER_OWNER_INTEGRATION_V1';
  const SNAPSHOT_TYPE='PMP_HELPER_OWNER_SNAPSHOT_V1';
  const EVENT_VERSION='PMP_HELPER_REGISTRATION_EVENT_V1';
  const JOURNAL_VERSION='PMP_HELPER_REGISTRATION_JOURNAL_V1';
  const CAPABILITY_VERSION='PMP_HELPER_CAPABILITY_CONTRACT_V1';
  const ROOT_AUTHORITY='app_orchestrator_owner';
  const GROWTH_OBSERVER='diagnostics_owner';
  const ID=/^[a-z0-9][a-z0-9._:-]{0,191}$/;
  const TIME=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
  const DIGEST=/^[0-9a-f]{64}$/;
  const EVENT_TYPES=Object.freeze([
    'HELPER_REGISTERED','HELPER_UPDATED','HELPER_REVOKED',
    'HELPER_REMOVED','HELPER_GROWTH_OBSERVED'
  ]);
  const REQUIRED_FIELDS=Object.freeze([
    'event_version','event_id','operation_id','monotonic_sequence','registry_epoch',
    'event_type','helper_id','helper_source_sha256','canonical_owner_id','section_id',
    'slot','source_version','growth_source','observed_at','previous_event_digest',
    'authority'
  ]);
  const AUTHORITY_FIELDS=Object.freeze([
    'contract_version','authorizer','capability_id','decision','action','revocation_epoch'
  ]);
  const HELPER_SPECS=Object.freeze([
    ['pass2_atlas_adapter','b2782a45c85c5127d8676c909adb6a7fb5f33e0942da6e12add0135380fd4eda','mount_registry_owner','mount_registry','atlas_runtime_adapter','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['authority_rules','578f966d6fd801806684739836d8eb690b2a92bfe2e2a8ade5fa7d26427c0591','app_orchestrator_owner','app_orchestrator','authority_rules_diagnostics','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['active_bug_contract','0dbcf9473e7ffcf1654412c51e981478429529f911a7826dd2d06ed667b73d4b','bank_screen_owner','bank','bug_contract_diagnostics','none','ELIGIBLE_STATIC_CAPABILITY',4],
    ['bug_watch_passive_capture','adcda055d9e3573c545072c5d5fc294a13ff3c1d43cf3cffa06b2ebba83b4bfc','bank_screen_owner','bank','bug_watch_capture','none','ELIGIBLE_STATIC_CAPABILITY',4],
    ['safe_writer_current_return_fix','685afcd60d5bb997af71f6317a090f4a9e4e53adca5aa103c6edaf8be85be8c3','reload_current_owner','current_reload','current_return_fix','none','HELD_CONTRACT_CONFLICT',0],
    ['phase8_atlas_marker','78fddb8c97b92e8f52829920fd4537c1920bbf2a0a2f526cf4e3c12cccec242e','mount_registry_owner','mount_registry','atlas_marker_diagnostics','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['pass1r_version_aligner','cef6f909293a4cb501a0421ec4e1485623f0d6e4b98bee14cf9e6a9edf247cd6','diagnostics_owner','diagnostics','version_alignment','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['pass1w_live_proof_reader','87b010bffd893d6594cf0a247ecaa2bc780e0b8ac1309af595c81989cc077ce4','diagnostics_owner','diagnostics','live_proof_reader','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['active_path_discovery_machine','5575f2826ba175c76ccdae79ac88d2b197d91b28007e58f46bb36ebf32fe5909','app_orchestrator_owner','app_orchestrator','active_path_diagnostics','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['active_path_discovery_machine_v2','1e6f47e85333a09263dbc9f5918a378ee545a9866e830ef82b1104de322151f7','app_orchestrator_owner','app_orchestrator','active_path_diagnostics_v2','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['continuous_run_bank_order_frame_loader','49be28248ded163733367500941dd87f85b38967d0d984592e0f7e5995cf68a3','continuous_run_level_owner','continuous_run','continuous_run_frame_loader','continuous_run_frame_loader','ELIGIBLE_STATIC_CAPABILITY',0],
    ['active_path_discovery_zip_export','1030420ddfae52df47a1b12824e23a1af7ed6d49946bb4e054e0d1b04c4e12f9','app_orchestrator_owner','app_orchestrator','active_path_discovery_export_menu','none','ELIGIBLE_STATIC_CAPABILITY',0],
    ['legacy_helper_registry','299e607133df55ed74f7bade798cb96e76566cefd3fd73b87da63f2b64650dbf','app_orchestrator_owner','app_orchestrator','legacy_helper_registry_snapshot','none','HELD_LEGACY',0],
    ['pass8_helper_rules_certification','e3c029ebeaf82184779b2c4515321dea3edb7942c4936382cc7c15557c4787c9','app_orchestrator_owner','app_orchestrator','pass8_helper_rules_certification_gate','none','ELIGIBLE_STATIC_CAPABILITY',0]
  ].map(row=>Object.freeze({
    helper_id:row[0],helper_source_sha256:row[1],
    canonical_owner_id:row[2],section_id:row[3],slot:row[4],
    growth_source:row[5],disposition:row[6],guard_requirement_count:row[7]
  })));
  const UNKNOWN_SOURCES=Object.freeze([
    'pmp-continuous-run-helper-conflict-blocker-v1.js',
    'pmp-helper-bank-live-inspector-v1.js',
    'pmp-helper-bank-live-inspector-v2.js',
    'pmp-helper-problem-display-sync-v1.js',
    'pmp-helper-problem-memory-v1.js',
    'pmp-helper-problem-type-only-v1.js',
    'pmp-helper-problem-type-seeds-v1.js',
    'pmp-helper-symptom-watcher-v1.js',
    'pmp-p15-helper-tidy-v1.js'
  ]);

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
  function utf8(value){
    const out=[];
    for(let index=0;index<value.length;index++){
      let point=value.charCodeAt(index);
      if(point>=0xd800&&point<=0xdbff&&index+1<value.length){
        const low=value.charCodeAt(index+1);
        if(low>=0xdc00&&low<=0xdfff){
          point=0x10000+((point-0xd800)<<10)+(low-0xdc00);
          index++;
        }
      }
      if(point<0x80)out.push(point);
      else if(point<0x800)out.push(0xc0|(point>>6),0x80|(point&63));
      else if(point<0x10000)out.push(0xe0|(point>>12),0x80|((point>>6)&63),0x80|(point&63));
      else out.push(0xf0|(point>>18),0x80|((point>>12)&63),0x80|((point>>6)&63),0x80|(point&63));
    }
    return out;
  }
  function rotate(value,count){return (value>>>count)|(value<<(32-count))}
  function sha256Text(value){
    const constants=[
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    ];
    const bytes=utf8(value),bitLength=bytes.length*8;
    bytes.push(0x80);
    while(bytes.length%64!==56)bytes.push(0);
    const high=Math.floor(bitLength/0x100000000),low=bitLength>>>0;
    for(let shift=24;shift>=0;shift-=8)bytes.push((high>>>shift)&255);
    for(let shift=24;shift>=0;shift-=8)bytes.push((low>>>shift)&255);
    const hash=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    for(let offset=0;offset<bytes.length;offset+=64){
      const words=new Array(64);
      for(let index=0;index<16;index++){
        const at=offset+index*4;
        words[index]=((bytes[at]<<24)|(bytes[at+1]<<16)|(bytes[at+2]<<8)|bytes[at+3])>>>0;
      }
      for(let index=16;index<64;index++){
        const a=words[index-15],b=words[index-2];
        const s0=(rotate(a,7)^rotate(a,18)^(a>>>3))>>>0;
        const s1=(rotate(b,17)^rotate(b,19)^(b>>>10))>>>0;
        words[index]=(words[index-16]+s0+words[index-7]+s1)>>>0;
      }
      let [a,b,c,d,e,f,g,h]=hash;
      for(let index=0;index<64;index++){
        const s1=(rotate(e,6)^rotate(e,11)^rotate(e,25))>>>0;
        const choice=((e&f)^((~e)&g))>>>0;
        const first=(h+s1+choice+constants[index]+words[index])>>>0;
        const s0=(rotate(a,2)^rotate(a,13)^rotate(a,22))>>>0;
        const majority=((a&b)^(a&c)^(b&c))>>>0;
        const second=(s0+majority)>>>0;
        h=g;g=f;f=e;e=(d+first)>>>0;d=c;c=b;b=a;a=(first+second)>>>0;
      }
      const values=[a,b,c,d,e,f,g,h];
      for(let index=0;index<8;index++)hash[index]=(hash[index]+values[index])>>>0;
    }
    return hash.map(value=>value.toString(16).padStart(8,'0')).join('');
  }
  function digest(value){return sha256Text(canonical(value))}
  function actionFor(type){
    return {
      HELPER_REGISTERED:'register_helper',
      HELPER_UPDATED:'update_helper',
      HELPER_REVOKED:'revoke_helper',
      HELPER_REMOVED:'remove_helper',
      HELPER_GROWTH_OBSERVED:'observe_helper_growth'
    }[type];
  }
  function sideEffects(){
    return Object.freeze({
      section_owner_events:0,mount_lifecycle_events:0,legacy_atlas_calls:0,
      mounts:0,repairs:0,route_assignments:0,bank_mutations:0,
      storage_migrations:0,persisted_user_data_writes:0,
      helper_behavior_activations:0,production_activations:0
    });
  }
  function dependencyStatus(sectionRuntime){
    return Object.freeze({
      section_owner_runtime_available:!!(
        sectionRuntime&&sectionRuntime.available===true&&
        typeof sectionRuntime.snapshot==='function'
      ),
      section_owner_registry:'mount_registry_owner'
    });
  }
  function sectionOwnerPresent(sectionRuntime,ownerId,sectionId){
    try{
      const snapshot=sectionRuntime.snapshot();
      return !!(
        plain(snapshot)&&snapshot.type==='PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1'&&
        Array.isArray(snapshot.registered)&&snapshot.registered.some(row=>
          plain(row)&&row.owner_id===ownerId&&row.section_id===sectionId&&
          row.status==='REGISTERED_CAPABILITY_BOUND'
        )
      );
    }catch(_){return false}
  }
  function shape(event){
    if(!plain(event))return 'REJECTED_MALFORMED_EVENT';
    if(Object.keys(event).length!==REQUIRED_FIELDS.length||
       REQUIRED_FIELDS.some(key=>!Object.prototype.hasOwnProperty.call(event,key))){
      return 'REJECTED_MALFORMED_EVENT';
    }
    if(event.event_version!==EVENT_VERSION)return 'REJECTED_EVENT_VERSION';
    for(const key of ['event_id','operation_id','helper_id','canonical_owner_id','section_id','slot','source_version']){
      if(!ID.test(String(event[key]||'')))return 'REJECTED_IDENTITY';
    }
    if(!Number.isInteger(event.monotonic_sequence)||event.monotonic_sequence<1)return 'REJECTED_SEQUENCE';
    if(!Number.isInteger(event.registry_epoch)||event.registry_epoch<1)return 'REJECTED_EPOCH';
    if(EVENT_TYPES.indexOf(event.event_type)<0)return 'REJECTED_EVENT_TYPE';
    if(!DIGEST.test(String(event.helper_source_sha256||'')))return 'REJECTED_SOURCE_HASH';
    if(!TIME.test(String(event.observed_at||'')))return 'REJECTED_TIME';
    if(event.previous_event_digest!==null&&!DIGEST.test(String(event.previous_event_digest))){
      return 'REJECTED_PREVIOUS_DIGEST';
    }
    if(!plain(event.authority)||Object.keys(event.authority).length!==AUTHORITY_FIELDS.length||
       AUTHORITY_FIELDS.some(key=>!Object.prototype.hasOwnProperty.call(event.authority,key))){
      return 'REJECTED_AUTHORITY_SHAPE';
    }
    return null;
  }
  function create(sectionRuntime){
    const dependencies=dependencyStatus(sectionRuntime);
    const specs=new Map(HELPER_SPECS.map(row=>[row.helper_id,row]));
    const registered=new Map(),pending=new Map(),revoked=new Map();
    const eventsById=new Map(),operations=new Set();
    const journal=[],diagnostics=[],rejectionCounts={};
    let rejected=0,duplicates=0,last=null;
    function deny(code,event){
      rejected++;
      rejectionCounts[code]=(rejectionCounts[code]||0)+1;
      return Object.freeze({
        accepted:false,mutated:false,authority_granted:false,behavior_authorized:false,
        code,event_id:event&&event.event_id||null,
        operation_id:event&&event.operation_id||null
      });
    }
    function accept(code,event,mutated){
      return Object.freeze({
        accepted:true,mutated,authority_granted:false,behavior_authorized:false,
        code,event_id:event.event_id,operation_id:event.operation_id
      });
    }
    function applyHelperEvent(input){
      const invalid=shape(input);
      if(invalid)return deny(invalid,input);
      const event=clone(input),eventHash=digest(event);
      if(eventsById.has(event.event_id)){
        if(eventsById.get(event.event_id)===eventHash){
          duplicates++;
          return accept('DUPLICATE_EVENT_IGNORED',event,false);
        }
        return deny('REJECTED_DUPLICATE_EVENT_CONFLICT',event);
      }
      if(operations.has(event.operation_id))return deny('REJECTED_DUPLICATE_OPERATION',event);
      const spec=specs.get(event.helper_id);
      if(!spec)return deny('REJECTED_UNKNOWN_HELPER',event);
      if(spec.disposition==='HELD_LEGACY')return deny('REJECTED_LEGACY_HELPER_HELD',event);
      if(spec.disposition!=='ELIGIBLE_STATIC_CAPABILITY'){
        return deny('REJECTED_HELPER_CONFLICT_HELD',event);
      }
      if(event.helper_source_sha256!==spec.helper_source_sha256)return deny('REJECTED_SOURCE_HASH',event);
      if(event.canonical_owner_id!==spec.canonical_owner_id||event.section_id!==spec.section_id){
        return deny('REJECTED_OWNER_BINDING',event);
      }
      if(event.slot!==spec.slot)return deny('REJECTED_SLOT_BINDING',event);
      if(event.growth_source!==spec.growth_source)return deny('REJECTED_GROWTH_SOURCE',event);
      if(!dependencies.section_owner_runtime_available){
        return deny('REJECTED_SECTION_OWNER_RUNTIME_UNAVAILABLE',event);
      }
      if(!sectionOwnerPresent(sectionRuntime,event.canonical_owner_id,event.section_id)){
        return deny('REJECTED_SECTION_OWNER_NOT_REGISTERED',event);
      }
      const growth=event.event_type==='HELPER_GROWTH_OBSERVED';
      const authority=event.authority;
      if(authority.contract_version!==CAPABILITY_VERSION||
         authority.capability_id!=='cap:p8u2:'+event.helper_id||
         authority.action!==actionFor(event.event_type)){
        return deny('REJECTED_REGISTRATION_AUTHORITY',event);
      }
      if(growth){
        if(spec.growth_source==='none'||authority.authorizer!==GROWTH_OBSERVER||
           authority.decision!=='OBSERVED_ONLY_NO_AUTHORITY'||authority.revocation_epoch!==0){
          return deny('REJECTED_GROWTH_OBSERVER_AUTHORITY',event);
        }
      }else if(authority.authorizer!==ROOT_AUTHORITY||
                authority.decision!=='AUTHORIZED_STATIC_EVENT'){
        return deny('REJECTED_REGISTRATION_AUTHORITY',event);
      }
      const priorEpoch=revoked.get(event.helper_id)||0;
      if(!growth&&event.event_type!=='HELPER_REVOKED'&&authority.revocation_epoch!==priorEpoch){
        return deny('REJECTED_REVOCATION_EPOCH',event);
      }
      if(last===null){
        if(event.monotonic_sequence!==1||event.registry_epoch!==1||
           event.previous_event_digest!==null)return deny('REJECTED_JOURNAL_START',event);
      }else{
        if(event.monotonic_sequence<=last.monotonic_sequence)return deny('REJECTED_STALE_SEQUENCE',event);
        if(event.monotonic_sequence!==last.monotonic_sequence+1)return deny('REJECTED_SEQUENCE_GAP',event);
        if(event.registry_epoch<last.registry_epoch)return deny('REJECTED_STALE_EPOCH',event);
        if(event.registry_epoch>last.registry_epoch+1)return deny('REJECTED_EPOCH_GAP',event);
        if(event.previous_event_digest!==last.event_digest)return deny('REJECTED_EVENT_CHAIN',event);
        if(event.observed_at<last.observed_at)return deny('REJECTED_TIME_REGRESSION',event);
      }
      let code;
      if(event.event_type==='HELPER_REGISTERED'){
        if(registered.has(event.helper_id))return deny('REJECTED_DUPLICATE_HELPER',event);
        if(revoked.has(event.helper_id))return deny('REJECTED_HELPER_REVOKED',event);
        registered.set(event.helper_id,{
          helper_id:event.helper_id,canonical_owner_id:event.canonical_owner_id,
          section_id:event.section_id,slot:event.slot,growth_source:event.growth_source,
          source_version:event.source_version,registry_epoch:event.registry_epoch,
          guard_requirement_count:spec.guard_requirement_count,
          status:'REGISTERED_STATIC_EVENT_ONLY',behavior_authorized:false
        });
        code='HELPER_REGISTERED';
      }else if(event.event_type==='HELPER_UPDATED'){
        if(!registered.has(event.helper_id))return deny('REJECTED_HELPER_NOT_REGISTERED',event);
        const row=registered.get(event.helper_id);
        row.source_version=event.source_version;
        row.registry_epoch=event.registry_epoch;
        code='HELPER_UPDATED';
      }else if(event.event_type==='HELPER_REVOKED'){
        if(!registered.has(event.helper_id))return deny('REJECTED_HELPER_NOT_REGISTERED',event);
        if(!Number.isInteger(authority.revocation_epoch)||authority.revocation_epoch<=priorEpoch){
          return deny('REJECTED_STALE_REVOCATION',event);
        }
        revoked.set(event.helper_id,authority.revocation_epoch);
        registered.get(event.helper_id).status='REVOKED_STATIC_EVENT_ONLY';
        code='HELPER_REVOKED';
      }else if(event.event_type==='HELPER_REMOVED'){
        if(!registered.has(event.helper_id))return deny('REJECTED_HELPER_NOT_REGISTERED',event);
        registered.delete(event.helper_id);
        code='HELPER_REMOVED';
      }else{
        pending.set(event.helper_id,{
          helper_id:event.helper_id,canonical_owner_id:event.canonical_owner_id,
          section_id:event.section_id,slot:event.slot,growth_source:event.growth_source,
          status:'OBSERVED_PENDING_NO_AUTHORITY',authority_granted:false,
          behavior_authorized:false
        });
        code='HELPER_GROWTH_RECORDED_NO_AUTHORITY';
      }
      const normalized=clone(event);
      normalized.event_digest=eventHash;
      last=normalized;
      eventsById.set(event.event_id,eventHash);
      operations.add(event.operation_id);
      journal.push(normalized);
      diagnostics.push({
        operation_id:event.operation_id,event_id:event.event_id,
        helper_id:event.helper_id,canonical_owner_id:event.canonical_owner_id,
        section_id:event.section_id,slot:event.slot,event_type:event.event_type,
        result:code,capability_present:true,authority_granted:false,
        behavior_authorized:false
      });
      return accept(code,event,true);
    }
    function snapshot(){
      return clone({
        type:SNAPSHOT_TYPE,version:VERSION,event_version:EVENT_VERSION,
        journal_version:JOURNAL_VERSION,capability_contract_version:CAPABILITY_VERSION,
        root_authority:ROOT_AUTHORITY,growth_observer:GROWTH_OBSERVER,dependencies,
        registered:Array.from(registered.values()).sort((a,b)=>a.helper_id.localeCompare(b.helper_id)),
        pending_growth:Array.from(pending.values()).sort((a,b)=>a.helper_id.localeCompare(b.helper_id)),
        revoked:Object.fromEntries(Array.from(revoked.entries()).sort()),
        held_declared:HELPER_SPECS.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY').map(
          row=>({helper_id:row.helper_id,disposition:row.disposition})
        ),
        unknown_sources:UNKNOWN_SOURCES.map(file=>({file,status:'HELD_NO_CAPABILITY'})),
        journal,diagnostics,
        counts:{
          eligible_static:HELPER_SPECS.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY').length,
          held_declared:HELPER_SPECS.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY').length,
          unknown_sources:UNKNOWN_SOURCES.length,registered:registered.size,
          pending_growth:pending.size,revoked:revoked.size,
          accepted:journal.length,rejected,duplicates,rejection_codes:clone(rejectionCounts)
        },
        disclosure:{
          capability_ids_exposed_to_diagnostics:false,
          helper_source_hashes_exposed_to_diagnostics:false,
          raw_authority_payloads_exposed:false,
          source_versions_exposed_to_diagnostics:false
        },
        side_effects:sideEffects()
      });
    }
    return Object.freeze({
      type:TYPE,version:VERSION,available:true,
      mode:'PASSIVE_EXPLICIT_HELPER_EVENTS_ONLY',
      eventVersion:EVENT_VERSION,journalVersion:JOURNAL_VERSION,
      capabilityContractVersion:CAPABILITY_VERSION,
      rootAuthority:ROOT_AUTHORITY,growthObserver:GROWTH_OBSERVER,
      dependencies,applyHelperEvent,snapshot,sideEffects:sideEffects()
    });
  }
  function packageJournal(runtime){
    if(!runtime||typeof runtime.snapshot!=='function')return null;
    const snapshot=runtime.snapshot(),entries=clone(snapshot.journal);
    return {
      type:JOURNAL_VERSION,version:VERSION,entry_count:entries.length,
      head_event_digest:entries.length?entries[entries.length-1].event_digest:null,
      snapshot_sha256:digest({
        registered:snapshot.registered,
        pending_growth:snapshot.pending_growth,
        revoked:snapshot.revoked
      }),
      entries
    };
  }
  function restore(sectionRuntime,packageValue){
    const empty=create(sectionRuntime);
    function rejected(code,index,outcome){
      return Object.freeze({
        restored:false,mutated:false,authority_granted:false,
        behavior_authorized:false,code,
        rejected_index:Number.isInteger(index)?index:null,
        rejected_code:outcome&&outcome.code||null,
        operation_ids:Object.freeze([]),runtime:empty,side_effects:sideEffects()
      });
    }
    if(!plain(packageValue)||packageValue.type!==JOURNAL_VERSION||
       packageValue.version!==VERSION)return rejected('RESTART_REJECTED_PACKAGE',null,null);
    if(!Array.isArray(packageValue.entries)||
       packageValue.entry_count!==packageValue.entries.length){
      return rejected('RESTART_REJECTED_COUNT',null,null);
    }
    const candidate=create(sectionRuntime),operationIds=[];
    for(let index=0;index<packageValue.entries.length;index++){
      const event=clone(packageValue.entries[index]);
      if(!plain(event)||!Object.prototype.hasOwnProperty.call(event,'event_digest')){
        return rejected('RESTART_REJECTED_JOURNAL_EVENT',index,{code:'REJECTED_STORED_EVENT_DIGEST'});
      }
      const stored=event.event_digest;
      delete event.event_digest;
      if(!DIGEST.test(String(stored))||stored!==digest(event)){
        return rejected('RESTART_REJECTED_JOURNAL_EVENT',index,{code:'REJECTED_STORED_EVENT_DIGEST'});
      }
      const outcome=candidate.applyHelperEvent(event);
      if(!outcome.accepted||!outcome.mutated){
        return rejected('RESTART_REJECTED_JOURNAL_EVENT',index,outcome);
      }
      operationIds.push(outcome.operation_id);
    }
    const repack=packageJournal(candidate);
    if(repack.head_event_digest!==packageValue.head_event_digest){
      return rejected('RESTART_REJECTED_HEAD',null,null);
    }
    if(repack.snapshot_sha256!==packageValue.snapshot_sha256){
      return rejected('RESTART_REJECTED_SNAPSHOT',null,null);
    }
    return Object.freeze({
      restored:true,mutated:packageValue.entries.length>0,authority_granted:false,
      behavior_authorized:false,code:'RESTART_REPLAY_ACCEPTED',
      rejected_index:null,rejected_code:null,
      operation_ids:Object.freeze(operationIds),runtime:candidate,side_effects:sideEffects()
    });
  }
  function install(target){
    const host=target&&typeof target==='object'?target:null;
    if(!host)return null;
    const existing=host.PMPHelperOwnerRuntimeV1;
    if(existing&&existing.type===TYPE)return existing;
    const runtime=create(host.PMPSectionOwnerMountRuntimeV1);
    host.PMPHelperOwnerRuntimeV1=runtime;
    return runtime;
  }
  return Object.freeze({
    type:TYPE,version:VERSION,snapshotType:SNAPSHOT_TYPE,
    eventVersion:EVENT_VERSION,journalVersion:JOURNAL_VERSION,
    capabilityContractVersion:CAPABILITY_VERSION,
    rootAuthority:ROOT_AUTHORITY,growthObserver:GROWTH_OBSERVER,
    helpers:HELPER_SPECS,unknownSources:UNKNOWN_SOURCES,
    create,restore,packageJournal,install,digest
  });
});
