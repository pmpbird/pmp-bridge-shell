#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
A = 'fae1b37e6088d1e6333b51427e1e7184a7e90c29'
F = 'OTHER_RECORD_SPECIFIC_PROOF'
QUEUE = 'audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW = 'audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY = 'audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY = 'audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
RECEIPTS = {
    'current_runtime_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json', '5942c78a331d078b11364f46313079df3d9e887f'),
    'private_uncaptured_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json', '92045d7fa63839582ec518066033d58fede2ed8c'),
    'deployment_live_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json', '84d580215ee70c3c1e6b0b5a2d606c0c5d690eac'),
    'dependency_platform_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json', '7ccb9a57451e80ced1a88de47406e92b7dc0b486'),
    'cross_source_conflict_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Independent_Verification_v1.json', '3e7df143344d51b4be07e3cd25cd6d3be78edee9'),
    'authoritative_packet_law_family_receipt_blob_sha': ('audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Independent_Verification_v1.json', '10e46b2498a3bff34bbd4a5afd82a125be3fc0b8'),
}
CENSUS = R / 'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Census_v1.json'
DEC = R / 'audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Decisions_v1.jsonl'
REM = R / 'audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Remaining_Queue_v1.jsonl'
COV = R / 'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Coverage_v1.json'
STAT = R / 'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Status_v1.md'
IDENTITY_KEYS = ('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')

