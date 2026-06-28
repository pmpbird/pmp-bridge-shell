(()=>{
'use strict';
const V='1.0.0-bug-lab-not-bug-memory';
function T(){try{return top||window}catch(e){return window}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function go(){try{T().location.href='bug-memory-current-clean-v1.html?fresh=bug-lab-auto-bank-'+Date.now()+'&contrast=2'}catch(e){location.href='bug-memory-current-clean-v1.html?fresh=bug-lab-auto-bank-'+Date.now()+'&contrast=2'}return false}
function patchDoc(d){try{let w=d.defaultView||window;if(w&&!w.__pmpBugLabSecretOwnerV1){let old=typeof w.showSecret==='function'?w.showSecret:null;w.showSecret=function(name){let n=String(name||'');if(n==='Bug Memory'||n==='Bug Lab')return go();if(old)return old.apply(this,arguments)}}Array.from(d.querySelectorAll('button,a,[role="button"]')).forEach(b=>{let t=clean(b.textContent);if(t==='Bug Memory'){b.textContent='Bug Lab';b.setAttribute('data-bug-lab-secret-control-owner-v1','renamed');b.onclick=e=>{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}return go()}}if(t==='Bug Lab'){b.onclick=e=>{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}return go()}}});if(!d.documentElement.dataset.pmpBugLabSecretControlDelegateV1){d.documentElement.dataset.pmpBugLabSecretControlDelegateV1='1';d.addEventListener('click',e=>{let b=e.target&&e.target.closest&&e.target.closest('button,a,[role="button"]');if(!b)return;let t=clean(b.textContent);if(t==='Bug Memory'||t==='Bug Lab'){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();return go()}},true)}}catch(e){}}
function scan(){docs(T().document).forEach(patchDoc)}
window.PMPBugLabSecretControlOwnerV1={version:V,scan};
window.addEventListener('load',()=>[80,250,800,1600,3200].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();