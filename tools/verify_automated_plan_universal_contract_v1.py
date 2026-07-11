#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def load(p): return json.loads((R / p).read_text(encoding='utf-8'))
def read(p): return (R / p).read_text(encoding='utf-8')
def need(c, m):
    if not c: raise SystemExit(m)
def fields(o, names, label): need(not [n for n in names if n not in o], f'{label} missing required fields')
def exact(a, b, label): need(set(a) == set(b), f'{label} mismatch')
def all_false(o, names, label):
    for n in names: need(o[n] is False, f'{label}.{n} must be false')

policy = load('automation/engine/v1/engine-policy.json')
contract = load('automation/engine/v1/universal-contract.json')
plan = load('automation/plans/packet-01-5.v1.json')
state = load('automation/state/active-plan.json')
usage = load('automation/state/usage-ledger.json')
room = read('pmp-automated-plan-room-v1.js')
native_match = read('pmp-automated-plan-native-match-v1.js')
legacy_wrapper = read('pmp-current-inner-cleanbug-rgcontrols-v6.html')
current_map = load('pmp-current-map-v12.json')
workflow = read('.github/workflows/automated_plan_foundation.yml')

backends = {'github_models_free', 'local_ollama'}
stops = {
  'execution_disabled','plan_not_compiled','schema_invalid','plan_identity_mismatch',
  'checkpoint_mismatch','authoritative_main_changed','backend_unavailable',
  'free_limit_reached','paid_path_detected','unsafe_permission_detected',
  'changed_file_outside_allowlist','deterministic_verification_failed',
  'independent_rebuild_mismatch','unresolved_ambiguity','manual_stop_requested'
}

need(contract['type'] == 'PMP_UNIVERSAL_AUTOMATED_PLAN_CONTRACT', 'wrong contract type')
need(contract['version'] == '1.0.0', 'wrong contract version')
exact(contract['schema_registry'], {'plan','checkpoint','result_envelope','usage_ledger','evidence_capsule'}, 'schema registry')
for name, schema in contract['schema_registry'].items():
    fields(schema, ['schema_id','required_fields'], f'schema {name}')
    need(bool(schema['required_fields']), f'schema {name} has no required fields')

machine = contract['state_machine']
need(machine['initial_status'] == 'setup', 'wrong initial state')
need('paused' in machine['transitions']['running'], 'running cannot pause')
need('running' in machine['transitions']['paused'], 'paused cannot resume')
for n in ['pause_commits_checkpoint_before_exit','resume_starts_from_stored_next_unit','resume_requires_plan_identity_match','resume_requires_live_main_reverification','resume_must_not_repeat_verified_completed_units','resume_must_not_skip_unverified_units']:
    need(machine['pause_resume'][n] is True, f'pause/resume guard false: {n}')
exact(contract['stop_conditions'], stops, 'contract stop conditions')

bc = contract['backend_contract']
need(bc['request_schema_id'] == 'pmp.automated-plan.evidence-capsule.v1', 'request schema mismatch')
need(bc['result_schema_id'] == 'pmp.automated-plan.result.v1', 'result schema mismatch')
need(bc['checkpoint_schema_id'] == 'pmp.automated-plan.checkpoint.v1', 'checkpoint schema mismatch')
need(bc['common_authority'] == 'proposal_only', 'backend authority widened')
exact([b['backend_id'] for b in bc['backends']], backends, 'contract backends')
for b in bc['backends']:
    all_false(b, ['requires_paid_api_key','model_may_write_repository','model_may_merge'], b['backend_id'])
for n in ['same_plan_id','same_plan_version','same_checkpoint_schema','same_result_schema','same_next_unit','same_stop_conditions','same_independent_verification','checkpoint_reverified_before_resume']:
    need(n in bc['switching_invariants'], f'missing switch invariant: {n}')

um = contract['usage_measurement']
need(um['minimum_completed_pass_samples_for_estimate'] >= 3, 'usage sample floor too small')
need(um['no_estimate_without_samples'] is True, 'usage may guess')
need(um['rate_limit_behavior'] == 'checkpoint_then_pause_without_paid_fallback', 'wrong rate-limit behavior')

