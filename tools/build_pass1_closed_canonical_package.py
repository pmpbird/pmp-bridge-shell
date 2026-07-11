#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, io, json, shutil, stat, subprocess, tarfile, zipfile
from pathlib import Path, PurePosixPath

SOURCE_COMMIT = "e7ba1b9384303abbbc67d3e9b0522e51bec65493"
PACKAGE_NAME = "CURRENT_USE_THIS_PMP_APP_ORCHESTRATOR_PASS1_CLOSED_CANONICAL_V2.zip"
FIXED_TIME = (2026, 7, 11, 0, 0, 0)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    work = Path('.pass1-closed-package-work')
    if work.exists(): shutil.rmtree(work)
    staging = work / 'staging'
    repo = staging / 'APP_ORCHESTRATOR_REPOSITORY'
    transfer = staging / 'PMP_APP_TRANSFER'
    repo.mkdir(parents=True); transfer.mkdir(parents=True); output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(['git','cat-file','-e',f'{SOURCE_COMMIT}^{{commit}}'],check=True)
    tar_bytes = subprocess.run(['git','archive','--format=tar',SOURCE_COMMIT],check=True,stdout=subprocess.PIPE).stdout
    with tarfile.open(fileobj=io.BytesIO(tar_bytes),mode='r:') as tf:
        for member in tf.getmembers():
            p=PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts: raise RuntimeError(f'unsafe archive path: {member.name}')
        tf.extractall(repo)

    receipt = repo / 'audit/pass1-final-closure-receipt.json'
    if not receipt.is_file(): raise RuntimeError('Pass 1 closure receipt missing from source commit')
    receipt_obj=json.loads(receipt.read_text())
    if receipt_obj['status']!='PASS1_FORMALLY_CLOSED_AT_EXERCISED_SCOPE': raise RuntimeError('Pass 1 receipt is not closed')
    if receipt_obj['phase_and_pass']['pass2_started'] is not False: raise RuntimeError('Pass 2 state is wrong')
    shutil.copy2(receipt, transfer / 'PASS1_FINAL_CLOSURE_RECEIPT.json')

    (transfer/'00_READ_FIRST.md').write_text(
      '# PMP App / App Orchestrator — Pass 1 Closed Canonical Package\n\n'
      f'This ZIP is frozen from exact main commit `{SOURCE_COMMIT}`.\n\n'
      '- Pass 1: formally closed at exercised scope\n'
      '- Pass 2: not started\n'
      '- A-001: integrated, 212/212 identities, zero unresolved\n'
      '- A-002: 41/41 final live matrix\n'
      '- A-003: 21/21 repository and 47/47 adversarial browser\n'
      '- Crosswalk Router: separate future-integration project, not included\n\n'
      'Every later App Orchestrator move must update the current canonical ZIP and rerun package verification.\n',
      encoding='utf-8')

    metadata={
      'SOURCE_IDENTITY.json':{
        'type':'PMP_APP_ORCHESTRATOR_SOURCE_IDENTITY_V2','repository':'pmpbird/pmp-bridge-shell',
        'branch':'main','source_commit':SOURCE_COMMIT,'source_mode':'exact_git_archive',
        'closure_receipt':'audit/pass1-final-closure-receipt.json'},
      'PASS_AND_PHASE_LEDGER.json':{
        'type':'PMP_APP_ORCHESTRATOR_PASS_AND_PHASE_LEDGER_V2',
        'overall_project':{'pass':'Pass 1','phase':'Final closure','status':'FORMALLY_CLOSED_AT_EXERCISED_SCOPE'},
        'completed':[{'repair':'A-001','status':'COMPLETE_MERGED_FINAL_VERIFIED'},
                     {'repair':'A-002','status':'COMPLETE_MERGED_FINAL_STABLE_VERIFIED'},
                     {'repair':'A-003','status':'COMPLETE_MERGED_FINAL_STABLE_VERIFIED'},
                     {'delivery':'PR #38 and PR #40','status':'COMPLETE'},
                     {'closure':'PR #43','status':'COMPLETE_MERGED'}],
        'current':{'pass':'Pass 1','status':'CLOSED'},
        'next':{'pass':'Pass 2','status':'NOT_STARTED'}},
      'PROJECT_BOUNDARY.json':{
        'type':'PMP_APP_ORCHESTRATOR_PROJECT_BOUNDARY_V2','included_project':'PMP App / App Orchestrator',
        'excluded_project':'Crosswalk Router','crosswalk_router_zip_used':False,
        'crosswalk_router_dependency_created':False},
      'CANONICAL_PACKAGE_RULE.json':{
        'type':'PMP_APP_ORCHESTRATOR_CANONICAL_PACKAGE_RULE_V2',
        'rule':'Every completed App Orchestrator work move must be written into the current canonical ZIP and followed by ZIP integrity verification before the move is complete.',
        'canonical_filename':PACKAGE_NAME,'base_source_commit':SOURCE_COMMIT},
      'PASS1_CLOSURE_STATUS.json':{
        'type':'PMP_APP_ORCHESTRATOR_PASS1_CLOSURE_STATUS_V2','overall_pass':'Pass 1',
        'status':'FORMALLY_CLOSED_AT_EXERCISED_SCOPE','pass2_started':False,
        'closure_receipt_id':receipt_obj['receipt_id'],'closure_receipt_sha256':receipt_obj['receipt_sha256'],
        'next_boundary':'Select and authorize Pass 2 before performing Pass 2 work.'}
    }
    for name,obj in metadata.items(): write_json(transfer/name,obj)

    verifier = '''#!/usr/bin/env python3
import hashlib,json,sys,zipfile
from pathlib import PurePosixPath
p=sys.argv[1]; errors=[]
def h(b): return hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(p) as z:
 n=z.namelist()
 if len(n)!=len(set(n)): errors.append('duplicate names')
 for x in n:
  q=PurePosixPath(x)
  if q.is_absolute() or '..' in q.parts: errors.append('unsafe '+x)
 m=json.loads(z.read('PMP_APP_TRANSFER/PACKAGE_MANIFEST.json'))
 for r in m['files']:
  if r['path'] not in n or h(z.read(r['path']))!=r['sha256']: errors.append('manifest '+r['path'])
 for line in z.read('PMP_APP_TRANSFER/SHA256SUMS.txt').decode().splitlines():
  d,x=line.split('  ',1)
  if x not in n or h(z.read(x))!=d: errors.append('checksum '+x)
 receipt=json.loads(z.read('PMP_APP_TRANSFER/PASS1_FINAL_CLOSURE_RECEIPT.json'))
 if receipt['status']!='PASS1_FORMALLY_CLOSED_AT_EXERCISED_SCOPE': errors.append('receipt status')
 if receipt['phase_and_pass']['pass2_started'] is not False: errors.append('pass2 state')
 if any(x.lower().endswith('.zip') and 'crosswalk' in x.lower() for x in n): errors.append('crosswalk contamination')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors,'checks_failed':len(errors)},indent=2,sort_keys=True))
raise SystemExit(0 if not errors else 1)
'''
    (transfer/'verify_package.py').write_text(verifier,encoding='utf-8')

    payload=[]
    for f in sorted(p for p in staging.rglob('*') if p.is_file()):
        rel=f.relative_to(staging).as_posix()
        if rel in {'PMP_APP_TRANSFER/PACKAGE_MANIFEST.json','PMP_APP_TRANSFER/SHA256SUMS.txt'}: continue
        b=f.read_bytes(); payload.append({'path':rel,'bytes':len(b),'sha256':digest(b)})
    write_json(transfer/'PACKAGE_MANIFEST.json',{'type':'PMP_APP_ORCHESTRATOR_CLOSED_CANONICAL_MANIFEST_V2',
      'package':PACKAGE_NAME,'source_commit':SOURCE_COMMIT,
      'manifest_rule':'Manifest and checksum files exclude recursive self-reference.','files':payload})
    sums=[]
    for f in sorted(p for p in staging.rglob('*') if p.is_file() and p!=transfer/'SHA256SUMS.txt'):
        sums.append(f'{digest(f.read_bytes())}  {f.relative_to(staging).as_posix()}')
    (transfer/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n',encoding='utf-8')

    package=output_dir/PACKAGE_NAME
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(p for p in staging.rglob('*') if p.is_file()):
            rel=f.relative_to(staging).as_posix(); info=zipfile.ZipInfo(rel,FIXED_TIME)
            info.compress_type=zipfile.ZIP_DEFLATED; info.create_system=3
            info.external_attr=(stat.S_IFREG | (0o755 if f.name=='verify_package.py' else 0o644))<<16
            z.writestr(info,f.read_bytes())
    verification=subprocess.run(['python3',str(transfer/'verify_package.py'),str(package)],check=True,text=True,capture_output=True).stdout
    (output_dir/'package-verification.json').write_text(verification,encoding='utf-8')
    package_sha=digest(package.read_bytes())
    (output_dir/f'{PACKAGE_NAME}.sha256').write_text(f'{package_sha}  {PACKAGE_NAME}\n',encoding='utf-8')
    with zipfile.ZipFile(package) as z: names=z.namelist()
    report={'type':'PMP_APP_ORCHESTRATOR_PASS1_CLOSED_PACKAGE_BUILD_REPORT_V2','status':'PASS',
      'overall_project_pass':'Pass 1','pass1_status':'FORMALLY_CLOSED_AT_EXERCISED_SCOPE',
      'pass2_started':False,'package':PACKAGE_NAME,'package_sha256':package_sha,
      'package_bytes':package.stat().st_size,'member_count':len(names),
      'unique_member_names':len(names)==len(set(names)),'source_commit':SOURCE_COMMIT,
      'crosswalk_router_archive_included':False}
    write_json(output_dir/'package-build-report.json',report)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,default=Path('dist'))
    print(json.dumps(build(ap.parse_args().output_dir),indent=2,sort_keys=True))
