(()=>{
'use strict';
const V='2.0.0-inactive-read-only-compatibility';
function inspect(doc){
  const root=doc||document;
  let duplicateSurfaces=0,routeButtons=0;
  try{duplicateSurfaces=root.querySelectorAll('#safeWriterCanonical,[data-pmp-safe-writer-version],section[data-pmp-safe-writer-version]').length}catch(e){}
  try{routeButtons=Array.from(root.querySelectorAll('button,a')).filter(node=>/Open Safe Writer/i.test(String(node.textContent||''))).length}catch(e){}
  return{
    type:'PMP_HIDDEN_SAFE_WRITER_SURFACE_INSPECTION_V2',
    version:V,
    owner:'safe_writer_owner',
    at:new Date().toISOString(),
    read_only:true,
    duplicate_surface_candidates:duplicateSurfaces,
    open_safe_writer_controls:routeButtons
  };
}
window.PMPHiddenSafeWriterSurfaceCleanerV1={
  version:V,
  owner:'safe_writer_owner',
  role:'inactive_read_only_compatibility_inspector',
  inspect,
  scan:inspect,
  rule:'Legacy cleaner is inert. Safe Writer owner alone may mount, route, hide, or remove its surface.'
};
})();
