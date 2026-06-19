(()=>{
  if(window.PMPAutomatedPlanStableGridV1)return;
  window.PMPAutomatedPlanStableGridV1=true;
  function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>7)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function inject(doc){
    try{
      if(!doc||!doc.head||doc.getElementById('pmpAutomatedPlanStableGridV1Style'))return;
      let st=doc.createElement('style');
      st.id='pmpAutomatedPlanStableGridV1Style';
      st.textContent='#pmpAutomatedPlanOverlayV1 .pmp-ap-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}#pmpAutomatedPlanOverlayV1 .pmp-ap-grid>.mini{width:100%!important;margin-top:0!important;min-width:0!important}@media(max-width:520px){#pmpAutomatedPlanOverlayV1 .pmp-ap-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}';
      doc.head.appendChild(st);
    }catch(e){}
  }
  function scan(){deepDocuments(document).forEach(inject)}
  window.addEventListener('load',()=>[50,150,300,700,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,700);
  scan();
})();
