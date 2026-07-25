#!/usr/bin/env python3
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOADER=ROOT/'pmp-route-guardian-current-loader-v22.html'
MANIFEST=ROOT/'pmp-runtime-integrity-manifest-v1.json'
AUDIT=ROOT/'audit/pass3/pass3-passive-runtime-consumer-integration-unit2-v1.json'
MAP=ROOT/'pmp-current-map-v12.json'

def validate(m,h):
    req=('type','source_role','destination_role','map_path','map_version','route_epoch','destination_path')
    if not isinstance(h,dict) or any(not h.get(k) for k in req): return False
    return (h['type']=='PMP_ROUTE_HANDOFF_V1' and h['source_role']=='route_guardian' and
            h['destination_role']=='current_app' and h['map_path']=='pmp-current-map-v12.json' and
            h['map_version']==m['app_version'] and h['route_epoch']==m['route_epoch'] and
            h['destination_path']==m['current_app']['path'])

def main():
    text=LOADER.read_text(); m=json.loads(MAP.read_text()); audit=json.loads(AUDIT.read_text())
    assert audit['selected_consumer']==LOADER.name
    assert 'function canonicalContractHandoff' in text
    assert 'function validateCurrentAppHandoff' in text
    assert text.index('validateCurrentAppHandoff(loaded,handoff,contract)') < text.index('resolver.buildUrl(handoff')
    assert text.index('resolver.buildUrl(handoff') < text.index('location.href=launchUrl')
    assert "source_role:'route_guardian'" in text and "destination_role:'current_app'" in text
    assert "contract.map_path!=='pmp-current-map-v12.json'" in text
    good={'type':'PMP_ROUTE_HANDOFF_V1','source_role':'route_guardian','destination_role':'current_app','map_path':'pmp-current-map-v12.json','map_version':m['app_version'],'route_epoch':m['route_epoch'],'destination_path':m['current_app']['path']}
    assert validate(m,good)
    cases=[]
    for k in good:
        bad=copy.deepcopy(good); bad.pop(k); cases.append(bad)
    for k,v in [('type','OTHER'),('source_role','historic_guardian'),('destination_role','reload_owner'),('map_path','pmp-current-map-v11.json'),('map_version','stale'),('route_epoch','stale'),('destination_path','pmp-current-reload-owner-v27.html')]:
        bad=copy.deepcopy(good); bad[k]=v; cases.append(bad)
    assert all(not validate(m,b) for b in cases)
    data=LOADER.read_bytes(); manifest=json.loads(MANIFEST.read_text())
    rec=next(r for r in manifest['records'] if r['path']==LOADER.name)
    assert rec['bytes']==len(data)
    assert rec['sha256_hex']==hashlib.sha256(data).hexdigest()
    blob=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    assert rec['git_blob_sha']==blob
    assert audit['integration']['new_persisted_user_state_added'] is False
    assert audit['integrity']['current_map_changed'] is False and audit['integrity']['resolver_changed'] is False
    print(f'PASS: passive consumer source integration; 1 positive and {len(cases)} fail-closed contract cases')
if __name__=='__main__': main()
