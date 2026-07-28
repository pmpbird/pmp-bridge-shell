(()=>{
  const V='1.0.0-current-page-only';
  const MAP_URL='pmp-route-code-map-v1.json';
  const OUT='pmp_current_page_code_scope_v1_receipt';
  const RELOAD='pmp_reload_current_v1_receipt';
  const SNAP='pmp_reload_current_live_snapshot_v12_last_kept';
  const TEST='pmp_current_screen_test_engine_v1_last_report';
  function T(){try{return top||window}catch(e){return window}}
  function read(k,z){try{return JSON.parse(T().localStorage.getItem(k)||'null')||z}catch(e){return z}}
  function write(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
  function clean(s){return String(s||'').trim()}
  function file(src){return clean(src).split('?')[0].split('#')[0].split('/').pop()}
  function uniq(a){let seen={};return (a||[]).map(file).filter(x=>{if(!x||seen[x])return false;seen[x]=1;return true})}
  function bankFromName(s){s=String(s||'').toLowerCase();let pairs=[['continuous_run','continuous run bank'],['connections','connections bank'],['protection','protection bank'],['migration','migration bank'],['ui_control_surface','ui / control surface bank'],['test_verification','test / verification bank'],['bug_memory','bug memory bank'],['world','world bank'],['library','library bank'],['workshop','workshop bank'],['helper','helper bank']];for(const p of pairs)if(s.includes(p[1]))return p[0];return''}
  function routeFromName(s){s=String(s||'').toLowerCase();if(s.includes('control'))return'#control';if(s.includes('bank'))return'#bank';if(s.includes('bridge')||s.includes('connections'))return'#bridge';if(s.includes('library'))return'#library';if(s.includes('workshop'))return'#workshop';if(s.includes('world'))return'#world';return''}
  function ctx(){let snap=read(SNAP,null),reload=read(RELOAD,null),test=read(TEST,null),page=clean((snap&&snap.page)||(reload&&reload.page)||''),bank=clean((snap&&snap.bank_detail)||(reload&&reload.bank_detail)||''),pageName=clean(test&&test.current_screen&&test.current_screen.page);if(!bank)bank=bankFromName(pageName);let route=page&&page.charAt(0)==='#'?page:routeFromName(pageName||page);if(!route&&bank)route='#bank';let scripts=uniq((((test||{}).code_inventory||{}).scripts||[]).map(x=>x&&x.src));return{page,bank_detail:bank,page_name:pageName,route,scripts,test_scope:test&&test.scope||'',code_scope:test&&test.code_inventory&&test.code_inventory.scope||''}}
  async function loadMap(){try{let r=await fetch(MAP_URL+'?fresh=current-page-code-scope-'+Date.now(),{cache:'no-store'});if(r&&r.ok)return await r.json()}catch(e){}return null}
  function mapped(map,c){if(!map)return{kind:'map_missing',key:'',source:'none',files:[]};if(c.bank_detail&&map.bank_detail_files&&map.bank_detail_files[c.bank_detail])return{kind:'bank_detail',key:c.bank_detail,source:'bank_detail_files.'+c.bank_detail,files:uniq(map.bank_detail_files[c.bank_detail])};if(c.route&&map.route_files&&map.route_files[c.route])return{kind:'route',key:c.route,source:'route_files.'+c.route,files:uniq(map.route_files[c.route])};return{kind:'unmapped_current_page',key:c.bank_detail||c.route||c.page_name||c.page||'unknown',source:'none',files:[]}}
  function compare(mappedFiles,liveFiles){let m=uniq(mappedFiles),l=uniq(liveFiles),ms={},ls={};m.forEach(x=>ms[x]=1);l.forEach(x=>ls[x]=1);let matched=l.filter(x=>ms[x]),liveExtra=l.filter(x=>!ms[x]),mappedMissing=m.filter(x=>!ls[x]),flags=[];if(!m.length)flags.push('no_map_entry_for_current_page');if(liveExtra.length)flags.push('current_page_live_files_not_in_map');if(mappedMissing.length)flags.push('mapped_current_page_files_not_live');return{scope:'current_page_only',pass:!flags.length,status:flags.length?'CURRENT_PAGE_SCOPE_NEEDS_ATTENTION':'CURRENT_PAGE_SCOPE_PASS',flags,mapped_count:m.length,live_count:l.length,matched_count:matched.length,live_unmapped_count:liveExtra.length,mapped_missing_count:mappedMissing.length,matched,live_unmapped:liveExtra,mapped_missing:mappedMissing}}
  async function scan(){let c=ctx(),map=await loadMap(),m=mapped(map,c),cmp=compare(m.files,c.scripts),out={type:'PMP_CURRENT_PAGE_CODE_SCOPE_V1_RECEIPT',version:V,at:new Date().toISOString(),mode:'quiet_current_page_only',scope:'current_page_only_not_whole_app',context:c,map_loaded:!!map,map_version:map&&map.version||'',matched_map_source:m.source,scope_kind:m.kind,scope_key:m.key,repo_files:m.files,repo_files_count:m.files.length,live_files:c.scripts,live_files_count:c.scripts.length,comparison:cmp,pass:cmp.pass,status:cmp.status,flags:cmp.flags,canonical_reload_receipt_read_only:!!read(RELOAD,null),note:'Only the current page is checked. This diagnostic writes only its own receipt and never extends or rewrites the canonical Reload Current receipt.'};write(OUT,out);return out}
  T().PMPCurrentPageCodeScopeV1={version:V,scan,key:OUT};
  addEventListener('load',()=>[500,1300,2600,5200,8500].forEach(t=>setTimeout(scan,t)));
  setInterval(()=>scan(),2400);
  scan();
})();
