#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass

CURRENT = "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html"
INTEGRITY_SW = "pmp-integrity-service-worker-v1.js"
EXPECTED_SW_VERSION = "1.1.0-a003-runtime-integrity-sri"
EXPECTED_MANIFEST = "pmp-runtime-integrity-manifest-v1.json"
READINESS_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000
POLL_MS = 250

STATE_OLD = "const state = { tamperPath: null, offlinePath: null, requests: [] };"
STATE_NEW = r'''const state = { tamperPath: null, offlinePath: null, requests: [], guardianDiagnostics: [] };
const A003_GUARDIAN_EVIDENCE_PATH = process.env.A003_GUARDIAN_EVIDENCE_PATH || RESULT_PATH + '.guardian-readiness.json';'''
OUTPUT_OLD = "fatal_error: fatalError, results, request_count: state.requests.length"
OUTPUT_NEW = "fatal_error: fatalError, results, request_count: state.requests.length, guardian_diagnostics: state.guardianDiagnostics, guardian_evidence_path: A003_GUARDIAN_EVIDENCE_PATH"

A003_OPEN_CURRENT_FUNCTION_OLD = r'''async function openCurrentFromGuardian(page, screen) {
  const frame = await guardianFrame(page);
  await frame.click('#openBtn',{force:true});
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#' + screen, { timeout: 30000, waitUntil: 'commit' });
  return frameReachedHome(page, '#' + screen);
}'''

