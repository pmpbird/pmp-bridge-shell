(function(){
  'use strict';
  const OWNER='pmp-connection-bank-inventory-v1';
  const INVENTORY_KEY='pmp_connection_bank_inventory_v1';
  const REGISTRY_KEY='pmp_connection_protected_bank_registry_v1';
  const RECEIPT_KEY='pmp_connection_bank_inventory_receipt_v1';
  const PROTECTED=[
    {key:'pmp_code_safety_bank_v1',owner:'Code Safety',purpose:'code-safety memory and checks',policy:'DO NOT OVERWRITE'},
    {key:'pmp_safe_writer_last_good_v3',owner:'Safe Writer',purpose:'last-good safe writer pointer',policy:'DO NOT OVERWRITE'},
    {key:'pmp_clean_connection_packets_v5',owner:'Connections',purpose:'clean connection packet set',policy:'DO NOT OVERWRITE'},
    {key:'pmp_corpus_inbox_v1',owner:'PMP Corpus',purpose:'protected corpus inbox/source bank',policy:'DO NOT OVERWRITE'},
    {key:'pmp_private_bug_memory_existing_v1',owner:'Bug Memory',purpose:'existing private bug memory',policy:'DO NOT OVERWRITE'},
    {key:'pmp_backend_config_v1',owner:'Backend Config',purpose:'backend/tool configuration',policy:'DO NOT OVERWRITE'},
    {key:'bug_memory',owner:'Bug Memory',purpose:'bug memory family',policy:'DO NOT OVERWRITE'},
    {key:'safe_point_bank',owner:'Safe Point',purpose:'safe-point bank family',policy:'DO NOT OVERWRITE'},
    {key:'last_good_pointer',owner:'Route Guardian / Safe Writer',purpose:'last-good pointer family',policy:'DO NOT OVERWRITE'},
    {key:'emergency_pointer',owner:'Route Guardian',purpose:'emergency pointer family',policy:'DO NOT OVERWRITE'},
    {key:'proof_ledger',owner:'Proof Ledger',purpose:'proof ledger family',policy:'DO NOT OVERWRITE'},
    {key:'receipt_ledger',owner:'Receipt Ledger',purpose:'receipt ledger family',policy:'DO NOT OVERWRITE'},
    {key:'automation_runtime_checkpoint',owner:'Automation Runtime',purpose:'automation/runtime checkpoint family',policy:'DO NOT OVERWRITE'},
    {key:INVENTORY_KEY,owner:'Connections Bank Inventory',purpose:'bank inventory output',policy:'OWNED BY CONNECTION BANK INVENTORY'},
    {key:REGISTRY_KEY,owner:'Connections Bank Inventory',purpose:'protected bank registry output',policy:'OWNED BY CONNECTION BANK INVENTORY'},
    {key:RECEIPT_KEY,owner:'Connections Bank Inventory',purpose:'inventory receipt output',policy:'OWNED BY CONNECTION BANK INVENTORY'}
  ];
  function now(){return new Date().toISOString()}
  function text(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
  function jget(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
  function bytes(s){try{return new Blob([s||'']).size}catch(e){return String(s||'').length}}
  function hash(s){let h=2166136261; s=String(s||''); for(let i=0;i<s.length;i++){h^=s.charCodeAt(i); h=Math.imul(h,16777619)} return (h>>>0).toString(16).padStart(8,'0')}
  function classify(k){
    const x=String(k||'').toLowerCase();
    if(x.includes('corpus'))return 'PMP Corpus / protected source bank';
    if(x.includes('connection'))return 'Connection / bridge bank';
    if(x.includes('bug'))return 'Bug Memory';
    if(x.includes('safe')||x.includes('last_good'))return 'Safe Writer / last-good';
    if(x.includes('receipt'))return 'Receipt ledger';
    if(x.includes('proof'))return 'Proof ledger';
    if(x.includes('packet'))return 'Packet source or packet state';
    if(x.includes('queue')||x.includes('task'))return 'Task queue';
    if(x.includes('backend'))return 'Backend configuration';
    if(x.includes('vault')||x.includes('bank')||x.includes('store'))return 'Bank / store';
    return 'Other app storage';
  }
  function policyFor(k){
    const key=String(k||'').toLowerCase();
    for(const p of PROTECTED){
      const pkey=String(p.key||'').toLowerCase();
      if(key===pkey || key.includes(pkey) || pkey.includes(key))return p.policy;
    }
    if(/corpus|bug|safe|last_good|emergency|proof|receipt|backend|vault|bank/.test(key))return 'PROTECT UNTIL OWNER AUDIT';
    return 'READ ONLY UNTIL OWNER AUDIT';
  }
  function inventory(){
    const rows=[];
    try{
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i); const v=localStorage.getItem(k)||'';
        if(!/pmp|packet|corpus|connection|vault|bank|store|bug|safe|receipt|proof|ledger|queue|task|backend|last_good|emergency/i.test(k))continue;
        rows.push({key:k,family:classify(k),policy:policyFor(k),chars:v.length,bytes:bytes(v),hash:hash(v),has_value:!!v});
      }
    }catch(e){rows.push({key:'INVENTORY_SCAN_ERROR',family:'error',policy:'BLOCKED',error:String(e)})}
    rows.sort((a,b)=>String(a.family).localeCompare(String(b.family))||String(a.key).localeCompare(String(b.key)));
    return {type:'PMP_CONNECTION_BANK_INVENTORY_V1',owner:OWNER,created_at:now(),rule:'inventory only; no existing bank overwritten',protected_registry:PROTECTED,rows};
  }
  function saveInventory(){
    const inv=inventory();
    const receipt={type:'PMP_BANK_INVENTORY_RECEIPT_V1',owner:OWNER,at:now(),inventory_key:INVENTORY_KEY,registry_key:REGISTRY_KEY,receipt_key:RECEIPT_KEY,total_rows:inv.rows.length,protected_count:PROTECTED.length,write_policy:'writes only new connection inventory namespace; existing banks read only'};
    localStorage.setItem(INVENTORY_KEY,JSON.stringify(inv,null,2));
    localStorage.setItem(REGISTRY_KEY,JSON.stringify(PROTECTED,null,2));
    localStorage.setItem(RECEIPT_KEY,JSON.stringify(receipt,null,2));
    return {inv,receipt};
  }
  function deepest(win){
    win=win||window;
    try{const fs=win.document.querySelectorAll('iframe'); for(const f of fs){try{if(f.contentWindow&&f.contentWindow.document)return deepest(f.contentWindow)}catch(e){}}}catch(e){}
    return win;
  }
  function panelDoc(){try{return deepest(window).document}catch(e){return null}}
  function panelWin(){try{return deepest(window)}catch(e){return null}}
  function esc(s){return String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
  function renderPanel(d){
    d=d||panelDoc(); if(!d)return false;
    const p=d.getElementById('bridgePanel'); if(!p)return false;
    const saved=saveInventory(); const inv=saved.inv;
    p.className='note';
    p.innerHTML='<div style="display:grid;gap:10px"><h2 style="margin:0;color:#d8ffe2">Bank Inventory + Protected Registry</h2><div><b>Status:</b> inventory saved. Existing banks were read only.</div><div><b>Rows:</b> '+inv.rows.length+' &nbsp; <b>Protected:</b> '+PROTECTED.length+'</div><button class="mini" id="pmpCopyBankInventoryBtn">Copy Inventory JSON</button><button class="mini" id="pmpCopyProtectedRegistryBtn">Copy Protected Registry</button><div class="warn"><b>Do not overwrite:</b><br>'+PROTECTED.map(x=>esc(x.key)+' — '+esc(x.owner)).join('<br>')+'</div><pre style="white-space:pre-wrap;overflow:auto;max-height:360px;background:#0c141e;color:#d8ffe2;border:1px solid var(--line,#fff);border-radius:14px;padding:10px">'+esc(inv.rows.map(r=>r.policy+' | '+r.family+' | '+r.key+' | chars:'+r.chars+' | hash:'+r.hash).join('\n'))+'</pre></div>';
    const copy=(val)=>{try{navigator.clipboard.writeText(val)}catch(e){const ta=d.createElement('textarea');ta.value=val;d.body.appendChild(ta);ta.select();d.execCommand('copy');ta.remove()}};
    const a=d.getElementById('pmpCopyBankInventoryBtn'); if(a)a.onclick=function(e){if(e)e.preventDefault();copy(JSON.stringify(inv,null,2));return false};
    const b=d.getElementById('pmpCopyProtectedRegistryBtn'); if(b)b.onclick=function(e){if(e)e.preventDefault();copy(JSON.stringify(PROTECTED,null,2));return false};
    return false;
  }
  function addButton(d){
    d=d||panelDoc(); if(!d)return;
    const p=d.getElementById('bridgePanel'); if(!p)return;
    if(d.getElementById('pmpOpenBankInventoryBtn'))return;
    const btn=d.createElement('button');
    btn.id='pmpOpenBankInventoryBtn'; btn.className='mini'; btn.type='button';
    btn.textContent='Open Bank Inventory + Protected Registry';
    btn.style.marginTop='10px'; btn.style.width='100%';
    btn.onclick=function(e){if(e){e.preventDefault();e.stopPropagation()}return renderPanel(d)};
    p.appendChild(btn);
  }
  function patch(){
    const w=panelWin(), d=panelDoc(); if(!w||!d)return;
    if(!w.__pmpConnectionBankInventoryV1){
      w.__pmpConnectionBankInventoryV1=true;
      const old=w.openConnectionsPanel;
      if(typeof old==='function'){
        w.openConnectionsPanel=function(){const r=old.apply(this,arguments); setTimeout(()=>addButton(d),60); setTimeout(()=>addButton(d),220); return r};
      }
      w.openBankInventoryProtectedRegistry=function(){return renderPanel(d)};
    }
    const bridge=d.getElementById('bridge');
    if(bridge && !d.getElementById('pmpBridgeBankInventoryCardBtn')){
      const tool=bridge.querySelector('.toolstrip')||bridge.querySelector('.card')||bridge;
      const btn=d.createElement('button'); btn.id='pmpBridgeBankInventoryCardBtn'; btn.className='mini'; btn.type='button'; btn.textContent='Bank Inventory';
      btn.onclick=function(e){if(e){e.preventDefault();e.stopPropagation()} try{if(typeof w.go==='function')w.go('bridge')}catch(x){} const p=d.getElementById('bridgePanel'); if(p)p.className='note'; return renderPanel(d)};
      tool.appendChild(btn);
    }
    try{const bp=d.getElementById('bridgePanel'); if(bp && /Connections/i.test(text(bp)))addButton(d)}catch(e){}
  }
  window.PMPConnectionBankInventoryV1={patch,inventory,saveInventory,renderPanel,protectedRegistry:PROTECTED,keys:{INVENTORY_KEY,REGISTRY_KEY,RECEIPT_KEY}};
  [100,500,1200,2500].forEach(t=>setTimeout(patch,t));
  setInterval(patch,2500);
})();
