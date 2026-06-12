# PMP Current — Resident Reasoning Connection Audit

AUDIT VERSION: v1.0.0-final-packet-02  
AUDITED ON: 2026-06-11  
REPOSITORY: pmpbird/pmp-bridge-shell  
AUDIT STATE: PASS WITH WATCH

## 0. Critical correction

The earlier Packet 02 audit used the older Inventory Eyes manifest current-flow statement too strongly.

Corrected current route evidence shows the active route is:

`pmp-app-current.html`  
→ `pmp-current-map.json`  
→ `pmp-route-guardian-current-loader-v10.html`  
→ `pmp-current-inner-cleanbug-rgcontrols-v3.html`  
→ `pmp-home-single-v6.html`

The older manifest still lists `pmp-home-single-v14.html -> pmp-home-single-v6.html`, but the current map now points to Route Guardian v10 and current-inner RG controls v3. Packet 02 uses the current map as the stronger route authority.

## 1. Current Resident entry surface

Current verified user-facing entry chain:

1. `pmp-app-current.html` loads the current map.
2. `pmp-current-map.json` points to `pmp-route-guardian-current-loader-v10.html`.
3. Route Guardian v10 force-fetches the current app.
4. The current app is `pmp-current-inner-cleanbug-rgcontrols-v3.html`.
5. Current inner loads `pmp-home-single-v6.html` inside iframe `#app`.
6. Resident drawer inside the loaded base app remains the normal Resident request surface.

Verified current Resident objects:

- Screen/drawer: `div#resident.drawer`
- Input element: `textarea#ask`
- Paste/context input: `textarea#paste`
- Run control: button with `onclick="residentRun()"`
- Reply output: `div#residentReply`
- Warning output: `div#residentWarning`
- Work output: `pre#residentWork`

Additional Resident-connected surfaces:

- `resident.html` — Deep Resident Intelligence overlay opened by current-inner controls.
- `bm.html` — Bug Memory room Resident, private/manual.
- `safe-writer-v14.html` — Safe Writer Resident wrapper.
- `code-safety-v13.html` — Code Safety Resident wrapper.
- `resident-notes-catalog-v3.html`, `resident-notes-backend-v2.html`, `resident-zip-xray-v2.html`, `private-bug-mixer-lab-v1.html` — private Bug Memory/Notes/ZIP/Mixer tools.

## 2. Complete request-to-reply flow

Plain-language current flow:

USER INPUT  
→ `#ask` in Resident drawer  
→ `residentRun()`  
→ injected patch layers may run first  
→ local regex/template routing  
→ local report/storage/tool function OR manual ChatGPT handoff  
→ reply/work/warning display  
→ session chat and local work ledger write  
→ optional clipboard/Shortcut/backend handoff only when a relevant tool path is invoked

Detailed corrected route/request flow:

1. `pmp-app-current.html` loads `pmp-current-map.json`.
2. The map points to Route Guardian v10 and current inner v3.
3. Route Guardian v10 opens the current inner app.
4. Current inner v3 loads `pmp-home-single-v6.html` and injects support scripts.
5. User opens Resident drawer and presses Run.
6. Before the original v6 `residentRun()` may answer, patch scripts may intercept or add context:
   - `pmp-resident-xray-core.js` refreshes X-Ray context before the answer.
   - `pmp-resident-lossless-readiness.js` intercepts lossless/readiness questions.
   - `pmp-copy-lossless-diagnostic.js` intercepts copy-lossless diagnostic questions.
   - `pmp-resident-work-fix.js` patches Show Work / Copy Work.
   - current-inner controls add Deep Resident overlay and route/tool patches.
7. If no injected patch consumes the request, v6 `residentRun()` reads `#ask` and `#paste`, lowercases the request, stores user chat, and applies local regex branches.
8. Matched branches perform local deterministic work.
9. Unmatched/deeper requests produce a manual ChatGPT handoff under Show Work.

## 3. Reply flow

Reply paths found:

- v6 Resident uses `plain(message, work, next, warning)`.
- `plain()` writes to `#residentReply`, `#residentWork`, `#residentWarning`, session chat, and `pmp_single_resident_work_v6`.
- X-Ray writes context to `pmp_resident_xray_context_v1` and history/rule keys.
- Lossless readiness writes reports to `#residentReply`, `#residentWork`, and `pmp_resident_lossless_readiness_latest_v1`.
- Copy-lossless diagnostic writes `pmp_copy_lossless_diagnostic_v1` and may show/copy diagnostic JSON.
- Deep Resident `resident.html` writes local JSON/template reports through local report functions.
- Tool wrappers write JSON responses to local output elements and/or copy handoff JSON.

