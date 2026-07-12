#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

PATCH_CHILD = r'''def patch_child(p,realm,actors):
 s=p.read_text();doc=p.name
 def external(m):
  attrs=m.group(1)
  srcm=re.search(r'\bsrc\s*=\s*([\'\"])(.*?)\1',attrs,re.I|re.S)
  if not srcm:return m.group(0)
  src=srcm.group(2);path=src.split('?')[0].split('#')[0].lstrip('./')
  if path in actors:return f'<script type="application/pmp-p2c-managed-actor" data-pmp-path="{path}" data-pmp-src="{src}"></script>'
  return m.group(0)
 s=re.sub(r'<script\b([^>]*)>\s*</script>',external,s,flags=re.I|re.S)
 def inline(m):
  attrs=m.group(1);body=m.group(2)
  if re.search(r'\bsrc\s*=',attrs,re.I):return m.group(0)
  if 'application/pmp-p2c-managed-' in attrs:return m.group(0)
  if re.search(r'\btype\s*=\s*([\'\"])(?:application/(?:json|ld\+json)|text/template)\1',attrs,re.I):return m.group(0)
  return f'<script type="application/pmp-p2c-managed-document" data-pmp-path="{doc}">{body}</script>'
 s=re.sub(r'<script\b([^>]*)>(.*?)</script>',inline,s,flags=re.I|re.S)
 marker='<script type="application/pmp-p2c-managed-'
 i=s.find(marker)
 if i<0:raise SystemExit('NO_MANAGED_TAG:'+doc)
 pre=f'<script id="pmpP2CProofLock" type="application/json">{{"status":"DISPOSABLE_PROOF_ACTIVE"}}</script>\n<script src="pmp-p2c-production-enforcement-prelude-candidate-001.js" data-pmp-realm="{realm}" data-pmp-document-path="{doc}"></script>\n'
 p.write_text(s[:i]+pre+s[i:])
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, type=Path)
    args = parser.parse_args()

    source = args.path.read_text()
    old_snapshot = "if p.is_file() and '.git/' not in p.relative_to(root).as_posix()}"
    new_snapshot = "if p.is_file() and p.relative_to(root).as_posix() != '.git' and '.git/' not in p.relative_to(root).as_posix()}"
    if old_snapshot not in source:
        raise SystemExit("WORKTREE_SNAPSHOT_PATCH_POINT_MISSING")
    source = source.replace(old_snapshot, new_snapshot, 1)

    start = source.index("def patch_child(")
    end = source.index("def write_runtime(", start)
    source = source[:start] + PATCH_CHILD + source[end:]
    args.path.write_text(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
