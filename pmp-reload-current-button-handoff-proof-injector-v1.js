(()=>{
'use strict';
const V='1.0.0-reload-current-button-handoff-proof-injector';
const HANDOFF_KEY='pmp_reload_current_button_handoff_receipt';
function readJson(w,k){try{let raw=w.localStorage.getItem(k);return raw?JSON.parse(raw):null}catch(e){return null}}
function handoffReport(w){let r=readJson(w,HANDOFF_KEY);return{receipt_present:!!r,launcher_version:r&&r.launcher_version||null,maps_tried:r&&r.maps_tried||null,map_selected:r&&r.map_selected||null,current_app_path_selected:r&&r.current_app_path_selected||null,current_app_cache_key_selected:r&&r.current_app_cache_key_selected||null,final_launch_url:r&&r.final_launch_url||null,pass:!!(r&&r.pass===true)}}
function patchInner(win){try{if(!win||win.__pmpReloadCurrentButtonHandoffProofInjected)return false;win.__pmpReloadCurrentButtonHandoffProofInjected=true;let original=win.pmpBuildReloadCurrentProof;if(typeof original!=='function')return false;win.pmpBuildReloadCurrentProof=function(){let proof=original.apply(this,arguments);try{proof.reload_current_button_handoff=handoffReport(win)}catch(e){proof.reload_current_button_handoff={receipt_present:false,launcher_version:null,maps_tried:null,map_selected:null,current_app_path_selected:null,current_app_cache_key_selected:null,final_launch_url:null,pass:false,error:String(e&&e.message||e)}}try{win.PMP_RELOAD_CURRENT_LAST_PROOF=proof}catch(e){}return proof};try{win.PMPPass7ReloadCurrentOwnershipFreshnessProofV1={version:'1.0.2-handoff-receipt-injected',last:()=>win.PMP_RELOAD_CURRENT_LAST_PROOF||null,build:win.pmpBuildReloadCurrentProof}}catch(e){}return true}catch(e){return false}}
function injectInto(doc){try{if(!doc||doc.getElementById('pmpReloadCurrentButtonHandoffProofInjectorV1Inline'))return false;let s=doc.createElement('script');s.id='pmpReloadCurrentButtonHandoffProofInjectorV1Inline';s.textContent='('+patchInner.toString()+')(window);';(doc.head||doc.documentElement).appendChild(s);return true}catch(e){return false}}
function patchFrame(){try{let f=document.getElementById('a')||document.querySelector('iframe');if(!f)return false;let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(!d)return false;injectInto(d);return patchInner(f.contentWindow)}catch(e){return false}}
function install(){patchFrame()}
function receipt(){let r={type:'PMP_RELOAD_CURRENT_BUTTON_HANDOFF_PROOF_INJECTOR_V1_RECEIPT',version:V,localstorage_key:HANDOFF_KEY,patch_target:'existing Reload Current Ownership/Freshness Proof',field_added:'reload_current_button_handoff',side_effects:{route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false},at:new Date().toISOString(),pass:true};try{localStorage.setItem('pmp_reload_current_button_handoff_proof_injector_v1_receipt',JSON.stringify(r,null,2))}catch(e){}return r}
try{window.PMPReloadCurrentButtonHandoffProofInjectorV1={version:V,install,report:()=>handoffReport(window),receipt}}catch(e){}
receipt();
[50,150,350,800,1500,3000,6000,10000].forEach(t=>setTimeout(install,t));
addEventListener('load',()=>[50,150,350,800,1500,3000,6000,10000].forEach(t=>setTimeout(install,t)));
setInterval(install,1500);
})();
