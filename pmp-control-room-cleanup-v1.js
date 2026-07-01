(function(){
'use strict';
const VERSION='1.3.0-bank-cr-diagnostic-sharpening';
const OWNER='pmp-control-room-cleanup-v1';
const BANK_CR_DIAG_VERSION='4B-bank-cr-diagnostics-sharpened-passive';
const DIAG_MAX=90;
const LEGAL_ORDER=[
  'run_state_summary',
  'lossless_slots_zip_import',
  'staging_transfer_store',
  'bank_project_registry',
  'run_state_detail',
  'bank_delete_tools',
  'level_1',
  'level_2',
  'level_3',
  'level_4',
  'level_4b',
  'levels_5_30',
  'level_30b'
];
const BANK_CR_TARGETS={
  bank_tab:{label:'Bank tab',selectors:['[data-tab="bank"]','#bank'],actual:[/^Bank$/i],status:[/Master Bank Inventory/i]},
  continuous_run_opener:{label:'Continuous Run opener',selectors:['[data-open-bank="continuous_run"]'],actual:[/^Continuous Run Bank$/i,/Continuous Run Bankrecords/i],status:[/Continuous Run Bank/i]},
  continuous_run_detail:{label:'Continuous Run detail',selectors:['[data-run-bank-tools]','[data-run-bank-detail]'],actual:[/^Continuous Run Bank$/i,/^Run State Summary$/i],status:[/Current Continuous Run status/i,/Transfer Store Slot Check/i]},
  run_state_summary:{label:'Run State Summary',selectors:['[data-cr-run-state-summary]','[data-bso-run-state]'],actual:[/^Run State Summary$/i],status:[/Run State Summary Status:/i,/Current Continuous Run status/i]},
  lossless_slots_zip_import:{label:'Lossless Slots ZIP Import',selectors:['[data-lossless-slots]','[data-zip-import]'],actual:[/^Lossless Slots ZIP Import$/i],status:[/Import Lossless Slots ZIP/i]},
  staging_transfer_store:{label:'Staging Transfer Store',selectors:['[data-transfer-store]','[data-staging-transfer-store]'],actual:[/^Staging Transfer Store \/ Verify Store$/i,/^Staging Transfer Store$/i],status:[/Store ItemVerify StoreCopy Manifest/i,/Transfer Store Slot Check/i]},
  bank_project_registry:{label:'Bank Project Registry',selectors:['[data-bank-project-registry]'],actual:[/^Bank Project Registry$/i],status:[/Bank Project Registry API/i]},
  run_state_detail:{label:'Run State Detail',selectors:['[data-run-state-detail]'],actual:[/^Run State Detail$/i],status:[/^Status: started/i,/Current work area:/i]},
  bank_delete_tools:{label:'Bank Delete Tools',selectors:['[data-bank-delete-tools]','[data-delete-tools]'],actual:[/^Bank Delete Tools$/i],status:[/Delete Selected/i,/Mode 1: Clean Test Data/i]},
  level_1:{label:'Level 1',selectors:['[data-level="1"]','[data-cr-level="1"]'],actual:[/^Level 1\b/i],status:[/Source ZIP: PRESENT Level 2/i]},
  level_2:{label:'Level 2',selectors:['[data-level="2"]','[data-cr-level="2"]'],actual:[/^Level 2\b/i],status:[/Level 2: PDFs/i]},
  level_3:{label:'Level 3',selectors:['[data-level="3"]','[data-cr-level="3"]'],actual:[/^Level 3\b/i],status:[/Level 3 Source Text Reader Records/i]},
  level_4:{label:'Level 4',selectors:['[data-level="4"]','[data-cr-level="4"]'],actual:[/^Level 4\b(?!B)/i],status:[/Level 4 ready/i]},
  level_4b:{label:'Level 4B',selectors:['[data-level="4b"]','[data-cr-level="4b"]'],actual:[/^Level 4B\b/i],status:[/Level 4B:.*READY/i,/Automatic Source Gate Hook Status/i]},
  levels_5_30:{label:'Levels 5-30',selectors:['[data-levels="5-30"]'],actual:[/^Level 5\b/i],status:[/Level 5 ready/i,/Level 6 ready/i,/Level 7\b/i,/Level 30 Final Seal/i]},
  level_30b:{label:'Level 30B',selectors:['[data-level="30b"]','[data-cr-level="30b"]'],actual:[/^Level 30B\b/i],status:[/Level 30B:.*ACTIVE/i,/Resident Startup Auto-Gate/i,/Resident Use Mode/i,/Request Intake/i]}
};
function textOf(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim();}
function now(){return new Date().toISOString();}
function safeJson(k,f){try{let v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function sameOriginWin(w){try{return !!(w&&w.document&&w.location)}catch(e){return false}}
function windowsFrom(w,a,seen,depth){
  a=a||[];seen=seen||[];depth=depth||0;
  if(!sameOriginWin(w)||depth>8||seen.indexOf(w)!==-1)return a;
  seen.push(w);a.push(w);
  try{if(w.parent&&w.parent!==w)windowsFrom(w.parent,a,seen,depth+1)}catch(e){}
  try{if(w.top&&w.top!==w)windowsFrom(w.top,a,seen,depth+1)}catch(e){}
  try{Array.from(w.document.querySelectorAll('iframe,frame')).forEach(function(f){try{windowsFrom(f.contentWindow,a,seen,depth+1)}catch(e){}})}catch(e){}
  return a;
}
function allDocuments(){
  const out=[];
  windowsFrom(window).forEach(function(w){
    try{out.push({w:w,d:w.document,url:String(w.location&&w.location.href||''),title:w.document.title||''})}catch(e){}
  });
  return out;
}
function findObject(name){
  const wins=windowsFrom(window);
  for(let i=0;i<wins.length;i++){try{if(wins[i][name])return wins[i][name]}catch(e){}}
  return null;
}
function isVisible(x,el){try{let cs=x.w.getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&cs.opacity!=='0'&&r.width>0&&r.height>0&&!el.hidden}catch(e){return false}}
function elementDocOrder(x,el){try{return Array.from(x.d.querySelectorAll('body *')).indexOf(el)}catch(e){return -1}}
function count(sel){
  let total=0,visible=0,first='';
  allDocuments().forEach(function(x){
    try{
      Array.from(x.d.querySelectorAll(sel)).forEach(function(el){
        total++;
        if(!first)first=textOf(el).slice(0,120);
        if(isVisible(x,el))visible++;
      });
    }catch(e){}
  });
  return {selector:sel,total:total,visible:visible,first_text:first};
}
function registryState(){
  const regObj=findObject('PMPMountRegistryV1');
  const orch=findObject('PMPAppOrchestratorV1');
  const reg=safeJson('pmp_mount_registry_v1',null);
  const snap=safeJson('pmp_mount_registry_live_snapshot_v1',null);
  const missing=safeJson('pmp_mount_registry_missing_expected_v1',[]);
  const receipt=safeJson('pmp_mount_registry_v1_receipt',null);
  return {regObj:regObj,orch:orch,reg:reg,snap:snap,missing:Array.isArray(missing)?missing:[],receipt:receipt};
}
function smokeProof(){
  const st=registryState();
  const docs=allDocuments().map(function(x){return {url:x.url,title:x.title}});
  const checks={
    mount_registry_loaded:!!st.regObj,
    mount_registry_version:st.regObj&&st.regObj.version||st.reg&&st.reg.version||null,
    app_orchestrator_loaded:!!st.orch,
    app_orchestrator_version:st.orch&&st.orch.version||null,
    registry_storage_present:!!st.reg,
    registry_snapshot_present:!!st.snap,
    bank_tab:count('[data-tab="bank"], #bank'),
    continuous_run_opener:count('[data-open-bank="continuous_run"]'),
    continuous_run_detail:count('[data-run-bank-tools], [data-run-bank-detail], [data-bso-run-state], [data-cr-run-state-summary]'),
    control_room:count('#control, [data-screen="control"], [data-tab="control"]'),
    blank_screen_warning:docs.length<2?'possible_low_document_count':'none_obvious'
  };
  return {
    type:'PMP_COPY_SMOKE_TEST_PROOF_V1',
    version:VERSION,
    owner:OWNER,
    built_at:now(),
    mode:'passive_copy_only',
    rule:'Copies proof only. No fixing, moving, deleting, Bank rebuild, route change, storage overwrite, or IndexedDB write.',
    current_href:String(location.href||''),
    documents:docs,
    checks:checks,
    registry_summary:{
      slot_count:st.reg&&Array.isArray(st.reg.slots)?st.reg.slots.length:null,
      atlas_bucket_count:st.reg&&Array.isArray(st.reg.atlas_buckets)?st.reg.atlas_buckets.length:null,
      storage_owner_count:st.reg&&Array.isArray(st.reg.storage_owners)?st.reg.storage_owners.length:null,
      indexeddb_owner_count:st.reg&&Array.isArray(st.reg.indexeddb_owners)?st.reg.indexeddb_owners.length:null,
      missing_expected_count:st.missing.length,
      receipt_version:st.receipt&&st.receipt.version||null,
      receipt_mode:st.receipt&&st.receipt.mode||null
    },
    missing_expected:st.missing,
    bank_cr_diagnostics_summary:bankCrSummary(),
    visual_user_check_required:'User still confirms whether the screen looked normal.'
  };
}
function uniqueElements(arr){
  const out=[];
  arr.forEach(function(el){if(el&&out.indexOf(el)===-1)out.push(el)});
  return out;
}
function baseHit(x,docIndex,el,evidenceType,matchedBy){
  let visible=isVisible(x,el);
  return {
    doc_index:docIndex,
    doc_title:x.title,
    doc_url:x.url,
    order:elementDocOrder(x,el),
    visible:visible,
    evidence_type:evidenceType,
    matched_by:matchedBy||'',
    tag:String(el.tagName||'').toLowerCase(),
    id:el.id||'',
    class_name:el.className&&String(el.className).slice(0,120)||'',
    text:textOf(el).slice(0,220)
  };
}
function selectorHits(x,cfg){
  let out=[];
  (cfg.selectors||[]).forEach(function(sel){
    try{Array.from(x.d.querySelectorAll(sel)).forEach(function(el){out.push({el:el,by:sel})})}catch(e){}
  });
  return out;
}
function headingHits(x,patterns){
  const out=[];
  try{
    Array.from(x.d.querySelectorAll('h1,h2,h3,summary')).forEach(function(el){
      const t=textOf(el);
      if(patterns.some(function(p){return p.test(t)}))out.push({el:el,by:'heading:'+t.slice(0,80)});
    });
  }catch(e){}
  return out;
}
function statusHits(x,patterns){
  const out=[];
  try{
    Array.from(x.d.querySelectorAll('pre,.note,.warn,.card,button,div')).forEach(function(el){
      const t=textOf(el);
      if(!t||t.length>2500)return;
      if(patterns.some(function(p){return p.test(t)}))out.push({el:el,by:'status:'+t.slice(0,80)});
    });
  }catch(e){}
  return out;
}
function broadTextHits(x,patterns){
  const out=[];
  try{
    Array.from(x.d.querySelectorAll('button,h1,h2,h3,summary,section,article,div,pre')).forEach(function(el){
      const t=textOf(el);
      if(!t||t.length>6000)return;
      if(patterns.some(function(p){return p.test(t)}))out.push({el:el,by:'broad:'+t.slice(0,80)});
    });
  }catch(e){}
  return out;
}
function firstVisible(hits){return hits.find(function(h){return h.visible})||null}
function sortHits(hits){return hits.sort(function(a,b){return a.doc_index-b.doc_index||a.order-b.order})}
function targetStatus(name,cfg){
  const actual=[],selector=[],status=[],broad=[];
  allDocuments().forEach(function(x,docIndex){
    uniqueElements(selectorHits(x,cfg).map(function(h){return h.el})).forEach(function(el){selector.push(baseHit(x,docIndex,el,'selector_hit','selector'))});
    uniqueElements(headingHits(x,cfg.actual||[]).map(function(h){return h.el})).forEach(function(el){actual.push(baseHit(x,docIndex,el,'actual_panel_heading','heading'))});
    uniqueElements(statusHits(x,cfg.status||[]).map(function(h){return h.el})).forEach(function(el){status.push(baseHit(x,docIndex,el,'status_or_summary_signal','status'))});
    uniqueElements(broadTextHits(x,(cfg.actual||[]).concat(cfg.status||[])).map(function(h){return h.el})).forEach(function(el){broad.push(baseHit(x,docIndex,el,'broad_dom_signal','broad'))});
  });
  sortHits(actual);sortHits(selector);sortHits(status);sortHits(broad);
  const all=sortHits(uniqueByKey(actual.concat(selector).concat(status).concat(broad)));
  return {
    name:name,
    label:cfg.label,
    actual_panel_count:actual.length,
    visible_actual_panel_count:actual.filter(function(h){return h.visible}).length,
    selector_count:selector.length,
    status_signal_count:status.length,
    broad_signal_count:broad.length,
    visible_total:all.filter(function(h){return h.visible}).length,
    first_actual_panel:actual[0]||null,
    first_visible_actual_panel:firstVisible(actual),
    first_status_signal:status[0]||null,
    first_broad_signal:broad[0]||null,
    actual_panel_hits:actual.slice(0,5),
    selector_hits:selector.slice(0,4),
    status_signal_hits:status.slice(0,5),
    broad_signal_hits:broad.slice(0,5)
  };
}
function uniqueByKey(arr){
  const seen={},out=[];
  arr.forEach(function(h){
    const k=[h.doc_index,h.order,h.evidence_type,h.text].join('|');
    if(!seen[k]){seen[k]=1;out.push(h)}
  });
  return out;
}
function orderFrom(targets,kind){
  const rows=[];
  LEGAL_ORDER.forEach(function(k){
    const st=targets[k];
    if(!st)return;
    const h=kind==='actual'?st.first_actual_panel:kind==='visible'?st.first_visible_actual_panel:kind==='status'?st.first_status_signal:st.first_broad_signal;
    if(h)rows.push({key:k,label:st.label,doc_index:h.doc_index,order:h.order,visible:h.visible,text:h.text,evidence_type:h.evidence_type});
  });
  return rows.sort(function(a,b){return a.doc_index-b.doc_index||a.order-b.order});
}
function issueList(rows){
  const measured=rows.map(function(x){return x.key});
  const issues=[];
  for(let i=0;i<measured.length;i++){
    for(let j=i+1;j<measured.length;j++){
      const a=measured[i],b=measured[j];
      if(LEGAL_ORDER.indexOf(a)>LEGAL_ORDER.indexOf(b))issues.push({before_in_dom:a,after_in_dom:b,expected_before:b,expected_after:a});
    }
  }
  return issues;
}
function bankCrSnapshot(){
  const targets={};
  Object.keys(BANK_CR_TARGETS).forEach(function(k){targets[k]=targetStatus(k,BANK_CR_TARGETS[k])});
  const actualRows=orderFrom(targets,'actual');
  const visibleRows=orderFrom(targets,'visible');
  const statusRows=orderFrom(targets,'status');
  const broadRows=orderFrom(targets,'broad');
  const actualOrder=actualRows.map(function(x){return x.key});
  const visibleOrder=visibleRows.map(function(x){return x.key});
  const statusOrder=statusRows.map(function(x){return x.key});
  const broadOrder=broadRows.map(function(x){return x.key});
  const actualIssues=issueList(actualRows);
  const statusIssues=issueList(statusRows);
  const broadIssues=issueList(broadRows);
  const deleteActual=actualRows.find(function(x){return x.key==='bank_delete_tools'});
  const level1Actual=actualRows.find(function(x){return x.key==='level_1'});
  const level3Visible=targets.level_3&&targets.level_3.visible_actual_panel_count>0;
  const conclusion=actualIssues.length?'possible_real_panel_order_issue':'status_or_broad_signal_only_unless_visible_problem_seen';
  return {
    at:now(),
    route_hash:String(location.hash||''),
    docs:allDocuments().map(function(x){return {url:x.url,title:x.title}}),
    targets:targets,
    legal_order:LEGAL_ORDER,
    actual_panel_order:actualOrder,
    visible_panel_order:visibleOrder,
    status_signal_order:statusOrder,
    hidden_or_broad_dom_order:broadOrder,
    actual_panel_order_issues:actualIssues,
    status_signal_order_issues:statusIssues,
    hidden_or_broad_order_issues:broadIssues,
    diagnostic_sharpening:{
      actual_panel_order_count:actualOrder.length,
      visible_panel_order_count:visibleOrder.length,
      status_signal_order_count:statusOrder.length,
      broad_signal_order_count:broadOrder.length,
      interpretation:conclusion,
      rule:'Treat actual_panel_order as the only fix-worthy order signal. Status/broad order is diagnostic context only.'
    },
    known_watchpoints:{
      delete_tools_before_level_1_actual:!!(deleteActual&&level1Actual&&(deleteActual.doc_index<level1Actual.doc_index||(deleteActual.doc_index===level1Actual.doc_index&&deleteActual.order<level1Actual.order))),
      level_3_visible_actual_now:!!level3Visible,
      bank_visible_now:!!(targets.bank_tab&&targets.bank_tab.visible_total>0),
      continuous_run_detail_visible_actual_now:!!(targets.continuous_run_detail&&targets.continuous_run_detail.visible_actual_panel_count>0),
      status_order_issue_count:statusIssues.length,
      actual_order_issue_count:actualIssues.length
    }
  };
}
function diagState(){
  const k='__pmpBankCrDiagnosticsV4B';
  if(!window[k])window[k]={started_at:now(),samples:[],last:null,copy_count:0};
  return window[k];
}
function bankCrObserve(){
  const st=diagState();
  const snap=bankCrSnapshot();
  st.last=snap;
  st.samples.push({
    at:snap.at,
    hash:String(location.hash||''),
    bank_visible:snap.known_watchpoints.bank_visible_now,
    continuous_run_detail_visible_actual:snap.known_watchpoints.continuous_run_detail_visible_actual_now,
    level_3_visible_actual:snap.known_watchpoints.level_3_visible_actual_now,
    delete_tools_before_level_1_actual:snap.known_watchpoints.delete_tools_before_level_1_actual,
    actual_order_issue_count:snap.known_watchpoints.actual_order_issue_count,
    status_order_issue_count:snap.known_watchpoints.status_order_issue_count,
    actual_panel_order:snap.actual_panel_order,
    visible_panel_order:snap.visible_panel_order,
    status_signal_order:snap.status_signal_order,
    interpretation:snap.diagnostic_sharpening.interpretation
  });
  if(st.samples.length>DIAG_MAX)st.samples.splice(0,st.samples.length-DIAG_MAX);
  return snap;
}
function bankCrSummary(){
  const st=diagState();
  const samples=st.samples||[];
  return {
    diagnostic_version:BANK_CR_DIAG_VERSION,
    started_at:st.started_at,
    sample_count:samples.length,
    last_sample_at:samples.length?samples[samples.length-1].at:null,
    saw_bank_visible:samples.some(function(s){return s.bank_visible}),
    saw_continuous_run_detail_visible_actual:samples.some(function(s){return s.continuous_run_detail_visible_actual}),
    saw_level_3_visible_actual:samples.some(function(s){return s.level_3_visible_actual}),
    saw_delete_tools_before_level_1_actual:samples.some(function(s){return s.delete_tools_before_level_1_actual}),
    max_actual_order_issue_count:samples.reduce(function(m,s){return Math.max(m,s.actual_order_issue_count||0)},0),
    max_status_order_issue_count:samples.reduce(function(m,s){return Math.max(m,s.status_order_issue_count||0)},0),
    last_actual_panel_order:samples.length?samples[samples.length-1].actual_panel_order:[],
    last_visible_panel_order:samples.length?samples[samples.length-1].visible_panel_order:[],
    last_status_signal_order:samples.length?samples[samples.length-1].status_signal_order:[],
    rule:'Passive observation only. No Bank fix, move, delete, rebuild, route change, or app storage write.'
  };
}
function bankCrDiagnosticsProof(){
  const st=diagState();
  const last=bankCrObserve();
  st.copy_count++;
  return {
    type:'PMP_BANK_CR_DIAGNOSTICS_PROOF_V1',
    pass:'4B',
    version:VERSION,
    diagnostic_version:BANK_CR_DIAG_VERSION,
    owner:OWNER,
    built_at:now(),
    mode:'passive_observe_and_copy_only',
    rule:'No fixing, moving, deleting, Bank rebuild, route change, Bank storage write, or IndexedDB write.',
    instructions:'Best sample: open Bank, open Continuous Run Bank, then return to Control Room and copy this proof.',
    sharpening:'Separates actual panels from visible panels, status/summary signals, and hidden/broad DOM signals.',
    summary:bankCrSummary(),
    last_snapshot:last,
    recent_samples:(st.samples||[]).slice(-30),
    interpretation_note:'Only actual_panel_order_issues should drive a fix. Status_signal_order or hidden_or_broad_order can be diagnostic noise.'
  };
}
async function copyObject(doc,out,obj,okText){
  const text=JSON.stringify(obj,null,2);
  let copied=false;
  try{await navigator.clipboard.writeText(text);copied=true}catch(e){
    try{const ta=doc.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';doc.body.appendChild(ta);ta.focus();ta.select();copied=doc.execCommand('copy');ta.remove()}catch(x){}
  }
  if(out){out.textContent=copied?okText:text;out.className=copied?'note':'warn'}
  return obj;
}
async function copyProof(doc,out){return copyObject(doc,out,smokeProof(),'Smoke Test Proof copied. Paste it into ChatGPT.')}
async function copyBankCrDiagnostics(doc,out){return copyObject(doc,out,bankCrDiagnosticsProof(),'Bank / Continuous Run Diagnostics copied. Paste it into ChatGPT.')}
function controlHost(doc){
  if(!doc)return null;
  return doc.getElementById('control')||
    doc.querySelector('[data-screen="control"],[data-tab-panel="control"],section.control,.control-room')||
    Array.from(doc.querySelectorAll('section,main,div')).find(function(x){return /^Control( Room)?$/i.test(textOf(x.querySelector('h1,h2')||''))});
}
function installCopySmokeProof(doc){
  const host=controlHost(doc);
  if(!host||doc.getElementById('pmpCopySmokeTestProofControlV1'))return;
  const card=doc.createElement('div');
  card.id='pmpCopySmokeTestProofControlV1';
  card.setAttribute('data-pmp-copy-smoke-test-proof-v1','control-room');
  card.style.cssText='border:2px solid var(--line,#07101c);border-radius:22px;padding:12px;margin:12px 0;background:var(--card,#fff);color:var(--text,#07101c)';
  card.innerHTML='<button id="pmpCopySmokeTestProofButtonV1" class="big" type="button"><span class="icon">✓</span><span>Copy Smoke Test Proof<small>passive proof packet for ChatGPT</small></span><span class="chev">›</span></button><button id="pmpCopyBankCrDiagnosticsButtonV1" class="big" type="button" style="margin-top:8px"><span class="icon">▣</span><span>Copy Bank / Continuous Run Diagnostics<small>Pass 4B sharpened panel/status proof</small></span><span class="chev">›</span></button><div id="pmpCopySmokeTestProofOutV1" class="note" style="margin-top:8px">Copies proof only. No fixing or moving.</div>';
  const first=host.firstElementChild;
  if(first)host.insertBefore(card,first.nextSibling||first);else host.appendChild(card);
  const btn=doc.getElementById('pmpCopySmokeTestProofButtonV1');
  const diag=doc.getElementById('pmpCopyBankCrDiagnosticsButtonV1');
  const out=doc.getElementById('pmpCopySmokeTestProofOutV1');
  if(btn)btn.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}copyProof(doc,out);return false};
  if(diag)diag.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}copyBankCrDiagnostics(doc,out);return false};
}
function applyCleanup(doc){
  bankCrObserve();
  if(!doc)return;
  Array.from(doc.querySelectorAll('button')).forEach(function(button){
    var text=textOf(button);
    if(text.indexOf('Automatic App Update')!==-1 || text.indexOf('Open Code Safety')!==-1){
      button.dataset.pmpControlRoomCleanup='route-guardian-owned';
      button.style.display='none';
    }
  });
  installCopySmokeProof(doc);
}
if(!window.__pmpBankCrDiagnosticsTimerV4B){
  window.__pmpBankCrDiagnosticsTimerV4B=setInterval(function(){try{bankCrObserve()}catch(e){}},450);
  try{bankCrObserve()}catch(e){}
}
window.PMPControlRoomCleanupV1={
  version:VERSION,
  owner:OWNER,
  apply:applyCleanup,
  smokeProof:smokeProof,
  copyProof:function(){return copyProof(document,null)},
  bankCrObserve:bankCrObserve,
  bankCrSummary:bankCrSummary,
  bankCrDiagnosticsProof:bankCrDiagnosticsProof,
  copyBankCrDiagnostics:function(){return copyBankCrDiagnostics(document,null)}
};
})();