## 4. Reasoning-source classification

Current Resident is a mixed local system:

- fixed scripted responses: present
- keyword/regex rules: present
- decision trees: present
- template filling: present
- stored local context: partial
- local deterministic inspection/reporting: present
- external AI model: not found
- backend AI service: not found
- manual ChatGPT handoff: present

Conclusion:

No direct external AI model call was found in the corrected current route, injected support scripts, Deep Resident, Bug Memory, Notes, ZIP, Mixer, Safe Writer, or Code Safety Resident surfaces audited in Packet 02.

The current deeper-reasoning path remains manual ChatGPT handoff, not autonomous Resident model reasoning.

## 5. External connections and backend

Verified external or quasi-external connections:

1. Current map/static file fetches
   - Used by stable door, Route Guardian, X-Ray, and reports.

2. Optional backend configuration
   - Key: `pmp_backend_config_v1`
   - Client paths found include `/api`, `/api/resident-archive`, and `/api/private-bug-memory`.
   - No AI-provider endpoint, model name, model auth, or AI response parser was found.
   - Backend implementation source was not available through repository fetch; `worker.js` and `cloudflare-worker.js` are referenced in manifest but not fetchable.

3. iOS Shortcut handoffs
   - `PMP Vault GitHub Writer`
   - `PMP Save Private Memory`
   - These are manual/user-mediated clipboard/Shortcut paths.
   - They do not prove Resident direct repo-write authority.

4. External CDN
   - JSZip loaded from jsDelivr in ZIP/Notes/Mixer tools.
   - This enables local ZIP processing, not AI reasoning.

## 6. Local rule behavior

Resident local rules include:

- storage/local-storage/memory cleanup/status
- packet request/save/pipeline handling
- learn/remember from paste
- lossless/readiness/status checks
- automatic app update preparation
- hidden/private boundary refusal
- copy-lossless diagnostics
- source body intake and local field extraction
- private Bug Memory ZIP/Notes/Mixer preparation
- default manual ChatGPT handoff

These are deterministic client-side behaviors. They are not model reasoning.

## 7. Prompt and context behavior

Prompt behavior is handoff-based.

Known prompt/copy pathways:

- `outsideProjectPrompt()` / packet request handoff
- Bug Memory `copyResidentPrompt()`
- Notes backend Resident prompt copy
- Mixer prediction prompt copy
- Safe Writer/Code Safety handoff copy

Context currently available to Resident or Resident-connected tools:

- current user message: yes
- session chat: partial/session-only
- Active Work Thread: partial/local
- route/current map: yes
- X-Ray app context: yes, safe observable only
- Inventory Eyes: yes, but manifest may be stale versus current map
- source body text: manual local loader only
- body laws: not automatic in normal Run
- private Bug Memory: manual/private tools only
- full source code: not automatic in normal Run
- ChatGPT answers: manual paste/learn only

## 8. Memory and persistence

Important storage records found or confirmed:

- `pmp_single_session_chat_v6`
- `pmp_single_resident_work_v6`
- `pmp_clean_connection_packets_v5`
- `pmp_corpus_inbox_v1`
- `pmp_backend_config_v1`
- `pmp_resident_xray_context_v1`
- `pmp_resident_xray_history_v1`
- `pmp_resident_xray_rule_v1`
- `pmp_inventory_eyes_latest_v1`
- `pmp_app_lossless_inventory_latest_v1`
- `pmp_lossless_visible_compact_latest_v1`
- `pmp_resident_auto_lossless_inventory_context_v1`
- `pmp_resident_lossless_readiness_latest_v1`
- `pmp_resident_lossless_copy_arm_v1`
- `pmp_copy_lossless_diagnostic_v1`
- `pmp_route_guardian_v10_receipt`
- `pmp_route_guardian_last_good`
- `pmp_route_guardian_report_v1`
- `pmp_code_safety_bank_v1`
- `pmp_auto_update_request_v20`
- `pmp_resident_learning_single_v6`
- `pmp_resident_thread_v1`
- `pmp_resident_report_v1`
- `pmp_bug_memory_v1`
- `pmp_private_bug_memory_existing_v1`
- `pmp_medium_source_bodies_v1`
- `pmp_medium_manifest_records_v1`
- `pmp_medium_loaded_source_text_v1`
- `pmp_medium_source_text_raw_v1`
- `pmp_medium_field_registry_v1`
- `pmp_medium_transfer_receipts_v1`
- `pmp_medium_field_extraction_receipts_v1`

