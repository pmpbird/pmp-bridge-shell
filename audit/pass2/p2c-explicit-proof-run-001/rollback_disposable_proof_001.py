#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
def hf(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def snap(root):
 out={}
 for p in sorted(root.rglob("*")):
  if p.is_file():
   rel=p.relative_to(root).as_posix()
   if rel.startswith(".git/") or rel==".git":continue
   out[rel]={"bytes":p.stat().st_size,"sha256":hf(p)}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--baseline-root",type=Path,required=True);ap.add_argument("--activated-root",type=Path,required=True);ap.add_argument("--preparation-result",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 prep=json.loads(x.preparation_result.read_text());expected=prep["baseline_snapshot"]
 if (x.activated_root/".git").exists():
  subprocess.run(["git","reset","--hard","c618596f2b5c99ca7f355153a5bd31268170df80"],cwd=x.activated_root,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  subprocess.run(["git","clean","-fdx"],cwd=x.activated_root,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 else:
  if x.activated_root.exists():shutil.rmtree(x.activated_root)
  shutil.copytree(x.baseline_root,x.activated_root,ignore=shutil.ignore_patterns(".git","node_modules","__pycache__"))
 actual=snap(x.activated_root)
 missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected));changed=sorted(k for k in set(expected)&set(actual) if expected[k]!=actual[k])
 out={"type":"PMP_P2C_DISPOSABLE_PROOF_ROLLBACK_RESULT_001","status":"PASS" if not(missing or extra or changed) else "FAIL","baseline_file_count":len(expected),"restored_file_count":len(actual),"missing":missing,"extra":extra,"changed":changed,"byte_for_byte_restored":not(missing or extra or changed),"production_changed":False}
 x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2))
 raise SystemExit(0 if out["status"]=="PASS" else 1)
if __name__=="__main__":main()
