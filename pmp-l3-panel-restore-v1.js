(()=>{
'use strict';
function topWin(){try{return window.top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function panel(d){let box=d.querySelector('[data-temp-transfer-store][data-v2="1"]')||d.querySelector('[data-temp-transfer-store]')||d.getElementById('bank');if(!box)return;let host=box.querySelector('[data-source-zip-levels-single]')||box;let p=box.querySelector('[data-source-text-reader-level3]')||d.querySelector('[data-source-text-reader-level3]');if(!p){p=d.createElement('div');p.setAttribute('data-source-text-reader-level3','');p.style.cssText='margin:8px 0 0;padding:8px;border:1px solid rgba(0,0,0,.08);border-radius:10px';p.innerHTML='<h4 style="margin:0 0 4px">Level 3 — Source Text Reader</h4><p class="sub">Part of Source ZIP Levels. Search and open the recovered source texts.</p><input data-l3-q placeholder="search or note number" style="width:100%;box-sizing:border-box;margin:4px 0;padding:8px;border-radius:8px"><div class="grid"><button class="mini" data-l3-verify>Verify 29/29</button><button class="mini" data-l3-search>Search Source Text</button><button class="mini" data-l3-open>Open Note</button></div><pre class="note" data-l3-out style="max-height:220px;overflow:auto;white-space:pre-wrap">Level 3 restored simple state.</pre>'}if(p.parentNode!==host)host.appendChild(p)}
function scan(){docs(topWin().document).forEach(d=>{try{panel(d)}catch(e){}})}
window.PMPL3PanelRestoreV1={scan};
window.addEventListener('load',()=>[300,1000,2500,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,2000);scan();
})();