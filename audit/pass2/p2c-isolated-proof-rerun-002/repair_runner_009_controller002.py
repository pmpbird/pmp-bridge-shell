#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}_PATCH_POINT_COUNT:{count}")
    return text.replace(old, new, 1)


def patch_prepare(path: Path) -> None:
    source = path.read_text()

    old_state = ' g=g.replace("const tokenSet=new WeakSet();","const tokenSet=new WeakSet();\\nconst tokenValidators=new WeakMap();",1)'
    new_state = ' g=g.replace("const tokenSet=new WeakSet();","const tokenSet=new WeakSet();\\nconst tokenValidators=new WeakMap();\\nconst propertyListenerMap=new WeakMap();",1)'
    source = replace_once(source, old_state, new_state, "R009C002_GATE_PROPERTY_MAP")

    old_anchor_line = ' anchor="function wrapCallback(token,callback){return typeof callback===\'function\'?function(){return run(token,callback,this,Array.from(arguments))}:callback}\\n"'
    new_anchor_lines = ' anchor="function wrapCallback(token,callback){return typeof callback===\'function\'?function(){return run(token,callback,this,Array.from(arguments))}:callback}\\n"\n new_wrap="function wrapCallback(token,callback){if(typeof callback!==\'function\')return callback;return function(){try{return run(token,callback,this,Array.from(arguments))}catch(error){const settle=callback.__pmpAuthorityFailure;if(typeof settle===\'function\'){settle(error);return}throw error}}}\\n"'
    source = replace_once(source, old_anchor_line, new_anchor_lines, "R009C002_GATE_AUTHORITY_FAILURE_SETTLEMENT_ANCHOR")
    old_replace_line = ' g=g.replace(anchor,new_validator+anchor,1)'
    new_replace_line = ' g=g.replace(anchor,new_validator+new_wrap,1)'
    source = replace_once(source, old_replace_line, new_replace_line, "R009C002_GATE_AUTHORITY_FAILURE_SETTLEMENT_REPLACE")

    old_gate_write = " gate_path.write_text(g)\n return {'status':'APPLIED','authority_model':'CALLBACK_BOUND_TOKEN_VALIDATOR','global_ambient_authority':False,'lease_revalidated_on_callback':True,'ambient_depth_constant_zero':True}"
    new_gate_write = r''' event_setter_anchor="""function install(){
  if(!state.configured)throw new Error('Configure the gate before installing guards.');"""
 event_setter_insert="""function patchEventHandlerSetters(proto){
  if(!proto)return 0;let patched=0;
  for(const name of Object.getOwnPropertyNames(proto)){
    if(!/^on[a-z]/i.test(name))continue;
    const descriptor=Object.getOwnPropertyDescriptor(proto,name);
    if(!descriptor||typeof descriptor.set!=='function'||descriptor.set.__pmpActorCallbackSetter)continue;
    const nativeGet=descriptor.get,nativeSet=descriptor.set;
    function guarded(value){
      const token=requireCapability('event_listener',{operation:'event_handler_property',event:String(name).slice(2),property:String(name)});
      let byTarget=propertyListenerMap.get(this);if(!byTarget){byTarget=new Map();propertyListenerMap.set(this,byTarget)}
      if(typeof value==='function'){
        const wrapped=wrapCallback(token,value);byTarget.set(name,{original:value,wrapped});return nativeSet.call(this,wrapped)
      }
      byTarget.delete(name);return nativeSet.call(this,value)
    }
    guarded.__pmpActorCallbackSetter=true;
    const getter=typeof nativeGet==='function'?function(){const actual=nativeGet.call(this),byTarget=propertyListenerMap.get(this),row=byTarget&&byTarget.get(name);return row&&row.wrapped===actual?row.original:actual}:nativeGet;
    try{Object.defineProperty(proto,name,{...descriptor,get:getter,set:guarded});patched++}catch(e){}
  }
  return patched;
}
function install(){
  if(!state.configured)throw new Error('Configure the gate before installing guards.');"""
 if g.count(event_setter_anchor)!=1:raise SystemExit('R009C002_GATE_EVENT_SETTER_INSERT_POINT_INVALID')
 g=g.replace(event_setter_anchor,event_setter_insert,1)
 install_anchor="  const nativeTimeout=globalThis.setTimeout&&globalThis.setTimeout.bind(globalThis),nativeInterval=globalThis.setInterval&&globalThis.setInterval.bind(globalThis);"
 install_insert="""  let eventHandlerSetterCount=0;
  for(const key of Reflect.ownKeys(globalThis)){
    let ctor;try{ctor=globalThis[key]}catch(e){continue}
    if(typeof ctor!=='function'||!ctor.prototype)continue;
    eventHandlerSetterCount+=patchEventHandlerSetters(ctor.prototype)
  }
  state.eventHandlerSetterCount=eventHandlerSetterCount;
"""
 if g.count(install_anchor)!=1:raise SystemExit('R009C002_GATE_EVENT_SETTER_INSTALL_POINT_INVALID')
 g=g.replace(install_anchor,install_insert+install_anchor,1)
 report_old="async_authority_model:'CALLBACK_BOUND_TOKEN_VALIDATOR',pass2_complete:false"
 report_new="async_authority_model:'SOURCE_NORMALIZED_PROMISE_CONTINUATIONS',callback_registration_authority:'EVENT_HANDLER_PROPERTY_SETTERS_BOUND',event_handler_setter_count:state.eventHandlerSetterCount||0,pass2_complete:false"
 if g.count(report_old)!=1:raise SystemExit('R009C002_GATE_REPORT_POINT_INVALID')
 g=g.replace(report_old,report_new,1)
 gate_path.write_text(g)
 return {'status':'APPLIED','authority_model':'SOURCE_NORMALIZED_PROMISE_CONTINUATIONS','callback_registration_authority':'EVENT_HANDLER_PROPERTY_SETTERS_BOUND','global_ambient_authority':False,'lease_revalidated_on_callback':True,'ambient_depth_constant_zero':True,'authority_failure_settlement':'PROMISE_REJECT_WITHOUT_ACTOR_AUTHORITY'}
'''
    source = replace_once(source, old_gate_write, new_gate_write, "R009C002_PREPARE_GATE_EXTENSION")

    function_anchor = "def main():\n"
    normalization_function = r'''def apply_repair009_normalized_sources(activated_root:Path,payload_root:Path):
 manifest_path=payload_root/'repair009-normalized-source-manifest-002.json'
 source_root=payload_root/'repair009-normalized-sources-002'
 manifest=json.loads(manifest_path.read_text())
 if manifest.get('type')!='PMP_REPAIR009_NORMALIZED_SOURCE_MANIFEST_002':raise SystemExit('R009C002_NORMALIZED_MANIFEST_TYPE_INVALID')
 applied=[]
 for row in manifest.get('records',[]):
  rel=row['path'];target=activated_root/rel;source=source_root/rel
  if not target.is_file() or not source.is_file():raise SystemExit('R009C002_NORMALIZED_SOURCE_MISSING:'+rel)
  original=file_sha(target);candidate=file_sha(source)
  if original!=row['original_sha256']:raise SystemExit('R009C002_ORIGINAL_SOURCE_MISMATCH:'+rel+':'+original)
  if candidate!=row['transformed_sha256']:raise SystemExit('R009C002_TRANSFORMED_SOURCE_MISMATCH:'+rel+':'+candidate)
  shutil.copy2(source,target)
  if file_sha(target)!=row['transformed_sha256']:raise SystemExit('R009C002_NORMALIZED_COPY_MISMATCH:'+rel)
  applied.append({'path':rel,'original_sha256':original,'transformed_sha256':candidate,'kind':row['kind'],'realm':row['realm']})
 return {'status':'APPLIED','model':'TYPESCRIPT_5_8_3_ES2016_ASYNC_TO_GENERATOR_PROMISE_CONTINUATIONS','record_count':len(applied),'global_ambient_authority':False,'quarantined_actors_changed':False,'records':applied}

'''
    if source.count(function_anchor) != 1:
        raise SystemExit("R009C002_PREPARE_MAIN_ANCHOR_INVALID")
    source = source.replace(function_anchor, normalization_function + function_anchor, 1)

    copy_anchor = " for p in sorted((a.payload_root/'contracts').iterdir()):shutil.copy2(p,a.activated_root/p.name)\n # Proof-only repair: prefetch all source bytes before installing the gate; no production file is modified."
    copy_insert = " for p in sorted((a.payload_root/'contracts').iterdir()):shutil.copy2(p,a.activated_root/p.name)\n repair009_async_continuation_normalization=apply_repair009_normalized_sources(a.activated_root,a.payload_root)\n # Proof-only repair: prefetch all source bytes before installing the gate; no production file is modified."
    source = replace_once(source, copy_anchor, copy_insert, "R009C002_NORMALIZED_SOURCE_APPLICATION")

    output_anchor = "'callback_bound_actor_lease_repair':callback_bound_actor_lease_repair,'production_changed':False"
    output_insert = "'callback_bound_actor_lease_repair':callback_bound_actor_lease_repair,'repair009_async_continuation_normalization':repair009_async_continuation_normalization,'production_changed':False"
    source = replace_once(source, output_anchor, output_insert, "R009C002_PREPARE_OUTPUT")
    path.write_text(source)


