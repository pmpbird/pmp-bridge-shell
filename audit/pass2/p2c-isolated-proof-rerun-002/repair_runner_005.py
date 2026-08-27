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

    root_html = root / "after/pmp-app-current.html"
    source = root_html.read_text()
    source = replace_once(
        source,
        "const verifiedResolver=await verifyPath(RESOLVER_PATH,loadedManifest.index);",
        "const verifiedResolver=await verifyPath(RESOLVER_PATH,loadedManifest.index);\n"
        "    const verifiedCurrentMap=await verifyPath('pmp-current-map-v12.json',loadedManifest.index);",
        "ROOT_CURRENT_MAP_PREFETCH",
    )
    source = replace_once(
        source,
        "const loaded=await resolver.load(),handoff=resolver.resolve(loaded.map,'route_guardian'),hash=resolver.normalizeHash(location.hash,loaded.map),launchUrl=resolver.buildUrl(handoff,{fresh:'current-entry-'+handoff.route_epoch+'-'+Date.now(),map_version:handoff.map_version,route_epoch:handoff.route_epoch},hash);",
        "await resolver.integrityContext();\n"
        "    const verifiedMapObject=JSON.parse(new TextDecoder().decode(verifiedCurrentMap.bytes));\n"
        "    resolver.validateMap(verifiedMapObject);\n"
        "    const loaded={map:verifiedMapObject,map_sha256:verifiedCurrentMap.sha256_hex};\n"
        "    const handoff=resolver.resolve(loaded.map,'route_guardian'),hash=resolver.normalizeHash(location.hash,loaded.map),launchUrl=resolver.buildUrl(handoff,{fresh:'current-entry-'+handoff.route_epoch+'-'+Date.now(),map_version:handoff.map_version,route_epoch:handoff.route_epoch},hash);",
        "ROOT_CURRENT_MAP_VERIFIED_BYTES_USE",
    )
    root_html.write_text(source)

    runner = root / "run_full_isolated_proof_002.py"
    runner_source = runner.read_text()
    old_order = """ results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180))
 e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-restored.json');results.append(run('a003-live-restored-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-restored-command.json',420))
 server=None
 try:
  server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300))
 finally:stop_server(server,a.evidence_dir/'a002-restored-http.log')
"""
    new_order = """ results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180))
 server=None
 try:
  server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',360))
 finally:stop_server(server,a.evidence_dir/'a002-restored-http.log')
 e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-restored.json');results.append(run('a003-live-restored-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-restored-command.json',420))
"""
    runner_source = replace_once(
        runner_source,
        old_order,
        new_order,
        "RESTORED_REGRESSION_ORDER",
    )
    runner.write_text(runner_source)

    repair_006 = Path(__file__).with_name("repair_runner_006.py")
    subprocess.run(
        [sys.executable, str(repair_006), "--bundle-root", str(root)],
        check=True,
    )

    print("CURRENT_MAP_PREFETCH_RESTORED_ORDER_AND_REPAIR_006_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
