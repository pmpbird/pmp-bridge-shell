#!/usr/bin/env python3
import json
import subprocess
import textwrap

node = r'''
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('pmp-mount-registry-v1.js','utf8');
const storage={};
const doc={location:{pathname:'/pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html'},querySelectorAll:()=>[]};
const localStorage={setItem:(k,v)=>storage[k]=String(v),getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null};
const sandbox={
  window:null,top:null,document:doc,localStorage,
  setTimeout:()=>0,setInterval:()=>0,clearTimeout:()=>{},clearInterval:()=>{},
  Date,JSON,Array,Set,String,Object,RegExp
};
sandbox.window=sandbox;sandbox.top=sandbox;
vm.createContext(sandbox);vm.runInContext(src,sandbox,{filename:'pmp-mount-registry-v1.js'});
const api=sandbox.PMPMountRegistryV1;
if(!api)throw new Error('PMPMountRegistryV1 unavailable');
const r=api.registry();
const out={version:api.version,buckets:r.atlas_buckets.map(x=>x.id),classification:r.repo_file_classification,files:r.files,slots:r.slots,merge:r.active_discovery_merge,rule:r.rule};
process.stdout.write(JSON.stringify(out));
'''
proc=subprocess.run(['node','-e',node],text=True,capture_output=True,check=False)
assert proc.returncode == 0, proc.stderr
r=json.loads(proc.stdout)

assert r['version']=='1.7.0-registry-completeness-semantics-20260826A'
assert 'RECOVERY_REACHABLE' in r['buckets']
assert 'INTENTIONAL_OUTSIDE_ACTIVE_ATLAS' in r['buckets']
recovery=set(r['classification']['RECOVERY_REACHABLE'])
outside=set(r['classification']['INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'])
assert len(recovery)==10, len(recovery)
assert len(outside)==22, len(outside)
assert r['merge']['recovery_count']==10
assert r['merge']['intentional_outside_count']==22
assert all(x['bucket']!='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS' for x in r['slots'])
outside_rows={x['path'] for x in r['files'] if x['bucket']=='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'}
assert outside_rows==outside
assert 'pmp-route-guardian-last-good-clean-v1.js' in recovery
assert 'pmp-route-guardian-last-good-clean-v1.js' not in set(r['classification']['ACTIVE_CURRENT_APP'])
assert 'pmp-runtime-integrity-manifest-v1.json' in set(r['classification']['ACTIVE_CURRENT_APP'])
assert 'resident.html' in set(r['classification']['SUPPORT_REACHABLE'])
assert 'no authority is granted by registry presence' in r['rule']

print('PASS atlas registry completeness and semantics independent verifier')
