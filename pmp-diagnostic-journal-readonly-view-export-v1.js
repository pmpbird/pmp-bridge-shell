(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PMPDiagnosticJournalReadonlyViewExportV1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const VIEW_TYPE='PMP_DIAGNOSTIC_JOURNAL_READONLY_VIEW_V1';
  const EXPORT_TYPE='PMP_DIAGNOSTIC_JOURNAL_BOUNDED_EXPORT_V1';
  const ENTRY_TYPE='PMP_DIAGNOSTIC_JOURNAL_ENTRY_V1';
  const CONTRACT_VERSION='1.0.0';
  const DEFAULT_VISIBLE_ENTRIES=64;
  const MAX_VISIBLE_ENTRIES=128;
  const DEFAULT_EXPORT_ENTRIES=128;
  const MAX_EXPORT_ENTRIES=256;
  const MAX_EXPORT_BYTES=262144;
  const MAX_STRING=512;
  const MAX_ARRAY=32;
  const MAX_KEYS=64;
  const MAX_DEPTH=6;
  const REDACTED='[REDACTED]';
  const FACT_KINDS=Object.freeze(['OBSERVED_FACT','DERIVED_FACT','INFERRED_CONCLUSION']);
  const TRUST_LEVELS=Object.freeze(['OWNER_ATTESTED','SYSTEM_VERIFIED','OBSERVER_REPORTED','INFERRED']);
  const SEVERITY_LEVELS=Object.freeze(['DEBUG','INFO','NOTICE','WARNING','ERROR','CRITICAL']);
  const SENSITIVE_KEY=/(authorization|bearer|cookie|credential|password|passwd|secret|token|api[_-]?key|private[_-]?key|session|email|phone|address|user[_-]?data|persisted[_-]?data|clipboard|notes?|absolute[_-]?path)/i;
  const SENSITIVE_VALUE=/(bearer\s+[a-z0-9._~+/=-]{8,}|(?:sk|ghp|github_pat)_[a-z0-9_-]{8,})/i;

  function plain(value){
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&
      (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
  }
  function clone(value){
    return JSON.parse(JSON.stringify(value));
  }
  function freeze(value){
    if(value&&typeof value==='object'&&!Object.isFrozen(value)){
      Object.freeze(value);
      Object.keys(value).forEach(key=>freeze(value[key]));
    }
    return value;
  }
  function stable(value,indent){
    const normalize=item=>{
      if(Array.isArray(item))return item.map(normalize);
      if(plain(item)){
        const out={};
        Object.keys(item).sort().forEach(key=>{out[key]=normalize(item[key])});
        return out;
      }
      return item;
    };
    return JSON.stringify(normalize(value),null,indent||0);
  }
  function utf8Bytes(value){
    const text=String(value);
    if(typeof TextEncoder==='function')return new TextEncoder().encode(text).length;
    return unescape(encodeURIComponent(text)).length;
  }
  function fingerprint(value){
    const text=stable(value);
    let a=2166136261>>>0;
    let b=2246822519>>>0;
    for(let i=0;i<text.length;i++){
      const code=text.charCodeAt(i);
      a=Math.imul(a^code,16777619)>>>0;
      b=Math.imul(b^code,3266489917)>>>0;
    }
    return ('00000000'+a.toString(16)).slice(-8)+('00000000'+b.toString(16)).slice(-8);
  }
  function exactKeys(value,required,optional){
    if(!plain(value))return false;
    const allowed=new Set(required.concat(optional||[]));
    return required.every(key=>Object.prototype.hasOwnProperty.call(value,key))&&
      Object.keys(value).every(key=>allowed.has(key));
  }
  function iso(value){
    return typeof value==='string'&&
      /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(value)&&
      Number.isFinite(Date.parse(value));
  }
  function safePayload(value,key,depth){
    depth=depth||0;
    if(depth>MAX_DEPTH)return false;
    if(key&&SENSITIVE_KEY.test(String(key)))return value===REDACTED;
    if(value===null||typeof value==='boolean'||typeof value==='number')return true;
    if(typeof value==='string'){
      return value.length<=MAX_STRING+1&&!SENSITIVE_VALUE.test(value);
    }
    if(Array.isArray(value)){
      return value.length<=MAX_ARRAY&&value.every(item=>safePayload(item,'',depth+1));
    }
    if(plain(value)){
      const keys=Object.keys(value);
      return keys.length<=MAX_KEYS&&keys.every(name=>safePayload(value[name],name,depth+1));
    }
    return false;
  }
  function validateEntry(row){
    const required=[
      'type','version','event_id','observed_at','fact_kind','severity','code',
      'source','provenance','subject','summary','details','redaction','sequence',
      'recorded_at','fingerprint'
    ];
    if(!exactKeys(row,required,[]))return null;
    if(row.type!==ENTRY_TYPE||row.version!==CONTRACT_VERSION)return null;
    if(typeof row.event_id!=='string'||!row.event_id||row.event_id.length>MAX_STRING)return null;
    if(!iso(row.observed_at)||!iso(row.recorded_at))return null;
    if(!FACT_KINDS.includes(row.fact_kind)||!SEVERITY_LEVELS.includes(row.severity))return null;
    if(typeof row.code!=='string'||!row.code||row.code.length>MAX_STRING)return null;
    if(!plain(row.source)||!plain(row.provenance)||!plain(row.redaction))return null;
    if(!TRUST_LEVELS.includes(row.provenance.trust)||!Array.isArray(row.provenance.evidence_refs))return null;
    if(!Number.isInteger(row.sequence)||row.sequence<1)return null;
    if(typeof row.fingerprint!=='string'||!/^[0-9a-f]{16}$/.test(row.fingerprint))return null;
    if(!safePayload(row.subject,'',0)||!safePayload(row.summary,'summary',0)||
       !safePayload(row.details,'',0))return null;
    return freeze(clone(row));
  }
  function counts(rows){
    const result={
      fact_kind:{OBSERVED_FACT:0,DERIVED_FACT:0,INFERRED_CONCLUSION:0},
      trust:{OWNER_ATTESTED:0,SYSTEM_VERIFIED:0,OBSERVER_REPORTED:0,INFERRED:0},
      severity:{DEBUG:0,INFO:0,NOTICE:0,WARNING:0,ERROR:0,CRITICAL:0}
    };
    rows.forEach(row=>{
      result.fact_kind[row.fact_kind]++;
      result.trust[row.provenance.trust]++;
      result.severity[row.severity]++;
    });
    return freeze(result);
  }
  function sideEffects(){
    return freeze({
      journal_appends:0,
      journal_restores:0,
      local_storage_writes:0,
      indexed_db_writes:0,
      network_requests:0,
      dom_mutations:0,
      route_changes:0,
      repairs:0,
      persisted_user_data_writes:0
    });
  }
  function unavailable(status,details){
    return freeze({
      type:VIEW_TYPE,
      version:VERSION,
      status,
      available:false,
      entry_count:0,
      visible_entry_count:0,
      entries:[],
      counts:counts([]),
      journal_status:null,
      disclosure:{
        contract_redaction_required:true,
        raw_unvalidated_entries_exposed:false,
        maximum_visible_entries:MAX_VISIBLE_ENTRIES,
        entries_truncated:false
      },
      rejection:details||null,
      side_effects:sideEffects()
    });
  }
  function validateOptions(options,mode){
    options=options||{};
    const allowed=['limit','fact_kind','severity','code'];
    if(mode==='export')allowed.push('created_at');
    if(!exactKeys(options,mode==='export'?['created_at']:[],allowed.filter(x=>x!=='created_at'))){
      throw Object.assign(new Error('INVALID_OPTIONS'),{code:'INVALID_OPTIONS'});
    }
    const maximum=mode==='export'?MAX_EXPORT_ENTRIES:MAX_VISIBLE_ENTRIES;
    const fallback=mode==='export'?DEFAULT_EXPORT_ENTRIES:DEFAULT_VISIBLE_ENTRIES;
    const limit=options.limit===undefined?fallback:options.limit;
    if(!Number.isInteger(limit)||limit<0||limit>maximum){
      throw Object.assign(new Error('INVALID_LIMIT'),{code:'INVALID_LIMIT'});
    }
    if(options.fact_kind!==undefined&&!FACT_KINDS.includes(options.fact_kind)){
      throw Object.assign(new Error('INVALID_FACT_KIND'),{code:'INVALID_FACT_KIND'});
    }
    if(options.severity!==undefined&&!SEVERITY_LEVELS.includes(options.severity)){
      throw Object.assign(new Error('INVALID_SEVERITY'),{code:'INVALID_SEVERITY'});
    }
    if(options.code!==undefined&&(typeof options.code!=='string'||!options.code||options.code.length>MAX_STRING)){
      throw Object.assign(new Error('INVALID_CODE'),{code:'INVALID_CODE'});
    }
    if(mode==='export'&&!iso(options.created_at)){
      throw Object.assign(new Error('INVALID_CREATED_AT'),{code:'INVALID_CREATED_AT'});
    }
    const result={limit};
    ['fact_kind','severity','code'].forEach(key=>{
      if(options[key]!==undefined)result[key]=options[key];
    });
    if(mode==='export')result.created_at=options.created_at;
    return result;
  }
  function create(journal){
    const available=!!journal&&typeof journal.read==='function'&&
      typeof journal.diagnostics==='function';

    function collect(options,mode){
      if(!available)return {ok:false,view:unavailable('JOURNAL_UNAVAILABLE')};
      let requested;
      try{requested=validateOptions(options,mode)}catch(error){
        return {ok:false,view:unavailable(error.code||'INVALID_OPTIONS')};
      }
      let diagnostic;
      try{diagnostic=journal.diagnostics()}catch(_){
        return {ok:false,view:unavailable('JOURNAL_DIAGNOSTICS_ERROR')};
      }
      if(!plain(diagnostic)||diagnostic.type!=='PMP_DIAGNOSTIC_JOURNAL_STATUS_V1'||
         diagnostic.version!==CONTRACT_VERSION||!Number.isInteger(diagnostic.capacity)||
         diagnostic.capacity<1){
        return {ok:false,view:unavailable('JOURNAL_DIAGNOSTICS_MALFORMED')};
      }
      const readOptions={limit:Math.min(requested.limit,diagnostic.capacity)};
      ['fact_kind','severity','code'].forEach(key=>{
        if(requested[key]!==undefined)readOptions[key]=requested[key];
      });
      let raw;
      try{raw=readOptions.limit===0?[]:journal.read(readOptions)}catch(_){
        return {ok:false,view:unavailable('JOURNAL_READ_ERROR')};
      }
      if(!Array.isArray(raw)||raw.length>readOptions.limit){
        return {ok:false,view:unavailable('JOURNAL_READ_MALFORMED')};
      }
      const rows=raw.map(validateEntry);
      if(rows.some(row=>row===null)){
        return {ok:false,view:unavailable('JOURNAL_ENTRY_MALFORMED_OR_UNREDACTED')};
      }
      return {ok:true,rows,diagnostic:freeze(clone(diagnostic)),requested,readOptions};
    }
    function read(options){
      const result=collect(options,'view');
      if(!result.ok)return result.view;
      const rows=result.rows;
      return freeze({
        type:VIEW_TYPE,
        version:VERSION,
        status:rows.length?'READY_WITH_ENTRIES':'READY_EMPTY',
        available:true,
        entry_count:result.diagnostic.entry_count,
        visible_entry_count:rows.length,
        entries:rows,
        counts:counts(rows),
        journal_status:result.diagnostic,
        disclosure:{
          contract_redaction_required:true,
          raw_unvalidated_entries_exposed:false,
          maximum_visible_entries:MAX_VISIBLE_ENTRIES,
          entries_truncated:result.diagnostic.entry_count>rows.length
        },
        rejection:null,
        side_effects:sideEffects()
      });
    }
    function exportBundle(options){
      const result=collect(options,'export');
      if(!result.ok){
        return freeze({
          ok:false,
          status:result.view.status,
          type:EXPORT_TYPE,
          version:VERSION,
          bytes:0,
          text:'',
          bundle:null,
          side_effects:sideEffects()
        });
      }
      const selected=result.rows.slice();
      const selectedBeforeByteBound=selected.length;
      let omittedForByteBound=0;
      let bundle;
      let text;
      function rebuild(){
        const payload={
          type:EXPORT_TYPE,
          version:VERSION,
          created_at:result.requested.created_at,
          source_contract:{
            entry_type:ENTRY_TYPE,
            contract_version:CONTRACT_VERSION,
            view_version:VERSION
          },
          filter:{
            requested_limit:result.requested.limit,
            fact_kind:result.requested.fact_kind||null,
            severity:result.requested.severity||null,
            code:result.requested.code||null
          },
          bounds:{
            maximum_entries:MAX_EXPORT_ENTRIES,
            maximum_bytes:MAX_EXPORT_BYTES,
            selected_before_byte_bound:selectedBeforeByteBound,
            exported_entries:selected.length,
            omitted_for_byte_bound:omittedForByteBound,
            journal_entries_not_selected:Math.max(
              0,result.diagnostic.entry_count-selectedBeforeByteBound
            )
          },
          entries:selected.map(row=>clone(row)),
          integrity:{
            algorithm:'PMP_STABLE_FINGERPRINT_V1',
            entries_fingerprint:fingerprint(selected)
          },
          disclosure:{
            contract_redaction_required:true,
            raw_unvalidated_entries_exposed:false,
            persisted_user_data_included:false
          },
          side_effects:sideEffects()
        };
        payload.integrity.bundle_fingerprint=fingerprint(payload);
        bundle=freeze(payload);
        text=stable(bundle,2)+'\n';
      }
      rebuild();
      while(utf8Bytes(text)>MAX_EXPORT_BYTES&&selected.length){
        selected.shift();
        omittedForByteBound++;
        rebuild();
      }
      if(utf8Bytes(text)>MAX_EXPORT_BYTES){
        return freeze({
          ok:false,
          status:'EXPORT_BOUND_UNSATISFIABLE',
          type:EXPORT_TYPE,
          version:VERSION,
          bytes:0,
          text:'',
          bundle:null,
          side_effects:sideEffects()
        });
      }
      return freeze({
        ok:true,
        status:selected.length?'READY_WITH_ENTRIES':'READY_EMPTY',
        type:EXPORT_TYPE,
        version:VERSION,
        bytes:utf8Bytes(text),
        text,
        bundle,
        side_effects:sideEffects()
      });
    }
    return freeze({
      version:VERSION,
      available,
      read,
      exportBundle
    });
  }

  return freeze({
    version:VERSION,
    viewType:VIEW_TYPE,
    exportType:EXPORT_TYPE,
    limits:{
      default_visible_entries:DEFAULT_VISIBLE_ENTRIES,
      maximum_visible_entries:MAX_VISIBLE_ENTRIES,
      default_export_entries:DEFAULT_EXPORT_ENTRIES,
      maximum_export_entries:MAX_EXPORT_ENTRIES,
      maximum_export_bytes:MAX_EXPORT_BYTES
    },
    create
  });
});
