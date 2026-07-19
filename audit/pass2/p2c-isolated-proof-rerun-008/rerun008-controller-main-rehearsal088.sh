#!/usr/bin/env bash
set -euo pipefail
BASE_WRAPPER="$AUDIT_DIR/rerun008-controller-main-receipt082.sh"
MATERIALIZED="${TMPDIR:-/tmp}/p2c-rehearsal088-wrapper-$$.sh"
trap 'rm -f "$MATERIALIZED"' EXIT
cp "$BASE_WRAPPER" "$MATERIALIZED"
python3 - "$MATERIALIZED" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
old='python3 "$AUDIT_DIR/patch_runtime_nodepath_and_source_bindings_receipt082.py" --bundle-root "$BUNDLE_DIR" --old-source-commit c618596f2b5c99ca7f355153a5bd31268170df80 --new-source-commit "$SOURCE_COMMIT" --evidence-dir "$EVIDENCE_DIR"'
new=old+'\\npython3 "$AUDIT_DIR/patch_a002_native_messageport_setter_rehearsal088.py" --path "$BUNDLE_DIR/run_full_isolated_proof_002.py" --evidence-dir "$EVIDENCE_DIR"'
if text.count(old)!=1:
    raise SystemExit(f'REHEARSAL088_RUNTIME_PATCH_HOOK_COUNT_INVALID:{text.count(old)}')
text=text.replace(old,new,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED"
export P2C_REHEARSAL_SKIP_AUTHORIZATION=1
exec bash "$MATERIALIZED"
