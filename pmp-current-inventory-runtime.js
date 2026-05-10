(() => {
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INV = 'pmp_app_lossless_inventory_latest_v1';
  const VISIBLE = 'pmp_lossless_visible_compact_latest_v1';
  const MANIFEST = 'pmp-inventory-eyes-manifest-v1.0.0.json';
  function now(){return new Date().toISOString()}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
  function read(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f||null))}catch(e){return f||null}}
  function deep(){try{let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);return{w,d}}catch(e){return{}}}
  function keys(){try{return Object.keys(localStorage).sort().map(k=>({key:k,value_captured:false}))}catch(e){return[]}}
  function buttons(d){try{return Array.from(d.querySelectorAll('button')).map((b,i)=>({index:i,text:(b.textContent||'').replace(/\s+/g,' ').trim().slice(0,160),visible:b.offsetParent!==null}))}catch(e){return[]}}
  async function getManifest(){try{let r=await fetch(MANIFEST+'?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error(String(r.status));return await r.json()}catch(e){return{type:'PMP_MANIFEST_FALLBACK',paths:['pmp-app-current.html','pmp-current-runtime.html','pmp-home-single-v6.html','bm.html'],classification_rules:{current_active:['pmp-app-current.html','pmp-current-runtime.html','pmp-home-single-v6.html']},error:String(e.message||e)}}}
  async function runInventory(trigger){
    const o=deep(), d=o.d;
    const m=await getManifest();
    const paths=Array.isArray(m.paths)?m.paths:[];
    const activeSet=new Set(((m.classification_rules||{}).current_active)||[]);
    const files=paths.map(p=>({path:p,status:activeSet.has(p)?'active_current':'known_or_support',active:activeSet.has(p)}));
    const s={type:'PMP_INVENTORY_EYES_APP_SCAN',version:'4.0.0-flattened-runtime',built_at:now(),trigger:trigger||'manual',scan_mode:'FULL_SAFE_APP_BASELINE_RUNTIME',privacy:'key names only; private values not captured; Apple Notes/private Bug Memory not scanned',manifest:{path:MANIFEST,type:m.type||null,version:m.version||null,path_count:paths.length},summary:{manifest_paths:paths.length,active_files:files.filter(x=>x.active).length,inactive_files:files.filter(x=>!x.active).length,local_storage_keys:keys().length,buttons:d?buttons(d).length:0},live_screen:{title:d&&d.title||'',buttons:d?buttons(d):[],visible_text_sample:d&&d.body?(d.body.innerText||'').replace(/\s+/g,' ').trim().slice(0,1200):''},storage_keys:keys(),file_inventory:files,active_files:files.filter(x=>x.active),inactive_files:files.filter(x=>!x.active)};
    write(EYES,s); write(INV,s);
    const receipt={type:'PMP_LOSSLESS_REPORT_RECEIPT',built_at:now(),full_report_saved:true,full_report_key:EYES,summary:s.summary,next:'Tap Copy Lossless Report.'};
    write(VISIBLE,receipt);
    const p=d&&d.getElementById('bridgePanel'); if(p){p.className='note';p.textContent=JSON.stringify(receipt,null,2)}
    const r=d&&d.getElementById('residentReply'); if(r)r.textContent='Lossless Quality complete. Full Inventory Eyes report saved locally.';
    return s;
  }
  function patch(){const o=deep(),d=o.d,w=o.w;if(!d||!w)return;w.improveLossless=function(){return runInventory('Improve Lossless Quality button')};for(const b of Array.from(d.querySelectorAll('button'))){const t=(b.textContent||'').replace(/\s+/g,' ').trim();if(t.includes('Improve Lossless Quality')&&!b.dataset.inventoryRuntime){b.dataset.inventoryRuntime='1';b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();runInventory('button_capture')},true)}}}
  setInterval(patch,700); setTimeout(patch,300);
  window.pmpRunInventoryRuntime=runInventory;
})();
