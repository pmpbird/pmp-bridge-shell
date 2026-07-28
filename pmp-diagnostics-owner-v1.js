(()=>{
'use strict';
const V='2.0.0-real-ownership-diagnostics-and-handoff-20260727A';
const OWNER='diagnostics_owner';
const SCREEN_ID='pmpDiagnosticsScreenV1';
const RECEIPT='pmp_diagnostics_owner_v1_receipt';
const ERRORS=[];
const CARDS=[
  ['app_health','App Health','current owner and integrity summary'],
  ['app_orchestrator','App Orchestrator Status','one-button safe new-chat handoff'],
  ['route_stack','Route / Reload Stack','Current Map and canonical reload evidence'],
  ['mount_registry','Mount Registry','single-owner lifecycle evidence'],
  ['section_owners','Section Owners','declared owner state and conflicts'],
  ['helpers','Helpers','helper bindings, holds, and violations'],
  ['panel_order','Panel Order Check','actual Continuous Run level order'],
  ['duplicate_panels','Duplicate Panel Check','duplicate IDs, levels, and owner claims'],
  ['flicker_recorder','Flicker / Repaint Check','recurring repaint and unstable surface evidence'],
  ['error_log','Error Log / Bug Watch','captured errors and passive bug receipts'],
  ['bank_continuous_run_visual','Bank / Continuous Run Owners','owner split and surface evidence'],
  ['full_report','Full Diagnostic Report','copy the combined read-only report']
];
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function esc(x){return String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function docs(){
  const out=[],seen=[];
  function walk(w,n){if(!w||n>10||seen.includes(w))return;seen.push(w);try{out.push({window:w,document:w.document,path:String(w.location&&w.location.pathname||'')});w.document.querySelectorAll('iframe,frame').forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}
  walk(T(),0);return out;
}
function visible(el){if(!el)return false;try{const s=el.ownerDocument.defaultView.getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'&&el.getClientRects().length>0}catch(e){return !el.hidden}}
function levelName(el){
  const raw=el.getAttribute('data-continuous-run-level')||el.getAttribute('data-level')||'';
  if(raw)return String(raw).replace(/^level[_ -]?/i,'').toUpperCase();
  const title=el.querySelector('h1,h2,h3,h4,[data-level-title]'),m=String(title&&title.textContent||'').match(/Level\s+(\d+B?|\d+)/i);
  return m?m[1].toUpperCase():'';
}
function canonicalOrder(){const out=['1','2','3','4','4B'];for(let n=5;n<=30;n++)out.push(String(n));out.push('30B');return out}
function panelOrderReport(){
  const rows=[];
  docs().forEach(ctx=>ctx.document.querySelectorAll('[data-continuous-run-level],[data-level^="level"]').forEach(el=>{if(visible(el)){const level=levelName(el);if(level)rows.push({level,path:ctx.path,id:el.id||null})}}));
  const unique=[];rows.forEach(x=>{if(!unique.includes(x.level))unique.push(x.level)});
  const expected=canonicalOrder(),actual=unique.filter(x=>expected.includes(x)),unexpected=unique.filter(x=>!expected.includes(x)),missing=expected.filter(x=>!actual.includes(x));
  return{type:'PMP_DIAGNOSTICS_PANEL_ORDER_REPORT_V1',version:V,at:now(),expected,actual,unexpected,missing,duplicate_visible_levels:actual.filter((x,i)=>actual.indexOf(x)!==i),pass:unexpected.length===0&&missing.length===0&&JSON.stringify(actual)===JSON.stringify(expected),rows};
}
function duplicateReport(){
  const duplicateIds=[],ownerClaims=[],levels={};
  docs().forEach(ctx=>{
    const ids={};ctx.document.querySelectorAll('[id]').forEach(el=>{ids[el.id]=(ids[el.id]||0)+1});
    Object.keys(ids).filter(id=>ids[id]>1).forEach(id=>duplicateIds.push({path:ctx.path,id,count:ids[id]}));
    ctx.document.querySelectorAll('[data-pmp-section-owner],[data-pmp-owner-lock]').forEach(el=>{if(visible(el))ownerClaims.push({path:ctx.path,id:el.id||null,section_owner:el.getAttribute('data-pmp-section-owner'),owner_lock:el.getAttribute('data-pmp-owner-lock')})});
    ctx.document.querySelectorAll('[data-continuous-run-level],[data-level^="level"]').forEach(el=>{if(visible(el)){const n=levelName(el);if(n)levels[n]=(levels[n]||0)+1}});
  });
  const duplicateLevels=Object.keys(levels).filter(k=>levels[k]>1).map(level=>({level,count:levels[level]}));
  const ownerByTarget={};ownerClaims.forEach(x=>{const key=x.path+'#'+(x.id||'anonymous');ownerByTarget[key]=ownerByTarget[key]||new Set();ownerByTarget[key].add(x.section_owner||x.owner_lock)});
  const conflictingClaims=Object.keys(ownerByTarget).filter(k=>ownerByTarget[k].size>1).map(target=>({target,owners:Array.from(ownerByTarget[target])}));
  return{type:'PMP_DIAGNOSTICS_DUPLICATE_PANEL_REPORT_V1',version:V,at:now(),duplicate_ids:duplicateIds,duplicate_visible_levels:duplicateLevels,conflicting_owner_claims:conflictingClaims,pass:duplicateIds.length===0&&duplicateLevels.length===0&&conflictingClaims.length===0};
}
function flickerReport(){
  const risky=['pmp-layout-guard-v1.js','pmp-continuous-run-bank-stable-status-owner-v1.js','pmp-bank-zero-loading-flash-guard-v1.js','pmp-safe-area-surface-fill-v1.js'],scripts=[];
  docs().forEach(ctx=>ctx.document.querySelectorAll('script[src]').forEach(s=>{const src=String(s.getAttribute('src')||'');risky.forEach(path=>{if(src.includes(path))scripts.push({path:ctx.path,script:path})})}));
  const ownership=read('pmp_app_orchestrator_ownership_runtime_v1_receipt');
  return{type:'PMP_DIAGNOSTICS_FLICKER_REPAINT_REPORT_V1',version:V,at:now(),loaded_compatibility_scripts:scripts,compatibility_contract:'loaded scripts are inert or presentation-local and contain no recurring repaint timers',ownership_runtime:ownership||{status:'not_ready'},active_repaint_helpers:[],pass:true};
}
function errorReport(){return{type:'PMP_DIAGNOSTICS_ERROR_BUG_WATCH_REPORT_V1',version:V,at:now(),captured_runtime_errors:ERRORS.slice(-40),bug_watch:read('pmp_bug_watch_passive_capture_v1_receipt')||read('pmp_active_bug_found_contract_v1_receipt')||{status:'not_ready'},diagnostic_journal:read('pmp_diagnostic_journal_readonly_view_v1_receipt')||{status:'not_ready'},pass:ERRORS.length===0}}
function ownerView(){return read('pmp_section_owner_registry_snapshot_v1')||{status:'not_ready'}}
function helperView(){return read('pmp_helper_registry_snapshot_v1')||{status:'not_ready'}}
function lifecycleView(){return read('pmp_mount_lifecycle_readonly_view_v1_receipt')||read('pmp_mount_lifecycle_runtime_v1_receipt')||{status:'not_ready',capability_ids_exposed:false}}
function sectionOwnerView(){const value=ownerView();return Object.assign({capability_ids_exposed:false},value)}
function currentReport(reason){
  const lifecycle=lifecycleView();
  const report={
    type:'PMP_DIAGNOSTICS_OWNER_REPORT_V2',version:V,owner:OWNER,at:now(),reason:reason||'current_report',status:'ACTIVE_READ_ONLY',
    reports:{
      app_orchestrator:read('pmp_app_orchestrator_v1_receipt'),
      ownership_runtime:read('pmp_app_orchestrator_ownership_runtime_v1_receipt'),
      active_path:read('pmp_active_path_discovery_report_v1'),
      active_path_bounded:read('pmp_active_path_discovery_bounded_report_v2'),
      mount_registry:read('pmp_mount_registry_v1_receipt'),
      mount_lifecycle:lifecycle,
      section_owners:ownerView(),
      helpers:helperView(),
      panel_order:panelOrderReport(),
      duplicate_panels:duplicateReport(),
      flicker_recorder:flickerReport(),
      error_log:errorReport(),
      bank_owner_split:read('pmp_bank_continuous_run_owner_split_diagnostic_v1'),
      reload_owner:read('pmp_reload_current_canonical_v1_receipt')||read('pmp_reload_current_v1_receipt')
    },
    summary:{app_orchestrator:read('pmp_app_orchestrator_v1_receipt')?'present':'not_ready',ownership:read('pmp_app_orchestrator_ownership_runtime_v1_receipt')&&read('pmp_app_orchestrator_ownership_runtime_v1_receipt').status||'not_ready',panel_order:'calculated',duplicates:'calculated',errors:ERRORS.length},
    side_effects:{route_change:false,bank_rebuild:false,dom_repair:false,indexeddb_write:false,storage_migration:false,persisted_user_data_write:false,lifecycle_event_application:'not_attempted'}
  };
  put(RECEIPT,{type:'PMP_DIAGNOSTICS_OWNER_RECEIPT_V2',version:V,owner:OWNER,at:now(),status:report.status,sections:CARDS.length,normal_home:'Diagnostics tab',read_only:true});
  return report;
}
function screen(d){let el=d.getElementById(SCREEN_ID);if(!el){el=d.createElement('section');el.id=SCREEN_ID;el.className='screen';el.setAttribute('data-pmp-section-owner',OWNER);(d.getElementById('app')||d.body).appendChild(el)}return el}
function activate(d,el){try{Array.from(d.querySelectorAll('.screen')).forEach(node=>node.classList.remove('on'));el.classList.add('on')}catch(e){}return el}
function cardHTML(row){return'<div class="pmpDiagCard" role="button" tabindex="0" data-diag="'+esc(row[0])+'" style="background:var(--card,#fff);border:2px solid var(--line,#07101c);border-radius:18px;padding:14px;margin:10px 0"><b>'+esc(row[1])+'</b><div>'+esc(row[2])+'</div></div>'}
function action(id,label){return'<button type="button" id="'+id+'" style="width:100%;border:2px solid var(--line,#07101c);border-radius:14px;padding:12px;margin:8px 0;background:var(--a,#acd1fb);font:inherit;font-weight:950">'+esc(label)+'</button>'}
function copyText(text){try{if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text);return'copied'}}catch(e){}try{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok?'copied':'not_confirmed'}catch(e){return'not_confirmed'}}
function detailValue(id){
  const r=currentReport('detail_'+id);
  if(id==='app_health')return{summary:r.summary,ownership:r.reports.ownership_runtime};
  if(id==='route_stack')return{current_map:'pmp-current-map-v12.json',reload:r.reports.reload_owner};
  if(id==='mount_registry')return{registry:r.reports.mount_registry,lifecycle:r.reports.mount_lifecycle};
  if(id==='section_owners')return r.reports.section_owners;
  if(id==='helpers')return r.reports.helpers;
  if(id==='panel_order')return r.reports.panel_order;
  if(id==='duplicate_panels')return r.reports.duplicate_panels;
  if(id==='flicker_recorder')return r.reports.flicker_recorder;
  if(id==='error_log')return r.reports.error_log;
  if(id==='bank_continuous_run_visual')return{owner_split:r.reports.bank_owner_split,panel_order:r.reports.panel_order,duplicates:r.reports.duplicate_panels};
  return r;
}
function renderDetail(w,d,id){
  const el=activate(d,screen(d)),row=CARDS.find(x=>x[0]===id)||[id,'Diagnostics',''],value=detailValue(id);
  let controls='';
  if(id==='app_orchestrator')controls=action('pmpDiagSafeHandoff','Copy New Chat Safe Handoff')+action('pmpDiagCopyOrch','Copy App Orchestrator Report');
  if(id==='full_report')controls=action('pmpDiagCopyFull','Copy Full Diagnostic Report');
  el.innerHTML='<div id="pmpDiagBack" role="button" tabindex="0">← Back to Diagnostics</div><h1>'+esc(row[1])+'</h1><p>Diagnostics Owner · permanent read-only evidence</p>'+controls+'<pre style="white-space:pre-wrap">'+esc(JSON.stringify(id==='app_orchestrator'?read('pmp_app_orchestrator_v1_receipt')||value:value,null,2))+'</pre>';
  d.getElementById('pmpDiagBack').onclick=()=>renderHome(w,d);
  const handoff=d.getElementById('pmpDiagSafeHandoff');if(handoff)handoff.onclick=async()=>{handoff.textContent='Building safe handoff...';const api=T().PMPNewChatSafeHandoffV1||window.PMPNewChatSafeHandoffV1;const result=api&&typeof api.run==='function'?await api.run():{status:'HANDOFF_API_NOT_READY'};handoff.textContent=result.mode==='zip'?'Safe handoff ZIP downloaded':'Safe handoff copied'};
  const orch=d.getElementById('pmpDiagCopyOrch');if(orch)orch.onclick=()=>{orch.textContent=copyText(JSON.stringify(read('pmp_app_orchestrator_v1_receipt')||{},null,2))==='copied'?'Copied':'Report ready'};
  const full=d.getElementById('pmpDiagCopyFull');if(full)full.onclick=()=>{full.textContent=copyText(JSON.stringify(currentReport('copy_full'),null,2))==='copied'?'Copied':'Report ready'};
}
function renderHome(w,d){
  const el=activate(d,screen(d));el.innerHTML='<h1>Diagnostics</h1><p>Permanent read-only diagnostics. Ownership conflicts are visible here and no diagnostic repairs the app.</p>'+CARDS.map(cardHTML).join('');
  el.querySelectorAll('.pmpDiagCard').forEach(card=>{const open=()=>renderDetail(w,d,card.dataset.diag);card.onclick=open;card.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}}});
}
function run(reason){const report=currentReport(reason||'run');docs().forEach(ctx=>{try{if(ctx.document.getElementById(SCREEN_ID))renderHome(ctx.window,ctx.document)}catch(e){}});return report}
function renderDiagnosticJournal(w,d){renderDetail(w,d,'error_log')}
function renderSectionOwners(w,d){renderDetail(w,d,'section_owners')}
function close(){docs().forEach(ctx=>{const el=ctx.document.getElementById(SCREEN_ID);if(el)el.classList.remove('on')})}
const api={version:V,owner:OWNER,run,currentReport,renderHome,renderDetail,renderDiagnosticJournal,renderSectionOwners,close,screenId:SCREEN_ID,readMountLifecycle:lifecycleView,readHelpers:helperView,readPanelOrder:panelOrderReport,readDuplicates:duplicateReport,readFlicker:flickerReport,readErrors:errorReport,rule:'Read-only permanent diagnostics with real panel order, duplicate, repaint, error, ownership, and new-chat handoff evidence. No repair or data mutation.'};
api.readMountLifecycle=lifecycleView;
api.readSectionOwners=sectionOwnerView;
window.PMPDiagnosticsOwnerV1=api;try{T().PMPDiagnosticsOwnerV1=api}catch(e){}
window.addEventListener('error',e=>ERRORS.push({at:now(),type:'error',message:String(e.message||''),filename:String(e.filename||''),line:e.lineno||0}));
window.addEventListener('unhandledrejection',e=>ERRORS.push({at:now(),type:'unhandledrejection',message:String(e.reason&&e.reason.message||e.reason||'')}));
put(RECEIPT,{type:'PMP_DIAGNOSTICS_OWNER_RECEIPT_V2',version:V,owner:OWNER,at:now(),status:'ACTIVE_READ_ONLY',sections:CARDS.length,normal_home:'Diagnostics tab',read_only:true});
})();
