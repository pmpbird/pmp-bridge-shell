# P2-C Post-Failure Guardian Readiness Repair Unit 2

This unit is limited to disposable A-003 test-harness readiness and timeout diagnostics.

- Canonical authority: V30 (`1b315768f9efcac9b5d5043ff4b9d10f5afa3c555300d69f4ce4baafade49570`)
- Base main: `d109cac3b89e67e28a2ae8ffae43e28b6a8009a7`
- PR #122: open and unmerged at `ea337f534e89c04b842e3d88513be6d052b9e410`
- Receipt 082: consumed
- Formal proof count: 1; result: FAIL
- Readiness wait: bounded to 15,000 ms with 250 ms polling
- Navigation wait: bounded to 30,000 ms
- Screen attempts: bounded to 2
- Failed-attempt evidence is written immediately to an append-only sidecar and embedded in the A-003 result.
- No formal proof, rerun, production change, candidate-runtime promotion, Current Map change, Safe Writer change, persisted-data change, or Pass 3 work is authorized.
- The repair PR must remain unmerged until separately authorized.
