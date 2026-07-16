#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        "bootBox.classList.add('hidden');await p2cRoot.navigate(frame,handoff,launchUrl);",
        "bootBox.classList.add('hidden');await p2cRoot.navigate(frame,handoff,launchUrl,finalReceipt);",
        "ROOT_NAVIGATE_RECEIPT",
    )
    root_html.write_text(source)

    route = root / "after/pmp-p2c-production-route-owner-broker-candidate-001.js"
    route.write_text(
        "(()=>{'use strict';globalThis.PMPP2CRouteOwnerBrokerCandidate001={handle(r){"
        "if(!r||r.operation!=='navigate_iframe'||!r.target||String(r.target.tagName).toUpperCase()!=='IFRAME')"
        "throw new Error('ROUTE_REQUEST_INVALID');"
        "if(!r.fixture_url||!r.map_path||!r.role||!r.bootstrap_receipt)throw new Error('ROUTE_PROOF_MISSING');"
        "localStorage.setItem('pmp_a003_bootstrap_receipt_v1',JSON.stringify(r.bootstrap_receipt,null,2));"
        "localStorage.setItem('pmp_current_entry_route_handoff_receipt_v1',JSON.stringify(r.bootstrap_receipt,null,2));"
        "r.target.src=r.fixture_url;"
        "return{status:'PASS',operation:r.operation,role:r.role,map_path:r.map_path,fixture_url:r.fixture_url,"
        "bootstrap_receipt_written:true}}};})();\n"
    )

    prepare = root / "prepare_disposable_proof_002.py"
    prepare_source = prepare.read_text()
    old_api = (
        "const api={active:true,loadActor:async(path,bytes)=>adapter.execute(path,text(bytes)),"
        "navigate:async(frame,handoff,url)=>{if(!routeLoaded){await adapter.execute(FILES.route,routeSource);"
        "routeLoaded=true}const auth=await adapter.authorize(FILES.route,routeSource,null);"
        "return adapter.run(auth,()=>globalThis.PMPP2CRouteOwnerBrokerCandidate001.handle({"
        "operation:'navigate_iframe',target:frame,fixture_url:url,map_path:handoff.map_path,role:handoff.role}))},"
        "report:adapter.report};"
    )
    new_api = (
        "const api={active:true,loadActor:async(path,bytes)=>adapter.execute(path,text(bytes)),"
        "navigate:async(frame,handoff,url,bootstrapReceipt)=>{"
        "const auth=await adapter.authorize(FILES.route,routeSource,null);"
        "return adapter.run(auth,()=>{if(!routeLoaded){"
        "new Function(routeSource+'\\n//# sourceURL='+FILES.route).call(globalThis);routeLoaded=true}"
        "return globalThis.PMPP2CRouteOwnerBrokerCandidate001.handle({operation:'navigate_iframe',target:frame,"
        "fixture_url:url,map_path:handoff.map_path,role:handoff.role,bootstrap_receipt:bootstrapReceipt})})},"
        "report:adapter.report};"
    )
    prepare_source = replace_once(
        prepare_source,
        old_api,
        new_api,
        "ROOT_ROUTE_BROKER_SINGLE_TOKEN",
    )
    prepare.write_text(prepare_source)

    policy_path = root / "policy-template.json"
    policy = json.loads(policy_path.read_text())
    route_row = next(
        (
            actor
            for actor in policy["actors"]
            if actor["path"] == "pmp-p2c-production-route-owner-broker-candidate-001.js"
        ),
        None,
    )
    if route_row is None:
        raise SystemExit("ROUTE_POLICY_ROW_MISSING")
    route_row["capabilities"] = sorted(
        set(route_row.get("capabilities", []))
        | {"navigation", "resource_target_change", "storage_write"}
    )
    route_row["sha256"] = sha256(route)
    policy_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")

    runner = root / "run_full_isolated_proof_002.py"
    runner.write_text(
        r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys,time
from pathlib import Path
SOURCE='c618596f2b5c99ca7f355153a5bd31268170df80'
def txt(v):
 if isinstance(v,bytes):return v.decode('utf-8','replace')
 return v or ''
def run(name,cmd,cwd,env,out,timeout):
 st=time.monotonic();print(json.dumps({'event':'START','lane':name}),flush=True)
 try:
  p=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout);status='PASS' if p.returncode==0 else 'FAIL';r={'name':name,'status':status,'returncode':p.returncode,'elapsed_seconds':round(time.monotonic()-st,3),'stdout':txt(p.stdout),'stderr':txt(p.stderr)}
 except subprocess.TimeoutExpired as e:r={'name':name,'status':'FAIL_TIMEOUT','returncode':None,'elapsed_seconds':round(time.monotonic()-st,3),'stdout':txt(e.stdout),'stderr':txt(e.stderr)}
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'event':'END','lane':name,'status':r['status'],'elapsed_seconds':r['elapsed_seconds']}),flush=True);return r
def stop_server(server,log):
 if server is None:return
 server.terminate()
 try:server.wait(timeout=10)
 except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
 log.write_text(txt(server.stdout.read() if server.stdout else '')+'\nSTDERR\n'+txt(server.stderr.read() if server.stderr else ''))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--activated-root',type=Path,required=True);ap.add_argument('--baseline-root',type=Path,required=True);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--scripts-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[];server=None
 try:
  results.append(run('production-shaped-browser-active',['node',str(a.scripts_root/'run_production_shaped_browser_proof_002.cjs'),str(a.activated_root),str(a.evidence_dir/'browser-active.json')],a.activated_root,env,a.evidence_dir/'browser-active-command.json',180))
  results.append(run('a003-repository-active-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-active.json')],a.activated_root,env,a.evidence_dir/'a003-repository-active-command.json',180))
  e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-active.json');results.append(run('a003-live-active-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-active-command.json',420))
  server=subprocess.Popen([sys.executable,'-m','http.server','8000','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8000/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-active.json');results.append(run('a002-active-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-active-command.json',300))
 finally:
  stop_server(server,a.evidence_dir/'a002-active-http.log')
  results.append(run('byte-for-byte-rollback',[sys.executable,str(a.scripts_root/'rollback_disposable_proof_002.py'),'--activated-root',str(a.activated_root),'--baseline-root',str(a.baseline_root),'--source-commit',SOURCE,'--output',str(a.evidence_dir/'rollback.json')],a.activated_root,env,a.evidence_dir/'rollback-command.json',180))
 results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180))
 e=dict(env);e['A003_RESULT_PATH']=str(a.evidence_dir/'a003-live-restored.json');results.append(run('a003-live-restored-47',[sys.executable,'tools/run_a003_live_final.py'],a.activated_root,e,a.evidence_dir/'a003-live-restored-command.json',420))
 server=None
 try:
  server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300))
 finally:stop_server(server,a.evidence_dir/'a002-restored-http.log')
 def rd(p):
  q=a.evidence_dir/p
  try:return json.loads(q.read_text())
  except:return None
 browser=rd('browser-active.json');a3ra=rd('a003-repository-active.json');a3la=rd('a003-live-active.json');a2a=rd('a002-active.json');rb=rd('rollback.json');a3rr=rd('a003-repository-restored.json');a3lr=rd('a003-live-restored.json');a2r=rd('a002-restored.json')
 semantic=bool(browser and browser.get('tests_failed')==0 and a3ra and a3ra.get('tests_passed')==21 and a3ra.get('tests_failed')==0 and a3la and a3la.get('tests_passed')==47 and a3la.get('tests_failed')==0 and a2a and a2a.get('tests_passed')==41 and a2a.get('tests_failed')==0 and not a2a.get('fatal_error') and rb and rb.get('byte_for_byte_restored') is True and a3rr and a3rr.get('tests_passed')==21 and a3rr.get('tests_failed')==0 and a3lr and a3lr.get('tests_passed')==47 and a3lr.get('tests_failed')==0 and a2r and a2r.get('tests_passed')==41 and a2r.get('tests_failed')==0 and not a2r.get('fatal_error'))
 out={'type':'PMP_P2C_EXPLICIT_ISOLATED_PROOF_RERUN_AGGREGATE_003','status':'PASS' if semantic and all(x['status']=='PASS' for x in results) else 'FAIL','source_repository_commit':SOURCE,'lanes':[{k:v for k,v in x.items() if k not in ('stdout','stderr')} for x in results],'browser':browser,'a003_repository_active':a3ra,'a003_live_active':a3la,'a002_active':a2a,'rollback':rb,'a003_repository_restored':a3rr,'a003_live_restored':a3lr,'a002_restored':a2r,'production_patch_applied':False,'active_chain_integrated_in_production':False,'proof_scope':'DISPOSABLE_COPY_ONLY','pass2_complete':False,'pass3_started':False}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'lanes':out['lanes'],'production_patch_applied':False},indent=2));return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
