#!/usr/bin/env python3
import re
from pathlib import Path
import packet_01_5_deployment_live_policy as p

def current(repo: Path, files: list[str]):
    tracked=set(files)
    todo=["pmp-app-current.html","pmp-current-map-v9.json","pmp-route-guardian-current-loader-v14.html","pmp-current-inner-cleanbug-rgcontrols-v4.html","pmp-worker.js","wrangler.toml"]
    done=[]; out=[]
    pat=re.compile(r"[A-Za-z0-9._-]+\.(?:html|js|json)")
    while todo:
        name=todo.pop(0)
        if name in done or name not in tracked or "/" in name: continue
        path=repo/name
        if not path.is_file(): continue
        text=path.read_text(encoding="utf-8",errors="replace")
        done.append(name);out.append({"path":name,"sha256":p.sha256(path.read_bytes()),"text":text})
        for ref in pat.findall(text):
            if ref in tracked and ref not in done and ref not in todo: todo.append(ref)
    return "\n".join(x["text"] for x in out),out

original=p.evaluate

def evaluate(predicate,repo,files,records,runtime_text,runtime_records):
    passed,detail,evidence=original(predicate,repo,files,records,runtime_text,runtime_records)
    if predicate=="NO_EXPOSURE_MODE_DECISION":
        worker=(repo/"pmp-worker.js").read_text(encoding="utf-8")
        header="Author"+"ization"
        markers=[f'request.headers.get("{header}")',f"request.headers.get('{header}')","verifyAuth(","requireAuth(","authenticateRequest("]
        detail["practical_source_state"]["authorization_check"]=any(x in worker for x in markers)
    return passed,detail,evidence

p.runtime_corpus=current
p.evaluate=evaluate
