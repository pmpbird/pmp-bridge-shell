(function(){
'use strict';
if(window.PMPAutomatedPlanRoomV1)return;
const MAIN_LABEL='Automated Plan';
const STATE_URL='automation/state/active-plan.json';
const POLICY_URL='automation/engine/v1/engine-policy.json';
const CONTROLLER_STATUS_URL='automation/state/controller-status.json';
let cachedState=null,cachedPolicy=null,cachedController=null,cachedRuntime=null;
function textOf(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(function(frame){try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
async function readJson(path){let join=path.indexOf('?')>=0?'&':'?';let r=await fetch(path+join+'fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(path+' status '+r.status);return r.json()}
async function readOptional(path){if(!path)return null;try{return await readJson(path)}catch(e){return null}}
async function refreshData(){let values=await Promise.all([readJson(STATE_URL),readJson(POLICY_URL),readOptional(CONTROLLER_STATUS_URL)]);cachedState=values[0];cachedPolicy=values[1];cachedController=values[2];let runtimeUrl=cachedController&&cachedController.runtime_status_url;cachedRuntime=await readOptional(runtimeUrl);return[cachedState,cachedPolicy,cachedController,cachedRuntime]}
function genericStatus(state){let s=String(state&&state.status||'idle').toLowerCase();if(s==='running')return'Running';if(s==='paused')return'Paused';if(s==='stopped')return'Stopped';if(s==='complete')return'Complete';if(s==='setup')return'Setup';if(s==='ready')return'Ready';return'Idle'}
function statusLine(state){let s=genericStatus(state);if(s==='Setup')return'Setup — execution is safely locked';if(s==='Paused')return'Paused — ready to continue';if(s==='Running')return'Running — verified work in progress';if(s==='Stopped')return'Stopped — details contain the exact reason';if(s==='Complete')return'Complete — final receipt preserved';if(s==='Ready')return'Ready — waiting for the next verified event';return'No active automated work'}
function controllerLine(state,controller,runtime){let live=runtime||controller||{};let next=live&&live.checkpoint&&live.checkpoint.next_unit||live.next_unit||state&&state.checkpoint&&state.checkpoint.next_unit||'next unit';if(runtime){let s=String(runtime.status||'').replace(/_/g,' ');if(s==='paused')return'Paused safely — resume remains at '+next;if(s==='ready')return'Controller ready — next verified unit is '+next;if(s==='running')return'Running one verified unit: '+next;if(s==='complete')return'Automated plan complete';return'Controller status: '+s}if(controller&&String(controller.controller_status||'').indexOf('execution_locked')>=0)return'Controller ready — '+next+' has not started';return statusLine(state)}
function css(doc){let old=doc.getElementById('pmp-automated-plan-room-v1-style');if(old)return;let st=doc.createElement('style');st.id='pmp-automated-plan-room-v1-style';st.textContent=`
#pmpAutomatedPlanOverlayV1{position:fixed;inset:0;z-index:999998;background:var(--floor,var(--background,#f3ded4));overflow:auto;color:var(--text,#07101c)}
#pmpAutomatedPlanOverlayV1 .pmp-ap-wrap{max-width:820px;margin:auto;padding:calc(38px + env(safe-area-inset-top)) 14px calc(38px + env(safe-area-inset-bottom));min-height:100vh;background:var(--floor,var(--background,#f3ded4))}
#pmpAutomatedPlanOverlayV1 .pmp-ap-card{background:var(--card,#fff);border:var(--borderWidth,2px) solid var(--line,#07101c);border-radius:28px;padding:18px;margin:0 0 16px;box-shadow:var(--cardShadow,var(--shadow,0 12px 28px #0002))}
#pmpAutomatedPlanOverlayV1 .pmp-ap-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#pmpAutomatedPlanOverlayV1 .pmp-ap-details{margin-top:10px}
#pmpAutomatedPlanOverlayV1 .pmp-ap-kv{display:grid;grid-template-columns:minmax(110px,.7fr) 1.3fr;gap:8px;padding:8px 0;border-bottom:1px solid var(--line,#07101c);font-weight:850;overflow-wrap:anywhere}
#pmpAutomatedPlanOverlayV1 .pmp-ap-kv:last-child{border-bottom:0}
#pmpAutomatedPlanEntryV1 .pmp-ap-dot{width:12px;height:12px;border-radius:50%;background:var(--a,var(--accent,#acd1fb))}
#pmpAutomatedPlanEntryV1 .pmp-ap-entry-text{display:grid;gap:3px}
#pmpAutomatedPlanEntryV1 .pmp-ap-entry-title{font-weight:950;font-size:18px;line-height:1.05}
#pmpAutomatedPlanEntryV1 .pmp-ap-entry-status{font-size:13px;font-weight:800;opacity:.96}
@media(max-width:520px){#pmpAutomatedPlanOverlayV1 .pmp-ap-grid{grid-template-columns:1fr}#pmpAutomatedPlanOverlayV1 .pmp-ap-kv{grid-template-columns:1fr}}
`;doc.head.appendChild(st)}
function closeRoom(doc){let o=doc.getElementById('pmpAutomatedPlanOverlayV1');if(o)o.remove();try{let w=doc.defaultView;if(w&&typeof w.go==='function')w.go('control');else w.location.hash='#control'}catch(e){}return false}
function kv(doc,key,value){let row=doc.createElement('div');row.className='pmp-ap-kv';let a=doc.createElement('div');a.textContent=key;let b=doc.createElement('div');b.textContent=value==null?'':String(value);row.append(a,b);return row}
function yesNo(value){return value?'yes':'no'}
function shortSha(value){value=String(value||'');return value.length===40?value.slice(0,12)+'…':value||'none'}
function effectiveRuntime(state,controller,runtime){if(runtime&&runtime.plan_id===state.active_plan_id)return runtime;return null}
function costAssurance(controller,runtime){let status=runtime&&runtime.billing_gate&&runtime.billing_gate.status||controller&&controller.zero_cost_assurance||'unverified';return status==='verified'?'verified — account paid usage disabled':'unverified — hosted execution blocked'}
function detailValue(state,policy,controller,runtime){let live=effectiveRuntime(state,controller,runtime);let checkpoint=live&&live.checkpoint||state&&state.checkpoint||{};let pause=live&&live.pause||{};return{
'Internal plan':state&&state.active_plan_id||'none',
'Controller':controller&&controller.controller_status||'not loaded',
'Work status':live&&live.status||genericStatus(state),
'Last completed':checkpoint.last_completed_boundary||'none',
'Next unit':checkpoint.next_unit||controller&&controller.next_unit||'none',
'Next unit started':live?yesNo(live.active_request):controller?yesNo(controller.next_unit_started):'unknown',
'Backend':live&&live.selected_backend||state&&state.execution&&state.execution.selected_backend||'none',
'First run supervised':controller?yesNo(controller.first_real_run_requires_supervision):'unknown',
'One unit at a time':controller?yesNo(controller.one_work_unit_at_a_time):'unknown',
'Automatic resume':controller?yesNo(controller.automatic_resume_supported):'unknown',
'Resume from':pause.same_unit_preserved&&checkpoint.next_unit||controller&&controller.resume_from||checkpoint.next_unit||'none',
'Pause reason':pause.reason||controller&&controller.pause_reason||state&&state.execution&&state.execution.stop_reason||'none',
'Last verified main':shortSha(live&&live.pinned_main_sha||controller&&controller.last_verified_main_before_build),
'Model write authority':controller&&controller.model_write_authority||state&&state.execution&&state.execution.write_authority||'none',
'Model merge authority':controller&&controller.model_merge_authority||state&&state.execution&&state.execution.merge_authority||'none',
'Zero-cost assurance':costAssurance(controller,live),
'Verification sandbox':controller&&controller.verification_sandbox||'not verified',
'Checkpoint persistence':controller&&controller.persistence_checkpoint_mode||'not verified',
'Execution enabled':state&&state.execution_enabled?'yes':'no'
}}
function renderRoom(doc){css(doc);let old=doc.getElementById('pmpAutomatedPlanOverlayV1');if(old)old.remove();let overlay=doc.createElement('div');overlay.id='pmpAutomatedPlanOverlayV1';let wrap=doc.createElement('div');wrap.className='pmp-ap-wrap';let card=doc.createElement('section');card.className='pmp-ap-card card';let title=doc.createElement('h1');title.textContent=MAIN_LABEL;let sub=doc.createElement('p');sub.className='sub';sub.id='pmpAutomatedPlanRoomStatusV1';sub.textContent=controllerLine(cachedState,cachedController,cachedRuntime);let back=doc.createElement('button');back.className='big';back.innerHTML='<span class="icon">←</span><span>Back to Control Room<small>return without changing plan state</small></span><span class="chev">›</span>';back.onclick=function(e){if(e)e.preventDefault();return closeRoom(doc)};let controls=doc.createElement('div');controls.className='pmp-ap-grid';let refresh=doc.createElement('button');refresh.className='mini';refresh.textContent='Refresh';let detailsButton=doc.createElement('button');detailsButton.className='mini';detailsButton.textContent='Details';let note=doc.createElement('div');note.className='note';note.id='pmpAutomatedPlanRoomNoteV1';note.textContent=cachedController&&cachedController.safe_message||'The plan identity and checkpoint are stored internally. The main Control Room button stays universal.';let details=doc.createElement('div');details.className='panel pmp-ap-details hidden';details.id='pmpAutomatedPlanDetailsV1';let values=detailValue(cachedState,cachedPolicy,cachedController,cachedRuntime);Object.keys(values).forEach(k=>details.appendChild(kv(doc,k,values[k])));detailsButton.onclick=function(){details.classList.toggle('hidden');return false};refresh.onclick=async function(){refresh.disabled=true;try{await refreshData();renderRoom(doc)}catch(e){note.textContent='Unable to refresh plan state. No state was changed. '+String(e&&e.message||e)}finally{refresh.disabled=false}};controls.append(refresh,detailsButton);card.append(title,sub,back,controls,note,details);wrap.appendChild(card);overlay.appendChild(wrap);doc.body.appendChild(overlay);return false}
function openRoom(doc){renderRoom(doc);refreshData().then(function(){if(doc.getElementById('pmpAutomatedPlanOverlayV1'))renderRoom(doc)}).catch(function(e){let n=doc.getElementById('pmpAutomatedPlanRoomNoteV1');if(n)n.textContent='Plan state could not be loaded. No state was changed. '+String(e&&e.message||e)});return false}
function mount(doc){try{if(!doc||!doc.body||!doc.head)return false;let control=doc.getElementById('control');if(!control)return false;css(doc);let existing=doc.getElementById('pmpAutomatedPlanEntryV1');if(existing){let s=existing.querySelector('.pmp-ap-entry-status');if(s)s.textContent=statusLine(cachedState);return true}let button=doc.createElement('button');button.id='pmpAutomatedPlanEntryV1';button.className='big';button.innerHTML='<span class="icon">◆</span><span class="pmp-ap-entry-text"><span class="pmp-ap-entry-title"></span><span class="pmp-ap-entry-status"></span></span><span class="chev">›</span>';button.querySelector('.pmp-ap-entry-title').textContent=MAIN_LABEL;button.querySelector('.pmp-ap-entry-status').textContent=statusLine(cachedState);button.onclick=function(e){if(e)e.preventDefault();return openRoom(doc)};let card=control.querySelector('.card')||control;let colorPanel=doc.getElementById('colorPanel');if(colorPanel&&colorPanel.parentNode===card)card.insertBefore(button,colorPanel);else card.appendChild(button);return true}catch(e){return false}}
function scan(){let count=0;deepDocuments(document).forEach(function(doc){if(mount(doc))count++});return count}
refreshData().catch(function(){}).finally(function(){scan();[100,300,700,1400,2800].forEach(t=>setTimeout(scan,t));setInterval(scan,900)});
window.PMPAutomatedPlanRoomV1={scan:scan,open:function(){let d=deepDocuments(document).find(x=>x.getElementById&&x.getElementById('control'));return d&&openRoom(d)},refresh:refreshData};
})();
