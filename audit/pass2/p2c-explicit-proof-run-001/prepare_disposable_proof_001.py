#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, json, mimetypes, os, re, shutil, zipfile
from pathlib import Path

SOURCE_COMMIT="c618596f2b5c99ca7f355153a5bd31268170df80"
EXPECTED_PATCH_SHA="a0fc06f2197e59914780edc0da9fda6cd5f4d38526d6f0d978b77fffdf527d7c"
EXPECTED_CLOSURE_SHA="2b61d40a1f13e5bce42176f9044f02acc5918a2feb21eb01bcdea7a4bb2cb9af"
EXPECTED_V14_SHA="04fd41e7ecfdea999db939a8eaf8a069b77c5209753941e0464a334608ee6aaf"
EXPECTED_PAYLOAD_SHA="6384c71b47825c52b3697cffeb84aabf951069199e2d843e636253e502a4bdee"
RUNTIME_EXTENSIONS={".html",".htm",".js",".mjs",".json",".wasm",".css"}
EXCLUDED_DIRS={".git",".github","audit","tools","node_modules","__pycache__"}
EXCLUDED_FILES={"pmp-app-current.html","pmp-runtime-integrity-manifest-v1.json"}

def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def hf(p:Path)->str:
    x=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):x.update(c)
    return x.hexdigest()
def gitblob(b:bytes)->str:return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def file_snapshot(root:Path)->dict:
    out={}
    for p in sorted(root.rglob("*")):
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel==".git":continue
        out[rel]={"bytes":p.stat().st_size,"sha256":hf(p)}
    return out
def copy_tree(src:Path,dst:Path):
    if dst.exists():shutil.rmtree(dst)
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns(".git","node_modules","__pycache__"))
def runtime_paths(root:Path):
    out=[]
    for dp,dns,fns in os.walk(root):
        dns[:]=sorted(d for d in dns if d not in EXCLUDED_DIRS)
        b=Path(dp)
        for n in sorted(fns):
            p=b/n; rel=p.relative_to(root).as_posix()
            if rel in EXCLUDED_FILES or p.suffix.lower() not in RUNTIME_EXTENSIONS:continue
            out.append(p)
    return out
def record(root:Path,p:Path):
    b=p.read_bytes(); rel=p.relative_to(root).as_posix()
    dg=hashlib.sha256(b).digest()
    return {"path":rel,"bytes":len(b),"git_blob_sha":gitblob(b),
      "sha256_hex":dg.hex(),"sha256_base64":base64.b64encode(dg).decode(),
      "sri":"sha256-"+base64.b64encode(dg).decode(),
      "mime_type":mimetypes.guess_type(rel)[0] or "application/octet-stream",
      "execution_class":{".html":"EXECUTABLE_DOCUMENT",".htm":"EXECUTABLE_DOCUMENT",".js":"EXECUTABLE_SCRIPT",".mjs":"EXECUTABLE_MODULE",".json":"RUNTIME_DATA",".wasm":"EXECUTABLE_WASM",".css":"STYLE_SOURCE"}.get(p.suffix.lower(),"RUNTIME_SOURCE"),
      "enforcement":"SERVICE_WORKER_PRE_RESPONSE_SHA256"}
def flatten(v,o):
    if isinstance(v,dict):
        if isinstance(v.get("path"),str):o.add(v["path"].split("?",1)[0].split("#",1)[0])
        for x in v.values():flatten(x,o)
    elif isinstance(v,list):
        for x in v:flatten(x,o)
def reseal(root:Path,receipt_sha:str):
    template=json.loads((root/"pmp-runtime-integrity-manifest-v1.json").read_text())
    records=sorted((record(root,p) for p in runtime_paths(root)),key=lambda x:x["path"])
    m={k:v for k,v in template.items() if k not in {"records","counts","source_commit","proof_source_commit"}}
    m["type"]="PMP_RUNTIME_INTEGRITY_MANIFEST_V1";m["version"]="20260711A-A003-FINAL"
    m["source_commit"]="DISPOSABLE_P2C_PROOF_001"
    m["proof_source_commit"]=SOURCE_COMMIT
    m["proof_authorization_receipt_sha256"]=receipt_sha
    m["records"]=records
    mp=set();flatten(json.loads((root/"pmp-current-map-v12.json").read_text()),mp);mp.discard("pmp-app-current.html")
    m["counts"]={"runtime_records":len(records),"executable_records":sum(Path(r["path"]).suffix.lower() in {".html",".htm",".js",".mjs",".json",".wasm"} for r in records),"style_records":sum(Path(r["path"]).suffix.lower()==".css" for r in records),"map_declared_paths":len(mp),"map_declared_covered":sum(p in {r["path"] for r in records} for p in mp),"historical_records":len(m.get("historical_records",[])),"external_records":len(m.get("external_records",[])),"external_errors":0}
    mb=(json.dumps(m,indent=2,sort_keys=True)+"\n").encode()
    (root/"pmp-runtime-integrity-manifest-v1.json").write_bytes(mb)
    md=h(mb)
    rootp=root/"pmp-app-current.html";s=rootp.read_text()
    s,n=re.subn(r"const MANIFEST_SHA256='[0-9a-f]{64}';",f"const MANIFEST_SHA256='{md}';",s,count=1)
    if n!=1:raise SystemExit("ROOT_MANIFEST_DIGEST_REPLACEMENT_FAILED")
    rootp.write_text(s)
    runtime_set=h(("\n".join(f"{r['path']}:{r['sha256_hex']}" for r in records)+"\n").encode())
    seal={"type":"PMP_A003_MANIFEST_SEAL_V1","status":"SEALED_DISPOSABLE_PROOF_ONLY","repair_id":"A-003","manifest_path":"pmp-runtime-integrity-manifest-v1.json","manifest_sha256":md,"manifest_bytes":len(mb),"manifest_version":"20260711A-A003-FINAL","runtime_source_set_sha256":runtime_set,"root_trust_anchor":"pmp-app-current.html","root_self_verifiable":False,"sealed_branch":"DISPOSABLE_COPY_ONLY","source_repository_commit":SOURCE_COMMIT,"proof_authorization_receipt_sha256":receipt_sha,"production_merge_authorized":False,"rule":"Disposable proof seal only. Production remains untouched."}
    (root/"audit/a003-manifest-seal.json").parent.mkdir(parents=True,exist_ok=True)
    (root/"audit/a003-manifest-seal.json").write_text(json.dumps(seal,indent=2,sort_keys=True)+"\n")
    return {"manifest_sha256":md,"runtime_record_count":len(records),"runtime_source_set_sha256":runtime_set}
