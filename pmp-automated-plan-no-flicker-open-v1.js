(()=>{
  if(window.PMPAutomatedPlanNoFlickerOpenV1)return;
  window.PMPAutomatedPlanNoFlickerOpenV1=true;
  function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function bind(doc){
    try{
      let b=doc.getElementById('pmpAutomatedPlanEntryV1');
      if(!b||b.dataset.pmpNoFlickerOpenV1)return false;
      b.dataset.pmpNoFlickerOpenV1='1';
      b.onclick=async function(e){
        if(e)e.preventDefault();
        try{
          if(window.PMPAutomatedPlanRoomV1&&typeof window.PMPAutomatedPlanRoomV1.refresh==='function')await window.PMPAutomatedPlanRoomV1.refresh();
          if(window.PMPAutomatedPlanRoomV1&&typeof window.PMPAutomatedPlanRoomV1.open==='function')return window.PMPAutomatedPlanRoomV1.open();
        }catch(x){
          if(window.PMPAutomatedPlanRoomV1&&typeof window.PMPAutomatedPlanRoomV1.open==='function')return window.PMPAutomatedPlanRoomV1.open();
        }
        return false;
      };
      return true;
    }catch(e){return false}
  }
  function scan(){deepDocuments(document).forEach(bind)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,700);
  scan();
})();
