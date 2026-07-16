#!/usr/bin/env bash
set -euo pipefail
ORIGINAL_CONTROLLER_BLOB='cff2fffc59680e667abb53b0c18f508f6561e9eb'
OLD_PATCHER_SHA256='efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'
NEW_PATCHER_SHA256='d4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
OLD_MANIFEST_SHA256='72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619'
NEW_MANIFEST_SHA256='d53dc787298e8fec5f00227b680645dffd25774913ba34461d4969df6bf2b803'
OLD_CONTROLLER='repair_runner_009_controller002.py'
NEW_CONTROLLER='repair_runner_009_controller002_policycompat_022.py'
OLD_CONTROLLER_SHA256='ad10e91f9f8319747d08f6f882031eae48aee7c9d7813b1a3f63ad5d0e4a72f7'
NEW_CONTROLLER_SHA256='1a553e229078239f0d17e25ca813788b4b25aa1d33fd511cdc179f1a6ebecb13'
OLD_ALLOWLIST="allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','audit/a002-live-runtime.cjs'}"
NEW_ALLOWLIST="allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','.github/workflows/pass2-p2c-exhaustive-preproof-discovery.yml','audit/a002-live-runtime.cjs'}"
MATERIALIZED_CONTROLLER="${TMPDIR:-/tmp}/p2c-rerun008-controller-main-receipt024-$$.sh"
trap 'rm -f "$MATERIALIZED_CONTROLLER"' EXIT

git cat-file blob "$ORIGINAL_CONTROLLER_BLOB" > "$MATERIALIZED_CONTROLLER"
python3 - "$MATERIALIZED_CONTROLLER" "$OLD_PATCHER_SHA256" "$NEW_PATCHER_SHA256" "$OLD_MANIFEST_SHA256" "$NEW_MANIFEST_SHA256" "$OLD_CONTROLLER" "$NEW_CONTROLLER" "$OLD_CONTROLLER_SHA256" "$NEW_CONTROLLER_SHA256" "$OLD_ALLOWLIST" "$NEW_ALLOWLIST" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
old_patcher,new_patcher,old_manifest,new_manifest,old_controller,new_controller,old_controller_sha,new_controller_sha,old_allowlist,new_allowlist=sys.argv[2:]
text=path.read_text()
old_install='''rm -rf "$NODE_HOME"; mkdir -p "$NODE_HOME"; cd "$NODE_HOME"
npm init -y >/dev/null
npm install --no-save playwright@1.55.0
"$NODE_HOME/node_modules/.bin/playwright" install --with-deps chromium'''
new_install='''rm -rf "$NODE_HOME"; mkdir -p "$NODE_HOME"
(
  cd "$NODE_HOME"
  npm init -y >/dev/null
  npm install --no-save playwright@1.55.0
  "$NODE_HOME/node_modules/.bin/playwright" install --with-deps chromium
)'''
expected_counts={old_patcher:1,old_manifest:1,old_controller:4,old_controller_sha:1,old_allowlist:1,old_install:1}
labels={old_patcher:'PATCHER_SHA',old_manifest:'MANIFEST_SHA',old_controller:'CONTROLLER_PATH',old_controller_sha:'CONTROLLER_SHA',old_allowlist:'INTERNAL_ALLOWLIST',old_install:'BROWSER_INSTALL_CWD'}
for old,expected in expected_counts.items():
    actual=text.count(old)
    if actual!=expected:raise SystemExit(f'RECEIPT024_{labels[old]}_BINDING_COUNT_INVALID:{actual}:EXPECTED:{expected}')
text=text.replace(old_patcher,new_patcher,1)
text=text.replace(old_manifest,new_manifest,1)
text=text.replace(old_controller,new_controller)
text=text.replace(old_controller_sha,new_controller_sha,1)
text=text.replace(old_allowlist,new_allowlist,1)
text=text.replace(old_install,new_install,1)
if text.count(new_controller)!=4:raise SystemExit(f'RECEIPT024_NEW_CONTROLLER_PATH_BINDING_COUNT_INVALID:{text.count(new_controller)}')
if text.count(new_controller_sha)!=1:raise SystemExit(f'RECEIPT024_NEW_CONTROLLER_SHA_BINDING_COUNT_INVALID:{text.count(new_controller_sha)}')
if text.count(new_allowlist)!=1:raise SystemExit(f'RECEIPT024_NEW_INTERNAL_ALLOWLIST_COUNT_INVALID:{text.count(new_allowlist)}')
if text.count(new_install)!=1:raise SystemExit(f'RECEIPT024_NEW_BROWSER_INSTALL_CWD_COUNT_INVALID:{text.count(new_install)}')
path.write_text(text)
PY
if [ "${P2C_STOP_BEFORE_PREPARATION:-0}" = "1" ]; then
  python3 - "$MATERIALIZED_CONTROLLER" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
marker='echo "=== Prepare explicitly authorized disposable active copy ==="'
if text.count(marker)!=1:raise SystemExit(f'PREPARATION_MARKER_COUNT_INVALID:{text.count(marker)}')
prefix=text.split(marker,1)[0]
path.write_text(prefix+"printf '%s\\n' 'P2C_BROWSER_SETUP_HARD_STOP_BEFORE_PREPARATION'\n")
PY
fi
bash -n "$MATERIALIZED_CONTROLLER"
exec bash "$MATERIALIZED_CONTROLLER"