def git(*args: str) -> str:
    p = subprocess.run(['git', *args], cwd=R, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode(errors='replace').strip()

def show(path: str) -> bytes:
    return subprocess.run(['git','show',f'{A}:{path}'], cwd=R, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def rows(data: bytes) -> list[dict]:
    return [json.loads(x) for x in data.decode().splitlines() if x.strip()]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def write_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(canonical(x) + '\n' for x in values))

def exact_proof(q: dict) -> str:
    return (
        f"Provide one current, independently verifiable address-specific evidence receipt bound to {q['composite_address']} "
        f"and the complete preserved claim: {q['preserved_claim']} The receipt must identify the exact evidence source, "
        "capture the current acquisition date, immutable content hash, authority or provenance status, reproducible acquisition steps, "
        "and an independently repeatable PASS/FAIL verdict proving or disproving the entire claim without borrowing evidence from another address or family."
    )

def status(addresses: list[str]) -> str:
    return f'''# Packet 01.5 Pass 002 — Other Record Specific Proof Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative anchor: `{A}`
- Family records: 79
- Permanent-address count: {len(addresses)}
- Direct decisions: 0
- Exact remaining queues: 79
- Automatic `UNKNOWN — HOLD`: 0
- Address-specific direct-evidence receipts reviewed: 0
- Exact evidence sources identified: 0
- Current evidence dates verified: no
- Immutable evidence hashes verified: no
- Provenance statuses verified: no
- Reproducible acquisition verified: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 122 processed + 0 remaining = 122

No current independently verifiable address-specific receipt met the complete-claim decision gate. All 79 prior `UNCLASSIFIED` states remain preserved and all 79 records remain queued for the smallest exact proof required.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, Pass 002 consolidation, or Packet 04 work occurred.
'''

def main() -> None:
    git('cat-file', '-e', f'{A}^{{commit}}')
    qb, wb, ib, ob = show(QUEUE), show(WINDOW), show(INVENTORY), show(OVERLAY)
    queue = rows(qb)
    selected = sorted((x for x in queue if x.get('evidence_domain') == F), key=lambda x: x['inventory_position'])
    addresses = [x['composite_address'] for x in selected]
    assert len(queue) == 122
    assert len(selected) == len(addresses) == len(set(addresses)) == 79
    assert addresses == sorted(addresses, key=lambda a: next(x['inventory_position'] for x in selected if x['composite_address'] == a))
    for q in selected:
        assert q['queue_id'] == 'SP002-OTHER_RECORD_SPECIFIC_PROOF'
        assert q['prior_applicability_state'] == 'UNCLASSIFIED'
        assert q['prior_applicability_decision_hash'] is None
        assert q['state_preservation_rule'] == 'PRESERVE_CURRENT_STATE_UNTIL_DIRECT_MERGED_EVIDENCE_SUPPORTS_A_DECISION'
        for key in IDENTITY_KEYS:
            assert key in q
    assert len(rows(ib)) == len(rows(ob)) == 2750
    assert sha(qb) == '0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
    assert sha(wb) == 'eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
    assert sha(ib) == '76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
    assert sha(ob) == '465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
    receipt_values = {}
    for key, (path, expected) in RECEIPTS.items():
        actual = git('rev-parse', f'{A}:{path}')
        assert actual == expected
        receipt_values[key] = actual
    census = {
        'packet': '01.5', 'pass': '002', 'family': F, 'authoritative_anchor': A,
        'family_records': 79, 'addresses_in_inventory_order': addresses,
        'source_pass_distribution': {str(p): sum(1 for x in selected if x['source_pass'] == p) for p in sorted({x['source_pass'] for x in selected})},
        'records': [{k: q[k] for k in IDENTITY_KEYS} for q in selected],
    }
    remaining = []
    for q in selected:
        remaining.append({
            **q,
            'family': F,
            'family_result': 'REMAIN_QUEUED',
            'family_inspection_status': 'NO_CURRENT_ADDRESS_SPECIFIC_DIRECT_EVIDENCE_RECEIPT',
            'direct_decision_supported': False,
            'address_specific_evidence_receipts_reviewed': 0,
            'exact_evidence_source_identified': False,
            'current_evidence_date_verified': False,
            'immutable_evidence_hash_verified': False,
            'provenance_status_verified': False,
            'reproducible_acquisition_verified': False,
            'smallest_exact_remaining_proof': exact_proof(q),
            'prior_state_preserved': True,
        })
    coverage = {
        'packet': '01.5', 'pass': '002', 'family': F, 'authoritative_anchor': A,
        'family_records': 79, 'decided_records': 0, 'remaining_queued_records': 79,
        'unknown_hold_created': 0, 'complete_nonduplicated_coverage': True,
        'direct_decision_gate_matches': 0, 'address_specific_evidence_receipts_reviewed': 0,
        'exact_evidence_sources_identified': 0, 'current_evidence_dates_verified': False,
        'immutable_evidence_hashes_verified': False, 'provenance_statuses_verified': False,
        'reproducible_acquisition_verified': False,
        'pass_002_total_records': 122, 'previously_processed_records': 43,
        'family_records_accounted': 79, 'processed_records_if_merged': 122,
        'remaining_unprocessed_records': 0, 'pass_002_reconciliation_exact': True,
        'queue_sha256': sha(qb), 'window_sha256': sha(wb),
        'source_inventory_sha256': sha(ib), 'source_inventory_count': 2750, 'source_inventory_unchanged': True,
        'pass_002_overlay_sha256': sha(ob), 'pass_002_overlay_count': 2750, 'pass_002_overlay_unchanged': True,
        **receipt_values,
        'previously_merged_family_artifacts_unchanged': True,
        'records_outside_family_unchanged': True,
        'evidence_reacquired': False, 'other_evidence_families_processed': False,
        'application_behavior_modified': False, 'configuration_modified': False,
        'dependencies_modified': False, 'deployment_modified': False, 'runtime_state_modified': False,
        'routing_assignments': 0, 'destination_assignments': 0, 'grouping_assignments': 0,
        'source_records_removed_or_closed': 0, 'implementation_actions': 0, 'packet_04_actions': 0,
    }
    write_json(CENSUS, census)
    write_jsonl(DEC, [])
    write_jsonl(REM, remaining)
    write_json(COV, coverage)
    STAT.write_text(status(addresses))
    print(json.dumps({'status':'BUILT','family_records':79,'decisions':0,'remaining_queue':79,'addresses':addresses}, indent=2))

if __name__ == '__main__':
    main()
