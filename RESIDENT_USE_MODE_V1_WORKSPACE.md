# Resident Use Mode v1 Workspace

Branch: `upgrade-workspace-v2-resident-use-mode-v1`

Purpose:
- Keep `sealed-release-v1` untouched as the protected rollback point.
- Build normal Resident use features safely on top of the sealed Levels 1-30 + 30B system.
- Do not add more certification levels unless a future upgrade truly needs a new proof layer.

Baseline rules:
- Level 30 remains the Final Seal / Done Lock.
- Level 30B remains the Resident startup auto-gate.
- Resident may run only when 30B confirms Level 30 is sealed.
- Future work should improve usable Resident mode without weakening the sealed certification chain.

First target:
- Resident Use Mode v1: a normal app area where the user can use Resident without pressing certification buttons.
