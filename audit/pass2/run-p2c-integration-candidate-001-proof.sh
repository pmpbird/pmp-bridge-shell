#!/usr/bin/env bash
set -euo pipefail

export BASE_MAIN_COMMIT="c618596f2b5c99ca7f355153a5bd31268170df80"
export CANDIDATE_DIR="/tmp/p2c-integration-candidate-001"

git merge-base --is-ancestor "$BASE_MAIN_COMMIT" HEAD
python3 - <<'PY'
import json,os,pathlib,subprocess
changed=set(subprocess.check_output(['git','diff','--name-only',os.environ['BASE_MAIN_COMMIT'],'HEAD'],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-integration-candidate-001-proof.yml','audit/pass2/p2c-integration-candidate-001-scope-lock.json','audit/pass2/p2c-integration-candidate-001-status.md','audit/pass2/run-p2c-integration-candidate-001-proof.sh'}
extras={p for p in changed if p not in allowed and not p.startswith('audit/pass2/p2c-integration-candidate-001-generator/')}
assert not extras,sorted(extras)
scope=json.loads(pathlib.Path('audit/pass2/p2c-integration-candidate-001-scope-lock.json').read_text())
assert scope['production_runtime_files_changed'] is False and scope['active_chain_integration'] is False
pathlib.Path('/tmp/p2c-scope-result.json').write_text(json.dumps({'status':'PASS','changed_paths':sorted(changed),'active_chain_integrated':False,'pass2_complete':False,'pass3_started':False},indent=2)+'\n')
PY

python3 - <<'PY'
import gzip,hashlib,json,pathlib,traceback
source=pathlib.Path('audit/pass2/p2c-integration-candidate-001-generator/generator.py.gz')
expected_compressed='96255ab71825abc0894f741322235623848bb1339c50c31cdf010d62077a9aa0'
expected_source='ed55dadfbcff934b3d63d179b26d6a60bd91bf83cf1a3b16952ebf05c2b980cc'
result={'status':'FAIL','source_exists':source.is_file(),'expected_compressed_sha256':expected_compressed,'expected_source_sha256':expected_source}
try:
    compressed=source.read_bytes(); compressed_sha=hashlib.sha256(compressed).hexdigest()
    result.update({'compressed_bytes':len(compressed),'compressed_sha256':compressed_sha})
    assert compressed_sha==expected_compressed
    raw=gzip.decompress(compressed); source_sha=hashlib.sha256(raw).hexdigest()
    result.update({'decoded_bytes':len(raw),'source_sha256':source_sha})
    assert source_sha==expected_source
    pathlib.Path('/tmp/build_p2c_integration_candidate_001.py').write_bytes(raw)
    result['status']='PASS'
except Exception as exc:
    result.update({'exception_type':type(exc).__name__,'exception':str(exc),'traceback':traceback.format_exc()})
pathlib.Path('/tmp/p2c-generator-decode-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert result['status']=='PASS',result
PY

rm -rf "$CANDIDATE_DIR"
python3 /tmp/build_p2c_integration_candidate_001.py --repo . --output-dir "$CANDIDATE_DIR" 2>&1 | tee /tmp/p2c-candidate-build-console.log

npm install --no-save playwright@1.55.0
npx playwright install --with-deps chromium
NODE_PATH="$GITHUB_WORKSPACE/node_modules" P2C_PORT=8765 node "$CANDIDATE_DIR/run-p2c-production-shaped-browser-integration-candidate-001.cjs" "$CANDIDATE_DIR" /tmp/p2c-production-shaped-browser-result.json 2>&1 | tee /tmp/p2c-production-shaped-browser-console.log
python3 - <<'PY'
import json,pathlib
r=json.loads(pathlib.Path('/tmp/p2c-production-shaped-browser-result.json').read_text())
assert r['status']=='PASS' and r['tests_failed']==0 and r['tests_passed']==r['tests_total']
assert r['order_ok'] is True and r['allowed_helper_requests']==1 and r['evil_requests']==0
assert r['production_sentinel']=='unchanged' and r['active_chain_integrated'] is False
assert set(r['realm_orders'])=={'root','guardian','reload-owner','inner-v30','inner-v23'}
PY

python3 tools/test_a003_integrity.py --output /tmp/p2c-a003-repository.json 2>&1 | tee /tmp/p2c-a003-repository-console.log
A003_RESULT_PATH=/tmp/p2c-a003-live.json python3 tools/run_a003_live_final.py 2>&1 | tee /tmp/p2c-a003-live-console.log
python3 -m http.server 8000 --bind 127.0.0.1 > /tmp/p2c-a002-http.log 2>&1 &
for i in $(seq 1 30); do curl -fsS http://127.0.0.1:8000/pmp-current-map-v12.json >/dev/null && break; sleep 1; done
A002_BASE_URL=http://127.0.0.1:8000/ A002_RESULT_PATH=/tmp/p2c-a002-live.json NODE_PATH="$GITHUB_WORKSPACE/node_modules" node audit/a002-live-runtime.cjs 2>&1 | tee /tmp/p2c-a002-live-console.log

python3 - <<'PY'
import json,pathlib
def rd(p): return json.loads(pathlib.Path(p).read_text())
b=rd('/tmp/p2c-production-shaped-browser-result.json'); a2=rd('/tmp/p2c-a002-live.json'); a3r=rd('/tmp/p2c-a003-repository.json'); a3l=rd('/tmp/p2c-a003-live.json')
assert (a2['tests_total'],a2['tests_passed'],a2['tests_failed'])==(41,41,0) and a2.get('fatal_error') is None
assert (a3r['tests_total'],a3r['tests_passed'],a3r['tests_failed'])==(21,21,0)
assert (a3l['tests_total'],a3l['tests_passed'],a3l['tests_failed'])==(47,47,0) and a3l.get('fatal_error') is None
out={'type':'PMP_APP_ORCHESTRATOR_PASS2_P2C_PRODUCTION_INTEGRATION_PATCH_CANDIDATE_001_AGGREGATE','status':'PASS_INACTIVE_CANDIDATE_READY_FOR_ENFORCEMENT_REVIEW','overall_project_pass':'Pass 2','phase':'P2-C','source_repository_commit':'c618596f2b5c99ca7f355153a5bd31268170df80','production_shaped_browser':b,'a002_live':a2,'a003_repository':a3r,'a003_adversarial_live':a3l,'production_files_changed':False,'active_chain_integrated':False,'pass2_complete':False,'pass3_started':False,'activation_decision':'NO_ACTIVATION_CANDIDATE_ONLY','remaining_to_finish_pass2':'one enforcement and closure phase','numbered_passes_after_pass2':6,'exact_next_move':'Build and independently review the inactive P2-C enforcement patch and rollback-ready closure gate; activate nothing without explicit authorization.'}
pathlib.Path('/tmp/p2c-integration-candidate-aggregate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'browser':f"{b['tests_passed']}/{b['tests_total']}",'a002':f"{a2['tests_passed']}/{a2['tests_total']}",'a003_repository':f"{a3r['tests_passed']}/{a3r['tests_total']}",'a003_live':f"{a3l['tests_passed']}/{a3l['tests_total']}"},indent=2))
PY
