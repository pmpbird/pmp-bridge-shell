#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL114_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


OLD_SERVER_LIFECYCLE = r'''def stop_server(server,log):
 if server is None:return
 server.terminate()
 try:server.wait(timeout=10)
 except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
 log.write_text(txt(server.stdout.read() if server.stdout else '')+'\nSTDERR\n'+txt(server.stderr.read() if server.stderr else ''))'''


STREAMED_SERVER_LIFECYCLE = r'''def start_server(port,cwd,log):
 log_handle=log.open('w')
 try:server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=cwd,stdout=log_handle,stderr=subprocess.STDOUT,text=True)
 except Exception:
  log_handle.close();raise
 server._pmp_http_log_handle=log_handle
 return server
def stop_server(server,log):
 if server is None:return
 server.terminate()
 try:server.wait(timeout=10)
 except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
 log_handle=getattr(server,'_pmp_http_log_handle',None)
 if log_handle is not None:
  log_handle.flush();log_handle.close();return
 log.write_text(txt(server.stdout.read() if server.stdout else '')+'\nSTDERR\n'+txt(server.stderr.read() if server.stderr else ''))'''


ACTIVE_PIPE_SERVER = "server=subprocess.Popen([sys.executable,'-m','http.server','8000','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)"
ACTIVE_STREAMED_SERVER = "server=start_server('8000',a.activated_root,a.evidence_dir/'a002-active-http.log')"

RESTORED_PIPE_SERVER = "server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)"
RESTORED_STREAMED_SERVER = "server=start_server('8001',a.activated_root,a.evidence_dir/'a002-restored-http.log')"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL114_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(original, OLD_SERVER_LIFECYCLE, STREAMED_SERVER_LIFECYCLE, "SERVER_LIFECYCLE")
    text = replace_once(text, ACTIVE_PIPE_SERVER, ACTIVE_STREAMED_SERVER, "ACTIVE_SERVER")
    text = replace_once(text, RESTORED_PIPE_SERVER, RESTORED_STREAMED_SERVER, "RESTORED_SERVER")
    compile(text, str(args.path), "exec")

    contracts = {
        "start_server_definition": text.count("def start_server(port,cwd,log):"),
        "streamed_stdout": text.count("stdout=log_handle,stderr=subprocess.STDOUT"),
        "log_handle_attached": text.count("server._pmp_http_log_handle=log_handle"),
        "log_handle_closed": text.count("log_handle.flush();log_handle.close();return"),
        "active_streamed_server": text.count(ACTIVE_STREAMED_SERVER),
        "restored_streamed_server": text.count(RESTORED_STREAMED_SERVER),
        "active_pipe_server": text.count(ACTIVE_PIPE_SERVER),
        "restored_pipe_server": text.count(RESTORED_PIPE_SERVER),
        "bounded_a002_retry_calls": text.count("results.append(run_a002_with_bounded_fresh_process_retry("),
    }
    expected = {
        "start_server_definition": 1,
        "streamed_stdout": 1,
        "log_handle_attached": 1,
        "log_handle_closed": 1,
        "active_streamed_server": 1,
        "restored_streamed_server": 1,
        "active_pipe_server": 0,
        "restored_pipe_server": 0,
        "bounded_a002_retry_calls": 2,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL114_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_HTTP_SERVER_LOG_BACKPRESSURE_REHEARSAL_114",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "github_observation": {
            "active_http_log_bytes_and_result": "58499_PASS",
            "restored_http_log_bytes_and_result": "64033_TIMEOUT",
            "pipe_capacity_signature": "FAILURE_AT_APPROXIMATELY_64_KIB",
            "second_attempt_first_request_timeout": True,
        },
        "root_cause": "UNCONSUMED_HTTP_SERVER_STDERR_PIPE_BACKPRESSURE",
        "repair": "STREAM_HTTP_SERVER_STDOUT_AND_STDERR_DIRECTLY_TO_EVIDENCE_FILE",
        "http_logs_preserved": True,
        "bounded_retry_preserved": True,
        "assertions_weakened": False,
        "original_sha256": sha256(original.encode()),
        "patched_sha256": sha256(text.encode()),
        "contracts": contracts,
        "production_changed": False,
        "production_activation_authorized": False,
        "current_map_changed": False,
        "persisted_data_changed": False,
        "formal_proof_executed": False,
        "merge_authorized": False,
        "unknown_actor_policy_weakened": False,
        "unauthorized_capability_policy_weakened": False,
    }
    (args.evidence_dir / "http-server-log-backpressure-repair-114.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
