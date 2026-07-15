#!/usr/bin/env bash
set -uo pipefail
mkdir -p "$EVIDENCE_DIR"
python3 - <<'PY'
import hashlib,json,os,pathlib,shlex,subprocess,sys,tarfile

evidence=pathlib.Path(os.environ['EVIDENCE_DIR'])
diag=evidence/'receipt016-controller-diagnostic.json'
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
deps=pathlib.Path(os.environ['DEPS_DIR'])
bundle_dir=pathlib.Path(os.environ['BUNDLE_DIR'])
bundle_tar=pathlib.Path(os.environ['BUNDLE_TAR'])
normalized=pathlib.Path(os.environ['NORMALIZED_ROOT'])

def write(status,line,command,expected,actual,affected,extra=None):
    out={
      'type':'PMP_P2C_RECEIPT016_CONTROLLER_DIAGNOSTIC_V1',
      'status':status,
      'failed_line':line,
      'failed_command':command,
      'expected_value':str(expected),
      'actual_value':str(actual),
      'affected_file':str(affected),
      'diagnostic_scope':'PRE_WORKTREE_VERIFICATION_AND_RECONSTRUCTION_ONLY',
      'git_worktree_add_executed':False,
      'playwright_or_chromium_install_executed':False,
      'disposable_copy_preparation_executed':False,
      'browser_proof_executed':False,
      'proof_run_count_executed':0,
      'receipts_modified':False,
      'authorization_bindings_modified':False,
      'production_files_modified':False,
      'current_map_modified':False,
      'persisted_data_modified':False,
    }
    if extra: out.update(extra)
    diag.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

def fail(line,command,expected,actual,affected,extra=None):
    write('FAIL',line,command,expected,actual,affected,extra)
    print(f'RECEIPT016_DIAGNOSTIC_FAILURE line={line} command={command!r} expected={expected!r} actual={actual!r} affected={str(affected)!r}',file=sys.stderr)
    raise SystemExit(1)

def check(line,command,actual,expected,affected):
    if actual != expected: fail(line,command,expected,actual,affected)

