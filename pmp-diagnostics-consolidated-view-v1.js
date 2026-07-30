(()=>{
'use strict';
const V='1.0.1-tab-open-repair-20260729A';
const OWNER='diagnostics_owner';
const SCREEN_ID='pmpDiagnosticsScreenV1';
const CARDS=[
  ['whole_app','Whole App Health','all accessible app frames, stored evidence, runtime structure, visual integrity, errors and confidence'],
  ['app_orchestrator_system','App Orchestrator System','App Orchestrator, owners, helpers, protected resources, writers, enforcement, proof and transfer'],
  ['full_report','Copy Full Diagnostic Report','copy the complete confidence-labelled Diagnostics Owner report']
];
let ORIGINAL_RENDER_HOME=null;
function T(){try{return window.top||window}catch(_){return window}}
function esc(value){return String(value==null?'':value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function api(){return T().PMPDiagnosticsOwnerV1||window.PMPDiagnosticsOwnerV1||null}
function docs(){
  const out=[],seen=[];
  function walk(w,depth){if(!w||depth>10||seen.includes(w))return;seen.push(w);try{out.push({window:w,document:w.document,path:String(w.location&&w.location.pathname||''),title:String(w.document&&w.document.title||'')});w.document.querySelectorAll('iframe,frame').forEach(frame=>{try{walk(frame.contentWindow,depth+1)}catch(_){}})}catch(_){}}
  walk(T(),0);return out;
}
function readRegistry(){try{const runtime=T().PMPAppOrchestratorOwnershipRuntimeV1||window.PMPAppOrchestratorOwnershipRuntimeV1;const registry=runtime&&typeof runtime.registry==='function'?runtime.registry():null;return registry&&Array.isArray(registry.resources)?{type:registry.type||'PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1',version:registry.version||null,root_authority:registry.root_authority||null,rules:registry.rules||{},resource_count:registry.resources.length,resources:registry.resources}:{status:'REGISTRY_RUNTIME_NOT_AVAILABLE'}}catch(error){return{status:'REGISTRY_READ_ERROR',error:String(error&&error.message||error)}}}
function current(){const diagnostics=api();return diagnostics&&typeof diagnostics.currentReport==='function'?diagnostics.currentReport('consolidated_view'):{status:'DIAGNOSTICS_OWNER_NOT_READY'}}
function wholeAppHealth(report){
  const accessible=docs().map(ctx=>({path:ctx.path,title:ctx.title,screen_count:ctx.document.querySelectorAll('.screen').length,script_count:ctx.document.querySelectorAll('script[src]').length,frame_count:ctx.document.querySelectorAll('iframe,frame').length}));
  return{
    type:'PMP_WHOLE_APP_HEALTH_VIEW_V1',version:V,owner:OWNER,at:new Date().toISOString(),
    scope:'all currently accessible same-origin app documents plus stored whole-app evidence for non-rendered systems',
    accessible_documents:accessible,
    app_orchestrator:report.reports&&report.reports.app_orchestrator,
    ownership_runtime:report.reports&&report.reports.ownership_runtime,
    routes:report.reports&&report.reports.reload_owner,
    active_path:{canonical:report.reports&&report.reports.active_path,bounded:report.reports&&report.reports.active_path_bounded},
    mounts:{registry:report.reports&&report.reports.mount_registry,lifecycle:report.reports&&report.reports.mount_lifecycle},
    ownership:{section_owners:report.reports&&report.reports.section_owners,helpers:report.reports&&report.reports.helpers,bank_owner_split:report.reports&&report.reports.bank_owner_split},
    runtime_structure:{panel_order:report.reports&&report.reports.panel_order,note:'When a visual surface is not rendered, stored structural evidence is retained and the visual-only portion remains explicitly unevaluated.'},
    visual_integrity:{duplicate_panels:report.reports&&report.reports.duplicate_panels,flicker_recorder:report.reports&&report.reports.flicker_recorder},
    errors_and_history:report.reports&&report.reports.error_log,
    confidence:report.diagnostic_confidence||{},summary:report.summary||{},
    boundaries:{read_only:true,ownership_changes:false,helper_changes:false,route_changes:false,dom_repair:false,storage_migration:false,persisted_user_data_write:false}
  };
}
function orchestratorSystem(report){
  const registry=readRegistry();
  const runtime=report.reports&&report.reports.ownership_runtime;
  return{
    type:'PMP_APP_ORCHESTRATOR_SYSTEM_VIEW_V1',version:V,owner:OWNER,at:new Date().toISOString(),
    authority_layers:{
      app_orchestrator:{role:'top coordinator and boundary observer',evidence:report.reports&&report.reports.app_orchestrator},
      owners:{role:'one declared authority per governed area',evidence:report.reports&&report.reports.section_owners},
      helpers:{role:'read, inspect, request, or present under an owner; no independent owner-state commit',evidence:report.reports&&report.reports.helpers}
    },
    protected_resources:registry,
    canonical_writers:registry.resources?registry.resources.map(row=>({resource_id:row.id,owner:row.owner,writer:row.writer,presentation_helper:row.presentation_helper||null,readers:row.readers||row.legacy_readers||[],requesters:row.requesters||[],schema:row.schema||null,frame_scope:row.frame_scope||null,handoff:row.handoff||null})):[],
    runtime_enforcement:{ownership_runtime:runtime,rule:'Unknown resources and undeclared actors fail closed. Helpers do not receive owner write authority.'},
    proof_and_maintenance:{active_path:{canonical:report.reports&&report.reports.active_path,bounded:report.reports&&report.reports.active_path_bounded},mount_registry:report.reports&&report.reports.mount_registry,route_evidence:report.reports&&report.reports.reload_owner,duplicate_and_conflict_check:report.reports&&report.reports.duplicate_panels,error_and_bug_watch:report.reports&&report.reports.error_log,required_gates:['App Orchestrator Ownership Maintenance','Runtime Integrity Seal','Permanent No-Blind-Flying Gate']},
    transfer:{copy_app_orchestrator_system_report:true,copy_new_chat_safe_handoff:true,copy_full_diagnostic_report:true},
    boundaries:{read_only:true,ownership_changes:false,helper_changes:false,registry_write:false,authority_takeover:false,persisted_user_data_write:false}
  };
}
function screen(documentValue){return documentValue.getElementById(SCREEN_ID)}
function ensureScreen(windowValue,documentValue){
  let host=screen(documentValue);
  if(!host&&typeof ORIGINAL_RENDER_HOME==='function'){
    ORIGINAL_RENDER_HOME(windowValue,documentValue);
    host=screen(documentValue);
  }
  if(host){
    try{Array.from(documentValue.querySelectorAll('.screen')).forEach(node=>node.classList.remove('on'));host.classList.add('on');host.scrollTop=0}catch(_){}
  }
  return host;
}
function card(row){return '<button type="button" class="pmpDiagCard" data-diag-consolidated="'+esc(row[0])+'"><span class="pmpDiagIcon">▣</span><span><b>'+esc(row[1])+'</b><small>'+esc(row[2])+'</small></span><span class="pmpDiagChevron">›</span></button>'}
function copyText(text){try{if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text);return'copied'}}catch(_){}try{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok?'copied':'not_confirmed'}catch(_){return'not_confirmed'}}
async function handoff(button){button.textContent='Building safe handoff...';const handoffApi=T().PMPNewChatSafeHandoffV1||window.PMPNewChatSafeHandoffV1;const result=handoffApi&&typeof handoffApi.run==='function'?await handoffApi.run():{status:'HANDOFF_API_NOT_READY'};button.textContent=result.mode==='zip'?'Safe handoff ZIP downloaded':((result.mode==='clipboard'||result.mode==='copy')&&result.status==='PASS'?'Safe handoff copied':'Safe handoff unavailable')}
function renderHome(windowValue,documentValue){const host=ensureScreen(windowValue,documentValue);if(!host)return false;host.innerHTML='<h1 class="pmpDiagTitle">Diagnostics</h1><p class="pmpDiagSub">Whole-app, read-only diagnostics. Existing owners, helpers, writers and evidence are displayed without changing their authority.</p><div class="pmpDiagGrid">'+CARDS.map(card).join('')+'</div>';host.querySelectorAll('[data-diag-consolidated]').forEach(button=>button.onclick=()=>renderDetail(windowValue,documentValue,button.getAttribute('data-diag-consolidated')));return true}
function renderDetail(windowValue,documentValue,id){const host=ensureScreen(windowValue,documentValue);if(!host)return false;const report=current();let title='Diagnostics',shown=report,controls='';if(id==='whole_app'){title='Whole App Health';shown=wholeAppHealth(report)}else if(id==='app_orchestrator_system'){title='App Orchestrator System';shown=orchestratorSystem(report);controls='<button type="button" class="pmpDiagAction" id="pmpDiagCopyOrchestratorSystem">Copy App Orchestrator System Report</button><button type="button" class="pmpDiagAction" id="pmpDiagSafeHandoff">Copy New Chat Safe Handoff</button>'}else if(id==='full_report'){title='Copy Full Diagnostic Report';controls='<button type="button" class="pmpDiagAction" id="pmpDiagCopyFull">Copy Full Diagnostic Report</button>'}host.innerHTML='<button type="button" class="pmpDiagBack" id="pmpDiagBack">← Back to Diagnostics</button><h1 class="pmpDiagTitle">'+esc(title)+'</h1><p class="pmpDiagSub">Diagnostics Owner · consolidated proof-labelled read-only evidence</p><div class="pmpDiagQuick">'+controls+'</div><pre>'+esc(JSON.stringify(shown,null,2))+'</pre>';documentValue.getElementById('pmpDiagBack').onclick=()=>renderHome(windowValue,documentValue);const copySystem=documentValue.getElementById('pmpDiagCopyOrchestratorSystem');if(copySystem)copySystem.onclick=()=>{copySystem.textContent=copyText(JSON.stringify(orchestratorSystem(current()),null,2))==='copied'?'Copied':'Report ready'};const handoffButton=documentValue.getElementById('pmpDiagSafeHandoff');if(handoffButton)handoffButton.onclick=()=>handoff(handoffButton);const full=documentValue.getElementById('pmpDiagCopyFull');if(full)full.onclick=()=>{full.textContent=copyText(JSON.stringify(current(),null,2))==='copied'?'Copied':'Report ready'};return true}
function install(){const diagnostics=api();if(!diagnostics)return false;if(!diagnostics.__pmpConsolidatedOriginalRenderHome&&diagnostics.renderHome!==renderHome)diagnostics.__pmpConsolidatedOriginalRenderHome=diagnostics.renderHome;ORIGINAL_RENDER_HOME=diagnostics.__pmpConsolidatedOriginalRenderHome||ORIGINAL_RENDER_HOME;if(typeof ORIGINAL_RENDER_HOME!=='function')return false;diagnostics.renderHome=renderHome;diagnostics.renderDetail=renderDetail;diagnostics.renderWholeAppHealth=(w,d)=>renderDetail(w,d,'whole_app');diagnostics.renderAppOrchestratorSystem=(w,d)=>renderDetail(w,d,'app_orchestrator_system');docs().forEach(ctx=>{const host=screen(ctx.document);if(host&&host.classList.contains('on'))renderHome(ctx.window,ctx.document)});return true}
const publicApi={version:V,owner:OWNER,install,renderHome,renderDetail,wholeAppHealth:()=>wholeAppHealth(current()),appOrchestratorSystem:()=>orchestratorSystem(current()),rule:'Presentation and reporting consolidation only. It creates no owner or helper, changes no registry entry, and grants no authority.'};
window.PMPDiagnosticsConsolidatedViewV1=publicApi;try{T().PMPDiagnosticsConsolidatedViewV1=publicApi}catch(_){}
[0,100,300,900,2000,5000].forEach(delay=>setTimeout(install,delay));
})();
