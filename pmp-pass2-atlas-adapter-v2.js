(()=>{
'use strict';
const V='2.0.1-pass2-atlas-adapter-v2-contract';
const OWNER='pmp-pass2-atlas-adapter-v2';
const FILES=['pmp-pass2-atlas-adapter-v2.js','pmp-authority-rules-v1.js','pmp-active-bug-found-contract-v1.js','pmp-bug-watch-passive-capture-v1.js','pmp-current-inner-cleanbug-rgcontrols-v25.html'];
const BUCKET='ACTIVE_CURRENT_APP';
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean)));}
function clone(x){try{return JSON.parse(JSON.stringify(x||{}))}catch(e){return {}}}
function fileOwner(p){return p.indexOf('bug-watch')>-1?'Bug Watch Passive Capture':p.indexOf('contract')>-1?'Active Bug Found Contract':p.indexOf('v25')>-1?'Pass 2 v25 Shell':'Pass 2 Authority'}
function addFileRecord(r,path){r.files=Array.isArray(r.files)?r.files.slice():[];if(!r.files.some(f=>f&&f.path===path))r.files.push({path,bucket:BUCKET,owner:fileOwner(path),policy:'Pass 2 passive support file'});}
function patchRegistryReport(base){let r=clone(base);r.pass2_atlas_adapter={version:V,owner:OWNER,mode:'runtime_atlas_view_only',files:FILES.slice(),passive_only:true,indexeddb_write:false};r.repo_file_classification=r.repo_file_classification||{};r.repo_file_classification[BUCKET]=uniq([].concat(r.repo_file_classification[BUCKET]||[],FILES));FILES.forEach(p=>addFileRecord(r,p));['active_expected','expected_files','ACTIVE_EXPECTED'].forEach(k=>{if(Array.isArray(r[k]))r[k]=uniq(r[k].concat(FILES))});return r;}
function wrap(base){if(!base||base.__pass2_atlas_adapter_v2)return base;let out=Object.create(base);try{Object.keys(base).forEach(k=>{if(k!=='registry')out[k]=base[k]})}catch(e){}out.__pass2_atlas_adapter_v2=true;out.pass2_atlas_adapter_version=V;out.registry=function(){let r={};try{r=typeof base.registry==='function'?base.registry():{}}catch(e){r={registry_error:String(e&&e.message||e)}}return patchRegistryReport(r)};out.report=function(){return {type:'PMP_PASS2_ATLAS_ADAPTER_V2_REPORT',version:V,owner:OWNER,files:FILES.slice(),passive_only:true,indexeddb_write:false}};return out;}
let current=null;
try{if(window.PMPMountRegistryV1)current=wrap(window.PMPMountRegistryV1);Object.defineProperty(window,'PMPMountRegistryV1',{configurable:true,get(){return current},set(v){current=wrap(v)}})}catch(e){try{window.PMPPass2AtlasAdapterV2Error=String(e&&e.message||e)}catch(_) {}}
window.PMPPass2AtlasAdapterV2={version:V,owner:OWNER,files:FILES.slice(),wrap,patchRegistryReport};
})();