checks = set(contract['independent_verification']['checks'])
need(contract['independent_verification']['required'] is True, 'independent verification optional')
for n in ['schema_validation','checkpoint_continuity_validation','authoritative_main_validation','changed_file_allowlist_validation','zero_cost_policy_validation','backend_authority_validation','independent_rebuild_or_equivalent_deterministic_check','locked_reviewed_head_validation_before_merge','merge_parent_validation_after_merge']:
    need(n in checks, f'missing verification check: {n}')

need(policy['contract_path'] == 'automation/engine/v1/universal-contract.json', 'policy contract mismatch')
need(policy['usage_ledger_path'] == 'automation/state/usage-ledger.json', 'policy usage mismatch')
need(policy['cost_policy']['spending_ceiling_usd'] == 0, 'spending ceiling not zero')
all_false(policy['cost_policy'], ['paid_api_allowed','paid_fallback_allowed','larger_paid_github_runners_allowed','automatic_cost_escalation_allowed'], 'cost_policy')
exact([b['backend_id'] for b in policy['execution_backends']], backends, 'policy backends')
need(policy['backend_switching']['redesign_required'] is False, 'backend switch requires redesign')
need(policy['backend_switching']['checkpoint_reverification_required'] is True, 'backend switch lacks reverify')
need(policy['authority']['model_output_authority'] == 'proposal_only', 'model authority widened')
all_false(policy['authority'], ['model_may_write_main_directly','model_may_write_repository_directly','model_may_merge_directly'], 'authority')
all_false(policy['execution_defaults'], ['execution_enabled','autonomous_trigger_enabled','merge_authority_granted','pass_003_started'], 'execution_defaults')

fields(plan, contract['schema_registry']['plan']['required_fields'], 'plan')
need(plan['plan_id'] == 'packet_01_5' and plan['plan_version'] == '1.0.0', 'plan identity/version changed')
need(plan['user_facing_main_entry'] == 'Automated Plan', 'historical plan entry identity changed')
need(plan['plan_status'] == 'registered_not_compiled' and plan['execution_enabled'] is False, 'plan falsely executable')
need(plan['continuity']['last_completed_boundary'] == 'pass_002', 'Pass 002 checkpoint lost')
need(plan['continuity']['next_declared_boundary'] == 'pass_003', 'Pass 003 next boundary lost')
need(plan['compiled_units'] == [], 'foundation contains executable units')
exact(plan['backend_policy']['allowed_backends'], backends, 'plan backends')
need(plan['backend_policy']['same_contract_on_switch'] is True, 'plan contract changes by backend')
need(plan['backend_policy']['paid_fallback_allowed'] is False, 'plan paid fallback allowed')
exact(plan['stop_conditions'], stops, 'plan stop conditions')

need(state['active_plan_id'] == plan['plan_id'] and state['active_plan_version'] == plan['plan_version'], 'state plan mismatch')
need(state['status'] == 'setup' and state['execution_enabled'] is False, 'state falsely executable')
fields(state['checkpoint'], contract['schema_registry']['checkpoint']['required_fields'], 'checkpoint')
need(state['checkpoint']['last_completed_boundary'] == 'pass_002', 'state lost Pass 002')
need(state['checkpoint']['last_verified_unit'] == 'pass_002', 'state lost verified Pass 002')
need(state['checkpoint']['next_unit'] == 'pass_003', 'state lost Pass 003')
need(state['checkpoint']['resume_requires_live_main_reverification'] is True, 'resume skips main reverify')
need(state['recovery']['resume_strategy'] == 'exact_checkpoint', 'wrong resume strategy')
need(state['recovery']['on_interruption'] == 'resume_same_unit', 'wrong interruption recovery')
need(state['recovery']['on_rate_limit'] == 'pause_and_resume_after_reset', 'wrong free-limit recovery')
need(state['recovery']['on_backend_change'] == 'continue_same_unit_after_checkpoint_reverification', 'wrong backend recovery')
need(state['execution']['requested_action'] == 'none', 'execution requested')
need(state['execution']['write_authority'] == 'none' and state['execution']['merge_authority'] == 'none', 'authority granted')
need(state['execution']['spending_ceiling_usd'] == 0, 'state spending ceiling not zero')
need(state['execution']['stop_reason'] == 'foundation_only_not_enabled', 'wrong stop reason')

