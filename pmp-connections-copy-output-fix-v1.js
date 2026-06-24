(()=>{
'use strict';
const V='1.0.0-request-packet-copy-target';
function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function cleanText(el){return (el&&el.textContent||'').replace(/\s+/g,' ').trim()}
async function copyWithFallback(w,d,value,msg){
  const text=String(value||'');
  let ok=false;
  try{const nav=(w&&w.navigator)||navigator;if(nav&&nav.clipboard&&nav.clipboard.writeText){await nav.clipboard.writeText(text);ok=true}}catch(e){}
  if(!ok){try{const ta=d.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.left='-9999px';ta.style.top='0';d.body.appendChild(ta);ta.focus();ta.select();ok=!!d.execCommand&&d.execCommand('copy');ta.remove()}catch(e){}}
  try{const out=d.getElementById('connOut');if(out)out.textContent=msg||(ok?'Output copied.':'Copy failed. Text is still visible above.')}catch(e){}
  return ok;
}
function copyRequestText(w,d,e){
  if(e){try{e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}catch(x){}}
  const box=d.getElementById('connBox');
  return copyWithFallback(w,d,box?box.value:'','Request packet copied.');
}
function patchWindow(w,d){
  if(!w||!d||!d.getElementById)return;
  const mode=d.getElementById('connMode'),box=d.getElementById('connBox'),out=d.getElementById('connOut');
  if(!mode||!box||!out)return;
  if(!w.__pmpConnectionsCopyOutputOriginalV1&&typeof w.copyConnOutput==='function')w.__pmpConnectionsCopyOutputOriginalV1=w.copyConnOutput;
  if(w.__pmpConnectionsCopyOutputFixV1!==V){
    w.__pmpConnectionsCopyOutputFixV1=V;
    w.copyConnOutput=function(e){
      const m=d.getElementById('connMode');
      const active=String(m&&m.value||'');
      if(active==='request')return copyRequestText(w,d,e);
      const original=w.__pmpConnectionsCopyOutputOriginalV1;
      if(typeof original==='function')return original.apply(w,arguments);
      const fallback=d.getElementById('connOut');
      return copyWithFallback(w,d,fallback?fallback.textContent:'','Output copied.');
    };
  }
  Array.from(d.querySelectorAll('button')).forEach(b=>{
    if(cleanText(b)==='Copy Output'&&b.dataset.pmpConnectionsCopyOutputFixV1!==V){
      b.dataset.pmpConnectionsCopyOutputFixV1=V;
      b.addEventListener('click',function(e){
        const m=d.getElementById('connMode');
        if(String(m&&m.value||'')==='request')return w.copyConnOutput(e);
      },true);
    }
  });
}
function scan(){docs(document).forEach(d=>{try{patchWindow(d.defaultView,d)}catch(e){}})}
window.PMPConnectionsCopyOutputFixV1={version:V,scan};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
window.addEventListener('load',()=>[50,150,400,900,1800].forEach(t=>setTimeout(scan,t)));
setInterval(scan,500);
})();