'''
    )

    browser = root / "run_production_shaped_browser_proof_002.cjs"
    browser_source = browser.read_text()
    browser_source = replace_once(
        browser_source,
        "const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://127.0.0.1'),rel=decodeURIComponent(u.pathname).replace(/^\\/+/, '')||'pmp-app-current.html',file=path.join(root,rel);requests.push(rel);if(!file.startsWith(root)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);res.end('not found');return}",
        "const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://127.0.0.1'),rel=decodeURIComponent(u.pathname).replace(/^\\/+/, '')||'pmp-app-current.html';if(rel==='favicon.ico'){res.writeHead(204);res.end();return}const file=path.join(root,rel);requests.push(rel);if(!file.startsWith(root)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);res.end('not found');return}",
        "BROWSER_FAVICON",
    )
    browser_source = replace_once(
        browser_source,
        "return{boot,sw,sentinel:localStorage.getItem('pmp_p2c_proof_sentinel_002'),root_api:!!globalThis.PMPP2CProductionEnforcementRootCandidate002,root_report:globalThis.PMPP2CProductionEnforcementRootCandidate002&&globalThis.PMPP2CProductionEnforcementRootCandidate002.report?globalThis.PMPP2CProductionEnforcementRootCandidate002.report():null,prelude_failure:globalThis.PMPP2CProductionEnforcementPreludeFailureCandidate001||null}});",
        "return{boot,sw,sentinel:localStorage.getItem('pmp_p2c_proof_sentinel_002'),root_api:!!globalThis.PMPP2CProductionEnforcementRootCandidate002,root_report:globalThis.PMPP2CProductionEnforcementRootCandidate002&&globalThis.PMPP2CProductionEnforcementRootCandidate002.report?globalThis.PMPP2CProductionEnforcementRootCandidate002.report():null,prelude_failure:globalThis.PMPP2CProductionEnforcementPreludeFailureCandidate001||null,diagnostic:document.getElementById('routeDiagnostic')&&document.getElementById('routeDiagnostic').textContent||null}});",
        "BROWSER_DIAGNOSTIC",
    )
    browser.write_text(browser_source)

    print(
        json.dumps(
            {
                "status": "PASS",
                "route_sha256": sha256(route),
                "patched_files": [
                    str(path.relative_to(root))
                    for path in [root_html, route, prepare, policy_path, runner, browser]
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
