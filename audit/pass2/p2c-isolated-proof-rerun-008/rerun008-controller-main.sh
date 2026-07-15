#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; printf "RECEIPT010_COMMAND_FAILURE line=%s rc=%s command=%q\n" "$LINENO" "$rc" "$BASH_COMMAND" >&2; exit "$rc"' ERR

echo "=== Verify one-run authorization and audit-only scope ==="
set -euo pipefail
test "$EVENT_ACTION" = "opened"
test "$RUN_ATTEMPT" = "1"
test "$(git rev-parse HEAD)" = "$HEAD_SHA"
git cat-file -e "$SOURCE_COMMIT^{commit}"
git merge-base --is-ancestor "$SOURCE_COMMIT" HEAD
test ! -e .github/workflows/pass2-p2c-isolated-proof-rerun-002.yml
test ! -e .github/workflows/pass2-p2c-isolated-proof-rerun-003.yml
test ! -e .github/workflows/pass2-p2c-isolated-proof-rerun-004.yml
python3 - "$BASE_SHA" <<'PY'
import hashlib,json,pathlib,subprocess,sys
base=sys.argv[1]
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
changed=set(subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml'}
extras=sorted(p for p in changed if p not in allowed and not p.startswith(str(root)+'/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/'))
assert not extras,extras
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path=root/'P2C_EXACTLY_ONE_REFRESHED_FROZEN_CAPSULE_BROWSER_PROOF_AUTHORIZATION_RECEIPT_008.json'
receipt=json.loads(receipt_path.read_text())
directive=json.loads((root/'P2C_ISOLATED_PROOF_RERUN_EXECUTION_DIRECTIVE_008.json').read_text())
scope=json.loads((root/'scope-lock-rerun-008.json').read_text())
manifest=json.loads((root/'EXECUTABLE_RERUN_MANIFEST_007.json').read_text())
assert sha(receipt_path)=='37a439de5a4f8320d1cdea3e692be592c14dfc639d1e8b6d6f42ec11d3cd159a'
assert receipt['authorized'] is True and receipt['status']=='AUTHORIZED_UNCONSUMED' and receipt['authorization_consumed'] is False
assert receipt['proof_run_count_authorized']==1 and receipt['proof_run_count_executed_under_this_receipt']==0
assert receipt['authorization_scope']=='EXACTLY_ONE_FUTURE_CHECKSUM_BOUND_DISPOSABLE_COPY_ISOLATED_BROWSER_PROOF_USING_REFRESHED_FROZEN_CAPSULE_CONTROLLER006_ONLY'
assert receipt['refreshed_frozen_capsule']['source_repository_commit']==manifest['source_repository_commit']
assert receipt['workflow_execution_authorized'] is False and receipt['browser_proof_execution_authorized'] is False
assert receipt['separate_execution_authorization_required'] is True
assert directive['authorized'] is True and directive['workflow_execution_authorized'] is True and directive['browser_proof_execution_authorized'] is True and directive['authorization_receipt_sha256']==sha(receipt_path)
assert directive['proof_run_count_to_execute']==1 and directive['proof_run_count_previously_executed_under_receipt']==0
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    assert receipt[key] is False,key; assert directive[key] is False,key; assert scope[key] is False,key
assert scope['event']=='pull_request.opened' and scope['required_run_attempt']==1
assert scope['workflow_dispatch_allowed'] is False and scope['workflow_filename']==manifest['workflow_filename']
assert manifest['source_repository_commit']==directive['source_repository_commit']==scope['source_repository_commit']
pathlib.Path('/tmp/p2c-rerun-scope-008.json').write_text(json.dumps({'status':'PASS','event':'pull_request.opened','run_attempt':1,'base_sha':base,'head_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'authorization_receipt_sha256':sha(receipt_path),'source_repository_commit':manifest['source_repository_commit'],'changed_paths':sorted(changed),'production_runtime_files_changed':False,'production_activation_authorized':False,'logical_proof_authorization_count':1,'proof_runs_previously_executed':0,'repair_continuation':'009-controller002-controller007','second_proof_run_authorized':False},indent=2,sort_keys=True)+'\n')
PY

echo "=== Reconstruct checksum-bound base runner and apply Repairs 003 through 008 exactly once ==="
set -euo pipefail
rm -rf "$BUNDLE_DIR" "$BUNDLE_TAR" "$EVIDENCE_DIR" "$NORMALIZED_ROOT"
mkdir -p "$BUNDLE_DIR" "$EVIDENCE_DIR" "$NORMALIZED_ROOT"
test "$(sha256sum "$DEPS_DIR/bundle/part06_0.bin" | awk '{print $1}')" = "13435f1fcf4aa33c2df7d719944bc986fea8ebe45b7568766a3e086a56fa94ae"
test "$(sha256sum "$DEPS_DIR/bundle/part06_1.bin" | awk '{print $1}')" = "917bc7936f8d9e5cbefbccbc7c4ff75f97156fada545d26c82e8f149c3feb7f8"
tr -d '\r\n' < "$DEPS_DIR/bundle/part06_2.b64" | base64 -d > /tmp/p2c-part06-2.bin
test "$(sha256sum /tmp/p2c-part06-2.bin | awk '{print $1}')" = "250e8719e8e5184206464906a35e082a1e83d1dcfe717276fdfdba175c08fdfe"
cat "$DEPS_DIR/bundle/part00.b64" "$DEPS_DIR/bundle/part01.b64" "$DEPS_DIR/bundle/part02.b64" "$DEPS_DIR/bundle/part03.b64" | tr -d '\r\n' | base64 -d > "$BUNDLE_TAR"
cat "$DEPS_DIR/bundle/part04_0.bin" "$DEPS_DIR/bundle/part04_1.bin" "$DEPS_DIR/bundle/part04_2.bin" "$DEPS_DIR/bundle/part05_0.bin" "$DEPS_DIR/bundle/part05_1.bin" "$DEPS_DIR/bundle/part06_0.bin" "$DEPS_DIR/bundle/part06_1.bin" /tmp/p2c-part06-2.bin >> "$BUNDLE_TAR"
test "$(wc -c < "$BUNDLE_TAR")" = "61478"
test "$(sha256sum "$BUNDLE_TAR" | awk '{print $1}')" = "a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500"
test "$(sha256sum "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" | awk '{print $1}')" = "efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57"
test "$(sha256sum "$DEPS_DIR/repair_runner_003.py" | awk '{print $1}')" = "ebb6f7c0b1b5d41eb795e48706cbfd00a66117653e03a8bce7248a5f63b5c1ca"
test "$(sha256sum "$DEPS_DIR/repair_runner_005.py" | awk '{print $1}')" = "c7d327f8e7133fd1d6a2e2c0958d29f33844898ebba468d2266e78464982e6a8"
test "$(sha256sum "$DEPS_DIR/repair_runner_006.py" | awk '{print $1}')" = "f88802507841710193dcecb3abd62934488fef5ce1e347f4689bd2d5aa9cb30f"
test "$(sha256sum "$DEPS_DIR/repair_runner_007.py" | awk '{print $1}')" = "e47b2530a2ab4180b255d6c1d70cbc314e72564cb4fa35ab2229c824d81384ee"
test "$(sha256sum "$DEPS_DIR/repair_runner_008.py" | awk '{print $1}')" = "9de909e03b5a691d4215c785f36ad64ce38e844c7540b9f5bdc65f4a1b671972"
test "$(sha256sum "$DEPS_DIR/repair_runner_009_controller002.py" | awk '{print $1}')" = "ad10e91f9f8319747d08f6f882031eae48aee7c9d7813b1a3f63ad5d0e4a72f7"
test "$(sha256sum "$DEPS_DIR/repair009_transport_fidelity_controller003.py" | awk '{print $1}')" = "4adec534bfbb17e0fa11d81918b078a73f44c7e16f38fdaad747b12b3f6199e7"
test "$(sha256sum "$DEPS_DIR/transpile_async_sources.part00.b64" | awk '{print $1}')" = "c2febd1a52ac905aab8af36d6995694eaf4719f886fe228860c44e827e268be3"
test "$(sha256sum "$DEPS_DIR/transpile_async_sources.part01.b64" | awk '{print $1}')" = "07b68e774f7d8534a70ba1e0fdafbb6b1df109482462e86cb343c4ad4ac786a1"
test "$(sha256sum "$DEPS_DIR/transpile_async_sources.part02.b64" | awk '{print $1}')" = "9f0be30991386eb2e75d03525cd18f54a16d2b682b4ae73d23c0de15ff90ffde"
test "$(sha256sum "$DEPS_DIR/repair009-normalized-source-manifest-002.json" | awk '{print $1}')" = "9e8bb7a9e2a695085d5fd80028bc8a2a4076865c355812044cd78fb6b0d44b76"
test -s "$AUDIT_DIR/pass2-p2c-isolated-proof-rerun-008.workflow-candidate.yml.txt"
rm -rf /tmp/p2c-transformer-transport-006; mkdir -p /tmp/p2c-transformer-transport-006
cp "$DEPS_DIR"/transpile_async_sources.part*.b64 /tmp/p2c-transformer-transport-006/
python3 "$DEPS_DIR/repair009_transport_fidelity_controller003.py" /tmp/p2c-transformer-transport-006 | tee "$EVIDENCE_DIR/transport-controller003.json"
TRANSFORMER_JS=/tmp/p2c-transformer-transport-006/transpile_async_sources.decoded.js
test "$(sha256sum "$TRANSFORMER_JS" | awk '{print $1}')" = "c5ffb899637aa45feb64b604dca426503f99fc9a34f05a1c83a12d0cfef3d0dd"
test "$(git hash-object "$TRANSFORMER_JS")" = "06a33bfd0bed8cc4b914b519bab606ddcd719cd1"
tar -xzf "$BUNDLE_TAR" -C "$BUNDLE_DIR"
sha256sum "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" "$DEPS_DIR/repair_runner_003.py" "$DEPS_DIR/repair_runner_005.py" "$DEPS_DIR/repair_runner_006.py" "$DEPS_DIR/repair_runner_007.py" "$DEPS_DIR/repair_runner_008.py" "$DEPS_DIR/repair_runner_009_controller002.py" "$DEPS_DIR/repair009_transport_fidelity_controller003.py" "$DEPS_DIR/transpile_async_sources.part00.b64" "$DEPS_DIR/transpile_async_sources.part01.b64" "$DEPS_DIR/transpile_async_sources.part02.b64" "$DEPS_DIR/repair009-normalized-source-manifest-002.json" > "$EVIDENCE_DIR/repair-script-sha256-controller007.txt"
python3 -m py_compile "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" "$DEPS_DIR/repair_runner_003.py" "$DEPS_DIR/repair_runner_005.py" "$DEPS_DIR/repair_runner_006.py" "$DEPS_DIR/repair_runner_007.py" "$DEPS_DIR/repair_runner_008.py" "$DEPS_DIR/repair_runner_009_controller002.py"
python3 "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" --path "$BUNDLE_DIR/prepare_disposable_proof_002.py"
python3 "$DEPS_DIR/repair_runner_003.py" --bundle-root "$BUNDLE_DIR"
python3 "$DEPS_DIR/repair_runner_005.py" --bundle-root "$BUNDLE_DIR"
python3 "$DEPS_DIR/repair_runner_008.py" --bundle-root "$BUNDLE_DIR"

echo "=== Create exact detached baseline and active worktrees ==="
set -euo pipefail
rm -rf "$BASELINE_ROOT" "$ACTIVE_ROOT"
git worktree add --detach "$BASELINE_ROOT" "$SOURCE_COMMIT"
git worktree add --detach "$ACTIVE_ROOT" "$SOURCE_COMMIT"
test "$(git -C "$BASELINE_ROOT" rev-parse HEAD)" = "$SOURCE_COMMIT"
test "$(git -C "$ACTIVE_ROOT" rev-parse HEAD)" = "$SOURCE_COMMIT"
test -z "$(git -C "$BASELINE_ROOT" status --porcelain)"
test -z "$(git -C "$ACTIVE_ROOT" status --porcelain)"

echo "=== Deterministically regenerate and verify 19 normalized actor sources ==="
set -euo pipefail
npm install -g typescript@5.8.3
TS_GLOBAL_MODULE="$(npm root -g)/typescript"
TS_FIXED_MODULE="/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript"
test -f "$TS_GLOBAL_MODULE/package.json"
test "$(node --no-global-search-paths -e 'console.log(require(process.argv[1]).version)' "$TS_GLOBAL_MODULE/package.json")" = "5.8.3"
sudo mkdir -p "$(dirname "$TS_FIXED_MODULE")"
sudo rm -rf "$TS_FIXED_MODULE"
sudo ln -s "$TS_GLOBAL_MODULE" "$TS_FIXED_MODULE"
test -L "$TS_FIXED_MODULE"
test "$(node --no-global-search-paths -e 'console.log(require(process.argv[1]).version)' "$TS_FIXED_MODULE/package.json")" = "5.8.3"
python3 - <<'PY'
import json,os,pathlib,subprocess
fixed=pathlib.Path('/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript')
global_module=pathlib.Path(subprocess.check_output(['npm','root','-g'],text=True).strip())/'typescript'
out={
  'type':'PMP_REPAIR009_TYPESCRIPT_MODULE_PATH_RECEIPT_004',
  'status':'PASS',
  'typescript_version':'5.8.3',
  'global_module':str(global_module),
  'fixed_module':str(fixed),
  'fixed_module_is_symlink':fixed.is_symlink(),
  'fixed_module_resolves_to_global':fixed.resolve()==global_module.resolve(),
  'verification_preceded_transformer_execution':True,
}
assert out['fixed_module_is_symlink'] is True
assert out['fixed_module_resolves_to_global'] is True
(pathlib.Path(os.environ['EVIDENCE_DIR'])/'typescript-module-path-004.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
PY
python3 - <<'PY'
import hashlib,json,os,pathlib
root=pathlib.Path(os.environ['DEPS_DIR'])
bundle=pathlib.Path(os.environ['BUNDLE_DIR'])
baseline=pathlib.Path(os.environ['BASELINE_ROOT'])
manifest=json.loads((root/'repair009-normalized-source-manifest-002.json').read_text())
records=[]
for row in manifest['records']:
    source=(bundle/'after'/row['path']) if row['kind']=='document-inline' else (baseline/row['path'])
    assert source.is_file(),source
    actual=hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual==row['original_sha256'],(row['path'],actual,row['original_sha256'])
    records.append({'kind':row['kind'],'path':row['path'],'policy_original_sha256':row['original_sha256'],'quarantined':False,'realm':row['realm'],'source_path':str(source)})
out={'type':'PMP_REPAIR009_ASYNC_SOURCE_NORMALIZATION_INPUT_002','records':records}
pathlib.Path('/tmp/p2c-repair009-normalization-input-006.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
PY
node /tmp/p2c-transformer-transport-006/transpile_async_sources.decoded.js /tmp/p2c-repair009-normalization-input-006.json "$NORMALIZED_ROOT" > "$EVIDENCE_DIR/async-source-normalization-report-006.json"
python3 - <<'PY'
import json,os,pathlib
e=pathlib.Path(os.environ['EVIDENCE_DIR'])
root=pathlib.Path(os.environ['DEPS_DIR'])
report=json.loads((e/'async-source-normalization-report-006.json').read_text())
manifest=json.loads((root/'repair009-normalized-source-manifest-002.json').read_text())
assert report['type']=='PMP_REPAIR009_ASYNC_SOURCE_NORMALIZATION_REPORT_002'
assert report['typescript_version']=='5.8.3' and len(report['records'])==19
by={x['path']:x for x in report['records']}
for row in manifest['records']:
    got=by[row['path']]
    assert got['original_sha256']==row['original_sha256'],row['path']
    assert got['transformed_sha256']==row['transformed_sha256'],row['path']
    assert got['original_bytes']==row['original_bytes'],row['path']
    assert got['transformed_bytes']==row['transformed_bytes'],row['path']
    assert got['residual_async_nodes']==0 and got['residual_await_nodes']==0,row['path']
PY

echo "=== Apply Repair 009 Controller 002 and compile final disposable runner ==="
set -euo pipefail
python3 "$DEPS_DIR/repair_runner_009_controller002.py" --bundle-root "$BUNDLE_DIR" --normalized-root "$NORMALIZED_ROOT" --normalization-manifest "$DEPS_DIR/repair009-normalized-source-manifest-002.json" | tee "$EVIDENCE_DIR/repair009-controller002-apply.log"
python3 -m py_compile "$BUNDLE_DIR/prepare_disposable_proof_002.py" "$BUNDLE_DIR/rollback_disposable_proof_002.py" "$BUNDLE_DIR/run_full_isolated_proof_002.py"
node --check "$BUNDLE_DIR/after/pmp-p2c-production-enforcement-adapter-candidate-001.js"
node --check "$BUNDLE_DIR/run_production_shaped_browser_proof_002.cjs"

echo "=== Install isolated Chromium dependency ==="
set -euo pipefail
rm -rf "$NODE_HOME"; mkdir -p "$NODE_HOME"; cd "$NODE_HOME"
npm init -y >/dev/null
npm install --no-save playwright@1.55.0
"$NODE_HOME/node_modules/.bin/playwright" install --with-deps chromium

echo "=== Use Controller007-generated compatibility runtime receipt 008 ==="
set -euo pipefail
test "$(sha256sum "$AUDIT_DIR/p2c-proof-runtime-authorization-receipt-008.json" | awk '{print $1}')" = "0bbd7c4bcace7101237b9a0b8b612bf90bebd9697b95efc90a61bb6cdf438f26"
cp "$AUDIT_DIR/p2c-proof-runtime-authorization-receipt-008.json" "/tmp/p2c-proof-runtime-authorization-receipt-008.json"

echo "=== Prepare explicitly authorized disposable active copy ==="
set -o pipefail
python3 "$BUNDLE_DIR/prepare_disposable_proof_002.py" \
  --baseline-root "$BASELINE_ROOT" \
  --activated-root "$ACTIVE_ROOT" \
  --payload-root "$BUNDLE_DIR" \
  --authorization-receipt /tmp/p2c-proof-runtime-authorization-receipt-008.json \
  --evidence-dir "$EVIDENCE_DIR" \
  --output "$EVIDENCE_DIR/preparation.json" 2>&1 | tee "$EVIDENCE_DIR/preparation-console.log"
python3 - <<'PY'
import json,os,pathlib
r=json.loads((pathlib.Path(os.environ['EVIDENCE_DIR'])/'preparation.json').read_text())
assert r['status']=='PASS' and r['baseline_file_count']==1481
assert r['governed_actor_count']==86 and r['quarantine_count']==25
assert r['current_map_unchanged'] is True and r['production_changed'] is False
x=r['a003_root_receipt_authority_exception']
assert x['status']=='APPLIED' and x['capture_timing']=='BEFORE_ACTOR_GATE_INSTALL'
assert x['ordinary_actor_storage_authority_changed'] is False
assert x['ordinary_actor_network_authority_changed'] is False
y=r['callback_bound_actor_lease_repair']
assert y['status']=='APPLIED'
assert y['authority_model']=='SOURCE_NORMALIZED_PROMISE_CONTINUATIONS'
assert y['callback_registration_authority']=='EVENT_HANDLER_PROPERTY_SETTERS_BOUND'
assert y['global_ambient_authority'] is False and y['lease_revalidated_on_callback'] is True
assert y['ambient_depth_constant_zero'] is True
z=r['repair009_async_continuation_normalization']
assert z['status']=='APPLIED' and z['record_count']==19
assert z['global_ambient_authority'] is False and z['quarantined_actors_changed'] is False
PY

echo "=== Run exactly one active browser rollback and restored regression chain ==="
set -o pipefail
test ! -e "$EVIDENCE_DIR/proof-run-started.lock"
printf '%s\n' "$RUN_ID:$RUN_ATTEMPT" > "$EVIDENCE_DIR/proof-run-started.lock"
python3 "$BUNDLE_DIR/run_full_isolated_proof_002.py" \
  --activated-root "$ACTIVE_ROOT" \
  --baseline-root "$BASELINE_ROOT" \
  --evidence-dir "$EVIDENCE_DIR" \
  --scripts-root "$BUNDLE_DIR" \
  --output "$EVIDENCE_DIR/aggregate.json" 2>&1 | tee "$EVIDENCE_DIR/aggregate-console.log"

