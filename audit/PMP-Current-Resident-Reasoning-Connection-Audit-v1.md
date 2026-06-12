# PMP Current — Resident Reasoning Connection Audit

AUDIT VERSION: v1.0.0  
AUDITED ON: 2026-06-11  
REPOSITORY: pmpbird/pmp-bridge-shell  
AUDIT STATE: PASS WITH WATCH

## 1. Current Resident entry surface

The current app path is recorded in the Inventory Eyes manifest as:

USER CURRENT FLOW:
`pmp-app-current.html -> pmp-current-map.json -> pmp-current-inner.html -> pmp-home-single-v14.html -> pmp-home-single-v6.html`

The active Resident entry surface is the Resident drawer in `pmp-home-single-v6.html`, loaded through `pmp-home-single-v14.html`.

Verified current entry objects:

- Screen/drawer: `div#resident.drawer`
- Input element: `textarea#ask`
- Run control: button with `onclick="residentRun()"`
- Paste/context input: `textarea#paste`
- Reply output: `div#residentReply`
- Warning output: `div#residentWarning`
- Work output: `pre#residentWork`

Additional Resident surfaces:

- `resident.html` — Deep Resident Intelligence, local inspector/report tool.
- `safe-writer-v14.html` — Safe Writer wrapper Resident.
- `code-safety-v13.html` — Code Safety wrapper Resident.

## 2. Complete request-to-reply flow

Plain-language flow map:

USER INPUT  
→ `#ask` in current Resident drawer  
→ `residentRun()`  
→ optional X-Ray prepatch refreshes `pmp_resident_xray_context_v1`  
→ optional v14 patch intercepts Lossless/Inventory/Vault commands  
→ v6 `residentRun()` reads `#ask` and `#paste`  
→ request is lowercased and matched against local regex branches  
→ local branch runs deterministic tool/report/storage behavior OR unmatched request creates manual ChatGPT handoff  
→ `plain()` writes the reply to `#residentReply`  
→ `plain()` writes JSON work to `#residentWork`  
→ warning text appears in `#residentWarning` when supplied  
→ user/resident chat is stored in session chat  
→ latest Resident work is stored in local ledger  
→ tool output or copy/handoff packet is shown to the user

Stages:

- USER INPUT: present.
- ENTRY FUNCTION: `residentRun()`.
- CONTEXT READS: partial; storage, manifest, X-Ray, Inventory Eyes, visible tool frames.
- LOCAL RULES: present.
- EXTERNAL AI REASONING: not found.
- LOCAL REASONING: limited deterministic checks/rules/templates.
- RESPONSE PARSING: not present for AI response; local object rendering only.
- REPLY DISPLAY: `plain()`, `box()`, wrapper output functions.
- MEMORY WRITE: session chat, local work ledger, storage/report keys.
- TOOL OR NEXT-STEP OUTPUT: present through local reports, clipboard handoffs, Shortcut handoffs.

## 3. Reasoning-source classification

Current Resident reply system is a mixed local system:

- fixed scripted responses: present
- keyword rules: present
- decision tree: present
- template filling: present
- stored-response retrieval: partial/watch
- local deterministic reasoning: limited
- external AI model: not found
- backend AI service: not found
- manual ChatGPT handoff: present

Conclusion:

No verified direct external AI model call exists in the normal Resident Run flow. Deeper reasoning is currently handled by building handoff/work packets for ChatGPT/manual copy, not by Resident autonomously calling a model.

## 4. AI provider or backend details

No AI provider was verified.

Optional backend support exists through:

- storage key: `pmp_backend_config_v1`
- function: `backend(path,payload)`
- verified paths in current client code: `/api`, `/api/resident-archive`
- behavior: backend test/archive support, not verified AI reasoning
- failure behavior: local mode remains available when backend is off/unavailable

Backend source files `worker.js` and `cloudflare-worker.js` are listed in the manifest but were not fetchable through repository contents during this audit. This remains watch.

## 5. Local rule behavior

Current `residentRun()` routes by local regex branches:

- storage / local storage / memory full / clean / delete old
- packet request / make packet / get packet
- save packet / paste packet
- pipeline / check packet
- learn / remember
- lossless / quality / improve / better / weak / next move
- update / latest / newest
- hidden entrance / secret entrance
- default unmatched request → manual ChatGPT handoff

`resident.html` uses `classifyGoal()` to classify bug/build/organize/general requests into local response templates.

Safe Writer and Code Safety Residents use local context functions and local response templates.

## 6. Prompt and context behavior

Prompt behavior is manual-handoff oriented.

`outsideProjectPrompt()` exists to create text for an outside ChatGPT project / transfer packet. It does not call an AI model by itself.

Resident context currently includes some safe/local sources:

- current message: present, automatic
- previous conversation: partial, session chat only
- Active Work Thread: partial
- app map/current route: partial through manifest/current map/X-Ray/live screen
- source file content: not automatically loaded into normal Resident replies
- body laws: not found in normal Resident Run flow
- manifest: present for Inventory/X-Ray
- Bug Memory: partial/local; private contents excluded from safe inventory by rule
- Code Safety state: partial safe bank summary
- Resident X-Ray context: `pmp_resident_xray_context_v1`
- Inventory Eyes context: `pmp_inventory_eyes_latest_v1`, `pmp_resident_auto_lossless_inventory_context_v1`
- localStorage key names: scanned in safe paths
- private Notes contents: not captured by safe inventory
- ChatGPT responses: manual paste/learn path only

## 7. Memory and storage behavior

Important Resident-related records:

