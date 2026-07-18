#!/usr/bin/env bash
set -euo pipefail
export NODE_PATH="$NODE_HOME/node_modules${NODE_PATH:+:$NODE_PATH}"
BASE_WRAPPER="$AUDIT_DIR/rerun008-controller-main-receipt078.sh"
MATERIALIZED="${TMPDIR:-/tmp}/p2c-receipt082-wrapper-$$.sh"
trap 'rm -f "$MATERIALIZED"' EXIT
cp "$BASE_WRAPPER" "$MATERIALIZED"
python3 - "$MATERIALIZED" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
needle='python3 "$AUDIT_DIR/patch_prepare_source_commit_constant_receipt078.py" --path "$BUNDLE_DIR/prepare_disposable_proof_002.py" --source-commit "$SOURCE_COMMIT" --evidence-dir "$EVIDENCE_DIR"'
addition=needle+'\npython3 "$AUDIT_DIR/patch_run_full_source_commit_receipt082.py" --path "$BUNDLE_DIR/run_full_isolated_proof_002.py" --source-commit "$SOURCE_COMMIT" --evidence-dir "$EVIDENCE_DIR"'
if text.count(needle)!=1:
    raise SystemExit(f'RECEIPT082_PREPARE_PATCH_HOOK_COUNT_INVALID:{text.count(needle)}')
text=text.replace(needle,addition,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED"
exec bash "$MATERIALIZED"
