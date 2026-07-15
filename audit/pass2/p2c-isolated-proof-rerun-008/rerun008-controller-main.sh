#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$EVIDENCE_DIR"
python3 - <<'PY'
import hashlib,json,os,pathlib,shlex,subprocess,tarfile

evidence=pathlib.Path(os.environ['EVIDENCE_DIR'])
deps=pathlib.Path(os.environ['DEPS_DIR'])
bundle_dir=pathlib.Path(os.environ['BUNDLE_DIR'])
bundle_tar=pathlib.Path(os.environ['BUNDLE_TAR'])

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
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
lines=[]
for number,line in enumerate(target.read_text().splitlines(),1):
    if any(token in line for token in ('patch_','activated','scripts','def main','root_receipt')):
        lines.append({'line':number,'text':line})
out={
 'type':'PMP_P2C_RECEIPT016_RECONSTRUCTED_PATCH_CALL_SHAPE_V1',
 'status':'PASS',
 'target':str(target),
 'target_sha256':sha(target),
 'matching_lines':lines,
 'git_worktree_add_executed':False,
 'playwright_or_chromium_install_executed':False,
 'disposable_copy_preparation_executed':False,
 'browser_proof_executed':False,
 'proof_run_count_executed':0
}
(evidence/'receipt016-controller-diagnostic.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(evidence/'reconstructed-patch-call-shape.txt').write_text('\n'.join(f"{x['line']}: {x['text']}" for x in lines)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
PY
