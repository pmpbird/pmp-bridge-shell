(()=>{
  if(window.PMPAutomatedPlanInlineRoomV1)return;
  window.PMPAutomatedPlanInlineRoomV1=true;
  const SCREEN_ID='automatedPlanInlineRoomV1';
  const STATE_URL='automation/state/active-plan.json';
  const CONTROLLER_URL='automation/state/controller-status.json';
  function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function textOf(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
  async function readJson(path){let r=await fetch(path+'?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(path+' '+r.status);return r.json()}
  async function readOptional(path){try{return await readJson(path)}catch(e){return null}}
  function yesNo(v){return v?'yes':'no'}
  function back(w,d){try{if(typeof w.go==='function'){w.go('control');return false}}catch(e){}try{Array.from(d.querySelectorAll('.screen')).forEach(s=>s.classList.remove('on'));d.getElementById('control').classList.add('on');d.location.hash='#control'}catch(e){}return false}
  function statusLine(state,controller){let next=controller&&controller.next_unit||state&&state.checkpoint&&state.checkpoint.next_unit||'pass_003';if(controller&&String(controller.controller_status||'').indexOf('execution_locked')>=0)return'Controller ready — '+next+' has not started';if(state&&state.status==='setup')return'Setup — execution is safely locked';return'Plan state loaded'}
  function detailRows(state,controller){let cp=state&&state.checkpoint||{};let ex=state&&state.execution||{};return[
    ['Internal plan',state&&state.active_plan_id||'none'],['Controller',controller&&controller.controller_status||'not loaded'],['Last completed',cp.last_completed_boundary||'none'],['Next unit',controller&&controller.next_unit||cp.next_unit||'none'],['Next unit started',controller?yesNo(controller.next_unit_started):'unknown'],['Execution enabled',state&&state.execution_enabled?'yes':'no'],['Write authority',ex.write_authority||'none'],['Merge authority',ex.merge_authority||'none'],['Requested action',ex.requested_action||'none']
  ]}
  function row(d,k,v){let r=d.createElement('div');r.style.cssText='display:grid;grid-template-columns:minmax(110px,.7fr) 1.3fr;gap:8px;padding:8px 0;border-bottom:1px solid var(--line,#07101c);font-weight:850;overflow-wrap:anywhere';let a=d.createElement('div');a.textContent=k;let b=d.createElement('div');b.textContent=v;r.append(a,b);return r}
  async function openInline(w,d){
    let state=null,controller=null;
    try{state=await readJson(STATE_URL);controller=await readOptional(CONTROLLER_URL)}catch(e){state={status:'error',execution_enabled:false,checkpoint:{next_unit:'pass_003'},execution:{requested_action:'none',write_authority:'none',merge_authority:'none'}}}
    let old=d.getElementById(SCREEN_ID);if(old)old.remove();
    let wrap=d.querySelector('.wrap')||d.body;
    let s=d.createElement('section');s.id=SCREEN_ID;s.className='screen on';
    s.innerHTML='<div class="card"><h1>Automated Plan</h1><p class="sub" id="pmpApInlineStatus"></p><button class="big" data-pmp-ap-back="1"><span class="icon">←</span><span>Back to Control Room<small>return without changing plan state</small></span><span class="chev">›</span></button><div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 0"><button class="mini" data-pmp-ap-refresh="1" style="width:100%;margin:0;min-width:0">Refresh</button><button class="mini" data-pmp-ap-details="1" style="width:100%;margin:0;min-width:0">Details</button></div><div class="note" id="pmpApInlineNote">Controller hardening is installed. Hosted execution remains blocked until the account-level paid-usage setting is verified. Pass 003 has not started.</div><div class="panel hidden" id="pmpApInlineDetails" style="margin-top:10px"></div></div>';
    wrap.appendChild(s);
    Array.from(d.querySelectorAll('.screen')).forEach(x=>{if(x!==s)x.classList.remove('on')});
    d.location.hash='#automated-plan';
    d.getElementById('pmpApInlineStatus').textContent=statusLine(state,controller);
    let details=d.getElementById('pmpApInlineDetails');detailRows(state,controller).forEach(x=>details.appendChild(row(d,x[0],x[1])));
    s.querySelector('[data-pmp-ap-back]').onclick=e=>{e.preventDefault();return back(w,d)};
    s.querySelector('[data-pmp-ap-details]').onclick=e=>{e.preventDefault();details.classList.toggle('hidden');return false};
    s.querySelector('[data-pmp-ap-refresh]').onclick=e=>{e.preventDefault();return openInline(w,d)};
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
