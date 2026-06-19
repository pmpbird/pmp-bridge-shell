(()=>{
  if(window.PMPSafeWriterCanonicalRouteV1)return;
  window.PMPSafeWriterCanonicalRouteV1=true;
  const SCREEN_ID='safeWriterCanonical';
  const REQ_KEY='pmp_safe_writer_request_v1';
  const OUT_KEY='pmp_safe_writer_output_v1';
  function textOf(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
  function deepestApp(){
    let w=window,d=document,last={w,d};
    for(let i=0;i<8;i++){
      try{
        let f=(d&&d.getElementById&&d.getElementById('app'))||(d&&d.querySelector&&d.querySelector('iframe'));
        if(!f||!f.contentWindow||!f.contentDocument)break;
        w=f.contentWindow;d=f.contentDocument;last={w,d};
        if(d.getElementById&&d.getElementById('control'))return{w,d};
      }catch(e){break}
    }
    return last;
  }
  function setTab(d,name){try{Array.from(d.querySelectorAll('.tab')).forEach(t=>t.classList.toggle('on',textOf(t).toLowerCase().includes(name)))}catch(e){}}
  function showScreen(w,d,id){try{Array.from(d.querySelectorAll('.screen')).forEach(s=>s.classList.remove('on'));let s=d.getElementById(id);if(s)s.classList.add('on');d.location.hash=id==='control'?'#control':'#safe-writer';setTab(d,'control');if(typeof w.repaintAll==='function')w.repaintAll()}catch(e){}}
  function backToControl(w,d){try{if(typeof w.go==='function'){w.go('control');setTab(d,'control');return false}}catch(e){}showScreen(w,d,'control');return false}
  function safeWriterDraft(d){
    let req=d.getElementById('pmpSafeWriterRequestV1');
    let out=d.getElementById('pmpSafeWriterOutputV1');
    if(!req||!out)return false;
    let request=req.value.trim();
    if(!request){out.value='Write the app change you want Safe Writer to guard first.';return false}
    let text='SAFE WRITER REQUEST\n\nGoal:\n'+request+'\n\nRules:\n- Keep the normal app shell.\n- Keep Back to Control.\n- Do not activate automation.\n- Do not start Pass 003.\n- Do not add maintenance-only buttons to normal user screens.\n- Return through the canonical Control Room route.\n\nNext action:\nTurn this into a guarded app-update patch or a clear no-change reason.';
    out.value=text;
    try{localStorage.setItem(REQ_KEY,request);localStorage.setItem(OUT_KEY,text)}catch(e){}
    return false;
  }
  async function copySafeWriter(d){
    let out=d.getElementById('pmpSafeWriterOutputV1');let text=out&&out.value||'';
    if(!text.trim())safeWriterDraft(d),text=out&&out.value||'';
    try{await navigator.clipboard.writeText(text);out.value=text+'\n\nCopied.'}catch(e){out.value=text+'\n\nCopy failed. Select and copy this text manually.'}
    return false;
  }
  function ensureScreen(w,d){
    if(!d||!d.body)return null;
    let existing=d.getElementById(SCREEN_ID);if(existing)return existing;
    let wrap=d.querySelector('.wrap')||d.body;
    let s=d.createElement('section');s.id=SCREEN_ID;s.className='screen';
    s.innerHTML='<div class="card"><h1>Safe Writer v14</h1><p class="sub">Resident is inside Safe Writer. This page uses the normal app shell and returns through Control Room.</p><button class="mini" data-pmp-safe-writer-back="1">Back to Control</button></div><div class="card"><h1>PMP Safe Writer</h1><p class="sub">Write the app change here. Safe Writer turns it into a guarded update request without starting automation.</p><textarea id="pmpSafeWriterRequestV1" placeholder="Describe the app change you want to make..."></textarea><div class="grid"><button class="mini" data-pmp-safe-writer-prepare="1">Prepare Safe Update Request</button><button class="mini" data-pmp-safe-writer-copy="1">Copy Request</button></div><textarea id="pmpSafeWriterOutputV1" placeholder="Safe Writer output appears here."></textarea><div class="panel">Safe Writer is for app-code changes only. It does not activate automation, start Pass 003, or run maintenance verification.</div></div>';
    wrap.appendChild(s);
    let req=s.querySelector('#pmpSafeWriterRequestV1'),out=s.querySelector('#pmpSafeWriterOutputV1');
    try{req.value=localStorage.getItem(REQ_KEY)||'';out.value=localStorage.getItem(OUT_KEY)||''}catch(e){}
    s.querySelector('[data-pmp-safe-writer-back]').onclick=function(e){if(e)e.preventDefault();return backToControl(w,d)};
    s.querySelector('[data-pmp-safe-writer-prepare]').onclick=function(e){if(e)e.preventDefault();return safeWriterDraft(d)};
    s.querySelector('[data-pmp-safe-writer-copy]').onclick=function(e){if(e)e.preventDefault();return copySafeWriter(d)};
    return s;
  }
  function openSafeWriter(w,d){
    ensureScreen(w,d);
    showScreen(w,d,SCREEN_ID);
    try{localStorage.setItem('pmp_safe_writer_route_fix_v1',JSON.stringify({type:'PMP_SAFE_WRITER_CANONICAL_ROUTE_V1',at:new Date().toISOString(),safe_claim:'Safe Writer opened inside the current app shell with Back to Control and usable request/copy controls.',do_not_claim:'This does not activate automation, start Pass 003, run verification, or create a commit by itself.'}))}catch(e){}
    return false;
  }
  function patch(){
    const o=deepestApp(),w=o.w,d=o.d;if(!d||!d.querySelectorAll)return;
    ensureScreen(w,d);
    Array.from(d.querySelectorAll('button')).forEach(b=>{
      const t=textOf(b);
      if(/Open Safe Writer/i.test(t)){
        b.onclick=function(e){if(e){e.preventDefault();e.stopPropagation()}return openSafeWriter(w,d)};
        if(!b.dataset.pmpSafeWriterCanonicalRouteV1){
          b.dataset.pmpSafeWriterCanonicalRouteV1='1';
          b.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();return openSafeWriter(w,d)},true);
        }
      }
    });
    try{w.openSafeWriter=function(){return openSafeWriter(w,d)}}catch(e){}
  }
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(patch,t)));
  setInterval(patch,700);
  patch();
})();
