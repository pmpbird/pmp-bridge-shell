(() => {
  const VERSION = '1.6.0-page-scope-real-app-gate';
  const BASE_STATE_KEY = 'pmp_continuous_guardian_state_v1';
  const BASE_LEDGER_KEY = 'pmp_continuous_guardian_event_ledger_v1';
  const BASE_HEARTBEAT_KEY = 'pmp_continuous_guardian_last_heartbeat_v1';
  const BASE_SETTINGS_KEY = 'pmp_continuous_guardian_settings_v1';
  const SAVE_KEY = 'pmp_last_save_to_github_vault_press_v1';
  const DIAG_KEY = 'pmp_copy_lossless_diagnostic_v1';
  const REAL_APP_ENABLED_KEY = 'pmp_continuous_guardian_real_app_enabled_v1';
  const REAL_APP_KILL_SWITCH_KEY = 'pmp_continuous_guardian_real_app_kill_switch_v1';
  const MAX_EVENTS = 50;
  const GITHUB_FILES = [
    'pmp-lossless-inventory-vault/latest/packet.json',
    'pmp-lossless-inventory-vault/latest/report.json',
    'pmp-lossless-inventory-vault/latest/metadata.json',
    'pmp-lossless-inventory-vault/latest/mirror-status.json'
  ];

  function now(){return new Date().toISOString()}
  function safeRead(k, fallback){try{const v=localStorage.getItem(k);return v?JSON.parse(v):fallback}catch(_){return fallback}}
  function read(k, fallback){return safeRead(k,fallback)}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}}
  function ms(t){const n=Date.parse(t||'');return Number.isFinite(n)?n:NaN}
  function safeMessage(x){return String(x||'').slice(0,180)}
  function pagePath(){try{return String(location.pathname||'')}catch(_){return''}}
  const PAGE_PATH = pagePath();
  const IS_MIRROR = PAGE_PATH.includes('pmp-continuous-guardian-mirror-v1.html');
  const IS_REAL_APP = PAGE_PATH.includes('pmp-app-current.html');
  const PAGE_SCOPE = IS_MIRROR ? 'mirror' : IS_REAL_APP ? 'real-app' : 'other';
  function scopedKey(base){return base+'__'+PAGE_SCOPE}
  const STATE_KEY = scopedKey(BASE_STATE_KEY);
  const LEDGER_KEY = scopedKey(BASE_LEDGER_KEY);
  const HEARTBEAT_KEY = scopedKey(BASE_HEARTBEAT_KEY);
  const SETTINGS_KEY = scopedKey(BASE_SETTINGS_KEY);
  function truthyFlag(v){
    if(v===true || v==='true' || v==='TRUE' || v==='ALLOW' || v==='ENABLED' || v==='KILL')return true;
    if(v && typeof v==='object' && (v.enabled===true || v.allow===true || v.kill===true))return true;
    return false;
  }
  function realAppExplicitlyEnabled(){return truthyFlag(read(REAL_APP_ENABLED_KEY,false))}
  function realAppKillSwitchActive(){return truthyFlag(read(REAL_APP_KILL_SWITCH_KEY,false))}
  function pageGate(){
    if(!IS_REAL_APP)return {ok:true,reason:'not real app'};
    if(realAppKillSwitchActive())return {ok:false,reason:'real app kill switch active'};
    if(!realAppExplicitlyEnabled())return {ok:false,reason:'real app guardian not explicitly enabled'};
    return {ok:true,reason:'real app explicitly enabled'};
  }
  function compactProof(p){
    const out={};
    if(!p||typeof p!=='object')return out;
    for(const k of ['save_pressed_at','expected_packet_time','latest_packet_time','latest_report_time','latest_metadata_time','route','diagnostic_version','page_scope','gate_reason']){
      if(p[k])out[k]=String(p[k]).slice(0,120);
    }
    return out;
  }
  const saved = safeRead(STATE_KEY, null);
  const state = {
    type: 'PMP_CONTINUOUS_GUARDIAN_STATE',
    version: VERSION,
    page_scope: PAGE_SCOPE,
    page_path: PAGE_PATH,
    status: 'STOPPED',
    started_at: null,
    updated_at: null,
    last_heartbeat_at: null,
    last_local_check_at: null,
    last_github_check_at: null,
    loop_count: 0,
    auto_paused_by_visibility: false,
    user_paused: false,
    local: { status: 'UNKNOWN', weak: [] },
    github: { status: 'UNKNOWN', weak: [] },
    real_app_gate: { enabled: realAppExplicitlyEnabled(), kill_switch: realAppKillSwitchActive(), can_start: pageGate().ok, reason: pageGate().reason },
    guards: {
      watch_only: true,
      zero_cost: true,
      app_safe: true,
      mirror_safe: true,
      page_scope_separated: true,
      real_app_explicit_enable_required: true,
      real_app_kill_switch: true,
      no_mutation: true,
      no_auto_save: true,
      no_shortcut_open: true,
      no_github_write: true,
      manual_control_required: true
    },
    keys: {
      state: STATE_KEY,
      ledger: LEDGER_KEY,
      heartbeat: HEARTBEAT_KEY,
      settings: SETTINGS_KEY,
      real_app_enabled: REAL_APP_ENABLED_KEY,
      real_app_kill_switch: REAL_APP_KILL_SWITCH_KEY
    },
    note: 'Watch-only observer. Page-scoped state separates mirror from real app. Real app cannot start unless explicitly enabled and not killed.'
  };
  if (saved && saved.type === 'PMP_CONTINUOUS_GUARDIAN_STATE' && saved.page_scope === PAGE_SCOPE) {
    state.started_at = saved.started_at || null;
    state.loop_count = Number(saved.loop_count || 0);
    state.local = saved.local || state.local;
    state.github = saved.github || state.github;
    state.status = saved.status === 'RUNNING' ? 'RUNNING' : 'STOPPED';
    state.user_paused = !!saved.user_paused;
    state.auto_paused_by_visibility = !!saved.auto_paused_by_visibility;
  }

  function refreshGate(){
    const gate=pageGate();
    state.real_app_gate={enabled:realAppExplicitlyEnabled(),kill_switch:realAppKillSwitchActive(),can_start:gate.ok,reason:gate.reason};
    return gate;
  }
  function ledger(){const a=read(LEDGER_KEY,[]);return Array.isArray(a)?a:[]}
  function nextMoveFor(result,message){
    if(result==='blocked')return 'Stop risky paths and inspect before continuing.';
    if(result==='watch')return 'Keep watching; do not mutate the real app.';
    if(/freshness/i.test(message||''))return 'Run lossless diagnostic or wait for GitHub proof.';
    return 'Continue watch-only monitoring.';
  }
  function event(type,result,message,proof){
    const list=ledger();
    const last=list[list.length-1];
    const item={
      id:'CGE-'+Date.now().toString(36),
      time:now(),
      engine_version:VERSION,
      page_scope:PAGE_SCOPE,
      state:state.status,
      event_type:type,
      result:result||'info',
      message:safeMessage(message),
      proof:compactProof(Object.assign({page_scope:PAGE_SCOPE}, proof||{})),
      next_move:nextMoveFor(result,message)
    };
    if(last&&last.event_type===item.event_type&&last.result===item.result&&last.message===item.message){
      last.count=(last.count||1)+1;
      last.last_seen=item.time;
      write(LEDGER_KEY,list.slice(-MAX_EVENTS));
      return last;
    }
    list.push(item);
    write(LEDGER_KEY,list.slice(-MAX_EVENTS));
    return item;
  }
  function persist(){state.updated_at=now();state.page_scope=PAGE_SCOPE;state.page_path=PAGE_PATH;refreshGate();write(STATE_KEY,state)}
  function blockIfGateClosed(type){
    const gate=refreshGate();
    if(gate.ok)return false;
    state.status='STOPPED';
    event(type||'REAL_APP_GATE_BLOCKED','watch',gate.reason,{route:routeProof(),gate_reason:gate.reason});
    persist();
    return true;
  }
  function setStatus(s,why,proof){
    if(state.status==='STOPPED'&&s!=='RUNNING')return;
    if(state.user_paused&&s==='RUNNING')return;
    const priority={BLOCKED:6,PAUSED:5,WAITING:4,WATCH:3,RUNNING:2,GOOD:1,STOPPED:0,UNKNOWN:0};
    const old=state.status;
    if(priority[s]>=priority[old]||old==='STOPPED'||s==='STOPPED')state.status=s;
    if(old!==state.status)event('STATE_'+state.status,'info',why||('State changed to '+state.status),proof);
    persist();
  }
  function deep(){
    try{
      let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);
      for(let i=0;i<10;i++){const n=d&&d.getElementById&&d.getElementById('app');if(!n)break;w=n.contentWindow;d=n.contentDocument||w.document}
      return{w,d};
    }catch(e){return{error:String(e.message||e)}}
  }
  function buttons(d){try{return Array.from(d.querySelectorAll('button')).map(b=>(b.textContent||'').replace(/\s+/g,' ').trim()).filter(Boolean)}catch(_){return[]}}
  function routeProof(){try{return location.pathname+(location.search||'')+(location.hash||'')}catch(_){return''}}
  function localCheck(){
    if(state.status==='STOPPED')return;
    if(blockIfGateClosed('LOCAL_CHECK_GATE_BLOCKED'))return;
    const o=deep(),d=o.d,w=o.w,b=d?buttons(d):[];
    const weak=[];
    if(!d)weak.push('App document not loaded');
    if(!b.find(x=>x.includes('Improve Lossless Quality')))weak.push('Improve Lossless Quality button missing');
    if(!b.find(x=>x.includes('Save to GitHub Vault')||x.includes('Copy Lossless Report')))weak.push('Save to GitHub Vault button missing');
    if(!(w&&typeof w.copyCurrent==='function'))weak.push('copyCurrent missing');
    if(!(w&&typeof w.copyLosslessReport==='function'))weak.push('copyLosslessReport missing');
    const diag=read(DIAG_KEY,null);
    if(!diag)weak.push('Lossless diagnostic not yet recorded');
    state.local={status:weak.length?'WATCH':'GOOD',weak,route:routeProof(),checked_at:now(),diagnostic_version:diag&&diag.version||null};
    state.last_local_check_at=state.local.checked_at;
    if(weak.length){event('LOCAL_CHECK','watch',weak[0],{route:state.local.route,diagnostic_version:state.local.diagnostic_version});setStatus('WATCH','Local check has weak spots',state.local)}
    else event('LOCAL_CHECK','good','Local app safety check passed',{route:state.local.route,diagnostic_version:state.local.diagnostic_version});
    persist();
  }
  async function fetchJson(path){try{const r=await fetch(path+'?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch(_){return null}}
  function stamp(path,j){if(!j)return null;if(path.includes('metadata'))return j.updated_at||j.packet_built_at||j.report_built_at||j.built_at||null;return j.built_at||j.updated_at||j.packet_built_at||j.report_built_at||null}
  function notOlder(fileTime, expectedTime){const f=ms(fileTime),e=ms(expectedTime);return Number.isFinite(f)&&Number.isFinite(e)&&f+5000>=e}
  async function githubCheck(){
    if(state.status==='STOPPED')return;
    if(blockIfGateClosed('GITHUB_CHECK_GATE_BLOCKED'))return;
    const save=read(SAVE_KEY,null);
    const expected=save&&(save.packet_built_at||save.pressed_at)||null;
    const results=[];const weak=[];
    for(const p of GITHUB_FILES){const j=await fetchJson(p);results.push({path:p,ok:!!j,time:stamp(p,j)});if(!j)weak.push(p+' not reachable')}
    const packet=results.find(x=>x.path.includes('packet.json'));
    const report=results.find(x=>x.path.includes('report.json'));
    const metadata=results.find(x=>x.path.includes('metadata.json'));
    if(expected){
      if(!notOlder(packet&&packet.time,expected))weak.push('latest packet older than save');
      if(!notOlder(report&&report.time,expected))weak.push('latest report older than save');
      if(!notOlder(metadata&&metadata.time,expected))weak.push('latest metadata older than save');
    }else weak.push('No Save press recorded; freshness not proven');
    state.github={status:weak.length?'WATCH':'GOOD',weak,checked_at:now(),expected_packet_time:expected,latest_packet_time:packet&&packet.time||null,latest_report_time:report&&report.time||null,latest_metadata_time:metadata&&metadata.time||null,files:results};
    state.last_github_check_at=state.github.checked_at;
    if(weak.length){event('GITHUB_CHECK','watch',weak[0],state.github);setStatus(expected?'WAITING':'WATCH','GitHub proof incomplete',state.github)}
    else {event('GITHUB_CHECK','good','GitHub freshness proof passed',state.github);if(state.local.status==='GOOD')setStatus('GOOD','All watch-only proofs are good',state.github)}
    persist();
  }
  function heartbeat(){
    if(state.status==='STOPPED')return;
    if(blockIfGateClosed('HEARTBEAT_GATE_BLOCKED'))return;
    state.loop_count++;
    state.last_heartbeat_at=now();
    write(HEARTBEAT_KEY,{time:state.last_heartbeat_at,version:VERSION,status:state.status,loop_count:state.loop_count,page_scope:PAGE_SCOPE});
    if(state.loop_count%30===0)event('HEARTBEAT_OK','good','Heartbeat alive',{route:routeProof()});
    persist();
  }
  function start(){
    if(blockIfGateClosed('ENGINE_START_GATE_BLOCKED'))return snapshot();
    state.user_paused=false;state.auto_paused_by_visibility=false;
    state.status='RUNNING';state.started_at=state.started_at||now();event('ENGINE_STARTED','good','Watch-only engine started',{route:routeProof()});persist();
    localCheck();
    return snapshot();
  }
  function pause(){state.user_paused=true;state.auto_paused_by_visibility=false;setStatus('PAUSED','User paused engine',{route:routeProof()});event('ENGINE_PAUSED','info','Engine paused by user',{});persist();return snapshot()}
  function resume(){if(state.status==='PAUSED'&&state.user_paused){if(blockIfGateClosed('ENGINE_RESUME_GATE_BLOCKED'))return snapshot();state.user_paused=false;state.status='RUNNING';event('ENGINE_RESUMED','info','Engine resumed by user',{});persist();localCheck()}return snapshot()}
  function stop(){state.status='STOPPED';state.user_paused=false;state.auto_paused_by_visibility=false;event('ENGINE_STOPPED','info','Engine stopped by user',{});persist();return snapshot()}
  function allowRealAppStart(){
    if(!IS_REAL_APP)return {ok:false,reason:'real app enable can only be set from the real app page',page_scope:PAGE_SCOPE};
    write(REAL_APP_ENABLED_KEY,{enabled:true,enabled_at:now(),version:VERSION});
    refreshGate();event('REAL_APP_EXPLICITLY_ENABLED','info','Real app guardian explicitly enabled',{route:routeProof(),gate_reason:state.real_app_gate.reason});persist();return snapshot();
  }
  function disableRealAppStart(){
    if(!IS_REAL_APP)return {ok:false,reason:'real app disable can only be set from the real app page',page_scope:PAGE_SCOPE};
    write(REAL_APP_ENABLED_KEY,{enabled:false,disabled_at:now(),version:VERSION});
    state.status='STOPPED';refreshGate();event('REAL_APP_EXPLICITLY_DISABLED','info','Real app guardian disabled and stopped',{route:routeProof(),gate_reason:state.real_app_gate.reason});persist();return snapshot();
  }
  function killRealAppGuardian(){
    if(!IS_REAL_APP)return {ok:false,reason:'real app kill switch can only be set from the real app page',page_scope:PAGE_SCOPE};
    write(REAL_APP_KILL_SWITCH_KEY,{enabled:true,killed_at:now(),version:VERSION});
    state.status='STOPPED';refreshGate();event('REAL_APP_KILL_SWITCH_ON','blocked','Real app kill switch set; engine stopped',{route:routeProof(),gate_reason:state.real_app_gate.reason});persist();return snapshot();
  }
  function clearRealAppKillSwitch(){
    if(!IS_REAL_APP)return {ok:false,reason:'real app kill switch can only be cleared from the real app page',page_scope:PAGE_SCOPE};
    write(REAL_APP_KILL_SWITCH_KEY,{enabled:false,cleared_at:now(),version:VERSION});
    refreshGate();event('REAL_APP_KILL_SWITCH_OFF','info','Real app kill switch cleared; explicit enable still required',{route:routeProof(),gate_reason:state.real_app_gate.reason});persist();return snapshot();
  }
  function snapshot(){return JSON.parse(JSON.stringify({state,ledger:ledger()}))}

  let localTimer=null, githubTimer=null, heartbeatTimer=null;
  function installTimers(){
    if(heartbeatTimer)return;
    heartbeatTimer=setInterval(heartbeat,1000);
    localTimer=setInterval(()=>{if(state.status!=='STOPPED'&&state.status!=='PAUSED')localCheck()},10000);
    githubTimer=setInterval(()=>{if(state.status!=='STOPPED'&&state.status!=='PAUSED')githubCheck()},60000);
    document.addEventListener('visibilitychange',()=>{
      if(state.status==='STOPPED')return;
      if(document.hidden){state.auto_paused_by_visibility=true;setStatus('PAUSED','App hidden or backgrounded',{route:routeProof()});return}
      if(state.auto_paused_by_visibility&&!state.user_paused){
        if(blockIfGateClosed('APP_RESUME_GATE_BLOCKED'))return;
        event('APP_RESUMED','watch','App resumed; running local recovery check',{route:routeProof()});state.auto_paused_by_visibility=false;state.status='RUNNING';persist();localCheck();githubCheck()
      }
    });
  }

  window.PMPContinuousGuardianEngineV1={version:VERSION,start,pause,resume,stop,localCheck,githubCheck,snapshot,guards:state.guards,allowRealAppStart,disableRealAppStart,killRealAppGuardian,clearRealAppKillSwitch};
  write(SETTINGS_KEY,{version:VERSION,max_events:MAX_EVENTS,watch_only:true,page_scope:PAGE_SCOPE,state_key:STATE_KEY,ledger_key:LEDGER_KEY,real_app_explicit_enable_required:true,real_app_kill_switch:true,created_at:now()});
  installTimers();
  if(state.status==='RUNNING')start(); else persist();
})();
