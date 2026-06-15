#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
from runtime_source_git import ENTRY,clean,entry_paths,main_bytes,main_files,main_sha,main_text,refs,scripts,sha

WORKER_ROOTS=('pmp-worker.js','wrangler.toml')

def add_node(repo,nodes,path,role):
    if path in nodes:
        if role not in nodes[path]['roles']:nodes[path]['roles'].append(role)
        return
    nodes[path]={'path':path,'sha256':sha(main_bytes(repo,path)),'roles':[role]}
def add_edge(edges,source,target,kind):
    edge={'source':source,'target':target,'kind':kind}
    if edge not in edges:edges.append(edge)
def kind_for(source,target,text,direct,current_app,loader):
    if target in direct:return 'automatic-script'
    if source==loader and re.search(r'add\([^;]+["\']'+re.escape(target)+r'[?"\']',text):return 'runtime-injection-after-open'
    if source==current_app and target.endswith('.html'):return 'automatic-nested-wrapper'
    if source.endswith('v3.html') and target=='pmp-home-single-v6.html':return 'automatic-inner-application'
    if target.endswith('.html') and ('location.href' in text or 'actionUrl' in text):return 'manual-action-reachable'
    return 'literal-runtime-reference'

def build_graph(repo:Path):
    tracked=set(main_files(repo));nodes={};edges=[]
    add_node(repo,nodes,ENTRY,'public-entry');entry=main_text(repo,ENTRY);maps,fallback_loader=entry_paths(entry,tracked)
    if not maps:raise ValueError('No tracked current map declared')
    primary_map=maps[0];add_node(repo,nodes,primary_map,'primary-map');add_edge(edges,ENTRY,primary_map,'primary-map-first-success')
    for path in maps[1:]:add_node(repo,nodes,path,'fallback-map');add_edge(edges,ENTRY,path,'fallback-only-after-primary-map-failure')
    data=json.loads(main_text(repo,primary_map));loader=clean((data.get('route_guardian_loader') or data.get('current_loader') or {}).get('path',''));current_app=clean((data.get('current_app') or {}).get('path',''));fallback_app=clean((data.get('fallback_app') or {}).get('path',''))
    if loader not in tracked or current_app not in tracked:raise ValueError('Current map does not resolve tracked loader and app')
    add_node(repo,nodes,loader,'current-route-guardian');add_node(repo,nodes,current_app,'current-app-wrapper');add_edge(edges,primary_map,loader,'map-current-loader');add_edge(edges,loader,current_app,'manual-open-latest');add_edge(edges,primary_map,current_app,'map-current-app')
    if fallback_loader in tracked:add_node(repo,nodes,fallback_loader,'fallback-loader');add_edge(edges,ENTRY,fallback_loader,'fallback-only-after-map-failure')
    if fallback_app in tracked:add_node(repo,nodes,fallback_app,'fallback-app');add_edge(edges,primary_map,fallback_app,'fallback-only-app')
    primary=[ENTRY,primary_map,loader,current_app];seen=set(primary);queue=[current_app,loader]
    while queue:
        source=queue.pop(0);text=main_text(repo,source);direct=scripts(text,tracked)
        for target in refs(text,tracked):
            if target in maps or target==fallback_loader:continue
            kind=kind_for(source,target,text,direct,current_app,loader);add_node(repo,nodes,target,kind);add_edge(edges,source,target,kind)
            if kind in {'automatic-script','runtime-injection-after-open','automatic-nested-wrapper','automatic-inner-application','literal-runtime-reference'} and target not in seen:
                seen.add(target);primary.append(target);queue.append(target)
    for root in WORKER_ROOTS:
        if root in tracked:add_node(repo,nodes,root,'worker-or-platform-config');add_edge(edges,'platform',root,'worker-or-platform-config')
    fallback={e['target'] for e in edges if e['kind'].startswith('fallback-only')};manual={e['target'] for e in edges if e['kind']=='manual-action-reachable'};platform=set(WORKER_ROOTS)&tracked
    ordered=sorted(nodes.values(),key=lambda x:x['path']);edge_order=sorted(edges,key=lambda x:(x['source'],x['target'],x['kind']))
    digest='\n'.join([f"NODE|{x['sha256']}|{x['path']}|{','.join(sorted(x['roles']))}" for x in ordered]+[f"EDGE|{x['source']}|{x['target']}|{x['kind']}" for x in edge_order])+'\n'
    return {'main_commit':main_sha(repo),'public_entry':ENTRY,'map_precedence':maps,'primary_map':primary_map,'current_loader':loader,'current_app':current_app,'entry_fallback_loader':fallback_loader,'fallback_app':fallback_app,'nodes':ordered,'edges':edge_order,'primary_paths':sorted(set(primary)),'fallback_paths':sorted(fallback),'manual_action_paths':sorted(manual),'platform_paths':sorted(platform),'graph_sha256':sha(digest.encode())}
def graph_text(repo:Path,graph,manual=False):
    paths=list(graph['primary_paths'])+list(graph['platform_paths'])
    if manual:paths+=list(graph['manual_action_paths'])
    ordered=[]
    for path in paths:
        if path not in ordered:ordered.append(path)
    return '\n\n'.join(f'FILE:{path}\n{main_text(repo,path)}' for path in ordered)
