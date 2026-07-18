#!/usr/bin/env bash
set -euo pipefail
BASE_WRAPPER="$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
MATERIALIZED="${TMPDIR:-/tmp}/p2c-receipt070-base-wrapper-$$.sh"
trap 'rm -f "$MATERIALIZED"' EXIT
cp "$BASE_WRAPPER" "$MATERIALIZED"
python3 - "$MATERIALIZED" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
old="new_prepare='python3 \"$AUDIT_DIR/prepare_disposable_proof_002_receipt066_argument_proxy.py\" \"$BUNDLE_DIR/prepare_disposable_proof_002.py\" \"$SOURCE_COMMIT\"'"
new="new_prepare='python3 \"$BUNDLE_DIR/prepare_disposable_proof_002.py\"'"
if text.count(old)!=1:
    raise SystemExit(f'RECEIPT070_OLD_ARGUMENT_PROXY_BINDING_COUNT_INVALID:{text.count(old)}')
text=text.replace(old,new,1)
needle="path.write_text(text)\nPY"
inject="""hook='python3 \"$DEPS_DIR/repair-continuation-003/apply_prepare_repair_003.py\" --path \"$BUNDLE_DIR/prepare_disposable_proof_002.py\"'\npatched=hook+'\\npython3 \"$AUDIT_DIR/patch_prepare_disposable_proof_002_receipt070.py\" --path \"$BUNDLE_DIR/prepare_disposable_proof_002.py\" --source-commit \"$SOURCE_COMMIT\" --evidence-dir \"$EVIDENCE_DIR\"'\nif text.count(hook)!=1:raise SystemExit(f'RECEIPT070_PREPARE_REPAIR_HOOK_COUNT_INVALID:{text.count(hook)}')\ntext=text.replace(hook,patched,1)\npath.write_text(text)\nPY"""
if text.count(needle)!=1:
    raise SystemExit(f'RECEIPT070_TRANSFORMER_WRITE_HOOK_COUNT_INVALID:{text.count(needle)}')
text=text.replace(needle,inject,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED"
exec bash "$MATERIALIZED"