def patch_a002_determinism(path: Path) -> None:
    source = path.read_text()
    anchor = " s=s.replace(home_anchor,home_insert,1)\n a002.write_text(s)"
    insertion = r''' s=s.replace(home_anchor,home_insert,1)
 diag_anchor="function pmpA002Stage(name, detail = {}) { const row={name,detail,at:new Date().toISOString()};pmpA002StageEvidence.push(row);console.log(`A002_STAGE_EVIDENCE ${name} ${JSON.stringify(detail)}`);return row; }\nlet fatalError = null;"
 diag_insert="""function pmpA002Stage(name, detail = {}) { const row={name,detail,at:new Date().toISOString()};pmpA002StageEvidence.push(row);console.log(`A002_STAGE_EVIDENCE ${name} ${JSON.stringify(detail)}`);return row; }
const pmpA002RuntimeEvents=[];
function pmpA002Event(kind,detail={}){const row={kind,detail,at:new Date().toISOString()};pmpA002RuntimeEvents.push(row);console.log(`A002_RUNTIME_EVENT ${kind} ${JSON.stringify(detail)}`);return row}
function pmpA002AttachDiagnostics(page){if(page.__pmpA002DiagnosticsAttached)return;page.__pmpA002DiagnosticsAttached=true;page.on('console',m=>pmpA002Event('console',{type:m.type(),text:m.text()}));page.on('pageerror',e=>pmpA002Event('pageerror',{name:String(e&&e.name||'Error'),message:String(e&&e.message||e)}));page.on('requestfailed',r=>pmpA002Event('requestfailed',{url:r.url(),failure:r.failure()}));page.on('response',r=>{if(r.status()>=400)pmpA002Event('http-error',{url:r.url(),status:r.status()})});page.on('frameattached',f=>pmpA002Event('frameattached',{url:f.url()}));page.on('framedetached',f=>pmpA002Event('framedetached',{url:f.url()}));page.on('framenavigated',f=>pmpA002Event('framenavigated',{url:f.url()}))}
async function pmpA002FrameDiagnostics(page,label){const rows=[];for(const frame of page.frames()){let runtime;try{runtime=await frame.evaluate(()=>{const read=k=>{try{return localStorage.getItem(k)}catch(e){return null}};const diag=[...document.querySelectorAll('[id*=Diagnostic],[id*=diagnostic],#routeDiagnostic,#pmpRouteDiagnosticV3')].map(x=>({id:x.id,text:String(x.textContent||'').slice(0,4000),display:getComputedStyle(x).display}));return{ready_state:document.readyState,resolver_present:!!globalThis.PMPCurrentRouteResolver,service_worker_controller:navigator.serviceWorker&&navigator.serviceWorker.controller?navigator.serviceWorker.controller.scriptURL:null,diagnostics:diag,receipts:{inner_v4:read('pmp_inner_v4_route_fail_closed_v1'),inner_v3:read('pmp_inner_v3_route_fail_closed_v1'),home:read('pmp_home_single_v6_emergency_rollback_receipt'),guardian:read('pmp_route_guardian_v22_receipt'),reload_owner:read('pmp_auto_fresh_loader_v1_receipt'),inner_v23:read('pmp_inner_v23_route_fail_closed_v1')},iframes:[...document.querySelectorAll('iframe')].map(x=>({id:x.id||null,src_attribute:x.getAttribute('src'),src_property:x.src||null}))}})}catch(e){runtime={evaluation_error:String(e&&e.message||e)}}rows.push({url:frame.url(),runtime})}const out={label,frames:rows};pmpA002Event('frame-diagnostics',out);return out}
let fatalError = null;"""
 if s.count(diag_anchor)!=1:raise SystemExit('R009C002_A002_DIAGNOSTIC_INSERT_POINT_INVALID')
 s=s.replace(diag_anchor,diag_insert,1)
 output_anchor2="    stage_evidence: pmpA002StageEvidence,\n    results"
 output_insert2="    stage_evidence: pmpA002StageEvidence,\n    runtime_events: pmpA002RuntimeEvents,\n    determinism_model: 'FRESH_CONTROLLED_REBOOTSTRAP_AFTER_INTEGRITY_READY',\n    results"
 if s.count(output_anchor2)!=1:raise SystemExit('R009C002_A002_OUTPUT_POINT_INVALID')
 s=s.replace(output_anchor2,output_insert2,1)
 bootstrap_anchor2="  pmpA002Stage('bootstrap-start',{hash});\n  await page.goto"
 bootstrap_insert2="  pmpA002AttachDiagnostics(page);\n  pmpA002Stage('bootstrap-start',{hash});\n  await page.goto"
 if s.count(bootstrap_anchor2)!=1:raise SystemExit('R009C002_A002_ATTACH_POINT_INVALID')
 s=s.replace(bootstrap_anchor2,bootstrap_insert2,1)
 false_return="  return { reached: false, hash_matches: false, expected_hash: expectedHash, actual_hash: null, home_url: null, urls: page.frames().map(f => f.url()) };"
 false_insert="  const diagnostics=await pmpA002FrameDiagnostics(page,'home-timeout:'+expectedHash);\n  return { reached: false, hash_matches: false, expected_hash: expectedHash, actual_hash: null, home_url: null, urls: page.frames().map(f => f.url()), diagnostics };"
 if s.count(false_return)!=1:raise SystemExit('R009C002_A002_HOME_TIMEOUT_POINT_INVALID')
 s=s.replace(false_return,false_insert,1)
 barrier_anchor="  record('only-a003-integrity-worker-registered', registrations.length === 1 && registrations[0]?.includes('/' + INTEGRITY_SW), registrations);\n\n  const guardian = await guardianFrame(page);"
 barrier_insert="""  record('only-a003-integrity-worker-registered', registrations.length === 1 && registrations[0]?.includes('/' + INTEGRITY_SW), registrations);

  pmpA002Stage('fresh-controlled-rebootstrap-start',{url:page.url()});
  await page.goto('about:blank',{waitUntil:'load'});
  await bootstrap(page,'#world');
  const barrierStatus=await workerStatus(page);
  if(!(barrierStatus&&barrierStatus.type==='PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE'&&barrierStatus.receipt&&barrierStatus.receipt.state==='ENFORCED'))throw new Error('A002_FRESH_CONTROLLED_REBOOTSTRAP_NOT_ENFORCED');
  pmpA002Stage('fresh-controlled-rebootstrap-ready',{url:page.url(),controller_state:barrierStatus.receipt.state,controller_version:barrierStatus.receipt.version});

  const guardian = await guardianFrame(page);"""
 if s.count(barrier_anchor)!=1:raise SystemExit('R009C002_A002_FRESH_BARRIER_POINT_INVALID')
 s=s.replace(barrier_anchor,barrier_insert,1)
 a002.write_text(s)'''
    source = replace_once(source, anchor, insertion, "R009C002_A002_DETERMINISM_PATCH")
    path.write_text(source)


