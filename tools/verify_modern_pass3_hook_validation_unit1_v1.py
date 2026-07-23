#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH=ROOT/"audit/pass3/modern-hook-validation-unit1-v1.json"
EXACT_PATHS={
 ".github/workflows/modern-pass3-hook-validation-unit1-v1.yml",
 "audit/pass3/modern-hook-validation-unit1-v1.json",
 "tools/test_modern_pass3_hook_validation_unit1_v1.py",
 "tools/verify_modern_pass3_hook_validation_unit1_v1.py",
}
FORBIDDEN_PREFIXES=("pmp-current-map","pmp-safe-writer")
FORBIDDEN_EXACT={
 "pmp-pass3-route-handoff-freeze-v1.json",
 "pmp-phase3-hook-readiness-v1.js",
 "pmp-phase3-hook-validation-execution-v1.js",
}
def sha256(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def git_blob(p:pathlib.Path)->str:
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def fail(code,detail): raise SystemExit(code+":"+json.dumps(detail,sort_keys=True))
def validate_dataset(c,bodies,manifest,support,claims):
 expected=c["accepted_body_ids"]; slots=c["support_slots"]
 ids=[x.get("body_id") for x in bodies]; ss=[x.get("support_slot") for x in support]
 duplicates=sorted({x for x in ids if ids.count(x)>1 and x})
 slot_dups=sorted({x for x in ss if ss.count(x)>1 and x})
 missing=[x for x in expected if x not in ids]
 missing_slots=[x for x in slots if x not in ss]
 markers=all(x.get("begin_marker_seen") is True and x.get("end_marker_seen") is True for x in bodies)
 body_ptrs=all(bool(x.get("raw_source_pointer") or x.get("raw_source_inline") or x.get("raw_source_length",0)>0) for x in bodies)
 support_ptrs=all(bool(x.get("raw_source_pointer") or x.get("raw_source_inline") or x.get("raw_source_length",0)>0) for x in support)
 ceiling_ok=all(claims.get(k) is v for k,v in c["claim_ceiling"].items())
 checks={
  "hook_ids":c["hooks"]==[f"HOOK-{i:03d}" for i in range(1,7)],
  "body_count":len(bodies)==22,
  "missing_bodies":not missing,
  "duplicate_bodies":not duplicates,
  "manifest_count":len(manifest)==1,
  "support_count":len(support)==12,
  "missing_support_slots":not missing_slots,
  "duplicate_support_slots":not slot_dups,
  "markers_complete":markers,
  "body_raw_pointers":body_ptrs,
  "support_raw_pointers":support_ptrs,
  "claim_ceiling":ceiling_ok,
 }
 return {"pass":all(checks.values()),"checks":checks,"missing_bodies":missing,"duplicate_bodies":duplicates,"missing_support_slots":missing_slots,"duplicate_support_slots":slot_dups}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--base-sha");ap.add_argument("--head-sha");ap.add_argument("--output",type=pathlib.Path);a=ap.parse_args()
 c=json.loads(CONTRACT_PATH.read_text())
 if c["modern_pass3_name"]!="Modern Pass 3 — Hook Validation and Fail-Closed Readiness": fail("NAMESPACE_MISMATCH",{})
 for row in [c["historical_pass3"]["identity"],*c["runtime_sources"]]:
  p=ROOT/row["path"]
  if not p.is_file() or len(p.read_bytes())!=row["bytes"] or sha256(p)!=row["sha256"] or git_blob(p)!=row["git_blob_sha"]: fail("PRESERVATION_IDENTITY_MISMATCH",row)
 if a.base_sha and a.head_sha:
  changed=set(filter(None,subprocess.check_output(["git","diff","--name-only",a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()))
  if changed!=EXACT_PATHS: fail("EXACT_SCOPE_MISMATCH",{"missing":sorted(EXACT_PATHS-changed),"extra":sorted(changed-EXACT_PATHS)})
  if changed & FORBIDDEN_EXACT or any(p.startswith(FORBIDDEN_PREFIXES) for p in changed): fail("FORBIDDEN_PATH_CHANGE",sorted(changed))
 bodies=[{"body_id":x,"acceptance_state":"accepted","begin_marker_seen":True,"end_marker_seen":True,"raw_source_pointer":"sha256:"+x} for x in c["accepted_body_ids"]]
 support=[{"support_slot":x,"raw_source_pointer":"sha256:"+x} for x in c["support_slots"]]
 result=validate_dataset(c,bodies,[{"manifest_id":"MANIFEST-001"}],support,dict(c["claim_ceiling"]))
 if not result["pass"]: fail("POSITIVE_FIXTURE_FAILED",result)
 out={"type":"PMP_MODERN_PASS3_HOOK_VALIDATION_UNIT1_RECEIPT_V1","status":"PASS","deterministic":True,"modern_pass3":c["modern_pass3_name"],"hooks":c["hooks"],"positive":result,"claim_ceiling":c["claim_ceiling"],"historical_pass3_preserved":True,"runtime_sources_preserved":True,"real_app_proof":False}
 text=json.dumps(out,indent=2,sort_keys=True)+"\n"
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
 print(text,end="")
 return 0
if __name__=="__main__":raise SystemExit(main())
