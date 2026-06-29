(()=>{
'use strict';
const V='1.0.0';
function T(){try{return top||window}catch(e){return window}}
function allDocs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)allDocs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function text(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function set(x,k,v){try{x.style.setProperty(k,v,'important')}catch(e){}}
function title(d){let b=d.getElementById('bank');return b?text(b.querySelector('[data-bank-detail-title]')):''}
function isLevel(x){return /^Level\s+(?:[0-9]+[A-Z]?|30B)\s*[:—-]/i.test(text(x))}
function oneLine(x){set(x,'white-space','nowrap');set(x,'overflow','hidden');set(x,'text-overflow','ellipsis');set(x,'display','block');set(x,'max-width','100%');set(x,'line-height','1.18');set(x,'word-break','normal')}
function card(x){let c=x&&x.closest&&x.closest('section,article,div');if(!c)return;set(c,'overflow','hidden');set(c,'max-width','100%');set(c,'box-sizing','border-box')}
function scanDoc(d){try{let b=d.getElementById('bank');if(!b||title(d)!=='Continuous Run Bank')return;let n=0;Array.from(b.querySelectorAll('h1,h2,h3,h4,p,b,strong,button,summary,span')).forEach(x=>{if(isLevel(x)){oneLine(x);card(x);n++}});try{localStorage.setItem('pmp_continuous_run_single_line_hold_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_SINGLE_LINE_HOLD_V1',version:V,at:new Date().toISOString(),count:n}))}catch(e){}}catch(e){}}
function scan(){allDocs(T().document).forEach(scanDoc)}
window.PMPContinuousRunSingleLineHoldV1={version:V,scan};
try{new MutationObserver(()=>setTimeout(scan,30)).observe(document.documentElement,{childList:true,subtree:true,characterData:true})}catch(e){}
window.addEventListener('load',()=>[50,150,350,700,1200,2200,4500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,300);scan();
})();