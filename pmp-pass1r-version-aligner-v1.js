(()=>{
'use strict';
const V='2.0.0-read-only-mount-registry-alignment-20260727A';
const KEY='pmp_pass1r_version_alignment_diagnostic_v2';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function inspect(reason){
  let registry=null,api=null;
  try{api=window.PMPMountRegistryV1||T().PMPMountRegistryV1;if(api&&typeof api.registry==='function')registry=api.registry()}catch(e){}
  if(!registry)registry=read('pmp_mount_registry_v1');
  const out={
    type:'PMP_PASS1R_VERSION_ALIGNMENT_DIAGNOSTIC_V2',
    version:V,
    owner:'mount_registry_owner',
    actor:'pmp-pass1r-version-aligner-v1.js',
    at:now(),
    reason:reason||'inspect',
    status:registry?'OBSERVED_READ_ONLY':'REGISTRY_NOT_READY',
    observed_registry_version:registry&&registry.version||null,
    observed_slot_count:registry&&Array.isArray(registry.slots)?registry.slots.length:null,
    canonical_registry_written:false,
    canonical_receipt_written:false,
    canonical_global_changed:false,
    rule:'Compatibility diagnostic only. Mount Registry is the sole canonical registry, receipt, and global writer.'
  };
  return put(KEY,out);
}
const api={version:V,inspect,align:inspect,diagnosticKey:KEY,rule:'read_only_no_registry_alignment_write'};
window.PMPPass1RVersionAlignerV1=api;
setTimeout(()=>inspect('boot_observation'),0);
})();
