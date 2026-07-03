(function(){
  const V='1.0.0-current-return-hook';
  const OWNER='pmp-safe-writer-current-return-fix-v1';
  const KEY='pmp_safe_writer_current_return_fix_v1_receipt';
  const SAFE_URL='safe-writer-v14.html?fresh=safe-writer-current-return-fix-v1-20260703A&from=control-open&return=current-v27&hash=%23control';
  const RULE='Finds the Open Safe Writer button and opens it at the top app level with a fresh URL. No storage overwrite, no bank rebuild, no route map change.';
  function now(){return new Date().toISOString()}
  function txt(el){return String(el&&el.textContent||'').replace(/\s+/g,' ').trim()}
  function isSafeWriter(el){
    if(!el)return false;
    const t=txt(el).toLowerCase();
    const c=String(el.getAttribute&&el.getAttribute('onclick')||el.onclick||'').toLowerCase();
    return (t.includes('open safe writer')||c.includes('safe-writer-v14.html'));
  }
  function openSafeWriter(e){
    try{if(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation&&e.stopImmediatePropagation()}}catch(_e){}
    const url=SAFE_URL+'&t='+Date.now();
    try{window.top.location.href=url}catch(_e){location.href=url}
    return false;
  }
  function patchDoc(d,where){
    let n=0;
    try{
      d.querySelectorAll('button,a,[onclick]').forEach(el=>{
        if(isSafeWriter(el)&&el.dataset.pmpSafeWriterCurrentReturnFix!=='1'){
          el.dataset.pmpSafeWriterCurrentReturnFix='1';
          el.onclick=openSafeWriter;
          try{el.setAttribute('data-safe-writer-return','current-v27-top')}catch(_e){}
          n++;
        }
      });
    }catch(_e){}
    return n;
  }
  function walk(w,depth){
    let n=0;
    if(depth>8)return 0;
    try{n+=patchDoc(w.document,w.location&&w.location.pathname||'window')}catch(_e){}
    try{for(let i=0;i<w.frames.length;i++)n+=walk(w.frames[i],depth+1)}catch(_e){}
    return n;
  }
  function scan(){
    const patched=walk(window,0);
    const r={type:'PMP_SAFE_WRITER_CURRENT_RETURN_FIX_RECEIPT_V1',version:V,owner:OWNER,at:now(),patched_count:patched,open_target:SAFE_URL,rule:RULE};
    try{localStorage.setItem(KEY,JSON.stringify(r))}catch(_e){}
    return r;
  }
  let runs=0;
  function loop(){runs++;scan();if(runs<60)setTimeout(loop,700)}
  window.PMPSafeWriterCurrentReturnFixV1={version:V,owner:OWNER,scan,openSafeWriter,rule:RULE};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loop,{once:true});else loop();
})();
