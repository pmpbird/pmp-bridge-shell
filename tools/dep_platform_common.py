#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path

FAMILY='DEPENDENCY_OR_PLATFORM_STATE'
QUEUE_SHA='1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a'
INVENTORY_SHA='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
GEN=('dependency_platform_family','dependency-platform-family','routing_status_v88')
EX_PREFIX=('audit/applicability/','audit/routing-inventory/','audit/routing-batches/','audit/baseline-source/','audit/routing-evidence/')
EX_TERM=('historical','reconstructed','provisional','discovery','draft','candidate','temporary')
PASS=('status: pass','"status": "pass"','status: approved','"status": "approved"','independently verified','verification: pass','completion receipt')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def rows(path:Path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]
def files(repo:Path):return subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines()
def anchor(repo:Path):
    try:return subprocess.check_output(['git','rev-parse','origin/main'],cwd=repo,text=True).strip()
    except subprocess.CalledProcessError:return subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
def ver(name:str):
    vals=re.findall(r'(?:^|[-_.])v(\d+)(?=[-_.]|$)',name,flags=re.I);return max((int(x) for x in vals),default=0)
def fam(name:str):return re.sub(r'(?:^|[-_.])v\d+(?=[-_.]|$)','-v#',name.lower())
def allowed(name:str):
    low=name.lower()
    return not(any(x in low for x in GEN) or any(low.startswith(x) for x in EX_PREFIX) or any(x in low for x in EX_TERM) or '/plans/' in low or '-plan-' in low) and Path(name).suffix.lower() in {'.md','.json','.txt','.html','.js','.toml','.yml','.yaml'}
def corpus(repo:Path,names:list[str]):
    use=[n for n in names if allowed(n)];mx={}
    for n in use:mx[fam(n)]=max(mx.get(fam(n),0),ver(n))
    out=[]
    for n in use:
        if ver(n) and ver(n)<mx[fam(n)]:continue
        p=repo/n
        if p.is_file():out.append({'path':n,'sha256':sha(p.read_bytes()),'text':p.read_text(encoding='utf-8',errors='replace')})
    d='\n'.join(f"{x['sha256']}|{x['path']}" for x in out)+'\n';return out,sha(d.encode())
def census(repo:Path,names:list[str]):
    out=[]
    for n in names:
        if any(x in n.lower() for x in GEN):continue
        p=repo/n
        if p.is_file():out.append({'path':n,'sha256':sha(p.read_bytes())})
    d='\n'.join(f"{x['sha256']}|{x['path']}" for x in out)+'\n';return out,sha(d.encode())
def runtime(repo:Path,names:list[str]):
    tracked=set(names);todo=['pmp-app-current.html','pmp-current-map-v9.json','pmp-route-guardian-current-loader-v14.html','pmp-current-inner-cleanbug-rgcontrols-v4.html','pmp-worker.js','wrangler.toml'];seen=[];out=[];pat=re.compile(r'[A-Za-z0-9._-]+\.(?:html|js|json)')
    while todo:
        n=todo.pop(0)
        if n in seen or n not in tracked or '/' in n:continue
        p=repo/n
        if not p.is_file():continue
        t=p.read_text(encoding='utf-8',errors='replace');seen.append(n);out.append({'path':n,'sha256':sha(p.read_bytes()),'text':t})
        for r in pat.findall(t):
            if r in tracked and r not in seen and r not in todo:todo.append(r)
    d='\n'.join(f"{x['sha256']}|{x['path']}" for x in out)+'\n';return out,sha(d.encode())
def claim(item):
    t=item['missing_proof'];return t.split('Preserved claim: ',1)[1] if 'Preserved claim: ' in t else t
def passages(text):return [re.sub(r'\s+',' ',b).strip() for b in re.split(r'\n\s*\n|\n[─═-]{8,}\n',text) if b.strip()]
def find(records,groups,minimum):
    out=[]
    for x in records:
        verified=any(m in x['text'].lower() for m in PASS);best=None
        for p in passages(x['text']):
            low=p.lower();count=sum(1 for g in groups if any(t in low for t in g))
            if count>=minimum and (best is None or count>best['groups']):best={'path':x['path'],'sha256':x['sha256'],'groups':count,'verified':verified,'passage':p[:900]}
        if best:out.append(best)
    return out
def three(found,complete):
    full=[x for x in found if x['groups']>=complete and x['verified']];ev=[{'path':x['path'],'sha256':x['sha256']} for x in found[:20]]
    if full:return 'DISPROVED',{'complete':full,'partial':found},ev
    if found:return 'UNRESOLVED',{'complete':[],'partial':found},ev
    return 'SUPPORTED',{'complete':[],'partial':[]},[]
