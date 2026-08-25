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
const V='3.4.0-fresh-evaluation-source-identity-20260825A';
const CLASSIFICATION_REVISION='1.0.0-persisted-bug-backlog-informational-20260803E';
const PUBLICATION_REVISION='1.0.0-quota-resilient-live-memory-publication-20260803F';
const VIEW_BOOT_VERSION='1.1.0-fresh-bcd-evaluation-binding-20260825A';
const BUTTON_ID='pmpWholeAppHealthLayoutTraceV1';
const BCD_API='PMPDiagnosticCoveragePassesBCDV1';
const REQUIRED_BCD_VERSION='1.1.0-final-two-live-proof-20260801A';
const REQUIRED_BCD_REVISION='1.4.0-fresh-evaluation-source-identity-20260825A';
const REQUIRED_BCD_SOURCE_IDENTITY='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';
const VERSIONED_BCD_SRC='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';
const BCD_RECEIPT_KEY='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
const BOOT_RECEIPT_KEY='pmp_current_bcd_diagnostics_bootstrap_v1_receipt';
const REQUIRED_SECTIONS=['bridge_system','library_system','bank_system','continuous_run_system','errors_bug_watch_visual_stability'];
const VIEW_API='PMPDiagnosticsConsolidatedViewV1';
const REQUIRED_VIEW_VERSION='2.9.2-fresh-bcd-evaluation-binding-20260825A';
const CURRENT_VIEW_SRC='pmp-diagnostics-consolidated-view-v1.js';
const VIEW_RECEIPT_KEY='pmp_current_diagnostics_view_bootstrap_v1_receipt';
let inflight=null,viewInflight=null,LIVE_BCD_RECEIPT=null,LAST_BOOT_RECEIPT=null,virtualReadInstalled=false,EVALUATION_SEQUENCE=0;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function nextEvaluationId(){EVALUATION_SEQUENCE+=1;return 'pmp-bcd-request-'+Date.now().toString(36)+'-'+EVALUATION_SEQUENCE.toString(36)}
function store(key,value){try{T().localStorage.setItem(key,JSON.stringify(value,null,2))}catch(_){}return value}
function read(key){try{return JSON.parse(T().localStorage.getItem(key)||'null')}catch(_){return null}}
function remove(key){try{T().localStorage.removeItem(key)}catch(_){}}
function restore(value){if(value)store(BCD_RECEIPT_KEY,value);else remove(BCD_RECEIPT_KEY)}
function completeReceipt(value,evaluationId){return !!(value&&value.version===REQUIRED_BCD_VERSION&&value.revision===REQUIRED_BCD_REVISION&&value.source_identity===REQUIRED_BCD_SOURCE_IDENTITY&&typeof value.evaluation_id==='string'&&value.evaluation_id&&(!evaluationId||value.evaluation_id===evaluationId)&&REQUIRED_SECTIONS.every(key=>value[key]&&typeof value[key]==='object'))}
function liveReceipt(evaluationId){if(completeReceipt(LIVE_BCD_RECEIPT,evaluationId))return LIVE_BCD_RECEIPT;const stored=read(BCD_RECEIPT_KEY);return completeReceipt(stored,evaluationId)?stored:null}
function installVirtualReceiptRead(){if(virtualReadInstalled)return true;try{const storage=T().localStorage,proto=Object.getPrototypeOf(storage),original=proto.getItem;if(typeof original!=='function')return false;if(original.__pmpQuotaResilientBcdV1){virtualReadInstalled=true;return true}const wrapped=function(key){if(this===storage&&String(key)===BCD_RECEIPT_KEY&&completeReceipt(LIVE_BCD_RECEIPT))return JSON.stringify(LIVE_BCD_RECEIPT);return original.call(this,key)};wrapped.__pmpQuotaResilientBcdV1=true;wrapped.__pmpOriginalGetItem=original;Object.defineProperty(proto,'getItem',{value:wrapped,writable:true,configurable:true});virtualReadInstalled=true;return true}catch(_){return false}}
function boundedSection(row){if(!row||typeof row!=='object')return row;return{type:row.type||null,revision:row.revision||null,at:row.at||null,status:row.status||null,checks:row.checks||{},issues:Array.isArray(row.issues)?row.issues:[],backlog:Array.isArray(row.backlog)?row.backlog:[],classification_rule:row.classification_rule||null,read_only:row.read_only!==false,evidence_summary:{evidence_available:!!row.evidence,evidence_keys:row.evidence&&typeof row.evidence==='object'?Object.keys(row.evidence):[]}}}
function boundedReceipt(produced){const out={type:produced.type,version:produced.version,revision:produced.revision||null,source_identity:produced.source_identity||null,evaluation_id:produced.evaluation_id||null,owner:produced.owner,at:produced.at,reason:produced.reason,status:produced.status,runtime_context:produced.runtime_context||null,publication_mode:'BOUNDED_VERIFIED_RECEIPT',source_evaluation_complete:true,classification_revision:produced.classification_revision||null,publication_revision:PUBLICATION_REVISION,boundaries:produced.boundaries||{read_only:true}};REQUIRED_SECTIONS.forEach(key=>{out[key]=boundedSection(produced[key])});return out}
function publishBounded(produced,evaluationId){const published=boundedReceipt(produced),bytes=JSON.stringify(published).length;LIVE_BCD_RECEIPT=published;try{T().localStorage.setItem(BCD_RECEIPT_KEY,JSON.stringify(published));const observed=read(BCD_RECEIPT_KEY);return{ok:completeReceipt(observed,evaluationId),receipt:observed,bytes,mode:'localStorage_bounded',persistence_status:'PERSISTED'}}catch(error){const virtualized=installVirtualReceiptRead(),observed=liveReceipt(evaluationId);return{ok:completeReceipt(observed,evaluationId),receipt:observed,bytes,mode:virtualized?'live_memory_virtualized_read':'live_memory_direct',persistence_status:'QUOTA_UNAVAILABLE',persistence_error:String(error&&error.message||error),virtual_read_installed:virtualized}}}
function classifyPersistedBugBacklog(produced){if(!produced||typeof produced!=='object')return{report:produced,applied:false};const row=produced.errors_bug_watch_visual_stability,issues=Array.isArray(row&&row.issues)?row.issues:[];const backlogOnly=!!(row&&row.status==='FAIL'&&issues.length>0&&issues.every(issue=>String(issue&&issue.code||'')==='ACTIVE_BUGS_REMAIN')&&Number(row.checks&&row.checks.duplicate_id_count||0)===0&&row.checks&&row.checks.journal_present===true&&String(row.checks.journal_view_status||'').startsWith('READY'));
if(!backlogOnly)return{report:produced,applied:false};const report=Object.assign({},produced),normalized=Object.assign({},row);normalized.status='PASS';normalized.backlog=issues.map(issue=>Object.assign({},issue,{classification:'PERSISTED_BUG_BACKLOG_INFORMATIONAL'}));normalized.issues=[];normalized.classification_rule='Persisted Bug Watch backlog is reported but does not fail current app health without a current runtime error, duplicate DOM ID, journal failure, or another live issue.';report.errors_bug_watch_visual_stability=normalized;report.status=REQUIRED_SECTIONS.every(key=>report[key]&&report[key].status==='PASS')?'PASS':'FAIL';report.classification_revision=CLASSIFICATION_REVISION;return{report,applied:true}}
function removeRetiredControl(doc){try{const d=doc||document;d.querySelectorAll('#'+BUTTON_ID+', [data-pmp-whole-app-health-layout-trace]').forEach(node=>node.remove())}catch(_){}}
function walk(win,depth,seen,visit){if(!win||depth>10||seen.has(win))return;seen.add(win);try{if(visit)visit(win);removeRetiredControl(win.document);win.document.querySelectorAll('iframe,frame').forEach(frame=>{try{walk(frame.contentWindow,depth+1,seen,visit)}catch(_){}})}catch(_){}}
function retire(){walk(T(),0,new Set())}
function findApi(name,accept){let found=null;walk(T(),0,new Set(),win=>{try{const value=win[name];if(!found&&value&&(!accept||accept(value)))found=value}catch(_){}});return found}
function apiMatches(api){return !!(api&&api.version===REQUIRED_BCD_VERSION&&api.revision===REQUIRED_BCD_REVISION&&api.sourceIdentity===REQUIRED_BCD_SOURCE_IDENTITY)}
function anyApi(){return findApi(BCD_API)}
function currentApi(){return findApi(BCD_API,apiMatches)}
function currentView(){return findApi(VIEW_API,api=>api&&api.version===REQUIRED_VIEW_VERSION)}
function receipt(reason,status,extra){const expected=extra&&extra.evaluation_id||null,live=liveReceipt(expected),exact=currentApi(),any=anyApi();LAST_BOOT_RECEIPT=Object.assign({type:'PMP_CURRENT_BCD_DIAGNOSTICS_BOOTSTRAP_V1',version:V,classification_revision:CLASSIFICATION_REVISION,publication_revision:PUBLICATION_REVISION,owner:'diagnostics_owner',at:now(),reason:reason||'boot',status,required_version:REQUIRED_BCD_VERSION,required_revision:REQUIRED_BCD_REVISION,required_source_identity:REQUIRED_BCD_SOURCE_IDENTITY,versioned_source:VERSIONED_BCD_SRC,observed_any_api_version:any&&any.version||null,observed_api_version:exact&&exact.version||null,observed_api_revision:exact&&exact.revision||any&&any.revision||null,observed_api_source_identity:exact&&exact.sourceIdentity||any&&any.sourceIdentity||null,observed_receipt_version:live&&live.version||null,observed_receipt_revision:live&&live.revision||null,observed_receipt_source_identity:live&&live.source_identity||null,observed_receipt_evaluation_id:live&&live.evaluation_id||null,complete_sections:REQUIRED_SECTIONS.filter(key=>live&&live[key]),transactional:true,bounded_publication:true,quota_resilient_live_publication:true,fresh_evaluation_required:true,boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}},extra||{});store(BOOT_RECEIPT_KEY,LAST_BOOT_RECEIPT);return LAST_BOOT_RECEIPT}
function viewReceipt(reason,status,extra){const api=currentView();return store(VIEW_RECEIPT_KEY,Object.assign({type:'PMP_CURRENT_DIAGNOSTICS_VIEW_BOOTSTRAP_V1',version:VIEW_BOOT_VERSION,owner:'diagnostics_owner',at:now(),reason:reason||'boot',status,required_version:REQUIRED_VIEW_VERSION,current_source:CURRENT_VIEW_SRC,observed_version:api&&api.version||null,exact_version:!!(api&&api.version===REQUIRED_VIEW_VERSION),boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}},extra||{}))}
function loadScript(src){return new Promise(resolve=>{try{const s=document.createElement('script');s.async=false;s.src=src;s.onload=()=>resolve({status:'LOADED'});s.onerror=()=>resolve({status:'LOAD_ERROR'});(document.head||document.documentElement).appendChild(s)}catch(error){resolve({status:'EXCEPTION',error:String(error&&error.message||error)})}})}
function loadVersionedScript(){const api=currentApi();if(apiMatches(api))return Promise.resolve({status:'ALREADY_LOADED'});return loadScript(VERSIONED_BCD_SRC+'?fresh=fresh-evaluation-source-identity-20260825A-'+Date.now())}
async function runAndValidate(api,reason,previous){const evaluationId=nextEvaluationId();try{if(!apiMatches(api)||typeof api.run!=='function'){restore(previous);return receipt(reason,'API_SOURCE_IDENTITY_MISMATCH',{evaluation_id:evaluationId,rollback_applied:true})}const rawProduced=await api.run({reason:reason||'transactional_bcd_bootstrap',evaluation_id:evaluationId});if(!completeReceipt(rawProduced,evaluationId)){restore(previous);return receipt(reason,'NEW_EVALUATION_INCOMPLETE',{evaluation_id:evaluationId,rollback_applied:true,produced_version:rawProduced&&rawProduced.version||null,produced_revision:rawProduced&&rawProduced.revision||null,produced_source_identity:rawProduced&&rawProduced.source_identity||null,produced_evaluation_id:rawProduced&&rawProduced.evaluation_id||null})}const classified=classifyPersistedBugBacklog(rawProduced),produced=classified.report;let publication=publishBounded(produced,evaluationId);if(!publication.ok)publication=publishBounded(produced,evaluationId);const live=publication.receipt;if(!publication.ok||!completeReceipt(live,evaluationId)){restore(previous);return receipt(reason,'RECEIPT_PUBLICATION_FAILED',{evaluation_id:evaluationId,rollback_applied:true,produced_version:produced.version,publication})}return receipt(reason,'PASS',{evaluation_id:evaluationId,rollback_applied:false,replaced_previous_version:previous&&previous.version||null,replaced_previous_evaluation_id:previous&&previous.evaluation_id||null,publication_mode:publication.mode,publication_persistence_status:publication.persistence_status,persistence_warning:publication.persistence_status==='QUOTA_UNAVAILABLE'?publication.persistence_error||'Storage quota unavailable':null,published_bytes:publication.bytes,source_evaluation_status:rawProduced.status,source_evaluation_at:rawProduced.at,final_evaluation_status:produced.status,persisted_bug_backlog_classification_applied:classified.applied,live_receipt_available:true,runtime_context_document_count:rawProduced.runtime_context&&Array.isArray(rawProduced.runtime_context.accessible_documents)?rawProduced.runtime_context.accessible_documents.length:null})}catch(error){restore(previous);return receipt(reason,'RUN_ERROR',{evaluation_id:evaluationId,error:String(error&&error.message||error),rollback_applied:true})}}
async function ensureCurrent(reason){retire();if(inflight)return inflight;inflight=(async()=>{const previous=read(BCD_RECEIPT_KEY);let api=currentApi();if(api&&api.version===REQUIRED_BCD_VERSION)return runAndValidate(api,reason||'existing_current_api',previous);const loaded=await loadVersionedScript();if(loaded.status!=='LOADED'&&loaded.status!=='ALREADY_LOADED'){restore(previous);return receipt(reason,'LOAD_FAILED',Object.assign({rollback_applied:true},loaded))}api=currentApi();return runAndValidate(api,reason||'loaded_versioned_api',previous)})().finally(()=>{inflight=null});return inflight}
async function ensureCurrentView(reason){retire();if(viewInflight)return viewInflight;viewInflight=(async()=>{let api=currentView();if(api&&api.version===REQUIRED_VIEW_VERSION){try{if(typeof api.install==='function')api.install()}catch(_){}return viewReceipt(reason,'PASS',{load_status:'ALREADY_CURRENT'})}const previous=api&&api.version||null;const loaded=await loadScript(CURRENT_VIEW_SRC+'?fresh=exact-diagnostics-view-20260803B-'+Date.now());if(loaded.status!=='LOADED')return viewReceipt(reason,'LOAD_FAILED',{load_status:loaded.status,error:loaded.error||null,previous_version:previous});api=currentView();if(!api||api.version!==REQUIRED_VIEW_VERSION)return viewReceipt(reason,'VERSION_MISMATCH',{load_status:loaded.status,previous_version:previous});try{if(typeof api.install==='function')api.install()}catch(error){return viewReceipt(reason,'INSTALL_ERROR',{error:String(error&&error.message||error),previous_version:previous})}return viewReceipt(reason,'PASS',{load_status:loaded.status,replaced_previous_version:previous})})().finally(()=>{viewInflight=null});return viewInflight}
window.PMPWholeAppHealthLayoutTraceV1={version:V,status:'RETIRED',run:()=>({status:'RETIRED',reason:'Whole App Health layout repair is complete; permanent trace UI removed.'}),rule:'Invisible compatibility bootstrap only. Creates no trace controls or observers.'};
window.PMPCurrentBCDDiagnosticsBootstrapV1={version:V,classificationRevision:CLASSIFICATION_REVISION,publicationRevision:PUBLICATION_REVISION,requiredVersion:REQUIRED_BCD_VERSION,requiredRevision:REQUIRED_BCD_REVISION,requiredSourceIdentity:REQUIRED_BCD_SOURCE_IDENTITY,versionedSource:VERSIONED_BCD_SRC,run:ensureCurrent,last:()=>LAST_BOOT_RECEIPT||read(BOOT_RECEIPT_KEY),currentReceipt:()=>liveReceipt()};
window.PMPCurrentDiagnosticsViewBootstrapV1={version:VIEW_BOOT_VERSION,requiredVersion:REQUIRED_VIEW_VERSION,currentSource:CURRENT_VIEW_SRC,run:ensureCurrentView,last:()=>read(VIEW_RECEIPT_KEY)};
try{T().PMPWholeAppHealthLayoutTraceV1=window.PMPWholeAppHealthLayoutTraceV1;T().PMPCurrentBCDDiagnosticsBootstrapV1=window.PMPCurrentBCDDiagnosticsBootstrapV1;T().PMPCurrentDiagnosticsViewBootstrapV1=window.PMPCurrentDiagnosticsViewBootstrapV1}catch(_){}
retire();[0,500,1500,3500,7000].forEach(ms=>setTimeout(()=>{ensureCurrent('boot_'+ms);ensureCurrentView('boot_'+ms)},ms));window.addEventListener('pageshow',()=>{ensureCurrent('pageshow');ensureCurrentView('pageshow')});document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'){ensureCurrent('visible_resume');ensureCurrentView('visible_resume')}});
})();