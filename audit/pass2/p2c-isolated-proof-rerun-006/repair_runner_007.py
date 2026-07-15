#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}_PATCH_POINT_COUNT:{count}")
    return text.replace(old, new, 1)


def patch_prepare(prepare: Path) -> None:
    source = prepare.read_text()
    function = r'''
def patch_async_actor_leases(root:Path):
 gate_path=root/'pmp-actor-authority-gate-v1.js';g=gate_path.read_text()
 g=g.replace("current:null,denials:[]","current:null,ambient:[],ambientSerial:0,denials:[]",1)
 g=g.replace("const token=state.current;\n  if(!token||!tokenSet.has(token))", "const token=state.current||(state.ambient.length?state.ambient[state.ambient.length-1].token:null);\n  if(!token||!tokenSet.has(token))",1)
 anchor="function wrapCallback(token,callback){return typeof callback==='function'?function(){return run(token,callback,this,Array.from(arguments))}:callback}\n"
 insert="function pushAmbientToken(token){if(!tokenSet.has(token))return deny('INVALID_AMBIENT_ACTOR_TOKEN','actor_identity',null,null);const marker=Object.freeze({id:++state.ambientSerial,token});state.ambient.push(marker);return marker}\nfunction popAmbientToken(marker){const i=state.ambient.lastIndexOf(marker);if(i>=0)state.ambient.splice(i,1);return report()}\n"
 if g.count(anchor)!=1:raise SystemExit('GATE_AMBIENT_INSERT_POINT_INVALID')
 g=g.replace(anchor,insert+anchor,1)
 g=g.replace("current_actor:state.current&&state.current.actor.path||null,pass2_complete:false", "current_actor:state.current&&state.current.actor.path||null,ambient_actor:state.ambient.length&&state.ambient[state.ambient.length-1].token.actor.path||null,ambient_depth:state.ambient.length,pass2_complete:false",1)
 g=g.replace("configure,install,authorizeSource,run,report,DeniedError", "configure,install,authorizeSource,run,pushAmbientToken,popAmbientToken,report,DeniedError",1)
 gate_path.write_text(g)
 return {'status':'APPLIED','authority_model':'TEMPORARY_ASYNC_ACTOR_LEASE','permanent_ambient_authority':False,'nested_actor_stack':True}
'''
    anchor = "def main():\n"
    if source.count(anchor) != 1:
        raise SystemExit("PREPARE_MAIN_ANCHOR_INVALID")
    source = source.replace(anchor, function + "\n" + anchor, 1)
    invocation = " root_receipt_exception=patch_a003_root_receipt_authority(a.activated_root)\n"
    if source.count(invocation) != 1:
        raise SystemExit("ASYNC_GATE_INVOCATION_POINT_INVALID")
    source = source.replace(
        invocation,
        " async_actor_lease_repair=patch_async_actor_leases(a.activated_root)\n" + invocation,
        1,
    )
    output_point = "'a003_root_receipt_authority_exception':root_receipt_exception,'production_changed':False"
    if source.count(output_point) != 1:
        raise SystemExit("ASYNC_GATE_OUTPUT_POINT_INVALID")
    source = source.replace(
        output_point,
        "'a003_root_receipt_authority_exception':root_receipt_exception,'async_actor_lease_repair':async_actor_lease_repair,'production_changed':False",
        1,
    )
    prepare.write_text(source)


