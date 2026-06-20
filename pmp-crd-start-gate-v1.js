(()=>{
  if(window.PMPCRDStartGateV1)return;
  window.PMPCRDStartGateV1=true;
  const DRAFT_KEY='pmp_free_in_app_engine_recovery_draft_v1';
  const KEEP_KEY='pmp_free_in_app_engine_kept_draft_v1';
  function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>9)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function read(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
  function output(d,obj,kind){let out=d.getElementById('pmpApEngineOut');if(!out)return;out.className=kind||'hold';out.textContent=JSON.stringify(obj,null,2)}
  function checkDraft(){
    const draft=read(DRAFT_KEY)||read(KEEP_KEY);
    const problems=[];
    if(!draft)problems.push('missing_saved_mission_draft');
    if(draft&&draft.resume_from!=='pass_003')problems.push('resume_boundary_not_pass_003');
    if(draft&&draft.execution_enabled!==false)problems.push('execution_not_locked');
    if(draft&&draft.start_requested!==false)problems.push('start_already_requested');
    const auth=draft&&draft.authority||{};
    if(draft&&auth.write_authority!=='none')problems.push('write_authority_not_locked');
    if(draft&&auth.merge_authority!=='none')problems.push('merge_authority_not_locked');
    if(draft&&auth.paid_api_allowed!==false)problems.push('paid_api_not_blocked');
    if(draft&&auth.paid_fallback_allowed!==false)problems.push('paid_fallback_not_blocked');
    if(draft&&Number(auth.spending_ceiling_usd||0)!==0)problems.push('spending_ceiling_not_zero');
    if(draft&&draft.continuous_pass_to_pass_mission!==true)problems.push('continuous_mission_flag_missing');
    if(draft&&draft.auto_continue_after_verified_pass_after_enablement!==true)problems.push('auto_continue_after_verify_flag_missing');
    return {draft,problems};
  }
  function runGate(d){
    const r=checkDraft();
    if(r.problems.length){output(d,{status:'START_GATE_BLOCKED',execution_started:false,start_requested:false,resume_from:r.draft&&r.draft.resume_from||null,problems:r.problems,message:'Continuous run did not start.'},'fail');return false}
    output(d,{status:'START_GATE_READY_NOT_STARTED',execution_started:false,start_requested:false,resume_from:'pass_003',packet:'Packet 1.5',mode:'automatic_pass_to_pass_after_future_start',free_only:true,write_authority:'none',merge_authority:'none',paid_fallback_allowed:false,next_step:'Approve the final start action to begin pass_003.'},'hold');
    return false;
  }
  function wire(d){
    try{
      const compile=d.querySelector('[data-pmp-ap-compile]');
      if(!compile||d.getElementById('pmpStartContinuousRunGateV1'))return;
      const btn=d.createElement('button');
      btn.id='pmpStartContinuousRunGateV1';
      btn.className='mini';
      btn.textContent='Test Start Continuous Run Gate';
      btn.onclick=e=>{if(e)e.preventDefault();return runGate(d)};
      compile.parentNode.insertBefore(btn,compile.nextSibling);
    }catch(e){}
  }
  function scan(){docs(document).forEach(wire)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,400);
  scan();
})();
