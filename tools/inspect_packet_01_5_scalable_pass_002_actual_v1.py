#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='15f99fab2fea10f2cb62c1885eb403030060a7b7'
INV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OV='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl'
OUT=R/'audit/Packet_01.5_Scalable_Pass_002_Discovery_v1.json'
FIRST=123; LAST=244

def g(*a,b=False):
 p=subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def sb(p): return g('show',f'{A}:{p}',b=True)
def rows(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def sh(b): return hashlib.sha256(b).hexdigest()
def scalar_view(x):
 out={}
 for k,v in x.items():
  if isinstance(v,(str,int,float,bool)) or v is None: out[k]=v
  elif isinstance(v,list) and len(v)<=30: out[k]=v
  elif isinstance(v,dict) and len(v)<=30: out[k]=v
 return out

def main():
 g('cat-file','-e',f'{A}^{{commit}}')
 ib,ob=sb(INV),sb(OV); inv,ov=rows(ib),rows(ob)
 assert len(inv)==len(ov)==2750
 win_i=inv[FIRST-1:LAST]; win_o=ov[FIRST-1:LAST]
 assert len(win_i)==len(win_o)==122
 records=[]
 for pos,(src,cur) in enumerate(zip(win_i,win_o),start=FIRST):
  assert src['composite_address']==cur['composite_address']
  assert (src.get('envelope_hash') or src.get('source_envelope_hash'))==(cur.get('envelope_hash') or cur.get('source_envelope_hash'))
  assert src.get('source_block_hash')==cur.get('source_block_hash')
  records.append({
   'inventory_position':pos,
   'composite_address':src['composite_address'],
   'original_identifier':src.get('original_identifier'),
   'source_envelope_hash':src.get('envelope_hash') or src.get('source_envelope_hash'),
   'source_block_hash':src.get('source_block_hash'),
   'inventory_record':scalar_view(src),
   'starting_overlay_record':scalar_view(cur),
  })
 assert records[0]['composite_address']=='P01.5::P001::REG-001'
 result={'packet':'01.5','pass':'002','anchor':A,'inventory':{'path':INV,'sha256':sh(ib),'records':2750},'starting_overlay':{'path':OV,'sha256':sh(ob),'records':2750},'window':{'first_inventory_position':FIRST,'last_inventory_position':LAST,'records':122,'first_address':records[0]['composite_address'],'last_address':records[-1]['composite_address']},'records':records}
 OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'PASS','records':122,'first':records[0]['composite_address'],'last':records[-1]['composite_address'],'inventory_sha256':sh(ib),'overlay_sha256':sh(ob)},indent=2))
if __name__=='__main__': main()
