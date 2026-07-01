(function(){
'use strict';
const VERSION='1.1.0-copy-smoke-test-proof';
const OWNER='pmp-control-room-cleanup-v1';
function textOf(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim();}
function now(){return new Date().toISOString();}
function safeJson(k,f){try{let v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function sameOriginWin(w){try{return !!(w&&w.document&&w.location)}catch(e){return false}}
function windowsFrom(w,a,seen,depth){
  a=a||[];seen=seen||[];depth=depth||0;
  if(!sameOriginWin(w)||depth>8||seen.indexOf(w)!==-1)return a;
  seen.push(w);a.push(w);
  try{if(w.parent&&w.parent!==w)windowsFrom(w.parent,a,seen,depth+1)}catch(e){}
  try{if(w.top&&w.top!==w)windowsFrom(w.top,a,seen,depth+1)}catch(e){}
  try{Array.from(w.document.querySelectorAll('iframe,frame')).forEach(function(f){try{windowsFrom(f.contentWindow,a,seen,depth+1)}catch(e){}})}catch(e){}
  return a;
}
function allDocuments(){
  const out=[];
  windowsFrom(window).forEach(function(w){
    try{out.push({w:w,d:w.document,url:String(w.location&&w.location.href||''),title:w.document.title||''})}catch(e){}
  });
  return out;
}
function findObject(name){
  const wins=windowsFrom(window);
  for(let i=0;i<wins.length;i++){try{if(wins[i][name])return wins[i][name]}catch(e){}}
  return null;
}
function count(sel){
  let total=0,visible=0,first='';
  allDocuments().forEach(function(x){
    try{
      Array.from(x.d.querySelectorAll(sel)).forEach(function(el){
        total++;
        if(!first)first=textOf(el).slice(0,120);
        try{
          let cs=x.w.getComputedStyle(el),r=el.getBoundingClientRect();
          if(cs.display!=='none'&&cs.visibility!=='hidden'&&cs.opacity!=='0'&&r.width>0&&r.height>0&&!el.hidden)visible++;
        }catch(e){}
      });
    }catch(e){}
  });
  return {selector:sel,total:total,visible:visible,first_text:first};
}
function registryState(){
  const regObj=findObject('PMPMountRegistryV1');
  const orch=findObject('PMPAppOrchestratorV1');
  const reg=safeJson('pmp_mount_registry_v1',null);
  const snap=safeJson('pmp_mount_registry_live_snapshot_v1',null);
  const missing=safeJson('pmp_mount_registry_missing_expected_v1',[]);
  const receipt=safeJson('pmp_mount_registry_v1_receipt',null);
  return {regObj:regObj,orch:orch,reg:reg,snap:snap,missing:Array.isArray(missing)?missing:[],receipt:receipt};
}
function smokeProof(){
  const st=registryState();
  const docs=allDocuments().map(function(x){return {url:x.url,title:x.title}});
  const checks={
    mount_registry_loaded:!!st.regObj,
    mount_registry_version:st.regObj&&st.regObj.version||st.reg&&st.reg.version||null,
    app_orchestrator_loaded:!!st.orch,
    app_orchestrator_version:st.orch&&st.orch.version||null,
    registry_storage_present:!!st.reg,
    registry_snapshot_present:!!st.snap,
    bank_tab:count('[data-tab="bank"], #bank'),
    continuous_run_opener:count('[data-open-bank="continuous_run"]'),
    continuous_run_detail:count('[data-run-bank-tools], [data-run-bank-detail], [data-bso-run-state], [data-cr-run-state-summary]'),
    control_room:count('#control, [data-screen="control"], [data-tab="control"]'),
    blank_screen_warning:docs.length<2?'possible_low_document_count':'none_obvious'
  };
  return {
    type:'PMP_COPY_SMOKE_TEST_PROOF_V1',
    version:VERSION,
    owner:OWNER,
    built_at:now(),
    mode:'passive_copy_only',
    rule:'Copies proof only. No fixing, moving, deleting, Bank rebuild, route change, storage overwrite, or IndexedDB write.',
    current_href:String(location.href||''),
    documents:docs,
    checks:checks,
    registry_summary:{
      slot_count:st.reg&&Array.isArray(st.reg.slots)?st.reg.slots.length:null,
      atlas_bucket_count:st.reg&&Array.isArray(st.reg.atlas_buckets)?st.reg.atlas_buckets.length:null,
      storage_owner_count:st.reg&&Array.isArray(st.reg.storage_owners)?st.reg.storage_owners.length:null,
      indexeddb_owner_count:st.reg&&Array.isArray(st.reg.indexeddb_owners)?st.reg.indexeddb_owners.length:null,
      missing_expected_count:st.missing.length,
      receipt_version:st.receipt&&st.receipt.version||null,
      receipt_mode:st.receipt&&st.receipt.mode||null
    },
    missing_expected:st.missing,
    visual_user_check_required:'User still confirms whether the screen looked normal.'
  };
}
async function copyProof(doc,out){
  const proof=smokeProof();
  const text=JSON.stringify(proof,null,2);
  let copied=false;
  try{await navigator.clipboard.writeText(text);copied=true}catch(e){
    try{const ta=doc.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';doc.body.appendChild(ta);ta.focus();ta.select();copied=doc.execCommand('copy');ta.remove()}catch(x){}
  }
  if(out){
    out.textContent=copied?'Smoke Test Proof copied. Paste it into ChatGPT.':text;
    out.className=copied?'note':'warn';
  }
  return proof;
}
function controlHost(doc){
  if(!doc)return null;
  return doc.getElementById('control')||
    doc.querySelector('[data-screen="control"],[data-tab-panel="control"],section.control,.control-room')||
    Array.from(doc.querySelectorAll('section,main,div')).find(function(x){return /^Control( Room)?$/i.test(textOf(x.querySelector('h1,h2')||''))});
}
function installCopySmokeProof(doc){
  const host=controlHost(doc);
  if(!host||doc.getElementById('pmpCopySmokeTestProofControlV1'))return;
  const card=doc.createElement('div');
  card.id='pmpCopySmokeTestProofControlV1';
  card.setAttribute('data-pmp-copy-smoke-test-proof-v1','control-room');
  card.style.cssText='border:2px solid var(--line,#07101c);border-radius:22px;padding:12px;margin:12px 0;background:var(--card,#fff);color:var(--text,#07101c)';
  card.innerHTML='<button id="pmpCopySmokeTestProofButtonV1" class="big" type="button"><span class="icon">✓</span><span>Copy Smoke Test Proof<small>passive proof packet for ChatGPT</small></span><span class="chev">›</span></button><div id="pmpCopySmokeTestProofOutV1" class="note" style="margin-top:8px">Copies proof only. No fixing or moving.</div>';
  const first=host.firstElementChild;
  if(first)host.insertBefore(card,first.nextSibling||first);else host.appendChild(card);
  const btn=doc.getElementById('pmpCopySmokeTestProofButtonV1');
  const out=doc.getElementById('pmpCopySmokeTestProofOutV1');
  if(btn)btn.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}copyProof(doc,out);return false};
}
function applyCleanup(doc){
  if(!doc)return;
  Array.from(doc.querySelectorAll('button')).forEach(function(button){
    var text=textOf(button);
    if(text.indexOf('Automatic App Update')!==-1 || text.indexOf('Open Code Safety')!==-1){
      button.dataset.pmpControlRoomCleanup='route-guardian-owned';
      button.style.display='none';
    }
  });
  installCopySmokeProof(doc);
}
window.PMPControlRoomCleanupV1={version:VERSION,owner:OWNER,apply:applyCleanup,smokeProof:smokeProof,copyProof:function(){return copyProof(document,null)}};
})();
