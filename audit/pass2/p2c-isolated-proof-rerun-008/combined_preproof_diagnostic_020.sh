#!/usr/bin/env bash
set -euo pipefail
SOURCE_COMMIT='98b2e293717b81289e3b372d1fff8f5832d29fd6'
DEPS_DIR='audit/pass2/p2c-isolated-proof-rerun-006'
EVIDENCE_DIR='/tmp/p2c-combined-preproof-evidence'
BUNDLE_DIR='/tmp/p2c-combined-preproof-bundle'
BUNDLE_TAR='/tmp/p2c-combined-preproof-bundle.tar.gz'
SOURCE_DIR='/tmp/p2c-combined-preproof-sources'
NORMALIZED_ROOT='/tmp/p2c-combined-preproof-normalized'
TRANSPORT_DIR='/tmp/p2c-combined-preproof-transport'
trap 'rc=$?; printf "COMBINED_PREPROOF_FAILURE line=%s rc=%s command=%q\n" "$LINENO" "$rc" "$BASH_COMMAND" | tee "$EVIDENCE_DIR/failure.txt" >&2; exit "$rc"' ERR
rm -rf "$EVIDENCE_DIR" "$BUNDLE_DIR" "$BUNDLE_TAR" "$SOURCE_DIR" "$NORMALIZED_ROOT" "$TRANSPORT_DIR"
mkdir -p "$EVIDENCE_DIR" "$BUNDLE_DIR" "$SOURCE_DIR" "$NORMALIZED_ROOT" "$TRANSPORT_DIR"

# Stage 1: exact bundle reconstruction and all pre-worktree repairs.
tr -d '\r\n' < "$DEPS_DIR/bundle/part06_2.b64" | base64 -d > /tmp/p2c-part06-2-combined.bin
cat "$DEPS_DIR/bundle/part00.b64" "$DEPS_DIR/bundle/part01.b64" "$DEPS_DIR/bundle/part02.b64" "$DEPS_DIR/bundle/part03.b64" | tr -d '\r\n' | base64 -d > "$BUNDLE_TAR"
cat "$DEPS_DIR/bundle/part04_0.bin" "$DEPS_DIR/bundle/part04_1.bin" "$DEPS_DIR/bundle/part04_2.bin" "$DEPS_DIR/bundle/part05_0.bin" "$DEPS_DIR/bundle/part05_1.bin" "$DEPS_DIR/bundle/part06_0.bin" "$DEPS_DIR/bundle/part06_1.bin" /tmp/p2c-part06-2-combined.bin >> "$BUNDLE_TAR"
test "$(wc -c < "$BUNDLE_TAR")" = '61478'
test "$(sha256sum "$BUNDLE_TAR" | awk '{print $1}')" = 'a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500'
tar -xzf "$BUNDLE_TAR" -C "$BUNDLE_DIR"
test "$(sha256sum "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" | awk '{print $1}')" = 'd4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
test "$(sha256sum "$DEPS_DIR/repair009-normalized-source-manifest-002.json" | awk '{print $1}')" = 'd53dc787298e8fec5f00227b680645dffd25774913ba34461d4969df6bf2b803'
python3 -m py_compile "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" "$DEPS_DIR/repair_runner_003.py" "$DEPS_DIR/repair_runner_005.py" "$DEPS_DIR/repair_runner_006.py" "$DEPS_DIR/repair_runner_007.py" "$DEPS_DIR/repair_runner_008.py" "$DEPS_DIR/repair_runner_009_controller002.py"
python3 "$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py" --path "$BUNDLE_DIR/prepare_disposable_proof_002.py"
python3 "$DEPS_DIR/repair_runner_003.py" --bundle-root "$BUNDLE_DIR"
python3 "$DEPS_DIR/repair_runner_005.py" --bundle-root "$BUNDLE_DIR"
python3 "$DEPS_DIR/repair_runner_008.py" --bundle-root "$BUNDLE_DIR"

