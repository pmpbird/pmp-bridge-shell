(()=>{
'use strict';
const V='1.5.0-source-gate-requester-no-manifest-write-20260727A';
const ACTOR='pmp-continuous-run-bank-must-source-zip-v1.js';
const DB='pmp_continuous_run_bank_source_zip_db_v1';
const OS='files';
const TYPE='must_reference_source_zip';
function now(){return new Date().toISOString()}
function ownerApi(){return window.PMPContinuousRunBankTransferStoreV1||null}
function readManifest(){const api=ownerApi();return api&&typeof api.readManifest==='function'?api.readManifest():null}
function present(){const m=readManifest();return !!(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present&&m.must_reference_source_zip.indexeddb_key)}
function openDB(){return new Promise((resolve,reject)=>{try{const q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{try{q.result.createObjectStore(OS)}catch(e){}};q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error||Error('Source ZIP DB open failed'))}catch(e){reject(e)}})}
async function put(k,v){const db=await openDB();return new Promise((resolve,reject)=>{const tx=db.transaction(OS,'readwrite'),q=tx.objectStore(OS).put(v,k);q.onsuccess=()=>resolve(true);q.onerror=()=>reject(q.error||Error('Source ZIP write failed'))})}
async function sha(file){const buffer=await file.arrayBuffer(),digest=await crypto.subtle.digest('SHA-256',buffer);return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('')}
async function importSourceZip(file){
  if(!file)throw Error('Choose App Packets ZIP first.');
  if(!/\.zip$/i.test(file.name||''))throw Error('Must be a ZIP file.');
  if(Number(file.size||0)<1000)throw Error('ZIP is too small to be the source packets.');
  const api=ownerApi();
  if(!api||typeof api.commitSourceZip!=='function')throw Error('Bank transfer store owner is not ready.');
  const hash=await sha(file),key='must_reference_source_zip:latest',importedAt=now();
  await put(key,{type:'PMP_MUST_REFERENCE_SOURCE_ZIP_V1',version:V,owner:'source_gate_owner',file_name:file.name,size:file.size,hash,imported_at:importedAt,blob:file,rule:'Must-use source archive. Short packets remain operating map; source ZIP supplies proof, detail, and recovery body.'});
  return api.commitSourceZip({actor:ACTOR,source:{required:true,present:true,file_name:file.name,size:file.size,hash,imported_at:importedAt,indexeddb_key:key,rule:'Resident must reference this source ZIP. Metadata is committed only by the Bank transfer-store owner.'}});
}
function summary(){
  const m=readManifest()||{},z=m.source_zip_reader_level2,b=m.source_zip_extractor_level2b,c=m.source_pdf_text_level2d||m.source_pdf_text_level2c;
  return'Source ZIP: '+(present()?'PRESENT':'MISSING')+'\nLevel 2: '+(z?'PDFs '+z.pdf_count:'not read')+'\nLevel 2B: '+(b?'records '+b.note_count:'not extracted')+'\nLevel 2C: '+(c?'text records '+c.text_record_count+' / notes with text '+c.notes_with_text:'not recovered');
}
function load(src,flag){return new Promise((resolve,reject)=>{try{if(window[flag])return resolve();const s=document.createElement('script');s.src=src+'?fresh=sourcezip-requester-'+Date.now();s.onload=resolve;s.onerror=()=>reject(Error('load failed: '+src));(document.head||document.documentElement).appendChild(s)}catch(e){reject(e)}})}
async function runLevel(which){
  if(which==='2'){await load('pmp-source-zip-reader-level2-v1.js','PMPSourceZipReaderLevel2V1');return window.PMPSourceZipReaderLevel2V1.readZip()}
  if(which==='2b'){await load('pmp-source-zip-extractor-level2b-v1.js','PMPSourceZipExtractorLevel2BV1');return window.PMPSourceZipExtractorLevel2BV1.extractAll()}
  if(which==='2c'){await load('pmp-source-pdf-text-level2c-v1.js','PMPSourcePDFTextLevel2CV1');return window.PMPSourcePDFTextLevel2CV1.extractAll()}
  throw Error('Unknown source ZIP level: '+which);
}
function scan(){return{status:ownerApi()?'OWNER_READY':'OWNER_NOT_READY',manifest_write:false}}
window.PMPMustReferenceSourceZipV1={version:V,owner:'source_gate_owner',actor:ACTOR,data_only:true,scan,importSourceZip,present,type:TYPE,summary,runLevel,rule:'Owns source ZIP blob import only. Requests metadata commit from the Bank transfer-store owner and never writes the canonical manifest or receipt.'};
})();
