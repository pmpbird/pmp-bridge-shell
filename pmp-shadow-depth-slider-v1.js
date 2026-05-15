window.PMPShadowDepthSliderV1=(function(){
const KEY='pmp_shadow_depth_v1';
function clamp(n){return Math.max(0,Math.min(100,Number(n)||0))}
function readDepth(){try{let v=JSON.parse(localStorage.getItem(KEY)||'{}').value;return Number.isFinite(+v)?clamp(+v):75}catch(e){return 75}}
function writeDepth(v){localStorage.setItem(KEY,JSON.stringify({value:clamp(v),updated_at:new Date().toISOString()}));try{if(window.PMPNativeContrastBridgeV2)window.PMPNativeContrastBridgeV2.apply()}catch(e){}}
function label(v){v=clamp(v);if(v===0)return'flat';if(v<35)return'light';if(v<65)return'normal';if(v<85)return'strong clean';return'max clean'}
function injectDoc(doc){
  try{
    if(!doc||!doc.getElementById)return false;
    let body=doc.getElementById('colorBody')||doc.querySelector('[id*="colorBody"]')||doc.querySelector('#colorPanel .panel');
    if(!body||doc.getElementById('pmpShadowDepthControl'))return false;
    let wrap=doc.createElement('div');
    wrap.id='pmpShadowDepthControl';
    wrap.style.marginTop='12px';
    wrap.style.paddingTop='10px';
    wrap.style.borderTop='2px solid var(--line,#000)';
    wrap.innerHTML='<label style="display:grid;gap:6px;font-weight:950">Shadow Depth<input id="pmpShadowDepth" type="range" min="0" max="100" step="1"></label><div id="pmpShadowDepthReadout" style="font-weight:900;margin-top:6px">Shadow Depth</div><div style="font-size:12px;font-weight:800;margin-top:4px;opacity:.85">Shadow is separate from color and contrast. It controls visual lift only.</div>';
    body.appendChild(wrap);
    let input=doc.getElementById('pmpShadowDepth');
    let out=doc.getElementById('pmpShadowDepthReadout');
    function sync(){let v=readDepth();input.value=String(v);out.textContent='Shadow Depth: '+v+' — '+label(v)}
    input.addEventListener('input',function(){writeDepth(input.value);sync()});
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
function apply(){return{type:'PMP_SHADOW_DEPTH_SLIDER_REPORT',version:'1.0.0',built_at:new Date().toISOString(),injected_count:scan(document,0),shadow_depth:readDepth(),storage_key:KEY,rule:'Slider injection only. Does not change route, map, permissions, or app state beyond the shadow-depth visual setting.'}}
function start(){apply();[200,600,1200,2500,4500].forEach(t=>setTimeout(apply,t));setInterval(apply,1500)}
return{apply,start,readDepth,writeDepth};
})();try{window.PMPShadowDepthSliderV1.start()}catch(e){}