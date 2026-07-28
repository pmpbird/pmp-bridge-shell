(()=>{
'use strict';
const V='2.3.0-exclusive-bank-writer-broker-20260727A';
const OWNER='bank_screen_owner';
const WRITER='pmp-continuous-run-bank-transfer-store-v2.js';
const MANIFEST_KEY='pmp_continuous_run_bank_transfer_store_manifest_v1';
const RECEIPT_KEY='pmp_continuous_run_bank_transfer_store_receipts_v1';
const DB='pmp_continuous_run_bank_transfer_store_db_v1',OS='items';
const SOURCE_ZIP='must_reference_source_zip';
const SLOT_REQUIRED=[
  {type:'transfer_pack',label:'Transfer Pack'},
  {type:'packet_1_5_guide',label:'Packet 1.5 Guide'},
  {type:'current_work_source',label:'Current Work Source'},
  {type:'receipts_or_state',label:'Receipts or State'},
  {type:'receiver_test_checklist',label:'Receiver Test Checklist / Rules'}
];
const LOSSLESS_REQUIRED=[
  {type:'transfer_pack',label:'Transfer Pack',min:1000,terms:['lossless','transfer']},
  {type:'packet_0',label:'Packet 0',min:100,terms:['packet 0']},
  {type:'packet_1',label:'Packet 1',min:100,terms:['packet 1']},
  {type:'packet_1_5_guide',label:'Packet 1.5 Guide',min:500,terms:['packet 1.5']},
  {type:'raw_packets',label:'Raw Packets 04-26 / 06.5',min:500,terms:['packet']},
  {type:'current_work_source',label:'Current Work Source',min:200,terms:['pmp']},
  {type:'receipts_or_state',label:'Receipts or State',min:100,terms:['receipt','state']},
  {type:'receiver_test_checklist',label:'Receiver Test Checklist / Rules',min:200,terms:['receiver','test']},
  {type:'no_spend_rules',label:'No-Spend / Permission Rules',min:50,terms:['spend','paid']}
];
const BAD=['test','testing','placeholder','sample','example','asdf','none','n/a','na','todo','tbd'];
function now(){return new Date().toISOString()}
function j(k,d){try{let v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function save(k,v){localStorage.setItem(k,JSON.stringify(v,null,2));return v}
function hash(t){let h=2166136261;t=String(t||'');for(let i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,'0')}
function lines(t){t=String(t||'');return t?t.split(/\r\n|\r|\n/).length:0}
function words(t){t=String(t||'').trim();return t?t.split(/\s+/).length:0}
function uid(){return 'transfer_item_'+Date.now()+'_'+Math.random().toString(16).slice(2)}
function sourceZipPresent(m){return !!(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present&&m.must_reference_source_zip.indexeddb_key)}
function sourceMode(m){return sourceZipPresent(m)?'SOURCE ZIP PRESENT':'MISSING'}
function cleanOldLong(m){m=m||{};m.lossless_required=(m.lossless_required||[]).filter(x=>!(x&&x.type==='long_packet_0_26'));if(m.verification){m.verification.lossless_required=(m.verification.lossless_required||[]).filter(x=>!(x&&x.type==='long_packet_0_26'));m.verification.lossless_missing=(m.verification.lossless_missing||[]).filter(x=>x!=='long_packet_0_26')}m.must_reference_long_source_00_26={required:true,present:sourceZipPresent(m),mode:sourceMode(m),rule:'Short packets control the operating map. App Packets ZIP is the must-reference long source body.'};return m}
function openDB(){return new Promise((res,rej)=>{try{let q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{try{q.result.createObjectStore(OS)}catch(e){}};q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('IndexedDB open failed'))}catch(e){rej(e)}})}
async function idbPut(k,v){let db=await openDB();return await new Promise((res,rej)=>{let tx=db.transaction(OS,'readwrite'),st=tx.objectStore(OS),q=st.put(v,k);q.onsuccess=()=>res(true);q.onerror=()=>rej(q.error||Error('IndexedDB write failed'))})}
async function idbGet(k){let db=await openDB();return await new Promise((res,rej)=>{let tx=db.transaction(OS,'readonly'),st=tx.objectStore(OS),q=st.get(k);q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('IndexedDB read failed'))})}
function blank(){return cleanOldLong({type:'PMP_CONTINUOUS_RUN_BANK_STAGING_TRANSFER_STORE_MANIFEST_V2',version:V,owner:OWNER,bank:'continuous_run',updated_at:now(),slot_check_passed:false,lossless_verified:false,verified:false,verification:{status:'not_checked',missing:SLOT_REQUIRED.map(x=>x.type),lossless_missing:LOSSLESS_REQUIRED.map(x=>x.type).concat([SOURCE_ZIP]),weak_items:[],last_checked_at:null},rule:'Engine can run only when required source material, rules, receipts, and source ZIP are verified. Short packets control the operating map; source ZIP supplies proof/detail/recovery.',required:SLOT_REQUIRED,lossless_required:LOSSLESS_REQUIRED,source_required:{type:SOURCE_ZIP,label:'Must-Reference Source ZIP'},items:{},must_reference_source_zip:{required:true,present:false}})}
function readManifest(){let m=j(MANIFEST_KEY,null);if(!m||!m.type)m=blank();if(!m.items)m.items={};m=cleanOldLong(m);m.type='PMP_CONTINUOUS_RUN_BANK_STAGING_TRANSFER_STORE_MANIFEST_V2';m.version=V;m.owner=OWNER;m.bank='continuous_run';m.required=SLOT_REQUIRED;m.lossless_required=LOSSLESS_REQUIRED;m.source_required={type:SOURCE_ZIP,label:'Must-Reference Source ZIP'};if(!m.must_reference_source_zip)m.must_reference_source_zip={required:true,present:false};m.verified=!!m.lossless_verified;return save(MANIFEST_KEY,m)}
function receipts(){let r=j(RECEIPT_KEY,[]);return Array.isArray(r)?r:[]}
function appendReceipt(x){let r=receipts(),item=Object.assign({type:'PMP_STAGING_TRANSFER_STORE_RECEIPT_V2',owner:OWNER,bank:'continuous_run',at:now(),id:uid()},x||{});r.push(item);save(RECEIPT_KEY,r);try{let api=window.PMPContinuousWorkEngineStateV1||window.PMPContinuousRunStateBankV1;if(api&&api.appendReceipt)api.appendReceipt({type:item.action||'PMP_STAGING_TRANSFER_STORE_RECEIPT_V2',staging_transfer_store_receipt:item})}catch(e){}return item}
function commitSourceZip(request){
  request=request||{};
  if(request.actor!=='pmp-continuous-run-bank-must-source-zip-v1.js')throw Error('REJECTED_SOURCE_ZIP_REQUESTER');
  const source=request.source;
  if(!source||source.present!==true||!source.indexeddb_key)throw Error('REJECTED_SOURCE_ZIP_METADATA');
  let m=readManifest();
  m.must_reference_source_zip=Object.assign({required:true},source);
  m.slot_check_passed=false;m.lossless_verified=false;m.verified=false;m.updated_at=now();
  save(MANIFEST_KEY,m);
  appendReceipt({action:'commit_must_reference_source_zip_metadata_v2',requested_by:request.actor,summary:'Bank owner committed must-reference source ZIP metadata',file_name:source.file_name,size:source.size,hash:source.hash});
  return m.must_reference_source_zip;
}
function commitSourceStage(request){
  request=request||{};
  const allowed={
    'pmp-source-zip-reader-level2-v1.js':'source_zip_reader_level2',
    'pmp-source-zip-extractor-level2b-v1.js':'source_zip_extractor_level2b',
    'pmp-source-pdf-text-level2c-v1.js':'source_pdf_text_level2c',
    'pmp-source-reference-gate-level4-v1.js':'source_reference_gate_level4'
  };
  const field=allowed[request.actor];
  if(!field||request.field!==field)throw Error('REJECTED_SOURCE_STAGE_REQUESTER_OR_FIELD');
  if(!request.value||typeof request.value!=='object')throw Error('REJECTED_SOURCE_STAGE_VALUE');
  let m=readManifest();
  m[field]=request.value;
  if(field==='source_pdf_text_level2c')delete m.source_pdf_text_level2d;
  m.slot_check_passed=false;m.lossless_verified=false;m.verified=false;m.updated_at=now();
  save(MANIFEST_KEY,m);
  appendReceipt({action:'commit_source_stage_metadata_v2',requested_by:request.actor,field,summary:'Bank owner committed '+field+' metadata'});
  return m[field];
}
function presentTypes(m){let a=[];Object.keys(m.items||{}).forEach(t=>{if(Object.keys(m.items[t]||{}).length)a.push(t)});return a}
function bestMeta(m,t){let b=m.items&&m.items[t]||{},ids=Object.keys(b);if(!ids.length)return null;ids.sort((a,c)=>String(b[c].imported_at||'').localeCompare(String(b[a].imported_at||'')));return b[ids[0]]}
function q(kind,text,meta){text=String(text||'');meta=meta||{};let body=text.trim(),lower=body.toLowerCase(),rule=LOSSLESS_REQUIRED.find(x=>x.type===kind)||{min:50,terms:[]},issues=[],chars=Number(meta.characters||body.length||0),wc=Number(meta.word_count||words(body)||0);if(!chars)issues.push('empty_content');if(chars<rule.min)issues.push('too_short_min_'+rule.min+'_chars');if(wc<10&&chars<200)issues.push('too_few_words');if(BAD.includes(lower)||/^test\s*\d*$/i.test(body)||/^sample\s*\d*$/i.test(body))issues.push('placeholder_text');let terms=rule.terms||[];if(terms.length&&body&&chars>=rule.min&&!terms.some(t=>lower.includes(t)))issues.push('expected_terms_missing_'+terms.join('_or_'));return{ok:issues.length===0,issues,chars,word_count:wc,min_chars:rule.min}}
async function importItem(input){input=input||{};let kind=String(input.item_type||input.kind||'current_work_source').trim()||'current_work_source',text=String(input.text||'');if(!text.trim())throw Error('Paste real staging material first.');let name=String(input.name||kind).trim()||kind,id=String(input.id||kind).trim()||kind,key='continuous_run_transfer_store:'+kind+':'+id+':latest',quality=q(kind,text,{characters:text.length,word_count:words(text)});let stored={type:'PMP_STAGING_TRANSFER_STORE_ITEM_V2',version:V,bank:'continuous_run',item_type:kind,item_id:id,name,imported_at:now(),text,sha256_like:hash(text),characters:text.length,line_count:lines(text),word_count:words(text),quality};await idbPut(key,stored);let m=readManifest();m.items[kind]=m.items[kind]||{};m.items[kind][id]={item_type:kind,item_id:id,name,indexeddb_key:key,characters:stored.characters,line_count:stored.line_count,word_count:stored.word_count,hash:stored.sha256_like,imported_at:stored.imported_at,status:'stored',quality};m.slot_check_passed=false;m.lossless_verified=false;m.verified=false;m.updated_at=now();save(MANIFEST_KEY,m);appendReceipt({action:'import_staging_transfer_store_item_v2',summary:'Imported '+kind+' into Continuous Run Bank Staging Transfer Store',item_type:kind,item_id:id,quality});return{item:stored,manifest:verifyStore(false).manifest}}
function verifyStore(writeReceipt=true){let m=readManifest(),present=presentTypes(m),missing=SLOT_REQUIRED.filter(x=>!present.includes(x.type)).map(x=>x.type),empty=[];present.forEach(t=>Object.keys(m.items[t]||{}).forEach(id=>{let it=m.items[t][id];if(!it.characters)empty.push(t+':'+id)}));let slot=missing.length===0&&empty.length===0,losslessMissing=LOSSLESS_REQUIRED.filter(x=>!present.includes(x.type)).map(x=>x.type),weak=[];LOSSLESS_REQUIRED.forEach(rule=>{let meta=bestMeta(m,rule.type);if(!meta)return;let quality=meta.quality||q(rule.type,'',meta);if(!quality.ok)weak.push({item_type:rule.type,item_id:meta.item_id||'',name:meta.name||'',issues:quality.issues||[],characters:meta.characters||0,required_min_chars:quality.min_chars||rule.min})});if(!sourceZipPresent(m))losslessMissing.push(SOURCE_ZIP);let lossless=slot&&losslessMissing.length===0&&weak.length===0;m.slot_check_passed=slot;m.lossless_verified=lossless;m.verified=lossless;m.verification={status:lossless?'lossless_verified':(slot?'slot_check_passed_lossless_not_verified':'missing_required_slots'),slot_check_passed:slot,lossless_verified:lossless,missing,empty,lossless_missing:losslessMissing,weak_items:weak,last_checked_at:now(),required:SLOT_REQUIRED,lossless_required:LOSSLESS_REQUIRED,source_required:{type:SOURCE_ZIP,label:'Must-Reference Source ZIP'},present,must_reference_source_zip_present:sourceZipPresent(m),long_source_00_26_present:sourceZipPresent(m),long_source_00_26_mode:sourceMode(m)};m.updated_at=now();save(MANIFEST_KEY,m);if(writeReceipt)appendReceipt({action:'verify_staging_transfer_store_v2',summary:lossless?'Lossless Verified':(slot?'Slot Check Passed; Lossless NOT verified':'Slot Check not passed'),slot_check_passed:slot,lossless_verified:lossless,missing,lossless_missing:losslessMissing,weak_items:weak,must_reference_source_zip_present:sourceZipPresent(m)});return{slot_check_passed:slot,lossless_verified:lossless,verified:lossless,missing,empty,lossless_missing:losslessMissing,weak_items:weak,manifest:m}}
function engineGate(){let v=verifyStore(false),missing=[...(v.missing||[]),...(v.lossless_missing||[])];(v.weak_items||[]).forEach(x=>missing.push('weak:'+x.item_type+':'+(x.issues||[]).join('|')));return{ok:!!v.lossless_verified,reason:v.lossless_verified?'lossless_verified':'staging_transfer_store_not_lossless_verified',missing,slot_check_passed:!!v.slot_check_passed,lossless_verified:!!v.lossless_verified,weak_items:v.weak_items||[],message:v.lossless_verified?'Staging Transfer Store lossless verified.':'Staging Transfer Store is not lossless verified.',manifest:v.manifest}}
async function exportStore(){let m=readManifest(),items=[];for(const t of Object.keys(m.items||{})){for(const id of Object.keys(m.items[t]||{})){let meta=m.items[t][id],full=null;try{full=await idbGet(meta.indexeddb_key)}catch(e){}items.push({meta,full})}}return{type:'PMP_CONTINUOUS_RUN_BANK_STAGING_TRANSFER_STORE_EXPORT_V2',version:V,exported_at:now(),bank:'continuous_run',manifest:m,receipts:receipts(),items}}
function statusText(){let v=verifyStore(false),m=v.manifest,rows=[];rows.push('Slot Check: '+(v.slot_check_passed?'PASSED':'NOT PASSED'));rows.push('Lossless Verified: '+(v.lossless_verified?'YES':'NO'));rows.push('Missing required slots: '+(v.missing.length?v.missing.join(', '):'none'));rows.push('Missing lossless items: '+(v.lossless_missing.length?v.lossless_missing.join(', '):'none'));rows.push('Items:');Object.keys(m.items||{}).sort().forEach(t=>Object.keys(m.items[t]||{}).sort().forEach(id=>{let x=m.items[t][id];rows.push('['+t+'] '+(x.name||id)+' | chars '+x.characters+' | hash '+x.hash)}));return rows.join('\n')}
function scan(){return false}
window.PMPContinuousRunBankTransferStoreV1={version:V,owner:OWNER,writer:WRITER,data_only:true,required:SLOT_REQUIRED,lossless_required:LOSSLESS_REQUIRED,keys:{MANIFEST_KEY,RECEIPT_KEY,DB,OS},readManifest,receipts,importItem,commitSourceZip,commitSourceStage,verifyStore,engineGate,exportStore,statusText,scan};
readManifest();
})();
