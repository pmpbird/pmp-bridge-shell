(()=>{
  if(window.PMPContinuousRunEntryV1)return;
  window.PMPContinuousRunEntryV1=true;
  const LABEL='Continuous Run Dashboard';
  function docs(root,depth,out){
    out=out||[];depth=depth||0;
    if(!root||depth>8)return out;
    try{
      out.push(root);
      Array.from(root.querySelectorAll('iframe')).forEach(frame=>{
        try{
          let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);
          if(d)docs(d,depth+1,out);
        }catch(e){}
      });
    }catch(e){}
    return out;
  }
  function make(doc){
    try{
      let control=doc.getElementById('control');
      if(!control)return false;
      let button=doc.getElementById('pmpAutomatedPlanEntryV1');
      if(!button){
        button=doc.createElement('button');
        button.id='pmpAutomatedPlanEntryV1';
        button.className='big';
        button.innerHTML='<span class="icon">◆</span><span class="pmp-ap-entry-text"><span class="pmp-ap-entry-title"></span><span class="pmp-ap-entry-status"></span></span><span class="chev">›</span>';
        let card=control.querySelector('.card')||control;
        let colorPanel=doc.getElementById('colorPanel');
        if(colorPanel&&colorPanel.parentNode===card)card.insertBefore(button,colorPanel);else card.appendChild(button);
      }
      let title=button.querySelector('.pmp-ap-entry-title');
      let status=button.querySelector('.pmp-ap-entry-status');
      if(title)title.textContent=LABEL;
      if(status)status.textContent='Setup — execution is safely locked';
      button.onclick=function(e){if(e)e.preventDefault();return false};
      return true;
    }catch(e){return false}
  }
  function scan(){docs(document).forEach(make)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,900);
  scan();
})();
