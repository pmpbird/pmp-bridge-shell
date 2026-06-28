(()=>{
'use strict';
const V='1.0.0-remove-hidden-safe-writer-surface';
const SAFE_URL='safe-writer-v14.html?from=control-open&app=pmp-home-single-v6';
function T(){try{return top||window}catch(e){return window}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function removeHiddenSafeWriter(d){let count=0;try{Array.from(d.querySelectorAll('#safeWriterCanonical,[data-pmp-safe-writer-version],section[data-pmp-safe-writer-version]')).forEach(x=>{x.remove();count++})}catch(e){}return count}
function restoreNormalButton(w,d){try{Array.from(d.querySelectorAll('button,a')).forEach(b=>{let t=clean(b.textContent);if(/^Open Safe Writer$/i.test(t)||/Open Safe Writer/i.test(t)){b.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}try{w.location.href=SAFE_URL}catch(x){location.href=SAFE_URL}return false};b.setAttribute('data-pmp-safe-writer-normal-route','1')}});try{w.openSafeWriter=function(){w.location.href=SAFE_URL;return false}}catch(e){}}catch(e){}}
function cleanBugMemoryLinks(d){try{if(!/Bug Memory/i.test(String(d.title||''))&&!d.querySelector('h1'))return;let isBug=Array.from(d.querySelectorAll('h1')).some(h=>/^Bug Memory$/i.test(clean(h.textContent)));if(!isBug)return;Array.from(d.querySelectorAll('a,button')).forEach(b=>{let t=clean(b.textContent);if(/Safe Writer/i.test(t))b.remove()})}catch(e){}}
function scan(){let removed=0;docs(T().document).forEach(d=>{try{removed+=removeHiddenSafeWriter(d);let w=d.defaultView||window;restoreNormalButton(w,d);cleanBugMemoryLinks(d)}catch(e){}});try{if(removed)localStorage.setItem('pmp_hidden_safe_writer_surface_cleaner_v1_receipt',JSON.stringify({type:'PMP_HIDDEN_SAFE_WRITER_SURFACE_CLEANER_V1',version:V,removed,at:new Date().toISOString(),safe_claim:'Removed duplicate in-app Safe Writer surface only. Canonical Safe Writer v14 page remains available from normal Control Room.',do_not_claim:'This does not delete Safe Writer system files or source/mold tools.'}))}catch(e){}return removed}
window.PMPHiddenSafeWriterSurfaceCleanerV1={version:V,scan};
window.addEventListener('load',()=>[80,250,700,1500,3000,6000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();