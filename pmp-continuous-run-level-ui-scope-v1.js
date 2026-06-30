(()=>{
'use strict';
const V='1.0.19-level1plus-containment-guard';
const LEVELS=[
{n:'level1',s:['[data-cr-level1]','[data-cr-level1-source-gate]'],html:'<div class="card" data-cr-level1><h2>Level 1 — Must-Reference Source ZIP Gate / Import</h2><p class="sub">Import the Must-Reference Source ZIP before Level 2 reads it.</p><input type="file" accept=".zip,application/zip" data-cr-source-file><div class="grid"><button class="mini" data-cr-import-source>Import Must-Reference Source ZIP</button></div><pre class="note" data-cr-source-out>Ready.</pre></div>'},
{n:'level2',s:['[data-cr-level2]','[data-source-zip-levels-single]'],html:'<div class="card" data-cr-level2><h2>Level 2 — Source ZIP Reader</h2><p class="sub">Reads the ZIP imported by Level 1. Level 2B extracts PDFs. Level 2C recovers text.</p><div class="grid"><button class="mini" data-cr-run-l2>Read ZIP</button><button class="mini" data-cr-run-l2b>Extract PDFs</button><button class="mini" data-cr-run-l2c>Extract Text</button></div><pre class="note" data-cr-l2-out>Ready.</pre></div>'},
{n:'level3',s:['[data-source-text-reader-level3]']},
{n:'level4',s:['[data-source-reference-gate-level4]']},
{n:'level4b',s:['[data-source-reference-gate-level4b]']},
{n:'level5',s:['[data-level5-source-gated-runner]']},
{n:'level6',s:['[data-level6-audit-receipt-lock]']},
{n:'level7',s:['[data-level7-no-bypass-enforcement]']},
{n:'level8',s:['[data-level8-output-gate]']},
{n:'level9',s:['[data-level9-actual-resident-integration]']},
{n:'level10',s:['[data-level10-cert-lock]']},
{n:'level11',s:['[data-level11-startup-guard]']},
{n:'level12',s:['[data-level12-startup-enforcement]']},
{n:'level13',s:['[data-level13-failure-test]']},
{n:'level14',s:['[data-level14-recovery-proof]']},
{n:'level15',s:['[data-level15-source-invalidation]']},
{n:'level16',s:['[data-level16-source-bound]']},
{n:'level17',s:['[data-level17-source-mismatch]']},
{n:'level18',s:['[data-level18-recert-gate]']},
{n:'level19',s:['[data-level19-recovery-proof]']},
{n:'level20',s:['[data-level20-summary-lock]']},
{n:'level21',s:['[data-level21-one-tap-retest]']},
{n:'level22',s:['[data-level22-export-receipt]']},
{n:'level23',s:['[data-level23-integrity-check]']},
{n:'level24',s:['[data-level24-tamper-test]']},
{n:'level25',s:['[data-level25-receipt-bundle]']},
{n:'level26',s:['[data-level26-packet-integrity]']},
{n:'level27',s:['[data-level27-tampered-packet]']},
{n:'level28',s:['[data-level28-final-export]']},
{n:'level29',s:['[data-level29-cold-start]']},
{n:'level30',s:['[data-level30-final-seal]']},
{n:'level30b',s:['[data-resident-l30b-auto-gate]']}
];
const LEVEL_SELECTORS=LEVELS.flatMap(x=>x.s);
const GUARD_SELECTORS=LEVEL_SELECTORS.concat(['[data-cr-level1-level2-sequence-v1]']);
const RESIDENT_CHILDREN=['[data-resident-use-mode-v1]','[data-request-intake-v1]'];
const WATCHED=new WeakSet();
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentDocument)||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function S(x,k,v){try{x.style.setProperty(k,v,'important')}catch(e){}}
function R(x,k){try{x.style.removeProperty(k)}catch(e){}}
function properStack(x){return !!(x&&x.closest('[data-bank-detail-wrap]')&&x.closest('[data-run-bank-tools]')&&x.closest('[data-cr-level-stack]'))}
function hideLoose(x){if(!x||properStack(x))return;try{x.setAttribute('data-cr-level-containment-hidden','1')}catch(e){}S(x,'display','none');S(x,'visibility','hidden');S(x,'pointer-events','none')}
function showStacked(x){if(!x)return;try{x.removeAttribute('data-cr-level-containment-hidden')}catch(e){}R(x,'display');R(x,'visibility');R(x,'pointer-events')}
function containmentGuard(d){let b=d&&d.getElementById&&d.getElementById('bank');if(!b)return;GUARD_SELECTORS.forEach(sel=>{Array.from(b.querySelectorAll(sel)).forEach(x=>{if(properStack(x))showStacked(x);else hideLoose(x)})})}
function watch(d){try{if(!d||!d.body||WATCHED.has(d))return;WATCHED.add(d);let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;setTimeout(()=>{pending=false;try{containmentGuard(d)}catch(e){}},0)}).observe(d.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden']})}catch(e){}}
function isCR(d){let b=d.getElementById('bank');if(!b)return false;let run=b.querySelector('[data-run-bank-tools]');if(!run)return false;let t=clean((b.querySelector('[data-bank-detail-title],h1,h2')||{}).textContent||'');return !t||/Continuous Run Bank/i.test(t)||!!run.querySelector(LEVEL_SELECTORS.join(','))}
function styleCard(x){S(x,'background','rgba(255,255,255,.72)');S(x,'border','3px solid rgba(0,0,0,.22)');S(x,'border-radius','14px');S(x,'margin','0');S(x,'padding','10px');S(x,'box-sizing','border-box');S(x,'max-width','100%');S(x,'overflow','visible');Array.from(x.querySelectorAll('h1,h2,h3,h4,p,.sub,b,strong,button,summary,label')).forEach(e=>{S(e,'white-space','normal');S(e,'overflow','visible');S(e,'text-overflow','clip');S(e,'max-width','100%')});Array.from(x.querySelectorAll('pre,.note,.statusbar')).forEach(e=>{S(e,'white-space','pre-wrap');S(e,'overflow','auto');S(e,'max-width','100%')})}
function makeEl(d,html){let holder=d.createElement('div');holder.innerHTML=html;return holder.firstElementChild}
function host(d){let b=d.getElementById('bank');if(!b)return null;let run=b.querySelector('[data-run-bank-tools]');if(!run)return null;let h=run.querySelector('[data-continuous-run-level-ui-scope-v1]');if(!h){h=d.createElement('div');h.setAttribute('data-continuous-run-level-ui-scope-v1','');h.setAttribute('data-v2','1');h.innerHTML='<div data-cr-level-head><h2>Continuous Run Levels 1 through 30B</h2><p class="sub">Run in exact order. Level cards stay inside this stack only.</p></div><div data-cr-level-stack></div>';run.appendChild(h)}if(!h.querySelector('[data-cr-level-head]'))h.insertAdjacentHTML('afterbegin','<div data-cr-level-head><h2>Continuous Run Levels 1 through 30B</h2><p class="sub">Run in exact order. Level cards stay inside this stack only.</p></div>');if(!h.querySelector('[data-cr-level-stack]'))h.insertAdjacentHTML('beforeend','<div data-cr-level-stack></div>');let owner=run.querySelector('[data-bank-screen-owner-v1]');if(owner&&h.previousElementSibling!==owner)run.insertBefore(h,owner.nextSibling);S(h,'display','grid');S(h,'gap','12px');S(h,'background','transparent');S(h,'border','0');S(h,'padding','0');S(h,'margin','10px 0');return h}
function stack(h){let s=h.querySelector('[data-cr-level-stack]');if(!s){s=document.createElement('div');s.setAttribute('data-cr-level-stack','');h.appendChild(s)}S(s,'display','grid');S(s,'gap','12px');return s}
function firstIn(b,lvl){for(const sel of lvl.s){let a=Array.from(b.querySelectorAll(sel));let x=a.find(y=>y&&y.closest('[data-run-bank-tools]'))||a[0];if(x)return x}return null}
function keepResidentInside30B(b){let l30b=firstIn(b,LEVELS.find(x=>x.n==='level30b'));if(!l30b)return;RESIDENT_CHILDREN.forEach(sel=>Array.from(b.querySelectorAll(sel)).forEach(x=>{try{if(x!==l30b&&!l30b.contains(x))l30b.appendChild(x);styleCard(x)}catch(e){}}))}
function ensureLevel(d,b,s,lvl){let x=firstIn(b,lvl);if(!x&&lvl.html)x=makeEl(d,lvl.html);if(!x)return null;if(x.parentElement!==s)s.appendChild(x);showStacked(x);styleCard(x);return x}
function orderedLevels(d,b,s){let out=[];LEVELS.forEach(lvl=>{let x=ensureLevel(d,b,s,lvl);if(x&&out.indexOf(x)<0)out.push(x)});return out}
function hideOldSequence(b){Array.from(b.querySelectorAll('[data-cr-level1-level2-sequence-v1]')).forEach(x=>{if(!properStack(x))hideLoose(x)})}
function move(d,h){let b=d.getElementById('bank'),s=stack(h);keepResidentInside30B(b);orderedLevels(d,b,s).forEach(x=>{try{if(x.parentElement!==s)s.appendChild(x);showStacked(x);styleCard(x)}catch(e){}});hideOldSequence(b);Array.from(h.querySelectorAll('[data-cr-level-head]')).forEach(styleCard);containmentGuard(d)}
function scanDoc(d){containmentGuard(d);if(!isCR(d))return;let h=host(d);if(!h)return;move(d,h);try{localStorage.setItem('pmp_continuous_run_level_ui_scope_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_LEVEL_UI_SCOPE_V1',version:V,at:new Date().toISOString(),status:'level1plus_contained_or_stacked',order:'1,2,3,4,4B,5-30,30B',resident_tools:'inside_30B_only',guard:'level1plus_hidden_unless_inside_bank_detail_run_tools_stack'}))}catch(e){}}
function scan(){docs(T().document).forEach(d=>{try{watch(d);scanDoc(d)}catch(e){}})}
window.PMPContinuousRunLevelUIScopeV1={version:V,scan,rule:'exact sequential Continuous Run levels; Level 1+ hidden unless inside Continuous Run level stack'};
window.addEventListener('load',()=>[0,25,50,100,180,300,500,900,1200,2000,3000,5000,8000].forEach(t=>setTimeout(scan,t)));
let fastUntil=Date.now()+12000;let fast=setInterval(()=>{scan();if(Date.now()>fastUntil)clearInterval(fast)},150);
setInterval(scan,1200);scan();
})();