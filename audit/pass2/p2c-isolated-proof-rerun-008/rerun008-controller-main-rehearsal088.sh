#!/usr/bin/env bash
set -euo pipefail
BASE_WRAPPER="$AUDIT_DIR/rerun008-controller-main-receipt082.sh"
MATERIALIZED="${TMPDIR:-/tmp}/p2c-rehearsal090-wrapper-$$.sh"
trap 'rm -f "$MATERIALIZED"' EXIT
cp "$BASE_WRAPPER" "$MATERIALIZED"
python3 - "$MATERIALIZED" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
old='patch_runtime_nodepath_and_source_bindings_receipt082.py'
new='patch_runtime_nodepath_and_messageport_rehearsal090.py'
count=text.count(old)
if count!=1:
    raise SystemExit(f'REHEARSAL090_RUNTIME_PATCHER_FILENAME_COUNT_INVALID:{count}')
text=text.replace(old,new,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED"
export P2C_REHEARSAL_SKIP_AUTHORIZATION=1
exec bash "$MATERIALIZED"