A003_OPEN_CURRENT_FUNCTION_NEW = r'''async function openCurrentFromGuardian(page, screen, attempt) {
  const readinessTimeoutMs = 15000;
  const navigationTimeoutMs = 30000;
  const pollMs = 250;
  const startedAt = Date.now();
  const expectedHash = '#' + screen;
  const requestStart = state.requests.length;
  const navigationEvents = [];
  const readinessHistory = [];
  const persistGuardianAttempt = evidence => {
    const normalized = {
      type: 'PMP_P2C_A003_GUARDIAN_READINESS_ATTEMPT_EVIDENCE_001',
      evidence_id: evidence.evidence_id || `${screen}:${attempt}:${evidence.phase || 'unknown'}:${Date.now()}`,
      captured_at: new Date().toISOString(),
      ...evidence
    };
    state.guardianDiagnostics.push(normalized);
    fs.mkdirSync(path.dirname(A003_GUARDIAN_EVIDENCE_PATH), { recursive:true });
    fs.writeFileSync(A003_GUARDIAN_EVIDENCE_PATH, JSON.stringify({
      type: 'PMP_P2C_A003_GUARDIAN_READINESS_EVIDENCE_BUNDLE_001',
      status: state.guardianDiagnostics.some(row => row.status === 'FAIL') ? 'FAIL_EVIDENCE_PRESERVED' : 'PASS_OR_IN_PROGRESS',
      readiness_timeout_ms: readinessTimeoutMs,
      navigation_timeout_ms: navigationTimeoutMs,
      poll_ms: pollMs,
      bounded_screen_attempts: 2,
      attempts: state.guardianDiagnostics
    }, null, 2) + '\n');
    console.log(`A003_GUARDIAN_ATTEMPT_EVIDENCE ${JSON.stringify({evidence_id:normalized.evidence_id,screen,attempt,phase:normalized.phase,status:normalized.status,elapsed_ms:normalized.elapsed_ms})}`);
    return normalized;
  };
  const topControllerUrl = async () => page.evaluate(() => navigator.serviceWorker?.controller?.scriptURL || null).catch(() => null);
  const onFrameNavigated = navigatedFrame => navigationEvents.push({
    at: new Date().toISOString(),
    url: navigatedFrame.url(),
    main_frame: navigatedFrame === page.mainFrame()
  });
  page.on('framenavigated', onFrameNavigated);
  let frame = null;
  let readiness = null;
  let guardianFrameUrlBeforeClick = null;
  let surfaceBeforeClick = null;
  const guardianSurface = async () => {
    if (!frame || frame.isDetached()) return null;
    return frame.evaluate(() => {
      const readJson = key => { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch { return null; } };
      const button = document.getElementById('openBtn');
      const rect = button && button.getBoundingClientRect ? button.getBoundingClientRect() : null;
      return {
        guardian_frame_url: location.href,
        controller_url: navigator.serviceWorker?.controller?.scriptURL || null,
        guardian_message: document.getElementById('msg')?.textContent || null,
        guardian_report: document.getElementById('report')?.textContent || null,
        guardian_receipt: readJson('pmp_route_guardian_v22_receipt'),
        launch_state: {
          present: !!button,
          disabled: button ? !!button.disabled : null,
          visible: !!(button && rect && rect.width > 0 && rect.height > 0),
          text: button?.textContent || null
        }
      };
    }).catch(error => ({ evaluation_error: String(error?.message || error) }));
  };
  try {
    frame = await guardianFrame(page);
    guardianFrameUrlBeforeClick = frame.url();
    const readinessDeadline = Date.now() + readinessTimeoutMs;
    while (Date.now() < readinessDeadline) {
      readiness = await frame.evaluate(async ({ current, expectedHash, integritySw, expectedVersion, expectedManifest }) => {
        const button = document.getElementById('openBtn');
        const rect = button && button.getBoundingClientRect ? button.getBoundingClientRect() : null;
        const resolver = globalThis.PMPCurrentRouteResolver || null;
        const controller = navigator.serviceWorker?.controller || null;
        const controllerUrl = controller?.scriptURL || null;
        const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
        const nativeFetch = globalThis.__PMP_A003_TEST_NATIVE_FETCH;
        let integrity = null;
        let integrityError = null;
        let handoff = null;
        let handoffError = null;
        if (controller && typeof nativeSetter === 'function') {
          try {
            integrity = await new Promise((resolve, reject) => {
              const timer = setTimeout(() => reject(new Error('guardian_readiness_integrity_timeout')), 7000);
              const channel = new MessageChannel();
              nativeSetter.call(channel.port1, event => { clearTimeout(timer); resolve(event.data || null); });
              controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a003-guardian-readiness-test' }, [channel.port2]);
            });
          } catch (error) { integrityError = String(error?.message || error); }
        } else {
          integrityError = !controller ? 'controller_missing' : 'native_messageport_setter_missing';
        }
        if (resolver && typeof nativeFetch === 'function') {
          try {
            const [mapResponse, manifestResponse] = await Promise.all([
              nativeFetch('pmp-current-map-v12.json', { cache:'no-store' }),
              nativeFetch(expectedManifest, { cache:'no-store' })
            ]);
            if (!mapResponse.ok) throw new Error('current_map_http_' + mapResponse.status);
            if (!manifestResponse.ok) throw new Error('integrity_manifest_http_' + manifestResponse.status);
            const map = await mapResponse.json();
            const manifest = await manifestResponse.json();
            const node = map.current_app || null;
            const record = (manifest.records || []).find(row => row.path === node?.path) || null;
            handoff = {
              path: node?.path || null,
              map_path: 'pmp-current-map-v12.json',
              map_version: map.app_version || null,
              route_epoch: map.route_epoch || null,
              role: 'current_app',
              source_sha256: record?.sha256_hex || null,
              integrity_manifest_sha256: integrity?.receipt?.manifest_sha256 || null,
              normalized_hash: Array.isArray(map.allowed_hashes) && map.allowed_hashes.includes(location.hash) ? location.hash : (map.default_hash || null),
              map_integrity_header: mapResponse.headers.get('X-PMP-Integrity'),
              manifest_integrity_header: manifestResponse.headers.get('X-PMP-Integrity')
            };
          } catch (error) { handoffError = String(error?.message || error); }
        } else {
          handoffError = !resolver ? 'resolver_missing' : 'native_fetch_missing';
        }
        const integrityReceipt = integrity?.receipt || null;
        const controllerReady = !!controllerUrl && controllerUrl.includes('/' + integritySw);
        const integrityReady = integrity?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && integrityReceipt?.state === 'ENFORCED' && integrityReceipt?.version === expectedVersion && integrityReceipt?.manifest_path === expectedManifest;
        const handoffReady = !!handoff && handoff.path === current && /^[0-9a-f]{64}$/.test(String(handoff.source_sha256 || '')) && /^[0-9a-f]{64}$/.test(String(handoff.integrity_manifest_sha256 || '')) && handoff.normalized_hash === expectedHash;
        const launchReady = !!button && button.disabled === false && !!rect && rect.width > 0 && rect.height > 0;
        return {
          ready: controllerReady && integrityReady && handoffReady && launchReady,
          controller_url: controllerUrl,
          controller_ready: controllerReady,
          integrity_status: integrity,
          integrity_error: integrityError,
          current_map_handoff: handoff,
          current_map_handoff_error: handoffError,
          canonical_reload_ready: handoffReady,
          launch_state: { present: !!button, disabled: button ? !!button.disabled : null, visible: !!(button && rect && rect.width > 0 && rect.height > 0), text: button?.textContent || null },
          guardian_message: document.getElementById('msg')?.textContent || null,
          guardian_report: document.getElementById('report')?.textContent || null
        };
      }, { current: CURRENT, expectedHash, integritySw: INTEGRITY_SW, expectedVersion: '1.1.0-a003-runtime-integrity-sri', expectedManifest: MANIFEST });
      readinessHistory.push({ at: new Date().toISOString(), ...readiness });
      if (readiness?.ready) break;
      await page.waitForTimeout(pollMs);
    }
    if (!readiness?.ready) throw new Error('A003_GUARDIAN_READINESS_TIMEOUT');
    surfaceBeforeClick = await guardianSurface();
    await frame.click('#openBtn', { force:true });
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === expectedHash, { timeout:navigationTimeoutMs, waitUntil:'commit' });
    const home = await frameReachedHome(page, expectedHash);
    const success = {
      type: 'PMP_A003_GUARDIAN_READINESS_ATTEMPT_001',
      status: 'PASS',
      screen,
      attempt,
      expected_path: CURRENT,
      expected_hash: expectedHash,
      observed_top_level_url: page.url(),
      guardian_frame_url: surfaceBeforeClick?.guardian_frame_url || guardianFrameUrlBeforeClick,
      controller_url: readiness.controller_url,
      top_controller_url: await topControllerUrl(),
      canonical_reload_ready: readiness.canonical_reload_ready,
      integrity_status: readiness.integrity_status,
      current_map_handoff: readiness.current_map_handoff,
      launch_state: readiness.launch_state,
      guardian_message: surfaceBeforeClick?.guardian_message || readiness.guardian_message,
      guardian_report: surfaceBeforeClick?.guardian_report || readiness.guardian_report,
      guardian_receipt: await page.evaluate(() => { try { return JSON.parse(localStorage.getItem('pmp_route_guardian_v22_receipt') || 'null'); } catch { return null; } }).catch(() => surfaceBeforeClick?.guardian_receipt || null),
      navigation_assignment_observed: true,
      navigation_events: navigationEvents.slice(-32),
      request_ledger: state.requests.slice(requestStart),
      elapsed_ms: Date.now() - startedAt,
      timeout_evidence: { timed_out:false, readiness_timeout_ms:readinessTimeoutMs, navigation_timeout_ms:navigationTimeoutMs, poll_ms:pollMs, elapsed_ms:Date.now() - startedAt },
      readiness_history: readinessHistory.slice(-8)
    };
    const persistedSuccess = persistGuardianAttempt(success);
    console.log(`A003_GUARDIAN_ATTEMPT_PASS ${JSON.stringify(persistedSuccess)}`);
    return { ...home, guardian_readiness: readiness, guardian_attempt: persistedSuccess };
  } catch (error) {
    const surface = await guardianSurface();
    const observedTopLevelUrl = page.url();
    let observedPath = null;
    let observedHash = null;
    try { const parsed = new URL(observedTopLevelUrl); observedPath = parsed.pathname; observedHash = parsed.hash; } catch {}
    const requestLedger = state.requests.slice(requestStart);
    const navigationAssignmentObserved = !!(
      (observedPath && observedPath.endsWith('/' + CURRENT)) ||
      requestLedger.some(row => row.path === CURRENT) ||
      navigationEvents.some(row => { try { return new URL(row.url).pathname.endsWith('/' + CURRENT); } catch { return false; } })
    );
    const evidence = {
      type: 'PMP_A003_GUARDIAN_READINESS_ATTEMPT_001',
      status: 'FAIL',
      phase: readiness?.ready ? 'NAVIGATION' : 'READINESS',
      screen,
      attempt,
      expected_path: CURRENT,
      expected_hash: expectedHash,
      observed_top_level_url: observedTopLevelUrl,
      observed_path: observedPath,
      observed_hash: observedHash,
      guardian_frame_url: surface?.guardian_frame_url || surfaceBeforeClick?.guardian_frame_url || guardianFrameUrlBeforeClick,
      guardian_message: surface?.guardian_message || readiness?.guardian_message || null,
      guardian_report: surface?.guardian_report || readiness?.guardian_report || null,
      guardian_receipt: surface?.guardian_receipt || await page.evaluate(() => { try { return JSON.parse(localStorage.getItem('pmp_route_guardian_v22_receipt') || 'null'); } catch { return null; } }).catch(() => null),
      controller_url: surface?.controller_url || readiness?.controller_url || null,
      top_controller_url: await topControllerUrl(),
      integrity_status: readiness?.integrity_status || null,
      integrity_error: readiness?.integrity_error || null,
      current_map_handoff: readiness?.current_map_handoff || null,
      current_map_handoff_error: readiness?.current_map_handoff_error || null,
      canonical_reload_ready: readiness?.canonical_reload_ready === true,
      launch_state: surface?.launch_state || readiness?.launch_state || null,
      navigation_assignment_observed: navigationAssignmentObserved,
      navigation_events: navigationEvents.slice(-32),
      request_ledger: requestLedger,
      readiness_history: readinessHistory.slice(-8),
      timeout_evidence: {
        timed_out: /timeout/i.test(String(error?.name || '') + ' ' + String(error?.message || error)),
        readiness_timeout_ms: readinessTimeoutMs,
        navigation_timeout_ms: navigationTimeoutMs,
        poll_ms: pollMs,
        elapsed_ms: Date.now() - startedAt
      },
      error: { name: String(error?.name || 'Error'), message: String(error?.message || error), stack: String(error?.stack || '') }
    };
    const persistedFailure = persistGuardianAttempt(evidence);
    console.log(`A003_GUARDIAN_ATTEMPT_FAILED ${JSON.stringify(persistedFailure)}`);
    const wrapped = new Error('A003_GUARDIAN_ATTEMPT_FAILED:' + JSON.stringify({ evidence_id:persistedFailure.evidence_id, screen, attempt, phase:persistedFailure.phase, original_name:String(error?.name || 'Error'), original_message:String(error?.message || error) }));
    wrapped.name = String(error?.name || 'Error');
    wrapped.stack = String(error?.stack || wrapped.stack || '');
    wrapped.pmpGuardianEvidence = persistedFailure;
    throw wrapped;
  } finally {
    page.off('framenavigated', onFrameNavigated);
  }
}'''


