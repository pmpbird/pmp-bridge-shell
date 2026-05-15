window.PMPRouteHealthSummaryV1=(function(){
function loadShadowSlider(){
  try{
    if(window.PMPShadowDepthSliderV1){try{window.PMPShadowDepthSliderV1.start()}catch(e){};return {status:'SHADOW_SLIDER_ACTIVE',helper:'pmp-shadow-depth-slider-v1.js',already_loaded:true};}
    if(document.getElementById('pmp-shadow-depth-slider-v1-script'))return {status:'SHADOW_SLIDER_LOADING',helper:'pmp-shadow-depth-slider-v1.js'};
    const s=document.createElement('script');
    s.id='pmp-shadow-depth-slider-v1-script';
    s.src='pmp-shadow-depth-slider-v1.js?fresh=health-summary-v2-shadow-slider-'+Date.now();
    s.onload=function(){try{if(window.PMPShadowDepthSliderV1)window.PMPShadowDepthSliderV1.start()}catch(e){}};
    document.head.appendChild(s);
    return {status:'SHADOW_SLIDER_LOADING',helper:'pmp-shadow-depth-slider-v1.js'};
  }catch(e){return {status:'SHADOW_SLIDER_ERROR',helper:'pmp-shadow-depth-slider-v1.js',error:String(e&&e.message||e)};}
}
function shadowSliderReport(){
  try{
    loadShadowSlider();
    if(window.PMPShadowDepthSliderV1&&typeof window.PMPShadowDepthSliderV1.apply==='function')return window.PMPShadowDepthSliderV1.apply();
  }catch(e){return {type:'PMP_SHADOW_DEPTH_SLIDER_REPORT',version:'error',error:String(e&&e.message||e)};}
  return {type:'PMP_SHADOW_DEPTH_SLIDER_REPORT',version:'loading',shadow_depth:null};
}
function contrastReport(){
  try{
    if(window.PMPNativeContrastBridgeV2&&typeof window.PMPNativeContrastBridgeV2.apply==='function'){
      const r=window.PMPNativeContrastBridgeV2.apply();
      return {
        status:'NATIVE_CONTRAST_ACTIVE',
        bridge:'pmp-native-contrast-bridge-v2.js',
        version:(r&&r.version)||'2.x',
        colors:(r&&r.colors)||null,
        readability:(r&&r.readability)||null,
        shadow_depth:(r&&r.shadow_depth)||null,
        shadows:(r&&r.shadows)||null,
        source:(r&&r.source)||null,
        main_applied:!!(r&&r.main_applied),
        child_frames_applied:(r&&r.child_frames_applied)||0
      };
    }
  }catch(e){
    return {status:'NATIVE_CONTRAST_ERROR',bridge:'pmp-native-contrast-bridge-v2.js',error:String(e&&e.message||e)};
  }
  return {status:'NATIVE_CONTRAST_NOT_SEEN',bridge:'pmp-native-contrast-bridge-v2.js'};
}
function ensureBlockedRepoLink(){
  try{
    const box=document.getElementById('blockDetail');
    if(!box||!box.classList||!box.classList.contains('open'))return false;
    if(document.getElementById('pmp-blocked-repo-index-link-v1'))return true;
    const a=document.createElement('a');
    a.id='pmp-blocked-repo-index-link-v1';
    a.href='pmp-route-guardian-repo-index-v1.html?from=blocked-route-v9&fresh='+Date.now();
    a.textContent='Open Repo Index Diagnostic';
    a.style.display='block';
    a.style.textAlign='center';
    a.style.textDecoration='none';
    a.style.background='var(--accent,var(--a,#acd1fb))';
    a.style.color='#07101c';
    a.style.border='2px solid var(--line,#07101c)';
    a.style.borderRadius='16px';
    a.style.padding='12px';
    a.style.marginTop='10px';
    a.style.fontWeight='950';
    a.style.whiteSpace='normal';
    box.appendChild(a);
    return true;
  }catch(e){return false;}
}
function startBlockedRepoLink(){
  try{
    ensureBlockedRepoLink();
    const box=document.getElementById('blockDetail');
    if(box&&window.MutationObserver){
      const mo=new MutationObserver(()=>setTimeout(ensureBlockedRepoLink,0));
      mo.observe(box,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
    }
    setInterval(ensureBlockedRepoLink,1000);
  }catch(e){}
}
function build(report,cert,recovery){
  const ok=!!(cert&&cert.open_world_allowed===true);
  const lkg=!!(recovery&&recovery.available===true);
  const blocked=ok?[]:((cert&&cert.blocked_reasons)||['unknown block']);
  const contrast=contrastReport();
  const slider=shadowSliderReport();
  const hidden_support={repo_index:'pmp-route-guardian-repo-index-v1.html',repo_index_visibility:ok?'hidden':'blocked_only',resident:'pmp-resident-route-guardian-surface-v2.html'};
  setTimeout(startBlockedRepoLink,0);
  setTimeout(loadShadowSlider,0);
  return {
    type:'PMP_ROUTE_GUARDIAN_HEALTH_SUMMARY',
    version:'2.2.0-native-visuals-shadow-slider-loader',
    built_at:new Date().toISOString(),
    status:ok?'ROUTE_OK':'ROUTE_BLOCKED',
    route_ok:ok,
    route_blocked:!ok,
    open_world_allowed:ok,
    route_confidence:(cert&&cert.route_confidence)||'UNKNOWN',
    last_known_good_status:lkg?'LAST_KNOWN_GOOD_AVAILABLE':'LAST_KNOWN_GOOD_NOT_AVAILABLE',
    last_known_good_available:lkg,
    next_action:ok?'OPEN_WORLD':'COPY_REPORT_AND_USE_LAST_KNOWN_GOOD_FOR_DIAGNOSIS',
    blocker_count:blocked.length,
    blockers:blocked,
    current_surface:(report&&report.current_surface&&report.current_surface.file)||'unknown',
    approved_loader:(cert&&cert.paths&&cert.paths.loader)||'unknown',
    current_inner:(cert&&cert.paths&&cert.paths.current_inner)||'unknown',
    native_contrast_status:contrast.status,
    native_contrast_bridge:contrast.bridge,
    native_contrast_report:contrast,
    native_shadow_depth_status:(slider&&slider.injected_count>0)?'SHADOW_DEPTH_SLIDER_INJECTED':'SHADOW_DEPTH_SLIDER_LOADING_OR_WAITING_FOR_COLOR_PANEL',
    native_shadow_depth_helper:'pmp-shadow-depth-slider-v1.js',
    native_shadow_depth_report:slider,
    hidden_support:hidden_support,
    rule:'Health Summary is read-only. It must not restore, promote, delete, archive, or write app state. Repo Index link appears only inside the blocked-route diagnostic panel. Shadow Depth slider is loaded as a separate visual helper and appears inside the Color Settings panel when that panel exists.'
  };
}
function line(h){
  if(!h)return 'ROUTE_HEALTH_UNKNOWN';
  return h.status+' | '+h.last_known_good_status+' | '+(h.native_contrast_status||'NATIVE_CONTRAST_UNKNOWN')+' | '+(h.native_shadow_depth_status||'SHADOW_DEPTH_UNKNOWN')+' | next: '+h.next_action;
}
setTimeout(startBlockedRepoLink,0);
setTimeout(loadShadowSlider,0);
return{build,line,contrastReport,ensureBlockedRepoLink,startBlockedRepoLink,loadShadowSlider,shadowSliderReport};
})();