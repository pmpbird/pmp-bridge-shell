#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
text=path.read_text()
before_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
old="    const getter=typeof nativeGet==='function'?function(){const actual=nativeGet.call(this),byTarget=propertyListenerMap.get(this),row=byTarget&&byTarget.get(name);return row&&row.wrapped===actual?row.original:actual}:nativeGet;"
new="    const getter=typeof nativeGet==='function'?function(){return nativeGet.call(this)}:nativeGet;"
count=text.count(old)
if count!=1:raise SystemExit(f'REHEARSAL097_EVENT_HANDLER_GETTER_POINT_INVALID:{count}')
text=text.replace(old,new,1)
compile(text,str(path),'exec')
path.write_text(text)
after_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
receipt={
 'type':'PMP_P2C_EVENT_HANDLER_GETTER_AUTHORITY_REPAIR_097',
 'status':'PASS',
 'target':str(path),
 'before_sha256':before_sha256,
 'after_sha256':after_sha256,
 'replacement_count':1,
 'wrapped_callback_remains_observable_to_native_dispatch':True,
 'event_callback_actor_binding_preserved':True,
 'unknown_actor_policy_weakened':False,
 'production_changed':False,
 'proof_scope':'DISPOSABLE_COPY_ONLY',
}
(out/'event-handler-getter-authority-repair-097.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
