#!/usr/bin/env python3
from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]


def read(path):
    return (R / path).read_text(encoding='utf-8')


def load(path):
    return json.loads(read(path))


def need(condition, message):
    if not condition:
        raise SystemExit(message)

room = read('pmp-automated-plan-room-v1.js')
match = read('pmp-automated-plan-native-match-v1.js')
legacy_wrapper = read('pmp-current-inner-cleanbug-rgcontrols-v6.html')
current_map = load('pmp-current-map-v12.json')
restore_shim = read('pmp-home-single-v6.html')

# The old Automated Plan visual contract is historical. Verify the successor and retirement boundary.
need('Continuous Run Dashboard' in room, 'superseding dashboard label missing')
need('pmpAutomatedPlanEntryV1' in room, 'shared entry anchor missing')
need('Continuous Run Dashboard' in match, 'native matcher is not aligned to the superseding dashboard')
need("old.disabled=true" in match, 'legacy duplicate visual rules are not disabled')
for native_class in ["'big'", "'wrap'", "'card'", "'grid'", "'panel pmp-ap-details"]:
    need(native_class in match, f'native class not enforced: {native_class}')
for forbidden in ['font-family:', 'background:#', 'color:#', 'border-radius:28px']:
    need(forbidden not in match, f'native matcher defines separate visual value: {forbidden}')
need('background:var(--a)!important' in match, 'small controls do not follow the live accent variable')
need('color:var(--buttonText)!important' in match, 'small controls do not follow live contrast text')
need('box-shadow:var(--miniShadow)!important' in match, 'small controls do not follow live shadow settings')
need('Packet 01.5' not in match and 'packet_01_5' not in match, 'packet identity leaked into matcher')

need('pmp-automated-plan-room-v1.js' in legacy_wrapper, 'legacy v6 wrapper does not preserve the old loader')
need(current_map['app_version'] == 'PMP-CURRENT-1-A003', 'current map is not A-003')
need(current_map['route_contract']['runtime_integrity_required'] is True, 'current map does not require runtime integrity')
need(current_map['current_app']['path'] == 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html', 'unexpected current app authority')
need(current_map['current_app']['path'] != 'pmp-current-inner-cleanbug-rgcontrols-v6.html', 'retired v6 wrapper still owns current authority')
need('historical_home_sha256_mismatch' in restore_shim, 'current Home restore shim does not enforce historical byte identity')
need('document.write' in restore_shim, 'current Home restore shim is not the A-003 verified restore path')

print(json.dumps({
    'type': 'PMP_AUTOMATED_PLAN_VISUAL_RETIREMENT_VERIFICATION_V1',
    'result': 'PASS',
    'historical_visual_assertion_retired': True,
    'superseding_ui_owner': 'Continuous Run Dashboard',
    'native_theme_match_preserved': True,
    'legacy_wrapper': 'pmp-current-inner-cleanbug-rgcontrols-v6.html',
    'legacy_wrapper_current_authority': False,
    'current_app': current_map['current_app']['path'],
    'current_home_mode': 'A-003 SHA-256 verified restore shim'
}, indent=2))
