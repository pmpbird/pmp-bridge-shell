#!/usr/bin/env bash
set -euo pipefail
BASE_WRAPPER="$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
MATERIALIZED="${TMPDIR:-/tmp}/p2c-receipt082-base-wrapper-$$.sh"
trap 'rm -f "$MATERIALIZED"' EXIT
cp "$BASE_WRAPPER" "$MATERIALIZED"
python3 - "$MATERIALIZED" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
old="new_prepare='python3 \"$AUDIT_DIR/prepare_disposable_proof_002_receipt066_argument_proxy.py\" \"$BUNDLE_DIR/prepare_disposable_proof_002.py\" \"$SOURCE_COMMIT\"'"
new="new_prepare='python3 \"$BUNDLE_DIR/prepare_disposable_proof_002.py\"'"
if text.count(old)!=1:
    raise SystemExit(f'RECEIPT082_OLD_ARGUMENT_PROXY_BINDING_COUNT_INVALID:{text.count(old)}')
text=text.replace(old,new,1)
needle="path.write_text(text)\nPY"
inject="""prepare_hook='python3 \"$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py\" --path \"$BUNDLE_DIR/prepare_disposable_proof_002.py\"'
prepare_patched=prepare_hook+'\\npython3 \"$AUDIT_DIR/patch_prepare_source_commit_constant_receipt078.py\" --path \"$BUNDLE_DIR/prepare_disposable_proof_002.py\" --source-commit \"$SOURCE_COMMIT\" --evidence-dir \"$EVIDENCE_DIR\"'
if text.count(prepare_hook)!=1:raise SystemExit(f'RECEIPT082_PREPARE_REPAIR_HOOK_COUNT_INVALID:{text.count(prepare_hook)}')
text=text.replace(prepare_hook,prepare_patched,1)
repair009_hook='python3 \"$DEPS_DIR/repair_runner_009_controller002_policycompat_022.py\" --bundle-root \"$BUNDLE_DIR\" --normalized-root \"$NORMALIZED_ROOT\" --normalization-manifest \"$DEPS_DIR/repair009-normalized-source-manifest-002.json\" | tee \"$EVIDENCE_DIR/repair009-controller002-apply.log\"'
runtime_patch='python3 \"$AUDIT_DIR/patch_runtime_nodepath_and_source_bindings_receipt082.py\" --bundle-root \"$BUNDLE_DIR\" --old-source-commit c618596f2b5c99ca7f355153a5bd31268170df80 --new-source-commit \"$SOURCE_COMMIT\" --evidence-dir \"$EVIDENCE_DIR\"'
if text.count(repair009_hook)!=1:raise SystemExit(f'RECEIPT082_REPAIR009_FINAL_RUNNER_HOOK_COUNT_INVALID:{text.count(repair009_hook)}')
text=text.replace(repair009_hook,repair009_hook+'\\n'+runtime_patch,1)
marker='echo \"=== Prepare explicitly authorized disposable active copy ===\"'
nodepath='export NODE_PATH=\"$NODE_HOME/node_modules${NODE_PATH:+:$NODE_PATH}\"\\nprintf \"%s\\\\n\" \"NODE_PATH_BOUND:$NODE_PATH\" > \"$EVIDENCE_DIR/node-path-binding-082.log\"\\n'+marker
if text.count(marker)!=1:raise SystemExit(f'RECEIPT082_PREPARATION_MARKER_COUNT_INVALID:{text.count(marker)}')
text=text.replace(marker,nodepath,1)
path.write_text(text)
PY"""
if text.count(needle)!=1:
    raise SystemExit(f'RECEIPT082_TRANSFORMER_WRITE_HOOK_COUNT_INVALID:{text.count(needle)}')
text=text.replace(needle,inject,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED"
exec bash "$MATERIALIZED"
