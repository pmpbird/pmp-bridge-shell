#!/usr/bin/env python3
import argparse,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'audit/pass3/modern-pass3-exercised-scope-closure-v1.json').read_text())
def fail(c,d):raise SystemExit(c+':'+json.dumps(d,sort_keys=True))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-sha',required=True);ap.add_argument('--head-sha',required=True);ap.add_argument('--verify-base-identities',action='store_true');ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args()
 rows=C['unit1_files']+C['unit2_files']+C['protected_files']
 for row in rows:
  if not re.fullmatch(r'[0-9a-f]{40}',row['git_blob_sha']):fail('BAD_EXPECTED_IDENTITY',row)
 if a.verify_base_identities:
  for row in rows:
   got=subprocess.check_output(['git','rev-parse',f"{a.base_sha}:{row['path']}"],cwd=ROOT,text=True).strip()
   if got!=row['git_blob_sha']:fail('BASE_IDENTITY_MISMATCH',{'path':row['path'],'expected':row['git_blob_sha'],'actual':got})
 changed=set(filter(None,subprocess.check_output(['git','diff','--name-only',a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()))
 expected=set(C['changed_paths'])
 if changed!=expected:fail('EXACT_SCOPE_MISMATCH',{'missing':sorted(expected-changed),'extra':sorted(changed-expected)})
 status=subprocess.check_output(['git','diff','--name-status',a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()
 if any(not x.startswith('A\t') for x in status):fail('NON_ADDITION_CHANGE',status)
 false=['real_app_proof','production_activation','current_clean','frozen','full_transfer_proof','full_history_lossless','best_in_world']
 if any(C['claim_ceiling'].get(k) is not False for k in false):fail('CLAIM_CEILING',C['claim_ceiling'])
 out={'type':'PMP_MODERN_PASS3_EXERCISED_SCOPE_CLOSURE_VERIFICATION_V1','status':'PASS','exact_scope':True,'existing_files_modified':False,'base_identities_checked':a.verify_base_identities,'claim_ceiling_preserved':True,'formal_proof_count':1,'formal_proof_result':'FAIL','production_activation':False,'deterministic':True}
 text=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
 print(text,end='')
if __name__=='__main__':main()
