#!/usr/bin/env bash
set -euo pipefail
ORIGINAL_CONTROLLER_BLOB='cff2fffc59680e667abb53b0c18f508f6561e9eb'
OLD_PATCHER_SHA256='efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'
NEW_PATCHER_SHA256='d4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
OLD_MANIFEST_SHA256='72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619'
NEW_MANIFEST_SHA256='d53dc787298e8fec5f00227b680645dffd25774913ba34461d4969df6bf2b803'
OLD_CONTROLLER='repair_runner_009_controller002.py'
NEW_CONTROLLER='repair_runner_009_controller002_policycompat_022.py'
MATERIALIZED_CONTROLLER="${TMPDIR:-/tmp}/p2c-rerun008-controller-main-receipt024-$$.sh"
trap 'rm -f "$MATERIALIZED_CONTROLLER"' EXIT

git cat-file blob "$ORIGINAL_CONTROLLER_BLOB" > "$MATERIALIZED_CONTROLLER"
python3 - "$MATERIALIZED_CONTROLLER" "$OLD_PATCHER_SHA256" "$NEW_PATCHER_SHA256" "$OLD_MANIFEST_SHA256" "$NEW_MANIFEST_SHA256" "$OLD_CONTROLLER" "$NEW_CONTROLLER" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
old_patcher,new_patcher,old_manifest,new_manifest,old_controller,new_controller=sys.argv[2:]
text=path.read_text()
for old,label in ((old_patcher,'PATCHER_SHA'),(old_manifest,'MANIFEST_SHA'),(old_controller,'CONTROLLER_PATH')):
    if text.count(old)!=1:
        raise SystemExit(f'RECEIPT024_{label}_BINDING_COUNT_INVALID:{text.count(old)}')
text=text.replace(old_patcher,new_patcher,1)
text=text.replace(old_manifest,new_manifest,1)
text=text.replace(old_controller,new_controller,1)
path.write_text(text)
PY
bash -n "$MATERIALIZED_CONTROLLER"
exec bash "$MATERIALIZED_CONTROLLER"
