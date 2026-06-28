(()=>{
'use strict';
const V='1.0.0-move-loose-phase-tools';
const RECEIPT='pmp_mold_to_app_flow_owner_v1_receipt';
const FLOW_ID='pmpMoldToAppFlowOwnerV1';
const FLOW_BODY='pmpMoldToAppFlowBodyV1';
const ACTIONS_ID='pmpMoldToAppFlowActionsV1';
const PHASES_ID='pmpMoldToAppFlowPhasesV1';
const ACTION_RE=/^(Source Body Loader|Field Extraction)$/i;
const PHASE_RE=/(Phase\s*1\s*Source\s*Intake|Fail[- ]Closed\s*Simulation|Phase\s*[0-9]+|Phase\s*8A|Hook\s*Validation|Real\s*App\s*Proof|Current[- ]Clean|Freeze|Full[- ]Transfer|Full[- ]History|Raw\s*Old\s*History|History\s*Archive|History\s*Unavailable\s*Boundary)/i;
function T(){try{return top||window}catch(e){return window}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function txt(x){return clean((x&&x.textContent)||x&&x.value||'')}
function firstHeading(el){try{let h=el.querySelector&&el.querySelector('h1,h2,h3');return txt(h)}catch(e){return''}}
function isMoldButton(el){return /Mold[- ]to[- ]App\s+Wiring/i.test(txt(el))}
function isMoveAction(el){return ACTION_RE.test(txt(el))}
function isPhasePanel(el){let h=firstHeading(el),t=txt(el).slice(0,240);return PHASE_RE.test(h)||PHASE_RE.test(t)&&/Run Phase|Copy Phase|Stage Source|Verify Source|Accept Visible Source|No report yet|Read-only simulation/i.test(t)}
function nearestMoveNode(el){if(!el)return null;if(el.id==='pmpPhase1SingleCard')return el;let n=el.closest&&el.closest('#pmpPhase1SingleCard,.panel,section,.card,div');return n||el}
function makeFlow(d){let flow=d.createElement('div');flow.id=FLOW_ID;flow.setAttribute('data-mold-to-app-flow-owner-v1',V);flow.style.cssText='box-sizing:border-box;width:100%;max-width:100%;margin:12px 0;display:grid;gap:10px';flow.innerHTML='<details id="'+FLOW_BODY+'"><summary style="box-sizing:border-box;width:100%;padding:14px;border-radius:18px;border:3px solid #07101c;background:#172234;color:#eef4fb;font-weight:950;text-align:center;font-size:20px">Mold-to-App Wiring Flow</summary><div style="box-sizing:border-box;width:100%;max-width:100%;display:grid;gap:12px;margin-top:10px"><div class="note" style="box-sizing:border-box;max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere">Mold-to-App source, wiring, validation, proof, freeze, and history tools are grouped here. Data and logic stay intact; only the loose hidden-Control surface is moved.</div><div id="'+ACTIONS_ID+'" class="grid" style="box-sizing:border-box;width:100%;max-width:100%;display:grid;grid-template-columns:1fr 1fr;gap:8px"></div><div id="'+PHASES_ID+'" style="box-sizing:border-box;width:100%;max-width:100%;display:grid;gap:12px"></div></div></details>';return flow}
function ensureFlow(d,secret){let flow=d.getElementById(FLOW_ID);let mold=Array.from(secret.querySelectorAll('button,a,[role="button"]')).find(isMoldButton);if(!flow){flow=makeFlow(d);if(mold&&mold.parentNode){let after=mold.nextSibling;mold.parentNode.insertBefore(flow,after)}else secret.insertBefore(flow,secret.firstChild)}if(mold&&mold.getAttribute('data-mold-flow-toggle')!=='1'){mold.setAttribute('data-mold-flow-toggle','1');mold.onclick=e=>{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let det=d.getElementById(FLOW_BODY);if(det)det.open=!det.open;return false}}return flow}
function moveActions(d,secret,flow){let box=d.getElementById(ACTIONS_ID);if(!box)return 0;let moved=0;Array.from(secret.querySelectorAll('button,a,[role="button"]')).forEach(b=>{try{if(!isMoveAction(b))return;if(b.closest('#'+FLOW_ID))return;let node=nearestMoveNode(b);if(!node||node.id===FLOW_ID||node.contains(flow)||node.closest('#'+FLOW_ID))return;node.setAttribute('data-mold-to-app-flow-item','action');box.appendChild(node);moved++}catch(e){}});return moved}
function movePanels(d,secret,flow){let box=d.getElementById(PHASES_ID);if(!box)return 0;let moved=0;let candidates=Array.from(secret.children).concat(Array.from(secret.querySelectorAll('#pmpPhase1SingleCard,.panel,section,.card')));let seen=new Set();candidates.forEach(el=>{try{if(!el||seen.has(el))return;seen.add(el);if(el.id===FLOW_ID||el.closest&&el.closest('#'+FLOW_ID))return;if(isPhasePanel(el)){el.setAttribute('data-mold-to-app-flow-item','phase');box.appendChild(el);moved++}}catch(e){}});return moved}
function receipt(moved){try{if(!moved)return;localStorage.setItem(RECEIPT,JSON.stringify({type:'PMP_MOLD_TO_APP_FLOW_OWNER_V1_RECEIPT',version:V,at:new Date().toISOString(),moved,rule:'Mold-to-App phase/source/proof tools are grouped under Mold-to-App Wiring. Data and logic were not deleted.',safe_claim:'Only the loose hidden-Control surface was moved into one collapsible flow.',do_not_claim:'This does not complete mold wiring, proof, freeze, or source transfer.'}))}catch(e){}}
function scanDoc(d){try{let secret=d.getElementById('secretPanel');if(!secret)return 0;let flow=ensureFlow(d,secret);let moved=0;moved+=moveActions(d,secret,flow);moved+=movePanels(d,secret,flow);receipt(moved);return moved}catch(e){return 0}}
function scan(){let n=0;docs(T().document).forEach(d=>{n+=scanDoc(d)});return n}
window.PMPMoldToAppFlowOwnerV1={version:V,scan};
window.addEventListener('load',()=>[120,350,900,1800,3500,7000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);scan();
})();