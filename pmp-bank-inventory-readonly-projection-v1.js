(()=>{
'use strict';
const VERSION='1.0.0-pass10-unit3-readonly-projection-20260726A';
const CONTRACT='PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1';
const ITEM_VERSION='PMP_CANONICAL_BANK_INVENTORY_ITEM_V1';
const OWNER='bank_screen_owner';
const BANKS={world:'World Bank',continuous_run:'Continuous Run Bank',connections:'Connections Bank',library:'Library Bank',workshop:'Workshop Bank',helper:'Helper Bank',protection:'Protection Bank',bug_memory:'Bug Bank',migration:'Migration Bank',ui_control_surface:'UI / Control Surface Bank',settings_preferences:'Settings / Preferences Bank',test_verification:'Test / Verification Bank',master:'Master Bank Inventory'};
const RULES=[
  ['LOCAL_STORAGE','pmp_master_bank_inventory_v1',OWNER,'CANONICAL_INDEX','master','PMP_MASTER_BANK_INVENTORY_V1'],
  ['LOCAL_STORAGE','pmp_source_bank_router_receipts_v1',OWNER,'OWNER_GOVERNED_RECEIPT_CHAIN','master','PMP_MASTER_BANK_INVENTORY_V1'],
  ['LOCAL_STORAGE','pmp_helper_bank_index_v1',OWNER,'OWNER_GOVERNED_INDEX','helper','PMP_HELPER_BANK_INDEX_V1'],
  ['LOCAL_STORAGE','pmp_connections_bank_chat_memory_deposits_v1',OWNER,'OWNER_GOVERNED_INDEX','connections','PMP_CONNECTIONS_BANK_DEPOSIT_INDEX_V1'],
  ['LOCAL_STORAGE','pmp_continuous_run_state_bank_v1','continuous_run_level_owner','CONTINUOUS_RUN_OWNER_FACT','continuous_run','PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'],
  ['LOCAL_STORAGE','pmp_continuous_run_state_receipts_v1','continuous_run_level_owner','CONTINUOUS_RUN_OWNER_RECEIPT_CHAIN','continuous_run','PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'],
  ['LOCAL_STORAGE','pmp_continuous_run_state_manifest_v1','continuous_run_level_owner','CONTINUOUS_RUN_OWNER_MANIFEST','continuous_run','PMP_CONTINUOUS_RUN_STATE_MANIFEST_V1'],
  ['LOCAL_STORAGE','pmp_bank_project_registry_v1','continuous_run_level_owner','CONTINUOUS_RUN_PROJECT_INDEX','continuous_run','BANK_PROJECT_REGISTRY_V1'],
  ['LOCAL_STORAGE','pmp_bank_project_registry_v1_receipt','continuous_run_level_owner','CONTINUOUS_RUN_PROJECT_RECEIPT','continuous_run','BANK_PROJECT_REGISTRY_V1'],
  ['LOCAL_STORAGE','pmp_continuous_run_bank_transfer_store_manifest_v1','continuous_run_level_owner','AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE','continuous_run','PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'],
  ['LOCAL_STORAGE','pmp_continuous_run_bank_transfer_store_receipts_v1','continuous_run_level_owner','AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE','continuous_run','PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'],
  ['LOCAL_STORAGE','pmp_connection_bank_inventory_v1','historic_connection_inventory','HISTORIC_REFERENCE_ONLY','connections','PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1'],
  ['LOCAL_STORAGE','pmp_connection_protected_bank_registry_v1','historic_connection_inventory','HISTORIC_REFERENCE_ONLY','connections','PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1'],
  ['LOCAL_STORAGE','pmp_connection_bank_inventory_receipt_v1','historic_connection_inventory','HISTORIC_REFERENCE_ONLY','connections','PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1']
];
const INDEXED=[
  {storage_kind:'INDEXED_DB',namespace:'pmp_connections_bank_deposits_db_v1/deposits',owner_id:OWNER,classification:'OWNER_GOVERNED_BINARY_PAYLOAD',owning_bank:'connections'},
  {storage_kind:'INDEXED_DB',namespace:'pmp_continuous_run_bank_transfer_store_db_v1/items',owner_id:'continuous_run_level_owner',classification:'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE',owning_bank:'continuous_run'}
];
let lastSnapshot=null;
function B(){return window.PMPBankContinuousRunOwnerBoundaryV1||null}
function storage(){try{return window.localStorage||null}catch(e){return null}}
function bytes(s){try{return unescape(encodeURIComponent(String(s==null?'':s))).length}catch(e){return String(s==null?'':s).length}}
function clean(v){return String(v==null?'':v).trim()}
function clone(v){try{return JSON.parse(JSON.stringify(v))}catch(e){return v}}
function ruleFor(kind,namespace){let r=RULES.find(x=>x[0]===kind&&x[1]===namespace);return r?{storage_kind:r[0],namespace:r[1],owner_id:r[2],classification:r[3],owning_bank:r[4],schema_type:r[5]}:null}
function sha(value){let b=B();return b&&typeof b.sha256==='function'?b.sha256(String(value==null?'':value)):''}
function canonicalId(kind,namespace,nativeId,raw){
  let native=clean(nativeId),prefix=native?'bank-item:v1:':'bank-quarantine:v1:';
  let pre=native?[CONTRACT,kind,namespace,native].join('\x00'):[CONTRACT,kind||'',namespace||'',sha(raw)].join('\x00');
  return prefix+sha(pre)
}
function readRaw(key,counters){let b=B();counters.storage_reads++;return b&&typeof b.readRaw==='function'?b.readRaw(key):null}
function listKeys(counters){
  let s=storage(),out=[];if(!s)return out;
  try{for(let i=0;i<s.length;i++){counters.key_enumerations++;let k=s.key(i);if(k!=null)out.push(String(k))}}catch(e){}
  return Array.from(new Set(out)).sort()
}
function sourceVersion(parsed){let v=parsed&&parsed.version;return clean(v)||'unknown'}
function publicItem(item){
  return{
    item_version:item.item_version,
    canonical_id:item.canonical_id,
    source_storage_kind:item.source_storage_kind,
    source_namespace:item.source_namespace,
    source_native_id:item.source_native_id,
    owning_bank:item.owning_bank,
    owner_id:item.owner_id,
    schema_type:item.schema_type,
    schema_version:item.schema_version,
    source_schema_version:item.source_schema_version,
    payload_sha256:item.payload_sha256,
    payload_bytes:item.payload_bytes,
    compatibility_aliases:item.compatibility_aliases.slice(),
    namespace_classification:item.namespace_classification,
    state:item.state,
    quarantine_reasons:item.quarantine_reasons.slice(),
    write_authority:item.write_authority,
    delete_authority:item.delete_authority,
    exact_bytes_preserved_in_source:true,
    raw_payload_exposed_to_ui:false
  }
}
function makeItem(input){
  let raw=String(input.raw==null?'':input.raw),reasons=Array.from(new Set(input.reasons||[])).sort(),classification=input.classification||'UNKNOWN_NAMESPACE',state='ACTIVE';
  if(classification==='HISTORIC_REFERENCE_ONLY')state='REFERENCE_ONLY';
  if(input.stale)state='STALE';
  if(input.unavailable)state='UNAVAILABLE';
  if(reasons.some(x=>!['SOURCE_UNAVAILABLE','STALE_SOURCE'].includes(x)))state='QUARANTINED';
  return{
    item_version:ITEM_VERSION,
    canonical_id:canonicalId(input.storage_kind,input.namespace,input.native_id,raw),
    source_storage_kind:input.storage_kind,
    source_namespace:input.namespace,
    source_native_id:clean(input.native_id)||null,
    owning_bank:BANKS[input.owning_bank]?input.owning_bank:null,
    owner_id:input.owner_id||null,
    schema_type:input.schema_type||'PMP_UNKNOWN_SCHEMA',
    schema_version:'1.0.0',
    source_schema_version:input.source_schema_version||'unknown',
    payload_sha256:sha(raw),
    payload_bytes:bytes(raw),
    compatibility_aliases:Array.isArray(input.aliases)?input.aliases.slice():[],
    namespace_classification:classification,
    state,
    quarantine_reasons:reasons,
    write_authority:classification==='HISTORIC_REFERENCE_ONLY'||classification==='UNKNOWN_NAMESPACE'?'NONE':(classification==='AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE'?'NO_CANONICAL_WRITE_UNTIL_P10_U4':'OWNER_REQUEST_ONLY'),
    delete_authority:'DENY_BY_DEFAULT_EXACT_OWNER_CAPABILITY_AND_CONFIRMATION_REQUIRED',
    _raw:raw
  }
}
function nativeRows(rule,parsed,raw){
  let out=[],base={storage_kind:'LOCAL_STORAGE',namespace:rule.namespace,owning_bank:rule.owning_bank,owner_id:rule.owner_id,schema_type:rule.schema_type,source_schema_version:sourceVersion(parsed),classification:rule.classification,aliases:[]};
  function add(id,value,bank,aliases){out.push(makeItem(Object.assign({},base,{native_id:id,raw:typeof value==='string'?value:JSON.stringify(value),owning_bank:bank||base.owning_bank,aliases:aliases||[]})))}
  if(rule.namespace==='pmp_master_bank_inventory_v1'&&parsed&&parsed.banks){
    Object.keys(parsed.banks).sort().forEach(bank=>{let b=parsed.banks[bank]||{};(Array.isArray(b.records)?b.records:[]).forEach((row,i)=>add(clean(row&&row.record_id)||`record:${bank}:${i}`,row,BANKS[bank]?bank:'master',[`container:${rule.namespace}`,`schema-version:${base.source_schema_version}`]))})
  }else if(rule.namespace==='pmp_helper_bank_index_v1'&&parsed&&Array.isArray(parsed.helpers)){
    parsed.helpers.forEach((row,i)=>add([row&&row.helper_id,row&&row.owning_bank,row&&row.record_id].map(clean).filter(Boolean).join(':')||`helper:${i}`,row,'helper',[`container:${rule.namespace}`]))
  }else if(rule.namespace==='pmp_bank_project_registry_v1'&&parsed&&Array.isArray(parsed.projects)){
    parsed.projects.forEach((row,i)=>add(clean(row&&row.id)||`project:${i}`,row,'continuous_run',[`container:${rule.namespace}`]))
  }else if(rule.namespace==='pmp_connections_bank_chat_memory_deposits_v1'&&parsed&&parsed.records&&typeof parsed.records==='object'){
    Object.keys(parsed.records).sort().forEach(id=>add(id,parsed.records[id],'connections',[`container:${rule.namespace}`]))
  }else if(Array.isArray(parsed)){
    parsed.forEach((row,i)=>add(clean(row&&(row.record_id||row.id||row.receipt_id||row.operation_id))||`entry:${i}`,row,base.owning_bank,[`container:${rule.namespace}`]))
  }
  if(!out.length)add(`${rule.namespace}:container`,raw,base.owning_bank,[`source-schema-version:${base.source_schema_version}`]);
  return out
}
function collisionPass(items){
  let groups={};items.forEach(x=>(groups[x.canonical_id]||(groups[x.canonical_id]=[])).push(x));
  Object.values(groups).forEach(rows=>{if(rows.length>1&&new Set(rows.map(x=>x.payload_sha256)).size>1)rows.forEach(x=>{x.state='QUARANTINED';x.quarantine_reasons=Array.from(new Set(x.quarantine_reasons.concat('IDENTITY_COLLISION'))).sort()})});
  return items
}
function snapshot(reason){
  let boundary=B(),counters={storage_reads:0,storage_writes:0,storage_deletes:0,key_enumerations:0,indexeddb_reads:0},items=[],known=new Set(RULES.map(x=>x[1]));
  if(!boundary||typeof boundary.readRaw!=='function'||typeof boundary.sha256!=='function'){
    let result={type:'PMP_BANK_INVENTORY_READONLY_PROJECTION_V1',version:VERSION,contract_version:CONTRACT,owner:OWNER,status:'OWNER_BOUNDARY_UNAVAILABLE',reason:clean(reason)||'snapshot',banks:{},items:[],indexeddb_namespaces:clone(INDEXED),summary:{items:0,active:0,reference_only:0,quarantined:0,stale:0,unavailable:0},effects:counters,rules:{read_only:true,helper_registration_conveys_authority:false,active_tab_conveys_authority:false,write_api_exposed:false,delete_api_exposed:false,migration_api_exposed:false,raw_payload_exposed:false}};lastSnapshot=result;return clone(result)
  }
  RULES.forEach(row=>{
    let rule=ruleFor(row[0],row[1]),raw=readRaw(rule.namespace,counters);if(raw==null)return;
    let parsed=null,reasons=[];try{parsed=JSON.parse(raw)}catch(e){reasons.push('CORRUPT_RECORD')}
    let rows=nativeRows(rule,parsed,raw);if(reasons.length)rows=rows.map(x=>Object.assign(x,{state:'QUARANTINED',quarantine_reasons:Array.from(new Set(x.quarantine_reasons.concat(reasons))).sort()}));items.push(...rows)
  });
  listKeys(counters).filter(k=>!known.has(k)&&/(?:bank|continuous[_-]?run)/i.test(k)).forEach(k=>{
    let raw=readRaw(k,counters);if(raw==null)return;items.push(makeItem({storage_kind:'LOCAL_STORAGE',namespace:k,native_id:k,owning_bank:'master',owner_id:null,schema_type:'PMP_UNKNOWN_SCHEMA',source_schema_version:'unknown',classification:'UNKNOWN_NAMESPACE',raw,reasons:['UNKNOWN_NAMESPACE','UNKNOWN_OWNER','UNKNOWN_SCHEMA_TYPE']}))
  });
  collisionPass(items);
  let banks={};Object.keys(BANKS).forEach(k=>banks[k]={name:BANKS[k],items:[],references:[]});
  items.forEach(item=>(banks[item.owning_bank||'master']||banks.master).items.push(publicItem(item)));
  Object.keys(banks).forEach(k=>banks[k].items.sort((a,b)=>String(a.canonical_id).localeCompare(String(b.canonical_id))));
  let publicItems=items.map(publicItem).sort((a,b)=>String(a.canonical_id).localeCompare(String(b.canonical_id)));
  let result={
    type:'PMP_BANK_INVENTORY_READONLY_PROJECTION_V1',
    version:VERSION,
    contract_version:CONTRACT,
    owner:OWNER,
    status:'READ_ONLY_PROJECTION_READY',
    reason:clean(reason)||'snapshot',
    banks,
    items:publicItems,
    indexeddb_namespaces:clone(INDEXED).map(x=>Object.assign({},x,{state:'DECLARED_NOT_OPENED_BY_P10_U3'})),
    summary:{
      items:publicItems.length,
      active:publicItems.filter(x=>x.state==='ACTIVE').length,
      reference_only:publicItems.filter(x=>x.state==='REFERENCE_ONLY').length,
      quarantined:publicItems.filter(x=>x.state==='QUARANTINED').length,
      stale:publicItems.filter(x=>x.state==='STALE').length,
      unavailable:publicItems.filter(x=>x.state==='UNAVAILABLE').length,
      exact_source_bytes_preserved:true,
      raw_payloads_exposed:0
    },
    effects:counters,
    rules:{
      read_only:true,
      owner_facts_only:true,
      helper_registration_conveys_authority:false,
      active_tab_conveys_authority:false,
      filename_conveys_authority:false,
      write_api_exposed:false,
      delete_api_exposed:false,
      migration_api_exposed:false,
      raw_payload_exposed:false,
      unknown_or_orphan_policy:'QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE',
      historic_namespace_policy:'REFERENCE_ONLY_NEVER_SILENTLY_MERGE',
      refresh_mode:'EXPLICIT_USER_OR_OWNER_EVENT_ONLY'
    }
  };
  lastSnapshot=result;return clone(result)
}
function bank(key,reason){let s=snapshot(reason||`bank:${key}`);return clone(s.banks[key]||null)}
const api=Object.freeze({version:VERSION,contract_version:CONTRACT,item_version:ITEM_VERSION,owner:OWNER,snapshot,bank,lastSnapshot:()=>clone(lastSnapshot),namespaceRules:Object.freeze(RULES.map(x=>Object.freeze({storage_kind:x[0],namespace:x[1],owner_id:x[2],classification:x[3],owning_bank:x[4],schema_type:x[5]}))),indexedDBNamespaces:Object.freeze(INDEXED.map(x=>Object.freeze(clone(x)))),rule:'Read-only Bank projection consumes Bank-owner facts. It exposes no write, delete, migration, Helper authority, active-tab authority, or raw payload API.'});
window.PMPBankInventoryReadonlyProjectionV1=api;
try{window.dispatchEvent(new CustomEvent('pmp:bank-inventory-readonly-projection-ready',{detail:{version:VERSION,owner:OWNER}}))}catch(e){}
})();
