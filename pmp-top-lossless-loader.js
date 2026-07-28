(()=>{
'use strict';
const V='2.0.0-idempotent-owner-delegated-loader';
const FILES=[
  'pmp-top-lossless-packet-builder.js',
  'pmp-top-lossless-copy-open.js',
  'pmp-copy-lossless-diagnostic.js',
  'pmp-top-copy-lossless-button.js'
];
function loadOne(src,index){
  return new Promise(resolve=>{
    const id='pmpTopLosslessScript'+index;
    const existing=document.getElementById(id);
    if(existing){resolve({src,status:'already_present'});return}
    const script=document.createElement('script');
    script.id=id;
    script.src=src;
    script.dataset.pmpOwner='reload_current_owner';
    script.onload=()=>resolve({src,status:'loaded'});
    script.onerror=()=>resolve({src,status:'load_error'});
    document.head.appendChild(script);
  });
}
async function start(){
  if(window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY)return{status:'already_ready'};
  const results=[];
  for(let i=0;i<FILES.length;i++)results.push(await loadOne(FILES[i],i));
  window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY=true;
  window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY_AT=new Date().toISOString();
  return{status:'ready',results};
}
window.PMPTopLosslessLoaderV2={version:V,owner:'reload_current_owner',start,files:FILES.slice(),rule:'Idempotent one-time loading only; never remove, replace, or cache-bust an existing owner script.'};
window.pmpReloadTopLosslessFullModular=start;
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
else start();
})();
