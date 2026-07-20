#!/usr/bin/env python3
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--path',required=True);p.add_argument('--evidence-dir',required=True);a=p.parse_args()
path=pathlib.Path(a.path);out=pathlib.Path(a.evidence_dir);out.mkdir(parents=True,exist_ok=True)
text=path.read_text();before=hashlib.sha256(path.read_bytes()).hexdigest()
write_anchor=' gate_path.write_text(g)'
injection=r''' ledger_state_old="const state={configured:false,installed:false,policy:null,actors:new Map(),manifest:new Map(),current:null,registrationToken:null,denials:[],native:{},listenerMap:new WeakMap()};"
 ledger_state_new="const state={configured:false,installed:false,policy:null,actors:new Map(),manifest:new Map(),current:null,registrationToken:null,denials:[],eventPropertyRegistrations:[],eventPropertyInvocations:[],native:{},listenerMap:new WeakMap()};"
 if g.count(ledger_state_old)!=1:raise SystemExit(f'R100_GATE_LEDGER_STATE_POINT_INVALID:{g.count(ledger_state_old)}')
 g=g.replace(ledger_state_old,ledger_state_new,1)
 ledger_setter_old="""      if(typeof value==='function'){
        const wrapped=wrapCallback(token,value);byTarget.set(name,{original:value,wrapped});return nativeSet.call(this,wrapped)
      }"""
 ledger_setter_new="""      if(typeof value==='function'){
        const base=wrapCallback(token,value),actorPath=token.actor&&token.actor.path||null,targetId=this&&this.id||null,targetTag=this&&this.tagName||null;
        let invocationCount=0;
        const wrapped=function(){invocationCount++;state.eventPropertyInvocations.push({at:now(),actor_path:actorPath,property:String(name),target_id:targetId,target_tag:targetTag,invocation_count:invocationCount});if(state.eventPropertyInvocations.length>64)state.eventPropertyInvocations.shift();return base.apply(this,arguments)};
        try{Object.defineProperties(wrapped,{__pmpActorPath:{value:actorPath},__pmpEventProperty:{value:String(name)},__pmpInvocationCount:{get:()=>invocationCount}})}catch(e){}
        state.eventPropertyRegistrations.push({at:now(),actor_path:actorPath,property:String(name),target_id:targetId,target_tag:targetTag});if(state.eventPropertyRegistrations.length>64)state.eventPropertyRegistrations.shift();
        byTarget.set(name,{original:value,wrapped});return nativeSet.call(this,wrapped)
      }"""
 if g.count(ledger_setter_old)!=1:raise SystemExit(f'R100_GATE_LEDGER_SETTER_POINT_INVALID:{g.count(ledger_setter_old)}')
 g=g.replace(ledger_setter_old,ledger_setter_new,1)
 ledger_report_old="event_handler_setter_count:state.eventHandlerSetterCount||0,pass2_complete:false"
 ledger_report_new="event_handler_setter_count:state.eventHandlerSetterCount||0,event_property_registration_count:state.eventPropertyRegistrations.length,event_property_invocation_count:state.eventPropertyInvocations.length,event_property_registrations:state.eventPropertyRegistrations.map(clone),event_property_invocations:state.eventPropertyInvocations.map(clone),pass2_complete:false"
 if g.count(ledger_report_old)!=1:raise SystemExit(f'R100_GATE_LEDGER_REPORT_POINT_INVALID:{g.count(ledger_report_old)}')
 g=g.replace(ledger_report_old,ledger_report_new,1)
 gate_path.write_text(g)'''
count=text.count(write_anchor)
if count!=1:raise SystemExit(f'REHEARSAL100_GATE_WRITE_POINT_INVALID:{count}')
text=text.replace(write_anchor,injection,1);compile(text,str(path),'exec');path.write_text(text)
after=hashlib.sha256(path.read_bytes()).hexdigest()
receipt={'type':'PMP_P2C_EVENT_PROPERTY_REGISTRATION_LEDGER_REPAIR_100','status':'PASS','target':str(path),'before_sha256':before,'after_sha256':after,'registration_rows_capped':64,'invocation_rows_capped':64,'test_only':True,'production_changed':False,'authority_decision_changed':False,'unknown_actor_policy_weakened':False}
(out/'event-property-registration-ledger-repair-100.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
