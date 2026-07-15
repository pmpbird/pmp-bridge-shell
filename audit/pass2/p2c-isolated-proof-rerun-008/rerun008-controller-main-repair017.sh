#!/usr/bin/env bash
set -euo pipefail
ORIGINAL_CONTROLLER_BLOB='cff2fffc59680e667abb53b0c18f508f6561e9eb'
OLD_PATCHER_SHA256='efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'
NEW_PATCHER_SHA256='d4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
MATERIALIZED_CONTROLLER="${TMPDIR:-/tmp}/p2c-rerun008-controller-main-repair017-$$.sh"
trap 'rm -f "$MATERIALIZED_CONTROLLER"' EXIT

git cat-file blob "$ORIGINAL_CONTROLLER_BLOB" > "$MATERIALIZED_CONTROLLER"
python3 - "$MATERIALIZED_CONTROLLER" "$OLD_PATCHER_SHA256" "$NEW_PATCHER_SHA256" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1]);old=sys.argv[2];new=sys.argv[3]
text=path.read_text()
if text.count(old)!=1:
    raise SystemExit('RECEIPT017_PATCHER_CHECKSUM_BINDING_COUNT_INVALID')
text=text.replace(old,new,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED_CONTROLLER"
exec bash "$MATERIALIZED_CONTROLLER"
