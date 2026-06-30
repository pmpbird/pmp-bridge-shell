(()=>{
'use strict';
const V='1.0.20-cr-bank-ownership-stack-level12';
const ORDER=[
'[data-cr-level1],[data-cr-level1-source-gate]',
'[data-cr-level2],[data-source-zip-levels-single]',
'[data-source-text-reader-level3]',
'[data-source-reference-gate-level4]',
'[data-source-reference-gate-level4b]',
'[data-level5-source-gated-runner]',
'[data-level6-audit-receipt-lock]',
'[data-level7-no-bypass-enforcement]',
'[data-level8-output-gate]',
'[data-level9-actual-resident-integration]',
'[data-level10-cert-lock]',
'[data-level11-startup-guard]',
'[data-level12-startup-enforcement]',
'[data-level13-failure-test]',
'[data-level14-recovery-proof]',
'[data-level15-source-invalidation]',
'[data-level16-source-bound]',
'[data-level17-source-mismatch]',
'[data-level18-recert-gate]',
'[data-level19-recovery-proof]',
'[data-level20-summary-lock]',
'[data-level21-one-tap-retest]',
'[data-level22-export-receipt]',
'[data-level23-integrity-check]',
'[data-level24-tamper-test]',
'[data-level25-receipt-bundle]',
'[data-level26-packet-integrity]',
'[data-level27-tampered-packet]',
'[data-level28-final-export]',
'[data-level29-cold-start]',
'[data-level30-final-seal]',
'[data-resident-l30b-auto-gate]'
];
const GUARDED=ORDER.slice(2);
const LEVEL12=ORDER.slice(0,2).join(',');
const LEGACY_SEQ='[data-cr-level1-level2-sequence-v1]';
const TOOL_BUTTONS='[data-run-bank-save],[data-run-bank-stop],[data-run-bank-resume],[data-run-bank-copy],[data-run-bank-clear]';
const RESIDENT_CHILDREN=['[data-resident-use-mode-v1]','[data-request-intake-v1]'];
const WATCHED=new WeakSet();
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function S(x,k,v){try{x.style.setProperty(k,v,'important')}catch(e){}}
function R(x,k){try{x.style.removeProperty(k)}catch(e){}}
function properStack(x){return !!(x&&x.closest('[data-bank-detail-wrap]')&&x.closest('[data-run-bank-tools]')&&x.closest('[data-cr-level-stack]'))}
function hideLoose(x){if(!x||properStack(x))return;try{x.setAttribute('data-cr-level-containment-hidden','1')}catch(e){}S(x,'display','none');S(x,'visibility','hidden');S(x,'pointer-events','none')}
function showStacked(x){if(!x)return;try{x.removeAttribute('data-cr-level-containment-hidden')}catch(e){}R(x,'display');R(x,'visibility');R(x,'pointer-events')}
function containmentGuard(d){let b=d&&d.getElementById&&d.getElementById('bank');if(!b)return;GUARDED.forEach(sel=>{Array.from(b.querySelectorAll(sel)).forEach(x=>{if(properStack(x))showStacked(x);else hideLoose(x)})})}
function watch(d){try{if(!d||!d.body||WATCHED.has(d))return;WATCHED.add(d);let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;setTimeout(()=>{pending=false;try{scanDoc(d)}catch(e){}},0)}).observe(d.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden']})}catch(e){}}
function detailOpen(b){let w=b&&b.querySelector('[data-bank-detail-wrap]');return !!(w&&!w.classList.contains('hidden'))}
function detailTitle(b){let x=b&&b.querySelector('[data-bank-detail-title]');let t=clean((x||{}).textContent||'');if(t)return t;return clean(((b||document).querySelector('h1,h2')||{}).textContent||'')}
function isCR(d){let b=d.getElementById('bank');if(!b||!detailOpen(b))return false;let run=b.querySelector('[data-run-bank-tools]');if(!run)return false;let t=detailTitle(b);return /Continuous Run Bank/i.test(t)||!!run.querySelector('[data-source-text-reader-level3],[data-level30-final-seal],[data-resident-l30b-auto-gate]')}
function styleCard(x){S(x,'background','rgba(255,255,255,.72)');S(x,'border','3px solid rgba(0,0,0,.22)');S(x,'border-radius','14px');S(x,'margin','0');S(x,'padding','10px');S(x,'box-sizing','border-box');S(x,'max-width','100%');S(x,'overflow','visible');Array.from(x.querySelectorAll('h1,h2,h3,h4,p,.sub,b,strong,button,summary,label')).forEach(e=>{S(e,'white-space','normal');S(e,'overflow','visible');S(e,'text-overflow','clip');S(e,'max-width','100%')});Array.from(x.querySelectorAll('pre,.note,.statusbar')).forEach(e=>{S(e,'white-space','pre-wrap');S(e,'overflow','auto');S(e,'max-width','100%')})}
function stabilizeRunTools(run){if(!run)return;try{run.classList.remove('hidden')}catch(e){}S(run,'display','block');S(run,'visibility','visible');S(run,'opacity','1');S(run,'position','relative');S(run,'left','auto');S(run,'right','auto');S(run,'top','auto');S(run,'bottom','auto');S(run,'transform','none');S(run,'max-width','100%');S(run,'overflow','visible');S(run,'box-sizing','border-box');Array.from(run.querySelectorAll(TOOL_BUTTONS)).forEach(b=>{try{b.classList.remove('hidden')}catch(e){}R(b,'display');R(b,'visibility');R(b,'opacity');S(b,'max-width','100%')})}
function ensureCard(h,sel,html){let x=h.querySelector(sel);if(!x){let holder=h.ownerDocument.createElement('div');holder.innerHTML=html;x=holder.firstElementChild;let s=h.querySelector('[data-cr-level-stack]')||h;h.insertBefore(x,s)}return x}
function host(d){let b=d.getElementById('bank');if(!b)return null;let run=b.querySelector('[data-run-bank-tools]');if(!run)return null;stabilizeRunTools(run);let h=run.querySelector('[data-continuous-run-level-ui-scope-v1]');if(!h){h=d.createElement('div');h.setAttribute('data-continuous-run-level-ui-scope-v1','');h.setAttribute('data-v2','1');h.innerHTML='<div data-cr-level-head><h2>Continuous Run Levels 1 through 30B</h2><p class="sub">Run in exact order. Resident Use Mode and Request Intake stay inside Level 30B.</p></div><div data-cr-level-stack></div>';run.appendChild(h)}
if(!h.querySelector('[data-cr-level-head]'))h.insertAdjacentHTML('afterbegin','<div data-cr-level-head><h2>Continuous Run Levels 1 through 30B</h2><p class="sub">Run in exact order. Resident Use Mode and Request Intake stay inside Level 30B.</p></div>');
if(!h.querySelector('[data-cr-level-stack]'))h.insertAdjacentHTML('beforeend','<div data-cr-level-stack></div>');
if(!b.querySelector(LEVEL12)){ensureCard(h,'[data-cr-level1-source-gate]','<div data-cr-level1-source-gate><h3>Level 1 — Must-Reference Source ZIP Gate / Import</h3><p class="sub">Import the Must-Reference Source ZIP before Level 2 reads it.</p></div>');ensureCard(h,'[data-source-zip-levels-single]','<div data-source-zip-levels-single><h3>Level 2 — Source ZIP Reader</h3><p class="sub">Reads the ZIP imported by Level 1. Level 2B extracts PDFs. Level 2C recovers text.</p></div>')}
let owner=run.querySelector('[data-bank-screen-owner-v1]');if(owner&&h.previousElementSibling!==owner)run.insertBefore(h,owner.nextSibling);S(h,'display','grid');S(h,'gap','12px');S(h,'background','transparent');S(h,'border','0');S(h,'padding','0');S(h,'margin','10px 0');S(h,'max-width','100%');return h}
function stack(h){let s=h.querySelector('[data-cr-level-stack]');if(!s){s=h.ownerDocument.createElement('div');s.setAttribute('data-cr-level-stack','');h.appendChild(s)}S(s,'display','grid');S(s,'gap','12px');S(s,'max-width','100%');S(s,'overflow','visible');return s}
function firstIn(b,sel){let a=Array.from(b.querySelectorAll(sel));return a.find(x=>x&&properStack(x))||a.find(x=>x&&x.closest('[data-run-bank-tools]'))||a[0]||null}
function keepResidentInside30B(b){let l30b=firstIn(b,'[data-resident-l30b-auto-gate]');if(!l30b)return;RESIDENT_CHILDREN.forEach(sel=>Array.from(b.querySelectorAll(sel)).forEach(x=>{try{if(x!==l30b&&!l30b.contains(x))l30b.appendChild(x);styleCard(x)}catch(e){}}))}
function orderedLevels(b){let out=[];ORDER.forEach(sel=>{let x=firstIn(b,sel);if(x&&out.indexOf(x)<0)out.push(x)});return out}
function cleanupLegacy(b){Array.from(b.querySelectorAll(LEGACY_SEQ)).forEach(w=>{try{if(!w.querySelector(LEVEL12)){w.setAttribute('data-cr-level1-level2-sequence-adopted','1');S(w,'display','none');S(w,'visibility','hidden');S(w,'pointer-events','none')}}catch(e){}})}
function move(d,h){let b=d.getElementById('bank'),s=stack(h);stabilizeRunTools(b.querySelector('[data-run-bank-tools]'));keepResidentInside30B(b);orderedLevels(b).forEach(x=>{try{s.appendChild(x);showStacked(x);styleCard(x)}catch(e){}});Array.from(h.querySelectorAll('[data-cr-level-head]')).forEach(styleCard);cleanupLegacy(b);containmentGuard(d)}
function scanDoc(d){containmentGuard(d);if(!isCR(d))return;let h=host(d);if(!h)return;move(d,h);try{localStorage.setItem('pmp_continuous_run_level_ui_scope_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_LEVEL_UI_SCOPE_V1',version:V,at:new Date().toISOString(),status:'continuous_run_bank_owned_stack_created',order:'1,2,3,4,4B,5-30,30B',level12:'adopted_into_data_cr_level_stack',legacy_wrapper:'hidden_only_after_adoption',guard:'level3plus_hidden_unless_inside_bank_detail_run_tools_stack'}))}catch(e){}}
function scan(){docs(T().document).forEach(d=>{try{watch(d);scanDoc(d)}catch(e){}})}
window.PMPContinuousRunLevelUIScopeV1={version:V,scan,rule:'Continuous Run Bank ownership: create data-cr-level-stack, adopt Level 1/2, leave Level 3+ guard unchanged'};
window.addEventListener('load',()=>[0,50,120,250,500,900,1200,2000,3000,5000,8000].forEach(t=>setTimeout(scan,t)));
let fastUntil=Date.now()+12000;let fast=setInterval(()=>{scan();if(Date.now()>fastUntil)clearInterval(fast)},250);
setInterval(scan,1200);scan();
})();