class ContractViolation(ValueError):
    pass


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ContractViolation(f"{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


def patch_generated_harness_source(text: str) -> str:
    text = replace_once(text, STATE_OLD, STATE_NEW, "STATE")
    text = replace_once(text, OUTPUT_OLD, OUTPUT_NEW, "OUTPUT")
    text = replace_once(text, A003_OPEN_CURRENT_FUNCTION_OLD, A003_OPEN_CURRENT_FUNCTION_NEW, "OPEN_CURRENT_FUNCTION")
    return text


def runner_injection_source() -> str:
    return (
        " a003_guardian_state_old=" + repr(STATE_OLD) + "\n"
        " a003_guardian_state_new=" + repr(STATE_NEW) + "\n"
        " if s.count(a003_guardian_state_old)!=1:raise SystemExit(f'GUARDIAN001_STATE_ANCHOR_INVALID:{s.count(a003_guardian_state_old)}')\n"
        " s=s.replace(a003_guardian_state_old,a003_guardian_state_new,1)\n"
        " a003_guardian_output_old=" + repr(OUTPUT_OLD) + "\n"
        " a003_guardian_output_new=" + repr(OUTPUT_NEW) + "\n"
        " if s.count(a003_guardian_output_old)!=1:raise SystemExit(f'GUARDIAN001_OUTPUT_ANCHOR_INVALID:{s.count(a003_guardian_output_old)}')\n"
        " s=s.replace(a003_guardian_output_old,a003_guardian_output_new,1)\n"
        " a003_guardian_open_old=" + repr(A003_OPEN_CURRENT_FUNCTION_OLD) + "\n"
        " a003_guardian_open_new=" + repr(A003_OPEN_CURRENT_FUNCTION_NEW) + "\n"
        " if s.count(a003_guardian_open_old)!=1:raise SystemExit(f'GUARDIAN001_OPEN_CURRENT_ANCHOR_INVALID:{s.count(a003_guardian_open_old)}')\n"
        " s=s.replace(a003_guardian_open_old,a003_guardian_open_new,1)\n"
    )


def apply_guardian_readiness_patch_to_runner(text: str) -> str:
    return replace_once(text, " a003.write_text(s)", runner_injection_source() + " a003.write_text(s)", "RUNNER_WRITE")


def validate_readiness_snapshot(snapshot: dict) -> None:
    controller = str(snapshot.get("controller_url") or "")
    if not controller.endswith("/" + INTEGRITY_SW):
        raise ContractViolation("MISSING_CONTROLLER")
    integrity = snapshot.get("integrity_status") or {}
    receipt = integrity.get("receipt") or {}
    if integrity.get("type") != "PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE" or receipt.get("state") != "ENFORCED" or receipt.get("version") != EXPECTED_SW_VERSION or receipt.get("manifest_path") != EXPECTED_MANIFEST:
        raise ContractViolation("MISSING_INTEGRITY_RESPONSE")
    handoff = snapshot.get("current_map_handoff") or {}
    if handoff.get("path") != CURRENT or len(str(handoff.get("source_sha256") or "")) != 64 or len(str(handoff.get("integrity_manifest_sha256") or "")) != 64:
        raise ContractViolation("MISSING_CURRENT_MAP_HANDOFF")
    launch = snapshot.get("launch_state") or {}
    if launch.get("present") is not True or launch.get("disabled") is not False or launch.get("visible") is not True:
        raise ContractViolation("LAUNCH_NOT_READY")
    if snapshot.get("canonical_reload_ready") is not True:
        raise ContractViolation("CANONICAL_RELOAD_NOT_READY")


def assert_navigation_success(observation: dict, screen: str) -> None:
    if observation.get("navigation_assignment_observed") is not True:
        raise ContractViolation("NO_NAVIGATION_ASSIGNMENT")
    url = str(observation.get("observed_top_level_url") or "")
    if not url:
        raise ContractViolation("WRONG_FINAL_URL")
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if not parsed.path.endswith("/" + CURRENT):
        raise ContractViolation("WRONG_FINAL_URL")
    if parsed.fragment != screen:
        raise ContractViolation("WRONG_FINAL_HASH")


def validate_failure_evidence(evidence: dict) -> None:
    required_keys = {
        "screen", "attempt", "observed_top_level_url", "guardian_frame_url",
        "guardian_message", "guardian_report", "guardian_receipt", "request_ledger",
        "controller_url", "top_controller_url", "launch_state", "navigation_assignment_observed",
        "timeout_evidence", "error"
    }
    missing = sorted(required_keys - set(evidence))
    if missing:
        raise ContractViolation("FAILURE_EVIDENCE_MISSING:" + ",".join(missing))
    timeout = evidence.get("timeout_evidence")
    if not isinstance(timeout, dict) or not isinstance(timeout.get("timed_out"), bool) or timeout.get("readiness_timeout_ms") != READINESS_TIMEOUT_MS or timeout.get("navigation_timeout_ms") != NAVIGATION_TIMEOUT_MS or timeout.get("poll_ms") != POLL_MS or not isinstance(timeout.get("elapsed_ms"), int):
        raise ContractViolation("TIMEOUT_EVIDENCE_INVALID")
    if not isinstance(evidence.get("request_ledger"), list):
        raise ContractViolation("REQUEST_LEDGER_INVALID")
    if not isinstance(evidence.get("navigation_assignment_observed"), bool):
        raise ContractViolation("NAVIGATION_ASSIGNMENT_STATE_INVALID")


def contract_summary() -> dict:
    return {
        "type": "PMP_APP_ORCHESTRATOR_P2C_GUARDIAN_READINESS_DIAGNOSTIC_CONTRACT_001",
        "status": "STATIC_CONTRACT_DEFINED",
        "scope": "DISPOSABLE_A003_TEST_HARNESS_ONLY",
        "readiness_timeout_ms": READINESS_TIMEOUT_MS,
        "navigation_timeout_ms": NAVIGATION_TIMEOUT_MS,
        "poll_ms": POLL_MS,
        "bounded_attempts": 2,
        "captures": [
            "service_worker_controller", "canonical_reload_readiness", "integrity_status",
            "current_map_handoff", "launch_button_state", "guardian_message_report_receipt",
            "observed_top_level_url", "guardian_frame_url", "request_ledger",
            "navigation_events", "screen", "attempt", "elapsed_time", "append_only_attempt_sidecar"
        ],
        "production_changed": False,
        "candidate_runtime_changed": False,
        "formal_proof_authority_created": False,
        "formal_proof_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(contract_summary(), indent=2, sort_keys=True))