def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def blob(path): return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
def run(line,cmd,affected):
    p=subprocess.run(cmd,text=True,capture_output=True)
    (evidence/f'line-{line}.stdout.log').write_text(p.stdout)
    (evidence/f'line-{line}.stderr.log').write_text(p.stderr)
    if p.returncode:
        fail(line,' '.join(shlex.quote(str(x)) for x in cmd),'exit_code=0',f'exit_code={p.returncode}',affected,{'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]})
    return p

base=os.environ['BASE_SHA']
changed=set(subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','audit/a002-live-runtime.cjs'}
extras=sorted(p for p in changed if p not in allowed and not p.startswith(str(root)+'/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/'))
check(24,'controller changed-path allowlist',extras,[],'.git diff')
receipt_path=root/'P2C_EXACTLY_ONE_REFRESHED_FROZEN_CAPSULE_BROWSER_PROOF_AUTHORIZATION_RECEIPT_008.json'
receipt=json.loads(receipt_path.read_text())
directive_path=root/'P2C_ISOLATED_PROOF_RERUN_EXECUTION_DIRECTIVE_008.json'
directive=json.loads(directive_path.read_text())
scope_path=root/'scope-lock-rerun-008.json'; scope=json.loads(scope_path.read_text())
manifest_path=root/'EXECUTABLE_RERUN_MANIFEST_007.json'; manifest=json.loads(manifest_path.read_text())
check(31,'receipt008 sha256',sha(receipt_path),'37a439de5a4f8320d1cdea3e692be592c14dfc639d1e8b6d6f42ec11d3cd159a',receipt_path)
check(32,'receipt008 authorization tuple',(receipt.get('authorized'),receipt.get('status'),receipt.get('authorization_consumed')),(True,'AUTHORIZED_UNCONSUMED',False),receipt_path)
check(33,'receipt008 run-count tuple',(receipt.get('proof_run_count_authorized'),receipt.get('proof_run_count_executed_under_this_receipt')),(1,0),receipt_path)
check(34,'receipt008 authorization scope',receipt.get('authorization_scope'),'EXACTLY_ONE_FUTURE_CHECKSUM_BOUND_DISPOSABLE_COPY_ISOLATED_BROWSER_PROOF_USING_REFRESHED_FROZEN_CAPSULE_CONTROLLER006_ONLY',receipt_path)
check(35,'source commit receipt/manifest',receipt['refreshed_frozen_capsule']['source_repository_commit'],manifest['source_repository_commit'],receipt_path)
check(36,'receipt008 execution flags',(receipt.get('workflow_execution_authorized'),receipt.get('browser_proof_execution_authorized')),(False,False),receipt_path)
check(37,'separate authorization required',receipt.get('separate_execution_authorization_required'),True,receipt_path)
check(38,'directive authorization tuple',(directive.get('authorized'),directive.get('workflow_execution_authorized'),directive.get('browser_proof_execution_authorized'),directive.get('authorization_receipt_sha256')),(True,True,True,sha(receipt_path)),directive_path)
check(39,'directive run-count tuple',(directive.get('proof_run_count_to_execute'),directive.get('proof_run_count_previously_executed_under_receipt')),(1,0),directive_path)
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    check(40,f'forbidden flag {key}',(receipt.get(key),directive.get(key),scope.get(key)),(False,False,False),key)
check(42,'scope event tuple',(scope.get('event'),scope.get('required_run_attempt')),('pull_request.opened',1),scope_path)
check(43,'scope workflow tuple',(scope.get('workflow_dispatch_allowed'),scope.get('workflow_filename')),(False,manifest['workflow_filename']),scope_path)
check(44,'source commit directive/scope',(manifest['source_repository_commit'],directive['source_repository_commit'],scope['source_repository_commit']),(manifest['source_repository_commit'],)*3,manifest_path)

for p in (bundle_dir,bundle_tar,normalized):
    if p.is_dir(): subprocess.run(['rm','-rf',str(p)],check=True)
    elif p.exists(): p.unlink()
bundle_dir.mkdir(parents=True); normalized.mkdir(parents=True)
checks=[
(52,deps/'bundle/part06_0.bin','13435f1fcf4aa33c2df7d719944bc986fea8ebe45b7568766a3e086a56fa94ae'),
(53,deps/'bundle/part06_1.bin','917bc7936f8d9e5cbefbccbc7c4ff75f97156fada545d26c82e8f149c3feb7f8'),
(60,deps/'repair-continuation-003/apply_prepare_repair_003.py','efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'),
(61,deps/'repair_runner_003.py','ebb6f7c0b1b5d41eb795e48706cbfd00a66117653e03a8bce7248a5f63b5c1ca'),
(62,deps/'repair_runner_005.py','c7d327f8e7133fd1d6a2e2c0958d29f33844898ebba468d2266e78464982e6a8'),
(63,deps/'repair_runner_006.py','f88802507841710193dcecb3abd62934488fef5ce1e347f4689bd2d5aa9cb30f'),
(64,deps/'repair_runner_007.py','e47b2530a2ab4180b255d6c1d70cbc314e72564cb4fa35ab2229c824d81384ee'),
(65,deps/'repair_runner_008.py','9de909e03b5a691d4215c785f36ad64ce38e844c7540b9f5bdc65f4a1b671972'),
(66,deps/'repair_runner_009_controller002.py','ad10e91f9f8319747d08f6f882031eae48aee7c9d7813b1a3f63ad5d0e4a72f7'),
(67,deps/'repair009_transport_fidelity_controller003.py','4adec534bfbb17e0fa11d81918b078a73f44c7e16f38fdaad747b12b3f6199e7'),
(68,deps/'transpile_async_sources.part00.b64','c2febd1a52ac905aab8af36d6995694eaf4719f886fe228860c44e827e268be3'),
(69,deps/'transpile_async_sources.part01.b64','07b68e774f7d8534a70ba1e0fdafbb6b1df109482462e86cb343c4ad4ac786a1'),
(70,deps/'transpile_async_sources.part02.b64','9f0be30991386eb2e75d03525cd18f54a16d2b682b4ae73d23c0de15ff90ffde'),
(71,deps/'repair009-normalized-source-manifest-002.json','72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619')]
for line,path,expected in checks: check(line,f'sha256sum {path}',sha(path),expected,path)
part062=pathlib.Path('/tmp/p2c-part06-2.bin')
run(54,['bash','-lc',f"tr -d '\\r\\n' < {shlex.quote(str(deps/'bundle/part06_2.b64'))} | base64 -d > {part062}"],deps/'bundle/part06_2.b64')
check(55,f'sha256sum {part062}',sha(part062),'250e8719e8e5184206464906a35e082a1e83d1dcfe717276fdfdba175c08fdfe',part062)
run(56,['bash','-lc',f"cat {deps/'bundle/part00.b64'} {deps/'bundle/part01.b64'} {deps/'bundle/part02.b64'} {deps/'bundle/part03.b64'} | tr -d '\\r\\n' | base64 -d > {bundle_tar}"],bundle_tar)
with bundle_tar.open('ab') as out:
    for p in [deps/'bundle/part04_0.bin',deps/'bundle/part04_1.bin',deps/'bundle/part04_2.bin',deps/'bundle/part05_0.bin',deps/'bundle/part05_1.bin',deps/'bundle/part06_0.bin',deps/'bundle/part06_1.bin',part062]: out.write(p.read_bytes())
check(58,f'wc -c {bundle_tar}',bundle_tar.stat().st_size,61478,bundle_tar)
check(59,f'sha256sum {bundle_tar}',sha(bundle_tar),'a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500',bundle_tar)
candidate=root/'pass2-p2c-isolated-proof-rerun-008.workflow-candidate.yml.txt'
check(72,'test -s workflow candidate',candidate.exists() and candidate.stat().st_size>0,True,candidate)
transport=pathlib.Path('/tmp/p2c-transformer-transport-006'); subprocess.run(['rm','-rf',str(transport)]); transport.mkdir()
for p in deps.glob('transpile_async_sources.part*.b64'): (transport/p.name).write_bytes(p.read_bytes())
run(75,['python3',str(deps/'repair009_transport_fidelity_controller003.py'),str(transport)],deps/'repair009_transport_fidelity_controller003.py')
transformer=transport/'transpile_async_sources.decoded.js'
check(77,f'sha256sum {transformer}',sha(transformer),'c5ffb899637aa45feb64b604dca426503f99fc9a34f05a1c83a12d0cfef3d0dd',transformer)
check(78,f'git hash-object {transformer}',blob(transformer),'06a33bfd0bed8cc4b914b519bab606ddcd719cd1',transformer)
try:
    with tarfile.open(bundle_tar,'r:gz') as tf: tf.extractall(bundle_dir)
except Exception as exc: fail(79,f'tar -xzf {bundle_tar} -C {bundle_dir}','successful extraction',repr(exc),bundle_tar)
run(81,['python3','-m','py_compile',str(deps/'repair-continuation-003/apply_prepare_repair_003.py'),str(deps/'repair_runner_003.py'),str(deps/'repair_runner_005.py'),str(deps/'repair_runner_006.py'),str(deps/'repair_runner_007.py'),str(deps/'repair_runner_008.py'),str(deps/'repair_runner_009_controller002.py')],deps)
run(82,['python3',str(deps/'repair-continuation-003/apply_prepare_repair_003.py'),'--path',str(bundle_dir/'prepare_disposable_proof_002.py')],bundle_dir/'prepare_disposable_proof_002.py')
run(83,['python3',str(deps/'repair_runner_003.py'),'--bundle-root',str(bundle_dir)],deps/'repair_runner_003.py')
run(84,['python3',str(deps/'repair_runner_005.py'),'--bundle-root',str(bundle_dir)],deps/'repair_runner_005.py')
run(85,['python3',str(deps/'repair_runner_008.py'),'--bundle-root',str(bundle_dir)],deps/'repair_runner_008.py')
write('PASS',86,'diagnostic hard stop before git worktree add','stop before worktree creation','stopped before worktree creation','audit/pass2/p2c-isolated-proof-rerun-008/rerun008-controller-main.sh')
print('RECEIPT016_DIAGNOSTIC_PRE_WORKTREE_PASS')
PY
exit $?
