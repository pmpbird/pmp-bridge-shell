(() => {
  if (window.PMPContinuousRunSyncPacket15V1) return;
  window.PMPContinuousRunSyncPacket15V1 = true;

  const VERSION = '1.0.0-sync-v16-packet-1-5-manual-start-gate';
  const STATE_TYPE = 'PMP_CONTINUOUS_RUN_STATE_LEDGER_V2';
  const DRAFT_TYPE = 'PMP_FREE_IN_APP_CONTINUOUS_RUN_MISSION_DRAFT';
  const CURRENT_ROUTE = 'pmp-current-inner-cleanbug-rgcontrols-v16.html#control';
  const FALLBACK_ROUTE = 'pmp-route-guardian-last-good-v18.html';
  const RECOVERY_ROUTE = 'pmp-route-guardian-recovery-tools-v8.html';
  const PROOF_KEY = 'pmp_continuous_run_packet_1_5_gate_v1';
  const STATE_KEYS = [
    'pmp_continuous_run_state_ledger_v2',
    'pmp_same_shell_continuous_run_state_ledger_v2',
    'pmp_continuous_run_dashboard_state_v2'
  ];
  const DRAFT_KEYS = [
    'pmp_free_in_app_continuous_run_mission_draft_v1',
    'pmp_continuous_run_mission_draft_v1',
    'pmp_same_shell_continuous_run_mission_draft_v1'
  ];
  const MISSION_TEXT = 'Packet 1.5 continuous run: run through Packet 1.5 one verified unit at a time, using only the free path. Keep write authority none and merge authority none. Do not mutate the real app automatically. Stop on WATCH, BLOCKED, failed verification, unclear instruction, paid path, credential request, checkpoint mismatch, or manual stop. Start only after the user presses the manual Packet 1.5 start gate.';

  function now(){return new Date().toISOString()}
  function plusDays(d){const x=new Date();x.setDate(x.getDate()+d);return x.toISOString()}
  function readRaw(k){try{return localStorage.getItem(k)}catch(_){return null}}
  function read(k){try{const v=readRaw(k);return v?JSON.parse(v):null}catch(_){return null}}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(_){return false}}
  function allKeys(){try{return Array.from({length:localStorage.length},(_,i)=>localStorage.key(i)).filter(Boolean)}catch(_){return[]}}
  function findKeysByType(type){
    return allKeys().filter(k=>{const v=read(k);return v&&typeof v==='object'&&v.type===type});
  }
  function uniq(a){return Array.from(new Set(a.filter(Boolean)))}
  function inheritedState(){
    for(const k of uniq([...findKeysByType(STATE_TYPE),...STATE_KEYS])){const v=read(k);if(v&&typeof v==='object')return v}
    return null;
  }
  function inheritedDraft(){
    for(const k of uniq([...findKeysByType(DRAFT_TYPE),...DRAFT_KEYS])){const v=read(k);if(v&&typeof v==='object')return v}
    return null;
  }
  function patchState(old){
    const prev = old && typeof old==='object' ? old : {};
    const unitIndex = Math.max(73, Number((prev.verify_state&&prev.verify_state.unit_index)||72)+1);
    return {
      ...prev,
      type: STATE_TYPE,
      schema_version: '2.1.0',
      updated_at: now(),
      current_run_phase: 'packet_1_5_manual_start_gate_ready',
      current_app_route: CURRENT_ROUTE,
      current_active_route: CURRENT_ROUTE,
      route_guardian_fallback_route: FALLBACK_ROUTE,
      latest_recovery_tools_route: RECOVERY_ROUTE,
      current_before_last_good_route: CURRENT_ROUTE,
      current_before_last_good_sync_changed: true,
      route_guardian_protection_status: 'synced_to_current_v16_for_packet_1_5',
      current_cycle_count: Number(prev.current_cycle_count||0),
      cycles_reset: !!prev.cycles_reset,
      cycle_reset_state: prev.cycle_reset_state || { cycle_count: 0, cycles_reset: false, last_reset_at: null },
      last_completed_fix: 'continuous_run_sync_current_v16_packet_1_5_gate_v1',
      next_planned_fix: 'Packet 1.5 can begin only after the manual Packet 1.5 start gate is pressed by the user.',
      packet_1_5_gate: 'ready_after_user_start',
      blocked_state: 'not_blocked',
      do_not_repeat_fix_count: Number(prev.do_not_repeat_fix_count||6),
      do_not_repeat_fix_ledger_key: prev.do_not_repeat_fix_ledger_key || 'pmp_continuous_run_do_not_repeat_fix_ledger_v1',
      compile_state: {
        type: 'PMP_CONTINUOUS_RUN_COMPILED_UNIT_V1',
        compiled: true,
        status: 'compiled_packet_1_5_start_gate_only',
        resume_boundary: 'packet_1_5_manual_start_gate',
        visible_boundary_policy: 'shown_in_dashboard',
        unit_id: 'packet_1_5_manual_start_gate',
        unit_index: unitIndex,
        previous_unit: (prev.verify_state&&prev.verify_state.unit_id)||'hidden_continuous_unit_72',
        proposal_only: true,
        free_only: true,
        write_authority: 'none',
        merge_authority: 'none',
        paid_api_allowed: false,
        paid_fallback_allowed: false,
        spending_ceiling_usd: 0,
        verification_required_before_continue: true,
        compiled_at: now()
      },
      verify_state: {
        type: 'PMP_CONTINUOUS_RUN_VERIFIED_UNIT_V1',
        verified: true,
        continuation_allowed: false,
        manual_start_required: true,
        resume_boundary: 'packet_1_5_manual_start_gate',
        unit_id: 'packet_1_5_manual_start_gate',
        unit_index: unitIndex,
        proposal_only: true,
        free_only: true,
        locks_held: true,
        non_free_fallback_allowed: false,
        verified_at: now()
      },
      active_state: {
        type: 'PMP_CONTINUOUS_RUN_ACTIVE_V1',
        status: 'packet_1_5_manual_start_gate_ready',
        execution_started: false,
        start_requested: false,
        resume_boundary: 'packet_1_5_manual_start_gate',
        visible_boundary_policy: 'shown_in_dashboard',
        active_unit: 'packet_1_5_start_gate',
        mode: 'manual_start_required_before_packet_1_5',
        free_only: true,
        write_authority: 'none',
        merge_authority: 'none',
        paid_fallback_allowed: false,
        prepared_at: now()
      },
      recovery_fallback_if_next_action_fails: FALLBACK_ROUTE,
      non_regression: 'preserve Route Guardian v18/v8, Save Current restore points, readable Move Ledger, raw JSON report, cycle reset state, compile/verify gates, guardian dormant real-app safety, and label-change diagnostic.'
    };
  }
  function patchDraft(old){
    const prev = old && typeof old==='object' ? old : {};
    return {
      ...prev,
      type: DRAFT_TYPE,
      schema_id: 'pmp.automated-plan.continuous-run-mission.v1',
      schema_version: '1.1.0',
      status: 'packet_1_5_manual_start_gate_ready',
      dashboard_label: 'Continuous Run Dashboard',
      mission_mode: 'manual_start_then_automatic_verified_pass_to_pass',
      standing_mission: true,
      continuous_pass_to_pass_mission: true,
      auto_continue_after_verified_pass_after_enablement: true,
      requires_future_start_enablement: true,
      execution_enabled: false,
      start_requested: false,
      compiled_inside_app: true,
      compiled_at: now(),
      mission_text: MISSION_TEXT,
      resume_from: 'packet_1_5',
      queue: [
        {unit_id:'packet_1_5_intake',objective:'Accept Packet 1.5 input only after the manual start gate.'},
        {unit_id:'packet_1_5_split',objective:'Split Packet 1.5 into safe one-unit steps.'},
        {unit_id:'packet_1_5_one_step_run',objective:'Run one unit at a time using only free path and proposal-only authority.'},
        {unit_id:'packet_1_5_verify',objective:'Verify each unit before continuing.'},
        {unit_id:'packet_1_5_continue_gate',objective:'Continue only after GOOD verification and no WATCH/BLOCKED state.'},
        {unit_id:'packet_1_5_stop_gate_watch',objective:'Stop on paid path, credential request, write/merge approval, unclear instruction, failed verification, checkpoint mismatch, WATCH, BLOCKED, or manual stop.'},
        {unit_id:'packet_1_5_recovery_checkpoint',objective:'Keep a temporary recovery checkpoint so an interrupted run can resume safely.'}
      ],
      hard_stop_gates: [
        'execution_disabled','manual_start_not_pressed','paid_api_detected','paid_fallback_detected','spending_ceiling_above_zero','unsafe_write_authority','merge_authority_detected','credential_request_detected','unclear_user_instruction','authoritative_main_changed','checkpoint_mismatch','deterministic_verification_failed','independent_rebuild_mismatch','watch_state_detected','blocked_state_detected','manual_stop_requested'
      ],
      authority: {
        model_output_authority:'proposal_only',
        write_authority:'none',
        merge_authority:'none',
        paid_api_allowed:false,
        paid_fallback_allowed:false,
        spending_ceiling_usd:0
      },
      engine_status: 'packet_1_5_ready_manual_start_locked',
      storage_mode: 'temporary_recovery',
      stored_at: now(),
      recovery_expires_at: plusDays(7),
      keep_status: 'prepared_not_started',
      single_active_slot: true
    };
  }
  function deepDoc(){
    try{
      let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);
      for(let i=0;i<10;i++){let n=d&&d.getElementById&&d.getElementById('app');if(!n)break;w=n.contentWindow;d=n.contentDocument||w.document}
      return d||document;
    }catch(_){return document}
  }
  function patchMissionField(){
    const d=deepDoc();
    if(!d)return false;
    const areas=Array.from(d.querySelectorAll('textarea'));
    const mission=areas.find(a=>/continuous\s+run\s+mission/i.test(a.placeholder||'')||/continuous\s+run\s+mission/i.test((a.previousElementSibling&&a.previousElementSibling.textContent)||''));
    if(mission && !String(mission.value||'').trim()){
      mission.value = MISSION_TEXT;
      mission.dispatchEvent(new Event('input',{bubbles:true}));
      mission.dispatchEvent(new Event('change',{bubbles:true}));
      return true;
    }
    return false;
  }
  function run(){
    const state = patchState(inheritedState());
    const draft = patchDraft(inheritedDraft());
    const stateKeys = uniq([...findKeysByType(STATE_TYPE),...STATE_KEYS]);
    const draftKeys = uniq([...findKeysByType(DRAFT_TYPE),...DRAFT_KEYS]);
    stateKeys.forEach(k=>write(k,state));
    draftKeys.forEach(k=>write(k,draft));
    const fieldPatched = patchMissionField();
    const proof = {
      type: 'PMP_CONTINUOUS_RUN_PACKET_1_5_GATE_PROOF_V1',
      version: VERSION,
      at: now(),
      current_app_route: CURRENT_ROUTE,
      fallback: FALLBACK_ROUTE,
      state_keys_written: stateKeys,
      draft_keys_written: draftKeys,
      packet_1_5_gate: state.packet_1_5_gate,
      blocked_state: state.blocked_state,
      mission_present: true,
      mission_field_patched: fieldPatched,
      execution_enabled: false,
      start_requested: false,
      write_authority: 'none',
      merge_authority: 'none',
      paid_api_allowed: false,
      safe_claim: 'Existing Continuous Run state is synced to current v16 and Packet 1.5 is prepared behind a manual start gate only.',
      do_not_claim: 'Does not start Packet 1.5, does not write or merge GitHub changes, does not mutate the real app automatically, and does not approve paid paths.'
    };
    write(PROOF_KEY, proof);
    window.PMPContinuousRunSyncPacket15V1 = { version: VERSION, proof, rerun: run, mission: MISSION_TEXT };
    return proof;
  }
  setTimeout(run,250);
  setTimeout(run,1200);
  setTimeout(run,2800);
})();