- `pmp_single_session_chat_v6` — session chat; sessionStorage; latest 80.
- `pmp_single_resident_work_v6` — persistent Resident work ledger; latest 30.
- `pmp_clean_connection_packets_v5` — saved connection packets.
- `pmp_corpus_inbox_v1` — corpus candidate material.
- `pmp_backend_config_v1` — backend enabled/base URL config.
- `pmp_resident_xray_context_v1` — safe observable app map.
- `pmp_resident_xray_history_v1` — X-Ray history counts.
- `pmp_resident_xray_rule_v1` — X-Ray rule.
- `pmp_inventory_eyes_latest_v1` — latest Inventory Eyes report.
- `pmp_app_lossless_inventory_latest_v1` — lossless inventory report.
- `pmp_resident_auto_lossless_inventory_context_v1` — Resident inventory summary.
- `pmp_code_safety_bank_v1` — Code Safety safe-point bank summary.
- `pmp_auto_update_request_v20` — Automatic App Update request.
- `pmp_resident_learning_single_v6` — pasted learned lessons.
- `pmp_resident_thread_v1` — resident.html Active Work Thread.
- `pmp_resident_report_v1` — resident.html latest report.
- `pmp_bug_memory_v1` — resident.html Bug Memory.

## 8. Tool authority

Current verified tool authority:

- Current Resident drawer: guidance, preparation, manual handoff, limited local safe actions.
- Deep Resident Intelligence: inspect, report, storage scan, repair-request preparation.
- Safe Writer Resident wrapper: read context and copy handoff only.
- Code Safety Resident wrapper: read context and copy handoff only.
- Inventory Eyes/Lossless: safe manifest/live screen scan, local reports, clipboard/Shortcut handoff.
- X-Ray: hidden safe observable app-map context refresh.

Not verified:

- direct repository write authority
- autonomous commit authority
- autonomous promotion authority
- rollback authority
- validator modification authority
- permission change authority
- candidate creation authority

## 9. Privacy boundaries

Verified privacy boundaries:

- X-Ray captures app structure and storage key names only; it does not capture private values, Apple Notes contents, tokens, passwords, or secrets.
- Manifest privacy rule says safe inventory excludes private Bug Memory records, private Notes contents, tokens, passwords, secrets, and private localStorage values.
- User text does not automatically leave through an AI provider because no AI model call was found.
- User text/app context can leave through manual clipboard, Shortcut handoff, or enabled backend archive.
- Backend URL is stored in `pmp_backend_config_v1`; no AI-provider credential field was found in the audited current path.

## 10. Failure behavior

Verified or watch-classified failures:

- Empty/unmatched request: safe local handoff/default behavior with watch.
- Unclear request: manual ChatGPT handoff.
- Missing storage: fallback object/array.
- Malformed storage: caught parse failure, fallback returned.
- Backend off/unavailable: warning/fallback; local mode remains.
- AI service unavailable: no current AI service found.
- Network offline: local rules/storage remain; backend/static fetch/Shortcut may fail.
- Manifest/current map/vault unavailable: fallback/unavailable object.
- Clipboard unavailable: copy failure message or displayed JSON.
- localStorage cleared: persistent context lost; app falls back.
- Private/hidden entrance request: safe refusal.

## 11. Offline behavior

Resident can still run local rule/template responses and read existing localStorage/sessionStorage while offline. Static JSON fetches, optional backend actions, and Shortcut/GitHub writing paths may fail or remain unavailable.

## 12. Replaceability

- Resident interface: partly replaceable; DOM IDs and local functions are coupled.
- Conversation memory: partly replaceable; separate storage keys exist.
- Context builder: partly replaceable; X-Ray/Inventory/tool contexts are distinct but not unified.
- Prompt builder: tightly coupled to current local code.
- Provider adapter: not present for AI reasoning.
- Model call: not present.
- Response parser: not present for AI output.
- Explanation layer: local template/plain layer, tightly coupled to UI.
- Tool layer: partly replaceable; wrappers/links exist but authority is limited.
- Safety layer: partial; Safe Writer/Code Safety exist, but full guardian is not implemented.
- Outer guardian layer: not implemented in current reasoning flow.

## 13. Verified limitations

- No direct external AI model call found.
- No provider/model/auth/timeout/retry/AI response parser found.
- No autonomous repository write/commit/promotion/rollback authority found.
- No automatic body-law reader found in normal Run flow.
- No automatic full-source reader found in normal Run flow.
- Deeper reasoning currently depends on manual ChatGPT handoff.
- Candidate isolation and outer guardian are not implemented by this evidence.
- Safe Change, independent coding, and best-in-world claims remain unsupported.

## 14. Unknowns / watch

- Backend implementation remains unverified because `worker.js` and `cloudflare-worker.js` are listed but were not fetchable.
- No live iPhone Home Screen runtime test was performed during this audit.
- Exact deployed X-Ray script loading order was not runtime-observed.
- Some helper/archive files were not deeply audited because Packet 02 focused on current reasoning flow.

## 15. Blockers

No blocker prevents Packet 03.

## 16. Safe claim

The current Resident reasoning connection has been audited for the main current flow. Verified behavior is local guarded rule/template/context handling plus manual ChatGPT handoff, with optional backend/archive support and no verified direct AI model reasoning call or autonomous repository-write/promotion authority.

## 17. Do-not-claim

Do not claim:

- Resident Safe Change is implemented.
- Resident can independently code the app.
- Natural-Language AI Bridge is complete.
- Current reasoning engine is good enough for Safe Change.
- The current reasoning engine is replaceable unless proven later.
- Resident can directly control every linked tool.
- Resident has repository write authority.
- Resident can safely promote changes.
- Outer guardian is implemented.
- All unknowns are resolved.
- Backend behavior is fully verified.

## 18. Next authorized step

03 — PMP CURRENT — CURRENT-TO-FUTURE CAPABILITY MAP
