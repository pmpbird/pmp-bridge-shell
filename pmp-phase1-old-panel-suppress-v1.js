(()=>{
  if(window.PMPPhase1OldPanelSuppressV1)return;
  window.PMPPhase1OldPanelSuppressV1=true;
  function addStyle(){
    if(document.getElementById('pmpPhase1OldPanelSuppressStyleV1'))return;
    const s=document.createElement('style');
    s.id='pmpPhase1OldPanelSuppressStyleV1';
    s.textContent='#pmpPhase1PrivateCard,#pmpPhase1CurrentPanel,#pmpPhase1InlineCard,#pmpFloatP1Btn,#pmpFloatP1Panel{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;height:0!important;max-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;border:0!important}';
    (document.head||document.documentElement).appendChild(s);
  }
  function suppress(){
    addStyle();
    ['pmpPhase1PrivateCard','pmpPhase1CurrentPanel','pmpPhase1InlineCard','pmpFloatP1Btn','pmpFloatP1Panel'].forEach(id=>{
      try{const x=document.getElementById(id);if(x)x.remove()}catch(e){}
    });
    try{localStorage.setItem('pmp_phase1_old_panel_suppressed_v1',JSON.stringify({type:'PMP_PHASE1_OLD_PANEL_SUPPRESSED_V1',at:new Date().toISOString(),safe_claim:'Old stacked Phase 1 panels are hidden/removed so only the single clean Private Window panel remains visible.',do_not_claim:'This does not prove source acceptance, hook validation, full transfer, current-clean, frozen, or best-in-world.'}))}catch(e){}
  }
  suppress();
  setInterval(suppress,120);
})();