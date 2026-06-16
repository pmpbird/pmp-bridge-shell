python3 -c "import base64,pathlib;p=pathlib.Path('tools/workflow_restore_payload.txt');pathlib.Path('.github/workflows/packet_015_pass_002_current_runtime_family.yml').write_bytes(base64.b64decode(p.read_text().strip()))"
rm tools/workflow_restore_payload.txt tools/restore_runtime_family_workflow.sh
