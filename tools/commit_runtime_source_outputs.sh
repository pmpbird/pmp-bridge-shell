#!/usr/bin/env bash
set -euo pipefail
files=(
  audit/applicability/Packet_01.5_Current_Runtime_Source_Manifest_v1.json
  audit/applicability/Packet_01.5_Current_Runtime_Source_Decisions_v1.jsonl
  audit/applicability/Packet_01.5_Current_Runtime_Source_Remaining_Queue_v1.jsonl
  audit/Packet_01.5_Current_Runtime_Source_Precedence_v1.json
  audit/Packet_01.5_Current_Runtime_Source_Bounded_Tests_v1.json
  audit/Packet_01.5_Current_Runtime_Source_Evidence_Matrix_v1.json
  audit/Packet_01.5_Current_Runtime_Source_Coverage_v1.json
  audit/Packet_01.5_Current_Runtime_Source_v1.md
  audit/Packet_01.5_Current_Runtime_Source_Independent_Verification_v1.json
  audit/Packet_01.5_Current_Runtime_Source_Independent_Verification_v1.md
  audit/Packet_01.5_Routing_Status_v89.md
)
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -- "${files[@]}"
changed=$(git diff --cached --name-only)
for path in $changed; do
  allowed=false
  for expected in "${files[@]}"; do [[ "$path" == "$expected" ]] && allowed=true; done
  [[ "$allowed" == true ]] || { echo "Unexpected staged file: $path"; exit 1; }
done
if ! git diff --cached --quiet; then
  git commit -m "Verify current runtime source family"
  git push origin "HEAD:${GITHUB_HEAD_REF:-${GITHUB_REF_NAME}}"
fi
