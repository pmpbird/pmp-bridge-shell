(()=>{
  if(window.PMPDashboardLabelV5)return;
  window.PMPDashboardLabelV5=true;
  function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function rename(d){try{let b=d.getElementById('pmpAutomatedPlanEntryV1');if(!b)return;let t=b.querySelector('.pmp-ap-entry-title');if(t)t.textContent='Continuous Run Dashboard'}catch(e){}}
  function load(d){try{if(d.getElementById('pmp-card-loader-r4'))return;let s=d.createElement('script');s.id='pmp-card-loader-r4';s.src='pmp-crd-card-v1.js?fresh=r4';(d.head||d.documentElement).appendChild(s)}catch(e){}}
  function scan(){docs(document).forEach(d=>{rename(d);load(d)})}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,900);
  scan();
})();
