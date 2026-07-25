#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
def main():
    plan=load('audit/pass3/pass3-scope-reconciliation-unit-plan-v1.json')
    u1=load('audit/pass3/pass3-route-guardian-handoff-contract-unit1-v1.json')
    u2=load('audit/pass3/pass3-route-guardian-handoff-unit2-passive-consumer-v1.json')
    u3=load('audit/pass3/pass3-route-guardian-handoff-unit3-isolated-proof-v1.json')
    u4=load('audit/pass3/pass3-route-guardian-handoff-unit4-live-observation-v1.json')
    live=load('audit/pass3/pass3-unit4-live-observation-result.json')
    close=load('audit/pass3/pass3-route-guardian-handoff-unit5-closure-certification-v1.json')
    cmap=load('pmp-current-map-v12.json')
    assert plan['pass']==3 and len(plan['units'])==5
    assert u1['handoff_type']=='PMP_ROUTE_HANDOFF_V1'
    assert u1['route_authority']=='pmp-current-map-v12.json'
    assert u2['selected_consumer']['path']=='pmp-route-guardian-current-loader-v22.html'
    assert u2['preservation']['current_map_destination_truth_changed'] is False
    assert u3['status']=='PASS' and u3['canonical_accepts']==1 and u3['fail_closed_rejections']==19
    assert u3['zero_navigation_assignments'] and u3['zero_persisted_user_data_writes']
    assert u4['status']=='EVIDENCE_ONLY_PENDING_MERGE'
    assert any(x['unit']==4 and x['merged_pr']==140 for x in close['completed_units'])
    assert live['canonical']['consumer_accepted_before_navigation'] is True
    assert live['canonical']['app_orchestrator_acknowledged'] is True
    assert live['invalid_probe']['blocked_before_navigation'] is True
    assert live['invalid_probe']['navigation_assignments']==0
    assert live['invalid_probe']['persisted_user_data_writes']==0
    assert cmap['route_guardian']['path']=='pmp-route-guardian-current-loader-v22.html'
    assert cmap['current_app']['path']==live['canonical']['current_app']
    guardian=(ROOT/'pmp-route-guardian-current-loader-v22.html').read_text()
    assert 'consumeCurrentAppHandoff(loaded,handoff)' in guardian
    assert guardian.index('consumeCurrentAppHandoff(loaded,handoff)') < guardian.index('resolver.buildUrl(handoff')
    assert close['pass3_completion']=='CERTIFIED_PENDING_MERGE'
    assert close['closure_findings']['pass4_started'] is False
    assert close['preservation']['runtime_files_changed_by_unit5'] is False
    print('PASS: Units 1-4 collectively satisfy current-roadmap Pass 3 closure criteria')
if __name__=='__main__': main()
