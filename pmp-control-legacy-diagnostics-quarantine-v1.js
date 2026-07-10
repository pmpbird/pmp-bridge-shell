(()=>{
'use strict';
const V='1.0.1-disabled-rollback-20260710A';
const OWNER='pmp-control-legacy-diagnostics-quarantine-v1';
const KEY='pmp_control_legacy_diagnostics_quarantine_v1_receipt';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function unhide(){let n=0;docs(T().document).forEach(d=>{try{Array.from(d.querySelectorAll('[data-pmp-control-legacy-diagnostics-quarantined="true"]')).forEach(el=>{el.style.removeProperty('display');el.removeAttribute('data-pmp-control-legacy-diagnostics-quarantined');n++})}catch(e){}});return n}
function run(reason){let n=unhide();let r={type:'PMP_CONTROL_LEGACY_DIAGNOSTICS_QUARANTINE_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'DISABLED_ROLLBACK',reason:reason||'run',unhid_quarantined_blocks:n,rule:'Rollback: this script no longer hides Control Room content. It only unhides blocks previously marked by the failed quarantine.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',diagnostics_tab_dom_patch:'not_attempted',panel_move:'not_attempted',panel_hide:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted'}};put(KEY,r);return r}
window.PMPControlLegacyDiagnosticsQuarantineV1={version:V,owner:OWNER,run,rule:'Disabled rollback version. Unhide-only.'};try{T().PMPControlLegacyDiagnosticsQuarantineV1=window.PMPControlLegacyDiagnosticsQuarantineV1}catch(e){};
run('script_load_disabled');
})();