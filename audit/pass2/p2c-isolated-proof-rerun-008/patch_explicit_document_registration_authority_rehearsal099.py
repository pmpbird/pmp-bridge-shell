#!/usr/bin/env python3
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--bundle-root',required=True);p.add_argument('--prepare-path',required=True);p.add_argument('--evidence-dir',required=True);a=p.parse_args()
root=pathlib.Path(a.bundle_root);prepare=pathlib.Path(a.prepare_path);out=pathlib.Path(a.evidence_dir);out.mkdir(parents=True,exist_ok=True)
source=prepare.read_text();before_prepare=hashlib.sha256(prepare.read_bytes()).hexdigest()
write_anchor=' gate_path.write_text(g)'
injection=r''' registration_state_old="const state={configured:false,installed:false,policy:null,actors:new Map(),manifest:new Map(),current:null,denials:[],native:{},listenerMap:new WeakMap()};"
 registration_state_new="const state={configured:false,installed:false,policy:null,actors:new Map(),manifest:new Map(),current:null,registrationToken:null,denials:[],native:{},listenerMap:new WeakMap()};"
 if g.count(registration_state_old)!=1:raise SystemExit(f'R099_GATE_REGISTRATION_STATE_POINT_INVALID:{g.count(registration_state_old)}')
 g=g.replace(registration_state_old,registration_state_new,1)
 registration_function_anchor="function patchEventHandlerSetters(proto){"
 registration_function_insert="""function withRegistrationToken(token,fn){
  validateToken(token);if(typeof fn!=='function')throw new TypeError('Registration authority callback must be a function.');
  const previous=state.registrationToken;state.registrationToken=token;
  try{return run(token,fn)}finally{state.registrationToken=previous}
}
function patchEventHandlerSetters(proto){"""
 if g.count(registration_function_anchor)!=1:raise SystemExit(f'R099_GATE_REGISTRATION_FUNCTION_POINT_INVALID:{g.count(registration_function_anchor)}')
 g=g.replace(registration_function_anchor,registration_function_insert,1)
 registration_setter_old="      const token=requireCapability('event_listener',{operation:'event_handler_property',event:String(name).slice(2),property:String(name)});"
 registration_setter_new="      const detail={operation:'event_handler_property',event:String(name).slice(2),property:String(name)};const token=state.registrationToken?validateToken(state.registrationToken):requireActor();if(token.actor.capabilities.indexOf('event_listener')<0)return deny('UNAUTHORIZED_CAPABILITY','event_listener',detail,token.actor);"
 if g.count(registration_setter_old)!=1:raise SystemExit(f'R099_GATE_REGISTRATION_SETTER_POINT_INVALID:{g.count(registration_setter_old)}')
 g=g.replace(registration_setter_old,registration_setter_new,1)
 registration_api_old="const api=Object.freeze({type:TYPE,version:VERSION,configure,install,authorizeSource,bindTokenValidator,run,report,DeniedError:PMPActorAuthorityDeniedError});"
 registration_api_new="const api=Object.freeze({type:TYPE,version:VERSION,configure,install,authorizeSource,bindTokenValidator,withRegistrationToken,run,report,DeniedError:PMPActorAuthorityDeniedError});"
 if g.count(registration_api_old)!=1:raise SystemExit(f'R099_GATE_REGISTRATION_API_POINT_INVALID:{g.count(registration_api_old)}')
 g=g.replace(registration_api_old,registration_api_new,1)
 registration_report_old="callback_registration_authority:'EVENT_HANDLER_PROPERTY_SETTERS_BOUND'"
 registration_report_new="callback_registration_authority:'EXPLICIT_DOCUMENT_ACTOR_REGISTRATION_SCOPE'"
 if g.count(registration_report_old)!=1:raise SystemExit(f'R099_GATE_REGISTRATION_REPORT_POINT_INVALID:{g.count(registration_report_old)}')
 g=g.replace(registration_report_old,registration_report_new,1)
 gate_path.write_text(g)'''
count=source.count(write_anchor)
if count!=1:raise SystemExit(f'REHEARSAL099_PREPARE_GATE_WRITE_POINT_INVALID:{count}')
source=source.replace(write_anchor,injection,1);compile(source,str(prepare),'exec');prepare.write_text(source)
after_prepare=hashlib.sha256(prepare.read_bytes()).hexdigest()
adapter_old="async function evaluateAuthorized(auth,source,label){const before=snapshotGlobals(),result=runAsync(auth,()=>{return(0,eval)(String(source)+'\\n//# sourceURL='+String(label))});wrapExports(before,auth);if(result&&typeof result.then==='function')await result;return result}"
adapter_new="async function evaluateAuthorized(auth,source,label){const before=snapshotGlobals(),result=runAsync(auth,()=>gate.withRegistrationToken(auth.token,()=>{return(0,eval)(String(source)+'\\n//# sourceURL='+String(label))}));wrapExports(before,auth);if(result&&typeof result.then==='function')await result;return result}"
rows=[]
for candidate in sorted(root.rglob('pmp-p2c-production-enforcement-adapter-candidate-001.js')):
 text=candidate.read_text();n=text.count(adapter_old)
 if n==1:
  before=hashlib.sha256(candidate.read_bytes()).hexdigest();candidate.write_text(text.replace(adapter_old,adapter_new,1));after=hashlib.sha256(candidate.read_bytes()).hexdigest();rows.append({'path':str(candidate.relative_to(root)),'before_sha256':before,'after_sha256':after,'replacement_count':1})
if not rows:raise SystemExit('REHEARSAL099_ADAPTER_REGISTRATION_SCOPE_POINT_NOT_FOUND')
receipt={'type':'PMP_P2C_EXPLICIT_DOCUMENT_REGISTRATION_AUTHORITY_REPAIR_099','status':'PASS','prepare_path':str(prepare),'prepare_before_sha256':before_prepare,'prepare_after_sha256':after_prepare,'adapter_rows':rows,'registration_scope':'SYNCHRONOUS_DOCUMENT_ACTOR_EXECUTION_ONLY','callback_tokens_remain_lease_validated':True,'global_ambient_authority':False,'unknown_actor_policy_weakened':False,'production_changed':False,'proof_scope':'DISPOSABLE_COPY_ONLY'}
(out/'explicit-document-registration-authority-repair-099.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
