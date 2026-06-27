(()=>{
  const V='1.0.0-bridge-old-launcher-reload-to-reload-current';
  const KEY='pmp_launcher_reload_current_bridge_v1_receipt';
  function T(){try{return top||window}catch(e){return window}}
  function write(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
  function txt(x){return String((x&&x.textContent)||'').replace(/\s+/g,' ').trim()}
  function docs(d,a,n){a=a||[];n=n||0;if(!d||n>12)return a;try{a.push(d);d.querySelectorAll('iframe,frame').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
  function engine(){let w=T();return w.PMPBankReloadCurrentButtonV1||w.PMPLiveReloadRestoreV12||null}
  async function reloadCurrent(e,button){try{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let eng=engine();write({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:eng?'ROUTING_OLD_LAUNCHER_RELOAD_TO_RELOAD_CURRENT':'RELOAD_CURRENT_ENGINE_NOT_FOUND',button_text:txt(button)});if(eng&&typeof eng.run==='function')return await eng.run({preventDefault(){},stopPropagation(){},stopImmediatePropagation(){},currentTarget:button||null});let w=T();w.location.replace(String(w.location.href).split('#')[0].replace(/[?&]fresh=[^&#]*/g,'')+(String(w.location.href).includes('?')?'&':'?')+'fresh=launcher-bridge-fallback-'+Date.now()+(w.location.hash||''));}catch(err){write({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:'ERROR',error:String(err)})}return false}
  function patchDoc(d){try{let w=d.defaultView;if(w&&!w.__pmpLauncherReloadCurrentBridgeV1){let old=w.reloadApp;w.reloadApp=function(){return reloadCurrent(null,null)};w.__pmpLauncherReloadCurrentBridgeV1={version:V,oldReloadApp:old?true:false}}
    [...d.querySelectorAll('button,a,[role="button"]')].forEach(b=>{let label=txt(b).toLowerCase(),onclick=String(b.getAttribute('onclick')||'').toLowerCase();if(!(label==='reload'||label.includes('reload current')||onclick.includes('reloadapp')))return;if(b.__pmpReloadCurrentBridgePatched)return;b.__pmpReloadCurrentBridgePatched=true;b.addEventListener('click',e=>reloadCurrent(e,b),true);if(label==='reload')b.textContent='Reload Current';});
  }catch(e){}}
  function scan(){try{docs(T().document).forEach(patchDoc)}catch(e){}}
  T().PMPLauncherReloadCurrentBridgeV1={version:V,scan,key:KEY,reloadCurrent};
  addEventListener('load',()=>[120,500,1200,2500,5000,9000].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,1200);
  scan();
})();
