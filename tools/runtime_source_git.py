#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path

FAMILY='CURRENT_RUNTIME_SOURCE'
QUEUE_SHA='1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a'
INVENTORY_SHA='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
ENTRY='pmp-app-current.html'
FILE_REF=re.compile(r'[A-Za-z0-9._/-]+\.(?:html|js|json|toml|yml|yaml)')
SCRIPT_SRC=re.compile(r'<script[^>]+src=["\']([^"\']+)["\']',re.I)
EXCLUDED=('packet_01.5_','packet_01_5_','routing-inventory/','routing-evidence/','routing-batches/','baseline-source/')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def command(repo:Path,args:list[str],binary:bool=False):return subprocess.check_output(args,cwd=repo,text=not binary)
def main_sha(repo:Path)->str:return command(repo,['git','rev-parse','origin/main']).strip()
def main_files(repo:Path)->list[str]:return command(repo,['git','ls-tree','-r','--name-only','origin/main']).splitlines()
def main_bytes(repo:Path,path:str)->bytes:return command(repo,['git','show',f'origin/main:{path}'],binary=True)
def main_text(repo:Path,path:str)->str:return main_bytes(repo,path).decode('utf-8',errors='replace')
def jsonl(path:Path):return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
def claim(item):
    text=item['missing_proof'];return text.split('Preserved claim: ',1)[1] if 'Preserved claim: ' in text else text
def clean(value:str)->str:return value.split('?',1)[0].split('#',1)[0].lstrip('/')
def allowed(path:str,tracked:set[str])->bool:return path in tracked and not any(term in path.lower() for term in EXCLUDED)
def refs(text:str,tracked:set[str])->list[str]:
    out=[]
    for raw in FILE_REF.findall(text):
        path=clean(raw)
        if allowed(path,tracked) and path not in out:out.append(path)
    return out
def scripts(text:str,tracked:set[str])->list[str]:
    out=[]
    for raw in SCRIPT_SRC.findall(text):
        path=clean(raw)
        if allowed(path,tracked) and path not in out:out.append(path)
    return out
def entry_paths(text:str,tracked:set[str]):
    match=re.search(r'MAP_PATHS\s*=\s*\[([^\]]+)\]',text);maps=[]
    if match:maps=[clean(x) for x in re.findall(r'["\']([^"\']+)["\']',match.group(1)) if clean(x) in tracked]
    fallback=re.search(r'FALLBACK_LOADER\s*=\s*["\']([^"\']+)["\']',text)
    return maps,clean(fallback.group(1)) if fallback else ''
def source_map(path:Path):return {item['composite_address']:item for item in jsonl(path)}
