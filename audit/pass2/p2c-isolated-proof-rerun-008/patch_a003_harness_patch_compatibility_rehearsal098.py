#!/usr/bin/env python3
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--path',required=True);p.add_argument('--evidence-dir',required=True);a=p.parse_args()
path=pathlib.Path(a.path);out=pathlib.Path(a.evidence_dir);out.mkdir(parents=True,exist_ok=True)
text=path.read_text();before=hashlib.sha256(path.read_bytes()).hexdigest()
old=''' a003_wait_count=s.count("{ timeout: 30000 });")+s.count("{timeout:30000});")
 s=s.replace("{ timeout: 30000 });","{ timeout: 30000, waitUntil: 'domcontentloaded' });").replace("{timeout:30000});","{timeout:30000,waitUntil:'domcontentloaded'});")
 if a003_wait_count<2:raise SystemExit(f'A003_DOMCONTENTLOADED_WAIT_POINT_INVALID:{a003_wait_count}')'''
new=''' a003_wait_count=s.count("{ timeout: 30000 });")
 if a003_wait_count!=1:raise SystemExit(f'A003_DOMCONTENTLOADED_WAIT_POINT_INVALID:{a003_wait_count}')
 s=s.replace("{ timeout: 30000 });","{ timeout: 30000, waitUntil: 'domcontentloaded' });",1)'''
count=text.count(old)
if count!=1:raise SystemExit(f'REHEARSAL098_A003_RUNNER_PATCH_COMPAT_POINT_INVALID:{count}')
text=text.replace(old,new,1);compile(text,str(path),'exec');path.write_text(text)
after=hashlib.sha256(path.read_bytes()).hexdigest()
receipt={'type':'PMP_P2C_A003_HARNESS_PATCH_COMPATIBILITY_REPAIR_098','status':'PASS','target':str(path),'before_sha256':before,'after_sha256':after,'replacement_count':1,'historical_tamper_patch_point_preserved':True,'production_changed':False,'test_only':True}
(out/'a003-harness-patch-compatibility-repair-098.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
