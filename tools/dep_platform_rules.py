#!/usr/bin/env python3
from __future__ import annotations
from dep_platform_common import find,three

RULES={
'BUILD-006':('REPRODUCIBLE_BUILD_LOCK_RECIPE_ABSENT','CURRENT DEFECT OR LIMITATION',96),
'BUILD-008':('SUPPLY_CHAIN_EVIDENCE_SUITE_ABSENT','CURRENT DEFECT OR LIMITATION',96),
'BUILD-011':('UNIFIED_RELEASE_IDENTITY_ABSENT','CURRENT DEFECT OR LIMITATION',94),
'OPS-003':('MAINTENANCE_POLICY_ABSENT','CURRENT DEFECT OR LIMITATION',95),
'OPS-004':('LEGAL_TERMS_PRIVACY_REVIEW_ABSENT','CURRENT DEFECT OR LIMITATION',95),
'OPS-006':('AI_DATA_CLASSIFICATION_DECISION_ABSENT','CURRENT DEFECT OR LIMITATION',96),
'OPS-008':('EXTERNAL_ACCESS_RECOVERY_DECISION_ABSENT','CURRENT DEFECT OR LIMITATION',95),
'PLAT-010':('SUPPORTED_IOS_SAFARI_DEVICE_MATRIX_ABSENT','CURRENT DEFECT OR LIMITATION',96),
}
REASONS={
'BUILD-006':'No dependency lock record or verified reproducible build and artifact-generation recipe exists in the complete current census.',
'BUILD-008':'No complete dependency inventory, lock-integrity receipt, SBOM, vulnerability review, and license review suite exists.',
'BUILD-011':'No current release identity binds code, laws, prompts, schemas, tests, and provider settings with versions and digests.',
'OPS-003':'No approved policy assigns responsibility and update cadence across dependencies, providers, benchmarks, and device compatibility.',
'OPS-004':'No verified review receipt covers legal terms, licenses, and privacy obligations across the named providers and platforms.',
'OPS-006':'No approved classification decision says what source code and project context may or may not be sent to an AI provider.',
'OPS-008':'No approved recovery decision covers lost credentials, GitHub access, Notes access, and unavailable external providers together.',
'PLAT-010':'No approved support matrix defines supported iOS, Safari or WebKit versions, and device classes.',
}
EXTERNAL={
'AI-011':('Provider/model names and versions, account privacy settings, authoritative retention, training-use, residency, and deletion terms, plus a dated redacted account receipt.','Bind the exact configured provider account and model version; capture settings and governing-term digests without secrets.','Repository evidence does not identify the active provider account or establish external guarantees.','Provider/model configuration, account settings, terms, region, retention, or deletion guarantees change.'),
'AI-017':('Current and replacement provider/model versions, a frozen equivalence benchmark, and independently verified regression results.','Run both exact versions against frozen inputs and thresholds and retain a digest-bound comparison receipt.','No exact model pair or completed replacement-regression run is established.','Either model, benchmark, threshold, API, or result changes.'),
'PLAT-006':('A supported iOS/Safari/device matrix and executed receipts for eviction, private browsing, low-storage pressure, and OS-upgrade persistence.','Install on each supported physical configuration, seed non-secret state, run each condition, and record before/after digests.','Physical persistence behavior cannot be proven from repository source.','Supported devices, OS/browser versions, storage code, or results change.'),
'PLAT-011':('A bounded background-execution contract and suspension/resume tests on every supported iOS/Safari Home Screen configuration.','Measure suspend, timer throttling, network interruption, resume, and stale-state recovery against declared limits.','Repository source shows intentions, not actual iOS suspension behavior.','Background expectations, WebKit behavior, supported matrix, or runtime implementation changes.'),
'PROOF-012':('Bound provider/model and competitor versions, monitoring cadence, drift/freshness checks, claim-expiry rules, and dated monitoring receipts.','Record exact versions and claim dates, schedule rechecks, run drift/freshness comparisons, and expire stale claims.','Provider updates and competitor freshness are external changing state.','Versions, benchmark, cadence, thresholds, or claim dates change.'),
'RUN-013':('Exact provider/model configuration and executable self-improvement or replacement path, plus a bounded independently verified run.','Bind the effective route and versions, run a non-promoting sandbox trial, verify authority limits, and retain rollback proof.','No active replacement executor or completed self-improvement run is established.','Executor, provider/model, authority rule, sandbox result, or rollback mechanism changes.'),
}

