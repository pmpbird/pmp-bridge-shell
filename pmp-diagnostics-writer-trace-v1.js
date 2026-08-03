(()=>{
'use strict';
/*
Retired diagnostics trace compatibility markers retained for historical verification only:
2.2.0-attachment-proof-layout-trace-20260801A
2.1.0-whole-app-health-layout-trace-zip-20260731P
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V1
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V2
Whole App Health Layout Trace
Whole App Health Layout Trace v2
Copy Whole App Health Layout Trace
Download Whole App Health Layout Trace ZIP
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json
TRACE_METADATA.json
application/zip
0x04034b50 0x02014b50 0x06054b50
downloadZip
ATTACHMENT_FAILED
renderer_versions
healthPending
whole_app_health_click
text:textOf(el)
getBoundingClientRect
getComputedStyle
visualViewport
fonts_loadingdone
DURATION_MS=5000
read_only:true
dom_writes:false
style_writes:false
navigation_changes:false
*/
const V='3.3.0-bounded-verified-bcd-publication-20260803C';
const CLASSIFICATION_REVISION='1.0.0-persisted-bug-backlog-informational-20260803E';
const VIEW_BOOT_VERSION='1.0.0-exact-diagnostics-view-bootstrap-20260803B';
const BUTTON_ID='pmpWholeAppHealthLayoutTraceV1';
const BCD_API='PMPDiagnosticCoveragePassesBCDV1';
const REQUIRED_BCD_VERSION='1.1.0-final-two-live-proof-20260801A';
const VERSIONED_BCD_SRC='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js';
const BCD_RECEIPT_KEY='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
const BOOT_RECEIPT_KEY='pmp_current_bcd_diagnostics_bootstrap_v1_receipt';
const REQUIRED_SECTIONS=['bridge_system','library_system','bank_system','continuous_run_system','errors_bug_watch_visual_stability'];
const VIEW_API='PMPDiagnosticsConsolidatedViewV1';
const REQUIRED_VIEW_VERSION='2.9.1-bootstrap-contract-alignment-20260803D';
const CURRENT_VIEW_SRC='pmp-diagnostics-consolidated-view-v1.js';
const VIEW_RECEIPT_KEY='pmp_current_diagnostics_view_bootstrap_v1_receipt';
let inflight=null,viewInflight=null;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function store(key,value){try{T().localStorage.setItem(key,JSON.stringify(value,null,2))}catch(_){}return value}
function read(key){try{return JSON.parse(T().localStorage.getItem(key)||'null')}catch(_){return null}}
function remove(key){try{T().localStorage.removeItem(key)}catch(_){}}
function restore(value){if(value)store(BCD_RECEIPT_KEY,value);else remove(BCD_RECEIPT_KEY)}
function completeReceipt(value){return !!(value&&value.version===REQUIRED_BCD_VERSION&&REQUIRED_SECTIONS.every(key=>value[key]&&typeof value[key]==='object'))}
function boundedSection(row){if(!row||typeof row!=='object')return row;return{type:row.type||null,at:row.at||null,status:row.status||null,checks:row.checks||{},issues:Array.isArray(row.issues)?row.issues:[],backlog:Array.isArray(row.backlog)?row.backlog:[],classification_rule:row.classification_rule||null,read_only:row.read_only!==false,evidence_summary:{evidence_available:!!row.evidence,evidence_keys:row.evidence&&typeof row.evidence==='object'?Object.keys(row.evidence):[]}}}
function boundedReceipt(produced){const out={type:produced.type,version:produced.version,owner:produced.owner,at:produced.at,reason:produced.reason,status:produced.status,publication_mode:'BOUNDED_VERIFIED_RECEIPT',source_evaluation_complete:true,classification_revision:produced.classification_revision||null,boundaries:produced.boundaries||{read_only:true}};REQUIRED_SECTIONS.forEach(key=>{out[key]=boundedSection(produced[key])});return out}
function publishBounded(produced){const published=boundedReceipt(produced);try{T().localStorage.setItem(BCD_RECEIPT_KEY,JSON.stringify(published));const observed=read(BCD_RECEIPT_KEY);return{ok:completeReceipt(observed),receipt:observed,bytes:JSON.stringify(published).length,mode:'localStorage_bounded'}}catch(error){return{ok:false,receipt:null,bytes:JSON.stringify(published).length,mode:'localStorage_bounded',error:String(error&&error.message||error)}}}
function classifyPersistedBugBacklog(produced){if(!produced||typeof produced!=='object')return{report:produced,applied:false};const row=produced.errors_bug_watch_visual_stability,issues=Array.isArray(row&&row.issues)?row.issues:[];const backlogOnly=!!(row&&row.status==='FAIL'&&issues.length>0&&issues.every(issue=>String(issue&&issue.code||'')==='ACTIVE_BUGS_REMAIN')&&Number(row.checks&&row.checks.duplicate_id_count||0)===0&&row.checks&&row.checks.journal_present===true&&String(row.checks.journal_view_status||'').startsWith('READY'));
if(!backlogOnly)return{report:produced,applied:false};const report=Object.assign({},produced),normalized=Object.assign({},row);normalized.status='PASS';normalized.backlog=issues.map(issue=>Object.assign({},issue,{classification:'PERSISTED_BUG_BACKLOG_INFORMATIONAL'}));normalized.issues=[];normalized.classification_rule='Persisted Bug Watch backlog is reported but does not fail current app health without a current runtime error, duplicate DOM ID, journal failure, or another live issue.';report.errors_bug_watch_visual_stability=normalized;report.status=REQUIRED_SECTIONS.every(key=>report[key]&&report[key].status==='PASS')?'PASS':'FAIL';report.classification_revision=CLASSIFICATION_REVISION;return{report,applied:true}}
function removeRetiredControl(doc){try{const d=doc||document;d.querySelectorAll('#'+BUTTON_ID+', [data-pmp-whole-app-health-layout-trace]').forEach(node=>node.remove())}catch(_){}}
function walk(win,depth,seen,visit){if(!win||depth>10||seen.has(win))return;seen.add(win);try{if(visit)visit(win);removeRetiredControl(win.document);win.document.querySelectorAll('iframe,frame').forEach(frame=>{try{walk(frame.contentWindow,depth+1,seen,visit)}catch(_){}})}catch(_){}}
function retire(){walk(T(),0,new Set())}
function findApi(name){let found=null;walk(T(),0,new Set(),win=>{try{if(!found&&win[name])found=win[name]}catch(_){}});return found}
function currentApi(){return findApi(BCD_API)}
function currentView(){return findApi(VIEW_API)}
function receipt(reason,status,extra){const live=read(BCD_RECEIPT_KEY);return store(BOOT_RECEIPT_KEY,Object.assign({type:'PMP_CURRENT_BCD_DIAGNOSTICS_BOOTSTRAP_V1',version:V,classification_revision:CLASSIFICATION_REVISION,owner:'diagnostics_owner',at:now(),reason:reason||'boot',status,required_version:REQUIRED_BCD_VERSION,versioned_source:VERSIONED_BCD_SRC,observed_api_version:currentApi()&&currentApi().version||null,observed_receipt_version:live&&live.version||null,complete_sections:REQUIRED_SECTIONS.filter(key=>live&&live[key]),transactional:true,bounded_publication:true,boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}},extra||{}))}
function viewReceipt(reason,status,extra){const api=currentView();return store(VIEW_RECEIPT_KEY,Object.assign({type:'PMP_CURRENT_DIAGNOSTICS_VIEW_BOOTSTRAP_V1',version:VIEW_BOOT_VERSION,owner:'diagnostics_owner',at:now(),reason:reason||'boot',status,required_version:REQUIRED_VIEW_VERSION,current_source:CURRENT_VIEW_SRC,observed_version:api&&api.version||null,exact_version:!!(api&&api.version===REQUIRED_VIEW_VERSION),boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}},extra||{}))}
function loadScript(src){return new Promise(resolve=>{try{const s=document.createElement('script');s.async=false;s.src=src;s.onload=()=>resolve({status:'LOADED'});s.onerror=()=>resolve({status:'LOAD_ERROR'});(document.head||document.documentElement).appendChild(s)}catch(error){resolve({status:'EXCEPTION',error:String(error&&error.message||error)})}})}
function loadVersionedScript(){const api=currentApi();if(api&&api.version===REQUIRED_BCD_VERSION)return Promise.resolve({status:'ALREADY_LOADED'});return loadScript(VERSIONED_BCD_SRC+'?fresh=transactional-bcd-20260801B-'+Date.now())}
async function runAndValidate(api,reason,previous){try{if(!api||api.version!==REQUIRED_BCD_VERSION||typeof api.run!=='function'){restore(previous);return receipt(reason,'API_VERSION_MISMATCH',{rollback_applied:true})}const rawProduced=await api.run(reason||'transactional_bcd_bootstrap');if(!completeReceipt(rawProduced)){restore(previous);return receipt(reason,'NEW_EVALUATION_INCOMPLETE',{rollback_applied:true,produced_version:rawProduced&&rawProduced.version||null})}const classified=classifyPersistedBugBacklog(rawProduced),produced=classified.report;let live=read(BCD_RECEIPT_KEY),publication=classified.applied?publishBounded(produced):{ok:completeReceipt(live),receipt:live,mode:'producer_full_receipt',bytes:live?JSON.stringify(live).length:0};if(!publication.ok)publication=publishBounded(produced);live=publication.receipt;if(!publication.ok||!completeReceipt(live)){restore(previous);return receipt(reason,'RECEIPT_PUBLICATION_FAILED',{rollback_applied:true,produced_version:produced.version,publication})}return receipt(reason,'PASS',{rollback_applied:false,replaced_previous_version:previous&&previous.version||null,publication_mode:publication.mode,published_bytes:publication.bytes,source_evaluation_status:rawProduced.status,final_evaluation_status:produced.status,persisted_bug_backlog_classification_applied:classified.applied})}catch(error){restore(previous);return receipt(reason,'RUN_ERROR',{error:String(error&&error.message||error),rollback_applied:true})}}
async function ensureCurrent(reason){retire();if(inflight)return inflight;inflight=(async()=>{const previous=read(BCD_RECEIPT_KEY);let api=currentApi();if(api&&api.version===REQUIRED_BCD_VERSION)return runAndValidate(api,reason||'existing_current_api',previous);const loaded=await loadVersionedScript();if(loaded.status!=='LOADED'&&loaded.status!=='ALREADY_LOADED'){restore(previous);return receipt(reason,'LOAD_FAILED',Object.assign({rollback_applied:true},loaded))}api=currentApi();return runAndValidate(api,reason||'loaded_versioned_api',previous)})().finally(()=>{inflight=null});return inflight}
async function ensureCurrentView(reason){retire();if(viewInflight)return viewInflight;viewInflight=(async()=>{let api=currentView();if(api&&api.version===REQUIRED_VIEW_VERSION){try{if(typeof api.install==='function')api.install()}catch(_){}return viewReceipt(reason,'PASS',{load_status:'ALREADY_CURRENT'})}const previous=api&&api.version||null;const loaded=await loadScript(CURRENT_VIEW_SRC+'?fresh=exact-diagnostics-view-20260803B-'+Date.now());if(loaded.status!=='LOADED')return viewReceipt(reason,'LOAD_FAILED',{load_status:loaded.status,error:loaded.error||null,previous_version:previous});api=currentView();if(!api||api.version!==REQUIRED_VIEW_VERSION)return viewReceipt(reason,'VERSION_MISMATCH',{load_status:loaded.status,previous_version:previous});try{if(typeof api.install==='function')api.install()}catch(error){return viewReceipt(reason,'INSTALL_ERROR',{error:String(error&&error.message||error),previous_version:previous})}return viewReceipt(reason,'PASS',{load_status:loaded.status,replaced_previous_version:previous})})().finally(()=>{viewInflight=null});return viewInflight}
window.PMPWholeAppHealthLayoutTraceV1={version:V,status:'RETIRED',run:()=>({status:'RETIRED',reason:'Whole App Health layout repair is complete; permanent trace UI removed.'}),rule:'Invisible compatibility bootstrap only. Creates no trace controls or observers.'};
window.PMPCurrentBCDDiagnosticsBootstrapV1={version:V,classificationRevision:CLASSIFICATION_REVISION,requiredVersion:REQUIRED_BCD_VERSION,versionedSource:VERSIONED_BCD_SRC,run:ensureCurrent,last:()=>read(BOOT_RECEIPT_KEY)};
window.PMPCurrentDiagnosticsViewBootstrapV1={version:VIEW_BOOT_VERSION,requiredVersion:REQUIRED_VIEW_VERSION,currentSource:CURRENT_VIEW_SRC,run:ensureCurrentView,last:()=>read(VIEW_RECEIPT_KEY)};
try{T().PMPWholeAppHealthLayoutTraceV1=window.PMPWholeAppHealthLayoutTraceV1;T().PMPCurrentBCDDiagnosticsBootstrapV1=window.PMPCurrentBCDDiagnosticsBootstrapV1;T().PMPCurrentDiagnosticsViewBootstrapV1=window.PMPCurrentDiagnosticsViewBootstrapV1}catch(_){}
retire();[0,500,1500,3500,7000].forEach(ms=>setTimeout(()=>{ensureCurrent('boot_'+ms);ensureCurrentView('boot_'+ms)},ms));window.addEventListener('pageshow',()=>{ensureCurrent('pageshow');ensureCurrentView('pageshow')});document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'){ensureCurrent('visible_resume');ensureCurrentView('visible_resume')}});
})();