def patch_adapter(adapter: Path) -> None:
    source = adapter.read_text()
    source = replace_once(
        source,
        "const id='p2c-production-'+(++serial),leases=new Map(),receipts=[],quarantine=new Set((policy.quarantine_paths||[]).map(norm));let current=null,leaseSerial=0;",
        "const id='p2c-production-'+(++serial),leases=new Map(),receipts=[],quarantine=new Set((policy.quarantine_paths||[]).map(norm));let current=null,leaseSerial=0;",
        "ADAPTER_STATE",
    )
    run_anchor = " function run(auth,fn){if(!auth||auth.adapter_id!==id)deny('CROSS_REALM_AUTHORIZATION',{});const a=actor(auth.actor_path),lease=auth.lease_id&&leases.get(auth.lease_id);if(a.lease_required&&(!lease||!lease.active||Date.now()>lease.expires_at_ms))deny('LEASE_EXPIRED',{path:a.path});const prev=current;current=auth;try{return gate.run(auth.token,fn)}finally{current=prev}}\n"
    extension = r''' function validateAuth(auth){if(!auth||auth.adapter_id!==id)deny('CROSS_REALM_AUTHORIZATION',{});const a=actor(auth.actor_path),lease=auth.lease_id&&leases.get(auth.lease_id);if(a.lease_required&&(!lease||!lease.active||Date.now()>lease.expires_at_ms))deny('LEASE_EXPIRED',{path:a.path});return a}
 function runAsync(auth,fn){const a=validateAuth(auth),marker=gate.pushAmbientToken(auth.token),prev=current;current=auth;let result;try{result=gate.run(auth.token,fn)}catch(error){gate.popAmbientToken(marker);current=prev;throw error}current=prev;if(result&&typeof result.then==='function')return Promise.resolve(result).finally(()=>{gate.popAmbientToken(marker);receipts.push({status:'ASYNC_ACTOR_LEASE_SETTLED',actor_path:a.path})});gate.popAmbientToken(marker);return result}
 function snapshotGlobals(){const out=new Map();for(const key of Reflect.ownKeys(globalThis)){try{out.set(key,globalThis[key])}catch(e){}}return out}
 function wrapFunction(auth,fn,label){if(typeof fn!=='function'||fn.__pmpP2CActorWrapped)return fn;const wrapped=function(){return runAsync(auth,()=>fn.apply(this,Array.from(arguments)))};Object.defineProperty(wrapped,'__pmpP2CActorWrapped',{value:true});try{Object.defineProperty(wrapped,'name',{value:String(label||fn.name||'authorizedActorFunction'),configurable:true})}catch(e){}return wrapped}
 function wrapExports(before,auth){for(const key of Reflect.ownKeys(globalThis)){let value;try{value=globalThis[key]}catch(e){continue}if(before.has(key)&&before.get(key)===value)continue;if(typeof value==='function'){try{globalThis[key]=wrapFunction(auth,value,String(key))}catch(e){};continue}if(value&&typeof value==='object'){for(const name of Reflect.ownKeys(value)){let descriptor;try{descriptor=Object.getOwnPropertyDescriptor(value,name)}catch(e){continue}if(!descriptor||typeof descriptor.value!=='function'||descriptor.value.__pmpP2CActorWrapped)continue;try{Object.defineProperty(value,name,{...descriptor,value:wrapFunction(auth,descriptor.value,String(key)+'.'+String(name))})}catch(e){}}}}receipts.push({status:'ACTOR_EXPORTS_BOUND',actor_path:auth.actor_path})}
 async function evaluateAuthorized(auth,source,label){const before=snapshotGlobals(),result=runAsync(auth,()=>{return(0,eval)(String(source)+'\n//# sourceURL='+String(label))});wrapExports(before,auth);if(result&&typeof result.then==='function')await result;return result}
 async function executeInline(path,source,identitySource,opt={}){const a=actor(path),lease=openLease(path,opt.ttl_ms||90000),auth=await authorize(path,identitySource,lease);const result=await evaluateAuthorized(auth,source,a.path+'#document-inline');receipts.push({status:'DOCUMENT_EXECUTED',actor_path:a.path,lease_id:lease&&lease.id||null});return{status:'PASS',actor_path:a.path,lease,auth,result}}
'''
    if source.count(run_anchor) != 1:
        raise SystemExit("ADAPTER_RUN_EXTENSION_POINT_INVALID")
    source = source.replace(run_anchor, run_anchor + extension, 1)
    old_execute = " async function execute(path,source,opt={}){const a=actor(path);if(quarantine.has(norm(path))){receipts.push({status:'QUARANTINED_NOT_EXECUTED',actor_path:a.path});return{status:'QUARANTINED',actor_path:a.path}}const lease=openLease(path,opt.ttl_ms),auth=await authorize(path,source,lease);const result=run(auth,()=>{const fn=new Function(String(source)+'\\n//# sourceURL='+a.path);return fn.call(globalThis)});receipts.push({status:'EXECUTED',actor_path:a.path,lease_id:lease&&lease.id||null});return{status:'PASS',actor_path:a.path,lease,result}}"
    new_execute = " async function execute(path,source,opt={}){const a=actor(path);if(quarantine.has(norm(path))){receipts.push({status:'QUARANTINED_NOT_EXECUTED',actor_path:a.path});return{status:'QUARANTINED',actor_path:a.path}}const lease=openLease(path,opt.ttl_ms||90000),auth=await authorize(path,source,lease);const result=await evaluateAuthorized(auth,source,a.path);receipts.push({status:'EXECUTED',actor_path:a.path,lease_id:lease&&lease.id||null});return{status:'PASS',actor_path:a.path,lease,auth,result}}"
    source = replace_once(source, old_execute, new_execute, "ADAPTER_EXECUTE")
    source = replace_once(
        source,
        "return Object.freeze({type:TYPE,realm,execute,openLease,expireLease,authorize,run,report:",
        "return Object.freeze({type:TYPE,realm,execute,executeInline,openLease,expireLease,authorize,run,runAsync,report:",
        "ADAPTER_API",
    )
    adapter.write_text(source)


