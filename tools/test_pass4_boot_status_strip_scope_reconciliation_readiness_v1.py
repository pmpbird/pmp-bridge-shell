#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def main():
    audit=load('audit/pass4/pass4-boot-status-strip-scope-reconciliation-readiness-v1.json')
    roadmap=load('02_AUTHORITATIVE_13_PASS_ROADMAP.json')
    authority=load('audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json')
    assert audit['pass']==4 and audit['roadmap_name']=='Boot Status Strip'
    assert next(x for x in roadmap['roadmap'] if x['pass']==4)['name']=='Boot Status Strip'
    actor=next(x for x in authority['actors'] if x['actor']=='Boot Status Strip')
    assert set(actor['forbidden'])=={'change route','take app ownership','repair startup','modify storage'}
    assert audit['classification']['historical_work']=='NARROWER_HISTORICAL_COMPLETION'
    assert audit['classification']['current_path_revalidation_required'] is True
    assert audit['classification']['blind_rebuild_required'] is False
    assert len(audit['units'])==5
    assert [x['unit'] for x in audit['units']]==[1,2,3,4,5]
    assert audit['preservation']['runtime_changed_by_audit'] is False
    assert audit['preservation']['pass5_started'] is False
    for path in ['pmp-boot-status-strip-owner-v1.js','pmp-pass4-finalizer-receipt-v1.json','pmp-pass4-freeze-receipt-v1.json','pmp-route-guardian-current-loader-v22.html','pmp-current-map-v12.json']:
        assert (ROOT/path).is_file(), path
    freeze=load('pmp-pass4-freeze-receipt-v1.json')
    assert 'pmp-route-guardian-current-loader-v19.html' in freeze['frozen_live_path']
    cmap=load('pmp-current-map-v12.json')
    assert cmap['route_guardian']['path']=='pmp-route-guardian-current-loader-v22.html'
    print('PASS: Pass 4 historical scope reconciled against current verified path')
if __name__=='__main__': main()
