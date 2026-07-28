(()=>{
'use strict';
const V='2.0.0-canonical-reader-delegate-20260727A';
function find(){
  const windows=[window];try{if(window.top&&window.top!==window)windows.push(window.top)}catch(e){}
  for(const w of windows){try{if(w.PMPResidentContinuousRunStatusReaderV1)return w.PMPResidentContinuousRunStatusReaderV1}catch(e){}}
  return null;
}
function read(){
  const api=find();
  if(api&&typeof api.read==='function')return api.read();
  return{type:'PMP_RESIDENT_CR_STATUS_ROUTER_V2',version:V,status:'CANONICAL_READER_NOT_READY',read_only:true,canonical_reader:'pmp-resident-continuous-run-status-reader-v1.js'};
}
window.PMPResidentCRStatusRouterV1={version:V,role:'read_only_delegate',read,scan:read,rule:'Delegates to the canonical Resident status reader. It does not write status, wrap residentRun, bind Run buttons, or install a timer.'};
})();