Storage is local/browser-based unless copied, sent by Shortcut, or sent to an enabled backend path.

## 9. Tool authority

Verified current authority:

- Resident drawer: guidance, local reports, preparation, manual handoff.
- Route Guardian: route proof/static checks and gated navigation.
- X-Ray: safe observable app map/key-name scan.
- Lossless/Vault tools: build clipboard packet and open Shortcut.
- Source Body Loader: manual local source staging/verification/acceptance with watch.
- Field Extractor: local source parsing with watch.
- Private Medium buttons/claim controls: local seed tables, claim ceilings, receipts, simulated/real-app table checks with explicit do-not-claim boundaries.
- Bug Memory/Notes/ZIP/Mixer: private local/Notes/ZIP preparation.
- Safe Writer/Code Safety wrappers: read context/copy handoff only from wrapper layer.

Not found:

- autonomous code commit
- autonomous repository write
- autonomous promotion
- rollback authority
- validator weakening authority
- self-authority expansion
- direct external AI model control

## 10. Privacy and credential boundaries

Verified privacy boundaries:

- X-Ray and inventory paths are key-name/structure focused and exclude private values.
- Vault packet privacy gates say private Bug Memory, Apple Notes contents, tokens, passwords, secrets, and private values must not be written.
- Notes backend states the web app cannot secretly read Notes.
- Bug Memory tools require manual paste/load/copy.
- User text does not automatically go to an AI provider because no AI provider call was found.
- User text/context can leave through clipboard, Shortcut, or enabled backend paths.
- No AI-model credential field or stored token was found in the audited Resident route.

## 11. Failure behavior

Observed or code-supported failure behavior:

- Current map fetch failure: stable door falls back to Route Guardian fallback loader.
- Route Guardian current app fetch failure: fallback or blocked route report.
- Missing/malformed local storage: read helpers return fallback/null.
- Backend unavailable/off: local mode remains; backend call reports failure/off.
- AI service unavailable: no current AI service found.
- JSZip/CDN missing/offline: ZIP tools warn/check internet/reload.
- Clipboard unavailable: fallback copy or visible JSON/report.
- localStorage cleared: persistent context and memory reports are lost; route can still load.
- Unsafe private memory import: quarantine/review before import.
- Shortcut unavailable: packet may copy, but external save/write does not complete.

## 12. Offline behavior

Resident can still run local rules/templates and read existing localStorage/sessionStorage offline. Static fetches, JSZip CDN, backend actions, and Shortcut/GitHub/Notes handoff completion may fail or be incomplete.

## 13. Replaceability

- Resident interface: partly replaceable, but coupled to DOM IDs/functions.
- Conversation memory: partly replaceable local keys.
- Context builder: separate modules exist, but no unified provider-agnostic bridge.
- Prompt builder: manual and embedded.
- Provider adapter: not present for AI reasoning.
- Model call: not present.
- Response parser: not present for AI output.
- Explanation layer: local templates/plain text.
- Tool layer: wrappers/patches with limited authority.
- Safety layer: partial Route Guardian/Safe Writer/Code Safety/claim controls.
- Outer guardian: not implemented for Safe Change promotion.

## 14. Verified limitations

- No direct AI model reasoning connection found.
- No autonomous repository write authority found.
- No autonomous promotion or rollback authority found.
- No complete body-law reader in normal Run flow found.
- Current Inventory Eyes manifest is stale for route authority; current map is stronger.
- Backend implementation remains unavailable from repository fetch.
- Live iPhone runtime was not executed in this chat.
- Safe Change, candidate isolation, and trusted outer guardian remain not implemented.

## 15. Unknowns / watch

Remaining watch items:

1. Actual backend server implementation and retention/security are unverified.
2. Live installed Home Screen runtime was not observed here.
3. Exact runtime ordering among all injected patches is inferred from code load/order and intervals, not browser-executed here.
4. Optional Shortcut behavior depends on the user’s iPhone Shortcuts setup.

