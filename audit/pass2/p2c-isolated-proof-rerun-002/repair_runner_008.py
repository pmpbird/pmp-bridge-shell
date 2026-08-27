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
    start = "def patch_async_actor_leases(root:Path):\n"
    end = "\ndef main():\n"
    if source.count(start) != 1 or source.count(end) != 1:
        raise SystemExit("REPAIR007_PREPARE_FUNCTION_BOUNDARY_INVALID")
    before, remainder = source.split(start, 1)
    _, after = remainder.split(end, 1)
    replacement = r'''def patch_callback_bound_actor_leases(root:Path):
 gate_path=root/'pmp-actor-authority-gate-v1.js';g=gate_path.read_text()
 g=g.replace("const tokenSet=new WeakSet();","const tokenSet=new WeakSet();\nconst tokenValidators=new WeakMap();",1)
 old_require="""function requireActor(){
  const token=state.current;
  if(!token||!tokenSet.has(token))return deny('UNKNOWN_ACTOR','actor_identity',null,null);
  return token;
}"""
 new_require="""function validateToken(token){
  if(!token||!tokenSet.has(token))return deny('UNKNOWN_ACTOR','actor_identity',null,null);
  const validator=tokenValidators.get(token);
  if(validator){let valid=false;try{valid=validator()===true}catch(e){}if(!valid)return deny('ACTOR_LEASE_INVALID','actor_identity',{path:token.actor&&token.actor.path||null},token.actor||null)}
  return token;
}
function requireActor(){return validateToken(state.current)}"""
 if g.count(old_require)!=1:raise SystemExit('GATE_REQUIRE_ACTOR_ORIGINAL_POINT_INVALID')
 g=g.replace(old_require,new_require,1)
 anchor="function wrapCallback(token,callback){return typeof callback==='function'?function(){return run(token,callback,this,Array.from(arguments))}:callback}\n"
 new_validator="function bindTokenValidator(token,validator){validateToken(token);if(typeof validator!=='function')throw new TypeError('Actor token validator must be a function.');tokenValidators.set(token,validator);return report()}\n"
 if g.count(anchor)!=1:raise SystemExit('GATE_TOKEN_VALIDATOR_INSERT_POINT_INVALID')
 g=g.replace(anchor,new_validator+anchor,1)
 old_run="""function run(token,fn,thisArg,args){
  if(!tokenSet.has(token))return deny('INVALID_ACTOR_TOKEN','actor_identity',null,null);
  if(typeof fn!=='function')throw new TypeError('Authorized actor callback must be a function.');
  const previous=state.current;state.current=token;
  try{return fn.apply(thisArg,args||[])}finally{state.current=previous}
}"""
 new_run="""function run(token,fn,thisArg,args){
  validateToken(token);
  if(typeof fn!=='function')throw new TypeError('Authorized actor callback must be a function.');
  const previous=state.current;state.current=token;
  try{return fn.apply(thisArg,args||[])}finally{state.current=previous}
}"""
 if g.count(old_run)!=1:raise SystemExit('GATE_RUN_VALIDATION_POINT_INVALID')
 g=g.replace(old_run,new_run,1)
 g=g.replace("current_actor:state.current&&state.current.actor.path||null,pass2_complete:false","current_actor:state.current&&state.current.actor.path||null,ambient_actor:null,ambient_depth:0,async_authority_model:'CALLBACK_BOUND_TOKEN_VALIDATOR',pass2_complete:false",1)
 g=g.replace("configure,install,authorizeSource,run,report,DeniedError","configure,install,authorizeSource,bindTokenValidator,run,report,DeniedError",1)
 gate_path.write_text(g)
 return {'status':'APPLIED','authority_model':'CALLBACK_BOUND_TOKEN_VALIDATOR','global_ambient_authority':False,'lease_revalidated_on_callback':True,'ambient_depth_constant_zero':True}
'''
    source = before + replacement + end + after
    source = replace_once(
        source,
        " async_actor_lease_repair=patch_async_actor_leases(a.activated_root)\n",
        " callback_bound_actor_lease_repair=patch_callback_bound_actor_leases(a.activated_root)\n",
        "PREPARE_REPAIR008_INVOCATION",
    )
    source = replace_once(
        source,
        "'async_actor_lease_repair':async_actor_lease_repair,",
        "'callback_bound_actor_lease_repair':callback_bound_actor_lease_repair,",
        "PREPARE_REPAIR008_OUTPUT",
    )
    prepare.write_text(source)


