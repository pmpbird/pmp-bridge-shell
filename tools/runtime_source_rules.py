#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from runtime_source_git import main_files,main_text

DECISIONS={
'BUILD-010':('NO_NAMED_FLOW_CONCURRENCY_CONTROL','CURRENT DEFECT OR LIMITATION',94),
'BUILD-013':('NO_IMPLEMENTATION_QUALITY_BASELINE','CURRENT DEFECT OR LIMITATION',93),
'BUILD-014':('WRAPPER_AND_FALLBACK_ACCUMULATION_UNGOVERNED','CURRENT DEFECT OR LIMITATION',96),
'DATA-006':('MIGRATION_AND_BACKUP_EXIST','OUT-OF-SCOPE CANDIDATE',98),
'DATA-011':('NO_TRUSTED_MONOTONIC_ORDER_SOURCE','CURRENT DEFECT OR LIMITATION',96),
'DATA-012':('NO_APPEND_ONLY_TAMPER_EVIDENT_LEDGER','CURRENT DEFECT OR LIMITATION',96),
'GOV-015':('CURRENT_ROUTE_NOT_UNIFORMLY_COMMIT_AND_DIGEST_PINNED','CURRENT DEFECT OR LIMITATION',98),
'PLAT-009':('OLDER_FALLBACKS_WITHOUT_MIXED_VERSION_PROOF','CURRENT DEFECT OR LIMITATION',99),
'RUN-001':('NORMAL_RESIDENT_PATH_IS_LOCAL_DETERMINISTIC','CURRENT DEFECT OR LIMITATION',98),
'RUN-008':('NO_CANDIDATE_OBSERVER_OR_BASELINE_COMPARATOR','CURRENT DEFECT OR LIMITATION',96),
'RUN-015':('NO_RUNTIME_PERMISSION_OR_TOOL_ENFORCEMENT_GATE','CURRENT DEFECT OR LIMITATION',95),
}
REASONS={
'BUILD-010':'The complete effective runtime graph contains no lock, mutex, semaphore, atomic, compare-and-swap, or serialized authority mechanism for the named simultaneous flows.',
'BUILD-013':'No directly controlling runtime source or root enforcement configuration selects and executes a static type, lint, or security baseline for implementation artifacts.',
'BUILD-014':'The current route uses nested wrappers and explicit fallback paths, while the effective runtime contains no deprecation or wrapper-retirement enforcement.',
'DATA-006':'The complete preserved claim is disproved because the active current wrapper directly loads both a migration module and a backup module.',
'DATA-011':'The effective runtime uses wall-clock timestamps but contains no trusted ordering authority or monotonic event-sequence implementation.',
'DATA-012':'Current runtime state and receipts use mutable storage writes without a hash chain, signature, immutable append primitive, or append-only ledger enforcement.',
'GOV-015':'The public entry, current map, loader, and wrapper chain are path and cache-key selected but are not uniformly pinned to branch, commit SHA, and content digest.',
'PLAT-009':'The public entry explicitly retains a fallback map and older Route Guardian v9 path while the primary map selects v14, with no controlling mixed-version proof.',
'RUN-001':'The normal Resident run function is implemented inside the local app source and contains no provider adapter, model call, or network request in that reasoning path.',
'RUN-008':'No candidate runtime observer or baseline-comparison component is reachable from the effective runtime graph.',
'RUN-015':'Current tool and navigation actions are directly callable from UI/runtime functions without a runtime permission, capability, approval, or tool-policy enforcement gate.',
}
QUEUES={
'DATA-013':('pmp-home-single-v6.html plus pmp-current-inner-cleanbug-rgcontrols-v3.html','The final effective DOM after wrapper suppression and runtime injections has not been observed.','Whether minimization, consent, retention display, export, and deletion controls are simultaneously present and usable.','Local HTTPS server in a standards browser after pressing Open Latest App.','Open the current door, press Open Latest App, capture the final DOM and exercise each named control with a redacted receipt.','Static source includes storage-cleaning and export-related functions, but the wrapper alters visible controls; source alone cannot decide the complete UI claim.','Any base-app control, wrapper suppression rule, injected script, route, or browser behavior changes.'),
'GOV-012':('Effective runtime chain and packet-output surfaces reachable from it','A complete authoritative packet-by-packet output inventory is outside the runtime chain and has not been bound to every packet identifier.','Whether every required human and machine record exists for every packet.','Authoritative main repository plus approved packet index.','Generate a digest-bound expected-versus-present inventory for every packet and independently verify completeness.','The effective runtime cannot prove completeness of records that are not runtime-reachable.','Packet inventory requirements, packet identifiers, expected artifacts, or repository contents change.'),
'GOV-014':('Current runtime graph and existing freeze receipts','The freeze scope for historical, external, private, device, and provider state is not directly controlled by the runtime route.','Whether the freeze covers every state named by the preserved claim.','Authoritative main plus approved external/private evidence boundary.','Produce a scope matrix covering current, historical, external, private, device, and provider state and verify each frozen or explicitly excluded cell.','Runtime source proves only the current code path, not every historical or external state.','Freeze scope, external state, private evidence, provider state, device state, or governing receipt changes.'),
'OPS-015':('pmp-current-map-v9.json and current runtime module surfaces','No approved first-release/MVP scope record is directly controlling the runtime graph.','Whether a bounded safe first release is frozen instead of implicitly exposing the wider module set.','Authoritative main plus approved release-scope decision.','Bind a release-scope manifest to exact reachable modules and verify that non-MVP modules are disabled or absent.','Runtime reachability alone cannot prove the product scope decision or its acceptance boundary.','Release scope, reachable modules, feature flags, or approval changes.'),
'PLAT-001':('pmp-app-current.html through the complete primary wrapper chain','Physical Home Screen installation, cache, relaunch, and update behavior is not repository-provable.','Install, cold launch, relaunch, cache refresh, and update behavior.','Supported physical iPhone, exact iOS and Safari/WebKit version, Home Screen installed mode.','Install once, record loaded URLs and digests, relaunch offline/online, change a cache key, and retain timestamped results.','Source establishes intended routing but not installed-device cache behavior.','Device, iOS/WebKit version, route, cache key, serving headers, or test result changes.'),
'PLAT-004':('pmp-app-current.html → map v9 → Route Guardian v14 → wrapper v4 → wrapper v3 → home v6','The exact live frame ancestry and post-injection outermost order has not been observed.','Actual frame URLs, load order, and injected-script order after manual open.','Local or deployed HTTPS runtime in a browser with same-origin access.','Press Open Latest App, capture each frame URL and ordered script list after injection settles, and hash the receipt.','Static precedence proves intended order, not the final observed browser order.','Any route, wrapper, injection timing, browser behavior, or serving origin changes.'),
'PLAT-005':('pmp-home-single-v6.html localStorage-backed Resident state','The post-clear behavior has not been executed in a supported browser.','Whether saved Resident context is lost after clearing site storage and reloading.','Supported browser/device with non-secret seeded Resident context.','Seed identifiable test context, verify persistence, clear site storage, reload, and record before/after values and UI state.','Static storage calls strongly predict loss but do not prove the complete user-visible behavior.','Storage keys, backup path, browser/device, synchronization behavior, or test result changes.'),
'PROOF-001':('Current runtime graph plus current executable test entry points','No runtime-target manifest binds generated tests to the complete effective app chain and no current execution receipt covers it.','Whether pre-code test designs became generated and executed tests against the current runtime.','Authoritative main, exact runtime graph digest, and deterministic test environment.','Generate a test manifest mapped to current runtime files, execute it, and retain pass/fail plus coverage digests.','Repository verification workflows do not by themselves prove product-runtime test generation and execution.','Runtime graph, test manifest, test implementation, environment, or receipt changes.'),
'PROOF-008':('Current runtime graph plus current executable test entry points','No mutation, fuzz, property, or systematic fault-injection campaign is bound to the current graph.','Execution and results of each named test class.','Authoritative main and isolated deterministic test environment.','Run one bounded campaign for each named class against identified runtime targets and retain seeds, mutants/faults, outcomes, and digests.','Static runtime source cannot establish that these dynamic test classes were required and executed.','Runtime targets, tools, seeds, properties, fault model, thresholds, or results change.'),
}

