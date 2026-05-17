window.PMPSafeWriterOverlayFixV1=(function(){
function text(el){return String(el&&el.textContent||'').replace(/\s+/g,' ').trim()}
function repaint(){
  try{if(window.PMPNativeContrastBridgeV2&&window.PMPNativeContrastBridgeV2.apply)window.PMPNativeContrastBridgeV2.apply()}catch(e){}
  try{if(window.PMPVisualCleanupV1&&window.PMPVisualCleanupV1.apply)window.PMPVisualCleanupV1.apply()}catch(e){}
}
function closeOverlay(doc){
  try{const ov=doc.getElementById('pmpSafeWriterOverlayCurrentV1');if(ov)ov.remove()}catch(e){}
  try{const w=doc.defaultView;if(w&&typeof w.go==='function')w.go('control');else if(w)w.location.hash='#control'}catch(e){}
  [0,80,200,500,1000].forEach(t=>setTimeout(repaint,t));
  return false;
}
function patchSafeWriterFrame(frame,hostDoc){
  try{
    const fd=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);
    const fw=frame.contentWindow;
    if(!fd||!fw)return false;
    fw.backToControl=function(){return closeOverlay(hostDoc)};
    Array.from(fd.querySelectorAll('button')).forEach(b=>{
      if(/Back to Control|Back to Control Room/i.test(text(b))){
        b.textContent='← Back to Control Room';
        b.onclick=function(e){if(e){e.preventDefault();e.stopPropagation()}return closeOverlay(hostDoc)};
        b.style.background='var(--a,var(--accent,#b1d4ff))';
        b.style.color='var(--buttonText,#07101c)';
        b.style.border='2px solid var(--line,#07101c)';
        b.style.borderRadius='16px';
        b.style.fontWeight='950';
      }
    });
    return true;
  }catch(e){return false}
}
function openOverlay(doc){
  try{
    let old=doc.getElementById('pmpSafeWriterOverlayCurrentV1');if(old)old.remove();
    const ov=doc.createElement('div');
    ov.id='pmpSafeWriterOverlayCurrentV1';
    ov.style.position='fixed';ov.style.inset='0';ov.style.zIndex='999999';ov.style.background='var(--floor,var(--background,#f3ded4))';ov.style.overflow='hidden';
    const frame=doc.createElement('iframe');
    frame.id='pmpSafeWriterFrameCurrentV1';
    frame.title='Safe Writer';
    frame.src='safe-writer-v14.html?embedded=current-overlay&fresh='+Date.now();
    frame.style.position='fixed';frame.style.inset='0';frame.style.width='100%';frame.style.height='100%';frame.style.border='0';frame.style.background='var(--floor,var(--background,#f3ded4))';
    ov.appendChild(frame);doc.body.appendChild(ov);
    frame.onload=function(){patchSafeWriterFrame(frame,doc);setTimeout(()=>patchSafeWriterFrame(frame,doc),250);setTimeout(()=>patchSafeWriterFrame(frame,doc),900)};
    const w=doc.defaultView;
    const timer=w.setInterval(function(){if(!doc.getElementById('pmpSafeWriterOverlayCurrentV1')){w.clearInterval(timer);return}patchSafeWriterFrame(frame,doc)},700);
    return false;
  }catch(e){return false}
}
function patchDoc(doc){
  try{
    if(!doc||!doc.querySelectorAll)return 0;
    let n=0;
    Array.from(doc.querySelectorAll('button,a')).forEach(el=>{
      const t=text(el), href=String(el.getAttribute('href')||''), oc=String(el.getAttribute('onclick')||'');
      if(/Open Safe Writer/i.test(t)||/safe-writer-v14\.html/i.test(href+oc)){
        if(el.dataset.pmpSafeWriterOverlayFix==='1')return;
        el.dataset.pmpSafeWriterOverlayFix='1';
        el.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();return openOverlay(doc)},true);
        if(el.tagName==='BUTTON')el.onclick=function(e){if(e)e.preventDefault();return openOverlay(doc)};
        n++;
      }
    });
    return n;
  }catch(e){return 0}
}
function scan(doc,depth){
  let n=0;if(!doc||depth>6)return 0;
  n+=patchDoc(doc);
  try{Array.from(doc.querySelectorAll('iframe')).forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);n+=scan(d,depth+1)}catch(e){}})}catch(e){}
  return n;
}
function apply(){return{type:'PMP_SAFE_WRITER_OVERLAY_FIX_REPORT',version:'1.0.0',built_at:new Date().toISOString(),patched_controls:scan(document,0),rule:'Open Safe Writer is intercepted into a current-app overlay. Safe Writer Back closes the overlay and returns to the same live Control Room, then reapplies contrast and cleanup. No route, map, permissions, or app data changed.'}}
function start(){apply();[150,500,1200,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,900)}
return{apply,start,openOverlay};
})();try{window.PMPSafeWriterOverlayFixV1.start()}catch(e){}