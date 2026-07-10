(()=>{
'use strict';
const V='1.0.1-disabled-unhide-only-20260710A';
const OWNER='pmp-control-diagnostics-migration-v1';
const RECEIPT='pmp_control_diagnostics_migration_v1_receipt';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function unhide(){let n=0;try{docs(T().document).forEach(d=>{Array.from(d.querySelectorAll('[data-pmp-control-diagnostics-moved="true"]')).forEach(el=>{try{el.style.removeProperty('display');delete el.dataset.pmpControlDiagnosticsMoved;n++}catch(e){}})})}catch(e){}return n}
function run(){let n=unhide();let r={type:'PMP_CONTROL_DIAGNOSTICS_MIGRATION_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'DISABLED_UNHIDE_ONLY_ROLLBACK',unhidden_blocks:n,rule:'Rollback: this script no longer hides or moves Control Room content. It only unhides any blocks hidden by the previous migration attempt.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',diagnostics_deleted:'not_attempted',control_legacy_ui:'unhide_only'}};put(RECEIPT,r);return r}
window.PMPControlDiagnosticsMigrationV1={version:V,owner:OWNER,run,rule:'Disabled rollback version. Unhide only.'};try{T().PMPControlDiagnosticsMigrationV1=window.PMPControlDiagnosticsMigrationV1}catch(e){};
run();[100,400,1000,2000,4000].forEach(t=>setTimeout(run,t));
})();