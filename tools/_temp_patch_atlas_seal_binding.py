#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('pmp-active-path-discovery-machine-v1.js')
text = path.read_text('utf-8')
original = text

def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    text = text.replace(old, new, 1)

one("const VERSION='1.4.0-fresh-scan-classification-truth-20260825A';",
    "const VERSION='1.5.0-served-a003-reference-truth-20260826A';", 'version')
one("const CLASSIFICATION_REVISION='1.0.0-current-map-http-truth-20260825A';",
    "const CLASSIFICATION_REVISION='1.1.0-served-a003-reference-truth-20260826A';", 'revision')
one("const MAP_PATH='pmp-current-map-v12.json';",
    "const MAP_PATH='pmp-current-map-v12.json';\nconst MANIFEST_PATH='pmp-runtime-integrity-manifest-v1.json';", 'manifest path')

pat = re.compile(r"function extract\(text\)\{.*?\}\nfunction isPackage", re.S)
replacement = r'''function stripStaticComments(text,path){
  const src=String(text||''),kind=String(path||'');
  if(!/\.(?:js|mjs|css|html?|htm)$/i.test(kind))return src;
  let out='',i=0,quote='',escape=false,line=false,block=false,html=false;
  while(i<src.length){
    const c=src[i],n=src[i+1]||'';
    if(line){if(c==='\n'){line=false;out+=c}else out+=' ';i+=1;continue}
    if(block){if(c==='*'&&n==='/'){block=false;out+='  ';i+=2}else{out+=c==='\n'?'\n':' ';i+=1}continue}
    if(html){if(src.slice(i,i+3)==='-->'){html=false;out+='   ';i+=3}else{out+=c==='\n'?'\n':' ';i+=1}continue}
    if(quote){out+=c;if(escape)escape=false;else if(c==='\\')escape=true;else if(c===quote)quote='';i+=1;continue}
    if(c==="'"||c==='"'||c==='`'){quote=c;out+=c;i+=1;continue}
    if(c==='/'&&n==='/'&&/\.(?:js|mjs)$/i.test(kind)){line=true;out+='  ';i+=2;continue}
    if(c==='/'&&n==='*'){block=true;out+='  ';i+=2;continue}
    if(c==='<'&&src.slice(i,i+4)==='<!--'){html=true;out+='    ';i+=4;continue}
    out+=c;i+=1;
  }
  return out;
}
function extract(text,path){
  const out=[],strong=new Set(),source=stripStaticComments(text,path);
  function add(value,isStrong){const p=clean(value);if(!p)return;if(isStrong)strong.add(p);out.push(p)}
  String(source).replace(/(?:src|href)\s*=\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/\b(?:fetch|importScripts|import)\s*\(\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/\bnew\s+(?:Worker|SharedWorker)\s*\(\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/['"`(=\s]([a-zA-Z0-9._/-]+\.(?:html|htm|js|mjs|json|css|wasm))(?=$|[?#'"`\s)>,;])/gi,(m,p)=>{
    const c=clean(p);
    if(c&&!strong.has(c)&&!/^(?:metadata|packet|report)\.json$/i.test(c))out.push(c);
    return m;
  });
  return uniq(out);
}
function isPackage'''
text, count = pat.subn(lambda m: replacement, text, count=1)
if count != 1:
    raise SystemExit(f'extract block: expected one match, got {count}')

pat = re.compile(r"function integrityEvidence\(\)\{.*?\}\nasync function run", re.S)
replacement = r'''async function servedIntegrityEvidence(scanId){
  const out={source:'SERVED_A003_MANIFEST',path:MANIFEST_PATH,scan_id:String(scanId||''),fetch_ok:false,status:0,manifest_sha256:null,manifest_version:null,runtime_source_set_sha256:null,record_count:null,error:null};
  try{
    const response=await fetch(MANIFEST_PATH+'?active_path_integrity='+encodeURIComponent(out.scan_id),{cache:'no-store'});
    out.status=response.status;
    const bytes=new Uint8Array(await response.arrayBuffer());
    if(!response.ok){out.error='A003_MANIFEST_HTTP_'+response.status;return out}
    if(!(globalThis.crypto&&globalThis.crypto.subtle)){out.error='WEB_CRYPTO_UNAVAILABLE';return out}
    const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);
    out.manifest_sha256=Array.from(new Uint8Array(digest)).map(v=>v.toString(16).padStart(2,'0')).join('');
    try{
      const manifest=JSON.parse(new TextDecoder().decode(bytes));
      out.manifest_version=manifest.version||null;
      out.runtime_source_set_sha256=manifest.runtime_source_set_sha256||null;
      out.record_count=Array.isArray(manifest.records)?manifest.records.length:null;
    }catch(error){out.error='A003_MANIFEST_JSON_'+String(error&&error.message||error);return out}
    out.fetch_ok=true;
    return out;
  }catch(error){out.error=String(error&&error.message||error);return out}
}
async function run'''
text, count = pat.subn(lambda m: replacement, text, count=1)
if count != 1:
    raise SystemExit(f'integrity block: expected one match, got {count}')

one("const started=now(),policy=await loadPolicy(),atlas=atlasPaths(),live=liveFiles(),queue=[],seen={},rows=[],edges=[];",
    "const started=now(),policy=await loadPolicy(),integrity=await servedIntegrityEvidence(requestedScanId),atlas=atlasPaths(),live=liveFiles(),queue=[],seen={},rows=[],edges=[];", 'run evidence')
one("row.found=extract(text);if(canFollow(item))row.found.forEach(path=>{",
    "row.found=extract(text,item.path);if(canFollow(item))row.found.forEach(path=>{", 'path-aware extraction')
one("const integrity=integrityEvidence();", "", 'remove persisted integrity')
one("runtime_integrity_manifest_sha256:integrity.manifest_sha256,",
    "runtime_integrity_manifest_sha256:integrity.manifest_sha256,\n    runtime_integrity_binding:integrity,", 'report binding')
one("freeze_gate:{pass:policy.map_fetch_ok&&hard.length===0&&currentPolicyRejected.length===0&&currentHttpRejected.length===0&&currentNetworkErrors.length===0&&oldAsRoot.length===0,rule:'PASS requires current-map policy evidence, zero true missing required current files, zero current precondition/HTTP/network rejects, and zero historic files acting as current boot roots. Reachable files absent from the Atlas registry are ATLAS_REGISTRY_GAP, not HARD_MISSING.'}",
    "freeze_gate:{pass:policy.map_fetch_ok&&integrity.fetch_ok&&!!integrity.manifest_sha256&&integrity.scan_id===requestedScanId&&hard.length===0&&currentPolicyRejected.length===0&&currentHttpRejected.length===0&&currentNetworkErrors.length===0&&oldAsRoot.length===0,rule:'PASS requires current-map policy evidence, a served A-003 manifest digest bound to this exact scan ID, zero true missing required current files, zero current precondition/HTTP/network rejects, and zero historic files acting as current boot roots. Static comments and weak generic output basenames are not runtime dependency claims; reachable files absent from the Atlas registry are ATLAS_REGISTRY_GAP, not HARD_MISSING.'}", 'freeze gate binding')

if text == original:
    raise SystemExit('scanner did not change')
path.write_text(text, 'utf-8')
print('PATCH_OK')
