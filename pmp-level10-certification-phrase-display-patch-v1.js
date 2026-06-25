(()=>{
'use strict';
const V='1.0.0-level10-certification-phrase-display-patch';
const L10K='pmp_level10_full_chain_certification_lock_v1';
const REAL='pmp-static-inspection-automatic-test-selection-specification-v1';
const FAKE='purple banana airplane rule';
function W(){try{return window.top||window}catch(e){return window}}
function j(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function save(k,v){try{W().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function enrich(){let x=j(L10K,null);if(!x)return null;let changed=false;function one(c){if(!c)return;if(c.real_test_phrase!==REAL){c.real_test_phrase=REAL;changed=true}if(c.fake_test_phrase!==FAKE){c.fake_test_phrase=FAKE;changed=true}}
one(x.latest||x);if(Array.isArray(x.history))x.history.forEach(one);if(changed)save(L10K,x);return x}
function phraseText(){return 'Certification test phrases used:\nReal source phrase: '+REAL+'\nFake block phrase: '+FAKE}
function addToOutput(o){if(!o)return;let t=o.textContent||'';if(!t.trim())return;if(t.includes('Real source phrase:'))return;o.textContent=t+'\n\n'+phraseText()}
function patch(d){let p=d.querySelector('[data-level10-cert-lock]');if(!p)return;if(!p.querySelector('[data-l10-phrase-proof]')){let h=p.querySelector('p.sub')||p.querySelector('h4');if(h)h.insertAdjacentHTML('afterend','<pre class="note" data-l10-phrase-proof style="white-space:pre-wrap">'+phraseText()+'</pre>')}let o=p.querySelector('[data-l10-out]');let run=p.querySelector('[data-l10-run]'),view=p.querySelector('[data-l10-view]');[run,view].forEach(btn=>{if(btn&&!btn.dataset.l10PhrasePatch){btn.dataset.l10PhrasePatch='1';btn.addEventListener('click',()=>setTimeout(()=>{enrich();addToOutput(o)},900))}});enrich();addToOutput(o)}
function scan(){docs(W().document).forEach(d=>{try{patch(d)}catch(e){}})}
window.PMPLevel10PhraseDisplayPatchV1={version:V,scan,enrich,real_phrase:REAL,fake_phrase:FAKE};
window.addEventListener('load',()=>[300,1200,2500,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1500);scan();
})();