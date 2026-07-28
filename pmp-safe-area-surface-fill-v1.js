(()=>{
'use strict';
const V='2.0.0-presentation-local-idempotent-20260727A';
const STYLE_ID='pmpSafeAreaSurfaceFillV1Style';
const BG='#f3ded4',BOOT='#07101c';
let LAST=null;
function now(){return new Date().toISOString()}
function meta(name,content){let m=document.querySelector('meta[name="'+name+'"]');if(!m){m=document.createElement('meta');m.name=name;(document.head||document.documentElement).appendChild(m)}m.content=content}
function apply(reason){
  let style=document.getElementById(STYLE_ID);
  if(!style){style=document.createElement('style');style.id=STYLE_ID;(document.head||document.documentElement).appendChild(style)}
  style.textContent='html,body{margin:0!important;min-height:100%!important;width:100%!important;background:'+BG+'!important;background-color:'+BG+'!important;color-scheme:light;}body:before{content:"";position:fixed;inset:-180px;z-index:-2147483647;background:'+BG+';pointer-events:none;}iframe,#app{background:'+BG+'!important;background-color:'+BG+'!important;}#boot{left:0!important;right:0!important;top:0!important;bottom:0!important;width:auto!important;height:auto!important;border-radius:0!important;border:0!important;margin:0!important;background:'+BOOT+'!important;box-shadow:none!important;padding:calc(env(safe-area-inset-top,0px) + 12px) 12px calc(env(safe-area-inset-bottom,0px) + 12px)!important;}#boot:before{margin-top:0!important;}';
  const boot=!!document.getElementById('boot');
  meta('theme-color',boot?BOOT:BG);meta('apple-mobile-web-app-status-bar-style',boot?'black-translucent':'default');meta('msapplication-navbutton-color',boot?BOOT:BG);
  LAST={type:'PMP_SAFE_AREA_SURFACE_FILL_V2_RECEIPT',version:V,owner:'presentation_local',at:now(),reason:reason||'apply',document_path:String(location.pathname||''),style_id:STYLE_ID,status:'PASS',script_loading:false,dom_removal:false,panel_move:false,panel_hide:false,storage_write:false,recurring_timer:false};
  return LAST;
}
window.PMPSafeAreaSurfaceFillV1={version:V,owner:'presentation_local',apply,last:()=>LAST,rule:'Styles only the current document once. It never loads scripts, removes or hides panels, traverses frames, writes shared storage, or runs a timer.'};
apply('script_load');window.addEventListener('load',()=>apply('window_load'),{once:true});
})();
