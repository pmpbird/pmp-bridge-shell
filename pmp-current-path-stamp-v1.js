(()=>{
'use strict';
const V='1.0.3-neutralized-use-control-footer-file';
const IDS=['pmpCurrentPathStampV1','pmpCurrentPathStampFloatingV1','pmpCurrentPathStampFooterV1'];
function eachDoc(fn){let seen=[];function walk(w,n){if(!w||n>14||seen.indexOf(w)>-1)return;seen.push(w);try{if(w.document)fn(w.document);Array.from(w.document.querySelectorAll('iframe,frame')).forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}walk(window,0);try{walk(top,0)}catch(e){}}
function remove(){eachDoc(d=>IDS.forEach(id=>{try{let x=d.getElementById(id);if(x)x.remove()}catch(e){}}))}
window.PMPCurrentPathStampV1={version:V,install:remove,status:()=>({type:'PMP_CURRENT_PATH_STAMP_NEUTRALIZED',version:V})};
remove();setInterval(remove,1000);
})();