(()=>{
'use strict';
const V='1.0.0-pass2-p2b-exact-source-pre-side-effect';
const OWNER='pmp-pass2-actor-authorization-gate-v1';
const REGISTRY_PATH='pmp-pass2-actor-authority-registry-v1.json';
const RECEIPT_KEY='pmp_pass2_actor_authorization_gate_v1_receipt';
const QUARANTINE_KEY='pmp_pass2_actor_authorization_quarantine_ledger_v1';
const MAX_EVENTS=240;
const GLOBAL_FORBIDDEN=new Set(['storage.local.clear','storage.session.clear','indexeddb.delete','cache.delete','service_worker.register','code.eval']);
const installed=new WeakMap();
const loadedByWindow=new WeakMap();
const actorStack=[];
let registry=null,registryIndex=null,readyPromise=null,bootstrapSealed=false,documentActor=null,testMode=false;

function now(){return new Date().toISOString()}
function normalizePath(value){
  try{const u=new URL(String(value||''),location.href);return decodeURIComponent(u.pathname).replace(/^\/+/, '').replace(/^pmp-bridge-shell\//,'')}catch(e){return String(value||'').split(/[?#]/)[0].replace(/^\/+/, '')}
}
function pathForWindow(w){const pathname=decodeURIComponent(String(w&&w.location&&w.location.pathname||'')).replace(/\\/g,'/');if(!registryIndex)return pathname.replace(/^\/+/, '');let best='';Object.keys(registryIndex).forEach(path=>{if(pathname===('/'+path)||pathname.endsWith('/'+path)){if(path.length>best.length)best=path}});return best||pathname.replace(/^\/+/, '')}
function rootWindow(){try{return window.top||window}catch(e){return window}}
function actorForPath(path){return registryIndex&&registryIndex[normalizePath(path)]||null}
function currentActor(){return actorStack.length?actorStack[actorStack.length-1]:null}
function error(code,message,details){const e=new Error(message||code);e.code=code;e.details=details||null;return e}
function rawState(w){return installed.get(w)||null}
function rawStorage(w){const s=rawState(w);return s&&s.originals&&s.originals.localStorage||null}
function internal(w,fn){const s=rawState(w);if(!s)return fn();s.internal++;try{return fn()}finally{s.internal--}}
function readRaw(key,fallback){const w=rootWindow(),s=rawState(w);try{if(s&&s.originals.localGet)return JSON.parse(s.originals.localGet.call(w.localStorage,key)||JSON.stringify(fallback));return JSON.parse(w.localStorage.getItem(key)||JSON.stringify(fallback))}catch(e){return fallback}}
function writeRaw(key,value){const w=rootWindow(),s=rawState(w),text=JSON.stringify(value);try{if(s&&s.originals.localSet)return s.originals.localSet.call(w.localStorage,key,text);return w.localStorage.setItem(key,text)}catch(e){return null}}
function appendQuarantine(code,capability,details,actor){
  const old=readRaw(QUARANTINE_KEY,{type:'PMP_PASS2_AUTHORIZATION_QUARANTINE_LEDGER_V1',version:V,owner:OWNER,events:[]});
  const events=Array.isArray(old.events)?old.events.slice():[];
  const event={sequence:events.length+1,at:now(),code,capability:String(capability||''),actor:actor?{id:actor.id,path:actor.path,sha256:actor.sha256}:null,details:details||{},side_effect_executed:false};
  events.push(event);old.type='PMP_PASS2_AUTHORIZATION_QUARANTINE_LEDGER_V1';old.version=V;old.owner=OWNER;old.updated_at=event.at;old.events=events.slice(-MAX_EVENTS).map((x,i)=>Object.assign({},x,{sequence:i+1}));writeRaw(QUARANTINE_KEY,old);return event
}
function deny(code,capability,details,actor){appendQuarantine(code,capability,details,actor||currentActor());throw error(code,code==='P2_UNKNOWN_ACTOR'?'Unknown or unregistered actor blocked before side effect.':'Actor capability blocked before side effect.',Object.assign({capability},details||{}))}
function authorize(capability,details){
  const cap=String(capability||'');
  if(GLOBAL_FORBIDDEN.has(cap))return deny('P2_CAPABILITY_GLOBALLY_FORBIDDEN',cap,details,currentActor());
  const actor=currentActor();if(!actor)return deny('P2_UNKNOWN_ACTOR',cap,details,null);
  if(!actor.allowed_capabilities.includes(cap))return deny('P2_CAPABILITY_DENIED',cap,details,actor);
  return {allowed:true,actor:actor.path,capability:cap}
}
function withActor(actor,fn){
  if(!actor)return deny('P2_UNKNOWN_ACTOR','actor.context',{requested:null},null);
  actorStack.push(actor);
  let result;
  try{result=fn()}catch(e){actorStack.pop();throw e}
  if(result&&typeof result.then==='function')return Promise.resolve(result).finally(()=>{if(actorStack[actorStack.length-1]===actor)actorStack.pop();else{const i=actorStack.lastIndexOf(actor);if(i>=0)actorStack.splice(i,1)}});
  actorStack.pop();return result
}
function withActorPath(path,fn){const actor=actorForPath(path);if(!actor)return deny('P2_UNKNOWN_ACTOR','actor.context',{requested_path:normalizePath(path)},null);return withActor(actor,fn)}
function capture(actor,fn){if(typeof fn!=='function')return fn;return function(){const self=this,args=arguments;return withActor(actor,()=>fn.apply(self,args))}}
function documentActorFor(w){return actorForPath(pathForWindow(w))}
function implicitActor(w){const s=rawState(w);if(currentActor())return currentActor();if(s&&!s.sealed&&s.documentActor)return s.documentActor;return null}
function requireInWindow(w,cap,details){const s=rawState(w);if(s&&s.internal>0)return {allowed:true,internal:true};const implicit=implicitActor(w);if(implicit&&!currentActor())return withActor(implicit,()=>authorize(cap,details));return authorize(cap,details)}
function descriptor(proto,name){try{return Object.getOwnPropertyDescriptor(proto,name)}catch(e){return null}}
function define(proto,name,value){try{Object.defineProperty(proto,name,{value,writable:true,configurable:true})}catch(e){try{proto[name]=value}catch(_){}}}
function wrapHandlerProperties(w,state){
  const props=['onclick','onload','onerror','onchange','oninput','onsubmit','onpointerdown','onpointerup','ontouchstart','ontouchend','onmessage'];
  [w.Window&&w.Window.prototype,w.Document&&w.Document.prototype,w.HTMLElement&&w.HTMLElement.prototype].filter(Boolean).forEach(proto=>props.forEach(name=>{
    const d=descriptor(proto,name);if(!d||!d.set||!d.get||d.configurable===false)return;
    try{Object.defineProperty(proto,name,{configurable:true,enumerable:d.enumerable,get:d.get,set:function(fn){const actor=implicitActor(w);if(typeof fn==='function'){requireInWindow(w,'event.listen',{surface:name});return d.set.call(this,capture(actor,fn))}return d.set.call(this,fn)}})}catch(e){}
  }))
}
function install(w){
  if(!w||installed.has(w))return installed.get(w);
  const state={internal:0,sealed:false,documentActor:null,listenerMap:new WeakMap(),originals:{}};installed.set(w,state);
  try{state.documentActor=documentActorFor(w)}catch(e){}
  const O=state.originals;
  // Storage writes.
  if(w.Storage&&w.Storage.prototype){
    const p=w.Storage.prototype;O.storageSet=p.setItem;O.storageRemove=p.removeItem;O.storageClear=p.clear;
    try{O.localGet=w.localStorage.getItem;O.localSet=w.localStorage.setItem;O.localStorage=w.localStorage}catch(e){}
    define(p,'setItem',function(k,v){const local=this===w.localStorage;requireInWindow(w,local?'storage.local.write':'storage.session.write',{key:String(k)});return O.storageSet.call(this,k,v)});
    define(p,'removeItem',function(k){const local=this===w.localStorage;requireInWindow(w,local?'storage.local.delete':'storage.session.delete',{key:String(k)});return O.storageRemove.call(this,k)});
    define(p,'clear',function(){const local=this===w.localStorage;requireInWindow(w,local?'storage.local.clear':'storage.session.clear',{});return O.storageClear.call(this)});
  }
  // Timers and microtasks retain actor identity.
  O.setTimeout=w.setTimeout.bind(w);O.setInterval=w.setInterval.bind(w);O.clearTimeout=w.clearTimeout.bind(w);O.clearInterval=w.clearInterval.bind(w);
  w.setTimeout=function(fn,ms){requireInWindow(w,'timer.once',{delay:Number(ms)||0});const actor=implicitActor(w);return O.setTimeout(capture(actor,fn),ms,...Array.prototype.slice.call(arguments,2))};
  w.setInterval=function(fn,ms){requireInWindow(w,'timer.recurring',{delay:Number(ms)||0});const actor=implicitActor(w);return O.setInterval(capture(actor,fn),ms,...Array.prototype.slice.call(arguments,2))};
  if(typeof w.queueMicrotask==='function'){O.queueMicrotask=w.queueMicrotask.bind(w);w.queueMicrotask=function(fn){const actor=implicitActor(w);return O.queueMicrotask(capture(actor,fn))}}
  // Promise continuation identity.
  if(w.Promise&&w.Promise.prototype){const pp=w.Promise.prototype;O.promiseThen=pp.then;O.promiseCatch=pp.catch;O.promiseFinally=pp.finally;define(pp,'then',function(a,b){const actor=implicitActor(w);return O.promiseThen.call(this,capture(actor,a),capture(actor,b))});define(pp,'catch',function(a){const actor=implicitActor(w);return O.promiseCatch.call(this,capture(actor,a))});if(O.promiseFinally)define(pp,'finally',function(a){const actor=implicitActor(w);return O.promiseFinally.call(this,capture(actor,a))})}
  // Event listeners retain actor identity and are authority checked.
  if(w.EventTarget&&w.EventTarget.prototype){const ep=w.EventTarget.prototype;O.addEventListener=ep.addEventListener;O.removeEventListener=ep.removeEventListener;define(ep,'addEventListener',function(type,listener,options){requireInWindow(w,'event.listen',{event:String(type)});const actor=implicitActor(w);let wrapped=listener;if(typeof listener==='function'){wrapped=capture(actor,listener);state.listenerMap.set(listener,wrapped)}else if(listener&&typeof listener.handleEvent==='function'){const original=listener;wrapped={handleEvent:capture(actor,function(e){return original.handleEvent(e)})};state.listenerMap.set(listener,wrapped)}return O.addEventListener.call(this,type,wrapped,options)});define(ep,'removeEventListener',function(type,listener,options){return O.removeEventListener.call(this,type,state.listenerMap.get(listener)||listener,options)})}
  wrapHandlerProperties(w,state);
  // DOM mutation and script insertion.
  if(w.Node&&w.Node.prototype){const np=w.Node.prototype;O.appendChild=np.appendChild;O.insertBefore=np.insertBefore;O.replaceChild=np.replaceChild;O.removeChild=np.removeChild;
    define(np,'appendChild',function(child){if(child&&String(child.tagName||'').toUpperCase()==='SCRIPT')return requestScriptElement(w,this,child,null);requireInWindow(w,'dom.write',{operation:'appendChild'});return O.appendChild.call(this,child)});
    define(np,'insertBefore',function(child,ref){if(child&&String(child.tagName||'').toUpperCase()==='SCRIPT')return requestScriptElement(w,this,child,ref);requireInWindow(w,'dom.write',{operation:'insertBefore'});return O.insertBefore.call(this,child,ref)});
    define(np,'replaceChild',function(child,old){if(child&&String(child.tagName||'').toUpperCase()==='SCRIPT'){requestScriptElement(w,this,child,old);return old}requireInWindow(w,'dom.write',{operation:'replaceChild'});return O.replaceChild.call(this,child,old)});
    define(np,'removeChild',function(child){requireInWindow(w,'dom.write',{operation:'removeChild'});return O.removeChild.call(this,child)});
    const td=descriptor(np,'textContent');if(td&&td.set&&td.configurable!==false){O.textContent=td;try{Object.defineProperty(np,'textContent',{configurable:true,enumerable:td.enumerable,get:td.get,set:function(v){requireInWindow(w,'dom.write',{operation:'textContent'});return td.set.call(this,v)}})}catch(e){}}
  }
  if(w.Element&&w.Element.prototype){const ep=w.Element.prototype;O.setAttribute=ep.setAttribute;O.removeAttribute=ep.removeAttribute;define(ep,'setAttribute',function(name,value){const n=String(name).toLowerCase(),tag=String(this.tagName||'').toUpperCase();if(n==='src'&&(tag==='IFRAME'||tag==='FRAME'))requireInWindow(w,'navigation.frame',{url:String(value)});else if(n==='src'&&tag==='SCRIPT')requireInWindow(w,'script.load',{url:String(value)});else requireInWindow(w,'dom.write',{operation:'setAttribute',attribute:n});return O.setAttribute.call(this,name,value)});define(ep,'removeAttribute',function(name){requireInWindow(w,'dom.write',{operation:'removeAttribute',attribute:String(name)});return O.removeAttribute.call(this,name)});
    ['innerHTML','outerHTML'].forEach(name=>{const d=descriptor(ep,name);if(d&&d.set&&d.configurable!==false){try{Object.defineProperty(ep,name,{configurable:true,enumerable:d.enumerable,get:d.get,set:function(v){requireInWindow(w,'dom.write',{operation:name});return d.set.call(this,v)}})}catch(e){}}});
    if(ep.insertAdjacentHTML){O.insertAdjacentHTML=ep.insertAdjacentHTML;define(ep,'insertAdjacentHTML',function(pos,html){requireInWindow(w,'dom.write',{operation:'insertAdjacentHTML'});return O.insertAdjacentHTML.call(this,pos,html)})}
    if(ep.remove){O.elementRemove=ep.remove;define(ep,'remove',function(){requireInWindow(w,'dom.write',{operation:'remove'});return O.elementRemove.call(this)})}
  }
  if(w.Document&&w.Document.prototype&&w.Document.prototype.write){O.documentWrite=w.Document.prototype.write;define(w.Document.prototype,'write',function(){requireInWindow(w,'dom.write',{operation:'document.write'});return O.documentWrite.apply(this,arguments)})}
  if(w.HTMLIFrameElement&&w.HTMLIFrameElement.prototype){const d=descriptor(w.HTMLIFrameElement.prototype,'src');if(d&&d.set&&d.configurable!==false){O.iframeSrc=d;try{Object.defineProperty(w.HTMLIFrameElement.prototype,'src',{configurable:true,enumerable:d.enumerable,get:d.get,set:function(v){requireInWindow(w,'navigation.frame',{url:String(v)});return d.set.call(this,v)}})}catch(e){}}}
  // Network.
  if(typeof w.fetch==='function'){O.fetch=w.fetch.bind(w);w.fetch=function(input,init){requireInWindow(w,'network.fetch',{url:String(input&&input.url||input)});return O.fetch(input,init)}}
  if(w.XMLHttpRequest&&w.XMLHttpRequest.prototype){const xp=w.XMLHttpRequest.prototype;O.xhrOpen=xp.open;define(xp,'open',function(method,url){requireInWindow(w,'network.fetch',{method:String(method),url:String(url)});return O.xhrOpen.apply(this,arguments)})}
  if(w.WebSocket){O.WebSocket=w.WebSocket;try{w.WebSocket=new Proxy(O.WebSocket,{construct(target,args,newTarget){requireInWindow(w,'network.fetch',{url:String(args[0]||''),transport:'websocket'});return Reflect.construct(target,args,newTarget)}})}catch(e){}}
  // IndexedDB and Cache APIs.
  try{if(w.IDBFactory&&w.IDBFactory.prototype){const ip=w.IDBFactory.prototype;O.idbOpen=ip.open;O.idbDelete=ip.deleteDatabase;define(ip,'open',function(){requireInWindow(w,'indexeddb.open',{name:String(arguments[0]||'')});return O.idbOpen.apply(this,arguments)});define(ip,'deleteDatabase',function(){requireInWindow(w,'indexeddb.delete',{name:String(arguments[0]||'')});return O.idbDelete.apply(this,arguments)})}}catch(e){}
  try{if(w.CacheStorage&&w.CacheStorage.prototype){const cp=w.CacheStorage.prototype;O.cacheOpen=cp.open;O.cacheDelete=cp.delete;define(cp,'open',function(name){requireInWindow(w,'cache.open',{name:String(name)});return O.cacheOpen.call(this,name)});define(cp,'delete',function(name){requireInWindow(w,'cache.delete',{name:String(name)});return O.cacheDelete.call(this,name)})}if(w.Cache&&w.Cache.prototype){const c=w.Cache.prototype;['put','add','addAll'].forEach(name=>{if(c[name]){O['cache_'+name]=c[name];define(c,name,function(){requireInWindow(w,'cache.write',{operation:name});return O['cache_'+name].apply(this,arguments)})}});if(c.delete){O.cacheEntryDelete=c.delete;define(c,'delete',function(){requireInWindow(w,'cache.delete',{operation:'entry.delete'});return O.cacheEntryDelete.apply(this,arguments)})}}}catch(e){}
  // Navigation and privileged execution.
  O.windowOpen=w.open&&w.open.bind(w);if(O.windowOpen)w.open=function(url){requireInWindow(w,'navigation.window',{url:String(url||'')});return O.windowOpen.apply(w,arguments)};
  try{if(w.navigator&&w.navigator.serviceWorker&&w.navigator.serviceWorker.register){O.swRegister=w.navigator.serviceWorker.register.bind(w.navigator.serviceWorker);w.navigator.serviceWorker.register=function(){requireInWindow(w,'service_worker.register',{url:String(arguments[0]||'')});return O.swRegister.apply(this,arguments)}}}catch(e){}
  if(w.eval){O.eval=w.eval;w.eval=function(){requireInWindow(w,'code.eval',{});return O.eval.apply(w,arguments)}}
  if(w.Function){O.Function=w.Function;try{w.Function=new Proxy(O.Function,{construct(target,args,newTarget){requireInWindow(w,'code.eval',{});return Reflect.construct(target,args,newTarget)},apply(target,thisArg,args){requireInWindow(w,'code.eval',{});return Reflect.apply(target,thisArg,args)}})}catch(e){}}
  return state
}
function getLoadedSet(w){let set=loadedByWindow.get(w);if(!set){set=new Set();loadedByWindow.set(w,set)}return set}
function registryUrl(path){return new URL('/'+normalizePath(path),location.origin).href}
async function hashBytes(bytes){const b=bytes instanceof ArrayBuffer?bytes:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);const digest=await crypto.subtle.digest('SHA-256',b);return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('')}
function productionBootstrap(){try{const t=rootWindow();return t.PMPRuntimeIntegrityBootstrap||window.PMPRuntimeIntegrityBootstrap||null}catch(e){return null}}
function isFixture(){const p=normalizePath(location.pathname);return p==='audit/pass2/p2b-forbidden-action-fixture.html'&&new URL(location.href).searchParams.get('pmp_p2b_fixture')==='1'}
async function fetchVerified(path){
  const normalized=normalizePath(path),actor=actorForPath(normalized);if(!actor)return deny('P2_UNKNOWN_ACTOR','script.load',{requested_path:normalized},currentActor());if(actor.loadable===false)return deny('P2_ACTOR_NOT_LOADABLE','script.load',{requested_path:normalized,execution_class:actor.execution_class},currentActor());
  const bootstrap=productionBootstrap();let bytes,actual;
  if(bootstrap&&bootstrap.enforced&&typeof bootstrap.verifyPath==='function'){const verified=await bootstrap.verifyPath(normalized);bytes=verified.bytes;actual=verified.sha256_hex}else if(testMode){const r=await fetch(registryUrl(normalized)+'?pmp_p2b_fixture_bytes='+Date.now(),{cache:'no-store'});if(!r.ok)throw error('P2_SOURCE_FETCH_FAILED','Fixture source fetch failed.',{path:normalized,status:r.status});bytes=await r.arrayBuffer();actual=await hashBytes(bytes)}else throw error('P2_A003_BOOTSTRAP_REQUIRED','A-003 exact-source bootstrap is required before actor authorization.',{path:normalized});
  if(actual!==actor.sha256)throw error('P2_SOURCE_DIGEST_MISMATCH','Actor bytes do not match the registered exact source.',{path:normalized,expected:actor.sha256,actual});
  return {path:normalized,actor,bytes,sha256:actual}
}
function executeVerified(verified,opts,requester){
  const doc=opts&&opts.document||document,w=doc.defaultView||window;install(w);const state=rawState(w),loaded=getLoadedSet(w);if(loaded.has(verified.path))return Promise.resolve({status:'already_loaded',path:verified.path,sha256:verified.sha256});
  return new Promise((resolve,reject)=>{
    try{
      const element=opts&&opts.element||doc.createElement('script');
      const token='p2b_'+Math.random().toString(16).slice(2);
      const source=new TextDecoder().decode(verified.bytes)+'\n//# sourceURL='+verified.path;
      internal(w,()=>{state.originals.setAttribute.call(element,'data-pmp-authorized-path',verified.path);state.originals.setAttribute.call(element,'data-pmp-authorized-sha256',verified.sha256);if(element.hasAttribute&&element.hasAttribute('src')){state.originals.setAttribute.call(element,'data-pmp-requested-src',String(element.getAttribute('src')||''));state.originals.removeAttribute.call(element,'src')}if(opts&&opts.elementId)element.id=opts.elementId;element.text='try{'+source+'\n;window.__PMP_P2B_EXECUTION_OK__=window.__PMP_P2B_EXECUTION_OK__||{};window.__PMP_P2B_EXECUTION_OK__["'+token+'"]={ok:true};}catch(e){window.__PMP_P2B_EXECUTION_OK__=window.__PMP_P2B_EXECUTION_OK__||{};window.__PMP_P2B_EXECUTION_OK__["'+token+'"]={ok:false,error:String(e&&e.stack||e)};throw e;}'});
      withActor(verified.actor,()=>internal(w,()=>state.originals.appendChild.call(doc.head||doc.documentElement||doc.body,element)));
      const execution=w.__PMP_P2B_EXECUTION_OK__&&w.__PMP_P2B_EXECUTION_OK__[token];
      if(!execution||execution.ok!==true){const e=error('P2_ACTOR_EXECUTION_FAILED','Exact-source actor threw during authorized execution.',{path:verified.path,error:execution&&execution.error||'execution_marker_missing'});try{element.dispatchEvent(new w.Event('error'))}catch(_){}return reject(e)}
      loaded.add(verified.path);try{element.dispatchEvent(new w.Event('load'))}catch(_){}
      resolve({status:'loaded_exact_source',path:verified.path,sha256:verified.sha256,requester:requester&&requester.path||null})
    }catch(e){reject(e)}
  })
}
async function loadActor(path,opts){
  opts=opts||{};const requester=opts.requester||implicitActor((opts.document&&opts.document.defaultView)||window);
  if(!opts.internal){if(!requester)return deny('P2_UNKNOWN_ACTOR','script.load',{requested_path:normalizePath(path)},null);return withActor(requester,()=>{authorize('script.load',{requested_path:normalizePath(path),reason:opts.reason||null});const actor=actorForPath(path);if(!actor)return deny('P2_UNKNOWN_ACTOR','script.load',{requested_path:normalizePath(path)},requester);if(actor.loadable===false)return deny('P2_ACTOR_NOT_LOADABLE','script.load',{requested_path:normalizePath(path),execution_class:actor.execution_class},requester);return fetchVerified(path).then(v=>executeVerified(v,opts,requester))})}
  const actor=actorForPath(path);if(!actor)return deny('P2_UNKNOWN_ACTOR','script.load',{requested_path:normalizePath(path)},requester);if(actor.loadable===false)return deny('P2_ACTOR_NOT_LOADABLE','script.load',{requested_path:normalizePath(path),execution_class:actor.execution_class},requester);return fetchVerified(path).then(v=>executeVerified(v,opts,requester))
}
async function loadActors(paths,opts){const out=[];for(const path of paths)out.push(await loadActor(path,opts||{}));return out}
function requestScriptElement(w,parent,child,ref){
  const requester=implicitActor(w);requireInWindow(w,'script.load',{requested_src:String(child.src||child.getAttribute&&child.getAttribute('src')||'')});const requested=String(child.getAttribute&&child.getAttribute('src')||child.src||''),path=normalizePath(requested);if(!actorForPath(path))return deny('P2_UNKNOWN_ACTOR','script.load',{requested_path:path},requester);loadActor(path,{document:child.ownerDocument||w.document,element:child,requester,reason:'intercepted_script_append'}).catch(e=>{try{child.dispatchEvent(new w.Event('error'))}catch(_){}});return child
}
function navigateWindow(target,url,details){authorize('navigation.window',Object.assign({url:String(url)},details||{}));const w=target||window,s=rawState(w)||install(w);return internal(w,()=>{try{w.location.assign(String(url))}catch(e){w.location.href=String(url)}})}
function loadedActors(w){return Array.from(getLoadedSet(w||window)).sort()}
function bindCurrent(fn){const actor=implicitActor(window);if(!actor)throw error('P2_UNKNOWN_ACTOR','No actor context is available to bind.');return capture(actor,fn)}
function installWindow(w){authorize('gate.extend_window',{target:String(w&&w.location&&w.location.href||'unknown')});return install(w)}
function report(){return {type:'PMP_PASS2_ACTOR_AUTHORIZATION_GATE_REPORT_V1',version:V,owner:OWNER,enforced:!!registry,bootstrap_sealed:bootstrapSealed,registry_path:REGISTRY_PATH,registered_actors:registry?registry.counts.registered_actors:0,loaded_actors:loadedActors(),current_actor:currentActor()&&currentActor().path||null,global_forbidden:Array.from(GLOBAL_FORBIDDEN).sort(),quarantine_events:(readRaw(QUARANTINE_KEY,{events:[]}).events||[]).length,pass2_complete:false,pass3_started:false}}
function quarantineLedger(){return readRaw(QUARANTINE_KEY,{type:'PMP_PASS2_AUTHORIZATION_QUARANTINE_LEDGER_V1',version:V,owner:OWNER,events:[]})}
function sealBootstrap(reason){bootstrapSealed=true;installed.forEach&&installed.forEach(()=>{});[window,rootWindow()].forEach(w=>{const s=rawState(w);if(s)s.sealed=true});writeRaw(RECEIPT_KEY,{type:'PMP_PASS2_ACTOR_AUTHORIZATION_GATE_RECEIPT_V1',version:V,owner:OWNER,status:'ENFORCED',at:now(),reason:String(reason||'sealed'),registry_path:REGISTRY_PATH,registered_actors:registry&&registry.counts.registered_actors||0,global_forbidden:Array.from(GLOBAL_FORBIDDEN).sort(),pass2_complete:false,pass3_started:false});return report()}
async function initialize(){
  testMode=isFixture();let bytes,actual,bootstrap=productionBootstrap();
  if(bootstrap&&bootstrap.enforced&&typeof bootstrap.verifyPath==='function'){const verified=await bootstrap.verifyPath(REGISTRY_PATH);bytes=verified.bytes;actual=verified.sha256_hex}else if(testMode){const r=await fetch(registryUrl(REGISTRY_PATH)+'?pmp_p2b_fixture_registry='+Date.now(),{cache:'no-store'});if(!r.ok)throw error('P2_REGISTRY_FETCH_FAILED','Fixture registry fetch failed.',{status:r.status});bytes=await r.arrayBuffer();actual=await hashBytes(bytes)}else throw error('P2_A003_BOOTSTRAP_REQUIRED','A-003 bootstrap is required before the Pass 2 gate can initialize.');
  try{registry=JSON.parse(new TextDecoder().decode(bytes))}catch(e){throw error('P2_REGISTRY_JSON_INVALID','Actor registry is invalid JSON.')}
  if(registry.type!=='PMP_PASS2_ACTOR_AUTHORITY_REGISTRY_V1'||registry.default_policy!=='FAIL_CLOSED')throw error('P2_REGISTRY_CONTRACT_INVALID','Actor registry contract is invalid.');
  registryIndex={};registry.actors.forEach(actor=>{if(!actor||!actor.path||!/^[0-9a-f]{64}$/.test(actor.sha256)||registryIndex[actor.path])throw error('P2_REGISTRY_ACTOR_INVALID','Actor registry contains an invalid or duplicate actor.',{actor});registryIndex[actor.path]=Object.freeze(actor)});
  if(registry.counts.registered_actors!==registry.actors.length)throw error('P2_REGISTRY_COUNT_MISMATCH','Actor registry count does not match actor rows.');
  install(rootWindow());install(window);documentActor=documentActorFor(window);if(!documentActor)throw error('P2_DOCUMENT_ACTOR_UNREGISTERED','Current document is not a registered exact-source actor.',{path:normalizePath(location.pathname)});
  rawState(window).documentActor=documentActor;const topState=rawState(rootWindow());if(topState&&!topState.documentActor)topState.documentActor=documentActorFor(rootWindow());
  writeRaw(RECEIPT_KEY,{type:'PMP_PASS2_ACTOR_AUTHORIZATION_GATE_RECEIPT_V1',version:V,owner:OWNER,status:'READY_NOT_YET_SEALED',at:now(),registry_path:REGISTRY_PATH,registry_sha256:actual,registered_actors:registry.actors.length,document_actor:documentActor.path,global_forbidden:Array.from(GLOBAL_FORBIDDEN).sort(),pass2_complete:false,pass3_started:false});
  return report()
}
function ready(){if(!readyPromise)readyPromise=initialize();return readyPromise}
function runDocument(fn){if(!documentActor)throw error('P2_DOCUMENT_ACTOR_UNREGISTERED','Document actor is not ready.');return withActor(documentActor,fn)}
function can(path,capability){const actor=actorForPath(path);return !!(actor&&!GLOBAL_FORBIDDEN.has(String(capability))&&actor.allowed_capabilities.includes(String(capability)))}
function testAllowed(){if(!testMode)throw error('P2_TEST_API_FORBIDDEN','Test API is restricted to the exact adversarial fixture.')}
function testRunAs(path,fn){testAllowed();return withActorPath(path,fn)}
async function testVerifySource(path,bytes){testAllowed();const actor=actorForPath(path);if(!actor)return deny('P2_UNKNOWN_ACTOR','source.verify',{requested_path:normalizePath(path)},null);const actual=await hashBytes(bytes);if(actual!==actor.sha256)throw error('P2_SOURCE_DIGEST_MISMATCH','Test bytes do not match registered source.',{path:actor.path,expected:actor.sha256,actual});return true}

window.PMPPass2ActorAuthorizationGateV1=Object.freeze({version:V,owner:OWNER,registryPath:REGISTRY_PATH,ready,runDocument,loadActor,loadActors,authorize,can,navigateWindow,loadedActors,bindCurrent,installWindow,sealBootstrap,report,quarantineLedger,testRunAs,testVerifySource});
})();
