(()=>{
'use strict';
const V='1.0.0-exclusive-owner-runtime-20260727A';
const OWNER='app_orchestrator_owner';
const REGISTRY_URL='pmp-app-orchestrator-ownership-registry-v1.json';
const RECEIPT_KEY='pmp_app_orchestrator_ownership_runtime_v1_receipt';
let registry=null,last=null;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function resources(){return registry&&Array.isArray(registry.resources)?registry.resources:[]}
function resource(id){return resources().find(x=>x.id===id)||null}
function canWrite(actor,id){
  const row=resource(id);
  if(!row)return{allowed:false,code:'REJECTED_UNKNOWN_RESOURCE',actor,resource_id:id};
  const allowed=row.writer===actor;
  return{allowed,code:allowed?'ALLOWED_EXACT_OWNER':'REJECTED_NOT_CANONICAL_WRITER',actor,resource_id:id,canonical_writer:row.writer,owner:row.owner};
}
function canRequest(actor,id){
  const row=resource(id);
  if(!row)return{allowed:false,code:'REJECTED_UNKNOWN_RESOURCE',actor,resource_id:id};
  const allowed=row.writer===actor||(row.requesters||[]).includes(actor)||(row.readers||[]).includes(actor);
  return{allowed,code:allowed?'ALLOWED_DECLARED_PARTICIPANT':'REJECTED_UNDECLARED_PARTICIPANT',actor,resource_id:id,canonical_writer:row.writer,owner:row.owner};
}
function audit(reason){
  const duplicateIds=[];
  try{
    const seen={};
    document.querySelectorAll('[id]').forEach(el=>{seen[el.id]=(seen[el.id]||0)+1});
    Object.keys(seen).filter(id=>seen[id]>1).forEach(id=>duplicateIds.push({id,count:seen[id]}));
  }catch(e){}
  last={
    type:'PMP_APP_ORCHESTRATOR_OWNERSHIP_RUNTIME_RECEIPT_V1',
    version:V,
    owner:OWNER,
    at:now(),
    reason:reason||'audit',
    registry_version:registry&&registry.version||'not_loaded',
    resources_checked:resources().length,
    duplicate_ids_in_owner_frame:duplicateIds,
    status:registry?(duplicateIds.length?'NEEDS_REVIEW':'PASS'):'REGISTRY_NOT_LOADED',
    enforcement:{
      canonical_writer_lookup:true,
      undeclared_actor_fail_closed:true,
      helper_write_authority:false,
      persisted_user_data_mutation:false,
      storage_migration:false,
      dom_repair:false
    }
  };
  return put(RECEIPT_KEY,last);
}
async function load(){
  try{
    const response=await fetch(REGISTRY_URL+'?fresh='+Date.now(),{cache:'no-store'});
    if(!response.ok)throw Error('ownership registry HTTP '+response.status);
    registry=await response.json();
    return audit('registry_loaded');
  }catch(error){
    last={type:'PMP_APP_ORCHESTRATOR_OWNERSHIP_RUNTIME_RECEIPT_V1',version:V,owner:OWNER,at:now(),status:'FAIL_CLOSED',error:String(error&&error.message||error),resources_checked:0};
    return put(RECEIPT_KEY,last);
  }
}
const api={version:V,owner:OWNER,registry:()=>registry,resource,canWrite,canRequest,audit,last:()=>last,load,receiptKey:RECEIPT_KEY};
window.PMPAppOrchestratorOwnershipRuntimeV1=api;
try{T().PMPAppOrchestratorOwnershipRuntimeV1=api}catch(e){}
load();
})();
