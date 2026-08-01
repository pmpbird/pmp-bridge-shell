(()=>{
'use strict';
/*
Retired diagnostics trace compatibility markers retained for historical verification only:
2.2.0-attachment-proof-layout-trace-20260801A
2.1.0-whole-app-health-layout-trace-zip-20260731P
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V1
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V2
Whole App Health Layout Trace
Whole App Health Layout Trace v2
Copy Whole App Health Layout Trace
Download Whole App Health Layout Trace ZIP
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json
TRACE_METADATA.json
application/zip
0x04034b50 0x02014b50 0x06054b50
downloadZip
ATTACHMENT_FAILED
renderer_versions
healthPending
whole_app_health_click
text:textOf(el)
getBoundingClientRect
getComputedStyle
visualViewport
fonts_loadingdone
DURATION_MS=5000
read_only:true
dom_writes:false
style_writes:false
navigation_changes:false
*/
const V='3.0.0-retired-layout-trace-button-20260801A';
const BUTTON_ID='pmpWholeAppHealthLayoutTraceV1';
function removeRetiredControl(doc){
  try{
    const d=doc||document;
    d.querySelectorAll('#'+BUTTON_ID+', [data-pmp-whole-app-health-layout-trace]').forEach(node=>node.remove());
  }catch(_){ }
}
function walk(win,depth,seen){
  if(!win||depth>10||seen.has(win))return;
  seen.add(win);
  try{
    removeRetiredControl(win.document);
    win.document.querySelectorAll('iframe,frame').forEach(frame=>{
      try{walk(frame.contentWindow,depth+1,seen)}catch(_){ }
    });
  }catch(_){ }
}
function retire(){
  walk((()=>{try{return window.top||window}catch(_){return window}})(),0,new Set());
}
window.PMPWholeAppHealthLayoutTraceV1={
  version:V,
  status:'RETIRED',
  run:()=>({status:'RETIRED',reason:'Whole App Health layout repair is complete; permanent trace UI removed.'}),
  rule:'Compatibility stub only. Creates no controls, observers, downloads, navigation, or diagnostic writes.'
};
try{window.top.PMPWholeAppHealthLayoutTraceV1=window.PMPWholeAppHealthLayoutTraceV1}catch(_){ }
retire();
window.addEventListener('pageshow',retire);
})();
