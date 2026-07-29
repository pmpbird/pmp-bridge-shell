(()=>{
'use strict';
const VERSION='1.0.0-private-library-entry-20260729A';
const OWNER='library_section_owner';
const PRIVATE_LIBRARY_URL='https://phillips-macbook-air.tail64f36e.ts.net/library';
const RECEIPT_KEY='pmp_universal_discovery_library_v1_receipt';
const boundFrames=new WeakSet();
const observedDocuments=new WeakSet();
let lastReceipt=null;

function topWindow(){try{return window.top||window}catch(_error){return window}}
function documents(root,depth,seen,out){
  depth=depth||0;
  seen=seen||new Set();
  out=out||[];
  if(!root||depth>8||seen.has(root))return out;
  seen.add(root);
  out.push(root);
  try{
    Array.from(root.querySelectorAll('iframe,frame')).forEach(frame=>{
      try{
        const nested=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);
        if(nested)documents(nested,depth+1,seen,out);
      }catch(_error){}
    });
  }catch(_error){}
  return out;
}
function escapeText(value){
  return String(value==null?'':value).replace(/[&<>"]/g,character=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'
  }[character]));
}
function record(status,extra){
  const receipt=Object.assign({
    type:'PMP_UNIVERSAL_DISCOVERY_LIBRARY_ENTRY_V1_RECEIPT',
    version:VERSION,
    owner:OWNER,
    at:new Date().toISOString(),
    status,
    private_url:PRIVATE_LIBRARY_URL,
    public_credentials_stored:false,
    public_backend_used:false,
    arbitrary_terminal_access:false,
    private_transport:'TAILSCALE_SERVE_ONLY',
    model_api_exposed:false
  },extra||{});
  lastReceipt=receipt;
  try{topWindow().sessionStorage.setItem(RECEIPT_KEY,JSON.stringify(receipt,null,2))}catch(_error){}
  return receipt;
}
function openPrivateLibrary(event){
  if(event){event.preventDefault();event.stopPropagation()}
  const opened=window.open(PRIVATE_LIBRARY_URL,'_blank','noopener,noreferrer');
  record(opened?'PRIVATE_LIBRARY_OPEN_REQUESTED':'PRIVATE_LIBRARY_POPUP_BLOCKED',{
    next_action:opened
      ?'Continue through the Tailscale-private Mac surface.'
      :'Allow the new tab, then press Open Private Research Line again.'
  });
  return false;
}
function makeCard(documentValue){
  const library=documentValue.getElementById('library');
  if(!library||documentValue.getElementById('pmpUniversalDiscoveryLibraryV1'))return false;
  const host=library.querySelector('.card')||library;
  const card=documentValue.createElement('div');
  card.id='pmpUniversalDiscoveryLibraryV1';
  card.setAttribute('data-pmp-universal-discovery-library-v1','');
  card.setAttribute('data-owner',OWNER);
  card.innerHTML=
    "<hr style='border:0;border-top:2px solid var(--line,#fff);margin:18px 0'>"+
    "<h2>Universal Discovery Line</h2>"+
    "<p class='sub'>Private research controls on your Mac. The public PMP app stores no Mac credential and cannot send terminal commands.</p>"+
    "<button class='big' type='button' data-open-private-library>"+
      "<span class='icon'>⌁</span>"+
      "<span>Open Private Research Line<small>projects, harvester, campaigns, evidence, Gemma diagnostics, training and exports</small></span>"+
      "<span class='chev'>›</span>"+
    "</button>"+
    "<div class='note' data-private-library-status>"+
      "Private address: "+escapeText(PRIVATE_LIBRARY_URL)+"\n"+
      "Requires Tailscale on this device and the Mac control service to be running."+
    "</div>";
  host.appendChild(card);
  const button=card.querySelector('[data-open-private-library]');
  if(button)button.addEventListener('click',openPrivateLibrary);
  record('LIBRARY_ENTRY_INSTALLED',{document_title:String(documentValue.title||'')});
  return true;
}
function bindFrames(documentValue){
  try{
    Array.from(documentValue.querySelectorAll('iframe,frame')).forEach(frame=>{
      if(boundFrames.has(frame))return;
      boundFrames.add(frame);
      frame.addEventListener('load',()=>scan('nested_frame_load'));
    });
  }catch(_error){}
}
function observe(documentValue){
  if(observedDocuments.has(documentValue)||typeof MutationObserver!=='function')return;
  try{
    const observer=new MutationObserver(()=>scan('document_mutation'));
    observer.observe(documentValue.documentElement||documentValue,{childList:true,subtree:true});
    observedDocuments.add(documentValue);
  }catch(_error){}
}
function scan(reason){
  let installed=0;
  documents(document).forEach(documentValue=>{
    bindFrames(documentValue);
    observe(documentValue);
    if(makeCard(documentValue))installed++;
  });
  return record(
    installed?'LIBRARY_ENTRY_INSTALLED':'LIBRARY_ENTRY_WAITING',
    {reason:String(reason&&reason.type||reason||'manual'),installed_count:installed}
  );
}
window.PMPUniversalDiscoveryLibraryV1=Object.freeze({
  version:VERSION,
  owner:OWNER,
  privateLibraryUrl:PRIVATE_LIBRARY_URL,
  scan,
  lastReceipt:()=>lastReceipt,
  rule:'The public PMP Library only opens the Tailscale-private Mac surface. It stores no privileged credential, owns no execution authority, and never exposes the model API.'
});
window.addEventListener('load',scan,{once:true});
[0,100,300,900,2000,5000,10000].forEach(delay=>setTimeout(()=>scan('bounded_boot_retry_'+delay),delay));
scan('script_load');
})();
