(function(){
  function loadNativeContrastBridge(){
    try{
      if(window.PMPNativeContrastBridgeV1&&typeof window.PMPNativeContrastBridgeV1.start==='function'){
        window.PMPNativeContrastBridgeV1.start();
        return;
      }
      if(document.getElementById('pmp-native-contrast-bridge-v1-script'))return;
      const s=document.createElement('script');
      s.id='pmp-native-contrast-bridge-v1-script';
      s.src='pmp-native-contrast-bridge-v1.js?fresh=bug-catalog-engine-contrast-v1';
      s.async=false;
      document.head.appendChild(s);
    }catch(e){}
  }
  loadNativeContrastBridge();
  const CARDS_KEY='pmp_bug_cards_loaded_v1';
  const CATALOG_KEY='pmp_bug_catalog_live_v1';
  const META_KEY='pmp_bug_catalog_meta_v1';
  function now(){return new Date().toISOString()}
  function ymd(){return now().slice(0,10).replaceAll('-','')}
  function safeJson(s){try{return JSON.parse(s)}catch(e){return null}}
  function textBetweenAll(text,start,end){
    const out=[]; let i=0;
    while(true){const a=text.indexOf(start,i); if(a<0)break; const b=text.indexOf(end,a+start.length); if(b<0)break; out.push(text.slice(a+start.length,b).trim()); i=b+end.length}
    return out;
  }
  function extractJsonBlocks(text){
    const out=[]; const fences=[...text.matchAll(/```(?:json)?\s*([\s\S]*?)```/gi)];
    for(const f of fences){const o=safeJson(f[1].trim()); if(o)out.push(o)}
    const direct=safeJson(text.trim()); if(direct)out.push(direct);
    return out;
  }
  function extractRawJsonFromCardBlock(block){
    const idx=block.indexOf('Raw JSON:'); if(idx<0)return null;
    const raw=block.slice(idx+'Raw JSON:'.length).trim();
    const end=raw.indexOf('END PMP BUG CARD');
    const json=(end>=0?raw.slice(0,end):raw).trim();
    return safeJson(json);
  }
  function extractBugs(obj){
    if(!obj)return[];
    if(Array.isArray(obj))return obj;
    if(Array.isArray(obj.bugs))return obj.bugs;
    if(Array.isArray(obj.ranked_bugs))return obj.ranked_bugs.map(x=>x&&x.source?x.source:x);
    if(obj.report&&Array.isArray(obj.report.bugs))return obj.report.bugs;
    if(obj.body&&Array.isArray(obj.body.bugs))return obj.body.bugs;
    if(obj.type&&/BUG|PMP_.*BUG/i.test(String(obj.type)))return[obj];
    if(obj.id||obj.name||obj.symptom||obj.observed_behavior||obj.plain_summary)return[obj];
    return[];
  }
  function parseCards(input){
    const text=String(input||'').trim(); if(!text)return[];
    let cards=[];
    for(const obj of extractJsonBlocks(text))cards=cards.concat(extractBugs(obj));
    for(const block of textBetweenAll(text,'PMP BUG CARD','END PMP BUG CARD')){
      const obj=extractRawJsonFromCardBlock(block);
      if(obj)cards.push(obj);
    }
    const seen=new Set();
    return cards.map(normalizeBugCard).filter(c=>{const k=c.id+'|'+c.name+'|'+c.plain_summary;if(seen.has(k))return false;seen.add(k);return true});
  }
  function normalizeBugCard(bug,i){
    i=i||0; const id=bug.id||('BUG-'+ymd()+'-'+String(i+1).padStart(3,'0'));
    return {type:bug.type||'PMP_BUG_CARD',version:bug.version||'1.0',id,
      name:bug.name||bug.easy_name||'Untitled bug',
      plain_summary:bug.plain_summary||bug.summary||bug.symptom||bug.observed_behavior||'No plain summary yet.',
      where_seen:bug.where_seen||{room:bug.room||'',page_or_file:bug.page_or_file||bug.file||'',button_or_path:bug.button_or_path||'',device_context:bug.device_context||''},
      observed_behavior:bug.observed_behavior||bug.observed||bug.symptom||'',
      expected_behavior:bug.expected_behavior||bug.expected||'',
      repeat_steps:Array.isArray(bug.repeat_steps)?bug.repeat_steps:(Array.isArray(bug.steps)?bug.steps:[]),
      evidence:Array.isArray(bug.evidence)?bug.evidence:[],
      suspected_cause:bug.suspected_cause||bug.cause||'unknown',
      impact:bug.impact||{severity:bug.severity||'medium',blocks_work:!!bug.blocks_work,privacy_sensitive:!!bug.privacy_sensitive,can_corrupt_memory:!!bug.can_corrupt_memory,can_confuse_resident:!!bug.can_confuse_resident},
      resident_instruction:bug.resident_instruction||'Resident should remember this bug and check for it before changing related files.',
      status:bug.status||'new',created_at:bug.created_at||now(),source:bug};
  }
  function kind(card){const t=JSON.stringify(card).toLowerCase();
    if(/home screen|cache|stale|old stack|automatic app update|version|route/.test(t))return'route_version_cache';
    if(/theme|color|contrast|grey|gray|card|panel|readability/.test(t))return'theme_contrast';
    if(/notes|shortcut|save private memory|clipboard/.test(t))return'notes_shortcut';
    if(/resident|launcher|drawer|tool/.test(t))return'resident_launcher_tools';
    if(/catalog|index|bug card|bug batch|load memory|mixer/.test(t))return'bug_memory_catalog';
    if(/privacy|private|secret/.test(t))return'privacy_boundary';
    return'general_app';}
  function severity(card){const s=String((card.impact&&card.impact.severity)||card.severity||'medium').toLowerCase();return {critical:100,high:75,medium:50,low:25}[s]||50}
  function score(card){let n=severity(card); const k=kind(card); if(k==='route_version_cache')n+=25; if(k==='privacy_boundary')n+=20; if(k==='bug_memory_catalog')n+=15; if(card.impact&&card.impact.blocks_work)n+=10; if(card.impact&&card.impact.can_corrupt_memory)n+=20; if(card.impact&&card.impact.can_confuse_resident)n+=8; return Math.min(150,n)}
  function buildCatalog(cards){
    const normalized=cards.map(normalizeBugCard);
    const ranked=normalized.map(c=>({...c,bug_kind:kind(c),fundamental_score:score(c)})).sort((a,b)=>b.fundamental_score-a.fundamental_score||String(a.id).localeCompare(String(b.id)));
    const by_kind={}; for(const c of ranked){(by_kind[c.bug_kind]||(by_kind[c.bug_kind]=[])).push(c)}
    return {type:'PMP_LIVE_BUG_CATALOG',version:'1.0',built_at:now(),source:'raw Bug Cards loaded from Notes into app session',card_count:ranked.length,ranked_bugs:ranked,by_kind,summary:ranked.map((c,i)=>({rank:i+1,id:c.id,name:c.name,kind:c.bug_kind,score:c.fundamental_score,status:c.status}))};
  }
  function saveCatalogFromText(text){const cards=parseCards(text); const catalog=buildCatalog(cards); localStorage.setItem(CARDS_KEY,JSON.stringify(cards)); localStorage.setItem(CATALOG_KEY,JSON.stringify(catalog)); localStorage.setItem(META_KEY,JSON.stringify({type:'PMP_BUG_CATALOG_LOAD_META',loaded_at:now(),card_count:cards.length,catalog_key:CATALOG_KEY,cards_key:CARDS_KEY})); return {cards,catalog};}
  function loadCatalog(){return safeJson(localStorage.getItem(CATALOG_KEY)||'')||buildCatalog([])}
  function clearCatalog(){localStorage.removeItem(CARDS_KEY); localStorage.removeItem(CATALOG_KEY); localStorage.removeItem(META_KEY)}
  window.PMPBugCatalogEngine={CARDS_KEY,CATALOG_KEY,META_KEY,parseCards,normalizeBugCard,buildCatalog,saveCatalogFromText,loadCatalog,clearCatalog,kind,score,loadNativeContrastBridge};
})();
