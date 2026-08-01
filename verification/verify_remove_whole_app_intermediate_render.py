from pathlib import Path
import json

src = Path('pmp-diagnostics-consolidated-view-v1.js').read_text()
checks = {
    'version': '2.7.0-deferred-whole-app-open-20260731O' in src,
    'deferred_open': 'openWholeAppWhenReady' in src,
    'final_render_after_evidence': "renderDetail(w,d,'whole_app',true)" in src,
    'old_loading_card_removed': 'pmpDiagRunningV1' not in src,
    'no_authority_change': all(x in src for x in ['ownership_changes:false','helper_changes:false','route_changes:false','storage_migration:false'])
}
result = {'type':'PMP_REMOVE_WHOLE_APP_INTERMEDIATE_RENDER_VERIFICATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['status']=='PASS' else 1)
