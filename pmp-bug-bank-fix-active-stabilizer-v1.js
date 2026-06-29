(()=>{
'use strict';
const V='1.0.1-no-cooldown-mask';
const ACTIVE='pmp_bug_bank_active_bugs_v1',OLD_ACTIVE='pmp_helper_problem_memory_active_v1',CLEAR='pmp_bug_bank_active_clear_until_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function load(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function key(x){return [norm(x.signature),norm(x.type||x.kind||x.problem),norm(x.where||x.where_seen),norm(x.fix_rule)].filter(Boolean).join('|')||norm(JSON.stringify(x).slice(0,120))}
function uniq(a){let out=[],seen={};(Array.isArray(a)?a:[]).filter(Boolean).forEach(x=>{let k=key(x);if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function clearActive(){save(CLEAR,0);save(ACTIVE,[]);save(OLD_ACTIVE,[])}
function tidy(){save(CLEAR,0);save(ACTIVE,uniq(load(ACTIVE,[])).slice(0,40))}
function bind(d){try{let bank=d.getElementById('bank');if(!bank)return;let b=bank.querySelector('[data-bug-bank-fix-active]');if(!b||b.dataset.fixActiveStabilizerV1===V)return;b.dataset.fixActiveStabilizerV1=V;b.addEventListener('click',()=>{clearActive();setTimeout(clearActive,120);setTimeout(()=>{try{let c=T().PMPBugBankCurrentActiveCleanerV1;if(c&&c.scan)c.scan()}catch(e){}},900);setTimeout(tidy,1400)},true)}catch(e){}}
function scan(){save(CLEAR,0);docs(T().document).forEach(bind);tidy()}
window.PMPBugBankFixActiveStabilizerV1={version:V,scan,clearActive};
try{let mo=new MutationObserver(()=>setTimeout(scan,50));mo.observe(document.documentElement,{childList:true,subtree:true})}catch(e){}
window.addEventListener('load',()=>[100,400,1000,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();