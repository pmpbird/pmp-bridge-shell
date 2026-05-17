window.PMPShadowDepthSliderV1=(function(){
const KEY='pmp_shadow_depth_v1';
function clamp(n){return Math.max(0,Math.min(100,Number(n)||0))}
function readDepth(){try{let v=JSON.parse(localStorage.getItem(KEY)||'{}').value;return Number.isFinite(+v)?clamp(+v):75}catch(e){return 75}}
function bridgeApply(){try{if(window.PMPNativeContrastBridgeV2)window.PMPNativeContrastBridgeV2.apply()}catch(e){}}
function writeDepth(v){localStorage.setItem(KEY,JSON.stringify({value:clamp(v),updated_at:new Date().toISOString()}));bridgeApply()}
function label(v){v=clamp(v);if(v===0)return'flat';if(v<35)return'light';if(v<65)return'normal';if(v<85)return'strong clean';return'max clean'}
function relabelContrast(doc){
  try{
    let input=doc.getElementById('readability');
    if(input&&input.parentNode){
      Array.from(input.parentNode.childNodes).forEach(n=>{if(n.nodeType===3&&/Readability/i.test(n.nodeValue||''))n.nodeValue=(n.nodeValue||'').replace(/Readability Layer/i,'Contrast').replace(/Readability/i,'Contrast')});
    }
  }catch(e){}
}
function wakeExistingVisualControls(doc){
  try{
    ['readability','colorAccent','colorBg','colorCard','colorLine'].forEach(id=>{
      let el=doc.getElementById(id);if(!el||el.dataset.pmpVisualWake==='1')return;
      el.dataset.pmpVisualWake='1';
      ['input','change'].forEach(ev=>el.addEventListener(ev,()=>setTimeout(bridgeApply,0)));
    });
  }catch(e){}
}
function injectDoc(doc){
  try{
    if(!doc||!doc.getElementById)return false;
    relabelContrast(doc);
    wakeExistingVisualControls(doc);
    let body=doc.getElementById('colorBody')||doc.querySelector('[id*="colorBody"]')||doc.querySelector('#colorPanel .panel');
    if(!body)return false;
    let wrap=doc.getElementById('pmpShadowDepthControl');
    if(!wrap){
      wrap=doc.createElement('div');
      wrap.id='pmpShadowDepthControl';
      wrap.style.marginTop='10px';
      wrap.style.paddingTop='0';
      wrap.innerHTML='<label style="display:grid;gap:6px;font-weight:950">Shadow Depth<input id="pmpShadowDepth" type="range" min="0" max="100" step="1"></label><div id="pmpShadowDepthReadout" class="readout" style="font-weight:900;margin-top:6px">Shadow Depth</div>';
    }
    let rr=doc.getElementById('readabilityReadout');
    if(wrap.parentNode!==body)body.appendChild(wrap);
    if(rr&&rr.parentNode&&rr.nextSibling!==wrap)rr.parentNode.insertBefore(wrap,rr.nextSibling);
    let input=doc.getElementById('pmpShadowDepth');
    let out=doc.getElementById('pmpShadowDepthReadout');
    if(!input||!out)return false;
    function sync(){let v=readDepth();input.value=String(v);out.textContent='Shadow Depth: '+v+' — '+label(v)}
    if(input.dataset.pmpShadowBound!=='1'){
      input.dataset.pmpShadowBound='1';
      input.addEventListener('input',function(){writeDepth(input.value);sync()});
      input.addEventListener('change',function(){writeDepth(input.value);sync()});
    }
    sync();
    return true;
  }catch(e){return false}
}
function scan(doc,depth){
  let count=0;if(!doc||depth>6)return 0;
  if(injectDoc(doc))count++;
  try{Array.from(doc.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);count+=scan(d,depth+1)}catch(e){}})}catch(e){}
  return count;
}
function apply(){let injected=scan(document,0);bridgeApply();return{type:'PMP_SHADOW_DEPTH_SLIDER_REPORT',version:'1.2.0-no-explanation-box',built_at:new Date().toISOString(),injected_count:injected,shadow_depth:readDepth(),storage_key:KEY,placement:'after_contrast_readout_when_available',rule:'Slider injection only. Places Shadow Depth next to Contrast, wakes the visual bridge when any visual slider moves, and does not change route, map, permissions, or app state beyond the shadow-depth visual setting.'}}
function start(){apply();[200,600,1200,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,1500)}
return{apply,start,readDepth,writeDepth};
})();try{window.PMPShadowDepthSliderV1.start()}catch(e){}