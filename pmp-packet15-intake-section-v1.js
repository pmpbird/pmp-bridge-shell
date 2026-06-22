(()=>{
  if(window.PMPPacket15IntakeSectionV1&&window.PMPPacket15IntakeSectionV1.version==='1.0.0-intake-save-split-proof')return;
  const VERSION='1.0.0-intake-save-split-proof';
  const PACKET='pmp_packet_1_5_packet_text_v1';
  const UNITS='pmp_packet_1_5_units_v1';
  const UNIT_PROOF='pmp_packet_1_5_unit_proof_v1';
  const RUNNER='pmp_packet_1_5_continuous_runner_v1';
  const STATE='pmp_continuous_run_state_ledger_v2';
  const MISSION='pmp_compressed_continuous_run_mission_v1';
  const DRAFT='pmp_free_in_app_engine_recovery_draft_v1';
  const CURRENT='pmp-current-inner-cleanbug-rgcontrols-v16.html#control';
  function now(){return new Date().toISOString()}
  function raw(k){try{return localStorage.getItem(k)||''}catch(_){return''}}
  function setRaw(k,v){try{localStorage.setItem(k,String(v));return true}catch(_){return false}}
  function rd(k,d){try{let v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(_){return d}}
  function wr(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2));return true}catch(_){return false}}
  function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(_){}})}catch(_){ }return out}
  function safeId(s,i){let x=String(s||'unit').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'');return x?('packet_1_5_'+x).slice(0,80):('packet_1_5_unit_'+String(i+1).padStart(3,'0'))}
  function splitPacket(text){
    let t=String(text||'').trim();
    if(!t)return[];
    let parts=t.split(/\n(?=\s*(?:#{1,6}\s+|[-*•]\s+|\d+[.)]\s+|Unit\s+\d+|Step\s+\d+|Task\s+\d+))/i).map(x=>x.replace(/^\s*(?:#{1,6}\s+|[-*•]\s+|\d+[.)]\s+)/,'').trim()).filter(Boolean);
    if(parts.length<2)parts=t.split(/\n\s*\n+/).map(x=>x.trim()).filter(Boolean);
    if(parts.length<2)parts=t.split(/(?<=\.)\s+(?=(?:Unit|Step|Task|Checkpoint)\b)/i).map(x=>x.trim()).filter(Boolean);
    if(parts.length<2&&t.length>240)parts=t.match(/.{1,220}(?:\s+|$)/g).map(x=>x.trim()).filter(Boolean);
    if(parts.length<1)parts=[t];
    return parts.slice(0,200).map((x,i)=>({unit_id:safeId(x.split('\n')[0],i),unit_index:i,title:(x.split('\n')[0]||('Unit '+(i+1))).slice(0,90),objective:x,verified:false,source:'packet_1_5_intake',created_at:now()}));
  }
  function kstatus(){let s=rd(STATE,{});if(s.kernel_to_leaf_attachment_status)return String(s.kernel_to_leaf_attachment_status);let k=s.kernel_to_leaf_guard_families||{};let r=k.root_collar_stabilization||{};if(r.status==='SOLIDIFIED_DETAILED_ROOT_COLLAR')return'attached_saturated_solidified_detailed_root_collar';return k.type?'attached':'missing'}
  function runnerPatch(units){let r=rd(RUNNER,{});r.type=r.type||'PMP_PACKET_1_5_CONTINUOUS_RUNNER_V1';r.intake_saved=true;r.intake_units_ready=true;r.total_units=units.length;r.units_completed=Number(r.units_completed||0);r.current_unit_index=Number(r.current_unit_index||0);r.continuous_auto_run_after_manual_start=true;r.manual_click_between_units=false;r.write_authority='none';r.merge_authority='none';r.paid_api_allowed=false;r.paid_fallback_allowed=false;r.spending_ceiling_usd=0;r.updated_at=now();wr(RUNNER,r);return r}
  function savePacket(text){let t=String(text||'').trim();if(!t)return{ok:false,reason:'packet_1_5_text_missing'};setRaw(PACKET,t);return{ok:true,bytes:t.length,at:now()}}
  function splitAndSave(text){let t=String(text||raw(PACKET)||'').trim();let saved=savePacket(t);if(!saved.ok)return{ok:false,reason:saved.reason,units:[]};let units=splitPacket(t);wr(UNITS,units);runnerPatch(units);return{ok:true,units,unit_count:units.length,at:now()}}
  function unitProof(){let units=rd(UNITS,[]);let packet=raw(PACKET);let r=rd(RUNNER,{});let p={type:'PMP_PACKET_1_5_INTAKE_UNIT_PROOF_V1',version:VERSION,report_quality:'LOSSLESS',at:now(),packet_saved:!!packet,packet_characters:packet.length,units_split:Array.isArray(units)&&units.length>0,units_total:Array.isArray(units)?units.length:0,current_unit_index:Number(r.current_unit_index||0),units_completed:Number(r.units_completed||0),kernel_to_leaf_attachment_status:kstatus(),write_authority:'none',merge_authority:'none',paid_api_allowed:false,paid_fallback_allowed:false,spending_ceiling_usd:0,real_app_mutation:'none',manual_start_required:true,continuous_auto_run_after_manual_start:true,manual_click_between_units:false,units:units};wr(UNIT_PROOF,p);return p}
  function copy(text){try{navigator.clipboard.writeText(text);return true}catch(_){return false}}
  function showOut(page,msg){let o=page.querySelector('[data-crd-out]');if(o){o.classList.remove('hidden');o.textContent=msg}}
  function updateStatus(page){let units=rd(UNITS,[]),packet=raw(PACKET),r=rd(RUNNER,{}),st=page.querySelector('[data-p15-intake-status]');if(st)st.textContent='Intake: '+(packet?'saved':'empty')+' units: '+(Array.isArray(units)?units.length:0)+' runner units: '+Number(r.total_units||0)}
  function install(doc){try{
    let page=doc.getElementById('pmpContinuousRunDashboardScreenV1');if(!page)return;
    let card=page.querySelector('.card')||page;
    let box=page.querySelector('[data-p15-intake-section]');
    if(!box){
      box=doc.createElement('div');box.setAttribute('data-p15-intake-section','');
      box.innerHTML='<h2>Packet 1.5 Intake</h2><div class="statusbar" data-p15-intake-status>Intake: empty</div><textarea data-p15-intake-text placeholder="Paste Packet 1.5 here. This is separate from the Continuous Run Mission."></textarea><div class="grid"><button class="mini" data-p15-save>Save Packet 1.5</button><button class="mini" data-p15-split>Split Into Units</button></div><div class="grid"><button class="mini" data-p15-copy-units>Copy Unit Proof</button><button class="mini" data-p15-clear-intake>Clear Intake</button></div>';
      let before=page.querySelector('[data-p15-runner]')||page.querySelector('[data-crd-more]');card.insertBefore(box,before||null);
      let ta=box.querySelector('[data-p15-intake-text]');ta.value=raw(PACKET);
      ta.oninput=()=>{setRaw(PACKET,ta.value);updateStatus(page)};
      box.querySelector('[data-p15-save]').onclick=()=>{let res=savePacket(ta.value);updateStatus(page);showOut(page,res.ok?'Packet 1.5 saved. Now tap Split Into Units.':'Paste Packet 1.5 first.')};
      box.querySelector('[data-p15-split]').onclick=()=>{let res=splitAndSave(ta.value);updateStatus(page);showOut(page,res.ok?('Packet 1.5 split into '+res.unit_count+' units. The continuous runner will use these units after Start.'):('Cannot split: '+res.reason))};
      box.querySelector('[data-p15-copy-units]').onclick=()=>{let p=unitProof();let ok=copy('PMP PACKET 1.5 INTAKE UNIT PROOF\n'+JSON.stringify(p,null,2));showOut(page,ok?'Unit proof copied.':'Unit proof made; copy may need manual select.')};
      box.querySelector('[data-p15-clear-intake]').onclick=()=>{try{localStorage.removeItem(PACKET);localStorage.removeItem(UNITS);localStorage.removeItem(UNIT_PROOF)}catch(_){ }ta.value='';runnerPatch([]);updateStatus(page);showOut(page,'Packet 1.5 intake cleared.')};
    }
    updateStatus(page);
  }catch(e){}
  }
  function scan(){docs(document).forEach(install)}
  window.PMPPacket15IntakeSectionV1={version:VERSION,splitPacket,splitAndSave,unitProof,scan};
  window.addEventListener('load',()=>[80,220,600,1200,2400].forEach(t=>setTimeout(scan,t)));setInterval(scan,900);scan();
})();
