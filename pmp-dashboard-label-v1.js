(()=>{
  if(window.PMPDashboardLabelV13)return;
  window.PMPDashboardLabelV13=true;
  function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function rename(d){try{let b=d.getElementById('pmpAutomatedPlanEntryV1');if(!b)return;let t=b.querySelector('.pmp-ap-entry-title');if(t)t.textContent='Continuous Run Dashboard'}catch(e){}}
  function load(d){try{if(d.getElementById('pmp-card-loader-r10'))return;let s=d.createElement('script');s.id='pmp-card-loader-r10';s.src='pmp-crd-card-v1.js?fresh=r10';(d.head||d.documentElement).appendChild(s)}catch(e){}}
  function setCycleOneText(x){let s=String(x.textContent||'');if(s.indexOf('Cycle ')!==0)return;let a=s.split(' ');if(a.length>1){a[1]='1';x.textContent=a.join(' ')}}
  function doReset(d,b){let e=d.getElementById('pmpApEngineOut'),old=Number(e&&e.dataset&&e.dataset.visibleCycle||1),base=Number(localStorage.getItem('pmp_visible_cycle_base_v1')||1);if(old>0)localStorage.setItem('pmp_visible_cycle_base_v1',String(base+old-1));if(e&&e.children&&e.children[0])setCycleOneText(e.children[0]);if(e&&e.children&&e.children[1]&&e.children[1].children&&e.children[1].children[1])setCycleOneText(e.children[1].children[1]);if(e&&e.dataset)e.dataset.visibleCycle='1';b.textContent='Cycles Reset';setTimeout(()=>{b.textContent='Reset Cycles'},900)}
  function addReset(d){try{let g=d.querySelector('#continuousRunDashboardV1 .grid');if(!g||d.getElementById('pmpResetCyclesBtn'))return;let b=d.createElement('button');b.type='button';b.id='pmpResetCyclesBtn';b.className='mini';b.textContent='Reset Cycles';b.addEventListener('click',e=>{e.preventDefault();doReset(d,b)},true);g.appendChild(b)}catch(e){}}
  function scan(){docs(document).forEach(d=>{rename(d);load(d);addReset(d)})}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,900);
  scan();
})();
