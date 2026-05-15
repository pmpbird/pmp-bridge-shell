window.PMPLastKnownGoodV1=(function(){
const PATH='pmp-last-known-good-v1.json';
const RULE='advisory_only_no_auto_restore_no_auto_promote_no_delete_no_archive_no_app_state_write';
async function read(report,cert){
  const needed=!(cert&&cert.open_world_allowed===true);
  const base={type:'PMP_ROUTE_GUARDIAN_RECOVERY_PATH',version:'1.0.0',built_at:new Date().toISOString(),manifest_path:PATH,rule:RULE,needed:needed,included:false,available:false,current_route_passed:!needed};
  try{
    const r=await fetch(PATH+'?fresh='+Date.now(),{cache:'no-store'});
    const text=await r.text();
    let manifest=null;
    try{manifest=JSON.parse(text)}catch(e){return {...base,fetch_ok:r.ok,status:r.status,parse_ok:false,error:'manifest parse failed: '+String(e.message||e)}}
    const route=manifest.last_known_good_route||{};
    const clean=manifest.last_clean_pass_requirements||{};
    const summary={loader:route.loader||'missing',certifier:route.certifier||'missing',current_inner:route.current_inner||'missing',world_hash:route.world_hash||'#world',recorded_at:manifest.recorded_at||'unknown',route_confidence:clean.route_confidence||'unknown'};
    if(needed){
      return {...base,fetch_ok:r.ok,status:r.status,parse_ok:true,available:r.ok,included:true,recovery_summary:summary,last_known_good_route:route,last_clean_pass_requirements:clean,operator_message:manifest.operator_message||'Use last known good for diagnosis only. Do not auto-restore.'};
    }
    return {...base,fetch_ok:r.ok,status:r.status,parse_ok:true,available:r.ok,included:false,recovery_summary:summary,operator_message:'Current route passed. Last Known Good is available but not needed.'};
  }catch(e){return {...base,fetch_ok:false,status:0,parse_ok:false,error:String(e.message||e)}}
}
function explain(x){
  if(!x)return 'Last Known Good: unavailable';
  if(!x.needed)return 'Last Known Good: available but not needed because current route passed.';
  const s=x.recovery_summary||{};
  return ['LAST KNOWN GOOD / RECOVERY PATH','Rule: advisory only; no auto-restore, no auto-promote, no delete, no archive, no app-state write.','Loader: '+(s.loader||'missing'),'Certifier: '+(s.certifier||'missing'),'Current inner: '+(s.current_inner||'missing'),'World hash: '+(s.world_hash||'#world'),'Recorded: '+(s.recorded_at||'unknown')].join('\n');
}
return{read,explain};
})();