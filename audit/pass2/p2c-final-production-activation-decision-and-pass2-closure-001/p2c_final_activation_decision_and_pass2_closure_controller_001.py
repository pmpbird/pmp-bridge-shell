#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);p.add_argument('--decision',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 r=json.loads(a.review.read_text());d=json.loads(a.decision.read_text());c=json.loads(a.closure.read_text())
 checks={
  'review_fail_closed':r['verified_proof_status']=='INCOMPLETE_FAILED_CANNOT_SUPPORT_ACTIVATION_OR_PASS2_CLOSURE',
  'decision_hold':d['decision']=='HOLD_DO_NOT_ACTIVATE',
  'activation_not_authorized':d['production_activation_authorized'] is False and d['production_application_authorized'] is False,
  'closure_not_certified':c['certification_status']=='NOT_CERTIFIED_FAIL_CLOSED' and c['pass2_complete'] is False,
  'production_untouched':all([r['production_runtime_changed_by_review'] is False,r['current_map_changed'] is False,r['storage_changed'] is False,r['indexeddb_changed'] is False,r['cache_storage_changed'] is False,r['bank_changed'] is False]),
  'pass3_not_started':c['pass3_started'] is False
 }
 out={'type':'PMP_P2C_FINAL_ACTIVATION_DECISION_AND_PASS2_CLOSURE_CONTROLLER_RESULT_001','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'decision':d['decision'],'closure_certification':c['certification_status'],'production_patch_applied':False,'pass2_complete':False,'pass3_started':False}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
