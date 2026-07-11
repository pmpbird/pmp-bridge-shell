(function(global){
'use strict';

var MAP_PATH='pmp-current-map-v12.json';
var MANIFEST_PATH='pmp-runtime-integrity-manifest-v1.json';
var ROOT_TRUST_ANCHOR='pmp-app-current.html';
var INTEGRITY_SW_PATH='pmp-integrity-service-worker-v1.js';
var RESOLVER_VERSION='PMP_CURRENT_ROUTE_RESOLVER_V1_20260711D_A003';
var HANDOFF_TYPE='PMP_ROUTE_HANDOFF_V1';
var MAP_TYPE='PMP_CURRENT_APP_MAP';
var CONTRACT_TYPE='PMP_ROUTE_CONTRACT_V1';
var integrityPromise=null;
var activeIntegrityIndex=null;
var activeManifestSha256=null;

function RouteError(code,message,details){
  this.name='PMPRouteError';
  this.code=String(code||'ROUTE_ERROR');
  this.message=String(message||this.code);
  this.details=details||null;
  if(Error.captureStackTrace)Error.captureStackTrace(this,RouteError);
}
RouteError.prototype=Object.create(Error.prototype);
RouteError.prototype.constructor=RouteError;

function own(o,k){return !!o&&Object.prototype.hasOwnProperty.call(o,k)}
function freeze(o){try{return Object.freeze(o)}catch(e){return o}}
function cloneJson(v){return JSON.parse(JSON.stringify(v))}
function isScreenHash(v){return /^#[a-z0-9-]+$/.test(String(v||''))}
function hex(buffer){return Array.from(new Uint8Array(buffer)).map(function(v){return v.toString(16).padStart(2,'0')}).join('')}
async function sha256(data){return hex(await crypto.subtle.digest('SHA-256',data))}

function isLocalPath(path,extensions){
  path=String(path||'').trim();
  if(!path||path.length>240)return false;
  if(path.charAt(0)==='/'||path.indexOf('\\')!==-1||path.indexOf('..')!==-1)return false;
  if(/^[a-z][a-z0-9+.-]*:/i.test(path)||path.indexOf('//')===0)return false;
  if(/[?#\u0000-\u001f]/.test(path))return false;
  if(!/^[A-Za-z0-9._/-]+$/.test(path))return false;
  var dot=path.lastIndexOf('.');
  var ext=dot<0?'':path.slice(dot).toLowerCase();
  return extensions.indexOf(ext)!==-1;
}

function assertLocalRouteNode(node,role,extensions){
  if(!node||typeof node!=='object')throw new RouteError('ROLE_MISSING','Required route role is missing.',{role:role});
  if(!isLocalPath(node.path,extensions))throw new RouteError('ROLE_PATH_INVALID','Route role has an invalid local path.',{role:role,path:node.path});
  if(node.status&&String(node.status).toLowerCase()==='disabled')throw new RouteError('ROLE_DISABLED','Requested route role is disabled.',{role:role,path:node.path});
  return node;
}

function validateHashes(map){
  if(!Array.isArray(map.allowed_hashes)||map.allowed_hashes.length===0)throw new RouteError('HASH_POLICY_MISSING','Current Map has no allowed hash policy.');
  var seen={};
  map.allowed_hashes.forEach(function(hash){
    hash=String(hash||'');
    if(!isScreenHash(hash))throw new RouteError('HASH_INVALID','Current Map contains an invalid screen hash.',{hash:hash});
    if(seen[hash])throw new RouteError('HASH_DUPLICATE','Current Map contains a duplicate screen hash.',{hash:hash});
    seen[hash]=true;
  });
}

function validateMap(map){
  if(!map||typeof map!=='object'||Array.isArray(map))throw new RouteError('MAP_INVALID','Current Map is not a JSON object.');
  if(map.type!==MAP_TYPE)throw new RouteError('MAP_TYPE_INVALID','Current Map type is invalid.',{expected:MAP_TYPE,actual:map.type});
  if(!map.route_contract||map.route_contract.type!==CONTRACT_TYPE)throw new RouteError('CONTRACT_INVALID','Current Map route contract is missing or invalid.');
  if(map.route_contract.sole_authority!==MAP_PATH)throw new RouteError('AUTHORITY_INVALID','Current Map does not name itself as sole route authority.',{actual:map.route_contract.sole_authority});
  if(map.route_contract.resolver!=='pmp-current-route-resolver-v1.js')throw new RouteError('RESOLVER_CONTRACT_INVALID','Current Map resolver contract does not match this resolver.',{actual:map.route_contract.resolver});
  if(map.route_contract.failure_mode!=='fail_closed'||map.route_contract.implicit_fallbacks!==false)throw new RouteError('FAILURE_POLICY_INVALID','Current Map must require fail-closed routing with no implicit fallbacks.');
  if(map.route_contract.runtime_integrity_required!==true)throw new RouteError('INTEGRITY_REQUIRED_MISSING','Current Map must require runtime source-byte integrity enforcement.');
  if(map.route_contract.integrity_manifest!==MANIFEST_PATH)throw new RouteError('INTEGRITY_MANIFEST_MISMATCH','Current Map integrity manifest does not match the resolver contract.',{actual:map.route_contract.integrity_manifest});
  if(map.route_contract.integrity_service_worker!==INTEGRITY_SW_PATH)throw new RouteError('INTEGRITY_SW_MISMATCH','Current Map integrity Service Worker does not match the resolver contract.',{actual:map.route_contract.integrity_service_worker});
  if(map.route_contract.root_trust_anchor!==ROOT_TRUST_ANCHOR)throw new RouteError('ROOT_TRUST_ANCHOR_MISMATCH','Current Map root trust anchor does not match the resolver contract.',{actual:map.route_contract.root_trust_anchor});
  if(map.route_contract.integrity_algorithm!=='SHA-256'||map.route_contract.unlisted_executable_policy!=='fail_closed')throw new RouteError('INTEGRITY_POLICY_INVALID','Current Map runtime integrity policy is invalid.');
  if(!map.route_epoch||!map.app_version)throw new RouteError('MAP_IDENTITY_INCOMPLETE','Current Map version or route epoch is missing.');
  assertLocalRouteNode(map.entry,'entry',['.html']);
  assertLocalRouteNode(map.route_guardian,'route_guardian',['.html']);
  assertLocalRouteNode(map.current_app,'current_app',['.html']);
  validateHashes(map);
  return map;
}

function validateManifest(manifest){
  if(!manifest||manifest.type!=='PMP_RUNTIME_INTEGRITY_MANIFEST_V1')throw new RouteError('INTEGRITY_MANIFEST_TYPE_INVALID','Runtime integrity manifest type is invalid.');
  if(manifest.algorithm!=='SHA-256'||manifest.unlisted_executable_policy!=='FAIL_CLOSED')throw new RouteError('INTEGRITY_MANIFEST_POLICY_INVALID','Runtime integrity manifest policy is invalid.');
  if(!Array.isArray(manifest.records)||manifest.records.length===0)throw new RouteError('INTEGRITY_MANIFEST_EMPTY','Runtime integrity manifest has no records.');
  var roots=Array.isArray(manifest.root_trust_anchors)?manifest.root_trust_anchors:[];
  if(!roots.some(function(r){return r&&r.path===ROOT_TRUST_ANCHOR}))throw new RouteError('INTEGRITY_ROOT_MISSING','Runtime integrity manifest does not name the bootstrap root trust anchor.');
  return manifest;
}

function indexManifest(manifest){
  var index={};
  manifest.records.forEach(function(record){
    if(!record||typeof record.path!=='string'||!/^[0-9a-f]{64}$/.test(String(record.sha256_hex||'')))throw new RouteError('INTEGRITY_RECORD_INVALID','Runtime integrity manifest contains an invalid record.',{record:record});
    if(index[record.path])throw new RouteError('INTEGRITY_RECORD_DUPLICATE','Runtime integrity manifest contains a duplicate path.',{path:record.path});
    index[record.path]=record;
  });
  return index;
}

async function fetchBytes(path){
  var response;
  try{response=await fetch(path+'?pmp_integrity_verify='+encodeURIComponent(String(Date.now())),{cache:'no-store',credentials:'same-origin'})}
  catch(error){throw new RouteError('INTEGRITY_FETCH_FAILED','Runtime source could not be fetched.',{path:path,error:String(error&&error.message||error)})}
  if(!response||!response.ok)throw new RouteError('INTEGRITY_HTTP_FAILED','Runtime source request did not succeed.',{path:path,status:response&&response.status});
  return {response:response,bytes:await response.arrayBuffer()};
}

async function queryIntegrityWorker(){
  if(!('serviceWorker' in navigator)||!navigator.serviceWorker.controller)throw new RouteError('INTEGRITY_CONTROLLER_MISSING','Runtime integrity Service Worker is not controlling this page.');
  return new Promise(function(resolve,reject){
    var timer=setTimeout(function(){reject(new RouteError('INTEGRITY_STATUS_TIMEOUT','Runtime integrity Service Worker status timed out.'))},7000);
    var channel=new MessageChannel();
    channel.port1.onmessage=function(event){clearTimeout(timer);resolve(event.data||{})};
    try{navigator.serviceWorker.controller.postMessage({type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST',from:'route_resolver',at:new Date().toISOString()},[channel.port2])}
    catch(error){clearTimeout(timer);reject(new RouteError('INTEGRITY_STATUS_FAILED','Runtime integrity Service Worker status request failed.',{error:String(error&&error.message||error)}))}
  });
}

function contextFromBootstrap(bootstrap){
  if(!bootstrap||bootstrap.enforced!==true||!bootstrap.manifest||!/^[0-9a-f]{64}$/.test(String(bootstrap.manifestSha256||'')))throw new RouteError('INTEGRITY_BOOTSTRAP_INVALID','Runtime integrity bootstrap is missing or invalid.');
  var manifest=validateManifest(bootstrap.manifest);
  var index=indexManifest(manifest);
  return {
    source:'bootstrap',
    manifest:manifest,
    manifestSha256:String(bootstrap.manifestSha256),
    index:index,
    workerStatus:bootstrap.workerStatus||null,
    async verifyPath(path){
      if(typeof bootstrap.verifyPath==='function')return bootstrap.verifyPath(path);
      return verifyWithIndex(path,index);
    }
  };
}

async function verifyWithIndex(path,index){
  var record=index[path];
  if(!record)throw new RouteError('UNLISTED_RUNTIME_SOURCE','Runtime source is not listed in the integrity manifest.',{path:path});
  var got=await fetchBytes(path);
  var actual=await sha256(got.bytes);
  if(actual!==record.sha256_hex)throw new RouteError('SOURCE_DIGEST_MISMATCH','Runtime source bytes do not match the integrity manifest.',{path:path,expected:record.sha256_hex,actual:actual});
  return freeze({path:path,record:record,bytes:got.bytes,response:got.response,sha256_hex:actual});
}

async function contextFromServiceWorker(){
  var statusMessage=await queryIntegrityWorker();
  var receipt=statusMessage&&statusMessage.receipt;
  if(!receipt||statusMessage.type!=='PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE'||receipt.state!=='ENFORCED'||!/^[0-9a-f]{64}$/.test(String(receipt.manifest_sha256||'')))throw new RouteError('INTEGRITY_WORKER_NOT_ENFORCING','Runtime integrity Service Worker is not in the enforced state.',{status:statusMessage});
  var got=await fetchBytes(MANIFEST_PATH);
  var actual=await sha256(got.bytes);
  if(actual!==receipt.manifest_sha256)throw new RouteError('INTEGRITY_MANIFEST_DIGEST_MISMATCH','Manifest bytes do not match the controlling Service Worker.',{expected:receipt.manifest_sha256,actual:actual});
  var manifest;
  try{manifest=JSON.parse(new TextDecoder().decode(got.bytes))}catch(error){throw new RouteError('INTEGRITY_MANIFEST_JSON_INVALID','Runtime integrity manifest is not valid JSON.',{error:String(error&&error.message||error)})}
  validateManifest(manifest);
  var index=indexManifest(manifest);
  return {
    source:'service_worker',manifest:manifest,manifestSha256:actual,index:index,workerStatus:receipt,
    verifyPath:function(path){return verifyWithIndex(path,index)}
  };
}

async function integrityContext(){
  if(integrityPromise)return integrityPromise;
  integrityPromise=(async function(){
    var bootstrap=global.PMPRuntimeIntegrityBootstrap;
    var context=bootstrap?contextFromBootstrap(bootstrap):await contextFromServiceWorker();
    activeIntegrityIndex=context.index;
    activeManifestSha256=context.manifestSha256;
    return context;
  })();
  return integrityPromise;
}

function roleNode(map,role){
  role=String(role||'').trim();
  if(!role)throw new RouteError('ROLE_EMPTY','A route role is required.');
  if(role==='entry'||role==='route_guardian'||role==='current_app')return map[role];
  var parts=role.split('.');
  if(parts.length!==2)throw new RouteError('ROLE_FORMAT_INVALID','Route role format is invalid.',{role:role});
  var group=parts[0],name=parts[1];
  if(['runtime_chain','tool_routes','recovery_routes','historic_routes'].indexOf(group)===-1)throw new RouteError('ROLE_GROUP_INVALID','Route role group is not permitted.',{role:role});
  if(!map[group]||!own(map[group],name))throw new RouteError('ROLE_MISSING','Requested route role is not declared by Current Map.',{role:role});
  return map[group][name];
}

function resolve(map,role){
  validateMap(map);
  var node=assertLocalRouteNode(roleNode(map,role),role,['.html','.js','.json']);
  var record=activeIntegrityIndex&&activeIntegrityIndex[String(node.path)];
  if(!record)throw new RouteError('ROLE_INTEGRITY_RECORD_MISSING','Requested route role has no runtime integrity record.',{role:role,path:node.path});
  return freeze({
    type:HANDOFF_TYPE,
    resolver_version:RESOLVER_VERSION,
    map_path:MAP_PATH,
    map_version:String(map.app_version),
    route_epoch:String(map.route_epoch),
    role:String(role),
    path:String(node.path),
    cache_key:String(node.cache_key||map.route_epoch),
    status:String(node.status||'declared'),
    source_sha256:String(record.sha256_hex),
    source_git_blob_sha:String(record.git_blob_sha||''),
    integrity_manifest_path:MANIFEST_PATH,
    integrity_manifest_sha256:String(activeManifestSha256||''),
    issued_at:new Date().toISOString()
  });
}

function normalizeHash(hash,map){
  validateMap(map);
  hash=String(hash||'');
  return map.allowed_hashes.indexOf(hash)!==-1?hash:String(map.default_hash||map.allowed_hashes[0]);
}

function inheritedRuntimeHash(handoff){
  if(String(handoff&&handoff.role||'').indexOf('runtime_chain.')!==0)return '';
  try{
    var current=new URL(global.location.href);
    if(current.searchParams.get('route_authority')!==MAP_PATH)return '';
    var inherited=current.searchParams.get('requested_hash')||'';
    return isScreenHash(inherited)?inherited:'';
  }catch(e){return ''}
}

function buildUrl(handoff,params,hash){
  if(!handoff||handoff.type!==HANDOFF_TYPE)throw new RouteError('HANDOFF_INVALID','A valid map-issued route handoff is required.');
  if(!/^[0-9a-f]{64}$/.test(String(handoff.source_sha256||'')))throw new RouteError('HANDOFF_INTEGRITY_MISSING','Route handoff does not contain an expected source digest.');
  var query=[];
  var safeParams={};
  params=params||{};
  Object.keys(params).forEach(function(k){safeParams[k]=params[k]});
  var effectiveHash=String(hash||'');
  var inherited=inheritedRuntimeHash(handoff);
  if(inherited)effectiveHash=inherited;
  if(!own(safeParams,'handoff_role'))safeParams.handoff_role=handoff.role;
  if(!own(safeParams,'route_authority'))safeParams.route_authority=handoff.map_path;
  if(!own(safeParams,'route_guardian_policy'))safeParams.route_guardian_policy='current_map';
  if(!own(safeParams,'source_sha256'))safeParams.source_sha256=handoff.source_sha256;
  if(!own(safeParams,'integrity_manifest_sha256'))safeParams.integrity_manifest_sha256=handoff.integrity_manifest_sha256;
  if(effectiveHash&&!own(safeParams,'requested_hash'))safeParams.requested_hash=effectiveHash;
  Object.keys(safeParams).sort().forEach(function(k){
    var v=safeParams[k];
    if(v===undefined||v===null)return;
    query.push(encodeURIComponent(k)+'='+encodeURIComponent(String(v)));
  });
  return handoff.path+(query.length?'?'+query.join('&'):'')+effectiveHash;
}

async function load(){
  var integrity=await integrityContext();
  var verified=await integrity.verifyPath(MAP_PATH);
  var map;
  try{map=JSON.parse(new TextDecoder().decode(verified.bytes))}catch(error){throw new RouteError('MAP_JSON_FAILED','Current Map is not valid JSON.',{map_path:MAP_PATH,error:String(error&&error.message||error)})}
  validateMap(map);
  return freeze({
    resolver_version:RESOLVER_VERSION,
    map_path:MAP_PATH,
    map_sha256:verified.sha256_hex,
    integrity_manifest_path:MANIFEST_PATH,
    integrity_manifest_sha256:integrity.manifestSha256,
    integrity_source:integrity.source,
    map:freeze(cloneJson(map)),
    loaded_at:new Date().toISOString()
  });
}

function diagnostic(error,context){
  return freeze({
    type:'PMP_ROUTE_FAIL_CLOSED_DIAGNOSTIC_V1',
    resolver_version:RESOLVER_VERSION,
    map_path:MAP_PATH,
    integrity_manifest_path:MANIFEST_PATH,
    integrity_manifest_sha256:String(activeManifestSha256||''),
    at:new Date().toISOString(),
    context:String(context||'route'),
    code:String(error&&error.code||'ROUTE_ERROR'),
    message:String(error&&error.message||error||'Unknown route error'),
    details:error&&error.details||null,
    action:'navigation_blocked_no_unverified_fallback_consulted'
  });
}

var api=freeze({
  version:RESOLVER_VERSION,
  mapPath:MAP_PATH,
  manifestPath:MANIFEST_PATH,
  handoffType:HANDOFF_TYPE,
  RouteError:RouteError,
  integrityContext:integrityContext,
  load:load,
  validateMap:validateMap,
  resolve:resolve,
  normalizeHash:normalizeHash,
  buildUrl:buildUrl,
  diagnostic:diagnostic
});

global.PMPCurrentRouteResolver=api;
try{global.dispatchEvent(new CustomEvent('pmp-current-route-resolver-ready',{detail:{version:RESOLVER_VERSION,map_path:MAP_PATH,manifest_path:MANIFEST_PATH}}))}catch(e){}
})(typeof window!=='undefined'?window:this);