def patch_adapter(adapter: Path) -> None:
    source = adapter.read_text()
    old_authorize = " async function authorize(path,source,lease){const a=actor(path);if(quarantine.has(norm(path)))deny('ACTOR_QUARANTINED',{path:a.path});if(a.lease_required&&(!lease||!lease.active||lease.actor_path!==a.path))deny('LEASE_REQUIRED',{path:a.path});const token=await gate.authorizeSource(a.path,String(source));return Object.freeze({adapter_id:id,actor_path:a.path,lease_id:lease&&lease.id||null,token})}"
    new_authorize = " async function authorize(path,source,lease){const a=actor(path);if(quarantine.has(norm(path)))deny('ACTOR_QUARANTINED',{path:a.path});if(a.lease_required&&(!lease||!lease.active||lease.actor_path!==a.path))deny('LEASE_REQUIRED',{path:a.path});const token=await gate.authorizeSource(a.path,String(source)),leaseId=lease&&lease.id||null;gate.bindTokenValidator(token,()=>{if(!a.lease_required)return true;const live=leaseId&&leases.get(leaseId);return!!(live&&live.active&&live.actor_path===a.path&&Date.now()<=live.expires_at_ms)});return Object.freeze({adapter_id:id,actor_path:a.path,lease_id:leaseId,token})}"
    source = replace_once(source, old_authorize, new_authorize, "ADAPTER_TOKEN_VALIDATOR_BIND")
    old_run_async = " function runAsync(auth,fn){const a=validateAuth(auth),marker=gate.pushAmbientToken(auth.token),prev=current;current=auth;let result;try{result=gate.run(auth.token,fn)}catch(error){gate.popAmbientToken(marker);current=prev;throw error}current=prev;if(result&&typeof result.then==='function')return Promise.resolve(result).finally(()=>{gate.popAmbientToken(marker);receipts.push({status:'ASYNC_ACTOR_LEASE_SETTLED',actor_path:a.path})});gate.popAmbientToken(marker);return result}"
    new_run_async = " function runAsync(auth,fn){const a=validateAuth(auth),prev=current;current=auth;let result;try{result=gate.run(auth.token,fn)}finally{current=prev}if(result&&typeof result.then==='function')return Promise.resolve(result).finally(()=>{receipts.push({status:'ASYNC_ACTOR_LEASE_SETTLED',actor_path:a.path})});return result}"
    source = replace_once(source, old_run_async, new_run_async, "ADAPTER_REMOVE_GLOBAL_AMBIENT")
    old_report = "report:()=>({type:TYPE,realm,actor_count:actors.size,quarantine_count:quarantine.size,receipt_count:receipts.length,receipts:clone(receipts),active_chain_integration:true})"
    new_report = "report:()=>({type:TYPE,realm,actor_count:actors.size,quarantine_count:quarantine.size,receipt_count:receipts.length,receipts:clone(receipts),async_authority_model:'CALLBACK_BOUND_TOKEN_VALIDATOR',global_ambient_authority:false,active_chain_integration:true})"
    source = replace_once(source, old_report, new_report, "ADAPTER_REPORT_MODEL")
    adapter.write_text(source)


