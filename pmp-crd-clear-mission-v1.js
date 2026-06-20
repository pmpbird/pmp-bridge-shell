(()=>{
  if(window.PMPCRDClearMissionV1)return;
  window.PMPCRDClearMissionV1=true;
  function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>9)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function wire(d){
    try{
      const box=d.getElementById('pmpApCommandBox');
      if(!box||d.getElementById('pmpCrdClearMissionTextV1'))return;
      const btn=d.createElement('button');
      btn.id='pmpCrdClearMissionTextV1';
      btn.className='mini';
      btn.textContent='Clear Mission Text';
      btn.onclick=function(e){
        if(e)e.preventDefault();
        box.value='';
        box.focus();
        const out=d.getElementById('pmpApEngineOut');
        if(out){out.className='pass';out.textContent='Mission text cleared. Continuous run did not start.';}
        return false;
      };
      const grid=d.querySelector('[data-pmp-ap-compile]')&&d.querySelector('[data-pmp-ap-compile]').parentNode;
      if(grid)grid.insertBefore(btn,grid.firstChild);
      else box.insertAdjacentElement('afterend',btn);
    }catch(e){}
  }
  function scan(){docs(document).forEach(wire)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,400);
  scan();
})();
