#!/usr/bin/env python3
import argparse, hashlib, json, pathlib
p=argparse.ArgumentParser();p.add_argument('--path',required=True);p.add_argument('--evidence-dir',required=True);a=p.parse_args()
path=pathlib.Path(a.path);out=pathlib.Path(a.evidence_dir);out.mkdir(parents=True,exist_ok=True)
original=path.read_text();text=original
before_sha=hashlib.sha256(original.encode()).hexdigest()
import_old='import argparse,json,os,subprocess,sys,time'
import_new='import argparse,hashlib,json,os,subprocess,sys,time'
if text.count(import_old)==1:text=text.replace(import_old,import_new,1)
elif text.count(import_new)!=1:raise SystemExit(f'REHEARSAL096_IMPORT_POINT_INVALID:{text.count(import_old)}:{text.count(import_new)}')
main_anchor='def main():\n'
helper=r'''def capture_runtime_sources(root,evidence_dir,label):
 targets=('pmp-route-guardian-current-loader-v22.html','pmp-actor-authority-gate-v1.js','pmp-p2c-production-enforcement-adapter-candidate-001.js','pmp-p2c-production-enforcement-policy-candidate-001.json','audit/a002-live-runtime.cjs','audit/a003-live-runtime.cjs')
 rows=[]
 for rel in targets:
  src=root/rel
  row={'path':rel,'present':src.is_file()}
  if src.is_file():
   data=src.read_bytes();dest=evidence_dir/('runtime-source-096-'+label+'-'+rel.replace('/','__'));dest.write_bytes(data);row.update({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'evidence_path':dest.name})
  rows.append(row)
 receipt={'type':'PMP_P2C_RUNTIME_SOURCE_CAPTURE_096','status':'PASS','label':label,'rows':rows,'production_changed':False}
 (evidence_dir/f'runtime-source-capture-096-{label}.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 return receipt

'''
if text.count(main_anchor)!=1:raise SystemExit(f'REHEARSAL096_MAIN_POINT_INVALID:{text.count(main_anchor)}')
text=text.replace(main_anchor,helper+main_anchor,1)
a003_write_anchor=' a003.write_text(s)\n'
a003_patch=r''' a003_home_anchor="    const urls = page.frames().map(f => f.url());\n    const homeUrl = urls.find(u => /pmp-home-single-v6\\.html/.test(u));"
 a003_home_insert="""    const urls = page.frames().map(f => f.url());
    const pageUrl = page.url();
    let directPathMatches = false;
    let directHash = '';
    try { const parsed = new URL(pageUrl); directPathMatches = parsed.pathname.endsWith('/' + CURRENT); directHash = parsed.hash; } catch {}
    const canonicalReady = await page.evaluate(() => !!(window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function')).catch(() => false);
    if (directPathMatches && canonicalReady && directHash === expectedHash) return { reached:true, expected_hash:expectedHash, actual_hash:directHash, hash_matches:true, home_url:pageUrl, landing_mode:'canonical-current-app', urls };
    const homeUrl = urls.find(u => /pmp-home-single-v6\.html/.test(u));"""
 if s.count(a003_home_anchor)!=1:raise SystemExit(f'A003_DIRECT_CANONICAL_POINT_INVALID:{s.count(a003_home_anchor)}')
 s=s.replace(a003_home_anchor,a003_home_insert,1)
 a003_wait_count=s.count("{ timeout: 30000 });")+s.count("{timeout:30000});")
 s=s.replace("{ timeout: 30000 });","{ timeout: 30000, waitUntil: 'domcontentloaded' });").replace("{timeout:30000});","{timeout:30000,waitUntil:'domcontentloaded'});")
 if a003_wait_count<2:raise SystemExit(f'A003_DOMCONTENTLOADED_WAIT_POINT_INVALID:{a003_wait_count}')
 a003.write_text(s)
'''
if text.count(a003_write_anchor)!=1:raise SystemExit(f'REHEARSAL096_A003_WRITE_POINT_INVALID:{text.count(a003_write_anchor)}')
text=text.replace(a003_write_anchor,a003_patch,1)
a002_write_anchor=' a002.write_text(s)\n'
a002_patch=r''' a002_wait_count=s.count("{ timeout: 30000 });")
 s=s.replace("{ timeout: 30000 });","{ timeout: 30000, waitUntil: 'domcontentloaded' });")
 s=s.replace("  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control');","  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control', { waitUntil: 'domcontentloaded' });")
 if a002_wait_count<3:raise SystemExit(f'A002_DOMCONTENTLOADED_WAIT_POINT_INVALID:{a002_wait_count}')
 guardian_wait_old="""  pmpA002Stage('guardian-run-app-clicked',{url:guardian.url()});
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#world', { timeout: 30000, waitUntil: 'domcontentloaded' });"""
 guardian_wait_new="""  pmpA002Stage('guardian-run-app-clicked',{url:guardian.url()});
  try {
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#world', { timeout: 30000, waitUntil: 'domcontentloaded' });
  } catch (error) {
    const diagnostics = await pmpA002FrameDiagnostics(page,'guardian-launch-timeout');
    pmpA002Stage('guardian-launch-timeout',{name:String(error&&error.name||'Error'),message:String(error&&error.message||error),diagnostics});
    throw error;
  }"""
 if s.count(guardian_wait_old)!=1:raise SystemExit(f'A002_GUARDIAN_TIMEOUT_DIAGNOSTIC_POINT_INVALID:{s.count(guardian_wait_old)}')
 s=s.replace(guardian_wait_old,guardian_wait_new,1)
 diag_old="inner_v23:read('pmp_inner_v23_route_fail_closed_v1')},iframes:"
 diag_new="inner_v23:read('pmp_inner_v23_route_fail_closed_v1'),guardian:read('pmp_route_guardian_v22_receipt')},guardian_ui:{message:document.querySelector('#msg')?.textContent||null,report:document.querySelector('#report')?.textContent||null,open_disabled:!!document.querySelector('#openBtn')?.disabled},authority_gate:(()=>{try{return globalThis.PMPActorAuthorityGateV1&&globalThis.PMPActorAuthorityGateV1.report?globalThis.PMPActorAuthorityGateV1.report():null}catch(e){return{error:String(e&&e.message||e)}}})(),p2c_globals:Object.keys(globalThis).filter(k=>/PMP.*(Actor|Authority|Enforcement)/i.test(k)).sort(),iframes:"
 if s.count(diag_old)!=1:raise SystemExit(f'A002_GUARDIAN_DIAGNOSTIC_PAYLOAD_POINT_INVALID:{s.count(diag_old)}')
 s=s.replace(diag_old,diag_new,1)
 a002.write_text(s)
'''
if text.count(a002_write_anchor)!=1:raise SystemExit(f'REHEARSAL096_A002_WRITE_POINT_INVALID:{text.count(a002_write_anchor)}')
text=text.replace(a002_write_anchor,a002_patch,1)
active_old="a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[];server=None;patch_regression_harnesses(a.activated_root)"
active_new="a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[];server=None;capture_runtime_sources(a.activated_root,a.evidence_dir,'active-before-harness');patch_regression_harnesses(a.activated_root);capture_runtime_sources(a.activated_root,a.evidence_dir,'active-after-harness')"
if text.count(active_old)!=1:raise SystemExit(f'REHEARSAL096_ACTIVE_CAPTURE_POINT_INVALID:{text.count(active_old)}')
text=text.replace(active_old,active_new,1)
restored_old="results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180));patch_regression_harnesses(a.activated_root)"
restored_new="results.append(run('a003-repository-restored-21',[sys.executable,'tools/test_a003_integrity.py','--output',str(a.evidence_dir/'a003-repository-restored.json')],a.activated_root,env,a.evidence_dir/'a003-repository-restored-command.json',180));capture_runtime_sources(a.activated_root,a.evidence_dir,'restored-before-harness');patch_regression_harnesses(a.activated_root);capture_runtime_sources(a.activated_root,a.evidence_dir,'restored-after-harness')"
if text.count(restored_old)!=1:raise SystemExit(f'REHEARSAL096_RESTORED_CAPTURE_POINT_INVALID:{text.count(restored_old)}')
text=text.replace(restored_old,restored_new,1)
compile(text,str(path),'exec');path.write_text(text)
after_sha=hashlib.sha256(path.read_bytes()).hexdigest()
contracts={'capture_helper':text.count('def capture_runtime_sources('),'active_capture':text.count("capture_runtime_sources(a.activated_root,a.evidence_dir,'active-before-harness')"),'restored_capture':text.count("capture_runtime_sources(a.activated_root,a.evidence_dir,'restored-before-harness')"),'a002_guardian_timeout':text.count('A002_GUARDIAN_TIMEOUT_DIAGNOSTIC_POINT_INVALID'),'a003_direct_canonical':text.count('A003_DIRECT_CANONICAL_POINT_INVALID')}
expected={'capture_helper':1,'active_capture':1,'restored_capture':1,'a002_guardian_timeout':1,'a003_direct_canonical':1}
if contracts!=expected:raise SystemExit('REHEARSAL096_CONTRACT_INVALID:'+json.dumps({'actual':contracts,'expected':expected},sort_keys=True))
receipt={'type':'PMP_P2C_RUNTIME_SOURCE_AND_LANDING_DIAGNOSTIC_REPAIR_096','status':'PASS','target':str(path),'before_sha256':before_sha,'after_sha256':after_sha,'contracts':contracts,'test_only':True,'production_changed':False,'authority_policy_changed':False,'unknown_actor_policy_weakened':False}
(out/'runtime-source-and-landing-diagnostic-repair-096.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
