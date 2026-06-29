(()=>{
'use strict';
const V='1.0.5-layout-conflict-detector';
const ACTIVE='pmp_bug_bank_active_bugs_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function load(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function uniq(a){let out=[],seen={};(Array.isArray(a)?a:[]).filter(Boolean).forEach(x=>{let k=norm((x.type||'')+'|'+(x.where||x.where_seen||''));if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function visible(x){try{let cs=(x.ownerDocument.defaultView||window).getComputedStyle(x);let r=x.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0}catch(e){return false}}
function title(d){let b=d.getElementById('bank');return b?clean((b.querySelector('[data-bank-detail-title]')||{}).textContent||''):''}
function row(type,detail){return{type,where:'Continuous Run Bank',where_seen:'Continuous Run Bank',signature:type+'|Continuous Run Bank',detail:detail||{},bug_bank_section:'Active Bugs Found',severity:'high',how_it_happens:'Continuous Run Bank has visible layout ownership conflict.',fix_rule:'Stop DOM movers and let one owner render or place each level/helper surface.',last_seen:new Date().toISOString(),source:'layout-conflict-detector'}}
function scanCR(d,b){let current=[];let helpers=Array.from(b.querySelectorAll('[data-resident-use-mode-v1],[data-request-intake-v1]')).filter(visible);let bad=helpers.filter(x=>x.closest('[data-continuous-run-level-ui-scope-v1]')||x.closest('[data-cr-level-stack]'));let l3=Array.from(b.querySelectorAll('[data-source-text-reader-level3]')).filter(visible);if(helpers.length>2||bad.length||l3.length>1)current.push(row('Continuous Run Layout Ownership Conflict',{helpers:helpers.length,helpers_inside_level_area:bad.length,level3_visible_count:l3.length}));return current}
function scan(){let current=[];docs(T().document).forEach(d=>{let b=d.getElementById('bank');if(!b)return;if(title(d)==='Continuous Run Bank'||/Continuous Run Bank|Level\s+3/i.test(clean(b.textContent).slice(0,3000)))current=current.concat(scanCR(d,b))});let active=uniq(load(ACTIVE,[])).filter(x=>String(x.type)!=='Auto-detected overflow/clipping'&&String(x.type)!=='Continuous Run Layout Ownership Conflict');current.forEach(x=>active.push(x));if(!current.length)active=active.filter(x=>String(x.type)!=='Continuous Run Layout Ownership Conflict');save(ACTIVE,uniq(active).slice(0,40));try{localStorage.setItem('pmp_bug_bank_current_active_cleaner_v1_receipt',JSON.stringify({type:'PMP_BUG_BANK_CURRENT_ACTIVE_CLEANER_V1',version:V,at:new Date().toISOString(),current_observed:current.length}))}catch(e){}}
window.PMPBugBankCurrentActiveCleanerV1={version:V,scan};
try{new MutationObserver(()=>setTimeout(scan,80)).observe(document.documentElement,{childList:true,subtree:true,attributes:true})}catch(e){}
window.addEventListener('load',()=>[100,400,1000,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,800);scan();
})();