# Stage 2: deterministic 19-source normalization.
npm install -g typescript@5.8.3 >/dev/null
TS_GLOBAL_MODULE="$(npm root -g)/typescript"
TS_FIXED_MODULE='/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript'
test -f "$TS_GLOBAL_MODULE/package.json"
test "$(node --no-global-search-paths -e 'console.log(require(process.argv[1]).version)' "$TS_GLOBAL_MODULE/package.json")" = '5.8.3'
sudo mkdir -p "$(dirname "$TS_FIXED_MODULE")"
sudo rm -rf "$TS_FIXED_MODULE"
sudo ln -s "$TS_GLOBAL_MODULE" "$TS_FIXED_MODULE"
cp "$DEPS_DIR"/transpile_async_sources.part*.b64 "$TRANSPORT_DIR"/
python3 "$DEPS_DIR/repair009_transport_fidelity_controller003.py" "$TRANSPORT_DIR" > "$EVIDENCE_DIR/transport-controller003.json"
TRANSFORMER_JS="$TRANSPORT_DIR/transpile_async_sources.decoded.js"
test "$(sha256sum "$TRANSFORMER_JS" | awk '{print $1}')" = 'c5ffb899637aa45feb64b604dca426503f99fc9a34f05a1c83a12d0cfef3d0dd'
python3 - <<'PY'
import hashlib,json,pathlib,subprocess
source_commit='98b2e293717b81289e3b372d1fff8f5832d29fd6'
deps=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-006'); bundle=pathlib.Path('/tmp/p2c-combined-preproof-bundle')
source_dir=pathlib.Path('/tmp/p2c-combined-preproof-sources'); evidence=pathlib.Path('/tmp/p2c-combined-preproof-evidence')
manifest=json.loads((deps/'repair009-normalized-source-manifest-002.json').read_text()); records=[]
for index,row in enumerate(manifest['records'],1):
    target=source_dir/row['path']; target.parent.mkdir(parents=True,exist_ok=True)
    data=(bundle/'after'/row['path']).read_bytes() if row['kind']=='document-inline' else subprocess.check_output(['git','show',f'{source_commit}:{row["path"]}'])
    assert hashlib.sha256(data).hexdigest()==row['original_sha256'],(index,row['path'],'sha')
    assert len(data)==row['original_bytes'],(index,row['path'],'bytes')
    target.write_bytes(data)
    records.append({'kind':row['kind'],'path':row['path'],'policy_original_sha256':row['original_sha256'],'quarantined':False,'realm':row['realm'],'source_path':str(target)})
(evidence/'normalization-input.json').write_text(json.dumps({'type':'PMP_REPAIR009_ASYNC_SOURCE_NORMALIZATION_INPUT_002','records':records},indent=2,sort_keys=True)+'\n')
PY
node "$TRANSFORMER_JS" "$EVIDENCE_DIR/normalization-input.json" "$NORMALIZED_ROOT" > "$EVIDENCE_DIR/normalization-report.json"
python3 - <<'PY'
import json,pathlib
E=pathlib.Path('/tmp/p2c-combined-preproof-evidence'); D=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-006')
r=json.loads((E/'normalization-report.json').read_text()); m=json.loads((D/'repair009-normalized-source-manifest-002.json').read_text())
assert r['type']=='PMP_REPAIR009_ASYNC_SOURCE_NORMALIZATION_REPORT_002' and r['typescript_version']=='5.8.3' and len(r['records'])==19
by={x['path']:x for x in r['records']}
for i,row in enumerate(m['records'],1):
    got=by[row['path']]
    assert got['original_sha256']==row['original_sha256'],(i,row['path'],'original_sha256')
    assert got['transformed_sha256']==row['transformed_sha256'],(i,row['path'],'transformed_sha256')
    assert got['original_bytes']==row['original_bytes'],(i,row['path'],'original_bytes')
    assert got['transformed_bytes']==row['transformed_bytes'],(i,row['path'],'transformed_bytes')
    assert got['residual_async_nodes']==0 and got['residual_await_nodes']==0,(i,row['path'],'residual')
PY

# Stage 3: Repair 009 Controller 002 and final compile validation.
python3 "$DEPS_DIR/repair_runner_009_controller002.py" --bundle-root "$BUNDLE_DIR" --normalized-root "$NORMALIZED_ROOT" --normalization-manifest "$DEPS_DIR/repair009-normalized-source-manifest-002.json" | tee "$EVIDENCE_DIR/repair009-controller002-apply.log"
python3 -m py_compile "$BUNDLE_DIR/prepare_disposable_proof_002.py" "$BUNDLE_DIR/rollback_disposable_proof_002.py" "$BUNDLE_DIR/run_full_isolated_proof_002.py"
node --check "$BUNDLE_DIR/after/pmp-p2c-production-enforcement-adapter-candidate-001.js"
node --check "$BUNDLE_DIR/run_production_shaped_browser_proof_002.cjs"
python3 - <<'PY'
import hashlib,json,pathlib
D=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-006'); E=pathlib.Path('/tmp/p2c-combined-preproof-evidence')
out={'type':'PMP_P2C_COMBINED_PREPROOF_DIAGNOSTIC_V1','status':'PASS','repair009_controller002_executed':True,'compile_validation_passed':True,'preworktree_reconstruction_passed':True,'manifest_sha256':hashlib.sha256((D/'repair009-normalized-source-manifest-002.json').read_bytes()).hexdigest(),'git_worktree_add_executed':False,'playwright_or_chromium_installed':False,'disposable_copy_preparation_executed':False,'browser_proof_executed':False,'proof_run_count_executed':0,'production_files_modified':False,'current_map_modified':False,'persisted_data_modified':False,'next_stage':'STATIC_RESEAL_AND_COMPLETE_PREFLIGHT'}
(E/'combined-preproof-diagnostic.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
PY
