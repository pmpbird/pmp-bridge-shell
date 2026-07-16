#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def issue(q,order,label,path,expected,actual,command,line,dependency):
 q.append({'dependency_order':order,'label':label,'affected_file':str(path),'expected_anchor_or_condition':expected,'actual_match_count_or_value':actual,'exact_command':command,'controller_line':line,'dependency':dependency})

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle-root',type=pathlib.Path,required=True);ap.add_argument('--normalized-root',type=pathlib.Path,required=True);ap.add_argument('--manifest',type=pathlib.Path,required=True);ap.add_argument('--controller',type=pathlib.Path,required=True);ap.add_argument('--repo-root',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args()
 q=[]; checks=[]; manifest=json.loads(a.manifest.read_text());prepare=a.bundle_root/'prepare_disposable_proof_002.py';runner=a.bundle_root/'run_full_isolated_proof_002.py';policy_path=a.bundle_root/'policy-template.json';ps=prepare.read_text();rs=runner.read_text()
 anchors=[
 (1,'R009C002_GATE_PROPERTY_MAP',prepare,' g=g.replace("const tokenSet=new WeakSet();","const tokenSet=new WeakSet();\\nconst tokenValidators=new WeakMap();",1)',27),
 (2,'R009C002_GATE_AUTHORITY_FAILURE_SETTLEMENT_ANCHOR',prepare,' anchor="function wrapCallback(token,callback){return typeof callback===\'function\'?function(){return run(token,callback,this,Array.from(arguments))}:callback}\\n"',31),
 (3,'R009C002_GATE_AUTHORITY_FAILURE_SETTLEMENT_REPLACE',prepare,' g=g.replace(anchor,new_validator+anchor,1)',34),
 (4,'R009C002_PREPARE_GATE_EXTENSION',prepare," gate_path.write_text(g)\n return {'status':'APPLIED','authority_model':'CALLBACK_BOUND_TOKEN_VALIDATOR','global_ambient_authority':False,'lease_revalidated_on_callback':True,'ambient_depth_constant_zero':True}",38),
 (5,'R009C002_PREPARE_MAIN_ANCHOR',prepare,'def main():\n',86),
 (6,'R009C002_NORMALIZED_SOURCE_APPLICATION',prepare," for p in sorted((a.payload_root/'contracts').iterdir()):shutil.copy2(p,a.activated_root/p.name)\n # Proof-only repair: prefetch all source bytes before installing the gate; no production file is modified.",109),
 (7,'R009C002_PREPARE_OUTPUT',prepare,"'callback_bound_actor_lease_repair':callback_bound_actor_lease_repair,'production_changed':False",113),
 (8,'R009C002_A002_DETERMINISM_PATCH',runner,' s=s.replace(home_anchor,home_insert,1)\n a002.write_text(s)',121)]
 for order,label,path,anchor,line in anchors:
  count=(ps if path==prepare else rs).count(anchor);checks.append({'label':label,'affected_file':str(path),'expected_count':1,'actual_count':count,'pass':count==1})
  if count!=1: issue(q,order,label,path,'exactly one anchor match',count,'independent anchor census',line,'Repair 009 patch shape')
 policy=json.loads(policy_path.read_text());actors={x['path']:x for x in policy.get('actors',[])}
 for i,row in enumerate(manifest['records'],1):
  actor=actors.get(row['path'])
  if actor is None: issue(q,20+i,'R009C002_POLICY_ACTOR_MISSING',policy_path,row['path'],'missing','update_policy()',172,'policy actor inventory')
  elif actor.get('sha256')!=row['original_sha256']: issue(q,40+i,'R009C002_POLICY_ORIGINAL_SHA_MISMATCH',policy_path,row['original_sha256'],actor.get('sha256'),'update_policy()',174,'policy source identity')
  src=a.normalized_root/row['path'];actual='missing' if not src.is_file() else sha(src)
  if actual!=row['transformed_sha256']: issue(q,60+i,'R009C002_NORMALIZED_INPUT_INVALID',src,row['transformed_sha256'],actual,'copy_normalized_sources()',195,'normalized transformer output')
 controller_ran=False;crc=None;cout='';cerr=''
 if not q:
  cmd=[sys.executable,str(a.controller),'--bundle-root',str(a.bundle_root),'--normalized-root',str(a.normalized_root),'--normalization-manifest',str(a.manifest)];p=subprocess.run(cmd,text=True,capture_output=True);controller_ran=True;crc=p.returncode;cout=p.stdout;cerr=p.stderr
  if p.returncode!=0: issue(q,100,'R009C002_UNCLASSIFIED_CONTROLLER_FAILURE',a.controller,'exit_code=0',{'exit_code':p.returncode,'stderr':p.stderr[-4000:]},' '.join(cmd),'main','all independent prerequisites')
 comp=[]
 for path,kind in [(prepare,'python'),(a.bundle_root/'rollback_disposable_proof_002.py','python'),(runner,'python'),(a.bundle_root/'after/pmp-p2c-production-enforcement-adapter-candidate-001.js','node'),(a.bundle_root/'run_production_shaped_browser_proof_002.cjs','node')]:
  if not path.is_file(): comp.append({'path':str(path),'kind':kind,'status':'NOT_PRODUCED'});continue
  cmd=[sys.executable,'-m','py_compile',str(path)] if kind=='python' else ['node','--check',str(path)];p=subprocess.run(cmd,text=True,capture_output=True);comp.append({'path':str(path),'kind':kind,'status':'PASS' if p.returncode==0 else 'FAIL','stderr':p.stderr[-4000:]})
  if p.returncode: issue(q,200+len(q),'COMPILE_VALIDATION_FAILURE',path,'exit_code=0',{'exit_code':p.returncode,'stderr':p.stderr[-4000:]},' '.join(cmd),'compile validation','successfully produced output')
 superseded={'efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57':'old patcher','72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619':'old manifest','fb87f6dfc4a46cc07927b9ba78e1f8ac657eed2d16b4764b63f5ecb8c787e238':'intermediate manifest'};stale=[]
 for value,meaning in superseded.items():
  p=subprocess.run(['git','-C',str(a.repo_root),'grep','-n','-F',value,'--','.github/workflows','audit/pass2'],text=True,capture_output=True)
  for loc in p.stdout.splitlines(): stale.append({'superseded_value':value,'meaning':meaning,'location':loc})
 for i,row in enumerate(stale,1): issue(q,300+i,'STALE_CHECKSUM_BINDING',row['location'].split(':',1)[0],'current repaired binding or explicit historical receipt-only reference',row,'git grep stale checksum census','repository census','static reseal')
 q=sorted(q,key=lambda x:(x['dependency_order'],x['label']))
 out={'type':'PMP_PASS2_EXHAUSTIVE_PREPROOF_FAILURE_DISCOVERY_021','status':'PASS_NO_REMAINING_PREPROOF_FAILURES' if not q else 'COMPLETE_FAILURE_SET_COLLECTED','repair_queue_count':len(q),'repair_queue_dependency_ordered':q,'anchor_checks':checks,'controller_executed_diagnostic_mode':controller_ran,'controller_exit_code':crc,'controller_stdout':cout[-4000:],'controller_stderr':cerr[-4000:],'compile_results':comp,'stale_checksum_bindings':stale,'hard_stop':{'git_worktree_add_executed':False,'playwright_or_chromium_install_executed':False,'disposable_copy_preparation_executed':False,'browser_proof_executed':False,'proof_run_count_executed':0,'proof_authorized':False,'production_files_modified':False,'current_map_modified':False,'persisted_data_modified':False}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
