#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import pathlib

RESOLVER = 'pmp-current-route-resolver-v1.js'
CAPABILITY = 'timer_schedule'
EXPECTED_TEMPLATE_TYPE = 'PMP_P2C_PRODUCTION_ENFORCEMENT_POLICY_CANDIDATE_002'
EXPECTED_BEFORE = ['network_fetch']
EXPECTED_AFTER = ['network_fetch', 'timer_schedule']
EXPECTED_FAIL_CLOSED = 'BLOCK_BEFORE_SIDE_EFFECT'

p = argparse.ArgumentParser()
p.add_argument('--policy-path', required=True)
p.add_argument('--evidence-dir', required=True)
a = p.parse_args()

policy_path = pathlib.Path(a.policy_path)
evidence_dir = pathlib.Path(a.evidence_dir)
evidence_dir.mkdir(parents=True, exist_ok=True)
if not policy_path.is_file():
    raise SystemExit(f'REHEARSAL102_POLICY_NOT_FOUND:{policy_path}')

raw_before = policy_path.read_bytes()
policy = json.loads(raw_before)
before = copy.deepcopy(policy)

if policy.get('type') != EXPECTED_TEMPLATE_TYPE:
    raise SystemExit(f"REHEARSAL102_POLICY_TYPE_INVALID:{policy.get('type')}")
if policy.get('unknown_actor_policy') != EXPECTED_FAIL_CLOSED:
    raise SystemExit(f"REHEARSAL102_UNKNOWN_ACTOR_POLICY_INVALID:{policy.get('unknown_actor_policy')}")
if policy.get('unauthorized_capability_policy') != EXPECTED_FAIL_CLOSED:
    raise SystemExit(f"REHEARSAL102_UNAUTHORIZED_CAPABILITY_POLICY_INVALID:{policy.get('unauthorized_capability_policy')}")

actors = policy.get('actors')
if not isinstance(actors, list):
    raise SystemExit('REHEARSAL102_ACTOR_LIST_INVALID')
matches = [actor for actor in actors if actor.get('path') == RESOLVER]
if len(matches) != 1:
    raise SystemExit(f'REHEARSAL102_RESOLVER_ACTOR_COUNT_INVALID:{len(matches)}')
resolver = matches[0]
capabilities_before = resolver.get('capabilities')
if capabilities_before != EXPECTED_BEFORE:
    raise SystemExit('REHEARSAL102_RESOLVER_CAPABILITIES_BEFORE_INVALID:' + json.dumps(capabilities_before, sort_keys=True))
resolver['capabilities'] = EXPECTED_AFTER

changed = []
for old_actor, new_actor in zip(before['actors'], policy['actors']):
    if old_actor != new_actor:
        changed.append(new_actor.get('path'))
if changed != [RESOLVER]:
    raise SystemExit('REHEARSAL102_CHANGED_ACTOR_SET_INVALID:' + json.dumps(changed, sort_keys=True))
if len(before['actors']) != len(policy['actors']):
    raise SystemExit('REHEARSAL102_ACTOR_COUNT_CHANGED')
if policy.get('type') != before.get('type'):
    raise SystemExit('REHEARSAL102_POLICY_TYPE_CHANGED')
if policy.get('unknown_actor_policy') != before.get('unknown_actor_policy'):
    raise SystemExit('REHEARSAL102_UNKNOWN_ACTOR_POLICY_CHANGED')
if policy.get('unauthorized_capability_policy') != before.get('unauthorized_capability_policy'):
    raise SystemExit('REHEARSAL102_UNAUTHORIZED_CAPABILITY_POLICY_CHANGED')

policy_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + '\n')
raw_after = policy_path.read_bytes()
verification = json.loads(raw_after)
resolver_after = [actor for actor in verification['actors'] if actor.get('path') == RESOLVER]
if len(resolver_after) != 1 or resolver_after[0].get('capabilities') != EXPECTED_AFTER:
    raise SystemExit('REHEARSAL102_RESOLVER_CAPABILITY_WRITE_VERIFICATION_FAILED')
if verification.get('type') != EXPECTED_TEMPLATE_TYPE:
    raise SystemExit('REHEARSAL102_POLICY_TYPE_WRITE_VERIFICATION_FAILED')
if verification.get('unknown_actor_policy') != EXPECTED_FAIL_CLOSED:
    raise SystemExit('REHEARSAL102_UNKNOWN_ACTOR_POLICY_WRITE_VERIFICATION_FAILED')
if verification.get('unauthorized_capability_policy') != EXPECTED_FAIL_CLOSED:
    raise SystemExit('REHEARSAL102_UNAUTHORIZED_CAPABILITY_POLICY_WRITE_VERIFICATION_FAILED')

evidence = {
    'type': 'PMP_P2C_RESOLVER_TIMER_SCHEDULE_CAPABILITY_REPAIR_102',
    'status': 'PASS',
    'policy_path': str(policy_path),
    'policy_type_before': before.get('type'),
    'policy_type_after': verification.get('type'),
    'actor_path': RESOLVER,
    'capability_added': CAPABILITY,
    'capabilities_before': capabilities_before,
    'capabilities_after': resolver_after[0]['capabilities'],
    'changed_actor_paths': changed,
    'actor_count_before': len(before['actors']),
    'actor_count_after': len(verification['actors']),
    'policy_sha256_before': hashlib.sha256(raw_before).hexdigest(),
    'policy_sha256_after': hashlib.sha256(raw_after).hexdigest(),
    'scope': 'EXACTLY_ONE_DECLARED_RESOLVER_ACTOR',
    'required_runtime_operation': {
        'operation': 'setTimeout',
        'delay_ms': 7000,
        'purpose': 'integrity_worker_status_timeout',
    },
    'unknown_actor_policy_before': before.get('unknown_actor_policy'),
    'unknown_actor_policy_after': verification.get('unknown_actor_policy'),
    'unauthorized_capability_policy_before': before.get('unauthorized_capability_policy'),
    'unauthorized_capability_policy_after': verification.get('unauthorized_capability_policy'),
    'unknown_actor_protection_weakened': False,
    'other_actor_capabilities_changed': False,
    'production_changed': False,
    'production_activation_authorized': False,
    'current_map_changed': False,
    'persisted_data_changed': False,
    'formal_proof_executed': False,
}
(evidence_dir / 'resolver-timer-schedule-capability-repair-102.json').write_text(
    json.dumps(evidence, indent=2, sort_keys=True) + '\n'
)
print(json.dumps(evidence, sort_keys=True))
