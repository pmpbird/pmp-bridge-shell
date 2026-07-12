#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ACTORS=[
 ('audit/pass2/fixtures/p2b-known-storage-actor.js','fixture_storage','fixture-owner','fixture',['storage_write']),
 ('audit/pass2/fixtures/p2b-known-dom-actor.js','fixture_dom','fixture-owner','fixture',['dom_write']),
 ('audit/pass2/fixtures/p2b-known-limited-actor.js','fixture_limited','fixture-owner','fixture',[]),
 ('audit/pass2/fixtures/p2b-known-async-actor.js','fixture_async','fixture-owner','fixture',['timer_schedule','storage_write']),
]
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'));ap.add_argument('--output',type=Path,default=Path('pmp-actor-authority-policy-v1.json'));a=ap.parse_args()
 actors=[]
 for path,role,owner,phase,caps in ACTORS:
  data=(a.root/path).read_bytes();actors.append({'path':path,'sha256':sha(data),'role':role,'owner':owner,'phase':phase,'stop_condition':'bounded_fixture','capabilities':caps})
 policy={'type':'PMP_ACTOR_AUTHORITY_POLICY_V1','version':'1.0.0-pass2-p2b-fixture-policy','algorithm':'SHA-256','status':'P2B_CERTIFICATION_POLICY_NOT_ACTIVE_CHAIN','unknown_actor_policy':'BLOCK_BEFORE_SIDE_EFFECT','unauthorized_capability_policy':'BLOCK_BEFORE_SIDE_EFFECT','protected_capabilities':['storage_write','storage_delete','storage_clear','dom_write','dom_delete','script_injection','resource_target_change','document_write','navigation','network_fetch','indexeddb_open','indexeddb_delete','cache_open','cache_delete','timer_schedule','event_listener'],'actors':actors,'truth_boundary':'This P2-B policy certifies the gate engine and adversarial fixtures. Active-chain actor policy and integration remain a later Pass 2 phase.','pass2_complete':False,'pass3_started':False}
 a.output.write_text(json.dumps(policy,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','actors':len(actors),'output':str(a.output)},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
