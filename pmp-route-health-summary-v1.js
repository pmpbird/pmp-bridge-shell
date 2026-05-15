window.PMPRouteHealthSummaryV1=(function(){
function build(report,cert,recovery){
  const ok=!!(cert&&cert.open_world_allowed===true);
  const lkg=!!(recovery&&recovery.available===true);
  const blocked=ok?[]:((cert&&cert.blocked_reasons)||['unknown block']);
  return {
    type:'PMP_ROUTE_GUARDIAN_HEALTH_SUMMARY',
    version:'1.0.1-native-contrast',
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
    native_contrast_bridge:'pmp-native-contrast-bridge-v1.js',
    rule:'Health Summary is read-only. It must not restore, promote, delete, archive, or write app state.'
  };
}
function line(h){
  if(!h)return 'ROUTE_HEALTH_UNKNOWN';
  return h.status+' | '+h.last_known_good_status+' | next: '+h.next_action;
}
function loadNativeContrast(){
  try{
    if(window.PMPNativeContrastBridgeV1&&typeof window.PMPNativeContrastBridgeV1.start==='function'){
      window.PMPNativeContrastBridgeV1.start();
      return;
    }
    if(document.getElementById('pmp-native-contrast-bridge-v1-script'))return;
    const s=document.createElement('script');
    s.id='pmp-native-contrast-bridge-v1-script';
    s.src='pmp-native-contrast-bridge-v1.js?fresh=route-health-summary-v101';
    s.async=false;
    document.head.appendChild(s);
  }catch(e){}
}
loadNativeContrast();
return{build,line,loadNativeContrast};
})();