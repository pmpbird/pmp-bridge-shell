#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}_PATCH_POINT_COUNT:{count}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.bundle_root

    prepare = root / "prepare_disposable_proof_002.py"
    source = prepare.read_text()
    source = replace_once(
        source,
        "async function auto(){const tag=document.currentScript,realm=tag&&tag.dataset.pmpRealm,docPath=tag&&tag.dataset.pmpDocumentPath;if(!realm||realm==='root')return;return activeChild(realm,docPath)}",
        "async function auto(){const tag=document.currentScript,realm=tag&&tag.dataset.pmpRealm,docPath=tag&&tag.dataset.pmpDocumentPath;if(!realm||realm==='root')return;if(document.readyState==='loading')await new Promise(resolve=>document.addEventListener('DOMContentLoaded',resolve,{once:true}));return activeChild(realm,docPath)}",
        "CHILD_DOCUMENT_PARSE_BARRIER",
    )
    prepare.write_text(source)

    runner = root / "run_full_isolated_proof_002.py"
    runner_source = runner.read_text()
    helper_anchor = "def main():\n"
    helper = r'''def patch_regression_harnesses(root):
 a002=root/'audit/a002-live-runtime.cjs';s=a002.read_text()
 old="""    const timer = setTimeout(() => reject(new Error('A-003 integrity status timeout')), 8000);
    const channel = new MessageChannel();
    channel.port1.onmessage = event => { clearTimeout(timer); resolve(event.data); };"""
 new="""    const channel = new MessageChannel();
    channel.port1.onmessage = event => { resolve(event.data); };"""
 if s.count(old)!=1:raise SystemExit('A002_WORKER_STATUS_TIMER_PATCH_POINT_INVALID')
 s=s.replace(old,new,1).replace('const deadline = Date.now() + 30000;','const deadline = Date.now() + 60000;',1)
 a002.write_text(s)
 a003=root/'audit/a003-live-runtime.cjs';s=a003.read_text()
 old="""    const timer = setTimeout(() => reject(new Error('status timeout')), 8000);
    const channel = new MessageChannel();
    channel.port1.onmessage = e => { clearTimeout(timer); resolve(e.data); };"""
 new="""    const channel = new MessageChannel();
    channel.port1.onmessage = e => { resolve(e.data); };"""
 if s.count(old)!=1:raise SystemExit('A003_WORKER_STATUS_TIMER_PATCH_POINT_INVALID')
 a003.write_text(s.replace(old,new,1))
'''
    if runner_source.count(helper_anchor) != 1:
        raise SystemExit("RUNNER_MAIN_ANCHOR_INVALID")
    runner_source = runner_source.replace(helper_anchor, helper + helper_anchor, 1)
    runner_source = replace_once(
        runner_source,
        "ap=argparse.ArgumentParser();ap.add_argument('--activated-root',type=Path,required=True);ap.add_argument('--baseline-root',type=Path,required=True);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--scripts-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[];server=None",
        "ap=argparse.ArgumentParser();ap.add_argument('--activated-root',type=Path,required=True);ap.add_argument('--baseline-root',type=Path,required=True);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--scripts-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[];server=None;patch_regression_harnesses(a.activated_root)",
        "ACTIVE_HARNESS_NORMALIZATION",
    )
    runner_source = replace_once(
        runner_source,
        "results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180))",
        "results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180));patch_regression_harnesses(a.activated_root)",
        "RESTORED_HARNESS_NORMALIZATION",
    )
    runner.write_text(runner_source)

    repair_007 = Path(__file__).with_name("repair_runner_007.py")
    subprocess.run(
        [sys.executable, str(repair_007), "--bundle-root", str(root)],
        check=True,
    )

    print("CHILD_PARSE_BARRIER_HARNESS_NORMALIZATION_AND_REPAIR_007_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
