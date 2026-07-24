#!/usr/bin/env python3
import argparse,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json").read_text())
def fail(code,data):raise SystemExit(code+":"+json.dumps(data,sort_keys=True))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--base-sha",required=True);ap.add_argument("--head-sha",required=True)
 ap.add_argument("--verify-base-identities",action="store_true");ap.add_argument("--output",type=pathlib.Path)
 a=ap.parse_args()
 expected=set(C["changed_paths"])
 changed=set(filter(None,subprocess.check_output(["git","diff","--name-only",a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()))
 if changed!=expected:fail("EXACT_SCOPE_MISMATCH",{"missing":sorted(expected-changed),"extra":sorted(changed-expected)})
 status=subprocess.check_output(["git","diff","--name-status",a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()
 if any(not x.startswith("A\t") for x in status):fail("NON_ADDITION_CHANGE",status)
 if a.verify_base_identities:
  for row in C["protected_files"]:
   if not re.fullmatch(r"[0-9a-f]{40}",row["git_blob_sha"]):fail("BAD_EXPECTED_IDENTITY",row)
   got=subprocess.check_output(["git","rev-parse",f"{a.base_sha}:{row['path']}"],cwd=ROOT,text=True).strip()
   if got!=row["git_blob_sha"]:fail("BASE_IDENTITY_MISMATCH",{"path":row["path"],"expected":row["git_blob_sha"],"actual":got})
 if any(C["claim_ceiling"].get(k) is not False for k in ["active_chain_enforcement","real_app_proof","production_activation","later_pass_completion","formal_proof","current_clean","best_in_world"]):fail("CLAIM_CEILING",C["claim_ceiling"])
 if C["formal_proof"]!={"count":1,"result":"FAIL","receipt082":"CONSUMED","new_run":False}:fail("FORMAL_PROOF_BOUNDARY",C["formal_proof"])
 if C["pr122"]["merge_authorized"] is not False or C["pr122"]["modified"] is not False:fail("PR122_BOUNDARY",C["pr122"])
 out={"type":"PMP_PASS2_FULL_ROADMAP_AUTHORITY_DEFINITION_CLOSURE_VERIFICATION_V1","status":"PASS","exact_scope":True,"existing_files_modified":False,"base_identities_checked":a.verify_base_identities,"claim_ceiling_preserved":True,"formal_proof_count":1,"formal_proof_result":"FAIL","production_activation":False,"deterministic":True}
 text=json.dumps(out,indent=2,sort_keys=True)+"\n"
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
 print(text,end="")
if __name__=="__main__":main()
