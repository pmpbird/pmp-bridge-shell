#!/usr/bin/env bash
set -uo pipefail
mkdir -p "$EVIDENCE_DIR"
python3 - <<'PY'
import hashlib,json,os,pathlib,shlex,subprocess,sys,tarfile

evidence=pathlib.Path(os.environ['EVIDENCE_DIR'])
diag=evidence/'receipt016-controller-diagnostic.json'
deps=pathlib.Path(os.environ['DEPS_DIR'])
bundle_dir=pathlib.Path(os.environ['BUNDLE_DIR'])
bundle_tar=pathlib.Path(os.environ['BUNDLE_TAR'])
patcher=deps/'repair-continuation-003/apply_prepare_repair_003.py'
expected_patcher='1b9ce74b523e19809aa2b9f170826f9fb60e31adf8e34f2a247fe1ddb667bd21'

def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def write(status,line,command,expected,actual,affected,extra=None):
    out={
      'type':'PMP_P2C_RECEIPT016_PATCHPOINT_REPAIR_DIAGNOSTIC_V1',
      'status':status,
      'failed_line':line,
      'failed_command':command,
      'expected_value':str(expected),
      'actual_value':str(actual),
      'affected_file':str(affected),
      'diagnostic_scope':'FORMER_LINE_82_ONLY_PRE_WORKTREE',
      'former_line_82_succeeded':status=='PASS',
      'git_worktree_add_executed':False,
      'playwright_or_chromium_install_executed':False,
      'disposable_copy_preparation_executed':False,
      'browser_proof_executed':False,
      'proof_run_count_executed':0,
      'production_files_modified':False,
      'current_map_modified':False,
      'persisted_data_modified':False,
      'receipts_modified':False,
      'authorization_bindings_modified':False,
    }
    if extra: out.update(extra)
    diag.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

def fail(line,command,expected,actual,affected,extra=None):
    write('FAIL',line,command,expected,actual,affected,extra)
    raise SystemExit(1)

actual_patcher=sha(patcher)
if actual_patcher!=expected_patcher:
    fail(60,f'sha256sum {patcher}',expected_patcher,actual_patcher,patcher)
for p in (bundle_dir,bundle_tar):
    if p.is_dir(): subprocess.run(['rm','-rf',str(p)],check=True)
    elif p.exists(): p.unlink()
bundle_dir.mkdir(parents=True)
part062=pathlib.Path('/tmp/p2c-part06-2.bin')
p=subprocess.run(['bash','-lc',f"tr -d '\\r\\n' < {shlex.quote(str(deps/'bundle/part06_2.b64'))} | base64 -d > {part062}"],text=True,capture_output=True)
if p.returncode: fail(54,'decode bundle part06_2','exit_code=0',f'exit_code={p.returncode}',deps/'bundle/part06_2.b64',{'stderr':p.stderr})
p=subprocess.run(['bash','-lc',f"cat {deps/'bundle/part00.b64'} {deps/'bundle/part01.b64'} {deps/'bundle/part02.b64'} {deps/'bundle/part03.b64'} | tr -d '\\r\\n' | base64 -d > {bundle_tar}"],text=True,capture_output=True)
if p.returncode: fail(56,'decode base bundle','exit_code=0',f'exit_code={p.returncode}',bundle_tar,{'stderr':p.stderr})
with bundle_tar.open('ab') as out:
    for part in [deps/'bundle/part04_0.bin',deps/'bundle/part04_1.bin',deps/'bundle/part04_2.bin',deps/'bundle/part05_0.bin',deps/'bundle/part05_1.bin',deps/'bundle/part06_0.bin',deps/'bundle/part06_1.bin',part062]:
        out.write(part.read_bytes())
if bundle_tar.stat().st_size!=61478: fail(58,f'wc -c {bundle_tar}',61478,bundle_tar.stat().st_size,bundle_tar)
expected_tar='a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500'
if sha(bundle_tar)!=expected_tar: fail(59,f'sha256sum {bundle_tar}',expected_tar,sha(bundle_tar),bundle_tar)
with tarfile.open(bundle_tar,'r:gz') as tf: tf.extractall(bundle_dir)
target=bundle_dir/'prepare_disposable_proof_002.py'
cmd=['python3',str(patcher),'--path',str(target)]
p=subprocess.run(cmd,text=True,capture_output=True)
(evidence/'line-82.stdout.log').write_text(p.stdout)
(evidence/'line-82.stderr.log').write_text(p.stderr)
if p.returncode:
    fail(82,' '.join(shlex.quote(x) for x in cmd),'exit_code=0',f'exit_code={p.returncode}',target,{'stdout':p.stdout,'stderr':p.stderr})
write('PASS',82,' '.join(shlex.quote(x) for x in cmd),'exit_code=0','exit_code=0',target,{'repaired_patcher_sha256':actual_patcher,'hard_stop':'BEFORE_GIT_WORKTREE_ADD'})
print('RECEIPT016_FORMER_LINE_82_PASS')
PY
exit $?
