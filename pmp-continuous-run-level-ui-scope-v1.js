(()=>{
'use strict';
const V='1.0.20-pass9-canonical-level-order-denest-20260710A';
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
 ['18','[data-level18-recert-gate]','Level 18 — Re-Certification Gate'],
 ['19','[data-level19-recovery-proof]','Level 19 — Recovery Proof'],
 ['20','[data-level20-summary-lock]','Level 20 — Summary Lock'],
 ['21','[data-level21-one-tap-retest]','Level 21 — One-Tap Re-Test Lock'],
 ['22','[data-level22-export-receipt]','Level 22 — Export Receipt Integrity Check'],
 ['23','[data-level23-integrity-check]','Level 23 — Receipt Bundle Integrity Check'],
 ['24','[data-level24-tamper-test]','Level 24 — Tampered Receipt Rejection Test'],
 ['25','[data-level25-receipt-bundle]','Level 25 — Receipt Bundle'],
 ['26','[data-level26-packet-integrity]','Level 26 — Portable Packet Integrity Check'],
 ['27','[data-level27-tampered-packet]','Level 27 — Tampered Packet Rejection Test'],
 ['28','[data-level28-final-export]','Level 28 — One-Tap Final Export'],
 ['29','[data-level29-cold-start]','Level 29 — Cold-Start Verification Proof'],
 ['30','[data-level30-final-seal]','Level 30 — Final Seal'],
 ['30B','[data-resident-l30b-auto-gate]','Level 30B — Resident Startup Gate / Use Mode / Request Intake']
].map((x,i)=>({id:x[0],selector:x[1],title:x[2],index:i}));
const BY_ID={};LEVELS.forEach(x=>BY_ID[x.id]=x);
const ALL_SELECTORS=LEVELS.map(x=>x.selector).join(',');
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
function title(b){let x=b&&b.querySelector('[data-bank-detail-title]');return clean(x&&x.textContent||'')}
function detailOpen(b){let x=b&&b.querySelector('[data-bank-detail-wrap]');return !!(x&&!x.classList.contains('hidden'))}
function runSlot(b){return b&&b.querySelector('[data-continuous-run-owner-slot-v1],[data-run-bank-tools]')}
function isCR(d){let b=bank(d),run=runSlot(b);return !!(b&&detailOpen(b)&&run&&!run.classList.contains('hidden')&&/Continuous Run Bank/i.test(title(b)))}
function parseLevelText(t){t=clean(t);let m=t.match(/^Level\s+(30B|4B|[3-9]|[12][0-9]|30)\b/i);return m?m[1].toUpperCase():null}
function idBySelector(el){for(const meta of LEVELS){try{if(el.matches&&el.matches(meta.selector))return meta.id}catch(e){}}return null}
function heading(el){try{return el.querySelector(':scope > h1,:scope > h2,:scope > h3')||el.querySelector('h1,h2,h3')}catch(e){return el.querySelector('h1,h2,h3')}}
function levelId(el){return idBySelector(el)||parseLevelText((heading(el)||el).textContent||'')}
function hasDataLevel(el){try{return Array.from(el.attributes||[]).some(a=>/^data-(source-|level|resident-|cr-level)/i.test(a.name))}catch(e){return false}}
function candidateForHeading(h,b){let n=h;while(n&&n!==b&&n.parentElement){if(n.hasAttribute&&n.hasAttribute('data-cr-level-shell-v1'))return null;if(n.matches&&n.matches('section,article,.card'))return n;if(hasDataLevel(n)&&n!==h)return n;n=n.parentElement}return h.parentElement&&h.parentElement!==b?h.parentElement:null}
function properShell(el,id){let sh=el&&el.closest&&el.closest('[data-cr-level-shell-v1]');return !!(sh&&sh.getAttribute('data-cr-level-id')===id&&el.closest('[data-cr-level-content-v1]'))}
function isOwnedByThis(el){return !!(el&&el.closest&&el.closest('[data-continuous-run-level-ui-scope-v1]'))}
function ignore(el){return !el||!el.parentNode||(el.hasAttribute&&el.hasAttribute('data-cr-level-shell-v1'))||(el.hasAttribute&&el.hasAttribute('data-cr-level-content-v1'))||!!(el.closest&&el.closest('[data-cr-level-head]'))}
function styleBase(x){S(x,'background','rgba(255,255,255,.72)');S(x,'border','3px solid rgba(0,0,0,.22)');S(x,'border-radius','14px');S(x,'margin','0');S(x,'padding','10px');S(x,'box-sizing','border-box');S(x,'max-width','100%');S(x,'overflow','visible');Array.from(x.querySelectorAll('h1,h2,h3,h4,p,.sub,b,strong,button,summary,label')).forEach(e=>{S(e,'white-space','normal');S(e,'overflow','visible');S(e,'text-overflow','clip');S(e,'max-width','100%')});Array.from(x.querySelectorAll('pre,.note,.statusbar')).forEach(e=>{S(e,'white-space','pre-wrap');S(e,'overflow','auto');S(e,'max-width','100%')})}
function readiness(b){let run=runSlot(b);let ok=!!(run&&run.querySelector('[data-bank-screen-owner-v1]')&&run.querySelector('[data-bso-level1]')&&run.querySelector('[data-bso-level2]'));return ok?{state:'LOCKED_WAITING_FOR_LEVEL_PROOF',label:'Locked / waiting',note:'Visible in order. Waiting for Level 1 and Level 2 proof before runnable/trusted use.'}:{state:'BLOCKED_OWNER_STACK_INCOMPLETE',label:'Blocked',note:'Visible but not runnable. Bank Owner slot, Continuous Run Owner, Level 1, and Level 2 must exist first.'}}
function ensureHost(d){let b=bank(d),run=runSlot(b);if(!b||!run)return null;let h=run.querySelector('[data-continuous-run-level-ui-scope-v1]');if(!h){h=d.createElement('div');h.setAttribute('data-continuous-run-level-ui-scope-v1','');h.setAttribute('data-pass9-canonical-level-order-v1','');h.innerHTML='<div data-cr-level-head><h2>Continuous Run Levels 3 through 30B</h2><p class="sub">All levels are visible in fixed order. Readiness state controls whether a level is runnable/trusted.</p></div><div data-cr-level-stack></div>';run.appendChild(h)}let owner=run.querySelector('[data-bank-screen-owner-v1]');if(owner&&h.previousElementSibling!==owner)run.insertBefore(h,owner.nextSibling);S(h,'display','grid');S(h,'gap','12px');S(h,'background','transparent');S(h,'border','0');S(h,'padding','0');S(h,'margin','10px 0');let head=h.querySelector('[data-cr-level-head]');if(head)styleBase(head);return h}
function stack(h){let s=h.querySelector('[data-cr-level-stack]');if(!s){s=h.ownerDocument.createElement('div');s.setAttribute('data-cr-level-stack','');h.appendChild(s)}S(s,'display','grid');S(s,'gap','12px');return s}
function ensureShell(d,s,meta,ready){let sh=s.querySelector('[data-cr-level-shell-v1][data-cr-level-id="'+meta.id+'"]');if(!sh){sh=d.createElement('section');sh.setAttribute('data-cr-level-shell-v1','');sh.setAttribute('data-cr-level-id',meta.id);sh.setAttribute('data-cr-level-order',String(meta.index+3));sh.innerHTML='<div data-cr-level-readiness-badge-v1></div><h3>'+esc(meta.title)+'</h3><div data-cr-level-content-v1><p class="sub" data-cr-level-placeholder-text-v1>'+esc(ready.note)+'</p><pre class="note" data-cr-level-placeholder-status-v1>Readiness: '+esc(ready.state)+'\nOrder: visible inside Continuous Run Owner stack\nRule: visible does not mean runnable/trusted yet.</pre></div>';s.appendChild(sh)}s.appendChild(sh);sh.setAttribute('data-cr-level-readiness-state',ready.state);let badge=sh.querySelector('[data-cr-level-readiness-badge-v1]');if(badge)badge.textContent=ready.label;styleBase(sh);if(badge){S(badge,'display','inline-block');S(badge,'width','fit-content');S(badge,'margin','0 0 8px 0');S(badge,'padding','6px 10px');S(badge,'border','2px solid rgba(0,0,0,.35)');S(badge,'border-radius','999px');S(badge,'font-weight','950');S(badge,'background','#fff3de')}return sh}
function collectCandidates(b,h){let out=[];try{Array.from(b.querySelectorAll(ALL_SELECTORS)).forEach(el=>{let id=levelId(el);if(id&&BY_ID[id]&&!ignore(el))out.push({id,el,source:'selector'})})}catch(e){}try{Array.from(b.querySelectorAll('h1,h2,h3')).forEach(x=>{let id=parseLevelText(x.textContent||'');if(!id||!BY_ID[id])return;let el=candidateForHeading(x,b);if(el&&!ignore(el))out.push({id,el,source:'heading'})})}catch(e){}let seen=new Set(),cleaned=[];out.forEach(c=>{if(!c.el||!c.el.parentNode)return;let key=c.id+'::'+Math.random();try{if(!c.el.__pmpCrLevelCandidateId)c.el.__pmpCrLevelCandidateId='c'+Date.now()+Math.random();key=c.id+'::'+c.el.__pmpCrLevelCandidateId}catch(e){}if(seen.has(key))return;seen.add(key);cleaned.push(c)});return cleaned}
function denestAndOrder(d){let b=bank(d),h=ensureHost(d),moved=0,hidden=0,created=0,dupes=0;if(!b||!h)return{moved,hidden,created,dupes};let s=stack(h),ready=readiness(b),cands=collectCandidates(b,h);LEVELS.forEach(meta=>{let sh=ensureShell(d,s,meta,ready),content=sh.querySelector('[data-cr-level-content-v1]');let list=cands.filter(c=>c.id===meta.id&&c.el!==sh&&c.el!==content&&!(c.el.contains&&c.el.contains(sh)));let chosen=list.find(c=>!properShell(c.el,meta.id)&&!isOwnedByThis(c.el))||list.find(c=>properShell(c.el,meta.id))||list.find(c=>!isOwnedByThis(c.el))||null;if(chosen&&content){Array.from(content.querySelectorAll('[data-cr-level-placeholder-text-v1],[data-cr-level-placeholder-status-v1]')).forEach(x=>x.style.display='none');if(chosen.el.parentElement!==content){content.appendChild(chosen.el);moved++}styleBase(chosen.el);S(chosen.el,'display','block');S(chosen.el,'visibility','visible');try{chosen.el.setAttribute('data-cr-level-canonical-member-v1',meta.id)}catch(e){}}else{created++;Array.from(content.querySelectorAll('[data-cr-level-placeholder-text-v1],[data-cr-level-placeholder-status-v1]')).forEach(x=>x.style.display='')}
 list.forEach(c=>{if(chosen&&c.el===chosen.el)return;if(chosen&&c.el.contains&&c.el.contains(chosen.el))return;try{c.el.setAttribute('data-cr-level-duplicate-contained','1');S(c.el,'display','none');S(c.el,'visibility','hidden');S(c.el,'pointer-events','none');dupes++}catch(e){}})});
 // Final loose containment: any level-like card still outside the canonical stack is hidden only as an out-of-stack duplicate.
 collectCandidates(b,h).forEach(c=>{if(c.el.closest&&c.el.closest('[data-cr-level-stack]'))return;try{c.el.setAttribute('data-cr-level-loose-contained','1');S(c.el,'display','none');S(c.el,'visibility','hidden');S(c.el,'pointer-events','none');hidden++}catch(e){}});
 return{moved,hidden,created,dupes,readiness:ready.state}}
function scanDoc(d){if(!isCR(d))return;let r=denestAndOrder(d);put(RECEIPT,{type:'PMP_CONTINUOUS_RUN_LEVEL_UI_SCOPE_V1',version:V,at:now(),status:'CANONICAL_LEVEL3PLUS_ORDER_READY',levels_visible:'3_through_30B',readiness_state:r.readiness,real_level_nodes_moved:r.moved,placeholder_level_cards_active:r.created,loose_level_nodes_contained:r.hidden,duplicate_level_nodes_contained:r.dupes,rule:'Level 3+ is always visible in canonical order inside the Continuous Run Owner stack. Misordered legacy level nodes are de-nested or contained; readiness controls runnable/trusted state, not visibility.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',broad_dom_sweep:'not_attempted',hide_reason:'only loose_or_duplicate_level_nodes_outside_canonical_stack'}})}
function watch(d){try{if(!d||!d.body||WATCHED.has(d))return;WATCHED.add(d);let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;setTimeout(()=>{pending=false;try{scanDoc(d)}catch(e){}},60)}).observe(d.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden']})}catch(e){}}
function scan(){docs(T().document).forEach(d=>{try{watch(d);scanDoc(d)}catch(e){}})}
window.PMPContinuousRunLevelUIScopeV1={version:V,scan,rule:'Pass 9: canonical Level 3+ order; de-nest legacy glitches; visible readiness state.'};try{T().PMPContinuousRunLevelUIScopeV1=window.PMPContinuousRunLevelUIScopeV1}catch(e){};
window.addEventListener('load',()=>[0,50,150,300,700,1200,2200,4000,7000].forEach(t=>setTimeout(scan,t)));
let fastUntil=Date.now()+10000;let fast=setInterval(()=>{scan();if(Date.now()>fastUntil)clearInterval(fast)},350);
setInterval(scan,1000);scan();
})();