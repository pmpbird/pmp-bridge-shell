/* PMP Active Bug Found contract with durable session observer and Diagnostics V2 evidence bridge. */
(()=>{
'use strict';
const V='2.2.0-durable-session-diagnostics-20260728A';
const OWNER='pmp-active-bug-found-contract-v1';
const KEY='pmp_bug_bank_active_bugs_v1';
const RECEIPT_INDEX_KEY='pmp_bug_watch_receipt_lineage_v2';
const DEDUPE_KEY='pmp_bug_watch_dedupe_index_v2';
const HANDOFF_INDEX_KEY='pmp_bug_watch_handoff_lineage_v2';
const DURABLE_RECEIPT_KEY='pmp_bug_watch_session_durable_v1_receipt';
const DIAGNOSTICS_COMPAT_KEY='pmp_bug_watch_passive_capture_v1_receipt';
const CONTRACT_COMPAT_KEY='pmp_active_bug_found_contract_v1_receipt';
const NOTE='Read-only Active Bugs Found contract. Existing rows are never normalized, merged, truncated, reordered, or rewritten.';
const installed=[];
let capturedThisSession=0;
let duplicateThisSession=0;
let lastCaptureAt=null;
function now(){return new Date().toISOString()}
function clean(value){return String(value==null?'':value).replace(/\s+/g,' ').trim()}
function read(key,fallback){try{const raw=localStorage.getItem(key);return raw==null?fallback:JSON.parse(raw)}catch(_){return fallback}}
function write(key,value){try{localStorage.setItem(key,JSON.stringify(value,null,2));return true}catch(_){return false}}
function signature(row){return clean(row&&row.signature||[row&&row.type||row&&row.kind||row&&row.problem||'active bug',row&&row.where_seen||row&&row.where||'runtime',row&&row.symptom||row&&row.how_it_happens||''].join('|')).toLowerCase().replace(/[^a-z0-9|:/._ -]+/g,' ').slice(0,240)}
function shape(row){row=row||{};return{bug_id:row.bug_id||row.id||'',status:row.status||'unknown',severity:row.severity||row.level||'medium',source:row.source||row.evidence_source||'unknown',where_seen:clean(row.where_seen||row.where||'Runtime'),symptom:clean(row.symptom||row.how_it_happens||row.type||'Active bug symptom'),evidence:row.evidence||row.detail||{},signature:signature(row),raw_source:row}}
function rows(){const value=read(KEY,[]);return Array.isArray(value)?value:[]}
function report(){return{type:'PMP_ACTIVE_BUG_FOUND_CONTRACT_REPORT_V2',version:V,owner:OWNER,active_key:KEY,count:rows().length,note:NOTE,read_only:true,automatic_normalization:false,automatic_repair:false,classify_fixed:false,durable_session_observer:true}}
function add(row){let target;try{target=top||window}catch(_){target=window}const api=target.PMPBugAuthorityV2||window.PMPBugAuthorityV2;if(!api||typeof api.observe!=='function')return Promise.reject(new Error('BUG_AUTHORITY_UNAVAILABLE'));return api.observe('active_bug_found_contract',row||{})}
function normalize(){return Object.assign(report(),{status:'READ_ONLY_NO_NORMALIZATION',at:now()})}
function appendCandidate(row){
  const active=rows();
  const sig=signature(row);
  if(active.some(item=>signature(item)===sig)){duplicateThisSession++;publishEvidence('duplicate_observation');return false}
  const candidate={
    bug_id:'BUG-SESSION-'+Date.now().toString(36).toUpperCase()+'-'+Math.random().toString(36).slice(2,8).toUpperCase(),
    status:'candidate',
    severity:clean(row.severity||'high').toLowerCase(),
    source:'durable session bug watch',
    where_seen:clean(row.where_seen||row.where||'Active app runtime'),
    symptom:clean(row.symptom||row.how_it_happens||'Observed runtime problem'),
    evidence:row.evidence||row.detail||{},
    owner_guess:'',
    affected_area:clean(row.affected_area||row.where||row.where_seen||'Runtime'),
    safe_to_ignore:false,
    blocks_next_pass:!!row.blocks_next_pass,
    first_seen:now(),
    last_seen:now(),
    seen_count:1,
    work_allowed:false,
    fix_authorized:false,
    signature:sig,
    bug_bank_section:'Active Bugs Found',
    receipt_id:'SESSION-DURABLE-'+Date.now().toString(36).toUpperCase()
  };
  const next=active.concat([candidate]);
  try{localStorage.setItem(KEY,JSON.stringify(next));capturedThisSession++;lastCaptureAt=candidate.first_seen;publishEvidence('new_candidate');return true}catch(_){publishEvidence('capture_storage_failure');return false}
}
function evidenceSnapshot(reason){
  const active=rows();
  const receiptIndex=read(RECEIPT_INDEX_KEY,[]);
  const dedupe=read(DEDUPE_KEY,{});
  const handoffs=read(HANDOFF_INDEX_KEY,[]);
  return{
    type:'PMP_BUG_WATCH_SESSION_DURABLE_RECEIPT_V1',
    version:V,
    owner:'bug_bank_owner',
    at:now(),
    reason:reason||'heartbeat',
    status:'ACTIVE_SESSION_MONITORING',
    active_key:KEY,
    active_bug_count:active.length,
    v2_receipt_count:Array.isArray(receiptIndex)?receiptIndex.length:0,
    v2_dedupe_count:dedupe&&typeof dedupe==='object'&&!Array.isArray(dedupe)?Object.keys(dedupe).length:0,
    v2_handoff_count:Array.isArray(handoffs)?handoffs.length:0,
    installed_window_count:installed.length,
    captured_this_session:capturedThisSession,
    duplicates_this_session:duplicateThisSession,
    last_capture_at:lastCaptureAt,
    monitoring_scope:['runtime errors','unhandled promise rejections','script load failures','stylesheet load failures','iframe and frame load failures'],
    monitoring_lifetime:'current page session',
    passive_only:true,
    automatic_repair:false,
    existing_rows_rewritten:false,
    existing_rows_deleted:false
  }
}
function publishEvidence(reason){
  const receipt=evidenceSnapshot(reason);
  write(DURABLE_RECEIPT_KEY,receipt);
  write(DIAGNOSTICS_COMPAT_KEY,Object.assign({},receipt,{type:'PMP_BUG_WATCH_PASSIVE_CAPTURE_COMPATIBILITY_RECEIPT_V1',evidence_source:'Version 2 lineage plus durable session observer'}));
  write(CONTRACT_COMPAT_KEY,Object.assign({},report(),{type:'PMP_ACTIVE_BUG_FOUND_CONTRACT_COMPATIBILITY_RECEIPT_V1',at:receipt.at,status:'ACTIVE_READ_ONLY',durable_receipt_key:DURABLE_RECEIPT_KEY}));
  return receipt
}
function observe(row){appendCandidate(row)}
function installWindow(win){
  try{
    if(!win||installed.some(item=>item.win===win))return;
    const onError=event=>{
      try{
        const target=event.target||{};
        const tag=clean(target.tagName).toLowerCase();
        if(['script','link','iframe','frame'].includes(tag)){
          observe({type:'Resource Load Failure',where:'Active app resource load',symptom:tag+' failed to load.',severity:'high',detail:{tag,src:target.src||target.href||target.getAttribute&&target.getAttribute('src')||'',document_url:String(win.location&&win.location.href||'')}});
          return
        }
        if(event.message)observe({type:'Runtime Error',where:'Active app runtime',symptom:String(event.message),severity:'high',detail:{filename:event.filename||'',lineno:event.lineno||0,colno:event.colno||0,document_url:String(win.location&&win.location.href||'')}})
      }catch(_){}
    };
    const onReject=event=>{try{observe({type:'Unhandled Promise Rejection',where:'Active app runtime',symptom:String(event.reason&&event.reason.message||event.reason||'Unhandled promise rejection'),severity:'high',detail:{document_url:String(win.location&&win.location.href||'')}})}catch(_){}};
    win.addEventListener('error',onError,true);
    win.addEventListener('unhandledrejection',onReject);
    installed.push({win,onError,onReject})
  }catch(_){}
}
function walk(win,depth){
  if(!win||depth>12)return;
  installWindow(win);
  try{Array.from(win.document.querySelectorAll('iframe,frame')).forEach(frame=>{try{walk(frame.contentWindow,depth+1)}catch(_){}})}catch(_){}
}
function heartbeat(){let root;try{root=top||window}catch(_){root=window}walk(root,0);publishEvidence('heartbeat')}
window.PMPActiveBugFoundContractV1=Object.freeze({version:V,owner:OWNER,shape,normalize,add,report,rows,durableReceipt:()=>evidenceSnapshot('api_read'),publishEvidence});
heartbeat();
setInterval(heartbeat,2000);
})();
