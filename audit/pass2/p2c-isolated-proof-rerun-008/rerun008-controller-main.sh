#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$EVIDENCE_DIR"
python3 - <<'PY'
import hashlib,json,os,pathlib,shlex,subprocess,tarfile

evidence=pathlib.Path(os.environ['EVIDENCE_DIR'])
deps=pathlib.Path(os.environ['DEPS_DIR'])
bundle_dir=pathlib.Path(os.environ['BUNDLE_DIR'])
bundle_tar=pathlib.Path(os.environ['BUNDLE_TAR'])
patcher=deps/'repair-continuation-003/apply_prepare_repair_003.py'
expected='d4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(status,actual,stderr=''):
 out={'type':'PMP_P2C_RECEIPT016_PATCHPOINT_REPAIR_CONFIRMATION_V1','status':status,'former_line_82_succeeded':status=='PASS','patcher_path':str(patcher),'patcher_sha256_expected':expected,'patcher_sha256_actual':sha(patcher),'affected_file':str(bundle_dir/'prepare_disposable_proof_002.py'),'command':f'python3 {patcher} --path {bundle_dir}/prepare_disposable_proof_002.py','expected_value':'exit_code=0','actual_value':actual,'stderr':stderr,'hard_stop':'BEFORE_GIT_WORKTREE_ADD','git_worktree_add_executed':False,'playwright_or_chromium_install_executed':False,'disposable_copy_preparation_executed':False,'browser_proof_executed':False,'proof_run_count_executed':0,'production_files_modified':False,'current_map_modified':False,'persisted_data_modified':False,'receipts_modified':False,'authorization_bindings_modified':False}
 (evidence/'receipt016-controller-diagnostic.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

if sha(patcher)!=expected:
 write('FAIL','PATCHER_SHA_MISMATCH');raise SystemExit(1)
for p in (bundle_dir,bundle_tar):
 if p.is_dir(): subprocess.run(['rm','-rf',str(p)],check=True)
 elif p.exists(): p.unlink()
bundle_dir.mkdir(parents=True)
part062=pathlib.Path('/tmp/p2c-part06-2.bin')
subprocess.run(['bash','-lc',f"tr -d '\\r\\n' < {shlex.quote(str(deps/'bundle/part06_2.b64'))} | base64 -d > {part062}"],check=True)
subprocess.run(['bash','-lc',f"cat {deps/'bundle/part00.b64'} {deps/'bundle/part01.b64'} {deps/'bundle/part02.b64'} {deps/'bundle/part03.b64'} | tr -d '\\r\\n' | base64 -d > {bundle_tar}"],check=True)
with bundle_tar.open('ab') as out:
 for part in [deps/'bundle/part04_0.bin',deps/'bundle/part04_1.bin',deps/'bundle/part04_2.bin',deps/'bundle/part05_0.bin',deps/'bundle/part05_1.bin',deps/'bundle/part06_0.bin',deps/'bundle/part06_1.bin',part062]: out.write(part.read_bytes())
assert bundle_tar.stat().st_size==61478
assert sha(bundle_tar)=='a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500'
with tarfile.open(bundle_tar,'r:gz') as tf: tf.extractall(bundle_dir)
target=bundle_dir/'prepare_disposable_proof_002.py'
p=subprocess.run(['python3',str(patcher),'--path',str(target)],text=True,capture_output=True)
(evidence/'line-82.stdout.log').write_text(p.stdout)
(evidence/'line-82.stderr.log').write_text(p.stderr)
if p.returncode:
 write('FAIL',f'exit_code={p.returncode}',p.stderr);raise SystemExit(1)
write('PASS','exit_code=0',p.stderr)
print('RECEIPT016_FORMER_LINE_82_PASS')
PY
