#!/usr/bin/env python3
import copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/"audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json"
C=json.loads(P.read_text())
ACTORS=["Route Guardian","App Orchestrator","Mount Registry","Section Owners","Panel Modules","Helpers","Readiness Gate","Boot Status Strip","Bug Authority","Bug Watch","Bug Bank"]
FALSE=["active_chain_enforcement","real_app_proof","production_activation","later_pass_completion","formal_proof","current_clean","best_in_world"]
def check(c):
 g=[]
 if c.get("type")!="PMP_PASS2_FULL_ROADMAP_AUTHORITY_DEFINITION_CLOSURE_V1":g.append("type")
 if c.get("closure_scope")!="FULL_PLANNED_AUTHORITY_DEFINITION_SCOPE":g.append("scope")
 if c.get("pass2_complete_at_authority_definition_scope") is not True:g.append("completion")
 if "No actor may gain authority silently" not in c.get("global_rule",""):g.append("silent_authority")
 rows=c.get("actors",[])
 if [r.get("actor") for r in rows]!=ACTORS:g.append("actors")
 for r in rows:
  if not r.get("allowed"):g.append("allowed:"+str(r.get("actor")))
  if not r.get("forbidden"):g.append("forbidden:"+str(r.get("actor")))
  if not r.get("current_files"):g.append("files:"+str(r.get("actor")))
  if r.get("actor") not in {"Bug Authority","Bug Watch"} and not r.get("later_pass_dependency"):g.append("dependency:"+str(r.get("actor")))
 for k in FALSE:
  if c.get("claim_ceiling",{}).get(k) is not False:g.append("overclaim:"+k)
 if c.get("formal_proof")!={"count":1,"result":"FAIL","receipt082":"CONSUMED","new_run":False}:g.append("formal")
 p=c.get("pr122",{})
 if p.get("number")!=122 or p.get("state")!="OPEN" or p.get("merge_authorized") is not False or p.get("modified") is not False:g.append("pr122")
 if c.get("runtime_files_modified") is not False:g.append("runtime")
 if c.get("production_activation") is not False:g.append("activation")
 if len(c.get("changed_paths",[]))!=4:g.append("paths")
 return g
assert not check(C),check(C)
cases=[]
mutations=[
("missing_actor",lambda x:x["actors"].pop()),
("empty_allowed",lambda x:x["actors"][0].__setitem__("allowed",[])),
("empty_forbidden",lambda x:x["actors"][0].__setitem__("forbidden",[])),
("silent_gain",lambda x:x.__setitem__("global_rule","authority may expand")),
("later_pass_false_completion",lambda x:x["claim_ceiling"].__setitem__("later_pass_completion",True)),
("production",lambda x:x.__setitem__("production_activation",True)),
("formal_rerun",lambda x:x["formal_proof"].__setitem__("new_run",True)),
("pr122_merge",lambda x:x["pr122"].__setitem__("merge_authorized",True)),
("runtime_change",lambda x:x.__setitem__("runtime_files_modified",True)),
("real_app_overclaim",lambda x:x["claim_ceiling"].__setitem__("real_app_proof",True)),
("active_chain_overclaim",lambda x:x["claim_ceiling"].__setitem__("active_chain_enforcement",True)),
]
for n,f in mutations:
 x=copy.deepcopy(C);f(x);assert check(x),n;cases.append(n)
print(json.dumps({"type":"PMP_PASS2_FULL_ROADMAP_AUTHORITY_DEFINITION_CLOSURE_TEST_RECEIPT_V1","status":"PASS","positive":1,"negative_fail_closed":len(cases),"cases":cases,"deterministic":True},sort_keys=True))
