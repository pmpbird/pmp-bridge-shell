(()=>{
  if(window.PMPCRDPrestyleV1)return;
  window.PMPCRDPrestyleV1=true;
  const CSS='#continuousRunDashboardV1{overflow-anchor:none}#continuousRunDashboardV1 .card:has(#pmpApEngineOut){display:flex;flex-direction:column}#continuousRunDashboardV1 #pmpApCommandBox{order:1}#continuousRunDashboardV1 #pmpApEngineOut{order:2;min-height:280px;max-height:280px;overflow:auto;overflow-anchor:none;white-space:pre-wrap;margin:12px 0;background:#0f1724;color:#f8fbff;border:3px solid var(--line,#07101c);border-radius:26px;padding:20px;box-sizing:border-box;font-weight:800}#continuousRunDashboardV1 .card:has(#pmpApEngineOut)>.grid{order:3}#continuousRunDashboardV1 #pmpApQueuePreview{order:4;min-height:170px;overflow-anchor:none}';
  function inject(d){try{if(!d||d.getElementById('pmp-crd-stable-space-v4'))return;let s=d.createElement('style');s.id='pmp-crd-stable-space-v4';s.textContent=CSS;(d.head||d.documentElement).appendChild(s)}catch(e){}}
  function scan(root,depth){depth=depth||0;if(!root||depth>9)return;inject(root);try{Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)scan(d,depth+1);f.addEventListener('load',()=>{try{let nd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(nd)scan(nd,depth+1)}catch(e){}},{once:false})}catch(e){}})}catch(e){}}
  function run(){scan(document,0)}
  window.addEventListener('load',()=>[0,80,180,400,900,1800,3600,7000].forEach(t=>setTimeout(run,t)));
  [0,80,180,400,900,1800,3600,7000].forEach(t=>setTimeout(run,t));
})();