fields(usage, contract['schema_registry']['usage_ledger']['required_fields'], 'usage ledger')
need(usage['plan_id'] == plan['plan_id'], 'usage plan mismatch')
need(usage['measurement_status'] == 'not_started', 'usage falsely measured')
need(all(v == 0 for v in usage['totals'].values()), 'usage totals not zero')
need(usage['completed_pass_samples'] == [], 'invented usage samples')
need(usage['estimate']['sample_count'] == 0, 'invented sample count')
need(usage['estimate']['estimated_remaining_passes_today'] is None, 'invented pass estimate')
need(usage['estimate']['claim'] == 'not_enough_data', 'usage claim not truthful')

# The old UI assertion is formally retired; verify the superseding owner and authority boundary instead.
need('Continuous Run Dashboard' in room, 'superseding Continuous Run Dashboard label missing')
need('pmpAutomatedPlanEntryV1' in room, 'shared historical entry anchor missing')
need('Continuous Run Dashboard' in native_match, 'native matcher not aligned to superseding owner')
need('Packet 01.5' not in room and 'packet_01_5' not in room, 'packet identity leaked to superseding interface source')
need('pmp-automated-plan-room-v1.js' in legacy_wrapper, 'legacy v6 wrapper no longer preserves historical loader')
need(current_map['app_version'] == 'PMP-CURRENT-1-A003', 'current map is not A-003')
need(current_map['route_contract']['runtime_integrity_required'] is True, 'current runtime integrity is not required')
need(current_map['current_app']['path'] != 'pmp-current-inner-cleanbug-rgcontrols-v6.html', 'retired wrapper still owns current app authority')
need(policy['interface']['control_room_entry_count'] == 1, 'historical foundation allowed more than one entry')
all_false(policy['interface'], ['separate_color_palette_allowed','separate_contrast_system_allowed'], 'interface')

compact = workflow.replace(' ', '').lower()
need('permissions:\n  contents: read' in workflow, 'workflow not read-only')
need('contents:write' not in compact and 'pull-requests:write' not in compact, 'workflow has write permission')
for t in ['repository_dispatch:','workflow_run:','schedule:']:
    need(t not in workflow, f'autonomous trigger enabled: {t}')

combined = '\n'.join(read(p) for p in ['automation/engine/v1/engine-policy.json','automation/engine/v1/universal-contract.json','automation/plans/packet-01-5.v1.json','automation/state/active-plan.json','automation/state/usage-ledger.json','.github/workflows/automated_plan_foundation.yml'])
for token in ['OPENAI_API_KEY','api.openai.com','"paid_api_allowed": true','"paid_fallback_allowed": true','"execution_enabled": true','"autonomous_trigger_enabled": true','"merge_authority_granted": true','"model_may_write_repository": true','"model_may_merge": true']:
    need(token not in combined, f'prohibited token found: {token}')

all_false(contract['foundation_boundary'], ['execution_enabled','autonomous_trigger_enabled','merge_authority_granted','pass_003_started'], 'foundation_boundary')
print(json.dumps({
    'type':'PMP_AUTOMATED_PLAN_UNIVERSAL_CONTRACT_RETIREMENT_VERIFICATION_V1',
    'result':'PASS',
    'historical_contract_preserved':True,
    'superseding_ui_owner':'Continuous Run Dashboard',
    'legacy_v6_current_authority':False,
    'current_app':current_map['current_app']['path'],
    'runtime_integrity_required':True,
    'active_plan_id':state['active_plan_id'],
    'last_completed_boundary':'pass_002',
    'next_unit':'pass_003',
    'resume_strategy':'exact_checkpoint',
    'backends':sorted(backends),
    'backend_redesign_required':False,
    'usage_measurement_status':'not_started',
    'usage_estimate':None,
    'spending_ceiling_usd':0,
    'model_authority':'proposal_only',
    'execution_enabled':False,
    'pass_003_started':False
}, indent=2))
