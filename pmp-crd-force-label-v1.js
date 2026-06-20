(()=>{
  if(window.PMPCRDStableHelperV2)return;
  window.PMPCRDStableHelperV2=true;
  const OLD=['Auto','mated',' Plan'].join('');
  const NEW=['Continuous',' Run',' Dashboard'].join('');
  function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
  function style(d){try{if(d.getElementById('pmp-crd-stable-space-v2'))return;let s=d.createElement('style');s.id='pmp-crd-stable-space-v2';s.textContent='#continuousRunDashboardV1{overflow-anchor:none}#continuousRunDashboardV1 #pmpApEngineOut{min-height:280px;max-height:280px;overflow:auto;overflow-anchor:none;white-space:pre-wrap}#continuousRunDashboardV1 #pmpApQueuePreview{min-height:170px;overflow-anchor:none}';d.head.appendChild(s)}catch(e){}}
  function label(d){try{Array.from(d.getElementsByTagName('button')).forEach(b=>{let text=String(b.textContent||'');if(text.indexOf(OLD)<0)return;Array.from(b.querySelectorAll('span')).forEach(s=>{if(String(s.textContent||'').trim()===OLD)s.textContent=NEW});});}catch(e){}}
  function scan(){docs(document).forEach(d=>{style(d);label(d)})}
  window.addEventListener('load',()=>[50,250,900,2500].forEach(t=>setTimeout(scan,t)));
  document.addEventListener('click',()=>setTimeout(scan,80),true);
  scan();
})();
