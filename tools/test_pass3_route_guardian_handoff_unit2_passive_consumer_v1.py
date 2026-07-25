#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RG = ROOT / "pmp-route-guardian-current-loader-v22.html"
MAP = ROOT / "pmp-current-map-v12.json"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
BOOT = ROOT / "pmp-app-current.html"
AUDIT = ROOT / "audit/pass3/pass3-route-guardian-handoff-unit2-passive-consumer-v1.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extract_function(source, name):
    marker = "function " + name + "("
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError("function not closed")


def main():
    source = RG.read_text(encoding="utf-8")
    current_map = json.loads(MAP.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert audit["selected_consumer"]["path"] == RG.name
    assert "consumeCurrentAppHandoff(loaded,handoff)" in source
    assert source.index("consumeCurrentAppHandoff(loaded,handoff)") < source.index("resolver.buildUrl(handoff")
    assert source.index("resolver.buildUrl(handoff") < source.index("location.href=launchUrl")
    assert source.count("localStorage.setItem") == 1
    assert "pmp_route_guardian_v22_receipt" in source

    record = next(item for item in manifest["records"] if item["path"] == RG.name)
    assert record["bytes"] == RG.stat().st_size
    assert record["sha256_hex"] == sha256(RG)
    assert record["git_blob_sha"] == git_blob(RG)
    bootstrap = BOOT.read_text(encoding="utf-8")
    sealed = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", bootstrap).group(1)
    assert sealed == sha256(MANIFEST)

    function_source = extract_function(source, "handoffError") + "\n" + extract_function(source, "consumeCurrentAppHandoff")
    node = f"""
const vm=require('vm');
const source={json.dumps(function_source)};
const map={json.dumps(current_map)};
function RouteError(code,message,details){{this.code=code;this.message=message;this.details=details||null;}}
const resolver={{RouteError, handoffType:'PMP_ROUTE_HANDOFF_V1', mapPath:'pmp-current-map-v12.json'}};
const context={{resolver,location:{{pathname:'/'+map.route_guardian.path}},decodeURIComponent,Object}};
vm.createContext(context);vm.runInContext(source,context);
const good={{type:'PMP_ROUTE_HANDOFF_V1',role:'current_app',map_path:'pmp-current-map-v12.json',map_version:String(map.app_version),route_epoch:String(map.route_epoch),path:String(map.current_app.path)}};
function accepts(h){{try{{context.consumeCurrentAppHandoff({{map}},h);return true}}catch(e){{return false}}}}
if(!accepts(good))throw new Error('canonical handoff rejected');
const cases=[];
for(const field of ['type','role','map_path','map_version','route_epoch','path']){{const h={{...good}};delete h[field];cases.push(h)}}
for(const [field,value] of [['type','OTHER'],['role','reload_owner'],['map_path','pmp-current-map-v11.json'],['map_version','stale'],['route_epoch','stale'],['path','pmp-current-reload-owner-v27.html']]){{cases.push({{...good,[field]:value}})}}
for(const h of cases)if(accepts(h))throw new Error('invalid handoff accepted '+JSON.stringify(h));
context.location.pathname='/wrong-consumer.html';
if(accepts(good))throw new Error('wrong source consumer accepted');
console.log('PASS: 1 canonical and '+(cases.length+1)+' fail-closed consumer cases');
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
        handle.write(node)
        node_path = handle.name
    subprocess.check_call(["node", node_path])

    assert current_map["route_guardian"]["path"] == RG.name
    assert current_map["current_app"]["path"] == "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html"
    print("PASS: Unit 2 passive consumer source, integrity chain, and preservation verified")


if __name__ == "__main__":
    main()
