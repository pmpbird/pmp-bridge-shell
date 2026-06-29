(()=>{
'use strict';
const V='1.0.1-strong-level-text-lock';
function T(){try{return top||window}catch(e){return window}}
function allDocs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)allDocs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function text(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function set(x,k,v){try{x.style.setProperty(k,v,'important')}catch(e){}}
function isLevel(x){return /^Level\s+(?:[0-9]+[A-Z]?|30B)\s*[:—-]/i.test(text(x))}
function levelAttr(x){try{return Array.from(x.attributes||[]).some(a=>/^data-(l\d|r30b|level|source-reference-gate-level4)/i.test(a.name))}catch(e){return false}}
function oneLine(x){set(x,'white-space','nowrap');set(x,'overflow','hidden');set(x,'text-overflow','ellipsis');set(x,'display','block');set(x,'max-width','100%');set(x,'line-height','1.18');set(x,'word-break','normal');set(x,'overflow-wrap','normal')}
function card(x){let c=x&&x.closest&&x.closest('section,article,div');if(!c)return;set(c,'overflow','hidden');set(c,'max-width','100%');set(c,'box-sizing','border-box')}
function scanDoc(d){try{let b=d.getElementById('bank');if(!b)return;let scope=b.querySelector('[data-continuous-run-level-ui-scope-v1]')||b;if(!/Continuous Run|Lossless Slots ZIP Import|Level\s+30B|Level\s+29/i.test(text(scope).slice(0,6000)))return;let n=0;Array.from(scope.querySelectorAll('h1,h2,h3,h4,p,b,strong,button,summary,span,div')).forEach(x=>{if(isLevel(x)||levelAttr(x)){oneLine(x);card(x);n++}});try{localStorage.setItem('pmp_continuous_run_single_line_hold_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_SINGLE_LINE_HOLD_V1',version:V,at:new Date().toISOString(),count:n,rule:'Strong inline lock applied to Continuous Run level labels and badges.'}))}catch(e){}}catch(e){}}
function scan(){allDocs(T().document).forEach(scanDoc)}
window.PMPContinuousRunSingleLineHoldV1={version:V,scan};
try{new MutationObserver(()=>setTimeout(scan,30)).observe(document.documentElement,{childList:true,subtree:true,characterData:true,attributes:true})}catch(e){}
window.addEventListener('load',()=>[50,150,350,700,1200,2200,4500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,300);scan();
})();