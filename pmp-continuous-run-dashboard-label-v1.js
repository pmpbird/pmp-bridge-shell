(()=>{
  if(window.PMPContinuousRunDashboardLabelV1)return;
  window.PMPContinuousRunDashboardLabelV1=true;
  function deepDocuments(root,depth,out){
    out=out||[];depth=depth||0;
    if(!root||depth>7)return out;
    try{
      out.push(root);
      Array.from(root.querySelectorAll('iframe')).forEach(frame=>{
        try{
          let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);
          if(d)deepDocuments(d,depth+1,out);
        }catch(e){}
      });
    }catch(e){}
    return out;
  }
  function rename(doc){
    try{
      let b=doc.getElementById('pmpAutomatedPlanEntryV1');
      if(!b)return false;
      let title=b.querySelector('.pmp-ap-entry-title');
      if(title)title.textContent='Continuous Run Dashboard';
      return true;
    }catch(e){return false}
  }
  function scan(){deepDocuments(document).forEach(rename)}
  window.addEventListener('load',()=>[80,250,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,900);
  scan();
})();
