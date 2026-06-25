(()=>{
'use strict';
const V='4.1.0-source-level-visual-quarantine';
const BAD='[data-source-zip-reader-level2],[data-source-zip-extractor-level2b],[data-source-pdf-text-level2c]';
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>8)return a;try{a.push(d);d.querySelectorAll('iframe').forEach(f=>{try{let x=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(x)docs(x,a,n+1)}catch(e){}})}catch(e){}return a}
function scan(){docs(document).forEach(d=>{try{d.querySelectorAll(BAD).forEach(x=>{x.style.display='none';x.style.height='0';x.style.margin='0';x.style.padding='0';x.style.overflow='hidden'})}catch(e){}})}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[0,200,800,2000,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();