(()=>{
  if(window.PMPCRDStableHelperV3)return;
  window.PMPCRDStableHelperV3=true;
  const OLD=['Auto','mated',' Plan'].join('');
  const NEW=['Continuous',' Run',' Dashboard'].join('');
  function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
  function style(d){try{if(d.getElementById('pmp-crd-stable-space-v3'))return;let s=d.createElement('style');s.id='pmp-crd-stable-space-v3';s.textContent='#continuousRunDashboardV1{overflow-anchor:none}#continuousRunDashboardV1 .card:has(#pmpApEngineOut){display:flex;flex-direction:column}#continuousRunDashboardV1 #pmpApCommandBox{order:1}#continuousRunDashboardV1 #pmpApEngineOut{order:2;min-height:280px;max-height:280px;overflow:auto;overflow-anchor:none;white-space:pre-wrap;margin-top:12px}#continuousRunDashboardV1 .card:has(#pmpApEngineOut)>.grid{order:3}#continuousRunDashboardV1 #pmpApQueuePreview{order:4;min-height:170px;overflow-anchor:none}';d.head.appendChild(s)}catch(e){}}
  function label(d){try{Array.from(d.getElementsByTagName('button')).forEach(b=>{let text=String(b.textContent||'');if(text.indexOf(OLD)<0)return;Array.from(b.querySelectorAll('span')).forEach(s=>{if(String(s.textContent||'').trim()===OLD)s.textContent=NEW});});}catch(e){}}
  function scan(){docs(document).forEach(d=>{style(d);label(d)})}
  window.addEventListener('load',()=>[50,250,900,2500].forEach(t=>setTimeout(scan,t)));
  document.addEventListener('click',()=>setTimeout(scan,80),true);
  scan();
})();
