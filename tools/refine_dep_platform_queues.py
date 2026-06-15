#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'audit/applicability/Packet_01.5_Dependency_Platform_Family_Remaining_Queue_v1.jsonl'

DETAILS = {
    'BUILD-006': (
        'A current dependency lock record and a verified reproducible build and artifact-generation recipe are missing.',
        'Add the applicable manifest and lockfile, document exact build and artifact commands, then produce a clean-room reproducibility receipt with content digests.',
        'The complete build-identity predicate is not satisfied.',
        'A manifest, lockfile, build recipe, toolchain version, artifact format, or reproducibility receipt changes.'),
    'BUILD-008': (
        'A complete dependency inventory, verified lock-integrity receipt, SBOM, vulnerability review, and license review are missing as one current evidence suite.',
        'Generate a version-bound dependency inventory and SBOM, verify lock integrity, run vulnerability and license reviews, and retain digest-bound receipts.',
        'The complete supply-chain evidence suite is not present.',
        'A dependency, lock, SBOM, vulnerability result, license result, or review receipt changes.'),
    'BUILD-011': (
        'An approved release manifest binding code, laws, prompts, schemas, tests, and provider settings to exact versions and content digests is missing.',
        'Create one release-identity record that names and hashes every required component, then independently verify that the effective release matches it.',
        'Current records describe some components but do not establish one complete release identity.',
        'Any release component, version, digest, provider setting, or release-manifest rule changes.'),
    'OPS-003': (
        'An approved maintenance policy assigning owners and update cadence for dependencies, providers, benchmarks, and device compatibility is missing.',
        'Approve a maintenance matrix naming each category, responsible owner, review cadence, update trigger, and required receipt.',
        'Responsibility or cadence is incomplete across the full preserved claim.',
        'An owner, dependency, provider, benchmark, supported device, cadence, or maintenance rule changes.'),
    'OPS-004': (
        'A verified legal, terms, license, and privacy review covering AI providers, Cloudflare, GitHub, Apple Shortcuts and Notes, and dependencies is incomplete.',
        'Bind the exact services and versions, review their current governing terms and licenses, record privacy and data obligations, and approve a dated digest-bound receipt.',
        'Current dependency records identify services but do not prove the complete reviewed set.',
        'A service, dependency, license, term, privacy policy, account region, or review receipt changes.'),
    'OPS-006': (
        'An approved data-classification decision explicitly stating what source code and project context may and may not be sent to each AI provider is missing.',
        'Create a provider-specific classification matrix with allowed, prohibited, redaction, consent, and retention rules, then approve and digest it.',
        'Current data-boundary references do not directly decide the complete AI-provider transfer claim.',
        'The provider, data classes, redaction rule, consent rule, retention rule, or classification decision changes.'),
    'OPS-008': (
        'An approved recovery decision covering lost credentials, lost GitHub access, lost Notes access, and unavailable external providers is missing.',
        'Document recovery authority, backup proof, alternate access, revocation, restoration order, and a bounded recovery test for every named loss condition.',
        'The complete cross-service recovery predicate is not satisfied.',
        'Credentials, accounts, providers, backup paths, recovery authority, or test results change.'),
    'PLAT-010': (
        'An approved support matrix naming supported iOS versions, Safari or WebKit versions, and iPhone or iPad device classes, with compatibility receipts, is incomplete.',
        'Freeze the supported matrix, execute the minimum install, storage, update, offline, and recovery checks on each configuration, and retain dated receipts.',
        'Current platform references do not establish a complete supported and tested matrix.',
        'The supported device list, iOS version, Safari or WebKit version, runtime behavior, or compatibility result changes.'),
}

items = [json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines()]
for item in items:
    ident = item['original_identifier']
    if ident not in DETAILS:
        continue
    missing, method, block, reopen = DETAILS[ident]
    claim = item['missing_proof'].split('Preserved claim: ', 1)[-1]
    item['missing_proof'] = f'{missing} Preserved claim: {claim}'
    item['recommended_acquisition_method'] = method
    item['decision_blocked_until'] = block
    item['reopening_trigger'] = reopen
PATH.write_text(''.join(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n' for item in items), encoding='utf-8')
