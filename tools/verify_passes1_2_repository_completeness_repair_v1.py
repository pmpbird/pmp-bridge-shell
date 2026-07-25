#!/usr/bin/env python3
import argparse,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED={'.github/workflows/passes1-2-repository-completeness-repair-v1.yml','audit/pass1/pass1-post-merge-confirmation-v1.json','audit/passes1-2/canonical-authority-index-v1.json','audit/pass2/pass2-scope-precedence-crosswalk-v1.json','tools/test_passes1_2_repository_completeness_repair_v1.py','tools/verify_passes1_2_repository_completeness_repair_v1.py'}
def fail(code,data): raise SystemExit(code+':'+json.dumps(data,sort_keys=True))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-sha',required=True);ap.add_argument('--head-sha',required=True);ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args()
 changed=set(filter(None,subprocess.check_output(['git','diff','--name-only',a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()))
 if changed!=EXPECTED: fail('EXACT_SCOPE_MISMATCH',{'missing':sorted(EXPECTED-changed),'extra':sorted(changed-EXPECTED)})
 status=subprocess.check_output(['git','diff','--name-status',a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()
 if any(not row.startswith('A\t') for row in status): fail('NON_ADDITIVE_CHANGE',status)
 subprocess.check_call(['python3','tools/test_passes1_2_repository_completeness_repair_v1.py'],cwd=ROOT)
 receipt={'type':'PMP_PASSES1_2_REPOSITORY_COMPLETENESS_REPAIR_VERIFICATION_V1','status':'PASS','base_sha':a.base_sha,'head_sha':a.head_sha,'changed_paths':sorted(changed),'exact_scope':True,'additive_only':True,'runtime_files_modified':False,'persisted_data_modified':False,'pr122_modified':False,'pr122_merge_authorized':False,'pass3_started':False}
 if a.output:a.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
