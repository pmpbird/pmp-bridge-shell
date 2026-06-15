#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
A='32eb61ff9376a769a23292f4de06c3fdc08236f0'
P=[
'audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl',
'audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl',
'audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl',
'audit/routing-batches/Packet_01.5_Applicability_Batch_005_Plan_v1.json',
'audit/routing-batches/Packet_01.5_Applicability_Batch_005_Independent_Verification_v1.json',
'audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md',
'audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json',
'control-pack/pmp-control-pack-conflict-resolver-v1.json',
'audit/baseline-source/reconstructed/pmp-current-permanent-limitation-register-v3-final.json',
'audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md']
def g(*a,b=False):
 c=subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE).stdout
 return c if b else c.decode()
def main():
 out=[]
 for p in P:
  d=g('show',f'{A}:{p}',b=True)
  log=g('log','-1','--format=%H%x09%cIx09%s',A,'--',p).strip().split('\t',2)
  out.append({'path':p,'content_sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':g('rev-parse',f'{A}:{p}').strip(),'last_change_commit':log[0],'last_change_date':log[1],"last_change_subject':log[2]})
 q=R/'audit/Packet_01.5_Cross_Source_Conflict_Targeted_Metadata_v1.json'
 q.write_text(json.dumps({'anchor':A,"sources':out},indent=2)+'\n')
 print(q.read_text())
if __name__=='__main__':main()
