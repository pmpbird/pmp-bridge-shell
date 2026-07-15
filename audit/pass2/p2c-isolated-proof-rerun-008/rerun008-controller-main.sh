#!/usr/bin/env bash
set -uo pipefail

mkdir -p "$EVIDENCE_DIR" "$BUNDLE_DIR" "$NORMALIZED_ROOT"
DIAG="$EVIDENCE_DIR/receipt016-controller-diagnostic.json"

write_diag() {
  local status="$1" line="$2" command="$3" expected="$4" actual="$5" affected="$6"
  python3 - "$DIAG" "$status" "$line" "$command" "$expected" "$actual" "$affected" <<'PY'
import json,pathlib,sys
path,status,line,command,expected,actual,affected=sys.argv[1:]
out={
  'type':'PMP_P2C_RECEIPT016_CONTROLLER_DIAGNOSTIC_V1',
  'status':status,
  'failed_line':int(line) if line.isdigit() else line,
  'failed_command':command,
  'expected_value':expected,
  'actual_value':actual,
  'affected_file':affected,
  'diagnostic_scope':'PRE_WORKTREE_VERIFICATION_AND_RECONSTRUCTION_ONLY',
  'git_worktree_add_executed':False,
  'playwright_or_chromium_install_executed':False,
  'disposable_copy_preparation_executed':False,
  'browser_proof_executed':False,
  'proof_run_count_executed':0,
  'receipts_modified':False,
  'authorization_bindings_modified':False,
  'production_files_modified':False,
  'current_map_modified':False,
  'persisted_data_modified':False,
}
pathlib.Path(path).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
PY
}

fail() {
  local line="$1" command="$2" expected="$3" actual="$4" affected="$5"
  write_diag FAIL "$line" "$command" "$expected" "$actual" "$affected"
  printf 'RECEIPT016_DIAGNOSTIC_FAILURE line=%s command=%q expected=%q actual=%q affected=%q\n' "$line" "$command" "$expected" "$actual" "$affected" >&2
  exit 1
}

check_sha() {
  local file="$1" expected="$2" line="$3"
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')" || fail "$line" "sha256sum $file" "$expected" "COMMAND_FAILED" "$file"
  [ "$actual" = "$expected" ] || fail "$line" "sha256sum $file" "$expected" "$actual" "$file"
}

run_step() {
  local line="$1" affected="$2"; shift 2
  "$@"
  local rc=$?
  [ $rc -eq 0 ] || fail "$line" "$*" "exit_code=0" "exit_code=$rc" "$affected"
}

# Reproduce the controller's pre-worktree authorization and scope checks with named diagnostics.
python3 - "$BASE_SHA" "$DIAG" <<'PY'
import hashlib,json,pathlib,subprocess,sys
base,diag=sys.argv[1:]
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
def fail(line,command,expected,actual,affected):
    out={'type':'PMP_P2C_RECEIPT016_CONTROLLER_DIAGNOSTIC_V1','status':'FAIL','failed_line':line,'failed_command':command,'expected_value':str(expected),'actual_value':str(actual),'affected_file':str(affected),'diagnostic_scope':'PRE_WORKTREE_VERIFICATION_AND_RECONSTRUCTION_ONLY','git_worktree_add_executed':False,'playwright_or_chromium_install_executed':False,'disposable_copy_preparation_executed':False,'browser_proof_executed':False,'proof_run_count_executed':0,'receipts_modified':False,'authorization_bindings_modified':False,'production_files_modified':False,'current_map_modified':False,'persisted_data_modified':False}
    pathlib.Path(diag).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    raise SystemExit(1)
def check(line,command,actual,expected,affected):
    if actual!=expected: fail(line,command,expected,actual,affected)
