# A-002 Scope Lock

P0, P1, P2, and P3 are complete within their recorded tested scopes.

P3 changed only:

- `pmp-current-screen-pointer-v1.js`
- `pmp-reload-world-from-map-v1.js`
- `pmp-launcher-reload-current-bridge-v1.js`
- `pmp-launcher-reload-current-v2-guard.js`

P4 is not authorized by this file.

Forbidden until a separate P4 instruction:

- Safe Writer return mutation;
- Safe Writer page mutation;
- Code Safety route mutation;
- canonical Safe Writer route mutation;
- Route Guardian Action mutation;
- inner-v2 tool-return mutation;
- storage, cache, IndexedDB, or Bank clearing;
- merge to main;
- live-runtime certification claims not supported by a browser exercise.
