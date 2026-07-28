(()=>{
'use strict';
const V='2.0.0-read-only-symptom-analyzer';
function topWindow(){try{return window.top||window}catch(e){return window}}
function clean(value){return String(value||'').replace(/\s+/g,' ').trim()}
function documents(root,out,depth){
  out=out||[];depth=depth||0;
  if(!root||depth>8)return out;
  try{
    out.push(root);
    root.querySelectorAll('iframe,frame').forEach(frame=>{
      try{let doc=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(doc)documents(doc,out,depth+1)}catch(e){}
    });
  }catch(e){}
  return out;
}
function visible(element){
  try{
    const view=element.ownerDocument.defaultView;
    const style=view.getComputedStyle(element);
    const rect=element.getBoundingClientRect();
    return style.display!=='none'&&style.visibility!=='hidden'&&rect.width>0&&rect.height>0;
  }catch(e){return false}
}
function snapshot(){
  const findings=[];
  documents(topWindow().document).forEach((doc,frame)=>{
    try{
      const ids={};
      doc.querySelectorAll('[id]').forEach(node=>{ids[node.id]=(ids[node.id]||0)+1});
      Object.keys(ids).filter(id=>ids[id]>1).forEach(id=>findings.push({type:'duplicate_dom_id',frame,id,count:ids[id]}));
      const ownerClaims={};
      doc.querySelectorAll('[data-pmp-section-owner],[data-pmp-owner-lock]').forEach(node=>{
        const key=node.getAttribute('data-pmp-section-owner')||node.getAttribute('data-pmp-owner-lock')||'';
        if(key)ownerClaims[key]=(ownerClaims[key]||0)+1;
      });
      Object.keys(ownerClaims).filter(owner=>ownerClaims[owner]>1).forEach(owner=>findings.push({type:'duplicate_owner_claim',frame,owner,count:ownerClaims[owner]}));
      const bank=doc.getElementById('bank');
      if(bank){
        const continuous=bank.querySelectorAll('[data-bank-screen-owner-v1],[data-continuous-run-level-ui-scope-v1]').length;
        if(continuous>2)findings.push({type:'continuous_run_presentation_owner_collision',frame,count:continuous});
        const raw=bank.querySelector('[data-bank-helper]');
        const inspector=bank.querySelector('[data-helper-bank-live-inspector-v2]');
        if(raw&&inspector&&visible(raw)&&visible(inspector))findings.push({type:'helper_bank_dual_presentation',frame});
      }
    }catch(e){}
  });
  return{
    type:'PMP_HELPER_SYMPTOM_READ_ONLY_SNAPSHOT_V2',
    version:V,
    owner:'diagnostics_owner',
    at:new Date().toISOString(),
    read_only:true,
    findings,
    finding_count:findings.length
  };
}
window.PMPHelperProblemTypeSeedsV1={
  version:V,
  owner:'diagnostics_owner',
  role:'read_only_analyzer',
  snapshot,
  scan:snapshot,
  rule:'Returns evidence only. It never writes storage, removes DOM, binds controls, or schedules scans.'
};
window.PMPHelperSymptomWatcherV1=window.PMPHelperProblemTypeSeedsV1;
})();
