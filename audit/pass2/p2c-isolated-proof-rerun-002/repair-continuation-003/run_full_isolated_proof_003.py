#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys,time
from pathlib import Path
SOURCE='c618596f2b5c99ca7f355153a5bd31268170df80'

def text(v):
 if isinstance(v,bytes):return v.decode('utf-8','replace')
 return v or ''

def run(name,cmd,cwd,env,out,timeout):
 st=time.monotonic();print(json.dumps({'event':'START','lane':name}),flush=True)
 try:
  p=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
  r={'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'elapsed_seconds':round(time.monotonic()-st,3),'stdout':text(p.stdout),'stderr':text(p.stderr)}
 except subprocess.TimeoutExpired as e:
  r={'name':name,'status':'FAIL_TIMEOUT','returncode':None,'elapsed_seconds':round(time.monotonic()-st,3),'stdout':text(e.stdout),'stderr':text(e.stderr)}
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'event':'END','lane':name,'status':r['status'],'elapsed_seconds':r['elapsed_seconds']}),flush=True);return r

def run_a002(name,root,port,result_path,command_path,env):
 server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,text=True)
 try:
  time.sleep(1)
  e=dict(env);e['A002_BASE_URL']=f'http://127.0.0.1:{port}/';e['A002_RESULT_PATH']=str(result_path)
  return run(name,['node','audit/a002-live-runtime.cjs'],root,e,command_path,360)
 finally:
  server.terminate()
  try:server.wait(timeout=10)
  except subprocess.TimeoutExpired:
   server.kill();server.wait(timeout=10)

def read_json(p):
 try:return json.loads(p.read_text())
 except Exception:return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--activated-root',type=Path,required=True);ap.add_argument('--baseline-root',type=Path,required=True);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--scripts-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[]
 try:
  results.append(run('production-shaped-browser-active',['node',str(a.scripts_root/'run_production_shaped_browser_proof_002.cjs'),str(a.activated_root),str(a.evidence_dir/'browser-active.json')],a.activated_root,env,a.evidence_dir/'browser-active-command.json',240))
  results.append(run('a003-repository-active-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-active.json')],a.activated_root,env,a.evidence_dir/'a003-repository-active-command.json',180))
  results.append(run_a002('a002-active-41',a.activated_root,8000,a.evidence_dir/'a002-active.json',a.evidence_dir/'a002-active-command.json',env))
  e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-active.json')
  results.append(run('a003-live-active-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-active-command.json',480))
 finally:
  results.append(run('byte-for-byte-rollback',[sys.executable,str(a.scripts_root/'rollback_disposable_proof_002.py'),'--activated-root',str(a.activated_root),'--baseline-root',str(a.baseline_root),'--source-commit',SOURCE,'--output',str(a.evidence_dir/'rollback.json')],a.activated_root,env,a.evidence_dir/'rollback-command.json',180))
 # Mandatory restored-copy regressions after rollback.
 results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180))
 results.append(run_a002('a002-restored-41',a.activated_root,8001,a.evidence_dir/'a002-restored.json',a.evidence_dir/'a002-restored-command.json',env))
 e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-restored.json')
 results.append(run('a003-live-restored-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-restored-command.json',480))
 browser=read_json(a.evidence_dir/'browser-active.json');a3ra=read_json(a.evidence_dir/'a003-repository-active.json');a2a=read_json(a.evidence_dir/'a002-active.json');a3la=read_json(a.evidence_dir/'a003-live-active.json');rb=read_json(a.evidence_dir/'rollback.json');a3rr=read_json(a.evidence_dir/'a003-repository-restored.json');a2r=read_json(a.evidence_dir/'a002-restored.json');a3lr=read_json(a.evidence_dir/'a003-live-restored.json')
 semantic=bool(browser and browser.get('tests_failed')==0 and a3ra and a3ra.get('tests_passed')==21 and a3ra.get('tests_failed')==0 and a2a and a2a.get('tests_passed')==41 and a2a.get('tests_failed')==0 and a3la and a3la.get('tests_passed')==47 and a3la.get('tests_failed')==0 and rb and rb.get('byte_for_byte_restored') is True and a3rr and a3rr.get('tests_passed')==21 and a3rr.get('tests_failed')==0 and a2r and a2r.get('tests_passed')==41 and a2r.get('tests_failed')==0 and a3lr and a3lr.get('tests_passed')==47 and a3lr.get('tests_failed')==0)
 out={'type':'PMP_P2C_EXPLICIT_ISOLATED_PROOF_RERUN_AGGREGATE_003','status':'PASS' if semantic and all(x['status']=='PASS' for x in results) else 'FAIL','source_repository_commit':SOURCE,'repair_continuation':'A003_ROOT_RECEIPT_AUTHORITY_AND_TIMEOUT_SERIALIZER_003','lanes':[{k:v for k,v in x.items() if k not in ('stdout','stderr')} for x in results],'browser':browser,'a003_repository_active':a3ra,'a002_active':a2a,'a003_live_active':a3la,'rollback':rb,'a003_repository_restored':a3rr,'a002_restored':a2r,'a003_live_restored':a3lr,'production_patch_applied':False,'active_chain_integrated_in_production':False,'proof_scope':'DISPOSABLE_COPY_ONLY','pass2_complete':False,'pass3_started':False}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'lanes':out['lanes'],'production_patch_applied':False},indent=2));return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
