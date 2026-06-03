(()=>{
  const STATE_KEY='pmp_phase1_private_window_loader_state_v1';
  function writeState(state){try{localStorage.setItem(STATE_KEY,JSON.stringify({type:'PMP_PHASE1_PRIVATE_WINDOW_LOADER_STATE_V1',state,at:new Date().toISOString(),safe_claim:'Phase 1 loader is only injecting the native Private Window panel plus visible feedback.',do_not_claim:'This does not prove source acceptance, hook validation, full transfer, current-clean, frozen, or best-in-world.'}))}catch(e){}}
  function innerDoc(){
    try{if(window.F&&window.F.contentDocument)return window.F.contentDocument}catch(e){}
    try{if(typeof window.inside==='function'){const o=window.inside();if(o&&o.d)return o.d}}catch(e){}
    return null;
  }
  function cleanupOldSurfaces(d){
    try{const old=d&&d.getElementById&&d.getElementById('pmpPhase1InlineCard');if(old)old.remove()}catch(e){}
    try{const oldTop=document.getElementById('pmpFloatP1Btn');if(oldTop)oldTop.remove()}catch(e){}
    try{const oldTopPanel=document.getElementById('pmpFloatP1Panel');if(oldTopPanel)oldTopPanel.remove()}catch(e){}
  }
  function addScript(d,id,src,onState){
    if(d.getElementById(id))return true;
    const s=d.createElement('script');
    s.id=id;
    s.src=src;
    s.onload=()=>writeState(onState+'_loaded');
    s.onerror=()=>writeState(onState+'_failed');
    d.head.appendChild(s);
    writeState(onState+'_injected');
    return true;
  }
  function inject(){
    const d=innerDoc();
    cleanupOldSurfaces(d||document);
    if(!d||!d.head){writeState('waiting_for_inner_document');return false}
    addScript(d,'pmpPhase1PrivateWindowInnerScript','pmp-phase1-private-window-inner-v1.js?fresh=private-window-native-v1-'+Date.now(),'inner_private_window_script');
    addScript(d,'pmpPhase1PrivateWindowFeedbackScript','pmp-phase1-private-window-feedback-v1.js?fresh=private-window-feedback-v1-'+Date.now(),'inner_private_window_feedback');
    return true;
  }
  window.PMPPhase1SourceIntakeCurrentV1={run:inject};
  window.PMPPhase1SourceIntakeCurrentV3=window.PMPPhase1SourceIntakeCurrentV1;
  window.PMPPhase1SourceIntakeCurrentV4=window.PMPPhase1SourceIntakeCurrentV1;
  setInterval(inject,800);
  setTimeout(inject,150);
})();
