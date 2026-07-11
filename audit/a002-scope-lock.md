# A-002 Scope Lock

P0, P1, and P2 are complete within their recorded tested scopes.

P2 changed only:

- `pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html`
- `pmp-reload-current-live-update-marker-v1.json`
- `pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html`
- `pmp-current-inner-cleanbug-rgcontrols-v23.html`
- `pmp-current-inner-cleanbug-rgcontrols-v4.html`
- `pmp-current-inner-cleanbug-rgcontrols-v3.html`
- `pmp-home-single-v6.html`

P3 is not authorized by this file.

Forbidden until a separate P3 instruction:

- Current Screen Pointer mutation;
- Reload World mutation;
- Launcher Reload Bridge mutation;
- reload guard mutation;
- storage, cache, IndexedDB, or Bank clearing;
- merge to main;
- live-runtime certification claims not supported by a browser exercise.