def evaluate(identifier,records,file_rows):
    if identifier not in RULES:return 'EXTERNAL_REQUIRED',{'external':EXTERNAL[identifier]},[]
    names=[x['path'].lower() for x in file_rows]
    if identifier=='BUILD-006':
        pats=('package-lock.json','pnpm-lock.yaml','yarn.lock','bun.lock','poetry.lock','pipfile.lock','cargo.lock','go.sum','composer.lock','gemfile.lock')
        locks=[file_rows[i] for i,n in enumerate(names) if any(n.endswith(p) for p in pats)]
        m=find(records,[(('reproducible build','build command')),(('artifact generation','artifact-generation','build artifact')),(('lockfile','dependency lock','locked dependencies')),(('status: pass','verification: pass','completion receipt'))],2)
        full=[x for x in m if x['groups']>=4 and x['verified']];detail={'locks':locks,'recipe_matches':m,'complete':full};ev=locks+[{'path':x['path'],'sha256':x['sha256']} for x in m]
        return ('DISPROVED' if locks and full else 'SUPPORTED' if not locks and not m else 'UNRESOLVED'),detail,ev
    if identifier=='BUILD-008':
        locks=[x for x in file_rows if any(x['path'].lower().endswith(p) for p in ('package-lock.json','pnpm-lock.yaml','yarn.lock','poetry.lock','pipfile.lock','cargo.lock','go.sum'))]
        sbom=[x for x in file_rows if any(t in x['path'].lower() for t in ('sbom','cyclonedx','spdx'))]
        inv=find(records,[(('dependency inventory','third-party dependency')),(('version','digest'))],2)
        vul=find(records,[(('vulnerability review','vulnerability scan')),(('status: pass','verification: pass'))],2)
        lic=find(records,[(('license review','license compliance')),(('status: pass','verification: pass'))],2)
        cats={'lock':bool(locks),'sbom':bool(sbom),'inventory':bool(inv),'vulnerability':bool(vul),'license':bool(lic)};ev=locks+sbom+[{'path':x['path'],'sha256':x['sha256']} for x in inv+vul+lic]
        return ('DISPROVED' if all(cats.values()) else 'SUPPORTED' if not any(cats.values()) else 'UNRESOLVED'),cats,ev
    defs={
'BUILD-011':([(('release identity','release manifest')),(('code',)),(('laws','governing law')),(('prompts',)),(('schemas',)),(('tests',)),(('provider settings','provider configuration')),(('sha256','content digest'))],5,8),
'OPS-003':([(('maintenance policy','support policy')),(('dependencies',)),(('providers',)),(('benchmarks',)),(('device compatibility','supported devices')),(('owner','responsible')),(('cadence','schedule'))],4,7),
'OPS-004':([(('legal review','terms review')),(('license',)),(('privacy',)),(('ai provider',)),(('cloudflare',)),(('github',)),(('shortcuts','apple notes')),(('status: pass','completion receipt'))],4,8),
'OPS-006':([(('data classification',)),(('source code',)),(('project context',)),(('ai provider',)),(('allowed','permitted')),(('prohibited','forbidden')),(('status: approved','completion receipt'))],4,7),
'OPS-008':([(('recovery decision','recovery policy')),(('lost credentials',)),(('lost github','github account')),(('lost notes','notes access')),(('unavailable provider','provider outage')),(('status: approved','completion receipt'))],3,6),
'PLAT-010':([(('support matrix','supported matrix','device matrix')),(('ios',)),(('safari','webkit')),(('device','iphone','ipad')),(('version',)),(('status: approved','verification: pass'))],3,6),
}
    groups,minimum,complete=defs[identifier];return three(find(records,groups,minimum),complete)
