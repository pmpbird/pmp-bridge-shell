(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PMPDiagnosticJournalContractV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const ENTRY_TYPE='PMP_DIAGNOSTIC_JOURNAL_ENTRY_V1';
  const SNAPSHOT_TYPE='PMP_DIAGNOSTIC_JOURNAL_SNAPSHOT_V1';
  const FACT_KINDS=Object.freeze(['OBSERVED_FACT','DERIVED_FACT','INFERRED_CONCLUSION']);
  const TRUST=Object.freeze(['OWNER_ATTESTED','SYSTEM_VERIFIED','OBSERVER_REPORTED','INFERRED']);
  const SEVERITY=Object.freeze(['DEBUG','INFO','NOTICE','WARNING','ERROR','CRITICAL']);
  const DEFAULT_CAPACITY=256;
  const MAX_CAPACITY=4096;
  const DEFAULT_RETENTION_MS=7*24*60*60*1000;
  const MAX_RETENTION_MS=90*24*60*60*1000;
  const MAX_FUTURE_DRIFT_MS=5*60*1000;
  const MAX_STRING=512;
  const MAX_ARRAY=32;
  const MAX_KEYS=64;
  const MAX_DEPTH=5;
  const REDACTED='[REDACTED]';
  const SENSITIVE_KEY=/(authorization|bearer|cookie|credential|password|passwd|secret|token|api[_-]?key|private[_-]?key|session|email|phone|address|user[_-]?data|persisted[_-]?data|clipboard|notes?|absolute[_-]?path)/i;
  const SENSITIVE_VALUE=/(bearer\s+[a-z0-9._~+/=-]{8,}|(?:sk|ghp|github_pat)_[a-z0-9_-]{8,})/i;

  function clone(value){
    if(value===undefined)return undefined;
    return JSON.parse(JSON.stringify(value));
  }
  function plain(value){
    if(!value||typeof value!=='object'||Array.isArray(value))return false;
    const proto=Object.getPrototypeOf(value);
    return proto===Object.prototype||proto===null;
  }
  function iso(value){
    if(typeof value!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(value))return null;
    const time=Date.parse(value);
    return Number.isFinite(time)?time:null;
  }
  function boundedString(value,label,allowEmpty){
    if(typeof value!=='string')throw error('INVALID_STRING',label);
    const clean=value.trim();
    if((!allowEmpty&&!clean)||clean.length>MAX_STRING)throw error('INVALID_STRING',label);
    return clean;
  }
  function error(code,field,details){
    const out=new Error(code+(field?':'+field:''));
    out.code=code;
    out.field=field||null;
    out.details=details||null;
    return out;
  }
  function redact(value,key,depth,stats){
    depth=depth||0;
    stats=stats||{redacted:0,truncated:0,dropped:0};
    if(depth>MAX_DEPTH){stats.dropped++;return '[DEPTH_LIMIT]'}
    if(key&&SENSITIVE_KEY.test(String(key))){stats.redacted++;return REDACTED}
    if(value===null||typeof value==='boolean'||typeof value==='number')return value;
    if(typeof value==='string'){
      if(SENSITIVE_VALUE.test(value)){stats.redacted++;return REDACTED}
      if(value.length>MAX_STRING){stats.truncated++;return value.slice(0,MAX_STRING)+'…'}
      return value;
    }
    if(Array.isArray(value)){
      if(value.length>MAX_ARRAY)stats.dropped+=value.length-MAX_ARRAY;
      return value.slice(0,MAX_ARRAY).map(item=>redact(item,'',depth+1,stats));
    }
    if(plain(value)){
      const out={};
      const keys=Object.keys(value).sort();
      if(keys.length>MAX_KEYS)stats.dropped+=keys.length-MAX_KEYS;
      for(const name of keys.slice(0,MAX_KEYS))out[name]=redact(value[name],name,depth+1,stats);
      return out;
    }
    stats.dropped++;
    return '[UNSUPPORTED_VALUE]';
  }
  function stable(value){
    if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
    if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  function fingerprint(value){
    const text=stable(value);
    let a=2166136261>>>0;
    let b=2246822519>>>0;
    for(let i=0;i<text.length;i++){
      const c=text.charCodeAt(i);
      a=Math.imul(a^c,16777619)>>>0;
      b=Math.imul(b^c,3266489917)>>>0;
    }
    return ('00000000'+a.toString(16)).slice(-8)+('00000000'+b.toString(16)).slice(-8);
  }
  function entryFingerprint(value){
    const payload=clone(value);
    delete payload.redaction;
    return fingerprint(payload);
  }
  function exactKeys(value,required,optional,label){
    if(!plain(value))throw error('INVALID_OBJECT',label);
    const allowed=new Set(required.concat(optional||[]));
    for(const key of required)if(!Object.prototype.hasOwnProperty.call(value,key))throw error('MISSING_FIELD',label+'.'+key);
    for(const key of Object.keys(value))if(!allowed.has(key))throw error('UNKNOWN_FIELD',label+'.'+key);
  }
  function validateSource(source){
    exactKeys(source,['owner','component','channel'],[],'source');
    return {
      owner:boundedString(source.owner,'source.owner'),
      component:boundedString(source.component,'source.component'),
      channel:boundedString(source.channel,'source.channel')
    };
  }
  function validateProvenance(provenance,factKind){
    exactKeys(provenance,['trust','evidence_refs'],[],'provenance');
    if(!TRUST.includes(provenance.trust))throw error('INVALID_TRUST','provenance.trust');
    if(!Array.isArray(provenance.evidence_refs)||provenance.evidence_refs.length>MAX_ARRAY)throw error('INVALID_EVIDENCE_REFS','provenance.evidence_refs');
    const refs=provenance.evidence_refs.map((item,index)=>boundedString(item,'provenance.evidence_refs['+index+']'));
    if(factKind==='INFERRED_CONCLUSION'){
      if(provenance.trust!=='INFERRED')throw error('INFERENCE_TRUST_REQUIRED','provenance.trust');
      if(refs.length===0)throw error('INFERENCE_BASIS_REQUIRED','provenance.evidence_refs');
    }else{
      if(provenance.trust==='INFERRED')throw error('FACT_CANNOT_USE_INFERRED_TRUST','provenance.trust');
      if(factKind==='DERIVED_FACT'&&refs.length===0)throw error('DERIVED_BASIS_REQUIRED','provenance.evidence_refs');
    }
    return {trust:provenance.trust,evidence_refs:refs};
  }
  function normalizeInput(input,recordedAt){
    exactKeys(input,[
      'type','version','event_id','observed_at','fact_kind','severity','code',
      'source','provenance','subject','summary','details'
    ],[],'entry');
    if(input.type!==ENTRY_TYPE)throw error('INVALID_ENTRY_TYPE','type');
    if(input.version!==VERSION)throw error('INVALID_ENTRY_VERSION','version');
    if(!FACT_KINDS.includes(input.fact_kind))throw error('INVALID_FACT_KIND','fact_kind');
    if(!SEVERITY.includes(input.severity))throw error('INVALID_SEVERITY','severity');
    const observed=iso(input.observed_at);
    const recorded=iso(recordedAt);
    if(observed===null)throw error('INVALID_TIMESTAMP','observed_at');
    if(recorded===null)throw error('INVALID_TIMESTAMP','recorded_at');
    if(observed>recorded+MAX_FUTURE_DRIFT_MS)throw error('FUTURE_OBSERVATION','observed_at');
    if(!plain(input.subject))throw error('INVALID_OBJECT','subject');
    const redaction={redacted:0,truncated:0,dropped:0};
    const subject=redact(input.subject,'',0,redaction);
    const details=redact(input.details,'',0,redaction);
    return {
      type:ENTRY_TYPE,
      version:VERSION,
      event_id:boundedString(input.event_id,'event_id'),
      observed_at:input.observed_at,
      fact_kind:input.fact_kind,
      severity:input.severity,
      code:boundedString(input.code,'code'),
      source:validateSource(input.source),
      provenance:validateProvenance(input.provenance,input.fact_kind),
      subject,
      summary:redact(boundedString(input.summary,'summary'),'summary',0,redaction),
      details,
      redaction
    };
  }
  function validateConfig(config){
    config=config||{};
    exactKeys(config,[],['capacity','retention_ms'],'config');
    const capacity=config.capacity===undefined?DEFAULT_CAPACITY:config.capacity;
    const retention=config.retention_ms===undefined?DEFAULT_RETENTION_MS:config.retention_ms;
    if(!Number.isInteger(capacity)||capacity<1||capacity>MAX_CAPACITY)throw error('INVALID_CAPACITY','config.capacity');
    if(!Number.isInteger(retention)||retention<1||retention>MAX_RETENTION_MS)throw error('INVALID_RETENTION','config.retention_ms');
    return {capacity,retention_ms:retention};
  }
  function createJournal(config){
    const settings=validateConfig(config);
    let entries=[];
    let seen=new Map();
    let lastRecorded=-Infinity;
    let rejections=[];

    function reject(err){
      const row={code:err&&err.code||'UNKNOWN_REJECTION',field:err&&err.field||null};
      rejections.push(row);
      if(rejections.length>64)rejections=rejections.slice(-64);
      return {accepted:false,idempotent:false,rejection:row};
    }
    function prune(nowMs){
      const cutoff=nowMs-settings.retention_ms;
      const kept=entries.filter(row=>Date.parse(row.recorded_at)>=cutoff);
      const removed=entries.length-kept.length;
      entries=kept;
      seen=new Map(entries.map(row=>[row.event_id,{fingerprint:row.fingerprint,sequence:row.sequence}]));
      return removed;
    }
    function append(input,recordedAt){
      const before=stable(entries);
      try{
        const normalized=normalizeInput(input,recordedAt);
        const recorded=iso(recordedAt);
        if(recorded<lastRecorded)throw error('RECORDED_TIME_REGRESSION','recorded_at');
        const fp=entryFingerprint(normalized);
        const prior=seen.get(normalized.event_id);
        if(prior){
          if(prior.fingerprint===fp)return {accepted:true,idempotent:true,sequence:prior.sequence,evicted:0,expired:0};
          throw error('CONFLICTING_DUPLICATE','event_id');
        }
        const expired=prune(recorded);
        const sequence=entries.length?entries[entries.length-1].sequence+1:1;
        const row=Object.freeze(Object.assign({},normalized,{
          sequence,
          recorded_at:recordedAt,
          fingerprint:fp
        }));
        entries.push(row);
        seen.set(row.event_id,{fingerprint:fp,sequence});
        let evicted=0;
        while(entries.length>settings.capacity){
          const gone=entries.shift();
          seen.delete(gone.event_id);
          evicted++;
        }
        lastRecorded=recorded;
        return {accepted:true,idempotent:false,sequence,evicted,expired};
      }catch(err){
        if(stable(entries)!==before)throw error('FAIL_PASSIVE_VIOLATION',null,{cause:err&&err.code});
        return reject(err);
      }
    }
    function read(options){
      options=options||{};
      exactKeys(options,[],['limit','fact_kind','severity','code'],'read_options');
      const limit=options.limit===undefined?settings.capacity:options.limit;
      if(!Number.isInteger(limit)||limit<0||limit>settings.capacity)throw error('INVALID_LIMIT','read_options.limit');
      let rows=entries;
      for(const key of ['fact_kind','severity','code']){
        if(options[key]!==undefined)rows=rows.filter(row=>row[key]===options[key]);
      }
      return clone(rows.slice(-limit));
    }
    function snapshot(createdAt){
      if(iso(createdAt)===null)throw error('INVALID_TIMESTAMP','snapshot.created_at');
      return {
        type:SNAPSHOT_TYPE,
        version:VERSION,
        created_at:createdAt,
        capacity:settings.capacity,
        retention_ms:settings.retention_ms,
        last_recorded_at:Number.isFinite(lastRecorded)?new Date(lastRecorded).toISOString():null,
        entries:clone(entries),
        rejections:clone(rejections),
        integrity:fingerprint(entries)
      };
    }
    function restore(snapshot,restoredAt){
      const before={entries:stable(entries),rejections:stable(rejections),lastRecorded};
      try{
        exactKeys(snapshot,[
          'type','version','created_at','capacity','retention_ms','last_recorded_at',
          'entries','rejections','integrity'
        ],[],'snapshot');
        if(snapshot.type!==SNAPSHOT_TYPE||snapshot.version!==VERSION)throw error('INVALID_SNAPSHOT_IDENTITY','snapshot');
        if(snapshot.capacity!==settings.capacity||snapshot.retention_ms!==settings.retention_ms)throw error('SNAPSHOT_CONFIG_MISMATCH','snapshot');
        if(iso(snapshot.created_at)===null||iso(restoredAt)===null)throw error('INVALID_TIMESTAMP','snapshot');
        if(!Array.isArray(snapshot.entries)||snapshot.entries.length>settings.capacity)throw error('INVALID_SNAPSHOT_ENTRIES','snapshot.entries');
        if(!Array.isArray(snapshot.rejections)||snapshot.rejections.length>64)throw error('INVALID_SNAPSHOT_REJECTIONS','snapshot.rejections');
        if(snapshot.integrity!==fingerprint(snapshot.entries))throw error('SNAPSHOT_INTEGRITY_MISMATCH','snapshot.integrity');
        const next=[];
        const ids=new Set();
        let expected=null;
        let last=-Infinity;
        for(const row of snapshot.entries){
          exactKeys(row,[
            'type','version','event_id','observed_at','fact_kind','severity','code',
            'source','provenance','subject','summary','details','redaction','sequence',
            'recorded_at','fingerprint'
          ],[],'snapshot.entry');
          const normalized=normalizeInput({
            type:row.type,
            version:row.version,
            event_id:row.event_id,
            observed_at:row.observed_at,
            fact_kind:row.fact_kind,
            severity:row.severity,
            code:row.code,
            source:row.source,
            provenance:row.provenance,
            subject:row.subject,
            summary:row.summary,
            details:row.details
          },row.recorded_at);
          if(expected===null)expected=row.sequence;
          if(row.sequence!==expected++)throw error('SNAPSHOT_SEQUENCE_INVALID','snapshot.entry.sequence');
          if(ids.has(row.event_id))throw error('SNAPSHOT_DUPLICATE_EVENT','snapshot.entry.event_id');
          if(row.fingerprint!==entryFingerprint(normalized))throw error('SNAPSHOT_ENTRY_INTEGRITY_MISMATCH','snapshot.entry.fingerprint');
          const at=iso(row.recorded_at);
          if(at<last)throw error('SNAPSHOT_TIME_REGRESSION','snapshot.entry.recorded_at');
          last=at;
          ids.add(row.event_id);
          next.push(Object.freeze(clone(row)));
        }
        if(snapshot.last_recorded_at!==(Number.isFinite(last)?new Date(last).toISOString():null))throw error('SNAPSHOT_LAST_TIME_MISMATCH','snapshot.last_recorded_at');
        entries=next;
        seen=new Map(entries.map(row=>[row.event_id,{fingerprint:row.fingerprint,sequence:row.sequence}]));
        rejections=clone(snapshot.rejections);
        lastRecorded=last;
        const expired=prune(iso(restoredAt));
        return {restored:true,entries:entries.length,expired};
      }catch(err){
        entries=JSON.parse(before.entries);
        rejections=JSON.parse(before.rejections);
        lastRecorded=before.lastRecorded;
        seen=new Map(entries.map(row=>[row.event_id,{fingerprint:row.fingerprint,sequence:row.sequence}]));
        return {restored:false,rejection:{code:err&&err.code||'UNKNOWN_REJECTION',field:err&&err.field||null}};
      }
    }
    function diagnostics(){
      return {
        type:'PMP_DIAGNOSTIC_JOURNAL_STATUS_V1',
        version:VERSION,
        entry_count:entries.length,
        capacity:settings.capacity,
        retention_ms:settings.retention_ms,
        last_sequence:entries.length?entries[entries.length-1].sequence:0,
        rejection_count:rejections.length,
        rejection_counts:rejections.reduce((out,row)=>(out[row.code]=(out[row.code]||0)+1,out),{}),
        side_effects:{
          local_storage_writes:0,
          indexed_db_writes:0,
          network_requests:0,
          dom_mutations:0,
          route_changes:0,
          repairs:0,
          persisted_user_data_writes:0
        }
      };
    }
    return Object.freeze({append,read,snapshot,restore,diagnostics});
  }

  return Object.freeze({
    version:VERSION,
    entryType:ENTRY_TYPE,
    snapshotType:SNAPSHOT_TYPE,
    factKinds:FACT_KINDS,
    trustLevels:TRUST,
    severityLevels:SEVERITY,
    limits:Object.freeze({
      default_capacity:DEFAULT_CAPACITY,
      max_capacity:MAX_CAPACITY,
      default_retention_ms:DEFAULT_RETENTION_MS,
      max_retention_ms:MAX_RETENTION_MS,
      max_future_drift_ms:MAX_FUTURE_DRIFT_MS,
      max_string:MAX_STRING,
      max_array:MAX_ARRAY,
      max_keys:MAX_KEYS,
      max_depth:MAX_DEPTH
    }),
    redaction:Object.freeze({marker:REDACTED,sensitive_key_pattern:SENSITIVE_KEY.source}),
    createJournal
  });
});
