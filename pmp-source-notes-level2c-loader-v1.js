(()=>{
'use strict';
if(document.querySelector('script[data-pmp-level2c-loader]'))return;
let s=document.createElement('script');
s.setAttribute('data-pmp-level2c-loader','1');
s.src='pmp-source-pdf-text-level2c-v1.js?fresh=l2c-'+Date.now();
(document.head||document.documentElement).appendChild(s);
})();