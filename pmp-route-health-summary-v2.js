window.PMPRouteHealthSummaryV1=(function(){
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
        main_applied:!!(r&&r.main_applied),
        child_frames_applied:(r&&r.child_frames_applied)||0
      };
    }
  }catch(e){
    return {status:'NATIVE_CONTRAST_ERROR',bridge:'pmp-native-contrast-bridge-v2.js',error:String(e&&e.message||e)};
  }
  return {status:'NATIVE_CONTRAST_NOT_SEEN',bridge:'pmp-native-contrast-bridge-v2.js'};
}
function build(report,cert,recovery){
  const ok=!!(cert&&cert.open_world_allowed===true);
  const lkg=!!(recovery&&recovery.available===true);
  const blocked=ok?[]:((cert&&cert.blocked_reasons)||['unknown block']);
  const contrast=contrastReport();
  return {
    type:'PMP_ROUTE_GUARDIAN_HEALTH_SUMMARY',
    version:'2.0.0-native-contrast-v2-proof',
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
    rule:'Health Summary is read-only. It must not restore, promote, delete, archive, or write app state.'
  };
}
function line(h){
  if(!h)return 'ROUTE_HEALTH_UNKNOWN';
  return h.status+' | '+h.last_known_good_status+' | '+(h.native_contrast_status||'NATIVE_CONTRAST_UNKNOWN')+' | next: '+h.next_action;
}
return{build,line,contrastReport};
})();