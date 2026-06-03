(()=>{
  const STATE_KEY='pmp_phase1_private_window_loader_state_v1';
  function writeState(state){try{localStorage.setItem(STATE_KEY,JSON.stringify({type:'PMP_PHASE1_PRIVATE_WINDOW_LOADER_STATE_V2_SINGLE_PANEL',state,at:new Date().toISOString(),safe_claim:'Phase 1 loader is injecting one clean Private Window panel only.',do_not_claim:'This does not prove source acceptance, hook validation, full transfer, current-clean, frozen, or best-in-world.'}))}catch(e){}}
  function innerDoc(){
    try{if(window.F&&window.F.contentDocument)return window.F.contentDocument}catch(e){}
    try{if(typeof window.inside==='function'){const o=window.inside();if(o&&o.d)return o.d}}catch(e){}
    return null;
  }
  function cleanupOldSurfaces(d){
    if(!d)return;
    ['pmpPhase1InlineCard','pmpPhase1PrivateCard','pmpPhase1FeedbackBanner','pmpFloatP1Btn','pmpFloatP1Panel'].forEach(id=>{try{const x=d.getElementById(id);if(x)x.remove()}catch(e){}});
    try{const x=document.getElementById('pmpFloatP1Btn');if(x)x.remove()}catch(e){}
    try{const x=document.getElementById('pmpFloatP1Panel');if(x)x.remove()}catch(e){}
  }
  function inject(){
    const d=innerDoc();
    cleanupOldSurfaces(d||document);
    if(!d||!d.head){writeState('waiting_for_inner_document');return false}
    if(!d.getElementById('pmpPhase1PrivateWindowSingleScript')){
      const s=d.createElement('script');
      s.id='pmpPhase1PrivateWindowSingleScript';
      s.src='pmp-phase1-private-window-single-v1.js?fresh=single-panel-v1-'+Date.now();
      s.onload=()=>writeState('single_private_window_panel_loaded');
      s.onerror=()=>writeState('single_private_window_panel_failed');
      d.head.appendChild(s);
      writeState('single_private_window_panel_injected');
    } else {
      writeState('single_private_window_panel_already_present');
    }
    return true;
  }
  window.PMPPhase1SourceIntakeCurrentV1={run:inject};
  window.PMPPhase1SourceIntakeCurrentV3=window.PMPPhase1SourceIntakeCurrentV1;
  window.PMPPhase1SourceIntakeCurrentV4=window.PMPPhase1SourceIntakeCurrentV1;
  setInterval(inject,800);
  setTimeout(inject,150);
})();