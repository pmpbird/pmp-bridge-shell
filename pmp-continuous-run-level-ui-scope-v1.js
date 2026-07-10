(()=>{
'use strict';
const V='1.0.19-pass9-level3plus-always-present-readiness-state-20260710A';
const RECEIPT='pmp_continuous_run_level_ui_scope_v1_receipt';
const LEVELS=[
 ['3','[data-source-text-reader-level3]','Level 3 — Source Text Reader'],
 ['4','[data-source-reference-gate-level4]','Level 4 — Source Reference Gate'],
 ['4B','[data-source-reference-gate-level4b]','Level 4B — Source Reference Gate B'],
 ['5','[data-level5-source-gated-runner]','Level 5 — Source-Gated Runner'],
 ['6','[data-level6-audit-receipt-lock]','Level 6 — Audit Receipt Lock'],
 ['7','[data-level7-no-bypass-enforcement]','Level 7 — No-Bypass Enforcement'],
 ['8','[data-level8-output-gate]','Level 8 — Output Gate'],
 ['9','[data-level9-actual-resident-integration]','Level 9 — Actual Resident Integration'],
 ['10','[data-level10-cert-lock]','Level 10 — Certification Lock'],
 ['11','[data-level11-startup-guard]','Level 11 — Startup Guard'],
 ['12','[data-level12-startup-enforcement]','Level 12 — Startup Enforcement'],
 ['13','[data-level13-failure-test]','Level 13 — Failure Test'],
 ['14','[data-level14-recovery-proof]','Level 14 — Recovery Proof'],
 ['15','[data-level15-source-invalidation]','Level 15 — Source Invalidation'],
 ['16','[data-level16-source-bound]','Level 16 — Source Bound'],
 ['17','[data-level17-source-mismatch]','Level 17 — Source Mismatch'],
 ['18','[data-level18-recert-gate]','Level 18 — Recertification Gate'],
 ['19','[data-level19-recovery-proof]','Level 19 — Recovery Proof'],
 ['20','[data-level20-summary-lock]','Level 20 — Summary Lock'],
 ['21','[data-level21-one-tap-retest]','Level 21 — One-Tap Retest'],
 ['22','[data-level22-export-receipt]','Level 22 — Export Receipt'],
 ['23','[data-level23-integrity-check]','Level 23 — Integrity Check'],
 ['24','[data-level24-tamper-test]','Level 24 — Tamper Test'],
 ['25','[data-level25-receipt-bundle]','Level 25 — Receipt Bundle'],
 ['26','[data-level26-packet-integrity]','Level 26 — Packet Integrity'],
 ['27','[data-level27-tampered-packet]','Level 27 — Tampered Packet'],
 ['28','[data-level28-final-export]','Level 28 — Final Export'],
 ['29','[data-level29-cold-start]','Level 29 — Cold Start'],
 ['30','[data-level30-final-seal]','Level 30 — Final Seal'],
 ['30B','[data-resident-l30b-auto-gate]','Level 30B — Resident Startup Gate / Use Mode / Request Intake']
].map(x=>({id:x[0],selector:x[1],title:x[2]}));
const RESIDENT_CHILDREN=['[data-resident-use-mode-v1]','[data-request-intake-v1]'];
const WATCHED=new WeakSet();
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function S(x,k,v){try{x.style.setProperty(k,v,'important')}catch(e){}}
function R(x,k){try{x.style.removeProperty(k)}catch(e){}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function bank(d){return d&&d.getElementById&&d.getElementById('bank')}
function detailTitle(b){let x=b&&b.querySelector('[data-bank-detail-title]');return clean(x&&x.textContent||'')}
function detailOpen(b){let x=b&&b.querySelector('[data-bank-detail-wrap]');return !!(x&&!x.classList.contains('hidden'))}
function runSlot(b){return b&&b.querySelector('[data-continuous-run-owner-slot-v1],[data-run-bank-tools]')}
function isCR(d){let b=bank(d);if(!b||!detailOpen(b))return false;let run=runSlot(b);if(!run||run.classList.contains('hidden'))return false;return /Continuous Run Bank/i.test(detailTitle(b))}
function properStack(x){return !!(x&&x.closest('[data-bank-detail-wrap]')&&x.closest('[data-run-bank-tools]')&&x.closest('[data-cr-level-stack]'))}
function hideLoose(x){if(!x||properStack(x))return;try{x.setAttribute('data-cr-level-loose-contained','1')}catch(e){}S(x,'display','none');S(x,'visibility','hidden');S(x,'pointer-events','none')}
function showStacked(x){if(!x)return;try{x.removeAttribute('data-cr-level-loose-contained')}catch(e){}R(x,'display');R(x,'visibility');R(x,'pointer-events')}
function stackReady(b){let run=runSlot(b);return !!(b&&detailOpen(b)&&run&&!run.classList.contains('hidden')&&run.querySelector('[data-bank-screen-owner-v1]')&&run.querySelector('[data-bso-level1]')&&run.querySelector('[data-bso-level2]'))}
function readiness(b){return stackReady(b)?{state:'LOCKED_WAITING',label:'Locked / waiting',note:'Visible in order. Waiting for Level 1 and Level 2 proof before runnable/trusted use.'}:{state:'BLOCKED_OWNER_STACK_INCOMPLETE',label:'Blocked',note:'Visible placeholder. Bank Owner slot, Continuous Run Owner, Level 1, and Level 2 must be present first.'}}
function styleCard(x,meta,ready,placeholder){if(!x)return;try{x.setAttribute('data-cr-level-readiness-state',ready.state);x.setAttribute('data-cr-level-id',meta.id);x.setAttribute('data-cr-level-title',meta.title);if(placeholder)x.setAttribute('data-cr-level-placeholder-v1','1')}catch(e){}S(x,'display','block');S(x,'visibility','visible');S(x,'pointer-events','auto');S(x,'background','rgba(255,255,255,.72)');S(x,'border','3px solid rgba(0,0,0,.22)');S(x,'border-radius','14px');S(x,'margin','0');S(x,'padding','10px');S(x,'box-sizing','border-box');S(x,'max-width','100%');S(x,'overflow','visible');Array.from(x.querySelectorAll('h1,h2,h3,h4,p,.sub,b,strong,button,summary,label')).forEach(e=>{S(e,'white-space','normal');S(e,'overflow','visible');S(e,'text-overflow','clip');S(e,'max-width','100%')});Array.from(x.querySelectorAll('pre,.note,.statusbar')).forEach(e=>{S(e,'white-space','pre-wrap');S(e,'overflow','auto');S(e,'max-width','100%')});let badge=x.querySelector('[data-cr-level-readiness-badge-v1]');if(!badge){badge=x.ownerDocument.createElement('div');badge.setAttribute('data-cr-level-readiness-badge-v1','');x.insertBefore(badge,x.firstChild)}badge.textContent=ready.label;S(badge,'display','inline-block');S(badge,'width','fit-content');S(badge,'margin','0 0 8px 0');S(badge,'padding','6px 10px');S(badge,'border','2px solid rgba(0,0,0,.35)');S(badge,'border-radius','999px');S(badge,'font-weight','950');S(badge,'background','#fff3de')}
function placeholder(d,meta,ready){let x=d.createElement('section');x.setAttribute('data-cr-level-card-v1','');x.setAttribute('data-cr-level-id',meta.id);x.innerHTML='<h3>'+esc(meta.title)+'</h3><p class="sub">'+esc(ready.note)+'</p><pre class="note">Readiness: '+esc(ready.state)+'\nOrder: visible inside Continuous Run Owner stack\nRule: visible does not mean runnable or trusted yet.</pre>';styleCard(x,meta,ready,true);return x}
function firstReal(b,meta){let all=Array.from(b.querySelectorAll(meta.selector));return all.find(x=>!x.hasAttribute('data-cr-level-card-v1'))||null}
function host(d){let b=bank(d);if(!b||!isCR(d))return null;let run=runSlot(b);if(!run)return null;let h=run.querySelector('[data-continuous-run-level-ui-scope-v1]');if(!h){h=d.createElement('div');h.setAttribute('data-continuous-run-level-ui-scope-v1','');h.setAttribute('data-pass9-level3plus-always-present','1');h.innerHTML='<div data-cr-level-head><h2>Continuous Run Levels 3 through 30B</h2><p class="sub">All Level 3+ sections stay visible in order. Readiness state controls whether they are runnable/trusted.</p></div><div data-cr-level-stack></div>';run.appendChild(h)}if(!h.querySelector('[data-cr-level-head]'))h.insertAdjacentHTML('afterbegin','<div data-cr-level-head><h2>Continuous Run Levels 3 through 30B</h2><p class="sub">All Level 3+ sections stay visible in order. Readiness state controls whether they are runnable/trusted.</p></div>');if(!h.querySelector('[data-cr-level-stack]'))h.insertAdjacentHTML('beforeend','<div data-cr-level-stack></div>');let owner=run.querySelector('[data-bank-screen-owner-v1]');if(owner&&h.previousElementSibling!==owner)run.insertBefore(h,owner.nextSibling);S(h,'display','grid');S(h,'gap','12px');S(h,'background','transparent');S(h,'border','0');S(h,'padding','0');S(h,'margin','10px 0');Array.from(h.querySelectorAll('[data-cr-level-head]')).forEach(x=>styleCard(x,{id:'head',title:'Continuous Run Levels 3 through 30B'},readiness(b),false));return h}
function stack(h){let s=h.querySelector('[data-cr-level-stack]');if(!s){s=h.ownerDocument.createElement('div');s.setAttribute('data-cr-level-stack','');h.appendChild(s)}S(s,'display','grid');S(s,'gap','12px');return s}
function keepResidentInside30B(b){let real=b.querySelector('[data-resident-l30b-auto-gate]')||b.querySelector('[data-cr-level-card-v1][data-cr-level-id="30B"]');if(!real)return;RESIDENT_CHILDREN.forEach(sel=>Array.from(b.querySelectorAll(sel)).forEach(x=>{try{if(x!==real&&!real.contains(x))real.appendChild(x);styleCard(x,{id:'30B-child',title:'Resident 30B child'},readiness(b),false)}catch(e){}}))}
function buildOrdered(d,h){let b=bank(d),s=stack(h),ready=readiness(b),created=0,moved=0,contained=0;keepResidentInside30B(b);LEVELS.forEach(meta=>{let real=firstReal(b,meta);let card=s.querySelector('[data-cr-level-card-v1][data-cr-level-id="'+meta.id+'"]');if(real){if(card&&card!==real){card.remove()}if(real.parentElement!==s){s.appendChild(real);moved++}styleCard(real,meta,ready,false);showStacked(real);s.appendChild(real)}else{if(!card){card=placeholder(d,meta,ready);created++}styleCard(card,meta,ready,true);s.appendChild(card)}});LEVELS.forEach(meta=>Array.from(b.querySelectorAll(meta.selector)).forEach(x=>{if(!properStack(x)){hideLoose(x);contained++}}));return{created,moved,contained,readiness:ready.state}}
function watch(d){try{if(!d||!d.body||WATCHED.has(d))return;WATCHED.add(d);let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;setTimeout(()=>{pending=false;try{scanDoc(d)}catch(e){}},0)}).observe(d.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden']})}catch(e){}}
function scanDoc(d){if(!isCR(d))return;let h=host(d);if(!h)return;let result=buildOrdered(d,h);put(RECEIPT,{type:'PMP_CONTINUOUS_RUN_LEVEL_UI_SCOPE_V1',version:V,at:now(),status:'LEVEL3PLUS_ALWAYS_PRESENT_ORDERED_READINESS_STACK',levels_visible:'3_through_30B',readiness_state:result.readiness,created_placeholders:result.created,moved_real_level_nodes:result.moved,contained_loose_level_nodes:result.contained,rule:'Level 3+ must be visible in order inside the Continuous Run Owner stack. Readiness controls runnable/trusted state, not visibility.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',broad_dom_sweep:'not_attempted',visibility_hide_reason:'loose_or_duplicate_only_not_readiness'}})}
function scan(){docs(T().document).forEach(d=>{try{watch(d);scanDoc(d)}catch(e){}})}
window.PMPContinuousRunLevelUIScopeV1={version:V,scan,rule:'Pass 9: Level 3+ always visible in ordered Continuous Run stack; readiness state controls use.'};try{T().PMPContinuousRunLevelUIScopeV1=window.PMPContinuousRunLevelUIScopeV1}catch(e){};
window.addEventListener('load',()=>[0,50,120,250,500,900,1200,2000,3000,5000,8000].forEach(t=>setTimeout(scan,t)));
let fastUntil=Date.now()+12000;let fast=setInterval(()=>{scan();if(Date.now()>fastUntil)clearInterval(fast)},250);
setInterval(scan,1200);scan();
})();