#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'pmp-runtime-integrity-manifest-v1.json'
SEAL=ROOT/'audit/a003-manifest-seal.json'
BOOTSTRAP=ROOT/'pmp-app-current.html'
RUNTIME_PATHS=[
 'pmp-boot-status-strip-owner-v1.js',
 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
]

NEW_STRIP_SCRIPT='(()=>{\n\'use strict\';\nconst V=\'2.0.0-pass4-unit2-current-path-passive\';\nconst OWNER=\'pmp-boot-status-strip-owner-v1\';\nconst CONTRACT=\'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1\';\nconst STRIP_ID=\'pmpAppOrchestratorBootStatusStripV1\';\nconst STYLE_ID=\'pmpBootStatusStripOwnerV1Style\';\nconst SLOW_MS=9000;\nconst READY_HIDE_MS=1200;\nconst startedAt=Date.now();\nlet hidden=false,lastStatus=null,timer=null;\nfunction now(){return new Date().toISOString()}\nfunction text(id){try{const x=document.getElementById(id);return String(x&&x.textContent||\'\').replace(/\\s+/g,\' \').trim()}catch(e){return\'\'}}\nfunction ready(id){try{return document.getElementById(id)?.getAttribute(\'data-ready\')===\'true\'}catch(e){return false}}\nfunction orchestrator(){try{return window.PMPAppOrchestratorV1}catch(e){return null}}\nfunction snapshot(){\n  const api=orchestrator();\n  const note=text(\'bootNote\');\n  const log=text(\'bootLog\');\n  const combined=(note+\' \'+log).toLowerCase();\n  return {\n    elapsed_ms:Date.now()-startedAt,\n    current_document:String(location&&location.pathname||\'\'),\n    app_orchestrator_present:!!api,\n    app_orchestrator_valid:!!api&&typeof api===\'object\',\n    app_orchestrator_acknowledged:ready(\'bootOrchestrator\')||!!(api&&typeof api.getLastLaunchGateReceipt===\'function\'),\n    route_ready:ready(\'bootRoute\'),\n    runtime_ready:ready(\'bootRuntime\'),\n    entry_ready:ready(\'bootEntry\'),\n    failure_signal:/fail|error|blocked|unavailable/.test(combined),\n    failure_detail:/fail|error|blocked|unavailable/.test(combined)?(note||log||\'Startup failure observed\'):\'\',\n  };\n}\nfunction derive(input){\n  const x=input&&typeof input===\'object\'?input:{};\n  if(x.failure_signal||x.app_orchestrator_present&&!x.app_orchestrator_valid){\n    return {state:\'BOOT_FAILURE\',label:\'Startup needs attention\',detail:x.failure_detail||\'A required startup acknowledgement is malformed or unavailable.\'};\n  }\n  if(x.app_orchestrator_acknowledged&&x.route_ready&&x.runtime_ready){\n    return {state:\'READY_ACKNOWLEDGED\',label:\'App Orchestrator ready\',detail:\'Startup acknowledged. PMP entry remains owned by the existing startup chain.\'};\n  }\n  if(Number(x.elapsed_ms)>=SLOW_MS){\n    return {state:\'BOOT_SLOW\',label:\'Startup is taking longer\',detail:\'Still observing. No repair, reroute, or ownership change is being attempted.\'};\n  }\n  return {state:\'BOOTING\',label:\'App Orchestrator working…\',detail:\'Observing the current startup chain.\'};\n}\nfunction statusFrom(input){\n  const observed=input&&typeof input===\'object\'?input:snapshot();\n  const state=derive(observed);\n  return Object.freeze({type:\'PMP_BOOT_STATUS_STRIP_PASSIVE_STATUS_V1\',version:V,contract:CONTRACT,owner:OWNER,at:now(),...state,observed:Object.freeze({...observed}),side_effects:Object.freeze({route_assignments:0,persisted_user_data_writes:0,app_orchestrator_ownership_transfers:0,startup_repairs:0})});\n}\nfunction ensureStyle(){\n  if(!document.head||document.getElementById(STYLE_ID))return;\n  const s=document.createElement(\'style\');s.id=STYLE_ID;\n  s.textContent=\'#\'+STRIP_ID+\'{position:fixed;left:10px;right:10px;top:calc(7px + env(safe-area-inset-top));z-index:2147483647;pointer-events:none;display:grid;justify-items:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}#\'+STRIP_ID+\' .pmpPassiveBootStrip{max-width:min(620px,calc(100vw - 20px));box-sizing:border-box;border:2px solid #07101c;border-radius:999px;background:rgba(255,255,255,.97);color:#07101c;padding:8px 13px;box-shadow:0 6px 18px rgba(0,0,0,.14);font-size:12px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#\'+STRIP_ID+\'[data-state="BOOT_SLOW"] .pmpPassiveBootStrip{background:#fff3de}#\'+STRIP_ID+\'[data-state="BOOT_FAILURE"] .pmpPassiveBootStrip{background:#ffd9d5}#\'+STRIP_ID+\'[data-state="READY_ACKNOWLEDGED"] .pmpPassiveBootStrip{background:#dfffe4}\';\n  document.head.appendChild(s);\n}\nfunction render(status){\n  if(hidden||!document.body)return status;\n  ensureStyle();\n  let root=document.getElementById(STRIP_ID);\n  if(!root){root=document.createElement(\'div\');root.id=STRIP_ID;root.setAttribute(\'role\',\'status\');root.setAttribute(\'aria-live\',\'polite\');document.body.appendChild(root)}\n  root.setAttribute(\'data-state\',status.state);\n  root.setAttribute(\'data-pmp-passive-contract\',CONTRACT);\n  root.innerHTML=\'\';\n  const line=document.createElement(\'div\');line.className=\'pmpPassiveBootStrip\';line.textContent=status.label+\' — \'+status.detail;root.appendChild(line);\n  return status;\n}\nfunction hide(){hidden=true;try{document.getElementById(STRIP_ID)?.remove();document.getElementById(STYLE_ID)?.remove()}catch(e){}if(timer)clearInterval(timer)}\nfunction tick(input){lastStatus=statusFrom(input);render(lastStatus);if(lastStatus.state===\'READY_ACKNOWLEDGED\')setTimeout(hide,READY_HIDE_MS);return lastStatus}\nfunction start(){tick();timer=setInterval(()=>tick(),250);setTimeout(()=>{if(timer)clearInterval(timer)},15000)}\nwindow.PMPBootStatusStripOwnerV1=Object.freeze({version:V,owner:OWNER,contract:CONTRACT,mode:\'passive_current_path_observer_only\',derive,statusFrom,tick,hide,getLastStatus:()=>lastStatus,sideEffects:Object.freeze({routeAssignments:0,persistedUserDataWrites:0,appOrchestratorOwnershipTransfers:0,startupRepairs:0})});\ntry{start()}catch(e){try{render(statusFrom({failure_signal:true,failure_detail:String(e&&e.message||e),app_orchestrator_present:false,app_orchestrator_valid:false,elapsed_ms:Date.now()-startedAt}))}catch(_){}}\n})();\n'
INNER_TAG='<script src="pmp-boot-status-strip-owner-v1.js?fresh=pass4-unit2-current-path-20260725A"></script>'
ORCH_TAG='<script src="pmp-app-orchestrator-v1.js?fresh=app-orchestrator-final-clean-startup-certification-20260709A"></script>'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def blob(b:bytes)->str:return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 (ROOT/'pmp-boot-status-strip-owner-v1.js').write_text(NEW_STRIP_SCRIPT,'utf-8')
 inner_path=ROOT/'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'
 inner=inner_path.read_text('utf-8')
 if INNER_TAG not in inner:
  assert inner.count(ORCH_TAG)==1
  inner=inner.replace(ORCH_TAG,ORCH_TAG+'\n'+INNER_TAG)
  inner_path.write_text(inner,'utf-8')
 m=json.loads(MANIFEST.read_text('utf-8'))
 idx={r['path']:r for r in m['records']}
 for rel in RUNTIME_PATHS:
  b=(ROOT/rel).read_bytes();d=hashlib.sha256(b).digest();r=idx[rel]
  r.update(bytes=len(b),git_blob_sha=blob(b),sha256_hex=d.hex(),sha256_base64=base64.b64encode(d).decode(),sri='sha256-'+base64.b64encode(d).decode())
 identity={
  'algorithm':m['algorithm'],'network_policy':m['network_policy'],
  'protected_bootstrap_sources':m['protected_bootstrap_sources'],
  'records':[{k:r[k] for k in ('path','bytes','git_blob_sha','sha256_hex','execution_class','enforcement')} for r in m['records']],
  'historical_records':m['historical_records'],'external_records':m['external_records'],
  'root_trust_anchors':m['root_trust_anchors'],'unlisted_executable_policy':m['unlisted_executable_policy'],
 }
 m['runtime_source_set_sha256']=sha(json.dumps(identity,sort_keys=True,separators=(',',':')).encode())
 mb=(json.dumps(m,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
 MANIFEST.write_bytes(mb)
 seal=json.loads(SEAL.read_text('utf-8'))
 seal.update(manifest_bytes=len(mb),manifest_sha256=sha(mb),runtime_source_set_sha256=m['runtime_source_set_sha256'],sealed_branch='agent/pass4-unit2-bounded-passive-strip-integration-v2',pass4_context='Pass 4 Unit 2 installs the locked passive Boot Status Strip contract at the selected current v30 inner-document boundary and refreshes only required runtime integrity identities.')
 SEAL.write_text(json.dumps(seal,indent=2,sort_keys=True)+'\n','utf-8')
 s=BOOTSTRAP.read_text('utf-8');s2,n=re.subn(r"const MANIFEST_SHA256='[0-9a-f]{64}';",f"const MANIFEST_SHA256='{sha(mb)}';",s,count=1);assert n==1
 BOOTSTRAP.write_text(s2,'utf-8')
 print('PASS: Pass 4 Unit 2 runtime integrity identities regenerated')
if __name__=='__main__':main()