changed=set(subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','audit/a002-live-runtime.cjs'}
extras=sorted(p for p in changed if p not in allowed and not p.startswith(str(root)+'/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/'))
check(24,'controller changed-path allowlist',extras,[],','.git diff')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path=root/'P2C_EXACTLY_ONE_REFRESHED_FROZEN_CAPSULE_BROWSER_PROOF_AUTHORIZATION_RECEIPT_008.json'
receipt=json.loads(receipt_path.read_text()); directive=json.loads((root/'P2C_ISOLATED_PROOF_RERUN_EXECUTION_DIRECTIVE_008.json').read_text()); scope=json.loads((root/'scope-lock-rerun-008.json').read_text()); manifest=json.loads((root/'EXECUTABLE_RERUN_MANIFEST_007.json').read_text())
check(31,'receipt008 sha256',sha(receipt_path),'37a439de5a4f8320d1cdea3e692be592c14dfc639d1e8b6d6f42ec11d3cd159a',receipt_path)
check(32,'receipt008 authorization tuple',(receipt.get('authorized'),receipt.get('status'),receipt.get('authorization_consumed')),(True,'AUTHORIZED_UNCONSUMED',False),receipt_path)
check(33,'receipt008 run-count tuple',(receipt.get('proof_run_count_authorized'),receipt.get('proof_run_count_executed_under_this_receipt')),(1,0),receipt_path)
check(34,'receipt008 authorization scope',receipt.get('authorization_scope'),'EXACTLY_ONE_FUTURE_CHECKSUM_BOUND_DISPOSABLE_COPY_ISOLATED_BROWSER_PROOF_USING_REFRESHED_FROZEN_CAPSULE_CONTROLLER006_ONLY',receipt_path)
check(35,'source commit receipt/manifest',receipt['refreshed_frozen_capsule']['source_repository_commit'],manifest['source_repository_commit'],receipt_path)
check(36,'receipt008 execution flags',(receipt.get('workflow_execution_authorized'),receipt.get('browser_proof_execution_authorized')),(False,False),receipt_path)
check(37,'separate authorization required',receipt.get('separate_execution_authorization_required'),True,receipt_path)
check(38,'directive authorization tuple',(directive.get('authorized'),directive.get('workflow_execution_authorized'),directive.get('browser_proof_execution_authorized'),directive.get('authorization_receipt_sha256')),(True,True,True,sha(receipt_path)),root/'P2C_ISOLATED_PROOF_RERUN_EXECUTION_DIRECTIVE_008.json')
check(39,'directive run-count tuple',(directive.get('proof_run_count_to_execute'),directive.get('proof_run_count_previously_executed_under_receipt')),(1,0),root/'P2C_ISOLATED_PROOF_RERUN_EXECUTION_DIRECTIVE_008.json')
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    check(40,f'forbidden flag {key}',(receipt.get(key),directive.get(key),scope.get(key)),(False,False,False),key)
check(42,'scope event tuple',(scope.get('event'),scope.get('required_run_attempt')),('pull_request.opened',1),root/'scope-lock-rerun-008.json')
check(43,'scope workflow tuple',(scope.get('workflow_dispatch_allowed'),scope.get('workflow_filename')),(False,manifest['workflow_filename']),root/'scope-lock-rerun-008.json')
check(44,'source commit directive/scope',(manifest['source_repository_commit'],directive['source_repository_commit'],scope['source_repository_commit']),(manifest['source_repository_commit'],)*3,root/'EXECUTABLE_RERUN_MANIFEST_007.json')
PY
rc=$?
[ $rc -eq 0 ] || exit $rc

rm -rf "$BUNDLE_DIR" "$BUNDLE_TAR" "$NORMALIZED_ROOT"
mkdir -p "$BUNDLE_DIR" "$NORMALIZED_ROOT"
check_sha "$DEPS_DIR/bundle/part06_0.bin" "13435f1fcf4aa33c2df7d719944bc986fea8ebe45b7568766a3e086a56fa94ae" 52
check_sha "$DEPS_DIR/bundle/part06_1.bin" "917bc7936f8d9e5cbefbccbc7c4ff75f97156fada545d26c82e8f149c3feb7f8" 53
run_step 54 "$DEPS_DIR/bundle/part06_2.b64" bash -c 'tr -d "\r\n" < "$1" | base64 -d > /tmp/p2c-part06-2.bin' _ "$DEPS_DIR/bundle/part06_2.b64"
check_sha /tmp/p2c-part06-2.bin "250e8719e8e5184206464906a35e082a1e83d1dcfe717276fdfdba175c08fdfe" 55
run_step 56 "$BUNDLE_TAR" bash -c 'cat "$1" "$2" "$3" "$4" | tr -d "\r\n" | base64 -d > "$5"' _ "$DEPS_DIR/bundle/part00.b64" "$DEPS_DIR/bundle/part01.b64" "$DEPS_DIR/bundle/part02.b64" "$DEPS_DIR/bundle/part03.b64" "$BUNDLE_TAR"
run_step 57 "$BUNDLE_TAR" bash -c 'cat "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" >> "$9"' _ "$DEPS_DIR/bundle/part04_0.bin" "$DEPS_DIR/bundle/part04_1.bin" "$DEPS_DIR/bundle/part04_2.bin" "$DEPS_DIR/bundle/part05_0.bin" "$DEPS_DIR/bundle/part05_1.bin" "$DEPS_DIR/bundle/part06_0.bin" "$DEPS_DIR/bundle/part06_1.bin" /tmp/p2c-part06-2.bin "$BUNDLE_TAR"
actual_bytes="$(wc -c < "$BUNDLE_TAR" | tr -d ' ')"; [ "$actual_bytes" = "61478" ] || fail 58 "wc -c $BUNDLE_TAR" "61478" "$actual_bytes" "$BUNDLE_TAR"
check_sha "$BUNDLE_TAR" "a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500" 59
check_sha "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" "efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57" 60
check_sha "$DEPS_DIR/repair_runner_003.py" "ebb6f7c0b1b5d41eb795e48706cbfd00a66117653e03a8bce7248a5f63b5c1ca" 61
check_sha "$DEPS_DIR/repair_runner_005.py" "c7d327f8e7133fd1d6a2e2c0958d29f33844898ebba468d2266e78464982e6a8" 62
check_sha "$DEPS_DIR/repair_runner_006.py" "f88802507841710193dcecb3abd62934488fef5ce1e347f4689bd2d5aa9cb30f" 63
check_sha "$DEPS_DIR/repair_runner_007.py" "e47b2530a2ab4180b255d6c1d70cbc314e72564cb4fa35ab2229c824d81384ee" 64
check_sha "$DEPS_DIR/repair_runner_008.py" "9de909e03b5a691d4215c785f36ad64ce38e844c7540b9f5bdc65f4a1b671972" 65
check_sha "$DEPS_DIR/repair_runner_009_controller002.py" "ad10e91f9f8319747d08f6f882031eae48aee7c9d7813b1a3f63ad5d0e4a72f7" 66
check_sha "$DEPS_DIR/repair009_transport_fidelity_controller003.py" "4adec534bfbb17e0fa11d81918b078a73f44c7e16f38fdaad747b12b3f6199e7" 67
check_sha "$DEPS_DIR/transpile_async_sources.part00.b64" "c2febd1a52ac905aab8af36d6995694eaf4719f886fe228860c44e827e268be3" 68
check_sha "$DEPS_DIR/transpile_async_sources.part01.b64" "07b68e774f7d8534a70ba1e0fdafbb6b1df109482462e86cb343c4ad4ac786a1" 69
check_sha "$DEPS_DIR/transpile_async_sources.part02.b64" "9f0be30991386eb2e75d03525cd18f54a16d2b682b4ae73d23c0de15ff90ffde" 70
check_sha "$DEPS_DIR/repair009-normalized-source-manifest-002.json" "72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619" 71
[ -s "$AUDIT_DIR/pass2-p2c-isolated-proof-rerun-008.workflow-candidate.yml.txt" ] || fail 72 "test -s workflow candidate" "non-empty file" "missing-or-empty" "$AUDIT_DIR/pass2-p2c-isolated-proof-rerun-008.workflow-candidate.yml.txt"
rm -rf /tmp/p2c-transformer-transport-006; mkdir -p /tmp/p2c-transformer-transport-006
run_step 74 /tmp/p2c-transformer-transport-006 cp "$DEPS_DIR"/transpile_async_sources.part*.b64 /tmp/p2c-transformer-transport-006/
run_step 75 "$DEPS_DIR/repair009_transport_fidelity_controller003.py" python3 "$DEPS_DIR/repair009_transport_fidelity_controller003.py" /tmp/p2c-transformer-transport-006
TRANSFORMER_JS=/tmp/p2c-transformer-transport-006/transpile_async_sources.decoded.js
check_sha "$TRANSFORMER_JS" "c5ffb899637aa45feb64b604dca426503f99fc9a34f05a1c83a12d0cfef3d0dd" 77
actual_blob="$(git hash-object "$TRANSFORMER_JS")"; [ "$actual_blob" = "06a33bfd0bed8cc4b914b519bab606ddcd719cd1" ] || fail 78 "git hash-object $TRANSFORMER_JS" "06a33bfd0bed8cc4b914b519bab606ddcd719cd1" "$actual_blob" "$TRANSFORMER_JS"
run_step 79 "$BUNDLE_TAR" tar -xzf "$BUNDLE_TAR" -C "$BUNDLE_DIR"
run_step 81 "$DEPS_DIR" python3 -m py_compile "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" "$DEPS_DIR/repair_runner_003.py" "$DEPS_DIR/repair_runner_005.py" "$DEPS_DIR/repair_runner_006.py" "$DEPS_DIR/repair_runner_007.py" "$DEPS_DIR/repair_runner_008.py" "$DEPS_DIR/repair_runner_009_controller002.py"
run_step 82 "$BUNDLE_DIR/prepare_disposable_proof_002.py" python3 "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" --path "$BUNDLE_DIR/prepare_disposable_proof_002.py"
run_step 83 "$DEPS_DIR/repair_runner_003.py" python3 "$DEPS_DIR/repair_runner_003.py" --bundle-root "$BUNDLE_DIR"
run_step 84 "$DEPS_DIR/repair_runner_005.py" python3 "$DEPS_DIR/repair_runner_005.py" --bundle-root "$BUNDLE_DIR"
run_step 85 "$DEPS_DIR/repair_runner_008.py" python3 "$DEPS_DIR/repair_runner_008.py" --bundle-root "$BUNDLE_DIR"

write_diag PASS 86 "diagnostic hard stop before git worktree add" "stop before worktree creation" "stopped before worktree creation" "audit/pass2/p2c-isolated-proof-rerun-008/rerun008-controller-main.sh"
echo "RECEIPT016_DIAGNOSTIC_PRE_WORKTREE_PASS"
exit 0