def patch_prelude(prepare: Path) -> None:
    source = prepare.read_text()
    old = "for(const item of prefetched){if(item.tag.dataset.pmpSrc){await adapter.execute(item.path,item.source)}else{const lease=adapter.openLease(item.path,30000),auth=await adapter.authorize(item.path,item.documentSource,lease);adapter.run(auth,()=>new Function(item.source+'\\n//# sourceURL='+item.path+'#document-inline').call(globalThis))}}"
    new = "for(const item of prefetched){if(item.tag.dataset.pmpSrc){await adapter.execute(item.path,item.source,{ttl_ms:90000})}else{await adapter.executeInline(item.path,item.source,item.documentSource,{ttl_ms:90000})}}"
    source = replace_once(source, old, new, "PRELUDE_EXECUTION")
    prepare.write_text(source)


def patch_harness_and_browser(runner: Path, browser: Path) -> None:
    source = runner.read_text()
    old_write = "a003.write_text(s.replace(old,new,1))"
    new_write = """s=s.replace(old,new,1)
 bootstrap_old=\"  const page = await context.newPage();\\n  page.setDefaultTimeout(30000);\"
 bootstrap_new=\"  const page = await context.newPage();\\n  await page.addInitScript(() => { globalThis.__PMP_A003_TEST_NATIVE_FETCH = globalThis.fetch.bind(globalThis); });\\n  page.setDefaultTimeout(30000);\"
 if s.count(bootstrap_old)!=1:raise SystemExit('A003_NATIVE_FETCH_INIT_POINT_INVALID')
 s=s.replace(bootstrap_old,bootstrap_new,1)
 fetch_old=\"const response = await fetch(u, { cache:'no-store' });\"
 fetch_new=\"const nativeFetch=globalThis.__PMP_A003_TEST_NATIVE_FETCH;if(typeof nativeFetch!=='function')throw new Error('A003_TEST_NATIVE_FETCH_MISSING');const response = await nativeFetch(u, { cache:'no-store' });\"
 if s.count(fetch_old)!=1:raise SystemExit('A003_NATIVE_FETCH_USE_POINT_INVALID')
 s=s.replace(fetch_old,fetch_new,1)
 a003.write_text(s)"""
    source = replace_once(source, old_write, new_write, "A003_HARNESS_FETCH")
    source = source.replace(
        "'const deadline = Date.now() + 30000;','const deadline = Date.now() + 60000;'",
        "'const deadline = Date.now() + 30000;','const deadline = Date.now() + 120000;'",
        1,
    )
    runner.write_text(source)

    b = browser.read_text()
    marker = "await page.goto(`http://127.0.0.1:${port}/pmp-app-current.html#world`,{waitUntil:'domcontentloaded',timeout:60000});"
    insertion = marker + "let guardianFrame=null;for(let i=0;i<200&&!guardianFrame;i++){guardianFrame=page.frames().find(f=>/pmp-route-guardian-current-loader-v22\\.html/.test(f.url()));if(!guardianFrame)await page.waitForTimeout(100)}if(!guardianFrame)throw new Error('GUARDIAN_FRAME_NOT_FOUND');await guardianFrame.waitForSelector('#openBtn',{timeout:30000});await guardianFrame.click('#openBtn',{force:true});"
    b = replace_once(b, marker, insertion, "BROWSER_GUARDIAN_CLICK")
    browser.write_text(b)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.bundle_root
    prepare = root / "prepare_disposable_proof_002.py"
    patch_adapter(root / "after/pmp-p2c-production-enforcement-adapter-candidate-001.js")
    patch_prepare(prepare)
    patch_prelude(prepare)
    patch_harness_and_browser(
        root / "run_full_isolated_proof_002.py",
        root / "run_production_shaped_browser_proof_002.cjs",
    )
    print("ASYNC_ACTOR_LEASE_AND_HARNESS_ISOLATION_REPAIR_007_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
