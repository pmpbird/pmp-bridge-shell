(()=>{
'use strict';
const VERSION='1.0.0-pass2-p2b-exact-source-gate';
const TYPE='PMP_ACTOR_AUTHORITY_GATE_V1';
const POLICY_TYPE='PMP_ACTOR_AUTHORITY_POLICY_V1';
const DENY_CODE='PMP_ACTOR_AUTHORITY_DENIED';
const tokenSet=new WeakSet();
const state={configured:false,installed:false,policy:null,actors:new Map(),manifest:new Map(),current:null,denials:[],native:{},listenerMap:new WeakMap()};
class PMPActorAuthorityDeniedError extends Error{
  constructor(reason,detail){super(reason);this.name='PMPActorAuthorityDeniedError';this.code=DENY_CODE;this.reason=reason;this.detail=detail||null;}
}
function now(){return new Date().toISOString()}
function clone(value){return value==null?value:JSON.parse(JSON.stringify(value))}
function normalizePath(value){
  let raw=String(value||'').trim();
  if(!raw)return '';
  try{raw=new URL(raw,globalThis.location&&globalThis.location.href||'http://pmp.invalid/').pathname}catch(e){}
  raw=raw.replace(/^\/+/, '').split('?')[0].split('#')[0];
  return raw;
}
function hex(buffer){return Array.from(new Uint8Array(buffer)).map(v=>v.toString(16).padStart(2,'0')).join('')}
async function sha256Text(text){
  if(!globalThis.crypto||!globalThis.crypto.subtle)throw new Error('Web Crypto SHA-256 is required.');
  return hex(await globalThis.crypto.subtle.digest('SHA-256',new TextEncoder().encode(String(text))));
}
function manifestRecords(manifest){
  if(Array.isArray(manifest))return manifest;
  if(manifest&&Array.isArray(manifest.records))return manifest.records;
  throw new Error('Exact-source manifest records are required.');
}
function validatePolicy(policy){
  if(!policy||policy.type!==POLICY_TYPE)throw new Error('Actor authority policy type is invalid.');
  if(policy.algorithm!=='SHA-256')throw new Error('Actor authority policy must use SHA-256.');
  if(policy.unknown_actor_policy!=='BLOCK_BEFORE_SIDE_EFFECT')throw new Error('Unknown actor policy must fail closed.');
  if(policy.unauthorized_capability_policy!=='BLOCK_BEFORE_SIDE_EFFECT')throw new Error('Unauthorized capability policy must fail closed.');
  if(!Array.isArray(policy.actors)||!policy.actors.length)throw new Error('Actor authority policy has no actors.');
}
function configure(options){
  const policy=options&&options.policy,manifest=options&&options.manifest;
  validatePolicy(policy);
  const nextActors=new Map(),nextManifest=new Map();
  for(const record of manifestRecords(manifest)){
    const path=normalizePath(record&&record.path);
    const digest=String((record&&(record.sha256_hex||record.sha256))||'').toLowerCase();
    if(!path||!/^[0-9a-f]{64}$/.test(digest))continue;
    if(nextManifest.has(path))throw new Error('Duplicate exact-source manifest path: '+path);
    nextManifest.set(path,{path,sha256:digest});
  }
  for(const actor of policy.actors){
    const path=normalizePath(actor&&actor.path),digest=String(actor&&actor.sha256||'').toLowerCase();
    if(!path||!/^[0-9a-f]{64}$/.test(digest))throw new Error('Policy actor identity is invalid.');
    if(nextActors.has(path))throw new Error('Duplicate policy actor path: '+path);
    const record=nextManifest.get(path);
    if(!record||record.sha256!==digest)throw new Error('Policy actor is not exact-source manifest-backed: '+path);
    nextActors.set(path,Object.freeze({
      path,sha256:digest,role:String(actor.role||'actor'),owner:String(actor.owner||path),phase:String(actor.phase||'declared'),
      stop_condition:String(actor.stop_condition||'bounded'),capabilities:Object.freeze((actor.capabilities||[]).map(String).sort())
    }));
  }
  state.policy=clone(policy);state.actors=nextActors;state.manifest=nextManifest;state.configured=true;
  return report();
}
function deny(reason,capability,detail,actor){
  const entry=Object.freeze({type:'PMP_ACTOR_AUTHORITY_DENIAL_V1',at:now(),reason:String(reason),capability:String(capability||''),actor:actor?actor.path:null,detail:clone(detail)});
  state.denials.push(entry);if(state.denials.length>200)state.denials.splice(0,state.denials.length-200);
  throw new PMPActorAuthorityDeniedError(reason,entry);
}
function requireActor(){
  const token=state.current;
  if(!token||!tokenSet.has(token))return deny('UNKNOWN_ACTOR','actor_identity',null,null);
  return token;
}
function requireCapability(capability,detail){
  const token=requireActor(),actor=token.actor;
  if(actor.capabilities.indexOf(String(capability))<0)return deny('UNAUTHORIZED_CAPABILITY',capability,detail,actor);
  return token;
}
async function authorizeSource(path,sourceText){
  if(!state.configured)throw new Error('Actor authority gate is not configured.');
  const normalized=normalizePath(path),actor=state.actors.get(normalized);
  if(!actor)return deny('UNKNOWN_ACTOR','actor_identity',{path:normalized},null);
  const actual=await sha256Text(sourceText);
  if(actual!==actor.sha256)return deny('SOURCE_DIGEST_MISMATCH','actor_identity',{path:normalized,expected:actor.sha256,actual},actor);
  const token=Object.freeze({type:'PMP_AUTHORIZED_ACTOR_TOKEN_V1',actor,authorized_at:now()});
  tokenSet.add(token);return token;
}
function run(token,fn,thisArg,args){
  if(!tokenSet.has(token))return deny('INVALID_ACTOR_TOKEN','actor_identity',null,null);
  if(typeof fn!=='function')throw new TypeError('Authorized actor callback must be a function.');
  const previous=state.current;state.current=token;
  try{return fn.apply(thisArg,args||[])}finally{state.current=previous}
}
function wrapCallback(token,callback){return typeof callback==='function'?function(){return run(token,callback,this,Array.from(arguments))}:callback}
function patchMethod(target,name,capability,detailFactory){
  if(!target||typeof target[name]!=='function')return;
  const original=target[name];
  state.native[name+'@'+(target.constructor&&target.constructor.name||'object')]=original;
  try{Object.defineProperty(target,name,{configurable:true,writable:true,value:function(){
    const args=Array.from(arguments),cap=typeof capability==='function'?capability.call(this,args):capability;
    requireCapability(cap,detailFactory?detailFactory.call(this,args):{method:name});
    return original.apply(this,args);
  }});}catch(e){throw new Error('Cannot install authority guard for '+name+': '+String(e&&e.message||e))}
}
function patchSetter(proto,name,capability,detailFactory){
  if(!proto)return;const descriptor=Object.getOwnPropertyDescriptor(proto,name);
  if(!descriptor||typeof descriptor.set!=='function'||descriptor.set.__pmpAuthorityWrapped)return;
  const nativeSet=descriptor.set;
  function guarded(value){requireCapability(capability,detailFactory?detailFactory.call(this,value):{property:name});return nativeSet.call(this,value)}
  guarded.__pmpAuthorityWrapped=true;
  try{Object.defineProperty(proto,name,{...descriptor,set:guarded})}catch(e){throw new Error('Cannot install authority setter guard for '+name+': '+String(e&&e.message||e))}
}
function install(){
  if(!state.configured)throw new Error('Configure the gate before installing guards.');
  if(state.installed)return report();
  if(globalThis.Storage&&globalThis.Storage.prototype){
    patchMethod(Storage.prototype,'setItem','storage_write',args=>({operation:'setItem',key:String(args[0])}));
    patchMethod(Storage.prototype,'removeItem','storage_delete',args=>({operation:'removeItem',key:String(args[0])}));
    patchMethod(Storage.prototype,'clear','storage_clear',()=>({operation:'clear'}));
  }
  if(globalThis.Node&&globalThis.Node.prototype){
    patchMethod(Node.prototype,'appendChild',args=>{
      const node=args[0],tag=String(node&&node.tagName||'').toLowerCase();
      return tag==='script'?'script_injection':'dom_write';
    },args=>({operation:'appendChild',tag:String(args[0]&&args[0].tagName||'').toLowerCase(),src:normalizePath(args[0]&&args[0].src||'')}));
    patchMethod(Node.prototype,'insertBefore',args=>String(args[0]&&args[0].tagName||'').toLowerCase()==='script'?'script_injection':'dom_write',args=>({operation:'insertBefore',tag:String(args[0]&&args[0].tagName||'').toLowerCase()}));
    patchMethod(Node.prototype,'replaceChild',args=>String(args[0]&&args[0].tagName||'').toLowerCase()==='script'?'script_injection':'dom_write',args=>({operation:'replaceChild',tag:String(args[0]&&args[0].tagName||'').toLowerCase()}));
    patchMethod(Node.prototype,'removeChild','dom_delete',args=>({operation:'removeChild',tag:String(args[0]&&args[0].tagName||'').toLowerCase()}));
  }
  if(globalThis.Element&&globalThis.Element.prototype){
    patchMethod(Element.prototype,'setAttribute',args=>['src','href','action'].includes(String(args[0]||'').toLowerCase())?'resource_target_change':'dom_write',args=>({operation:'setAttribute',name:String(args[0]),value:String(args[1]||'').slice(0,300)}));
    patchMethod(Element.prototype,'insertAdjacentHTML','dom_write',args=>({operation:'insertAdjacentHTML',position:String(args[0])}));
    patchSetter(Element.prototype,'innerHTML','dom_write',value=>({operation:'innerHTML',length:String(value||'').length}));
    patchSetter(Element.prototype,'outerHTML','dom_write',value=>({operation:'outerHTML',length:String(value||'').length}));
  }
  if(globalThis.HTMLScriptElement)patchSetter(HTMLScriptElement.prototype,'src','resource_target_change',value=>({element:'script',src:normalizePath(value)}));
  if(globalThis.HTMLIFrameElement)patchSetter(HTMLIFrameElement.prototype,'src','navigation',value=>({element:'iframe',src:normalizePath(value)}));
  if(globalThis.Document&&globalThis.Document.prototype)patchMethod(Document.prototype,'write','document_write',args=>({operation:'document.write',length:String(args[0]||'').length}));
  if(globalThis.History&&globalThis.History.prototype){
    patchMethod(History.prototype,'pushState','navigation',args=>({operation:'pushState',url:String(args[2]||'')}));
    patchMethod(History.prototype,'replaceState','navigation',args=>({operation:'replaceState',url:String(args[2]||'')}));
  }
  if(typeof globalThis.open==='function')patchMethod(globalThis,'open','navigation',args=>({operation:'window.open',url:String(args[0]||'')}));
  if(typeof globalThis.fetch==='function')patchMethod(globalThis,'fetch','network_fetch',args=>({operation:'fetch',url:String(args[0]&&args[0].url||args[0]||'')}));
  if(globalThis.IDBFactory&&globalThis.IDBFactory.prototype){
    patchMethod(IDBFactory.prototype,'open','indexeddb_open',args=>({operation:'indexedDB.open',name:String(args[0]||'')}));
    patchMethod(IDBFactory.prototype,'deleteDatabase','indexeddb_delete',args=>({operation:'indexedDB.deleteDatabase',name:String(args[0]||'')}));
  }
  if(globalThis.CacheStorage&&globalThis.CacheStorage.prototype){
    patchMethod(CacheStorage.prototype,'open','cache_open',args=>({operation:'caches.open',name:String(args[0]||'')}));
    patchMethod(CacheStorage.prototype,'delete','cache_delete',args=>({operation:'caches.delete',name:String(args[0]||'')}));
  }
  const nativeTimeout=globalThis.setTimeout&&globalThis.setTimeout.bind(globalThis),nativeInterval=globalThis.setInterval&&globalThis.setInterval.bind(globalThis);
  if(nativeTimeout)globalThis.setTimeout=function(callback,delay){const token=requireCapability('timer_schedule',{operation:'setTimeout',delay:Number(delay)||0});const rest=Array.prototype.slice.call(arguments,2);return nativeTimeout(wrapCallback(token,callback),delay,...rest)};
  if(nativeInterval)globalThis.setInterval=function(callback,delay){const token=requireCapability('timer_schedule',{operation:'setInterval',delay:Number(delay)||0});const rest=Array.prototype.slice.call(arguments,2);return nativeInterval(wrapCallback(token,callback),delay,...rest)};
  if(globalThis.EventTarget&&globalThis.EventTarget.prototype){
    const nativeAdd=EventTarget.prototype.addEventListener,nativeRemove=EventTarget.prototype.removeEventListener;
    Object.defineProperty(EventTarget.prototype,'addEventListener',{configurable:true,writable:true,value:function(type,listener,options){
      const token=requireCapability('event_listener',{operation:'addEventListener',event:String(type)});
      if(typeof listener!=='function')return nativeAdd.call(this,type,listener,options);
      let byTarget=state.listenerMap.get(this);if(!byTarget){byTarget=new WeakMap();state.listenerMap.set(this,byTarget)}
      const wrapped=wrapCallback(token,listener);byTarget.set(listener,wrapped);return nativeAdd.call(this,type,wrapped,options);
    }});
    Object.defineProperty(EventTarget.prototype,'removeEventListener',{configurable:true,writable:true,value:function(type,listener,options){
      const byTarget=state.listenerMap.get(this),wrapped=byTarget&&byTarget.get(listener)||listener;return nativeRemove.call(this,type,wrapped,options);
    }});
  }
  if(globalThis.Promise&&globalThis.Promise.prototype&&typeof Promise.prototype.then==='function'){
    const nativeThen=Promise.prototype.then;
    Object.defineProperty(Promise.prototype,'then',{configurable:true,writable:true,value:function(onFulfilled,onRejected){
      const token=state.current;return nativeThen.call(this,token?wrapCallback(token,onFulfilled):onFulfilled,token?wrapCallback(token,onRejected):onRejected);
    }});
  }
  if(typeof globalThis.queueMicrotask==='function'){
    const nativeQueue=globalThis.queueMicrotask.bind(globalThis);
    globalThis.queueMicrotask=function(callback){const token=state.current;return nativeQueue(token?wrapCallback(token,callback):callback)};
  }
  state.installed=true;return report();
}
function report(){return {type:TYPE,version:VERSION,configured:state.configured,installed:state.installed,policy_type:state.policy&&state.policy.type||null,declared_actor_count:state.actors.size,unknown_actor_policy:state.policy&&state.policy.unknown_actor_policy||null,unauthorized_capability_policy:state.policy&&state.policy.unauthorized_capability_policy||null,denial_count:state.denials.length,denials:state.denials.map(clone),current_actor:state.current&&state.current.actor.path||null,pass2_complete:false,pass3_started:false}}
const api=Object.freeze({type:TYPE,version:VERSION,configure,install,authorizeSource,run,report,DeniedError:PMPActorAuthorityDeniedError});
globalThis.PMPActorAuthorityGateV1=api;
})();
