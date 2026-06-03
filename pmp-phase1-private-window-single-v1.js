(()=>{
  if(window.PMPPhase1PrivateWindowSingleV1)return;
  window.PMPPhase1PrivateWindowSingleV1=true;

  const EXPECTED=Array.from({length:22},(_,i)=>'BODY-'+String(i).padStart(3,'0'));
  const K={
    sourceBodies:'pmp_medium_source_bodies_v1',
    manifestRecords:'pmp_medium_manifest_records_v1',
    supportObjects:'pmp_medium_support_source_objects_v1',
    sourceReceipts:'pmp_medium_source_packet_receipts_v1',
    hookReceipts:'pmp_medium_hook_receipts_v1',
    transferReceipts:'pmp_medium_transfer_receipts_v1',
    bodyChain:'pmp_medium_body_chain_status_v1',
    privateBackup:'pmp_private_backup_latest_v1'
  };

  const now=()=>new Date().toISOString();
  const arr=v=>Array.isArray(v)?v:[];
  function read(k,f){try{let v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){return false}}
  function uniq(a){return [...new Set(a.filter(Boolean))]}
  function bodyId(s){let m=String(s||'').match(/BODY[-_ ]?(\d{3})/i);return m?'BODY-'+m[1]:''}
  function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return 'local_fnv32_'+(h>>>0).toString(16)+'_'+s.length}
  function line(raw,label){let target=label.toLowerCase().replace(/[-_ ]/g,'');for(const row of String(raw||'').split(/\r?\n/)){let x=row.trim(),i=x.indexOf(':');if(i<0)continue;let k=x.slice(0,i).toLowerCase().replace(/[-_ ]/g,'');if(k===target)return x.slice(i+1).trim()}return''}
  function section(raw,label){let txt=String(raw||''),i=txt.toLowerCase().indexOf(label.toLowerCase());if(i<0)return'';let p=txt.slice(i+label.length).replace(/^\s*:?\s*/,'');let m=p.search(/\n[A-Z][A-Z0-9 _\/-]{2,}:|\n[-=]{4,}/);return(m>=0?p.slice(0,m):p).trim()}

  function classify(raw){
    const u=String(raw||'').toUpperCase(), b=bodyId(raw);
    if(b&&EXPECTED.includes(b))return 'body';
    if(/MANIFEST/.test(u)&&/BODY-000/.test(u))return 'manifest';
    if(/HOOK REGISTRY/.test(u))return 'hook_registry';
    if(/LOSSLESS TRANSFER MEDIUM|MOLD-TO-APP LOSSLESS TRANSFER/.test(u))return 'transfer_medium';
    if(/APP WIRING PHASE/.test(u))return 'app_wiring_phase';
    if(/RECEIVER CARD/.test(u))return 'receiver_card';
    if(/PMP|BUG MOLD|APP WIRING|SOURCE/.test(u))return 'unknown_support';
    return 'unknown';
  }

  function parse(raw){
    raw=String(raw||'');
    const cls=classify(raw), b=bodyId(raw);
    const endLine=(raw.match(/^\s*END\b.*$/gim)||[]).slice(-1)[0]||'';
    let endBody=bodyId(endLine);
    if(!endBody){let m=raw.match(/END[\s\S]{0,200}?BODY[-_ ]?(\d{3})/i);if(m)endBody='BODY-'+m[1]}
    const safe=section(raw,'SAFE CLAIM')||line(raw,'SAFE CLAIM');
    const dnc=section(raw,'DO-NOT-CLAIM')||section(raw,'DO NOT CLAIM')||line(raw,'DO-NOT-CLAIM')||line(raw,'DO NOT CLAIM');
    const hs=hash(raw);
    return {
      source_packet_id:'packet_'+(b||cls)+'_'+hs,
      source_packet_class:cls,
      source_packet_title:line(raw,'SOURCE PACKET TITLE')||line(raw,'TITLE')||line(raw,'BODY NAME')||b||cls,
      source_packet_version:line(raw,'SOURCE PACKET VERSION')||line(raw,'PACKET VERSION')||line(raw,'VERSION'),
      body_id:b,
      body_name:line(raw,'BODY NAME'),
      body_version:line(raw,'BODY VERSION'),
      body_type:line(raw,'BODY TYPE'),
      mold_name:line(raw,'MOLD NAME'),
      mold_version:line(raw,'MOLD VERSION'),
      wrapper_reference:line(raw,'WRAPPER REFERENCE')||line(raw,'WRAPPER'),
      source_set_class:line(raw,'SOURCE SET CLASS'),
      compression_state:line(raw,'COMPRESSION STATE')||line(raw,'COMPRESSION')||(/\bCOMPRESSION\s*:?\s*NO\b/i.test(raw)?'no':''),
      begin_marker_seen:/^\s*BEGIN\b/im.test(raw),
      end_marker_seen:/^\s*END\b/im.test(raw),
      end_marker_purpose_seen:/END\s+MARKER\s+PURPOSE/i.test(raw),
      end_body_id:endBody,
      body_id_match_state:b&&endBody?(b===endBody?'match':'mismatch'):(b?'end_body_id_not_found':'body_id_not_found'),
      safe_claim_text:safe,
      do_not_claim_text:dnc,
      raw_source_text:raw,
      raw_source_hash:hs,
      created_at:now(),
      updated_at:now(),
      verification_state:'pasted',
      acceptance_state:'pasted',
      blocked_claims:[],
      safe_claim:safe||'source staged only',
      do_not_claim:dnc||'do not call accepted'
    };
  }

  function storeKey(p){return p.source_packet_class==='body'?K.sourceBodies:p.source_packet_class==='manifest'?K.manifestRecords:K.supportObjects}
  function savePacket(p){
    const k=storeKey(p), list=arr(read(k,[]));
    const i=list.findIndex(x=>x.source_packet_id===p.source_packet_id);
    if(i>=0)list[i]={...list[i],...p,updated_at:now()}; else list.push(p);
    write(k,list);
    return i>=0?list[i]:p;
  }
  function receipt(kind,p){
    const r={receipt_id:'receipt_'+Date.now()+'_'+Math.random().toString(36).slice(2,7),kind,created_at:now(),surface:'single_private_window_panel',...(p||{})};
    const h=arr(read(K.hookReceipts,[])); h.push(r); write(K.hookReceipts,h.slice(-500));
    const t=arr(read(K.transferReceipts,[])); t.push({receipt_id:r.receipt_id,type:'PMP_PHASE1_SINGLE_PANEL_RECEIPT_V1',kind,created_at:r.created_at,safe_claim:'Single Private Window panel receipt only.',do_not_claim:'Not hook validation, real app proof, full transfer, current-clean, frozen, or best-in-world.'}); write(K.transferReceipts,t.slice(-500));
    return r;
  }
  function currentRaw(){return document.getElementById('pmpPhase1SingleText')?.value||''}
  function currentPacket(){const raw=currentRaw();return raw.trim()?parse(raw):null}

  function verifyPacket(p){
    const err=[], hold=[];
    if(p.source_packet_class==='body'){
      if(!p.begin_marker_seen)err.push('BEGIN marker missing');
      if(!p.end_marker_seen)err.push('END marker missing');
      if(!p.body_id)err.push('BODY ID missing');
      if(p.end_body_id&&p.body_id!==p.end_body_id)err.push('BODY ID does not match END BODY ID');
      if(!/^no\b/i.test(String(p.compression_state||'')))err.push('COMPRESSION: no missing');
      if(!p.safe_claim_text)err.push('SAFE CLAIM missing');
      if(!p.do_not_claim_text)err.push('DO-NOT-CLAIM missing');
    } else if(p.source_packet_class==='manifest'){
      if(!p.begin_marker_seen)err.push('manifest BEGIN marker missing');
      if(!p.end_marker_seen)err.push('manifest END marker missing');
    } else {
      if(!p.begin_marker_seen)hold.push('BEGIN marker not found for support object');
      if(!p.end_marker_seen)hold.push('END marker not found for support object');
    }
    p.verification_state=err.length?'failed':(hold.length?'held':'verified');
    if(err.length)p.acceptance_state='held';
    p.blocked_claims=err.concat(hold);
    p.safe_claim=err.length?'source staged only':(hold.length?'source held with reason':'source verified only; not accepted until acceptance gate runs');
    p.do_not_claim='Verified is not accepted unless acceptance gate is run.';
    return p;
  }

  function buildChain(){
    const bodies=arr(read(K.sourceBodies,[]));
    const accepted=uniq(bodies.filter(x=>x.acceptance_state==='accepted'&&x.body_id).map(x=>x.body_id)).sort();
    const held=uniq(bodies.filter(x=>x.acceptance_state==='held').map(x=>x.body_id||x.source_packet_id)).sort();
    const rejected=uniq(bodies.filter(x=>x.acceptance_state==='rejected').map(x=>x.body_id||x.source_packet_id)).sort();
    const missing=EXPECTED.filter(x=>!accepted.includes(x));
    const cnt={}; bodies.filter(x=>x.acceptance_state==='accepted'&&x.body_id).forEach(x=>cnt[x.body_id]=(cnt[x.body_id]||0)+1);
    const duplicate=Object.keys(cnt).filter(x=>cnt[x]>1);
    const out={expected_body_range:'BODY-000 through BODY-021',accepted_body_list:accepted,held_body_list:held,rejected_body_list:rejected,missing_body_list:missing,duplicate_body_list:duplicate,body_order_state:missing.length?'incomplete':(duplicate.length?'duplicate_blocked':'complete_in_order'),body_gap_state:missing.length?'gaps_present':'no_gaps_in_expected_range',body_chain_safe_claim:missing.length?'Body chain incomplete; missing bodies remain not_loaded/not_accepted.':'All BODY-000 through BODY-021 locally accepted; manifest/runtime proof still required.',body_chain_do_not_claim:'Do not claim source-set current, manifest-current, app wired, hook validated, lossless, frozen, best-in-world, or current-clean from body chain alone.',updated_at:now()};
    write(K.bodyChain,out); receipt('body_chain_status_built',{hook_id:'HOOK-003',proof_state:out.body_order_state});
    return out;
  }

  function setOut(x){const o=document.getElementById('pmpPhase1SingleOut'); if(o)o.textContent=typeof x==='string'?x:JSON.stringify(x,null,2)}
  function banner(msg,type){const b=document.getElementById('pmpPhase1SingleBanner'); if(!b)return; b.textContent=msg; b.style.background=type==='bad'?'#ffb4a8':type==='warn'?'#f4d35e':type==='info'?'#d8e8ff':'#b8f7c1'}

  function stage(){
    let p=currentPacket();
    if(!p){banner('NO SOURCE — paste one body first.','bad'); return setOut('Paste one source packet first.');}
    p.verification_state='staged'; p.acceptance_state='staged'; p=savePacket(p);
    const sr=arr(read(K.sourceReceipts,[])); sr.push({source_packet_id:p.source_packet_id,source_packet_class:p.source_packet_class,body_id:p.body_id,raw_source_hash:p.raw_source_hash,stage_state:'staged',created_at:now(),safe_claim:'Source staged with raw text preserved exactly as pasted.',do_not_claim:'Staged is not verified, accepted, wired, current, or lossless.'}); write(K.sourceReceipts,sr.slice(-500));
    receipt('source_staged',{hook_id:'HOOK-001',input_source:p.source_packet_id,proof_state:'staged'});
    banner('STAGED — '+(p.body_id||p.source_packet_class)+'\nNext: tap Verify Source.','ok'); setOut(p);
  }
  function verify(){
    let p=currentPacket();
    if(!p){banner('NO SOURCE — paste one body first.','bad'); return setOut('Paste one source packet first.');}
    p=verifyPacket(p); p=savePacket(p);
    receipt('source_verified',{hook_id:p.source_packet_class==='body'?'HOOK-001/HOOK-002':'HOOK-004/HOOK-005',input_source:p.source_packet_id,proof_state:p.verification_state});
    if(p.source_packet_class==='body')buildChain();
    banner(p.verification_state==='verified'?'VERIFY PASSED — '+(p.body_id||p.source_packet_class)+'\nNext: tap Accept Verified Source.':'VERIFY '+p.verification_state.toUpperCase()+' — '+(p.body_id||p.source_packet_class),p.verification_state==='verified'?'ok':p.verification_state==='failed'?'bad':'warn'); setOut(p);
  }
  function accept(){
    let p=currentPacket();
    if(!p){banner('NO SOURCE — paste one body first.','bad'); return setOut('Paste one source packet first.');}
    p=verifyPacket(p);
    if(p.verification_state!=='verified'){
      p.acceptance_state='held'; p=savePacket(p); receipt('accept_blocked',{input_source:p.source_packet_id,proof_state:p.verification_state});
      banner('ACCEPT BLOCKED — '+(p.body_id||p.source_packet_class)+'\n'+p.blocked_claims.join(', '),'bad'); return setOut(p);
    }
    p.acceptance_state='accepted';
    p.safe_claim=p.source_packet_class==='body'?'body accepted into local body chain only':'source packet accepted only within its source class';
    p.do_not_claim=p.source_packet_class==='body'?'Accepted locally does not prove app wiring, hook validation, lossless transfer, GitHub Vault proof, Notes proof, current-clean, frozen, or best-in-world.':'Support/manifest acceptance does not count as BODY-000 through BODY-021 or prove implementation.';
    p=savePacket(p); receipt('source_accepted',{hook_id:p.source_packet_class==='body'?'HOOK-003':'HOOK-004/HOOK-005',input_source:p.source_packet_id,proof_state:'accepted_local_only'});
    const c=p.source_packet_class==='body'?buildChain():read(K.bodyChain,{});
    banner('ACCEPTED — '+(p.body_id||p.source_packet_class)+'\nAccepted bodies: '+arr(c.accepted_body_list).join(', '),'ok'); setOut(p);
  }
  function hold(){let p=currentPacket(); if(!p){banner('NO SOURCE TO HOLD.','bad'); return setOut('No source found.')} p.acceptance_state='held'; p.held_reason='held from single Private Window panel'; p=savePacket(p); receipt('source_held',{input_source:p.source_packet_id,proof_state:'held'}); banner('HELD — '+(p.body_id||p.source_packet_class),'warn'); setOut(p)}
  function status(){const c=buildChain(); const x={type:'PMP_PHASE1_SINGLE_PRIVATE_WINDOW_STATUS_V1',built_at:now(),surface:'single_inner_private_window_panel',accepted_bodies:arr(c.accepted_body_list).length,accepted_body_list:c.accepted_body_list,missing_body_list:c.missing_body_list,safe_claim:'One clean Private Window panel is active. Stage, Verify, and Accept all use the visible paste box only.',do_not_claim:'Not hook validation, real app proof, full transfer, current-clean, frozen, or best-in-world.'}; banner('STATUS SHOWN\nAccepted: '+x.accepted_bodies+' bodies','ok'); setOut(x)}
  function receipts(){const x={hook_receipts:arr(read(K.hookReceipts,[])).slice(-50),transfer_receipts:arr(read(K.transferReceipts,[])).slice(-50)}; banner('RECEIPTS SHOWN\nTotal hook receipts: '+arr(read(K.hookReceipts,[])).length,'ok'); setOut(x)}
  function backup(){const c=buildChain(); const d={type:'PMP_PRIVATE_WINDOW_BACKUP_V1',app_wrapper:'PMP Current / Single Private Window Phase 1 v1',built_at:now(),summary:{accepted_body_list:c.accepted_body_list,missing_body_list:c.missing_body_list},safe_claim:'Private backup contains localStorage PMP keys only.',do_not_claim:'Private backup is not GitHub Vault proof, not Apple Notes proof, not real app validation, and not full source transfer proof.',keys:{}}; for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i); if(k&&k.startsWith('pmp_'))d.keys[k]=localStorage.getItem(k)} write(K.privateBackup,d); receipt('private_backup_created',{hook_id:'HOOK-005',proof_state:'local_backup_created'}); banner('PRIVATE BACKUP CREATED\nLocal/private backup only.','ok'); setOut(d)}
  function route(a){if(a==='stage')stage(); else if(a==='verify')verify(); else if(a==='accept')accept(); else if(a==='hold')hold(); else if(a==='chain'){const c=buildChain(); banner('BODY CHAIN SHOWN\nAccepted: '+arr(c.accepted_body_list).join(', ')+'\nMissing: '+arr(c.missing_body_list).length+' bodies\nState: '+c.body_order_state,'ok'); setOut(c)} else if(a==='receipts')receipts(); else if(a==='backup')backup(); else status()}

  function mount(){
    const host=document.getElementById('secretPanel');
    if(!host)return;
    if(document.getElementById('pmpPhase1SingleCard'))return;
    const old=document.getElementById('pmpPhase1PrivateCard'); if(old)old.remove();
    const card=document.createElement('div'); card.id='pmpPhase1SingleCard'; card.className='panel'; card.style.marginTop='12px';
    card.innerHTML='<h2>Phase 1 Source Intake</h2><div class="note">Single clean Private Window panel. Every button uses only the text currently in this box.</div><div id="pmpPhase1SingleBanner" style="background:#d8e8ff;color:#07101c;border:3px solid #07101c;border-radius:16px;padding:10px 12px;margin:8px 0;font-weight:950;font-size:18px;line-height:1.2;white-space:pre-wrap">READY — paste one body, then Stage / Verify / Accept.</div><textarea id="pmpPhase1SingleText" placeholder="Paste one BODY here. Raw source is stored exactly as pasted." style="min-height:160px"></textarea><div id="pmpPhase1SingleBtns" class="grid"></div><pre id="pmpPhase1SingleOut" class="note">Tap Phase 1 Status first.</pre>';
    host.appendChild(card);
    [['Phase 1 Status','status'],['Stage Source','stage'],['Verify Source','verify'],['Accept Visible Source','accept'],['Hold Source','hold'],['Show Body Chain','chain'],['Show Receipts','receipts'],['Private Backup','backup']].forEach(([label,act])=>{let b=document.createElement('button'); b.type='button'; b.className='mini'; b.textContent=label; b.onclick=e=>{if(e){e.preventDefault(); e.stopPropagation(); if(e.stopImmediatePropagation)e.stopImmediatePropagation()} banner('RUNNING — '+label+'...','info'); setTimeout(()=>route(act),10); return false}; document.getElementById('pmpPhase1SingleBtns').appendChild(b)});
  }
  setInterval(mount,500); setTimeout(mount,100);
})();