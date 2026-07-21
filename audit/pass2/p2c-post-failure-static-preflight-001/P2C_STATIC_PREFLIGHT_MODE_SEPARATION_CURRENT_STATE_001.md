# P2-C Post-Failure Static Preflight Mode Separation 001

This unit repairs only the Receipt 038 static-preflight mode contradiction.

## Current authority boundary

- Receipt 082 is consumed.
- Formal proof run count is 1.
- Formal proof result is FAIL.
- PR #122 remains open and unmerged at `ea337f534e89c04b842e3d88513be6d052b9e410`.
- Historical Receipt 082 and Directive 083 bytes remain preserved but are not current unconsumed authority.
- No rerun, second proof, merge, production change, Current Map change, persisted-data change, candidate repair, or Pass 3 work is authorized.

## Static modes

- `maintenance_reseal`: the historical Head Seal 084 trigger path must be absent from the pull-request diff, and all historical proof-package files must remain byte-exact against the base tree.
- `exact_head_seal`: the diff must be exactly one allowed seal path, the head parent must equal the pull-request base, and every parent/base-tree/hash/blob binding must pass. A pass is static validation only and does not create execution authority.

The checker and workflow use only bounded Git read commands and Python. They never invoke, source, dispatch, or execute a formal wrapper, controller, proof, browser lane, production candidate, or rerun.