These do not prevent Packet 03 because the current reasoning source and tool authority ceiling are now known enough: local/rule/template/manual-handoff, not independent AI coding/promotion.

## 16. Blockers

No blocker prevents Packet 03.

## 17. Safe claim

Packet 02 traces the corrected current Resident route and Resident-connected injected support scripts. Current Resident reasoning is local guarded rules/templates/context reports plus manual ChatGPT handoff, with optional backend/Shortcut handoffs. No direct AI model call or autonomous write/promotion authority is verified.

## 18. Do-not-claim

Do not claim:

- Resident Safe Change is implemented.
- Resident can independently code the app.
- Natural-Language AI Bridge is complete.
- Resident has direct repository write authority.
- Resident can promote or roll back changes.
- Resident has a verified direct external AI reasoning engine.
- Backend behavior is fully verified.
- All runtime behavior is proven without live execution.
- Current app is best-in-world.

## 19. Next authorized step

03 — PMP CURRENT — CURRENT-TO-FUTURE CAPABILITY MAP

## 20. Packet 02 completion receipt

BEGIN PMP CURRENT — PART COMPLETION RECEIPT

PART:
02 — Resident Reasoning Connection Audit

STATUS:
PASS WITH WATCH

COMPLETED:
Corrected and completed the Resident reasoning connection audit. Traced the actual current route from stable entry through current map, Route Guardian v10, current-inner RG controls v3, base Resident v6, injected support scripts, Deep Resident, Bug Memory, Notes/ZIP/Mixer tools, Safe Writer wrapper, and Code Safety wrapper. Classified reasoning sources, context paths, storage records, external/backend/Shortcut paths, tool authority, privacy/credential boundaries, failure behavior, offline behavior, replaceability, verified limitations, and unresolved watch.

OUTPUTS CREATED:
- audit/pmp-resident-reasoning-connection-audit-v1.json
- audit/PMP-Current-Resident-Reasoning-Connection-Audit-v1.md

REASONING SOURCE FOUND:
Mixed local system: regex rules, deterministic scans, templates, stored local context, tool reports, and manual ChatGPT handoff. No verified direct external AI model call in the normal Resident Run flow.

CURRENT USER-TO-REPLY FLOW:
Stable door → current map → Route Guardian v10 → current-inner RG controls v3 → base app v6 → Resident drawer `#ask` → `residentRun()` plus injected patches → local rule/template/report behavior or manual ChatGPT handoff → reply/work/warning/chat/ledger output.

CURRENT TOOL AUTHORITY:
Guidance, inspection, local reports, context summaries, manual handoff, clipboard packet creation, Shortcut launch, local source intake, local field extraction with watch, private memory preparation. No verified autonomous repo write, commit, promotion, rollback, validator, or permission authority.

PROTECTED OBJECTS PRESERVED:
Frozen current app, current map, Route Guardian boundary, Resident behavior, storage keys, manifest, private values, credentials, private Notes boundary, private Bug Memory boundary, rollback/promotion authority, claim ceilings, outer-guardian authority.

UNRESOLVED WATCH:
- Backend implementation and retention/security remain unverified.
- Live iPhone Home Screen runtime was not executed in this audit.
- Exact runtime ordering among injected patch scripts was inferred from code, not browser-executed.
- Shortcut completion depends on user’s iPhone Shortcut setup.

BLOCKERS:
None preventing Packet 03.

SAFE CLAIM:
The current Resident reasoning connection has been audited for the corrected current route with watch. Resident currently uses local guarded rules/templates/context reports and manual ChatGPT handoff, with optional backend/Shortcut handoff paths. No direct AI model reasoning call or autonomous write/promotion authority is verified.

DO NOT CLAIM:
Resident Safe Change is implemented; Resident independently codes; Natural-Language AI Bridge is complete; Resident can promote, rollback, or write the repo autonomously; backend is fully verified; all runtime behavior is proven without live execution; best-in-world is supported.

NEXT AUTHORIZED PART:
03 — Current-to-Future Capability Map

NEXT-PART PREREQUISITES:
Project Start Card, Master Builder Guide, corrected Packet 02 audit JSON, corrected Packet 02 human audit, this Packet 02 completion receipt, and unresolved watch carried forward.

END PMP CURRENT — PART COMPLETION RECEIPT