def transform_overlay(payload:zipfile.ZipFile,root:Path,receipt_sha:str):
    brokers=["pmp-p2c-production-storage-owner-broker-candidate-001.js","pmp-p2c-production-indexeddb-owner-broker-candidate-001.js","pmp-p2c-production-cache-owner-broker-candidate-001.js","pmp-p2c-production-verified-loader-owner-broker-candidate-001.js"]
    for n in brokers:(root/n).write_bytes(payload.read("closure/"+n))
    policy=json.loads(payload.read("closure/pmp-p2c-production-enforcement-policy-candidate-002.json"))
    policy.update({"type":"PMP_ACTOR_AUTHORITY_POLICY_V1","version":"2.0.0-disposable-proof-active","activation_authorized":True,"active_chain_integration":True,"production_active_chain_integration":False,"proof_scope":"DISPOSABLE_COPY_ONLY","authorization_receipt_sha256":receipt_sha})
    (root/"pmp-p2c-production-enforcement-policy-candidate-001.json").write_text(json.dumps(policy,indent=2,sort_keys=True)+"\n")
    manifest=json.loads(payload.read("closure/pmp-p2c-production-enforcement-source-manifest-candidate-002.json"))
    manifest.update({"type":"PMP_P2C_PRODUCTION_ENFORCEMENT_SOURCE_MANIFEST_CANDIDATE_001","version":"2.0.0-disposable-proof-active","status":"EXACT_DISPOSABLE_PROOF_ACTIVE","active_chain_integration":True,"production_active_chain_integration":False,"proof_scope":"DISPOSABLE_COPY_ONLY","authorization_receipt_sha256":receipt_sha})
    manifest["manifest_sha256"]=h(json.dumps(manifest["records"],sort_keys=True,separators=(",",":")).encode())
    (root/"pmp-p2c-production-enforcement-source-manifest-candidate-001.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    reg=json.loads(payload.read("closure/pmp-p2c-production-enforcement-broker-registry-candidate-002.json"))
    reg.update({"type":"PMP_P2C_PRODUCTION_ENFORCEMENT_BROKER_REGISTRY_CANDIDATE_001","version":"2.0.0-disposable-proof-active","status":"DISPOSABLE_PROOF_ACTIVE","activation_authorized":True,"active_chain_integration":True,"production_active_chain_integration":False,"proof_scope":"DISPOSABLE_COPY_ONLY","authorization_receipt_sha256":receipt_sha})
    (root/"pmp-p2c-production-enforcement-broker-registry-candidate-001.json").write_text(json.dumps(reg,indent=2,sort_keys=True)+"\n")
    for n in ["P2C_STORAGE_OWNER_NAMESPACE_CONTRACT_001.json","P2C_INDEXEDDB_OWNER_NAMESPACE_CONTRACT_001.json","P2C_CACHE_OWNER_NAMESPACE_CONTRACT_001.json","P2C_VERIFIED_LOADER_OWNER_NAMESPACE_CONTRACT_001.json"]:(root/n).write_bytes(payload.read("closure/"+n))
    lock=json.loads((root/"pmp-p2c-production-enforcement-activation-lock-candidate-001.json").read_text())
    lock.update({"authorized":True,"activation_receipt_sha256":receipt_sha,"active_chain_integration":True,"production_active_chain_integration":False,"proof_scope":"DISPOSABLE_COPY_ONLY","pass2_complete":False,"pass3_started":False})
    (root/"pmp-p2c-production-enforcement-activation-lock-candidate-001.json").write_text(json.dumps(lock,indent=2,sort_keys=True)+"\n")
    cp=root/"pmp-p2c-production-owner-broker-controller-candidate-001.js";s=cp.read_text()
    old="if(b.proof==='DENY_ALL')throw new Error('BROKER_DISABLED')"
    new="if(['EXACT_ACTOR_KEY_CONTRACT','EXACT_DATABASE_STORE_KEY_CONTRACT','A003_EXACT_SOURCE_DIGEST','A003_P2C_REALM_LEASE_QUARANTINE'].includes(b.proof)){if(!p.contract_closed)throw new Error('OWNER_NAMESPACE_CONTRACT_PROOF_REQUIRED');return}if(b.proof==='DENY_ALL')throw new Error('BROKER_DISABLED');throw new Error('BROKER_PROOF_TYPE_DENIED')"
    if old not in s:raise SystemExit("BROKER_CONTROLLER_PATCH_POINT_MISSING")
    cp.write_text(s.replace(old,new,1))
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--baseline-root",type=Path,required=True);ap.add_argument("--activated-root",type=Path,required=True);ap.add_argument("--payload-package",type=Path,required=True);ap.add_argument("--authorization-receipt",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);ap.add_argument("--activated-existing",action="store_true");x=ap.parse_args()
    if hf(x.payload_package)!=EXPECTED_PAYLOAD_SHA:raise SystemExit("PAYLOAD_PACKAGE_SHA_MISMATCH")
    auth=json.loads(x.authorization_receipt.read_text());authsha=hf(x.authorization_receipt)
    req={"authorized":True,"authorization_scope":"PRODUCTION_SHAPED_ACTIVATION_AND_ROLLBACK_PROOF_ONLY","activation_itself_authorized":False,"production_apply_authorized":False,"source_repository_commit":SOURCE_COMMIT,"canonical_v14_sha256":EXPECTED_V14_SHA,"base_patch_package_sha256":EXPECTED_PATCH_SHA,"owner_namespace_closure_package_sha256":EXPECTED_CLOSURE_SHA}
    for k,v in req.items():
        if auth.get(k)!=v:raise SystemExit("AUTHORIZATION_RECEIPT_INVALID:"+k)
    baseline=file_snapshot(x.baseline_root)
    if len(baseline)!=1481:raise SystemExit(f"BASELINE_FILE_COUNT_MISMATCH:{len(baseline)}")
    if x.activated_existing:
        if not x.activated_root.is_dir(): raise SystemExit("ACTIVATED_EXISTING_ROOT_MISSING")
        if file_snapshot(x.activated_root)!=baseline: raise SystemExit("ACTIVATED_EXISTING_BASELINE_MISMATCH")
    else:
        copy_tree(x.baseline_root,x.activated_root)
    with zipfile.ZipFile(x.payload_package) as pz:
        binding=json.loads(pz.read("PAYLOAD_BINDING.json"))
        if binding.get("base_patch_package_sha256")!=EXPECTED_PATCH_SHA or binding.get("owner_namespace_closure_package_sha256")!=EXPECTED_CLOSURE_SHA:raise SystemExit("PAYLOAD_SOURCE_BINDING_MISMATCH")
        records={r["path"]:r for r in binding.get("records",[])}
        for name,rec in records.items():
            data=pz.read(name)
            if len(data)!=rec["bytes"] or h(data)!=rec["sha256"]:raise SystemExit("PAYLOAD_RECORD_MISMATCH:"+name)
        pm=json.loads(pz.read("PATCH_MANIFEST.json"))
        if h(pz.read("PATCH_MANIFEST.json"))!=auth.get("candidate_patch_manifest_file_sha256"):raise SystemExit("PATCH_MANIFEST_BINDING_MISMATCH")
        for op in pm["operations"]:
            p=x.activated_root/op["path"];before=p.read_bytes() if p.exists() else None
            if op["operation"]=="replace" and (before is None or h(before)!=op["before_sha256"]):raise SystemExit("PREIMAGE_MISMATCH:"+op["path"])
            if op["operation"]=="add" and p.exists():raise SystemExit("ADD_PATH_EXISTS:"+op["path"])
            data=pz.read("patch_after/"+op["path"])
            if h(data)!=op["after_sha256"]:raise SystemExit("AFTER_IMAGE_MISMATCH:"+op["path"])
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        transform_overlay(pz,x.activated_root,authsha)
    seal=reseal(x.activated_root,authsha)
    activated=file_snapshot(x.activated_root)
    report={"type":"PMP_P2C_DISPOSABLE_PROOF_PREPARATION_RESULT_001","status":"PASS","source_repository_commit":SOURCE_COMMIT,"baseline_file_count":len(baseline),"activated_file_count":len(activated),"authorization_receipt_sha256":authsha,"base_patch_operation_count":23,"closure_overlay_operation_count":11,"production_changed":False,"disposable_copy":str(x.activated_root),"a003":seal,"baseline_snapshot":baseline,"activated_snapshot":activated}
    x.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ["status","baseline_file_count","activated_file_count","authorization_receipt_sha256","base_patch_operation_count","closure_overlay_operation_count"]},indent=2))
if __name__=="__main__":main()
