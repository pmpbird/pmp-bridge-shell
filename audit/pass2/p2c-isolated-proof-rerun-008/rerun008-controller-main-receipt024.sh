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
NEW_ALLOWLIST="allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','.github/workflows/pass2-p2c-exhaustive-preproof-discovery.yml','.github/workflows/pass2-p2c-full-rehearsal-equivalence-closure.yml','.github/workflows/pass2-p2c-receipt038-static-preflight.yml','audit/a002-live-runtime.cjs'}"
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
  npm init -y >"$EVIDENCE_DIR/browser-npm-init.log" 2>&1
  npm install --no-save playwright@1.55.0 >"$EVIDENCE_DIR/browser-npm-install.log" 2>&1
  if ! "$NODE_HOME/node_modules/.bin/playwright" install --with-deps chromium >"$EVIDENCE_DIR/browser-install-with-deps.log" 2>&1; then
    "$NODE_HOME/node_modules/.bin/playwright" install chromium >"$EVIDENCE_DIR/browser-install-fallback.log" 2>&1
  fi
  node - <<'JS' >"$EVIDENCE_DIR/browser-launch-smoke.log" 2>&1
const { chromium } = require(process.env.NODE_HOME + '/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  await page.setContent('<title>p2c-browser-ready</title>');
  if (await page.title() !== 'p2c-browser-ready') throw new Error('browser smoke title mismatch');
  console.log(JSON.stringify({status:'PASS',browserVersion:browser.version()}));
  await browser.close();
})().catch(error => { console.error(error && error.stack || String(error)); process.exit(1); });
JS
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
marker='echo "=== Prepare explicitly authorized disposable active copy ==="'
if text.count(marker)!=1:raise SystemExit(f'PREPARATION_MARKER_COUNT_INVALID:{text.count(marker)}')
repair='''python3 - "${SOURCE_COMMIT:?SOURCE_COMMIT_REQUIRED}" "$BUNDLE_DIR" "$EVIDENCE_DIR" "$NORMALIZED_ROOT" <<'PY2'
import json,pathlib,re,sys
source=sys.argv[1]
if not re.fullmatch(r'[0-9a-f]{40}',source):
    raise SystemExit('SOURCE_COMMIT_FORMAT_INVALID')
roots=[pathlib.Path(p) for p in sys.argv[2:]]
changed=[]; observed=[]
def rewrite(node,path):
    count=0
    if isinstance(node,dict):
        for key,value in list(node.items()):
            if key=='source_repository_commit':
                observed.append((str(path),value))
                if value!=source:
                    node[key]=source; count+=1
            else:
                count+=rewrite(value,path)
    elif isinstance(node,list):
        for value in node: count+=rewrite(value,path)
    return count
for root in roots:
    if not root.exists(): continue
    for path in sorted(root.rglob('*.json')):
        try: data=json.loads(path.read_text())
        except Exception: continue
        count=rewrite(data,path)
        if count:
            path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\\n')
            changed.append({'path':str(path),'bindings_repaired':count})
if not changed:
    raise SystemExit('POST_GENERATION_SOURCE_REPOSITORY_COMMIT_BINDING_NOT_FOUND')
remaining=[]
for root in roots:
    if not root.exists(): continue
    for path in sorted(root.rglob('*.json')):
        try: data=json.loads(path.read_text())
        except Exception: continue
        def check(node):
            if isinstance(node,dict):
                for key,value in node.items():
                    if key=='source_repository_commit' and value!=source: remaining.append((str(path),value))
                    else: check(value)
            elif isinstance(node,list):
                for value in node: check(value)
        check(data)
if remaining:
    raise SystemExit(f'POST_GENERATION_SOURCE_REPOSITORY_COMMIT_BINDING_INCOMPLETE:{remaining}')
evidence=pathlib.Path(sys.argv[3]); evidence.mkdir(parents=True,exist_ok=True)
(evidence/'post-generation-source-commit-binding-repair-058.json').write_text(json.dumps({'status':'PASS','source_repository_commit':source,'changed':changed,'observed_binding_count':len(observed)},indent=2,sort_keys=True)+'\\n')
print(f'POST_GENERATION_SOURCE_REPOSITORY_COMMIT_BINDINGS_REPAIRED:{sum(x["bindings_repaired"] for x in changed)}:{source}')
PY2'''
text=text.replace(marker,repair+'\n'+marker,1)
path.write_text(text)
PY
if [ "${P2C_REHEARSAL_SKIP_AUTHORIZATION:-0}" = "1" ]; then
  python3 - "$MATERIALIZED_CONTROLLER" <<'PY'
import pathlib,sys
path=pathlib.Path(sys.argv[1])
text=path.read_text()
marker='echo "=== Reconstruct checksum-bound base runner and apply Repairs 003 through 008 exactly once ==="'
if text.count(marker)!=1:raise SystemExit(f'REHEARSAL_RECONSTRUCTION_MARKER_COUNT_INVALID:{text.count(marker)}')
path.write_text('#!/usr/bin/env bash\nset -euo pipefail\n'+marker+text.split(marker,1)[1])
PY
fi
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
