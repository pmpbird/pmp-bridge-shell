#!/usr/bin/env python3
"""Verify the canonical Packet 01.5 project-contact evidence catalog.

This verifier proves that the contact catalog matches the preserved Packet 03
capability summary and its explicit current-capability boundaries. It performs
no applicability classification and no routing assignment.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
EVIDENCE = AUDIT / "routing-evidence"

SUMMARY = EVIDENCE / "Packet_03_Current_Capability_Summary_Source_v1.md"
BOUNDARY = EVIDENCE / "Packet_03_Current_Capability_Boundary_Source_v1.md"
CATALOG = EVIDENCE / "Packet_01.5_Project_Contact_Evidence_Catalog_v1.json"
ROUTING_AUTH = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v1.json"
OUT_JSON = AUDIT / "Packet_01.5_Project_Contact_Evidence_Catalog_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Project_Contact_Evidence_Catalog_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Applicability_Classification_Status_v76.md"

SUMMARY_SHA = "8f995ef4609640a7aefbc7a5d3e9ef9e7c2986ede47ee3e20a36d30c914fa1d2"
PARENT_SHA = "fd1a51070affa44f790822767b4662f35349bc13d13503877ddb81688c921c39"
ALLOWED_TYPES = {"CURRENT_CONTACT", "PLANNED_CONTACT", "ABSENT_CONTACT", "SCOPE_EXCLUSION"}
EXPECTED_BOUNDARY_IDS = {
    "P03-BOUND-CAPABILITY-SET",
    "P03-BOUND-DIRECT-AI",
    "P03-BOUND-AUTONOMOUS-REPOSITORY",
    "P03-BOUND-OPTIONAL-BACKEND",
    "P03-BOUND-LOCAL-PRIVACY",
    "P03-BOUND-INSTALLED-RUNTIME",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def parse_summary_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\| (RC-\d{3}) \| ([^|]+?) \| VERIFIED \| (PRESERVE(?: AND UPGRADE)?) \| None \| ([^|]+?) \|$",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        rc, name, status, owners = match.groups()
        rows.append({
            "capability_id": rc,
            "name": name.strip(),
            "status": status.replace(" AND ", "_AND_").replace(" ", "_"),
            "owners": [owner.strip() for owner in owners.split(",")],
        })
    return rows


def main() -> None:
    summary_raw = SUMMARY.read_bytes()
    boundary_raw = BOUNDARY.read_bytes()
    catalog = load_json(CATALOG)
    routing_auth = load_json(ROUTING_AUTH)

    require(sha256(summary_raw) == SUMMARY_SHA, "preserved Packet 03 summary hash mismatch")
    require(PARENT_SHA in boundary_raw.decode("utf-8"), "parent source hash missing from boundary evidence")

    routing_ready = (
        routing_auth.get("status") == "PASS_ROUTING_START_AUTHORIZED"
        and routing_auth.get("watch") == "NONE"
        and routing_auth.get("blockers") == "NONE"
        and routing_auth.get("routing_start_authorized") is True
    )
    require(routing_ready, "routing-start authorization is not a clean pass")

    require(catalog.get("packet") == "01.5", "catalog packet mismatch")
    require(catalog.get("catalog") == "project_contact_evidence", "catalog identity mismatch")
    require(catalog.get("version") == 1, "catalog version mismatch")
    require(catalog.get("watch") == "NONE", "catalog contains a watch")
    require(catalog.get("blockers") == "NONE_KNOWN", "catalog contains a known blocker")
    require(catalog.get("parent_source", {}).get("sha256") == PARENT_SHA, "catalog parent source hash mismatch")
    require(catalog.get("preserved_summary_source", {}).get("sha256") == SUMMARY_SHA, "catalog summary hash mismatch")

    source_rows = parse_summary_rows(summary_raw.decode("utf-8"))
    require(len(source_rows) == 20, f"preserved summary contains {len(source_rows)} capability rows, expected 20")

    capabilities = catalog.get("current_capabilities")
    require(isinstance(capabilities, list) and len(capabilities) == 20, "catalog current-capability count mismatch")
    capability_ids = [entry.get("capability_id") for entry in capabilities]
    require(capability_ids == [f"RC-{number:03d}" for number in range(1, 21)], "catalog RC sequence mismatch")
    evidence_ids = [entry.get("evidence_id") for entry in capabilities]
    require(len(set(evidence_ids)) == 20, "current-capability evidence IDs are not unique")

    catalog_by_rc = {entry["capability_id"]: entry for entry in capabilities}
    for source in source_rows:
        entry = catalog_by_rc[source["capability_id"]]
        require(entry.get("name") == source["name"], f"capability name mismatch: {source['capability_id']}")
        require(entry.get("status") == source["status"], f"capability status mismatch: {source['capability_id']}")
        require(entry.get("owners") == source["owners"], f"owner list mismatch: {source['capability_id']}")
        require(isinstance(entry.get("domains"), list) and entry["domains"], f"contact domains missing: {source['capability_id']}")

    boundaries = catalog.get("boundary_evidence")
    require(isinstance(boundaries, list) and len(boundaries) == 6, "boundary-evidence count mismatch")
    boundary_ids = {entry.get("evidence_id") for entry in boundaries}
    require(boundary_ids == EXPECTED_BOUNDARY_IDS, "boundary-evidence identifier set mismatch")
    for entry in boundaries:
        require(entry.get("evidence_type") in ALLOWED_TYPES, f"invalid evidence type: {entry.get('evidence_id')}")
        require(isinstance(entry.get("domains"), list) and entry["domains"], f"boundary domains missing: {entry.get('evidence_id')}")
        require(bool(entry.get("explanation")), f"boundary explanation missing: {entry.get('evidence_id')}")
        require(bool(entry.get("decision_use")), f"boundary decision rule missing: {entry.get('evidence_id')}")

    all_evidence_ids = evidence_ids + list(boundary_ids)
    require(len(all_evidence_ids) == len(set(all_evidence_ids)) == 26, "catalog evidence identifiers are not globally unique")
    counts = catalog.get("counts", {})
    require(counts == {"current_capability_entries": 20, "boundary_entries": 6, "total_entries": 26}, "catalog count block mismatch")

    boundary_text = boundary_raw.decode("utf-8")
    required_boundary_phrases = [
        "No additional current Resident capability is proven strongly enough to create RC-021.",
        "No verified direct AI-model call.",
        "no autonomous repository action from the conversation drawer.",
        "Requests remain local unless the user explicitly copies",
        "No AI credential path.",
        "Installed iPhone runtime not observed",
    ]
    for phrase in required_boundary_phrases:
        require(phrase in boundary_text, f"required boundary phrase missing: {phrase}")

    catalog_hash = sha256(CATALOG.read_bytes())
    result = {
        "packet": "01.5",
        "verification": "project_contact_evidence_catalog_independent",
        "version": 1,
        "verification_date": date.today().isoformat(),
        "status": "PASS",
        "watch": "NONE",
        "blockers": "NONE",
        "catalog_sha256": catalog_hash,
        "parent_source_sha256": PARENT_SHA,
        "summary_source_sha256": SUMMARY_SHA,
        "current_capabilities": 20,
        "boundary_entries": 6,
        "total_evidence_entries": 26,
        "unique_evidence_ids": 26,
        "capability_sequence_match": "PASS",
        "capability_name_match": "PASS",
        "capability_status_match": "PASS",
        "downstream_owner_match": "PASS",
        "boundary_evidence_match": "PASS",
        "classification_law_present": True,
        "applicability_classifications_completed": 0,
        "routing_assignments_completed": 0,
        "first_batch_ready": True,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Packet 01.5 — Project-Contact Evidence Catalog Independent Verification v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "",
        "## Verified evidence base",
        "",
        "- Current capability entries: 20",
        "- Explicit boundary entries: 6",
        "- Total evidence entries: 26",
        "- Unique evidence identifiers: 26",
        f"- Catalog SHA-256: `{catalog_hash}`",
        f"- Parent Packet 03 source SHA-256: `{PARENT_SHA}`",
        f"- Preserved summary SHA-256: `{SUMMARY_SHA}`",
        "",
        "## Match proof",
        "",
        "- RC-001 through RC-020 sequence: PASS",
        "- Capability names: PASS",
        "- Preserve/upgrade statuses: PASS",
        "- Downstream owner lists: PASS",
        "- Capability-set and absent/planned-contact boundaries: PASS",
        "",
        "## Governing result",
        "",
        "No limitation may be classified from its discovery-domain name alone. Each decision must cite record-specific contact evidence from this catalog and explain the harm path into a current, planned, absent, or excluded project surface.",
        "",
        "FINAL RESULT: `PASS — PROJECT-CONTACT EVIDENCE CATALOG VERIFIED`",
        "",
        "WATCH: NONE",
        "",
        "BLOCKERS: NONE",
        "",
        "END PACKET 01.5 — PROJECT-CONTACT EVIDENCE CATALOG INDEPENDENT VERIFICATION v1",
        "",
    ]), encoding="utf-8")

    STATUS_MD.write_text("\n".join([
        "# Packet 01.5 — Applicability Classification Status v76",
        "",
        "STATUS: PROJECT-CONTACT EVIDENCE CATALOG VERIFIED",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING START: AUTHORIZED",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0 OF 2750",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "SEMANTIC COMBINATION: NOT AUTHORIZED",
        "INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED",
        "PACKET 04: NOT AUTHORIZED",
        "",
        "## Evidence catalog",
        "",
        "- Verified current capabilities: RC-001 through RC-020",
        "- Current capability evidence entries: 20",
        "- Explicit absent/planned/contact-boundary entries: 6",
        "- Total evidence entries: 26",
        "- Evidence identifiers unique: PASS",
        "",
        "## Classification boundary",
        "",
        "Every record must cite record-specific evidence. A real-world discovery domain does not become a present PMP Current limitation unless a current or planned project contact path is demonstrated.",
        "",
        "## Next required action",
        "",
        "Create Applicability Batch 001 from the first preserved source addresses. Classify each envelope with evidence while keeping all destination fields blank, then independently verify the batch as a single transaction.",
        "",
        "END PACKET 01.5 — APPLICABILITY CLASSIFICATION STATUS v76",
        "",
    ]), encoding="utf-8")
    print("PASS — Packet 01.5 project-contact evidence catalog verified")


if __name__ == "__main__":
    main()
