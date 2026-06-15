#!/usr/bin/env bash
set -euo pipefail
path="audit/Packet_01.5_Current_Runtime_Source_Debug.log"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -- "$path"
changed=$(git diff --cached --name-only)
[[ "$changed" == "$path" ]] || { echo "Unexpected staged file: $changed"; exit 1; }
git commit -m "Record current runtime verifier diagnostic"
git push origin "HEAD:${GITHUB_HEAD_REF:-${GITHUB_REF_NAME}}"
