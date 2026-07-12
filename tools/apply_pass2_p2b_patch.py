#!/usr/bin/env python3
from __future__ import annotations
import base64,hashlib,json,subprocess,zlib
from pathlib import Path
BASE_COMMIT="c767844d53b4b393928170387b6f988e49fe1fc6"
BOOTSTRAP_FILES=["tools/apply_pass2_p2b_patch.py",".github/workflows/pass2-p2b-patch-publisher.yml"]
PAYLOAD_GLOB='pass2_p2b_patch_payload_*.b64'
def git_blob(data:bytes)->str:return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
def main()->int:
 subprocess.run(["git","merge-base","--is-ancestor",BASE_COMMIT,"HEAD"],check=True)
 chunk_paths=sorted(Path('tools').glob(PAYLOAD_GLOB))
 if not chunk_paths: raise SystemExit('Patch payload chunks are missing')
 payload_text=''.join(path.read_text().strip() for path in chunk_paths)
 payload=json.loads(zlib.decompress(base64.b64decode(payload_text)))
 BOOTSTRAP_FILES.extend(str(path) for path in chunk_paths)
 for name,record in payload.items():
  path=Path(name); old=record["old_git_blob"]
  if old is None:
   if path.exists(): raise SystemExit(f"Refusing to replace unexpected new path: {name}")
  else:
   if not path.is_file(): raise SystemExit(f"Required base file missing: {name}")
   actual=git_blob(path.read_bytes())
   if actual!=old: raise SystemExit(f"Base identity mismatch for {name}: {actual} != {old}")
 for name,record in payload.items():
  path=Path(name); path.parent.mkdir(parents=True,exist_ok=True)
  data=base64.b64decode(record["content_b64"])
  if hashlib.sha256(data).hexdigest()!=record["sha256"]: raise SystemExit(f"Payload digest mismatch: {name}")
  path.write_bytes(data)
 for name in BOOTSTRAP_FILES:
  path=Path(name)
  if path.exists(): path.unlink()
 result={"type":"PMP_PASS2_P2B_PATCH_APPLICATION_V1","status":"PASS","base_commit":BASE_COMMIT,"files_written":len(payload),"paths":sorted(payload),"bootstrap_files_removed":BOOTSTRAP_FILES,"pass2_complete":False,"pass3_started":False}
 Path('/tmp/pass2-p2b-patch-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True))
 return 0
if __name__=="__main__": raise SystemExit(main())
