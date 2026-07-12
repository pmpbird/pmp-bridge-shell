#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,time,signal
from pathlib import Path
def run(name,cmd,cwd,env,out_json=None):
 p=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 log=Path(env["EVIDENCE_DIR"])/(name+".log");log.write_text(p.stdout)
 result=None
 if out_json and Path(out_json).is_file():
  try: result=json.loads(Path(out_json).read_text())
  except Exception as e: result={"parse_error":str(e)}
 return {"name":name,"returncode":p.returncode,"result":result,"log":str(log)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--activated-root",type=Path,required=True);ap.add_argument("--baseline-root",type=Path,required=True);ap.add_argument("--preparation-result",type=Path,required=True);ap.add_argument("--rollback-script",type=Path,required=True);ap.add_argument("--browser-script",type=Path,required=True);ap.add_argument("--evidence-dir",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);x=ap.parse_args()
 x.evidence_dir.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env["EVIDENCE_DIR"]=str(x.evidence_dir);env["NODE_PATH"]=env.get("NODE_PATH","")
 server=subprocess.Popen(["python3","-m","http.server","8765","--bind","127.0.0.1"],cwd=x.activated_root,stdout=(x.evidence_dir/"http.log").open("w"),stderr=subprocess.STDOUT)
 try:
  for _ in range(60):
   q=subprocess.run(["curl","-fsS","http://127.0.0.1:8765/pmp-current-map-v12.json"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   if q.returncode==0:break
   time.sleep(.5)
  steps=[]
  br=x.evidence_dir/"browser.json";e=env.copy();e["P2C_PROOF_BASE_URL"]="http://127.0.0.1:8765/";e["P2C_PROOF_BROWSER_RESULT"]=str(br)
  steps.append(run("production-shaped-browser",["node",str(x.browser_script)],x.activated_root,e,br))
  a3r=x.evidence_dir/"a003-repository.json";steps.append(run("a003-repository",["python3","tools/test_a003_integrity.py","--output",str(a3r)],x.activated_root,env,a3r))
  a3l=x.evidence_dir/"a003-live.json";e=env.copy();e["A003_RESULT_PATH"]=str(a3l);steps.append(run("a003-live",["python3","tools/run_a003_live_final.py"],x.activated_root,e,a3l))
  a2=x.evidence_dir/"a002-live.json";e=env.copy();e["A002_BASE_URL"]="http://127.0.0.1:8765/";e["A002_RESULT_PATH"]=str(a2);steps.append(run("a002-live",["node","audit/a002-live-runtime.cjs"],x.activated_root,e,a2))
 finally:
  server.terminate()
  try:server.wait(timeout=5)
  except:server.kill()
 rb=x.evidence_dir/"rollback.json";steps.append(run("rollback",["python3",str(x.rollback_script),"--baseline-root",str(x.baseline_root),"--activated-root",str(x.activated_root),"--preparation-result",str(x.preparation_result),"--output",str(rb)],x.baseline_root,env,rb))
 def ok(s):
  if s["returncode"]!=0:return False
  r=s.get("result") or {}
  if s["name"]=="production-shaped-browser":return r.get("status")=="PASS" and r.get("tests_failed")==0
  if s["name"]=="a003-repository":return r.get("tests_passed")==21 and r.get("tests_failed")==0
  if s["name"]=="a003-live":return r.get("tests_passed")==47 and r.get("tests_failed")==0
  if s["name"]=="a002-live":return r.get("tests_passed")==41 and r.get("tests_failed")==0
  if s["name"]=="rollback":return r.get("status")=="PASS" and r.get("byte_for_byte_restored") is True
  return False
 status="PASS" if all(ok(s) for s in steps) else "FAIL"
 out={"type":"PMP_P2C_EXPLICIT_PRODUCTION_SHAPED_PROOF_RUN_RESULT_001","status":status,"steps":steps,"production_changed":False,"production_patch_applied":False,"active_chain_integration":False,"disposable_copy_activated":True,"rollback_completed":bool(steps[-1].get("result",{}).get("byte_for_byte_restored"))}
 x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"steps":[{"name":s["name"],"returncode":s["returncode"],"summary":s.get("result") and {k:s["result"].get(k) for k in ["status","tests_total","tests_passed","tests_failed","byte_for_byte_restored"]}} for s in steps]},indent=2));raise SystemExit(0 if status=="PASS" else 1)
if __name__=="__main__":main()
