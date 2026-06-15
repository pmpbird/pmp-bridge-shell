#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "32eb61ff9376a769a23292f4de06c3fdc08236f0"
PATHS = [
    "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl",
    "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl",
    "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl",
    "audit/routing-batches/Packet_01.5_Applicability_Batch_005_Plan_v1.json",
    "audit/routing-batches/Packet_01.5_Applicability_Batch_005_Independent_Verification_v1.json",
    "audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md",
    "audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json",
    "control-pack/pmp-control-pack-conflict-resolver-v1.json",
    "audit/baseline-source/reconstructed/pmp-current-permanent-limitation-register-v3-final.json",
    "audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md",
]

def git(*args, binary=False):
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE)
    return result.stdout if binary else result.stdout.decode("utf-8")

def main():
    sources = []
    for path in PATHS:
        data = git("show", f"{ANCHOR}:{path}", binary=True)
        commit, date, subject = git("log", "-1", "--format=%H%x09%cI%x09%s", ANCHOR, "--", path).strip().split("\t", 2)
        sources.append({
            "path": path,
            "content_sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha": git("rev-parse", f"{ANCHOR}:{path}").strip(),
            "last_change_commit": commit,
            "last_change_date": date,
            "last_change_subject": subject,
        })
    output = ROOT / "audit/Packet_01.5_Cross_Source_Conflict_Targeted_Metadata_v1.json"
    output.write_text(json.dumps({"anchor": ANCHOR, "sources": sources}, indent=2) + "\n", encoding="utf-8")
    print(output.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
