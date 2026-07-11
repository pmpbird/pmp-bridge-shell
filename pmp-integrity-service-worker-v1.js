'use strict';
const PMP_INTEGRITY_SW_VERSION='1.1.0-a003-runtime-integrity-sri';
const PMP_VERIFIED_CACHE='pmp-integrity-verified-v1';
const PMP_EXECUTABLE_EXTENSIONS=['.html','.htm','.js','.mjs','.json','.wasm'];
const PARAMS=new URL(self.location.href).searchParams;
const MANIFEST_PATH=PARAMS.get('manifest_path')||'pmp-runtime-integrity-manifest-v1.json';
const EXPECTED_MANIFEST_SHA256=String(PARAMS.get('manifest_sha256')||'').toLowerCase();
const ROOT_TRUST_ANCHOR=PARAMS.get('root_anchor')||'pmp-app-current.html';
const EXPECTED_SW_SHA256=String(PARAMS.get('expected_sw_sha256')||'').toLowerCase();
let manifestPromise=null;
let integrityIndex=null;
let externalIndex=null;
let manifestObject=null;

class IntegrityError extends Error{
  constructor(code,message,details){super(message||code);this.name='PMPIntegrityError';this.code=String(code||'INTEGRITY_ERROR');this.details=details||null}
}
function hex(buffer){return Array.from(new Uint8Array(buffer)).map(v=>v.toString(16).padStart(2,'0')).join('')}
async function sha256(data){return hex(await crypto.subtle.digest('SHA-256',data))}
function relPath(url){const u=new URL(url,self.registration.scope),scopePath=new URL(self.registration.scope).pathname;let p=decodeURIComponent(u.pathname);if(p.startsWith(scopePath))p=p.slice(scopePath.length);return p.replace(/^\/+/, '')}
function executablePath(path){const clean=String(path||'').split(/[?#]/)[0].toLowerCase();return PMP_EXECUTABLE_EXTENSIONS.some(ext=>clean.endsWith(ext))}
function responseWithHeaders(bytes,response,extra){const headers=new Headers(response&&response.headers||{});Object.keys(extra||{}).forEach(k=>headers.set(k,String(extra[k])));return new Response(bytes,{status:response&&response.status||200,statusText:response&&response.statusText||'OK',headers})}
function escapeHtml(v){return String(v).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function failResponse(code,path,details,status){const payload={type:'PMP_RUNTIME_INTEGRITY_FAILURE_V1',version:PMP_INTEGRITY_SW_VERSION,at:new Date().toISOString(),code,path:path||null,manifest_path:MANIFEST_PATH,manifest_sha256:EXPECTED_MANIFEST_SHA256,details:details||null,action:'response_blocked_no_unverified_fallback'};notifyAll({type:'PMP_RUNTIME_INTEGRITY_FAILURE',receipt:payload}).catch(()=>{});const isHtml=/\.html?$/i.test(String(path||''));if(isHtml){const body='<!doctype html><meta charset="utf-8"><title>PMP Integrity Block</title><style>body{margin:0;background:#351414;color:#fff;font-family:system-ui;padding:24px}pre{white-space:pre-wrap;background:#180909;border:2px solid #fff;border-radius:16px;padding:14px}</style><h1>Runtime source blocked</h1><pre>'+escapeHtml(JSON.stringify(payload,null,2))+'</pre>';return new Response(body,{status:status||412,headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-PMP-Integrity':'blocked'}})}return new Response(JSON.stringify(payload,null,2),{status:status||412,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-PMP-Integrity':'blocked'}})}
async function notifyAll(message){const clients=await self.clients.matchAll({includeUncontrolled:true,type:'window'});clients.forEach(client=>{try{client.postMessage(message)}catch(e){}})}
async function fetchArray(url,init){const response=await fetch(url,Object.assign({cache:'no-store',credentials:'same-origin'},init||{}));if(!response.ok)throw new IntegrityError('SOURCE_HTTP_FAILED','Runtime source request failed.',{url:String(url),status:response.status});return{response,bytes:await response.arrayBuffer()}}
function validateManifest(manifest){if(!manifest||manifest.type!=='PMP_RUNTIME_INTEGRITY_MANIFEST_V1')throw new IntegrityError('MANIFEST_TYPE_INVALID','Integrity manifest type is invalid.');if(manifest.algorithm!=='SHA-256')throw new IntegrityError('MANIFEST_ALGORITHM_INVALID','Integrity manifest must use SHA-256.');if(manifest.unlisted_executable_policy!=='FAIL_CLOSED')throw new IntegrityError('MANIFEST_POLICY_INVALID','Unlisted executable policy must fail closed.');if(!Array.isArray(manifest.records)||manifest.records.length===0)throw new IntegrityError('MANIFEST_RECORDS_MISSING','Integrity manifest has no records.');const roots=Array.isArray(manifest.root_trust_anchors)?manifest.root_trust_anchors:[];if(!roots.some(r=>r&&r.path===ROOT_TRUST_ANCHOR))throw new IntegrityError('ROOT_TRUST_ANCHOR_MISMATCH','Manifest root trust anchor does not match Service Worker registration.');return manifest}
async function loadManifest(force){
  if(manifestPromise&&!force)return manifestPromise;
  manifestPromise=(async()=>{
    if(!/^[0-9a-f]{64}$/.test(EXPECTED_MANIFEST_SHA256))throw new IntegrityError('MANIFEST_DIGEST_MISSING','Expected manifest SHA-256 is missing or invalid.');
    const url=new URL(MANIFEST_PATH,self.registration.scope);url.searchParams.set('pmp_integrity_manifest_check',Date.now());
    const got=await fetchArray(url.href),actual=await sha256(got.bytes);
    if(actual!==EXPECTED_MANIFEST_SHA256)throw new IntegrityError('MANIFEST_DIGEST_MISMATCH','Integrity manifest bytes do not match the bootstrap digest.',{expected:EXPECTED_MANIFEST_SHA256,actual});
    let parsed;try{parsed=JSON.parse(new TextDecoder().decode(got.bytes))}catch(error){throw new IntegrityError('MANIFEST_JSON_INVALID','Integrity manifest is not valid JSON.',{error:String(error&&error.message||error)})}
    validateManifest(parsed);
    const index={};parsed.records.forEach(record=>{if(!record||typeof record.path!=='string'||!/^[0-9a-f]{64}$/.test(String(record.sha256_hex||'')))throw new IntegrityError('MANIFEST_RECORD_INVALID','Integrity manifest contains an invalid record.',{record});if(index[record.path])throw new IntegrityError('MANIFEST_DUPLICATE_PATH','Integrity manifest contains a duplicate path.',{path:record.path});index[record.path]=record});
    const ext={};(parsed.external_records||[]).forEach(record=>{if(!record||typeof record.url!=='string'||typeof record.sri!=='string'||!/^sha256-[A-Za-z0-9+/=]+$/.test(record.sri))throw new IntegrityError('EXTERNAL_RECORD_INVALID','Integrity manifest contains an invalid external record.',{record});ext[record.url]=record});
    integrityIndex=index;externalIndex=ext;manifestObject=parsed;return parsed;
  })();
  return manifestPromise;
}
function cacheKey(record){return new Request(new URL('__pmp_integrity_cache__/'+record.sha256_hex+'/'+encodeURIComponent(record.path),self.registration.scope).href)}
function transformExternalScripts(record,bytes){
  if(!record||record.execution_class!=='EXECUTABLE_DOCUMENT'||!externalIndex)return{bytes,transforms:0};
  let text;try{text=new TextDecoder().decode(bytes)}catch(e){return{bytes,transforms:0}}
  let transforms=0;
  text=text.replace(/<script\b(?=[^>]*\bsrc\s*=)([^>]*)>/gi,function(full,attrs){
    const match=attrs.match(/\bsrc\s*=\s*(['"])(.*?)\1/i);if(!match)return full;
    const src=match[2],external=externalIndex[src];if(!external||!Array.isArray(external.consumers)||external.consumers.indexOf(record.path)===-1)return full;
    const integrityMatch=attrs.match(/\bintegrity\s*=\s*(['"])(.*?)\1/i);if(integrityMatch&&integrityMatch[2]!==external.sri)throw new IntegrityError('EXTERNAL_SRI_MISMATCH','Document contains an incorrect external script integrity value.',{path:record.path,url:src,expected:external.sri,actual:integrityMatch[2]});
    const crossMatch=attrs.match(/\bcrossorigin\s*=\s*(['"])(.*?)\1/i);if(crossMatch&&String(crossMatch[2]).toLowerCase()!=='anonymous')throw new IntegrityError('EXTERNAL_CORS_POLICY_INVALID','External script must use anonymous CORS.',{path:record.path,url:src,actual:crossMatch[2]});
    let addition='';if(!integrityMatch)addition+=' integrity="'+external.sri+'"';if(!crossMatch)addition+=' crossorigin="anonymous"';transforms++;return '<script'+attrs+addition+'>';
  });
  return{bytes:new TextEncoder().encode(text).buffer,transforms};
}
function finalizeVerified(record,bytes,response,source){const transformed=transformExternalScripts(record,bytes),extra={'Cache-Control':'no-store','X-PMP-Integrity':source,'X-PMP-Integrity-SHA256':record.sha256_hex};if(transformed.transforms)extra['X-PMP-Integrity-Transform']='external-sri:'+transformed.transforms;return responseWithHeaders(transformed.bytes,response,extra)}
async function readVerifiedCache(record){const cache=await caches.open(PMP_VERIFIED_CACHE),hit=await cache.match(cacheKey(record));if(!hit)return null;const bytes=await hit.arrayBuffer(),actual=await sha256(bytes);if(actual!==record.sha256_hex){await cache.delete(cacheKey(record));return null}return finalizeVerified(record,bytes,hit,'verified-cache')}
async function storeVerifiedCache(record,bytes,response){const cache=await caches.open(PMP_VERIFIED_CACHE),cached=responseWithHeaders(bytes,response,{'Cache-Control':'no-store','X-PMP-Integrity':'verified-network-original','X-PMP-Integrity-SHA256':record.sha256_hex});await cache.put(cacheKey(record),cached.clone())}
async function verifiedResponse(request,record){let got;try{got=await fetchArray(request,{cache:'no-store'})}catch(error){const cached=await readVerifiedCache(record);if(cached)return cached;throw error}const actual=await sha256(got.bytes);if(actual!==record.sha256_hex)throw new IntegrityError('SOURCE_DIGEST_MISMATCH','Runtime source bytes do not match the integrity manifest.',{path:record.path,expected:record.sha256_hex,actual});await storeVerifiedCache(record,got.bytes,got.response);return finalizeVerified(record,got.bytes,got.response,'verified-network')}
async function manifestResponse(request){const got=await fetchArray(request,{cache:'no-store'}),actual=await sha256(got.bytes);if(actual!==EXPECTED_MANIFEST_SHA256)throw new IntegrityError('MANIFEST_DIGEST_MISMATCH','Requested manifest bytes do not match the bootstrap digest.',{expected:EXPECTED_MANIFEST_SHA256,actual});return responseWithHeaders(got.bytes,got.response,{'Cache-Control':'no-store','X-PMP-Integrity':'verified-manifest','X-PMP-Integrity-SHA256':actual})}
async function rootAnchorResponse(request){const response=await fetch(request,{cache:'no-store',credentials:'same-origin'});if(!response.ok)throw new IntegrityError('ROOT_ANCHOR_HTTP_FAILED','Bootstrap root could not be loaded.',{status:response.status});const headers=new Headers(response.headers);headers.set('Cache-Control','no-store');headers.set('X-PMP-Integrity','root-trust-anchor');return new Response(response.body,{status:response.status,statusText:response.statusText,headers})}
async function handleFetch(request){const url=new URL(request.url);if(url.origin!==self.location.origin)return fetch(request);const path=relPath(url.href);if(path===ROOT_TRUST_ANCHOR)return rootAnchorResponse(request);if(path===MANIFEST_PATH)return manifestResponse(request);await loadManifest(false);const record=integrityIndex&&integrityIndex[path];if(record)return verifiedResponse(request,record);if(executablePath(path))return failResponse('UNLISTED_EXECUTABLE_SOURCE',path,{destination:request.destination||null},412);return fetch(request,{cache:'no-store'})}
function statusReceipt(reason){return{type:'PMP_RUNTIME_INTEGRITY_STATUS_V1',version:PMP_INTEGRITY_SW_VERSION,reason:reason||'status',at:new Date().toISOString(),state:manifestObject?'ENFORCED':'INITIALIZING',manifest_path:MANIFEST_PATH,manifest_sha256:EXPECTED_MANIFEST_SHA256,root_trust_anchor:ROOT_TRUST_ANCHOR,expected_sw_sha256:EXPECTED_SW_SHA256,record_count:manifestObject&&manifestObject.counts&&manifestObject.counts.runtime_records||0,external_record_count:manifestObject&&manifestObject.counts&&manifestObject.counts.external_records||0,unlisted_executable_policy:'FAIL_CLOSED',network_policy:'VERIFY_BEFORE_RESPONSE',offline_policy:'MATCHING_VERIFIED_CACHE_ONLY',external_policy:'VERIFIED_DOCUMENT_THEN_SRI',does_not_touch:['localStorage','IndexedDB','Bank data','user content']}}
function reply(event,message){try{if(event.ports&&event.ports[0]){event.ports[0].postMessage(message);return true}}catch(e){}try{if(event.source&&event.source.postMessage){event.source.postMessage(message);return true}}catch(e){}return false}
self.addEventListener('install',event=>{event.waitUntil((async()=>{await loadManifest(true);await self.skipWaiting();await notifyAll({type:'PMP_RUNTIME_INTEGRITY_INSTALLED',receipt:statusReceipt('install')})})())});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{await loadManifest(false);await self.clients.claim();await notifyAll({type:'PMP_RUNTIME_INTEGRITY_ACTIVATED',receipt:statusReceipt('activate')})})())});
self.addEventListener('message',event=>{const data=event.data||{};if(data.type==='PMP_RUNTIME_INTEGRITY_STATUS_REQUEST'){event.waitUntil((async()=>{try{await loadManifest(false);reply(event,{type:'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE',receipt:statusReceipt('status')})}catch(error){reply(event,{type:'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE',receipt:Object.assign(statusReceipt('status_error'),{state:'FAILED',error:{code:error.code||'INTEGRITY_ERROR',message:String(error&&error.message||error),details:error.details||null}})})}})());return}if(data.type==='PMP_RUNTIME_INTEGRITY_REFRESH_MANIFEST'){event.waitUntil((async()=>{manifestPromise=null;integrityIndex=null;externalIndex=null;manifestObject=null;await loadManifest(true);reply(event,{type:'PMP_RUNTIME_INTEGRITY_REFRESH_DONE',receipt:statusReceipt('refresh')})})())}});
self.addEventListener('fetch',event=>{const request=event.request;if(request.method!=='GET')return;event.respondWith((async()=>{try{return await handleFetch(request)}catch(error){return failResponse(error.code||'INTEGRITY_ERROR',relPath(request.url),{message:String(error&&error.message||error),details:error.details||null},412)}})())});
