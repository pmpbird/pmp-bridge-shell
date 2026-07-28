(()=>{
'use strict';
const V='2.0.0-single-owner-loader-request';
function inject(){
  try{
    const doc=window.top&&window.top.document;
    if(!doc||!doc.head)return{status:'top_document_unavailable'};
    const existing=doc.getElementById('pmpTopLosslessFullModularLoader');
    if(existing)return{status:'already_present'};
    const script=doc.createElement('script');
    script.id='pmpTopLosslessFullModularLoader';
    script.src='pmp-top-lossless-loader.js';
    script.dataset.pmpOwner='reload_current_owner';
    doc.head.appendChild(script);
    return{status:'requested_once'};
  }catch(error){return{status:'request_failed',error:String(error&&error.message||error)}}
}
window.PMPTopLosslessInjectorV2={version:V,owner:'reload_current_owner',inject,rule:'One stable request only; never replace, reload, or poll the top loader.'};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',inject,{once:true});
else inject();
})();
