#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
APP=AUDIT/'applicability'
QUEUE=APP/'Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl'
INVENTORY=AUDIT/'routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
PASS=APP/'Packet_01.5_Runtime_Source_Pass_v1.json'
MANIFEST=APP/'Packet_01.5_Current_Runtime_Source_Manifest_v1.json'
DECISIONS=APP/'Packet_01.5_Current_Runtime_Source_Decisions_v1.jsonl'
REMAINING=APP/'Packet_01.5_Current_Runtime_Source_Remaining_Queue_v1.jsonl'
PRECEDENCE=AUDIT/'Packet_01.5_Current_Runtime_Source_Precedence_v1.json'
TESTS=AUDIT/'Packet_01.5_Current_Runtime_Source_Bounded_Tests_v1.json'
MATRIX=AUDIT/'Packet_01.5_Current_Runtime_Source_Evidence_Matrix_v1.json'
COVERAGE=AUDIT/'Packet_01.5_Current_Runtime_Source_Coverage_v1.json'
SUMMARY=AUDIT/'Packet_01.5_Current_Runtime_Source_v1.md'
VERIFY_JSON=AUDIT/'Packet_01.5_Current_Runtime_Source_Independent_Verification_v1.json'
VERIFY_MD=AUDIT/'Packet_01.5_Current_Runtime_Source_Independent_Verification_v1.md'
STATUS=AUDIT/'Packet_01.5_Routing_Status_v89.md'
