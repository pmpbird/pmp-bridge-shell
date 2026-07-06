(()=>{
'use strict';
const V='1.0.0-reload-current-live-update-gate';
const MARKER='pmp-reload-current-live-update-marker-v1.json';
const TARGET='pmp-current-inner-cleanbug-rgcontrols-v29.html';
const KEY='pmp_reload_current_live_update_gate_v1_receipt';
let last=null;
function hash(){return /^#(world|bridge|library|workshop|control|bank)$/i.test(location.hash||'')?location.hash:'#control'}
function frame(){return document.getElementById('a')||document.querySelector('iframe')}
function receipt(status,extra){const r=Object.assign({type:'PMP_RELOAD_CURRENT_LIVE_UPDATE_GATE_V1_RECEIPT',version:V,mode:'passive_reload_current_frame_only',marker:MARKER,target:TARGET,status,at:new Date().toISOString(),side_effects:{route_change_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false}},extra||{});try{localStorage.setItem(KEY,JSON.stringify(r,null,2))}catch(e){}return r}
function freshSrc(rev){return TARGET+'?fresh=live-update-gate-'+encodeURIComponent(String(rev||Date.now()))+'-'+Date.now()+hash()}
async function check(reason){try{const res=await fetch(MARKER+'?fresh='+Date.now(),{cache:'no-store'});const m=await res.json();const rev=String(m.revision||m.updated_at||m.version||'');if(!rev)return receipt('marker_without_revision',{reason});if(last===null){last=rev;return receipt('ready',{reason,revision:rev})}if(rev!==last){last=rev;const f=frame();if(f)f.src=freshSrc(rev);return receipt('frame_refreshed',{reason,revision:rev})}return receipt('no_change',{reason,revision:rev})}catch(e){return receipt('check_error',{reason,error:String(e&&e.message||e)})}}
window.PMPReloadCurrentLiveUpdateGateV1={version:V,check,last:()=>last,marker:MARKER,target:TARGET};
[300,1200,3000,6000].forEach(t=>setTimeout(()=>check('startup_'+t),t));
setInterval(()=>check('interval'),5000);
receipt('installed',{});
})();