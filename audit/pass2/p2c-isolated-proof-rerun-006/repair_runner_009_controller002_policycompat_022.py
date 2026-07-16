#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, pathlib, sys

HERE=pathlib.Path(__file__).resolve().parent
ORIGINAL=HERE/'repair_runner_009_controller002.py'
spec=importlib.util.spec_from_file_location('repair009_controller002_original',ORIGINAL)
if spec is None or spec.loader is None: raise SystemExit('R009C002_POLICYCOMPAT_IMPORT_FAILED')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

RECORD6='pmp-pass75-reload-runtime-platform-gate-v1.js'
RECORD6_FROZEN_POLICY_SHA='3bd54e89efc2cadfb89c55cf4811c11e176dcd6c43d5402d62a0da832772acb5'
RECORD6_CURRENT_ORIGINAL_SHA='203e1d0096f517e66b06f0534d991ab54555f936a5d2be42d9e8b2fa57fd5042'

def update_policy_compat(bundle_root:pathlib.Path,manifest:dict)->None:
    policy_path=bundle_root/'policy-template.json'
    policy=json.loads(policy_path.read_text())
    by_path={a['path']:a for a in policy['actors']}
    compatibility_used=[]
    for row in manifest['records']:
        actor=by_path.get(row['path'])
        if actor is None: raise SystemExit('R009C002_POLICY_ACTOR_MISSING:'+row['path'])
        actual=actor['sha256'];expected=row['original_sha256']
        if actual!=expected:
            allowed=(row['path']==RECORD6 and actual==RECORD6_FROZEN_POLICY_SHA and expected==RECORD6_CURRENT_ORIGINAL_SHA)
            if not allowed: raise SystemExit('R009C002_POLICY_ORIGINAL_SHA_MISMATCH:'+row['path']+':'+actual+':'+expected)
            compatibility_used.append({'path':row['path'],'frozen_policy_sha256':actual,'current_original_sha256':expected})
        actor['sha256']=row['transformed_sha256']
        actor['source_identity']='REPAIR009_TYPESCRIPT_5_8_3_ES2016_NORMALIZED_DISPOSABLE_PROOF_CANDIDATE'
        actor['async_continuation_authority']='PROMISE_REACTION_CALLBACK_BOUND_TOKEN_VALIDATOR'
    policy['repair009_async_continuation_model']='TYPESCRIPT_5_8_3_ES2016_ASYNC_TO_GENERATOR_PROMISE_CONTINUATIONS'
    policy['repair009_normalized_actor_count']=len(manifest['records'])
    policy['repair009_policy_identity_compatibility']=compatibility_used
    policy_path.write_text(json.dumps(policy,indent=2,sort_keys=True)+'\n')

mod.update_policy=update_policy_compat
raise SystemExit(mod.main())
