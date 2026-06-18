#!/usr/bin/env python3
from pathlib import Path

R = Path(__file__).resolve().parents[1]

def read(path):
    return (R / path).read_text(encoding='utf-8')

def need(condition, message):
    if not condition:
        raise SystemExit(message)

room = read('pmp-automated-plan-room-v1.js')
match = read('pmp-automated-plan-native-match-v1.js')
wrapper = read('pmp-current-inner-cleanbug-rgcontrols-v6.html')
app = read('pmp-home-single-v6.html')

need("const MAIN_LABEL='Automated Plan'" in room, 'universal label missing')
need('pmp-automated-plan-native-match-v1.js' in wrapper, 'native matcher not loaded')
need(wrapper.index('pmp-automated-plan-room-v1.js') < wrapper.index('pmp-automated-plan-native-match-v1.js'), 'native matcher must load after room')
need("old.disabled=true" in match, 'legacy duplicate visual rules are not disabled')
for native_class in ["'big'", "'wrap'", "'card'", "'grid'", "'panel pmp-ap-details"]:
    need(native_class in match, f'native class not enforced: {native_class}')
for native_class in ['big','mini','panel','note','sub','icon','chev']:
    need(native_class in room, f'room does not use native class: {native_class}')
for forbidden in ['font-family:', 'background:#', 'color:#', 'border-radius:28px']:
    need(forbidden not in match, f'native matcher defines separate visual value: {forbidden}')
need('background:var(--a)!important' in match, 'small controls do not follow the live accent variable')
need('color:var(--buttonText)!important' in match, 'small controls do not follow live contrast text')
need('box-shadow:var(--miniShadow)!important' in match, 'small controls do not follow live shadow settings')
need('Packet 01.5' not in match and 'packet_01_5' not in match, 'packet identity leaked into matcher')
need(match.count('Automated Plan') == 1, 'matcher should expose only the universal label')
need("id=\"control\"" in app or "id='control'" in app, 'real app Control Room not found')
need('class="big"' in app and 'class="mini"' in app and 'class="card"' in app, 'real app native classes not found')
print('AUTOMATED_PLAN_VISUAL_MATCH_STRUCTURE_PASS')
