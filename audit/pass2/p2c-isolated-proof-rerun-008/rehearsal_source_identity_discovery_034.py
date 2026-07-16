#!/usr/bin/env python3
import ast
import hashlib
import json
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
output = pathlib.Path(sys.argv[2])
text = path.read_text()
lines = text.splitlines()
hits = []
for index, line in enumerate(lines, 1):
    if "source_repository_commit" in line:
        start = max(1, index - 12)
        end = min(len(lines), index + 12)
        hits.append({
            "line": index,
            "source": line,
            "context": [
                {"line": line_number, "source": lines[line_number - 1]}
                for line_number in range(start, end + 1)
            ],
        })

tree = ast.parse(text)
assignments = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value.value

comparisons = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Compare):
        continue
    segment = ast.get_source_segment(text, node) or ""
    if "source_repository_commit" not in segment:
        continue
    names = {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}
    comparisons.append({
        "line": getattr(node, "lineno", None),
        "expression": segment,
        "resolved_names": {
            name: assignments[name] for name in names if name in assignments
        },
    })

result = {
    "type": "PMP_P2C_REHEARSAL_SOURCE_IDENTITY_DISCOVERY_034",
    "status": "PASS" if hits else "FAIL",
    "validator_path": str(path),
    "validator_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "source_repository_commit_hits": hits,
    "comparison_candidates": comparisons,
    "forty_hex_literals_in_validator": sorted(set(re.findall(r"\b[0-9a-f]{40}\b", text))),
    "formal_proof_executed": False,
    "disposable_preparation_executed": False,
    "production_modified": False,
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
