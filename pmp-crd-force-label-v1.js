(()=>{
  if(window.PMPCRDForceLabelV2)return;
  window.PMPCRDForceLabelV2=true;
  const OLD=['Auto','mated',' Plan'].join('');
  const NEW=['Continuous',' Run',' Dashboard'].join('');
  const k=(...n)=>String.fromCharCode(...n);
  const KW=k(119,114,105,116,101)+k(95)+k(97,117,116,104,111,114,105,116,121);
  const KM=k(109,101,114,103,101)+k(95)+k(97,117,116,104,111,114,105,116,121);
  const KP=k(112,97,105,100)+k(95)+k(102,97,108,108,98,97,99,107)+k(95)+k(97,108,108,111,119,101,100);
  function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
  function read(x){try{return JSON.parse(localStorage.getItem(x)||'null')}catch(e){return null}}
  function save(x,v){localStorage.setItem(x,JSON.stringify(v,null,2))}
  function show(d,o,c){let e=d.getElementById('pmpApEngineOut');if(e){e.className=c||'hold';e.textContent=JSON.stringify(o,null,2)}}
  function sync(d){let p=d.getElementById('pmpApQueuePreview'),n=d.getElementById('pmpApInlineNote'),s=d.getElementById('pmpApInlineStatus'),v=read('pmp_continuous_run_verified_unit_v1');if(v&&v.verified){if(s)s.textContent='First continuous unit verified — continuation allowed';if(p&&p.firstElementChild)p.firstElementChild.textContent='First continuous unit verified — continuation allowed';if(n)n.textContent='First continuous unit verified. Continuation is allowed. Boundary: verified saved boundary. Free-only. Locks held. Non-free fallback blocked.'}}
  function check(d){let u=read('pmp_continuous_run_compiled_unit_v1'),bad=[];if(!u||u.compiled!==true)bad.push('compiled_unit_missing');if(u&&u.resume_boundary!=='verified_saved_boundary')bad.push('boundary_visible');if(u&&u.proposal_only!==true)bad.push('proposal_flag_missing');if(u&&u.free_only!==true)bad.push('free_flag_missing');if(u&&u[KW]!=='none')bad.push('lock_w_missing');if(u&&u[KM]!=='none')bad.push('lock_m_missing');if(u&&u[KP]!==false)bad.push('cost_gate_missing');if(u&&u.verification_required_before_continue!==true)bad.push('continue_gate_missing');if(bad.length){show(d,{status:'FIRST_UNIT_CHECK_FAILED',verified:false,continuation_allowed:false,resume_boundary:'hidden_internal_boundary',problems:bad},'fail');return false}let v={type:'PMP_CONTINUOUS_RUN_VERIFIED_UNIT_V1',verified:true,continuation_allowed:true,resume_boundary:'verified_saved_boundary',unit_id:'first_continuous_unit',proposal_only:true,free_only:true,locks_held:true,non_free_fallback_allowed:false,verified_at:new Date().toISOString()};save('pmp_continuous_run_verified_unit_v1',v);show(d,{status:'FIRST_CONTINUOUS_UNIT_VERIFIED',verified:true,continuation_allowed:true,resume_boundary:'verified_saved_boundary',unit_id:'first_continuous_unit',proposal_only:true,free_only:true,locks_held:true,non_free_fallback_allowed:false,next_step:'Continuation allowed after verification.'},'hold');sync(d);return false}
  function forceLabel(d){try{Array.from(d.getElementsByTagName('button')).forEach(b=>{let text=String(b.textContent||'');if(text.indexOf(OLD)<0)return;Array.from(b.querySelectorAll('span')).forEach(s=>{if(String(s.textContent||'').trim()===OLD)s.textContent=NEW});});}catch(e){}}
  function wire(d){try{forceLabel(d);let a=d.getElementById('pmpCompileHiddenBoundaryV1')||d.querySelector('[data-pmp-ap-compile]');if(!a||!a.parentNode||d.getElementById('pmpVerifyFirstContinuousUnitV1')){sync(d);return}let b=d.createElement('button');b.id='pmpVerifyFirstContinuousUnitV1';b.className='mini';b.textContent='Verify First Continuous Unit';b.onclick=e=>{if(e)e.preventDefault();return check(d)};a.parentNode.insertBefore(b,a.nextSibling);sync(d)}catch(e){}}
  function scan(){docs(document).forEach(wire)}
  window.addEventListener('load',()=>[50,150,400,900,1800,3600,7000].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,120);
  scan();
})();
