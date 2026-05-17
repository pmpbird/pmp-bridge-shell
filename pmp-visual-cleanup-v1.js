window.PMPVisualCleanupV1=(function(){
function injectDoc(doc,label){
  try{
    if(!doc||!doc.head)return false;
    let st=doc.getElementById('pmp-visual-cleanup-v1-style');
    if(!st){st=doc.createElement('style');st.id='pmp-visual-cleanup-v1-style';doc.head.appendChild(st)}
    st.textContent=`
.drawer h2{color:#ffffff!important;text-shadow:none!important;opacity:1!important}
.drawer p,.drawer label{color:#f4f8ff!important;opacity:1!important}
.drawer .statusbar,.drawer .note,.drawer .reply{color:#d8ffe2!important;opacity:1!important}
#colorBody>.note{display:none!important}
#colorBody #colorStatus{display:none!important}
#colorBody p.sub{color:var(--text,#07101c)!important;background:transparent!important;box-shadow:none!important;border:0!important;padding:0!important}
#pmpShadowDepthControl .note{display:none!important}
button.mini[onclick*="openDeepResident"]{background:var(--a,var(--accent,#acd1fb))!important;color:var(--buttonText,#07101c)!important;border:2px solid var(--line,#07101c)!important;box-shadow:var(--buttonShadow,var(--shadow,0 12px 28px #0002))!important}
`;
    doc.documentElement.dataset.pmpVisualCleanupV1=label||'applied';
    try{
      Array.from(doc.querySelectorAll('#colorBody .note')).forEach(el=>{
        const t=String(el.textContent||'');
        if(/Shadow is separate|Contrast is separate|Contrast is not a color|Readability saved|Color settings ready/i.test(t))el.style.display='none';
      });
    }catch(e){}
    return true;
  }catch(e){return false}
}
function scan(doc,depth){
  let count=0;if(!doc||depth>6)return 0;
  if(injectDoc(doc,'depth-'+depth))count++;
  try{Array.from(doc.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);count+=scan(d,depth+1)}catch(e){}})}catch(e){}
  return count;
}
function apply(){return{type:'PMP_VISUAL_CLEANUP_REPORT',version:'1.0.0',built_at:new Date().toISOString(),applied_documents:scan(document,0),rule:'UI cleanup only. Makes Launcher/Resident drawer titles readable, hides Color Settings explanation boxes, keeps real sliders and controls, and does not change route, map, permissions, storage routes, or app data.'}}
function start(){apply();[150,500,1200,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,1500)}
return{apply,start};
})();try{window.PMPVisualCleanupV1.start()}catch(e){}