def patch_a002_stage_evidence(runner: Path) -> None:
    source = runner.read_text()
    old_write = " a002.write_text(s)\n"
    new_write = r''' stage_anchor="const results = [];\nlet fatalError = null;"
 stage_insert="const results = [];\nconst pmpA002StageEvidence = [];\nfunction pmpA002Stage(name, detail = {}) { const row={name,detail,at:new Date().toISOString()};pmpA002StageEvidence.push(row);console.log(`A002_STAGE_EVIDENCE ${name} ${JSON.stringify(detail)}`);return row; }\nlet fatalError = null;"
 if s.count(stage_anchor)!=1:raise SystemExit('A002_STAGE_LEDGER_INSERT_POINT_INVALID')
 s=s.replace(stage_anchor,stage_insert,1)
 output_anchor="    fatal_error: fatalError,\n    results"
 output_insert="    fatal_error: fatalError,\n    stage_evidence: pmpA002StageEvidence,\n    results"
 if s.count(output_anchor)!=1:raise SystemExit('A002_STAGE_OUTPUT_POINT_INVALID')
 s=s.replace(output_anchor,output_insert,1)
 bootstrap_anchor="async function bootstrap(page, hash) {\n  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'domcontentloaded' });"
 bootstrap_insert="async function bootstrap(page, hash) {\n  pmpA002Stage('bootstrap-start',{hash});\n  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'domcontentloaded' });\n  pmpA002Stage('bootstrap-page-loaded',{url:page.url(),hash});"
 if s.count(bootstrap_anchor)!=1:raise SystemExit('A002_STAGE_BOOTSTRAP_POINT_INVALID')
 s=s.replace(bootstrap_anchor,bootstrap_insert,1)
 guardian_anchor="    if (frame) return frame;"
 guardian_insert="    if (frame) { pmpA002Stage('guardian-frame-reached',{url:frame.url()}); return frame; }"
 if s.count(guardian_anchor)!=1:raise SystemExit('A002_STAGE_GUARDIAN_POINT_INVALID')
 s=s.replace(guardian_anchor,guardian_insert,1)
 click_anchor="  await guardian.click('#openBtn', { force: true });"
 click_insert="  pmpA002Stage('guardian-run-app-before-click',{url:guardian.url()});\n  await guardian.click('#openBtn', { force: true });\n  pmpA002Stage('guardian-run-app-clicked',{url:guardian.url()});"
 if s.count(click_anchor)!=1:raise SystemExit('A002_STAGE_GUARDIAN_CLICK_POINT_INVALID')
 s=s.replace(click_anchor,click_insert,1)
 loop_anchor="  for (const screen of SCREENS) {\n    const expectedHash = '#' + screen;"
 loop_insert="  for (const screen of SCREENS) {\n    const expectedHash = '#' + screen;\n    pmpA002Stage('screen-start',{screen,expected_hash:expectedHash,current_url:page.url()});"
 if s.count(loop_anchor)!=1:raise SystemExit('A002_STAGE_SCREEN_START_POINT_INVALID')
 s=s.replace(loop_anchor,loop_insert,1)
 home_anchor="    const home = await frameReachedHome(page, expectedHash);\n    record(`current-chain-home:${screen}`, home.reached && home.hash_matches,"
 home_insert="    const home = await frameReachedHome(page, expectedHash);\n    pmpA002Stage('home-observation',{screen,reached:home.reached,hash_matches:home.hash_matches,expected_hash:home.expected_hash,actual_hash:home.actual_hash,home_url:home.home_url,frame_urls:home.urls.slice(-8)});\n    record(`current-chain-home:${screen}`, home.reached && home.hash_matches,"
 if s.count(home_anchor)!=1:raise SystemExit('A002_STAGE_HOME_POINT_INVALID')
 s=s.replace(home_anchor,home_insert,1)
 a002.write_text(s)
'''
    source = replace_once(source, old_write, new_write, "RUNNER_A002_STAGE_EVIDENCE")
    runner.write_text(source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.bundle_root
    patch_prepare(root / "prepare_disposable_proof_002.py")
    patch_adapter(root / "after/pmp-p2c-production-enforcement-adapter-candidate-001.js")
    patch_a002_stage_evidence(root / "run_full_isolated_proof_002.py")
    print("CALLBACK_BOUND_AUTHORITY_AND_A002_STAGE_EVIDENCE_REPAIR_008_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
