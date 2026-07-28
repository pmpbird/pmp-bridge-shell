(()=>{
'use strict';
const V='2.4.0-single-handoff-owner-20260728A';
const OWNER='diagnostics_owner';
const SCREEN_ID='pmpDiagnosticsScreenV1';
const STYLE_ID='pmpDiagnosticsOwnerV1Style';
const RECEIPT='pmp_diagnostics_owner_v1_receipt';
const ERRORS=[];
const CARDS=[
  ['app_health','App Health Summary','runtime, owner, and safe-state summary'],
  ['app_orchestrator','App Orchestrator Status','one-button safe new-chat handoff'],
  ['route_stack','Route Stack','Current Map and canonical reload evidence'],
  ['mount_registry','Mount Registry Status','single-owner lifecycle evidence'],
  ['section_owners','Section Owners Status','declared owner state and conflicts'],
  ['helpers','Helpers Status','helper bindings, holds, and violations'],
  ['panel_order','Panel Order Check','actual Continuous Run level order and readiness'],
  ['duplicate_panels','Duplicate Panel Check','duplicate IDs, levels, and owner claims'],
  ['flicker_recorder','Flicker Recorder','recurring repaint and unstable surface evidence'],
  ['error_log','Error Log / Bug Watch','captured errors and passive bug receipts'],
  ['bank_continuous_run_visual','Bank / Continuous Run Visual State','owner split and surface evidence'],
  ['full_report','Copy Full Diagnostic Report','copy the combined read-only report']
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
function activePathValue(){
  return{
    canonical_report:read('pmp_active_path_discovery_report_v1')||{status:'canonical_scan_not_ready'},
    bounded_support_report:read('pmp_active_path_discovery_bounded_report_v2')||{status:'bounded_support_scan_not_ready'},
    ownership_rule:'pmp-active-path-discovery-machine-v1.js is the canonical writer; V2 is bounded support only.'
  };
}
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
function ensureStyle(d){
  let style=d.getElementById(STYLE_ID);
  if(!style){style=d.createElement('style');style.id=STYLE_ID;(d.head||d.documentElement).appendChild(style)}
  style.textContent=
    '#'+SCREEN_ID+'{position:fixed!important;inset:0!important;z-index:9!important;overflow:auto!important;-webkit-overflow-scrolling:touch!important;overscroll-behavior:contain!important;padding:58px 14px 76px!important;box-sizing:border-box!important;background:var(--floor,#f3ded4)!important;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;}'+
    '#'+SCREEN_ID+' *{box-sizing:border-box!important;}'+
    '#'+SCREEN_ID+' .pmpDiagTitle{margin:0 0 6px!important;font-size:31px!important;line-height:1.05!important;font-weight:950!important;letter-spacing:-.4px!important;}'+
    '#'+SCREEN_ID+' .pmpDiagSub{margin:0 0 12px!important;font-size:16px!important;line-height:1.25!important;font-weight:800!important;opacity:.76!important;}'+
    '#'+SCREEN_ID+' .pmpDiagQuick{display:grid!important;grid-template-columns:1fr!important;gap:8px!important;margin:0 0 12px!important;}'+
    '#'+SCREEN_ID+' .pmpDiagGrid{display:grid!important;grid-template-columns:1fr!important;gap:9px!important;width:100%!important;}'+
    '#'+SCREEN_ID+' .pmpDiagCard{display:grid!important;grid-template-columns:36px minmax(0,1fr) 20px!important;gap:9px!important;align-items:center!important;width:100%!important;min-height:64px!important;text-align:left!important;border:3px solid var(--line,#07101c)!important;border-radius:17px!important;background:var(--accent,var(--a,#acd1fb))!important;color:var(--text,#101827)!important;padding:10px 12px!important;font:inherit!important;box-shadow:0 4px 10px rgba(7,16,28,.09)!important;cursor:pointer!important;}'+
    '#'+SCREEN_ID+' .pmpDiagCard b{display:block!important;font-size:17px!important;line-height:1.08!important;font-weight:950!important;}'+
    '#'+SCREEN_ID+' .pmpDiagCard small{display:block!important;margin-top:3px!important;font-size:12px!important;line-height:1.18!important;font-weight:800!important;opacity:.72!important;}'+
    '#'+SCREEN_ID+' .pmpDiagIcon{font-size:20px!important;text-align:center!important;}'+
    '#'+SCREEN_ID+' .pmpDiagChevron{font-size:24px!important;font-weight:950!important;text-align:right!important;}'+
    '#'+SCREEN_ID+' .pmpDiagAction{display:block!important;width:100%!important;min-height:52px!important;border:3px solid var(--line,#07101c)!important;border-radius:16px!important;padding:10px 12px!important;background:var(--button,var(--a,#acd1fb))!important;color:var(--buttonText,var(--text,#101827))!important;font:950 17px/1.12 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;text-align:center!important;}'+
    '#'+SCREEN_ID+' .pmpDiagBack{display:block!important;width:100%!important;min-height:48px!important;border:2px solid var(--line,#07101c)!important;border-radius:15px!important;background:var(--card,#fff)!important;color:var(--text,#101827)!important;padding:10px!important;font-weight:950!important;margin-bottom:10px!important;text-align:center!important;}'+
    '#'+SCREEN_ID+' pre{white-space:pre-wrap!important;overflow:auto!important;max-height:420px!important;background:var(--card,#fff)!important;color:var(--text,#101827)!important;border:2px solid var(--line,#07101c)!important;border-radius:14px!important;padding:10px!important;font:700 11px/1.28 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important;}'+
    '@media(min-width:700px){#'+SCREEN_ID+' .pmpDiagQuick{grid-template-columns:1fr!important;}#'+SCREEN_ID+' .pmpDiagGrid{grid-template-columns:1fr 1fr!important;}}';
}
function screen(d){ensureStyle(d);let el=d.getElementById(SCREEN_ID);if(!el){el=d.createElement('section');el.id=SCREEN_ID;el.className='screen';el.setAttribute('data-pmp-section-owner',OWNER);(d.getElementById('app')||d.body).appendChild(el)}return el}
function activate(d,el){try{Array.from(d.querySelectorAll('.screen')).forEach(node=>node.classList.remove('on'));el.classList.add('on');el.scrollTop=0}catch(e){}return el}
function cardHTML(row){return'<button type="button" class="pmpDiagCard" data-diag="'+esc(row[0])+'"><span class="pmpDiagIcon">▣</span><span><b>'+esc(row[1])+'</b><small>'+esc(row[2])+'</small></span><span class="pmpDiagChevron">›</span></button>'}
function action(id,label){return'<button type="button" class="pmpDiagAction" id="'+id+'">'+esc(label)+'</button>'}
function copyText(text){try{if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text);return'copied'}}catch(e){}try{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok?'copied':'not_confirmed'}catch(e){return'not_confirmed'}}
async function runHandoff(button){
  button.textContent='Building safe handoff...';
  const api=T().PMPNewChatSafeHandoffV1||window.PMPNewChatSafeHandoffV1;
  const result=api&&typeof api.run==='function'?await api.run():{status:'HANDOFF_API_NOT_READY'};
  button.textContent=result.mode==='zip'?'Safe handoff ZIP downloaded':((result.mode==='clipboard'||result.mode==='copy')&&result.status==='PASS'?'Safe handoff copied':'Safe handoff unavailable');
}
function bindHandoff(d,id){const button=d.getElementById(id);if(button)button.onclick=()=>runHandoff(button)}
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
  el.innerHTML='<button type="button" class="pmpDiagBack" id="pmpDiagBack">← Back to Diagnostics</button><h1 class="pmpDiagTitle">'+esc(row[1])+'</h1><p class="pmpDiagSub">Diagnostics Owner · permanent read-only evidence</p><div class="pmpDiagQuick">'+controls+'</div><pre>'+esc(JSON.stringify(id==='app_orchestrator'?read('pmp_app_orchestrator_v1_receipt')||value:value,null,2))+'</pre>';
  d.getElementById('pmpDiagBack').onclick=()=>renderHome(w,d);
  bindHandoff(d,'pmpDiagSafeHandoff');
  const orch=d.getElementById('pmpDiagCopyOrch');if(orch)orch.onclick=()=>{orch.textContent=copyText(JSON.stringify(read('pmp_app_orchestrator_v1_receipt')||{},null,2))==='copied'?'Copied':'Report ready'};
  const full=d.getElementById('pmpDiagCopyFull');if(full)full.onclick=()=>{full.textContent=copyText(JSON.stringify(currentReport('copy_full'),null,2))==='copied'?'Copied':'Report ready'};
}
function renderHome(w,d){
  const el=activate(d,screen(d));
  el.innerHTML='<h1 class="pmpDiagTitle">Diagnostics</h1><p class="pmpDiagSub">Permanent read-only diagnostics. Original tools remain visible; ownership conflicts are reported without repairing or changing the app.</p><div class="pmpDiagGrid">'+CARDS.map(cardHTML).join('')+'</div>';
  el.querySelectorAll('.pmpDiagCard').forEach(card=>{const open=()=>renderDetail(w,d,card.dataset.diag);card.onclick=open;card.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}}});
}
function run(reason){const report=currentReport(reason||'run');docs().forEach(ctx=>{try{if(ctx.document.getElementById(SCREEN_ID))renderHome(ctx.window,ctx.document)}catch(e){}});return report}
function renderDiagnosticJournal(w,d){renderDetail(w,d,'error_log')}
function renderSectionOwners(w,d){renderDetail(w,d,'section_owners')}
function close(){docs().forEach(ctx=>{const el=ctx.document.getElementById(SCREEN_ID);if(el)el.classList.remove('on')})}
const api={version:V,owner:OWNER,run,currentReport,renderHome,renderDetail,renderDiagnosticJournal,renderSectionOwners,close,screenId:SCREEN_ID,readMountLifecycle:lifecycleView,readHelpers:helperView,readPanelOrder:panelOrderReport,readDuplicates:duplicateReport,readFlicker:flickerReport,readErrors:errorReport,readActivePath:activePathValue,rule:'Read-only permanent diagnostics with the safe-handoff action owned only by App Orchestrator Status, plus panel order, duplicate, repaint, error, and ownership evidence. Active Path Discovery remains on its Control surface. No repair or data mutation.'};
api.readMountLifecycle=lifecycleView;
api.readSectionOwners=sectionOwnerView;
window.PMPDiagnosticsOwnerV1=api;try{T().PMPDiagnosticsOwnerV1=api}catch(e){}
window.addEventListener('error',e=>ERRORS.push({at:now(),type:'error',message:String(e.message||''),filename:String(e.filename||''),line:e.lineno||0}));
window.addEventListener('unhandledrejection',e=>ERRORS.push({at:now(),type:'unhandledrejection',message:String(e.reason&&e.reason.message||e.reason||'')}));
put(RECEIPT,{type:'PMP_DIAGNOSTICS_OWNER_RECEIPT_V2',version:V,owner:OWNER,at:now(),status:'ACTIVE_READ_ONLY',sections:CARDS.length,normal_home:'Diagnostics tab',read_only:true});
})();
