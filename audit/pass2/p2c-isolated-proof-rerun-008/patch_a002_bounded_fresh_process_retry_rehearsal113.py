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
        raise SystemExit(f"REHEARSAL113_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


HELPER = r'''def a002_retryable_infrastructure_timeout(command_result,result_path):
 try:payload=json.loads(result_path.read_text())
 except Exception:return False
 fatal=payload.get('fatal_error')
 if command_result.get('status')=='PASS' or payload.get('tests_failed')!=0 or not isinstance(payload.get('tests_passed'),int) or payload.get('tests_passed')<=0 or not isinstance(fatal,dict):return False
 name=str(fatal.get('name') or '')
 message=str(fatal.get('message') or '')
 return ('page.goto' in message or 'ERR_ABORTED' in message) and (name=='TimeoutError' or 'Timeout' in message or 'ERR_ABORTED' in message)
def run_a002_with_bounded_fresh_process_retry(name,cmd,cwd,env,command_out,timeout,result_path,evidence_dir):
 attempts=[]
 for attempt in (1,2):
  attempt_result=evidence_dir/f'{result_path.stem}-attempt-{attempt}.json'
  attempt_command=evidence_dir/f'{result_path.stem}-attempt-{attempt}-command.json'
  attempt_env=dict(env);attempt_env['A002_RESULT_PATH']=str(attempt_result)
  command_result=run(f'{name}-attempt-{attempt}',cmd,cwd,attempt_env,attempt_command,timeout)
  attempts.append({'attempt':attempt,'command_evidence':attempt_command.name,'result_evidence':attempt_result.name,'status':command_result.get('status'),'returncode':command_result.get('returncode'),'elapsed_seconds':command_result.get('elapsed_seconds')})
  retryable=a002_retryable_infrastructure_timeout(command_result,attempt_result)
  if command_result.get('status')=='PASS' or attempt==2 or not retryable:
   if attempt_result.is_file():result_path.write_text(attempt_result.read_text())
   final=dict(command_result);final['name']=name;final['attempt_count']=attempt;final['attempts']=attempts;final['retry_model']='BOUNDED_ONE_FRESH_NODE_BROWSER_PROCESS_RETRY_FOR_ZERO_ASSERTION_FAILURE_PAGE_GOTO_TIMEOUT_ONLY';final['retryable_infrastructure_timeout']=retryable
   command_out.write_text(json.dumps(final,indent=2)+'\n')
   print(json.dumps({'event':'A002_BOUNDED_RETRY_FINAL','lane':name,'status':final['status'],'attempt_count':attempt,'retryable_infrastructure_timeout':retryable}),flush=True)
   return final
  print(json.dumps({'event':'A002_BOUNDED_RETRY','lane':name,'completed_attempt':attempt,'reason':'ZERO_ASSERTION_FAILURE_PAGE_GOTO_TIMEOUT','next_attempt':attempt+1}),flush=True)
 raise AssertionError('A002_BOUNDED_RETRY_UNREACHABLE')
'''


ACTIVE_OLD = "e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8000/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-active.json');results.append(run('a002-active-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-active-command.json',300))"
ACTIVE_NEW = "e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8000/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-active.json');results.append(run_a002_with_bounded_fresh_process_retry('a002-active-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-active-command.json',300,a.evidence_dir/'a002-active.json',a.evidence_dir))"

RESTORED_OLD = "e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',360))"
RESTORED_NEW = "e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run_a002_with_bounded_fresh_process_retry('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',360,a.evidence_dir/'a002-restored.json',a.evidence_dir))"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL113_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(original, "def stop_server(server,log):", HELPER + "def stop_server(server,log):", "HELPER_INSERTION")
    text = replace_once(text, ACTIVE_OLD, ACTIVE_NEW, "ACTIVE_LANE")
    text = replace_once(text, RESTORED_OLD, RESTORED_NEW, "RESTORED_LANE")
    compile(text, str(args.path), "exec")

    contracts = {
        "bounded_attempt_tuple": text.count("for attempt in (1,2):"),
        "fresh_node_process_invocations": text.count("command_result=run(f'{name}-attempt-{attempt}'"),
        "zero_assertion_failure_gate": text.count("payload.get('tests_failed')!=0"),
        "positive_progress_gate": text.count("payload.get('tests_passed')<=0"),
        "page_goto_gate": text.count("'page.goto' in message"),
        "a002_bounded_lane_calls": text.count("results.append(run_a002_with_bounded_fresh_process_retry("),
        "a002_unbounded_active_calls": text.count("results.append(run('a002-active-41'"),
        "a002_unbounded_restored_calls": text.count("results.append(run('a002-restored-41'"),
        "attempt_result_evidence": text.count("attempt_result=evidence_dir/f'{result_path.stem}-attempt-{attempt}.json'"),
        "attempt_command_evidence": text.count("attempt_command=evidence_dir/f'{result_path.stem}-attempt-{attempt}-command.json'"),
    }
    expected = {
        "bounded_attempt_tuple": 1,
        "fresh_node_process_invocations": 1,
        "zero_assertion_failure_gate": 1,
        "positive_progress_gate": 1,
        "page_goto_gate": 1,
        "a002_bounded_lane_calls": 2,
        "a002_unbounded_active_calls": 0,
        "a002_unbounded_restored_calls": 0,
        "attempt_result_evidence": 1,
        "attempt_command_evidence": 1,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL113_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_A002_BOUNDED_FRESH_PROCESS_RETRY_REHEARSAL_113",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "github_observation": "TWO_RUNS_PASSED_SEVEN_LANES_AND_ZERO_A002_ASSERTIONS_FAILED_BEFORE_NONDETERMINISTIC_PAGE_GOTO_TIMEOUT",
        "repair": "ONE_BOUNDED_FRESH_NODE_BROWSER_PROCESS_RETRY_FOR_A002_INFRASTRUCTURE_TIMEOUT_ONLY",
        "retry_eligibility": "NONZERO_PROGRESS_AND_ZERO_ASSERTION_FAILURES_AND_PAGE_GOTO_TIMEOUT_OR_ERR_ABORTED",
        "attempt_limit": 2,
        "fresh_process_per_attempt": True,
        "all_attempt_evidence_preserved": True,
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
    (args.evidence_dir / "a002-bounded-fresh-process-retry-repair-113.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
