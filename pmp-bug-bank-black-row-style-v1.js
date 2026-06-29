(()=>{
'use strict';
const V='1.0.1-family-rows-black';
const CSS=`
#bank [data-bug-bank-owner-v1] [data-bug-row-toggle],
#bank [data-bug-bank-owner-v1] [data-bug-row-copy],
#bank [data-bug-bank-family-view-v1] [data-bug-family-toggle],
#bank [data-bug-bank-family-view-v1] [data-bug-family-copy]{
  background:#172234 !important;
  background-color:#172234 !important;
  background-image:none !important;
  color:#eef4fb !important;
  border-color:#07101c !important;
  -webkit-text-fill-color:#eef4fb !important;
}
#bank [data-bug-bank-owner-v1] [data-bug-row-panel],
#bank [data-bug-bank-family-view-v1] [data-bug-family-panel],
#bank [data-bug-bank-family-view-v1] [data-bug-family-panel] div{
  background:#123024 !important;
  background-color:#123024 !important;
  background-image:none !important;
  color:#d8ffe2 !important;
  border-color:#07101c !important;
  -webkit-text-fill-color:#d8ffe2 !important;
}
`;
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function apply(d){try{let s=d.getElementById('pmpBugBankBlackRowStyleV1');if(!s){s=d.createElement('style');s.id='pmpBugBankBlackRowStyleV1';d.head.appendChild(s)}s.textContent=CSS}catch(e){}}
function scan(){docs(T().document).forEach(apply)}
window.PMPBugBankBlackRowStyleV1={version:V,scan};
window.addEventListener('load',()=>[100,400,1000,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();