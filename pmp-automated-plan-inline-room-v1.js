(()=>{
  if(window.PMPAutomatedPlanInlineRoomV1)return;
  window.PMPAutomatedPlanInlineRoomV1=true;
  const SCREEN_ID='automatedPlanInlineRoomV1';
  const STATE_URL='automation/state/active-plan.json';
  const CONTROLLER_URL='automation/state/controller-status.json';
  const ENGINE_URL='automation/state/free-in-app-engine-status.json';
  const DRAFT_KEY='pmp_free_in_app_engine_draft_v1';
  const STOP_GATES=['execution_disabled','paid_api_detected','paid_fallback_detected','spending_ceiling_above_zero','unsafe_write_authority','merge_authority_detected','unclear_user_instruction','authoritative_main_changed','checkpoint_mismatch','deterministic_verification_failed','independent_rebuild_mismatch','manual_stop_requested'];
  function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  async function readJson(path){let r=await fetch(path+'?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(path+' '+r.status);return r.json()}
  async function readOptional(path){try{return await readJson(path)}catch(e){return null}}
  function yesNo(v){return v?'yes':'no'}
  function back(w,d){try{if(typeof w.go==='function'){w.go('control');return false}}catch(e){}try{Array.from(d.querySelectorAll('.screen')).forEach(s=>s.classList.remove('on'));d.getElementById('control').classList.add('on');d.location.hash='#control'}catch(e){}return false}
  function loadDraft(){try{return JSON.parse(localStorage.getItem(DRAFT_KEY)||'null')}catch(e){return null}}
  function saveDraft(draft){localStorage.setItem(DRAFT_KEY,JSON.stringify(draft,null,2))}
  function clearDraft(){localStorage.removeItem(DRAFT_KEY)}
  function statusLine(state,controller,engine){let next=controller&&controller.next_unit||state&&state.checkpoint&&state.checkpoint.next_unit||'pass_003';if(engine&&engine.engine_status)return'Free in-app engine built — execution locked — next: '+next;if(controller&&String(controller.controller_status||'').indexOf('execution_locked')>=0)return'Controller ready — '+next+' has not started';if(state&&state.status==='setup')return'Setup — execution is safely locked';return'Plan state loaded'}
  function detailRows(state,controller,engine){let cp=state&&state.checkpoint||{};let ex=state&&state.execution||{};return[
    ['Internal plan',state&&state.active_plan_id||'none'],['Controller',controller&&controller.controller_status||'not loaded'],['Engine',engine&&engine.engine_status||'not loaded'],['Command intake',engine?yesNo(engine.command_intake_inside_app):'unknown'],['Free compiler',engine?yesNo(engine.free_plan_compiler):'unknown'],['Queued runner',engine?yesNo(engine.free_queued_runner):'unknown'],['Last completed',cp.last_completed_boundary||'none'],['Next unit',controller&&controller.next_unit||cp.next_unit||'none'],['Next unit started',controller?yesNo(controller.next_unit_started):'unknown'],['Execution enabled',state&&state.execution_enabled?'yes':'no'],['Write authority',ex.write_authority||'none'],['Merge authority',ex.merge_authority||'none'],['Requested action',ex.requested_action||'none'],['Paid fallback',ex.paid_fallback_allowed?'yes':'no']
  ]}
  function row(d,k,v){let r=d.createElement('div');r.style.cssText='display:grid;grid-template-columns:minmax(120px,.8fr) 1.2fr;gap:8px;padding:8px 0;border-bottom:1px solid var(--line,#07101c);font-weight:850;overflow-wrap:anywhere';let a=d.createElement('div');a.textContent=k;let b=d.createElement('div');b.textContent=String(v);r.append(a,b);return r}
  function out(d,value,state){let el=d.getElementById('pmpApEngineOut');if(!el)return;el.className=state==='fail'?'fail':state==='hold'?'hold':'pass';el.textContent=typeof value==='string'?value:JSON.stringify(value,null,2)}
  function summaryOut(d,draft){
    let el=d.getElementById('pmpApEngineOut');if(!el)return;
    if(!draft){out(d,'No queue draft yet.','pass');return}
    el.className='hold';el.innerHTML='';
    const title=d.createElement('div');title.style.cssText='font-size:20px;font-weight:950;margin-bottom:10px';title.textContent='Queue Draft Built';el.appendChild(title);
    [['Status',draft.status||'draft_not_started'],['Execution',draft.execution_enabled?'enabled':'not started'],['Start requested',draft.start_requested?'yes':'no'],['Resume from',draft.resume_from||'pass_003']].forEach(([k,v])=>el.appendChild(row(d,k,v)));
    const next=d.createElement('div');next.style.cssText='margin-top:12px;font-weight:900';next.textContent='Review the queue. Enablement is a separate future step.';el.appendChild(next);
  }
  function rawOut(d,draft){out(d,draft?{status:'RAW_DRAFT',execution_started:false,draft:draft}:{status:'NO_DRAFT',execution_started:false},draft?'hold':'pass')}
  function compileLocal(d,state,controller,engine){
    const box=d.getElementById('pmpApCommandBox');
    const command=String(box&&box.value||'').trim();
    if(!command){out(d,{status:'STOP',reason:'unclear_user_instruction',message:'Type an instruction first. Execution did not start.'},'fail');return false}
    if(command.length>2000){out(d,{status:'STOP',reason:'unclear_user_instruction',message:'Instruction is too large for the free in-app compiler. Execution did not start.'},'fail');return false}
    if(/\b(paid|billing|api key|merge now|force push|delete repo|secret)\b/i.test(command)){out(d,{status:'STOP',reason:'hard_free_path_stop_gate',message:'Blocked paid/unsafe/secret wording. Execution did not start.'},'fail');return false}
    const cp=state&&state.checkpoint||{};const next=controller&&controller.next_unit||cp.next_unit||'pass_003';
    const draft={type:'PMP_FREE_IN_APP_ENGINE_QUEUE_DRAFT',schema_id:'pmp.automated-plan.free-in-app-queue.v1',schema_version:'1.0.0',status:'draft_not_started',execution_enabled:false,start_requested:false,compiled_inside_app:true,compiled_at:new Date().toISOString(),user_command:command,resume_from:next,queue:[
      {unit_id:'intake_review',objective:'Normalize the user instruction and confirm it is free-path safe.'},
      {unit_id:'source_scope',objective:'Find the smallest relevant app/source scope without changing files.'},
      {unit_id:'compile_units',objective:'Convert the request into executable units with evidence paths and output allowlists.'},
      {unit_id:'queued_execution_ready',objective:'Prepare the queue for the existing verified-unit controller without starting it.'},
      {unit_id:'user_enablement_gate',objective:'Stop until explicit execution enablement and free gates pass.'}
    ],hard_stop_gates:STOP_GATES,authority:{model_output_authority:'proposal_only',write_authority:'none',merge_authority:'none',paid_api_allowed:false,paid_fallback_allowed:false,spending_ceiling_usd:0},engine_status:engine&&engine.engine_status||'built_execution_locked'};
    saveDraft(draft);renderDraft(d,draft);summaryOut(d,draft);return false
  }
  function renderDraft(d,draft){
    const p=d.getElementById('pmpApQueuePreview');if(!p)return;
    if(!draft){p.textContent='No queue draft yet.';return}
    p.innerHTML='';
    const title=d.createElement('div');title.style.fontWeight='950';title.textContent='Queue steps — not started';p.appendChild(title);
    draft.queue.forEach((u,i)=>{let line=d.createElement('div');line.style.cssText='padding:8px 0;border-bottom:1px solid var(--line,#07101c);font-weight:850';line.textContent=(i+1)+'. '+u.unit_id+' — '+u.objective;p.appendChild(line)});
  }
  async function openInline(w,d){
    let state=null,controller=null,engine=null;
    try{state=await readJson(STATE_URL);controller=await readOptional(CONTROLLER_URL);engine=await readOptional(ENGINE_URL)}catch(e){state={status:'error',execution_enabled:false,checkpoint:{next_unit:'pass_003'},execution:{requested_action:'none',write_authority:'none',merge_authority:'none',paid_fallback_allowed:false}}}
    let old=d.getElementById(SCREEN_ID);if(old)old.remove();
    let wrap=d.querySelector('.wrap')||d.body;
    let s=d.createElement('section');s.id=SCREEN_ID;s.className='screen on';
    s.innerHTML='<div class="card"><h1>Automated Plan</h1><p class="sub" id="pmpApInlineStatus"></p><button class="big" data-pmp-ap-back="1"><span class="icon">←</span><span>Back to Control Room<small>return without changing plan state</small></span><span class="chev">›</span></button><div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 0"><button class="mini" data-pmp-ap-refresh="1" style="width:100%;margin:0;min-width:0">Refresh</button><button class="mini" data-pmp-ap-details="1" style="width:100%;margin:0;min-width:0">Details</button></div><div class="note" id="pmpApInlineNote">Free in-app command engine is installed. Execution remains locked. Pass 003 has not started.</div><div class="panel hidden" id="pmpApInlineDetails" style="margin-top:10px"></div></div><div class="card"><h2>Engine Command</h2><p class="sub">Tell the engine what to do. This only builds a free queued plan draft; it does not run it.</p><textarea id="pmpApCommandBox" style="min-height:120px" placeholder="Example: clean up the app quality without changing Automated Plan execution state"></textarea><div class="grid"><button class="mini" data-pmp-ap-compile="1">Build Free Plan Draft</button><button class="mini" data-pmp-ap-preview="1">Preview Queue</button><button class="mini" data-pmp-ap-raw="1">Raw Draft</button><button class="mini" data-pmp-ap-clear="1">Clear Draft</button><button class="mini" data-pmp-ap-gates="1">Show Stop Gates</button></div><div id="pmpApEngineOut" class="pass">Ready. No execution started.</div><div id="pmpApQueuePreview" class="note" style="margin-top:10px">No queue draft yet.</div></div><div class="card"><h2>Hard Free-Path Gates</h2><div class="hold">Free only. No paid API. No paid fallback. $0 ceiling. No write authority. No merge authority. Stop on ambiguity, changed main, checkpoint mismatch, unsafe path, failed verification, or manual stop.</div></div>';
    wrap.appendChild(s);
    Array.from(d.querySelectorAll('.screen')).forEach(x=>{if(x!==s)x.classList.remove('on')});
    d.location.hash='#automated-plan';
    d.getElementById('pmpApInlineStatus').textContent=statusLine(state,controller,engine);
    let details=d.getElementById('pmpApInlineDetails');detailRows(state,controller,engine).forEach(x=>details.appendChild(row(d,x[0],x[1])));
    const draft=loadDraft();renderDraft(d,draft);if(draft)summaryOut(d,draft);
    s.querySelector('[data-pmp-ap-back]').onclick=e=>{e.preventDefault();return back(w,d)};
    s.querySelector('[data-pmp-ap-details]').onclick=e=>{e.preventDefault();details.classList.toggle('hidden');return false};
    s.querySelector('[data-pmp-ap-refresh]').onclick=e=>{e.preventDefault();return openInline(w,d)};
    s.querySelector('[data-pmp-ap-compile]').onclick=e=>{e.preventDefault();return compileLocal(d,state,controller,engine)};
    s.querySelector('[data-pmp-ap-preview]').onclick=e=>{e.preventDefault();let draft=loadDraft();renderDraft(d,draft);summaryOut(d,draft);return false};
    s.querySelector('[data-pmp-ap-raw]').onclick=e=>{e.preventDefault();rawOut(d,loadDraft());return false};
    s.querySelector('[data-pmp-ap-clear]').onclick=e=>{e.preventDefault();clearDraft();renderDraft(d,null);out(d,{status:'DRAFT_CLEARED',execution_started:false},'pass');return false};
    s.querySelector('[data-pmp-ap-gates]').onclick=e=>{e.preventDefault();out(d,{status:'HARD_FREE_PATH_STOP_GATES',execution_started:false,stop_gates:STOP_GATES},'hold');return false};
    return false;
  }
  function bind(doc){
    try{
      let w=doc.defaultView;let b=doc.getElementById('pmpAutomatedPlanEntryV1');
      if(!b||b.dataset.pmpInlineRoomV1)return false;
      b.dataset.pmpInlineRoomV1='1';
      b.onclick=e=>{e.preventDefault();e.stopPropagation();return openInline(w,doc)};
      b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();return openInline(w,doc)},true);
      return true;
    }catch(e){return false}
  }
  function scan(){deepDocuments(document).forEach(bind)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,700);
  scan();
})();
