#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, pathlib, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v",ROOT/"tools/verify_modern_pass3_hook_validation_unit1_v1.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
c=json.loads((ROOT/"audit/pass3/modern-hook-validation-unit1-v1.json").read_text())
def base():
 b=[{"body_id":x,"acceptance_state":"accepted","begin_marker_seen":True,"end_marker_seen":True,"raw_source_pointer":"ptr:"+x} for x in c["accepted_body_ids"]]
 s=[{"support_slot":x,"raw_source_pointer":"ptr:"+x} for x in c["support_slots"]]
 return b,[{"manifest_id":"MANIFEST-001"}],s,dict(c["claim_ceiling"])
def expect(name,mutator,should_pass=False):
 b,m,s,cl=base();mutator(b,m,s,cl);r=v.validate_dataset(c,b,m,s,cl)
 if r["pass"] is not should_pass: raise AssertionError(name+":"+json.dumps(r,sort_keys=True))
 return name
cases=[]
cases.append(expect("positive",lambda *x:None,True))
cases.append(expect("missing_body",lambda b,m,s,c:b.pop()))
cases.append(expect("duplicate_body",lambda b,m,s,c:b.append(dict(b[0]))))
cases.append(expect("missing_manifest",lambda b,m,s,c:m.clear()))
cases.append(expect("missing_support_slot",lambda b,m,s,c:s.pop()))
cases.append(expect("missing_raw_pointer",lambda b,m,s,c:b[0].pop("raw_source_pointer")))
cases.append(expect("missing_marker",lambda b,m,s,c:b[0].update(begin_marker_seen=False)))
cases.append(expect("overclaim",lambda b,m,s,c:c.update(real_app_proof=True)))
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/"a.json"
 v.main.__module__
import subprocess,sys
a=subprocess.check_output([sys.executable,str(ROOT/"tools/verify_modern_pass3_hook_validation_unit1_v1.py")],text=True)
b=subprocess.check_output([sys.executable,str(ROOT/"tools/verify_modern_pass3_hook_validation_unit1_v1.py")],text=True)
if a!=b: raise AssertionError("receipt_not_deterministic")
print(json.dumps({"status":"PASS","cases":cases,"deterministic_receipt":True},sort_keys=True))
