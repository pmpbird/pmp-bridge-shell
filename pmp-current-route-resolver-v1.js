(function(global){
'use strict';

var MAP_PATH='pmp-current-map-v12.json';
var RESOLVER_VERSION='PMP_CURRENT_ROUTE_RESOLVER_V1_20260711A';
var HANDOFF_TYPE='PMP_ROUTE_HANDOFF_V1';
var MAP_TYPE='PMP_CURRENT_APP_MAP';
var CONTRACT_TYPE='PMP_ROUTE_CONTRACT_V1';

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
    if(!/^#[a-z0-9-]+$/.test(hash))throw new RouteError('HASH_INVALID','Current Map contains an invalid screen hash.',{hash:hash});
    if(seen[hash])throw new RouteError('HASH_DUPLICATE','Current Map contains a duplicate screen hash.',{hash:hash});
    seen[hash]=true;
  });
}

function validateMap(map){
  if(!map||typeof map!=='object'||Array.isArray(map))throw new RouteError('MAP_INVALID','Current Map is not a JSON object.');
  if(map.type!==MAP_TYPE)throw new RouteError('MAP_TYPE_INVALID','Current Map type is invalid.',{expected:MAP_TYPE,actual:map.type});
  if(!map.route_contract||map.route_contract.type!==CONTRACT_TYPE)throw new RouteError('CONTRACT_INVALID','Current Map route contract is missing or invalid.');
  if(map.route_contract.sole_authority!==MAP_PATH)throw new RouteError('AUTHORITY_INVALID','Current Map does not name itself as sole route authority.',{actual:map.route_contract.sole_authority});
  if(map.route_contract.resolver!== 'pmp-current-route-resolver-v1.js')throw new RouteError('RESOLVER_CONTRACT_INVALID','Current Map resolver contract does not match this resolver.',{actual:map.route_contract.resolver});
  if(map.route_contract.failure_mode!=='fail_closed'||map.route_contract.implicit_fallbacks!==false)throw new RouteError('FAILURE_POLICY_INVALID','Current Map must require fail-closed routing with no implicit fallbacks.');
  if(!map.route_epoch||!map.app_version)throw new RouteError('MAP_IDENTITY_INCOMPLETE','Current Map version or route epoch is missing.');
  assertLocalRouteNode(map.entry,'entry',['.html']);
  assertLocalRouteNode(map.route_guardian,'route_guardian',['.html']);
  assertLocalRouteNode(map.current_app,'current_app',['.html']);
  validateHashes(map);
  return map;
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
    issued_at:new Date().toISOString()
  });
}

function normalizeHash(hash,map){
  validateMap(map);
  hash=String(hash||'');
  return map.allowed_hashes.indexOf(hash)!==-1?hash:String(map.default_hash||map.allowed_hashes[0]);
}

function buildUrl(handoff,params,hash){
  if(!handoff||handoff.type!==HANDOFF_TYPE)throw new RouteError('HANDOFF_INVALID','A valid map-issued route handoff is required.');
  var query=[];
  params=params||{};
  Object.keys(params).sort().forEach(function(k){
    var v=params[k];
    if(v===undefined||v===null)return;
    query.push(encodeURIComponent(k)+'='+encodeURIComponent(String(v)));
  });
  return handoff.path+(query.length?'?'+query.join('&'):'')+String(hash||'');
}

async function load(){
  var url=MAP_PATH+'?pmp_route_epoch_check='+encodeURIComponent(String(Date.now()));
  var response;
  try{
    response=await fetch(url,{cache:'no-store',credentials:'same-origin'});
  }catch(error){
    throw new RouteError('MAP_FETCH_FAILED','Current Map could not be fetched.',{map_path:MAP_PATH,error:String(error&&error.message||error)});
  }
  if(!response||!response.ok)throw new RouteError('MAP_HTTP_FAILED','Current Map request did not succeed.',{map_path:MAP_PATH,status:response&&response.status});
  var map;
  try{map=await response.json()}catch(error){throw new RouteError('MAP_JSON_FAILED','Current Map is not valid JSON.',{map_path:MAP_PATH,error:String(error&&error.message||error)})}
  validateMap(map);
  return freeze({
    resolver_version:RESOLVER_VERSION,
    map_path:MAP_PATH,
    map:freeze(cloneJson(map)),
    loaded_at:new Date().toISOString()
  });
}

function diagnostic(error,context){
  return freeze({
    type:'PMP_ROUTE_FAIL_CLOSED_DIAGNOSTIC_V1',
    resolver_version:RESOLVER_VERSION,
    map_path:MAP_PATH,
    at:new Date().toISOString(),
    context:String(context||'route'),
    code:String(error&&error.code||'ROUTE_ERROR'),
    message:String(error&&error.message||error||'Unknown route error'),
    details:error&&error.details||null,
    action:'navigation_blocked_no_fallback_consulted'
  });
}

var api=freeze({
  version:RESOLVER_VERSION,
  mapPath:MAP_PATH,
  handoffType:HANDOFF_TYPE,
  RouteError:RouteError,
  load:load,
  validateMap:validateMap,
  resolve:resolve,
  normalizeHash:normalizeHash,
  buildUrl:buildUrl,
  diagnostic:diagnostic
});

global.PMPCurrentRouteResolver=api;
try{global.dispatchEvent(new CustomEvent('pmp-current-route-resolver-ready',{detail:{version:RESOLVER_VERSION,map_path:MAP_PATH}}))}catch(e){}
})(typeof window!=='undefined'?window:this);
