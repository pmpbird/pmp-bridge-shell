(()=>{
'use strict';
const V='1.0.1-resident-continuous-run-status-reader-repatch';
const OWNER='pmp-resident-continuous-run-status-reader-v1';
const K={
  transferManifest:'pmp_continuous_run_bank_transfer_store_manifest_v1',
  transferReceipts:'pmp_continuous_run_bank_transfer_store_receipts_v1',
  sourceA:'pmp_packet_1_5_builder_source_v1',
  sourceB:'pmp_packet_1_5_packet_text_v1',
  units:'pmp_packet_1_5_units_v1',
  proofGate:'pmp_universal_work_proof_gate_run_v1',
  runner:'pmp_universal_continuous_work_runner_v1',
  runnerLegacy:'pmp_packet_1_5_continuous_runner_v1',
  runnerProof:'pmp_universal_continuous_work_runner_proof_v1',
  engineState:'pmp_continuous_run_state_bank_v1',
  engineReceipts:'pmp_continuous_run_state_receipts_v1',
  lastReader:'pmp_resident_continuous_run_status_reader_v1'
};
function now(){return new Date().toISOString()}
function raw(k){try{return localStorage.getItem(k)||''}catch(e){return''}}
function json(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function arr(x){return Array.isArray(x)?x:[]}
function sourceText(){return raw(K.sourceA)||raw(K.sourceB)||''}
function units(){return arr(json(K.units,[]))}
function proof(){return json(K.proofGate,null)}
function runner(){return json(K.runner,null)||json(K.runnerLegacy,null)||{} }
function transferFallback(){
  const m=json(K.transferManifest,null);
  const v=m&&m.verification||{};
  const missing=[].concat(arr(v.missing),arr(v.lossless_missing));
  arr(v.weak_items).forEach(x=>missing.push('weak:'+String(x&&x.item_type||'unknown')));
  return {ok:!!(m&&(m.verified||m.lossless_verified)),reason:m?(m.lossless_verified?'lossless_verified':'temporary_transfer_store_not_lossless_verified'):'temporary_transfer_store_manifest_missing',missing:missing.length?missing:(m?[]:['transfer_store_manifest']),slot_check_passed:!!(m&&(m.slot_check_passed||(v.slot_check_passed))),lossless_verified:!!(m&&(m.lossless_verified||(v.lossless_verified))),weak_items:arr(v.weak_items),manifest:m};
}
function transferGate(){
  try{const api=window.PMPContinuousRunBankTransferStoreV1;if(api&&typeof api.engineGate==='function')return api.engineGate()}catch(e){return {ok:false,reason:'transfer_store_api_error',missing:['transfer_store_api_error'],message:e.message,weak_items:[]}}
  return transferFallback();
}
function unitProof(){
  const u=units(),src=sourceText(),watch=[];
  u.forEach((x,i)=>{let miss=[];if(!x||!x.unit_id)miss.push('unit_id');if(!x||!x.unit_type)miss.push('unit_type');if(!x||!x.objective)miss.push('objective');if(!x||!x.checks||!x.checks.length)miss.push('checks');if(miss.length)watch.push({unit_index:i,unit_id:x&&x.unit_id||('unit_'+i),missing:miss})});
  const blocked=[];if(!src)blocked.push('source_missing');if(!u.length)blocked.push('work_units_missing');
  return {pass:!!src&&u.length>0&&watch.length===0&&blocked.length===0,source_characters:src.length,units_total:u.length,watch_units:watch.length,blocked_units:blocked,watch:watch.slice(0,12)};
}
function domStatus(w,d){
  let screen=false,runnerText='',proofText='';
  try{screen=!!(d&&d.getElementById&&d.getElementById('pmpContinuousRunDashboardScreenV1'));const sr=d&&d.querySelector&&d.querySelector('[data-sr-stat]');if(sr)runnerText=String(sr.textContent||'').trim();const ps=d&&d.querySelector&&d.querySelector('[data-p15-proof-section]');if(ps)proofText=String(ps.textContent||'').trim().slice(0,500)}catch(e){}
  return {screen_present:screen,runner_text:runnerText,proof_section_text:proofText};
}
function buildStatus(w,d){
  const g=transferGate(),up=unitProof(),pg=proof(),r=runner(),rp=json(K.runnerProof,null),manifest=g.manifest||json(K.transferManifest,null),state=json(K.engineState,null),receipts=arr(json(K.engineReceipts,[]));
  const pgStatus=pg&&pg.status?pg.status:(up.pass?'PASS':(up.blocked_units.length?'BLOCKED':'WATCH'));
  const runnerStatus=(r&&r.status)||((rp&&rp.status)||'unknown');
  const blocked=arr(pg&&pg.blocked_units).length?arr(pg.blocked_units):up.blocked_units;
  const out={type:'PMP_RESIDENT_CONTINUOUS_RUN_STATUS_READER_V1',version:V,owner:OWNER,at:now(),read_only:true,resident_access:'direct_read_from_resident_context',bank_access:{can_read_continuous_run_bank:true,transfer_store_verified:!!g.ok,reason:g.reason||'',slot_check_passed:!!g.slot_check_passed,lossless_verified:!!g.lossless_verified,missing:arr(g.missing),weak_items_count:arr(g.weak_items).length,manifest_present:!!manifest,receipt_count:arr(json(K.transferReceipts,[])).length},engine_access:{can_read_engine_state:true,runner_status:runnerStatus,proof_gate_status:pgStatus,proof_gate_ready:pgStatus==='PASS'||!!(pg&&pg.work_ready),source_characters:(pg&&Number(pg.source_characters))||up.source_characters,units_total:(pg&&Number(pg.units_total))||up.units_total,units_proven:(pg&&Number(pg.units_proven))||0,watch_units:(pg&&Number(pg.watch_units))||up.watch_units,blocked_units:blocked,completed:Number(r&&r.units_completed||0),total:Number(r&&r.total_units||up.units_total||0),engine_state_present:!!state,engine_receipt_count:receipts.length},dom_status:domStatus(w,d),plain:'',next:''};
  let why='';
  if(!out.engine_access.proof_gate_ready){why='Proof Gate is '+out.engine_access.proof_gate_status+'.';if(out.engine_access.blocked_units.length)why+=' Blocked by '+out.engine_access.blocked_units.join(', ')+'.'}
  else if(String(out.engine_access.runner_status).toUpperCase()==='BLOCKED'){why='Runner is BLOCKED. Check runner proof for reason.'}
  else why='Proof Gate is ready; runner status is '+out.engine_access.runner_status+'.';
  out.plain=['I can directly read the Continuous Run Bank and Continuous Work Engine status.','Continuous Run Bank transfer store: '+(out.bank_access.transfer_store_verified?'VERIFIED':'NOT VERIFIED')+'.','Source/transfer store missing: '+(out.bank_access.missing.length?out.bank_access.missing.join(', '):'none')+'.','Runner status: '+out.engine_access.runner_status+'.','Proof Gate: '+out.engine_access.proof_gate_status+'.','Work source characters: '+out.engine_access.source_characters+'. Work units: '+out.engine_access.units_total+'.','Why blocked: '+why].join('\n');
  out.next=out.engine_access.proof_gate_ready?'The engine may move to the runner step if the transfer store is verified.':'Save a work source, build work units, then run Proof Gate again.';
  return out;
}
function wantsStatus(q){q=String(q||'').toLowerCase();return /(continuous|run engine|work engine|runner|proof gate|transfer store|continuous run bank|work units)/.test(q)&&/(status|read|why|blocked|bank|engine|runner|proof|verified|missing|connect|use both)/.test(q)}
function showResident(w,d,out){
  save(K.lastReader,out);
  try{const reply=d.getElementById('residentReply');if(reply)reply.textContent=out.plain+'\n\nNext: '+out.next}catch(e){}
  try{const warn=d.getElementById('residentWarning');if(warn){warn.classList.add('hidden');warn.textContent=''}}catch(e){}
  try{const work=d.getElementById('residentWork');if(work){work.classList.remove('hidden');work.textContent=JSON.stringify(out,null,2)}}catch(e){}
  try{const chat=d.getElementById('residentChatBox');if(chat){chat.style.display='block';const b=d.createElement('div');b.className='bubble bot';b.textContent=out.plain;chat.appendChild(b);chat.scrollTop=chat.scrollHeight}}catch(e){}
}
function expose(w,d){w.PMPResidentContinuousRunStatusReaderV1={version:V,read:()=>buildStatus(w,d),copy:()=>{const out=buildStatus(w,d),txt=JSON.stringify(out,null,2);try{navigator.clipboard.writeText(txt)}catch(e){}return out}}}
function installInto(w,d){
  if(!w||!d)return;
  expose(w,d);
  if(typeof w.residentRun==='function'&&w.residentRun.__pmpCRStatusReaderPatched)return;
  const old=(typeof w.residentRun==='function')?w.residentRun:null;
  const patched=function(){
    const q=(d.getElementById('ask')||{}).value||'';
    if(wantsStatus(q)){const out=buildStatus(w,d);showResident(w,d,out);return false}
    return old?old.apply(this,arguments):false;
  };
  patched.__pmpCRStatusReaderPatched=true;
  patched.__pmpCRStatusReaderOld=old;
  w.residentRun=patched;
  w.__pmpResidentContinuousRunStatusReaderV1={version:V,patched_at:now(),old_resident_run_present:!!old};
}
function scan(){
  try{installInto(window,document)}catch(e){}
  try{const f=document.getElementById('app');const w=f&&f.contentWindow,d=f&&(f.contentDocument||w.document);if(w&&d)installInto(w,d)}catch(e){}
}
window.PMPResidentContinuousRunStatusReaderV1={version:V,scan,read:()=>buildStatus(window,document)};
function bind(){
  scan();
  try{
    const frame=document.getElementById('app');
    if(frame&&!frame.dataset.pmpResidentStatusOwnerBound){
      frame.dataset.pmpResidentStatusOwnerBound='1';
      frame.addEventListener('load',scan);
    }
  }catch(e){}
}
window.addEventListener('load',bind,{once:true});
bind();
})();
