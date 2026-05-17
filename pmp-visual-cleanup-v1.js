window.PMPVisualCleanupV1=(function(){
function hideIfText(doc,selector,patterns){
  try{
    Array.from(doc.querySelectorAll(selector)).forEach(el=>{
      const t=String(el.textContent||'').replace(/\s+/g,' ').trim();
      if(patterns.some(p=>p.test(t)))el.style.display='none';
    });
  }catch(e){}
}
function cleanupBridge(doc){
  try{
    const bp=doc.getElementById('bridgePanel');
    if(bp){
      const t=String(bp.textContent||'').replace(/\s+/g,' ').trim();
      if(/^Bridge ready\.?$/i.test(t))bp.style.display='none';
      else bp.style.display='block';
    }
  }catch(e){}
}
function cleanupControl(doc){
  hideIfText(doc,'#controlStatus',[ /Secret entrance is on the Control Room title\. No movement\. No zoom\.?/i ]);
  hideIfText(doc,'#colorBody p.sub',[ /Theme chooses the colors\./i, /Contrast decides how clearly those colors speak\./i ]);
  hideIfText(doc,'#colorBody .note',[ /Shadow is separate/i, /Contrast is separate/i, /Contrast is not a color/i, /Readability saved/i, /Color settings ready/i ]);
  try{const cs=doc.getElementById('colorStatus');if(cs)cs.style.display='none';}catch(e){}
}
function injectDoc(doc,label){
  try{
    if(!doc||!doc.head)return false;
    let st=doc.getElementById('pmp-visual-cleanup-v1-style');
    if(!st){st=doc.createElement('style');st.id='pmp-visual-cleanup-v1-style';doc.head.appendChild(st)}
    st.textContent=`
.drawer h2{color:#ffffff!important;text-shadow:none!important;opacity:1!important}
.drawer p,.drawer label{color:#f4f8ff!important;opacity:1!important}
.drawer .statusbar,.drawer .note,.drawer .reply{color:#d8ffe2!important;opacity:1!important}
#launcher h2,#resident h2{color:#ffffff!important;text-shadow:none!important;opacity:1!important}
#bridgePanel.panel{background:var(--card,#ffffff)!important;color:var(--text,#07101c)!important;border:0!important;box-shadow:none!important;padding:0!important;margin-top:10px!important}
#bridgePanel.panel h1,#bridgePanel.panel h2,#bridgePanel.panel h3,#bridgePanel.panel label,#bridgePanel.panel p{color:var(--text,#07101c)!important;opacity:1!important;text-shadow:none!important}
#bridgePanel.panel .note{background:transparent!important;color:var(--text,#07101c)!important;border:0!important;box-shadow:none!important;padding:8px 0!important}
#bridgePanel.panel textarea,#bridgePanel.panel select,#bridgePanel.panel input{background:var(--input,#0c141e)!important;color:#eef4fb!important;border-color:var(--line,#07101c)!important}
#bridgePanel.panel .mini,#bridgePanel.panel button{background:var(--a,var(--accent,#acd1fb))!important;color:var(--buttonText,#07101c)!important;border:2px solid var(--line,#07101c)!important;box-shadow:var(--buttonShadow,var(--shadow,0 12px 28px #0002))!important}
#control>.card>.sub,#control .card>.sub{color:var(--text,#07101c)!important;opacity:1!important;text-shadow:none!important}
#colorBody>.note,#colorBody #colorStatus,#controlStatus{display:none!important}
#colorBody p.sub{display:none!important}
#pmpShadowDepthControl .note{display:none!important}
button.mini[onclick*="openDeepResident"]{background:var(--a,var(--accent,#acd1fb))!important;color:var(--buttonText,#07101c)!important;border:2px solid var(--line,#07101c)!important;box-shadow:var(--buttonShadow,var(--shadow,0 12px 28px #0002))!important}
`;
    doc.documentElement.dataset.pmpVisualCleanupV1=label||'applied';
    cleanupBridge(doc);
    cleanupControl(doc);
    return true;
  }catch(e){return false}
}
function scan(doc,depth){
  let count=0;if(!doc||depth>6)return 0;
  if(injectDoc(doc,'depth-'+depth))count++;
  try{Array.from(doc.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);count+=scan(d,depth+1)}catch(e){}})}catch(e){}
  return count;
}
function apply(){return{type:'PMP_VISUAL_CLEANUP_REPORT',version:'1.1.0-bridge-control-cleanup',built_at:new Date().toISOString(),applied_documents:scan(document,0),rule:'UI cleanup only. Makes Launcher/Resident drawer titles readable, makes Bridge Share/Connections panels readable, hides useless Bridge ready and Control Room instruction boxes, hides Color Settings explanation text, keeps real sliders and controls, and does not change route, map, permissions, storage routes, or app data.'}}
function start(){apply();[150,500,1200,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,1500)}
return{apply,start};
})();try{window.PMPVisualCleanupV1.start()}catch(e){}