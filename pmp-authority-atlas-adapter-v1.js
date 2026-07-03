(()=>{
'use strict';
const V='2.0.1-pass2-atlas-adapter-bug-watch';
const OWNER='pmp-authority-atlas-adapter-v1';
const FILES=['pmp-authority-atlas-adapter-v1.js','pmp-authority-rules-v1.js','pmp-bug-watch-passive-capture-v1.js'];
const BUCKET='ACTIVE_CURRENT_APP';
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean)));}
function clone(x){try{return JSON.parse(JSON.stringify(x||{}))}catch(e){return {}}}
function ownerFor(path){return /bug-watch/i.test(path)?'Bug Watch Passive Capture':'Authority Rules'}
function policyFor(path){return /bug-watch/i.test(path)?'passive capture to Bug Bank Active Bugs Found only; no fix/delete/move/reroute':'passive authority map; no mutation authority'}
function addFileRecord(r,path){r.files=Array.isArray(r.files)?r.files.slice():[];if(!r.files.some(f=>f&&f.path===path))r.files.push({path,bucket:BUCKET,owner:ownerFor(path),policy:policyFor(path)});}
function patchRegistryReport(base){let r=clone(base);r.authority_atlas_adapter={version:V,owner:OWNER,mode:'runtime_atlas_view_only',files:FILES.slice(),passive_only:true,storage_write:'append_merge_active_bug_found_only_for_bug_watch',indexeddb_write:false};r.repo_file_classification=r.repo_file_classification||{};r.repo_file_classification[BUCKET]=uniq([].concat(r.repo_file_classification[BUCKET]||[],FILES));FILES.forEach(p=>addFileRecord(r,p));['active_expected','expected_files','ACTIVE_EXPECTED'].forEach(k=>{if(Array.isArray(r[k]))r[k]=uniq(r[k].concat(FILES))});return r;}
function wrap(base){if(!base||base.__authority_atlas_adapter_v1)return base;let out=Object.create(base);try{Object.keys(base).forEach(k=>{if(k!=='registry')out[k]=base[k]})}catch(e){}out.__authority_atlas_adapter_v1=true;out.authority_atlas_adapter_version=V;out.registry=function(){let r={};try{r=typeof base.registry==='function'?base.registry():{}}catch(e){r={registry_error:String(e&&e.message||e)}}return patchRegistryReport(r)};out.report=function(){return {type:'PMP_PASS2_ATLAS_ADAPTER_REPORT_V1',version:V,owner:OWNER,files:FILES.slice(),passive_only:true,storage_write:'append_merge_active_bug_found_only_for_bug_watch',indexeddb_write:false,mutation_scope:'runtime_registry_view_wrap_only'}};return out;}
let current=null;
try{
  if(window.PMPMountRegistryV1)current=wrap(window.PMPMountRegistryV1);
  Object.defineProperty(window,'PMPMountRegistryV1',{configurable:true,get(){return current},set(v){current=wrap(v)}});
}catch(e){try{window.PMPAuthorityAtlasAdapterV1Error=String(e&&e.message||e)}catch(_) {}}
window.PMPAuthorityAtlasAdapterV1={version:V,owner:OWNER,files:FILES.slice(),wrap,patchRegistryReport};
})();