def update_policy(bundle_root: Path, manifest: dict) -> None:
    policy_path = bundle_root / "policy-template.json"
    policy = json.loads(policy_path.read_text())
    by_path = {a["path"]: a for a in policy["actors"]}
    for row in manifest["records"]:
        actor = by_path.get(row["path"])
        if actor is None:
            raise SystemExit("R009C002_POLICY_ACTOR_MISSING:" + row["path"])
        if actor["sha256"] != row["original_sha256"]:
            raise SystemExit("R009C002_POLICY_ORIGINAL_SHA_MISMATCH:" + row["path"])
        actor["sha256"] = row["transformed_sha256"]
        actor["source_identity"] = "REPAIR009_TYPESCRIPT_5_8_3_ES2016_NORMALIZED_DISPOSABLE_PROOF_CANDIDATE"
        actor["async_continuation_authority"] = "PROMISE_REACTION_CALLBACK_BOUND_TOKEN_VALIDATOR"
    policy["repair009_async_continuation_model"] = "TYPESCRIPT_5_8_3_ES2016_ASYNC_TO_GENERATOR_PROMISE_CONTINUATIONS"
    policy["repair009_normalized_actor_count"] = len(manifest["records"])
    policy_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")


def copy_normalized_sources(bundle_root: Path, normalized_root: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("type") != "PMP_REPAIR009_NORMALIZED_SOURCE_MANIFEST_002":
        raise SystemExit("R009C002_INPUT_MANIFEST_TYPE_INVALID")
    destination = bundle_root / "repair009-normalized-sources-002"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for row in manifest["records"]:
        src = normalized_root / row["path"]
        dst = destination / row["path"]
        if not src.is_file() or sha256(src) != row["transformed_sha256"]:
            raise SystemExit("R009C002_NORMALIZED_INPUT_INVALID:" + row["path"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copy2(manifest_path, bundle_root / "repair009-normalized-source-manifest-002.json")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--normalized-root", type=Path, required=True)
    parser.add_argument("--normalization-manifest", type=Path, required=True)
    args = parser.parse_args()

    manifest = copy_normalized_sources(args.bundle_root, args.normalized_root, args.normalization_manifest)
    patch_prepare(args.bundle_root / "prepare_disposable_proof_002.py")
    patch_a002_determinism(args.bundle_root / "run_full_isolated_proof_002.py")
    update_policy(args.bundle_root, manifest)

    result = {
        "status": "PATCH_CANDIDATE_APPLIED",
        "normalized_actor_count": len(manifest["records"]),
        "callback_registration_authority": "EVENT_HANDLER_PROPERTY_SETTERS_BOUND",
        "async_continuation_authority": "TYPESCRIPT_5_8_3_ES2016_ASYNC_TO_GENERATOR_PROMISE_CONTINUATIONS",
        "a002_determinism_model": "FRESH_CONTROLLED_REBOOTSTRAP_AFTER_INTEGRITY_READY_PLUS_FRAME_DIAGNOSTICS",
        "global_ambient_authority": False,
        "proof_executed": False,
        "production_changed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
