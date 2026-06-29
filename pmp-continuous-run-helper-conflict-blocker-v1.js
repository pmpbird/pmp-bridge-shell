(()=>{
'use strict';
const V='1.0.0-helper-not-level';
const HELPERS='[data-resident-use-mode-v1],[data-request-intake-v1]';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function isCR(d){let b=d.getElementById('bank');if(!b)return false;let title=clean((b.querySelector('[data-bank-detail-title]')||{}).textContent||'');return title==='Continuous Run Bank'}
function lane(d,b){let run=b.querySelector('[data-run-bank-tools]')||b;let x=run.querySelector('[data-cr-helper-safe-lane]');if(!x){x=d.createElement('div');x.setAttribute('data-cr-helper-safe-lane','');x.setAttribute('data-bso-stage','');x.style.cssText='display:grid;gap:10px;margin:8px 0 12px;padding:0;border:0;background:transparent';let host=b.querySelector('[data-continuous-run-level-ui-scope-v1]')||run.firstChild;run.insertBefore(x,host||null)}return x}
function scanDoc(d){try{if(!isCR(d))return;let b=d.getElementById('bank'),safe=lane(d,b),moved=0;Array.from(b.querySelectorAll(HELPERS)).forEach(x=>{try{if(x.closest('[data-cr-helper-safe-lane]'))return;if(x.closest('[data-continuous-run-level-ui-scope-v1]')||x.closest('[data-cr-level-stack]')){safe.appendChild(x);moved++}x.setAttribute('data-cr-helper-not-level','1')}catch(e){}});try{localStorage.setItem('pmp_continuous_run_helper_conflict_blocker_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_HELPER_CONFLICT_BLOCKER_V1',version:V,at:new Date().toISOString(),moved,rule:'Resident Use Mode and Request Intake are helper/top-tool panels, not Continuous Run levels.'}))}catch(e){}}catch(e){}}
function scan(){docs(T().document).forEach(scanDoc)}
window.PMPContinuousRunHelperConflictBlockerV1={version:V,scan};
try{new MutationObserver(()=>setTimeout(scan,40)).observe(document.documentElement,{childList:true,subtree:true})}catch(e){}
window.addEventListener('load',()=>[100,300,800,1600,3500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();