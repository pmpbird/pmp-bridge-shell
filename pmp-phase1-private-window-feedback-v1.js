(()=>{
  if(window.PMPPhase1PrivateWindowFeedbackV1)return;
  window.PMPPhase1PrivateWindowFeedbackV1=true;
  const K={
    sourceBodies:'pmp_medium_source_bodies_v1',
    bodyChainStatus:'pmp_medium_body_chain_status_v1',
    hookReceipts:'pmp_medium_hook_receipts_v1'
  };
  function read(k,f){try{let v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
  function arr(v){return Array.isArray(v)?v:[]}
  function latestPacket(){
    const list=arr(read(K.sourceBodies,[]));
    return list.slice().reverse().find(x=>x&&x.body_id)||null;
  }
  function chain(){return read(K.bodyChainStatus,{accepted_body_list:[],missing_body_list:[],body_order_state:'not_loaded'})||{}}
  function banner(){
    const card=document.getElementById('pmpPhase1PrivateCard');
    if(!card)return null;
    let b=document.getElementById('pmpPhase1FeedbackBanner');
    if(!b){
      b=document.createElement('div');
      b.id='pmpPhase1FeedbackBanner';
      b.style.cssText='background:#f4d35e;color:#07101c;border:3px solid #07101c;border-radius:16px;padding:10px 12px;margin:8px 0;font-weight:950;font-size:18px;line-height:1.2;white-space:pre-wrap;box-shadow:0 4px 12px rgba(0,0,0,.25)';
      b.textContent='READY — tap a Phase 1 button.';
      const note=card.querySelector('.note');
      if(note&&note.nextSibling)card.insertBefore(b,note.nextSibling);else card.insertBefore(b,card.firstChild);
    }
    return b;
  }
  function say(msg,type){
    const b=banner();
    if(!b)return;
    b.textContent=msg;
    if(type==='ok')b.style.background='#b8f7c1';
    else if(type==='warn')b.style.background='#f4d35e';
    else if(type==='bad')b.style.background='#ffb4a8';
    else b.style.background='#d8e8ff';
  }
  function buttonName(t){
    t=String(t||'').replace(/\s+/g,' ').trim();
    if(/Stage/i.test(t))return 'stage';
    if(/Verify/i.test(t))return 'verify';
    if(/Accept/i.test(t))return 'accept';
    if(/Hold/i.test(t))return 'hold';
    if(/Body Chain/i.test(t))return 'chain';
    if(/Receipt/i.test(t))return 'receipts';
    if(/Backup/i.test(t))return 'backup';
    if(/Status/i.test(t))return 'status';
    return 'unknown';
  }
  function summarize(action){
    const p=latestPacket();
    const c=chain();
    const id=p&&p.body_id?p.body_id:'source packet';
    const accepted=arr(c.accepted_body_list);
    const missing=arr(c.missing_body_list);
    if(action==='stage'){
      if(p&&p.acceptance_state==='staged')return say('STAGED — '+id+'\nNext: tap Verify Source.', 'ok');
      if(p)return say('STAGE RESULT — '+id+'\nstate: '+(p.acceptance_state||'unknown')+' / '+(p.verification_state||'unknown'), 'warn');
      return say('NO SOURCE STAGED — paste one body first.', 'bad');
    }
    if(action==='verify'){
      if(p&&p.verification_state==='verified')return say('VERIFY PASSED — '+id+'\nNext: tap Accept Verified Source.', 'ok');
      if(p&&p.verification_state==='failed')return say('VERIFY FAILED — '+id+'\nBlocked: '+arr(p.blocked_claims).join(', '), 'bad');
      if(p)return say('VERIFY RESULT — '+id+'\nstate: '+(p.verification_state||'unknown'), 'warn');
      return say('NO STAGED SOURCE FOUND.', 'bad');
    }
    if(action==='accept'){
      if(p&&p.acceptance_state==='accepted')return say('ACCEPTED — '+id+'\nAccepted bodies: '+accepted.join(', '), 'ok');
      if(p)return say('ACCEPT BLOCKED — '+id+'\nstate: '+(p.acceptance_state||'unknown')+' / '+(p.verification_state||'unknown'), 'bad');
      return say('NO VERIFIED SOURCE FOUND.', 'bad');
    }
    if(action==='hold'){
      if(p)return say('HELD — '+id+'\nThis source is not accepted.', 'warn');
      return say('NO SOURCE FOUND TO HOLD.', 'bad');
    }
    if(action==='chain'){
      return say('BODY CHAIN SHOWN\nAccepted: '+(accepted.length?accepted.join(', '):'none')+'\nMissing: '+missing.length+' bodies\nState: '+(c.body_order_state||'unknown'), accepted.length?'ok':'warn');
    }
    if(action==='receipts'){
      return say('RECEIPTS SHOWN\nTotal hook receipts: '+arr(read(K.hookReceipts,[])).length, 'ok');
    }
    if(action==='backup'){
      return say('PRIVATE BACKUP CREATED\nLocal/private backup only.', 'ok');
    }
    if(action==='status'){
      return say('STATUS SHOWN\nPrivate Window Phase 1 is active.\nAccepted bodies: '+(accepted.length?accepted.join(', '):'none'), 'ok');
    }
  }
  function mount(){
    const card=document.getElementById('pmpPhase1PrivateCard');
    if(!card)return;
    banner();
    if(document.documentElement.dataset.pmpPhase1FeedbackCaptureV1)return;
    document.documentElement.dataset.pmpPhase1FeedbackCaptureV1='1';
    document.addEventListener('click',function(e){
      const btn=e.target&&e.target.closest&&e.target.closest('#pmpPhase1PrivateCard button');
      if(!btn)return;
      const action=buttonName(btn.textContent);
      say('RUNNING — '+btn.textContent.replace(/\s+/g,' ').trim()+'...', 'info');
      setTimeout(()=>summarize(action),120);
      setTimeout(()=>summarize(action),550);
    },true);
  }
  setInterval(mount,700);
  setTimeout(mount,100);
})();
