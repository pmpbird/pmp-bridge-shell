#!/usr/bin/env bash
set -euo pipefail

set -euo pipefail
python3 - <<'PY'
import json,os,pathlib
e=pathlib.Path(os.environ['EVIDENCE_DIR'])
aggregate=None
try:aggregate=json.loads((e/'aggregate.json').read_text())
except Exception as exc:(e/'aggregate-read-error.txt').write_text(repr(exc)+'\n')
proof_started=(e/'proof-run-started.lock').is_file()
proof_run_count=1 if proof_started else 0
semantic=False
if proof_started and aggregate:
    semantic=bool(
      aggregate.get('status')=='PASS' and
      aggregate.get('production_patch_applied') is False and
      aggregate.get('active_chain_integrated_in_production') is False and
      aggregate.get('proof_scope')=='DISPOSABLE_COPY_ONLY' and
      aggregate.get('browser',{}).get('tests_failed')==0 and
      aggregate.get('a002_active',{}).get('tests_passed')==41 and aggregate.get('a002_active',{}).get('tests_failed')==0 and not aggregate.get('a002_active',{}).get('fatal_error') and
      aggregate.get('a003_repository_active',{}).get('tests_passed')==21 and aggregate.get('a003_repository_active',{}).get('tests_failed')==0 and
      aggregate.get('a003_live_active',{}).get('tests_passed')==47 and aggregate.get('a003_live_active',{}).get('tests_failed')==0 and
      aggregate.get('rollback',{}).get('byte_for_byte_restored') is True and
      aggregate.get('a002_restored',{}).get('tests_passed')==41 and aggregate.get('a002_restored',{}).get('tests_failed')==0 and not aggregate.get('a002_restored',{}).get('fatal_error') and
      aggregate.get('a003_repository_restored',{}).get('tests_passed')==21 and aggregate.get('a003_repository_restored',{}).get('tests_failed')==0 and
      aggregate.get('a003_live_restored',{}).get('tests_passed')==47 and aggregate.get('a003_live_restored',{}).get('tests_failed')==0
    )
(e/'semantic-review-008.json').write_text(json.dumps({'status':'PASS' if semantic else 'FAIL','aggregate_present':aggregate is not None,'proof_started':proof_started,'proof_run_count_executed':proof_run_count,'workflow_attempt_completed':True,'second_proof_run_authorized':False},indent=2,sort_keys=True)+'\n')
PY
rm -f "$ACTIVE_ROOT/a003-live-runtime-effective.cjs"
git -C "$ACTIVE_ROOT" reset --hard "$SOURCE_COMMIT" >/dev/null
git -C "$ACTIVE_ROOT" clean -ffdx >/dev/null
test -z "$(git -C "$ACTIVE_ROOT" status --porcelain)"
test "$(git -C "$ACTIVE_ROOT" rev-parse HEAD)" = "$SOURCE_COMMIT"
python3 - <<'PY'
import hashlib,json,os,pathlib
def snap(root):
    out={}
    for p in sorted(pathlib.Path(root).rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix()
        if rel=='.git' or rel.startswith('.git/'):continue
        out[rel]=(p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
    return out
e=pathlib.Path(os.environ['EVIDENCE_DIR'])
review=json.loads((e/'semantic-review-008.json').read_text())
proof_started=(e/'proof-run-started.lock').is_file()
proof_run_count=1 if proof_started else 0
b=snap(os.environ['BASELINE_ROOT']);r=snap(os.environ['ACTIVE_ROOT'])
boundary_ok=b==r and len(r)==1481
out={'type':'PMP_P2C_ISOLATED_PROOF_RERUN008_FINAL_BOUNDARY_011','status':'PASS' if boundary_ok else 'FAIL','baseline_file_count':len(b),'restored_file_count':len(r),'byte_for_byte_restored_after_regressions':b==r,'production_checkout_dirty':False,'production_patch_applied':False,'production_activation_authorized':False,'merge_authorized':False,'proof_started':proof_started,'proof_run_count_executed':proof_run_count,'workflow_attempt_completed':True,'second_proof_run_authorized':False}
(e/'final-boundary.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2))
if review['status']!='PASS' or out['status']!='PASS':raise SystemExit(1)
PY
test -z "$(git status --porcelain)"
