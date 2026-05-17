window.PMPVisualCleanupV1=(function(){
const REMOVED_ATTR='data-pmp-visual-removed';
function text(el){return String(el&&el.textContent||'').replace(/\s+/g,' ').trim()}
function matchesAny(t,patterns){return patterns.some(p=>p.test(t))}
function removeIfText(doc,selector,patterns){
  let n=0;
  try{
    Array.from(doc.querySelectorAll(selector)).forEach(el=>{
      const t=text(el);
      if(matchesAny(t,patterns)){
        el.setAttribute(REMOVED_ATTR,'true');
        el.style.display='none';
        el.textContent='';
        n++;
      }
    });
  }catch(e){}
  return n;
}
function neutralizeBridgeReady(doc){
  try{
    const bp=doc.getElementById('bridgePanel');
    if(!bp)return 0;
    const t=text(bp);
    if(/^Bridge ready\.?$/i.test(t)){
      bp.setAttribute(REMOVED_ATTR,'bridge-ready');
      bp.textContent='';
      bp.style.display='none';
      return 1;
    }
    if(bp.classList&&bp.classList.contains('panel'))bp.style.display='block';
    return 0;
  }catch(e){return 0}
}
function wireDeepResidentBack(doc){
  let n=0;
  try{
    Array.from(doc.querySelectorAll('button,[onclick]')).forEach(el=>{
      const oc=String(el.getAttribute('onclick')||'');
      const t=text(el);
      if(/openDeepResident/i.test(oc)||/Deep Resident Intelligence/i.test(t)){
        el.setAttribute('onclick',"location.href='resident-control-return-wrapper-v1.html?from=control-room&fresh='+Date.now()");
        el.dataset.pmpResidentBackWrapper='true';
        n++;
      }
    });
  }catch(e){}
  return n;
}
function cleanupBridge(doc){
  let n=0;
  n+=neutralizeBridgeReady(doc);
  n+=removeIfText(doc,'.note',[ /^Tabs:\s*World\s*\/\s*Bridge\s*\/\s*Library\s*\/\s*Workshop\s*\/\s*Control\.?$/i ]);
  return n;
}
function cleanupControl(doc){
  let n=0;
  n+=removeIfText(doc,'#controlStatus,.note',[ /Secret entrance is on the Control Room title\. No movement\. No zoom\.?/i ]);
  n+=removeIfText(doc,'#colorBody p.sub,#colorBody .sub,p.sub',[ /Theme chooses the colors\./i, /Contrast decides how clearly those colors speak\./i ]);
  n+=removeIfText(doc,'#colorBody .note,.note',[ /Shadow is separate/i, /Contrast is separate/i, /Contrast is not a color/i, /Readability saved/i, /Color settings ready/i ]);
  try{const cs=doc.getElementById('colorStatus');if(cs){cs.setAttribute(REMOVED_ATTR,'color-status');cs.textContent='';cs.style.display='none';n++;}}catch(e){}
  n+=wireDeepResidentBack(doc);
  return n;
}
function cleanupPrivateAndBug(doc){
  let n=0;
  n+=removeIfText(doc,'.note,.status,.reply,pre,div,p',[ /^Private window open\.?$/i ]);
  n+=removeIfText(doc,'.note,.status,.reply,pre,div,p',[ /Paste the bug JSON, then tap Prepare Bug Memory\.?/i ]);
  n+=removeIfText(doc,'.note,.status,.reply,pre,div,p',[ /^No memory loaded in this page\.?$/i ]);
  n+=removeIfText(doc,'.note,.status,.reply,pre,div,p',[ /^Bug Lab ready\.?$/i ]);
  return n;
}
function installWatcher(doc){
  try{
    if(doc.__pmpVisualCleanupWatcher)return false;
    doc.__pmpVisualCleanupWatcher=true;
    if(doc.defaultView&&doc.defaultView.MutationObserver){
      const mo=new doc.defaultView.MutationObserver(()=>{
        try{cleanupBridge(doc);cleanupControl(doc);cleanupPrivateAndBug(doc)}catch(e){}
      });
      mo.observe(doc.documentElement,{childList:true,subtree:true,characterData:true});
    }
    return true;
  }catch(e){return false}
}
function injectDoc(doc,label){
  try{
    if(!doc||!doc.head)return false;
    let st=doc.getElementById('pmp-visual-cleanup-v1-style');
    if(!st){st=doc.createElement('style');st.id='pmp-visual-cleanup-v1-style';doc.head.appendChild(st)}
    st.textContent=`
[${REMOVED_ATTR}="true"],[${REMOVED_ATTR}="bridge-ready"],[${REMOVED_ATTR}="color-status"]{display:none!important;visibility:hidden!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important}
.drawer h2{color:#ffffff!important;text-shadow:none!important;opacity:1!important}
.drawer p,.drawer label{color:#f4f8ff!important;opacity:1!important}
.drawer .statusbar,.drawer .note,.drawer .reply{color:#d8ffe2!important;opacity:1!important}
#launcher h2,#resident h2{color:#ffffff!important;text-shadow:none!important;opacity:1!important}
#bridgePanel[${REMOVED_ATTR}="bridge-ready"]{display:none!important;height:0!important;margin:0!important;padding:0!important;border:0!important;box-shadow:none!important;overflow:hidden!important}
#bridgePanel.panel{background:var(--card,#ffffff)!important;color:var(--text,#07101c)!important;border:0!important;box-shadow:none!important;padding:0!important;margin-top:10px!important}
#bridgePanel.panel h1,#bridgePanel.panel h2,#bridgePanel.panel h3,#bridgePanel.panel label,#bridgePanel.panel p{color:var(--text,#07101c)!important;opacity:1!important;text-shadow:none!important}
#bridgePanel.panel .note{background:transparent!important;color:var(--text,#07101c)!important;border:0!important;box-shadow:none!important;padding:8px 0!important}
#bridgePanel.panel textarea,#bridgePanel.panel select,#bridgePanel.panel input{background:var(--input,#0c141e)!important;color:#eef4fb!important;border-color:var(--line,#07101c)!important}
#bridgePanel.panel .mini,#bridgePanel.panel button{background:var(--a,var(--accent,#acd1fb))!important;color:var(--buttonText,#07101c)!important;border:2px solid var(--line,#07101c)!important;box-shadow:var(--buttonShadow,var(--shadow,0 12px 28px #0002))!important}
#control>.card>.sub,#control .card>.sub{color:var(--text,#07101c)!important;opacity:1!important;text-shadow:none!important}
#colorBody>.note,#colorBody #colorStatus,#controlStatus{display:none!important}
#colorBody p.sub{display:none!important}
#pmpShadowDepthControl .note{display:none!important}
button.mini[onclick*="resident-control-return-wrapper"],button.mini[onclick*="openDeepResident"],button[data-pmp-resident-back-wrapper="true"]{background:var(--a,var(--accent,#acd1fb))!important;color:var(--buttonText,#07101c)!important;border:2px solid var(--line,#07101c)!important;box-shadow:var(--buttonShadow,var(--shadow,0 12px 28px #0002))!important}
`;
    doc.documentElement.dataset.pmpVisualCleanupV1=label||'applied';
    let removed=0;
    removed+=cleanupBridge(doc);
    removed+=cleanupControl(doc);
    removed+=cleanupPrivateAndBug(doc);
    installWatcher(doc);
    doc.documentElement.dataset.pmpVisualCleanupRemoved=String(removed);
    return true;
  }catch(e){return false}
}
function scan(doc,depth){
  let count=0;if(!doc||depth>6)return 0;
  if(injectDoc(doc,'depth-'+depth))count++;
  try{Array.from(doc.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);count+=scan(d,depth+1)}catch(e){}})}catch(e){}
  return count;
}
function apply(){return{type:'PMP_VISUAL_CLEANUP_REPORT',version:'1.2.0-dom-removal-and-resident-back',built_at:new Date().toISOString(),applied_documents:scan(document,0),rule:'UI cleanup only. Removes pointless status/instruction box content from the live DOM, prevents Bridge ready from flashing back after Share/Connections close, wires Deep Resident Intelligence through a Back-to-Control wrapper, and does not change route, map, permissions, storage routes, or app data.'}}
function start(){apply();[100,250,500,900,1500,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,700)}
return{apply,start};
})();try{window.PMPVisualCleanupV1.start()}catch(e){}