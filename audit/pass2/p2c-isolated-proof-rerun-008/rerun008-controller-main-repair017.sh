#!/usr/bin/env bash
set -euo pipefail
ORIGINAL_CONTROLLER_BLOB='cff2fffc59680e667abb53b0c18f508f6561e9eb'
OLD_PATCHER_SHA256='efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'
NEW_PATCHER_SHA256='d4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
OLD_MANIFEST_SHA256='72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619'
NEW_MANIFEST_SHA256='fb87f6dfc4a46cc07927b9ba78e1f8ac657eed2d16b4764b63f5ecb8c787e238'
MATERIALIZED_CONTROLLER="${TMPDIR:-/tmp}/p2c-rerun008-controller-main-repair017-$$.sh"
trap 'rm -f "$MATERIALIZED_CONTROLLER"' EXIT

git cat-file blob "$ORIGINAL_CONTROLLER_BLOB" > "$MATERIALIZED_CONTROLLER"
python3 - "$MATERIALIZED_CONTROLLER" "$OLD_PATCHER_SHA256" "$NEW_PATCHER_SHA256" "$OLD_MANIFEST_SHA256" "$NEW_MANIFEST_SHA256" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
old_patcher,new_patcher,old_manifest,new_manifest=sys.argv[2:]
text=path.read_text()
if text.count(old_patcher)!=1:
    raise SystemExit('RECEIPT017_PATCHER_CHECKSUM_BINDING_COUNT_INVALID')
if text.count(old_manifest)!=1:
    raise SystemExit('RECEIPT019_MANIFEST_CHECKSUM_BINDING_COUNT_INVALID')
text=text.replace(old_patcher,new_patcher,1).replace(old_manifest,new_manifest,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED_CONTROLLER"
exec bash "$MATERIALIZED_CONTROLLER"
