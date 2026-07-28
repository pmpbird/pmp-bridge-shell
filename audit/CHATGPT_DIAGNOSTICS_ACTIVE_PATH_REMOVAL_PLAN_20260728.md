# Diagnostics Active Path removal and handoff repair

Authorized scope:
- remove the top Active Path Discovery button from Diagnostics;
- remove the Active Path Discovery Diagnostics card and Diagnostics-only controls;
- preserve Active Path Discovery in Control;
- keep App Orchestrator Status in Diagnostics;
- repair the safe-handoff success-mode mismatch (`clipboard` versus `copy`);
- investigate HTTP 412 handoff resource failures without weakening runtime integrity.

This record is audit-only and does not itself change runtime behavior.
