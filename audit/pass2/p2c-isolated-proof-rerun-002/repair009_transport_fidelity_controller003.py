#!/usr/bin/env python3
from pathlib import Path
import base64,hashlib,json,subprocess,sys

def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def main():
 root=Path(sys.argv[1]);parts=sorted(root.glob('transpile_async_sources.part*.b64'))
 if len(parts)!=3:raise SystemExit('PART_COUNT_INVALID')
 raw=''.join(''.join(p.read_text().splitlines()) for p in parts)
 b=base64.b64decode(raw,validate=True)
 if len(b)!=3723:raise SystemExit('BYTE_COUNT_INVALID')
 if sha(b)!='c5ffb899637aa45feb64b604dca426503f99fc9a34f05a1c83a12d0cfef3d0dd':raise SystemExit('SHA256_INVALID')
 if blob(b)!='06a33bfd0bed8cc4b914b519bab606ddcd719cd1':raise SystemExit('GIT_BLOB_INVALID')
 out=root/'transpile_async_sources.decoded.js';out.write_bytes(b)
 subprocess.run(['node','--check',str(out)],check=True)
 print(json.dumps({'status':'PASS','bytes':len(b),'sha256':sha(b),'git_blob_sha1':blob(b)},indent=2))
if __name__=='__main__':main()