def has_any(text,terms):return any(term.lower() in text.lower() for term in terms)
def function_body(text,name):
    start=text.find('function '+name+'(')
    if start<0:return ''
    brace=text.find('{',start)
    if brace<0:return ''
    depth=0
    for index in range(brace,len(text)):
        if text[index]=='{':depth+=1
        elif text[index]=='}':
            depth-=1
            if depth==0:return text[brace+1:index]
    return ''
def evaluate(identifier,repo:Path,graph,core_text):
    paths=set(graph['primary_paths']);files=set(main_files(repo));used=[];detail={}
    if identifier not in DECISIONS:return 'RUNTIME_TEST_OR_NONRUNTIME_EVIDENCE_REQUIRED',{'queue':QUEUES[identifier]},[]
    if identifier=='BUILD-010':
        terms=('navigator.locks','broadcastchannel','atomics.','mutex','semaphore','compareandswap','compare-and-swap','serialized authority')
        found=[term for term in terms if term in core_text.lower()];detail={'concurrency_primitives':found};return ('UNRESOLVED' if found else 'SUPPORTED'),detail,[]
    if identifier=='BUILD-013':
        configs=[name for name in files if name.lower() in {'tsconfig.json','eslint.config.js','eslint.config.mjs','.eslintrc','.eslintrc.json','ruff.toml','mypy.ini','semgrep.yml','semgrep.yaml'}]
        terms=[term for term in ('eslint','typescript','mypy','ruff','semgrep','codeql') if term in core_text.lower()];detail={'root_enforcement_configs':configs,'runtime_enforcement_terms':terms};return ('UNRESOLVED' if configs or terms else 'SUPPORTED'),detail,configs
    if identifier=='BUILD-014':
        wrappers=[n['path'] for n in graph['nodes'] if any('wrapper' in role for role in n['roles'])];fallbacks=graph['fallback_paths'];guards=[x for x in ('deprecation policy','retire wrapper','obsolete-file cleanup','wrapper limit') if x in core_text.lower()];detail={'wrappers':wrappers,'fallbacks':fallbacks,'retirement_guards':guards};return ('SUPPORTED' if len(wrappers)>=2 and fallbacks and not guards else 'UNRESOLVED'),detail,wrappers+fallbacks
    if identifier=='DATA-006':
        migration='pmp-phase1-migrate-v1.js' in paths;backup='pmp-private-backup-lite-v1.js' in paths;detail={'migration_module_reachable':migration,'backup_module_reachable':backup};return ('DISPROVED' if migration and backup else 'UNRESOLVED'),detail,[x for x in ('pmp-phase1-migrate-v1.js','pmp-private-backup-lite-v1.js') if x in paths]
    if identifier=='DATA-011':
        clocks=[x for x in ('Date.now(','new Date(','toISOString(') if x in core_text];monotonic=[x for x in ('performance.now(','event_sequence','monotonic','trusted timestamp authority') if x.lower() in core_text.lower()];detail={'wall_clock_calls':clocks,'trusted_or_monotonic_sources':monotonic};return ('SUPPORTED' if clocks and not monotonic else 'UNRESOLVED'),detail,[]
    if identifier=='DATA-012':
        mutable=has_any(core_text,('localStorage.setItem','sessionStorage.setItem'));tamper=[x for x in ('hash chain','append-only','digital signature','immutable ledger','merkle') if x in core_text.lower()];detail={'mutable_storage_writes':mutable,'tamper_evidence_terms':tamper};return ('SUPPORTED' if mutable and not tamper else 'UNRESOLVED'),detail,[]
    if identifier=='GOV-015':
        route_paths=[graph['public_entry'],graph['primary_map'],graph['current_loader'],graph['current_app']];route='\n'.join(main_text(repo,p) for p in route_paths);pins={'branch':bool(re.search(r'branch\s*[:=]',route,re.I)),'commit_sha':bool(re.search(r'(commit|sha)[_ -]?(id|sha)?\s*[:=]',route,re.I)),'content_digest':'sha256' in route.lower()};detail={'route_paths':route_paths,'pins':pins};return ('SUPPORTED' if not all(pins.values()) else 'DISPROVED'),detail,route_paths
    if identifier=='PLAT-009':
        current=graph['current_loader'];fallback=graph['entry_fallback_loader'];current_v=re.findall(r'v(\d+)',current);fallback_v=re.findall(r'v(\d+)',fallback);older=bool(current_v and fallback_v and int(fallback_v[-1])<int(current_v[-1]));detail={'map_precedence':graph['map_precedence'],'current_loader':current,'fallback_loader':fallback,'fallback_is_older':older,'mixed_version_receipt_in_controlling_source':False};return ('SUPPORTED' if graph['fallback_paths'] and older else 'UNRESOLVED'),detail,[graph['public_entry'],graph['primary_map'],current,fallback]
    if identifier=='RUN-001':
        home=main_text(repo,'pmp-home-single-v6.html');body=function_body(home,'residentRun');network=[x for x in ('fetch(','xmlhttprequest','websocket','openai','anthropic','model.call','provider') if x in body.lower()];detail={'resident_run_found':bool(body),'network_or_provider_terms':network,'body_sha256':__import__('hashlib').sha256(body.encode()).hexdigest() if body else None};return ('SUPPORTED' if body and not network else 'UNRESOLVED'),detail,['pmp-home-single-v6.html']
    if identifier=='RUN-008':
        found=[x for x in ('candidate runtime observer','candidateobserver','baseline comparator','baselinecomparator') if x in core_text.lower()];detail={'observer_or_comparator_terms':found};return ('SUPPORTED' if not found else 'UNRESOLVED'),detail,[]
    if identifier=='RUN-015':
        enforcement=[x for x in ('permissiongate','authorizeTool','requiresApproval','toolPolicy','allowedTools','capabilityToken','denyTool') if x.lower() in core_text.lower()];detail={'manual_action_paths':graph['manual_action_paths'],'enforcement_terms':enforcement};return ('SUPPORTED' if graph['manual_action_paths'] and not enforcement else 'UNRESOLVED'),detail,graph['manual_action_paths']
    raise ValueError(identifier)
