#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def main():
    record=load('audit/pass4/pass4-boot-status-strip-unit1-current-path-contract-boundary-v1.json')
    readiness=load('audit/pass4/pass4-boot-status-strip-scope-reconciliation-readiness-v1.json')
    authority=load('audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json')
    cmap=load('pmp-current-map-v12.json')
    assert record['pass']==4 and record['unit']==1
    assert readiness['pass']==4 and len(readiness['units'])==5
    actor=next(x for x in authority['actors'] if x['actor']=='Boot Status Strip')
    assert set(actor['forbidden'])=={'change route','take app ownership','repair startup','modify storage'}
    contract=record['contract']
    assert contract['type']=='PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1'
    assert contract['required_states']==['BOOTING','BOOT_SLOW','BOOT_FAILURE','READY_ACKNOWLEDGED']
    assert contract['required_zero_effects']=={
        'route_assignments':0,
        'persisted_user_data_writes':0,
        'app_orchestrator_ownership_transfers':0,
        'startup_repairs':0,
    }
    boundary=record['selected_boundary']
    assert boundary['consumer_file']=='pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'
    assert boundary['read_only_inputs_only'] is True
    assert boundary['no_runtime_change_in_unit1'] is True
    assert cmap['route_guardian']['path']=='pmp-route-guardian-current-loader-v22.html'
    assert cmap['current_app']['path']=='pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html'
    inner=(ROOT/boundary['consumer_file']).read_text()
    assert 'pmp-app-orchestrator-v1.js' in inner
    assert record['preservation']['unit2_started'] is False
    assert record['preservation']['pass5_started'] is False
    print('PASS: current-path passive Boot Status Strip contract and boundary are locked')
if __name__=='__main__': main()
