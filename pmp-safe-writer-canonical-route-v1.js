(()=>{
  if(window.PMPSafeWriterCanonicalRouteV1)return;
  window.PMPSafeWriterCanonicalRouteV1=true;
  const SCREEN_ID='safeWriterCanonical';
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
  function setTab(d,name){
    try{Array.from(d.querySelectorAll('.tab')).forEach(t=>t.classList.toggle('on',textOf(t).toLowerCase().includes(name)))}catch(e){}
  }
  function showScreen(w,d,id){
    try{Array.from(d.querySelectorAll('.screen')).forEach(s=>s.classList.remove('on'));let s=d.getElementById(id);if(s)s.classList.add('on');d.location.hash=id==='control'?'#control':'#safe-writer';setTab(d,id==='control'?'control':'control');if(typeof w.repaintAll==='function')w.repaintAll()}catch(e){}
  }
  function backToControl(w,d){
    try{if(typeof w.go==='function'){w.go('control');setTab(d,'control');return false}}catch(e){}
    showScreen(w,d,'control');
    return false;
  }
  function openResident(w,d){
    try{if(typeof w.openDeepResident==='function')return w.openDeepResident()}catch(e){}
    try{if(typeof w.toggleDrawer==='function')return w.toggleDrawer('resident')}catch(e){}
    return backToControl(w,d);
  }
  function ensureScreen(w,d){
    if(!d||!d.body)return null;
    let existing=d.getElementById(SCREEN_ID);if(existing)return existing;
    let wrap=d.querySelector('.wrap')||d.body;
    let s=d.createElement('section');s.id=SCREEN_ID;s.className='screen';
    s.innerHTML='<div class="card"><h1>Safe Writer v14</h1><p class="sub">Resident is inside Safe Writer. This page uses the normal app shell and returns through Control Room.</p><div class="grid"><button class="mini" data-pmp-safe-writer-resident="1">Resident</button><button class="mini" data-pmp-safe-writer-back="1">Back to Control</button></div></div><div class="card"><h1>PMP Safe Writer</h1><p class="sub">Update machine only. Safe Writer edits, guards, and commits full pmp.html through Safe Update Transaction.</p><div class="panel">Clean split: manage the safe-point bank in Code Safety. Use this page only when changing app code.</div></div><div class="card"><h1>Connection</h1><p class="sub">Safe Writer stays inside this app. Maintenance verification buttons are hidden from the normal user screen.</p></div>';
    wrap.appendChild(s);
    s.querySelector('[data-pmp-safe-writer-back]').onclick=function(e){if(e)e.preventDefault();return backToControl(w,d)};
    s.querySelector('[data-pmp-safe-writer-resident]').onclick=function(e){if(e)e.preventDefault();return openResident(w,d)};
    return s;
  }
  function openSafeWriter(w,d){
    ensureScreen(w,d);
    showScreen(w,d,SCREEN_ID);
    try{localStorage.setItem('pmp_safe_writer_route_fix_v1',JSON.stringify({type:'PMP_SAFE_WRITER_CANONICAL_ROUTE_V1',at:new Date().toISOString(),safe_claim:'Safe Writer opened inside the current app shell with canonical Back to Control and without maintenance verification buttons.',do_not_claim:'This does not activate automation, start Pass 003, or run any verification.'}))}catch(e){}
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
