(()=>{
'use strict';
const V='1.0.0-cr-status-local-answer-router';
const LS={manifest:'pmp_continuous_run_bank_transfer_store_manifest_v1',source:'pmp_packet_1_5_builder_source_v1',source2:'pmp_packet_1_5_packet_text_v1',units:'pmp_packet_1_5_units_v1',proof:'pmp_universal_work_proof_gate_run_v1',runner:'pmp_universal_continuous_work_runner_v1',runner2:'pmp_packet_1_5_continuous_runner_v1',last:'pmp_resident_continuous_run_status_reader_v1'};
function j(k,d){try{let v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function s(k){try{return localStorage.getItem(k)||''}catch(e){return''}}
function put(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function a(x){return Array.isArray(x)?x:[]}
function txt(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function allDocs(d,n,o){o=o||[];if(!d||n>10)return o;try{o.push(d);Array.from(d.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)allDocs(z,n+1,o)}catch(e){}})}catch(e){}return o}
function wants(q){q=String(q||'').toLowerCase();return /(continuous|run engine|work engine|runner|proof gate|transfer store|continuous run bank|work units)/.test(q)&&/(status|read|why|blocked|bank|engine|runner|proof|verified|missing|connect|use both)/.test(q)}
function statusObj(d){
  let m=j(LS.manifest,null),v=m&&m.verification||{},p=j(LS.proof,null),r=j(LS.runner,null)||j(LS.runner2,null)||{},src=s(LS.source)||s(LS.source2),u=a(j(LS.units,[]));
  let miss=[].concat(a(v.missing),a(v.lossless_missing));
  a(v.weak_items).forEach(x=>miss.push('weak:'+String(x&&x.item_type||'unknown')));
  let blocked=p&&a(p.blocked_units).length?a(p.blocked_units):[];
  if(!p){if(!src)blocked.push('source_missing');if(!u.length)blocked.push('work_units_missing')}
  let out={type:'PMP_RESIDENT_CONTINUOUS_RUN_STATUS_READER_V1',version:V,at:new Date().toISOString(),read_only:true,bank_access:{can_read_continuous_run_bank:true,transfer_store_verified:!!(m&&(m.verified||m.lossless_verified)),slot_check_passed:!!(m&&(m.slot_check_passed||v.slot_check_passed)),lossless_verified:!!(m&&(m.lossless_verified||v.lossless_verified)),missing:miss,weak_items_count:a(v.weak_items).length,manifest_present:!!m},engine_access:{can_read_engine_state:true,runner_status:r.status||'unknown',proof_gate_status:p&&p.status?p.status:(blocked.length?'BLOCKED':'PASS'),proof_gate_ready:!!(p&&p.work_ready),source_characters:p&&Number(p.source_characters)||src.length,units_total:p&&Number(p.units_total)||u.length,units_proven:p&&Number(p.units_proven)||0,watch_units:p&&Number(p.watch_units)||0,blocked_units:blocked,completed:Number(r.units_completed||0),total:Number(r.total_units||u.length||0)},screen:(Array.from(d.querySelectorAll('.screen')).find(x=>x.classList&&x.classList.contains('on'))||{}).id||''};
  let why=out.engine_access.proof_gate_ready?'Proof Gate is ready.':'Proof Gate is '+out.engine_access.proof_gate_status+(out.engine_access.blocked_units.length?' because '+out.engine_access.blocked_units.join(', '):'')+'.';
  out.plain=['I can answer this locally from the app status.','Continuous Run Bank transfer store: '+(out.bank_access.transfer_store_verified?'VERIFIED':'NOT VERIFIED')+'.','Source/transfer store missing: '+(out.bank_access.missing.length?out.bank_access.missing.join(', '):'none')+'.','Runner status: '+out.engine_access.runner_status+'.','Proof Gate: '+out.engine_access.proof_gate_status+'.','Work source characters: '+out.engine_access.source_characters+'. Work units: '+out.engine_access.units_total+'.','Why blocked: '+why].join('\n');
  out.next=out.engine_access.proof_gate_ready?'Start Work Run can be tested if transfer store is verified.':'Load/save work source, build work units, then run Proof Gate again.';
  return put(LS.last,out);
}
function show(d,out){let r=d.getElementById('residentReply');if(r)r.textContent=out.plain+'\n\nNext: '+out.next;let w=d.getElementById('residentWork');if(w){w.classList.remove('hidden');w.textContent=JSON.stringify(out,null,2)}let warn=d.getElementById('residentWarning');if(warn){warn.classList.add('hidden');warn.textContent=''}}
function install(d){let win=d.defaultView;if(!win)return;win.PMPResidentContinuousRunStatusReaderV1={version:V,read:()=>statusObj(d)};if(typeof win.residentRun==='function'&&!win.residentRun.__crLocalAnswer){let old=win.residentRun;let f=function(){let q=(d.getElementById('ask')||{}).value||'';if(wants(q)){show(d,statusObj(d));return false}return old.apply(this,arguments)};f.__crLocalAnswer=true;win.residentRun=f}Array.from(d.querySelectorAll('button')).forEach(b=>{if(txt(b)==='Run'&&!b.dataset.crLocalAnswer){b.dataset.crLocalAnswer='1';b.addEventListener('click',e=>{let q=(d.getElementById('ask')||{}).value||'';if(wants(q)){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();show(d,statusObj(d));return false}},true)}})}
function scan(){allDocs(document,0,[]).forEach(install)}
window.addEventListener('load',()=>[50,200,600,1200,2400].forEach(t=>setTimeout(scan,t)));setInterval(scan,500);scan();
})();