(() => {
  const VERSION = '1.5.0-watch-only-safe-layer';
  const STATE_KEY = 'pmp_continuous_guardian_state_v1';
  const LEDGER_KEY = 'pmp_continuous_guardian_event_ledger_v1';
  const HEARTBEAT_KEY = 'pmp_continuous_guardian_last_heartbeat_v1';
  const SETTINGS_KEY = 'pmp_continuous_guardian_settings_v1';
  const SAVE_KEY = 'pmp_last_save_to_github_vault_press_v1';
  const DIAG_KEY = 'pmp_copy_lossless_diagnostic_v1';
  const MAX_EVENTS = 50;
  const GITHUB_FILES = [
    'pmp-lossless-inventory-vault/latest/packet.json',
    'pmp-lossless-inventory-vault/latest/report.json',
    'pmp-lossless-inventory-vault/latest/metadata.json',
    'pmp-lossless-inventory-vault/latest/mirror-status.json'
  ];

  const state = {
    type: 'PMP_CONTINUOUS_GUARDIAN_STATE',
    version: VERSION,
    status: 'STOPPED',
    started_at: null,
    updated_at: null,
    last_heartbeat_at: null,
    last_local_check_at: null,
    last_github_check_at: null,
    loop_count: 0,
    local: { status: 'UNKNOWN', weak: [] },
    github: { status: 'UNKNOWN', weak: [] },
    guards: {
      watch_only: true,
      zero_cost: true,
      app_safe: true,
      mirror_safe: true,
      no_mutation: true,
      no_auto_save: true,
      no_shortcut_open: true,
      no_github_write: true
    },
    note: 'Watch-only observer. Does not write app files, vault files, GitHub files, or open shortcuts.'
  };

  function now(){return new Date().toISOString()}
  function read(k, fallback){try{const v=localStorage.getItem(k);return v?JSON.parse(v):fallback}catch(_){return fallback}}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}}
  function ms(t){const n=Date.parse(t||'');return Number.isFinite(n)?n:NaN}
  function safeMessage(x){return String(x||'').slice(0,180)}
  function compactProof(p){
    const out={};
    if(!p||typeof p!=='object')return out;
    for(const k of ['save_pressed_at','expected_packet_time','latest_packet_time','latest_report_time','latest_metadata_time','route','diagnostic_version']){
      if(p[k])out[k]=String(p[k]).slice(0,120);
    }
    return out;
  }
  function ledger(){const a=read(LEDGER_KEY,[]);return Array.isArray(a)?a:[]}
  function event(type,result,message,proof){
    const list=ledger();
    const last=list[list.length-1];
    const item={
      id:'CGE-'+Date.now().toString(36),
      time:now(),
      engine_version:VERSION,
      state:state.status,
      event_type:type,
      result:result||'info',
      message:safeMessage(message),
      proof:compactProof(proof),
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
  function nextMoveFor(result,message){
    if(result==='blocked')return 'Stop risky paths and inspect before continuing.';
    if(result==='watch')return 'Keep watching; do not mutate the real app.';
    if(/freshness/i.test(message||''))return 'Run lossless diagnostic or wait for GitHub proof.';
    return 'Continue watch-only monitoring.';
  }
  function persist(){state.updated_at=now();write(STATE_KEY,state)}
  function setStatus(s,why,proof){
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
    state.loop_count++;
    state.last_heartbeat_at=now();
    write(HEARTBEAT_KEY,{time:state.last_heartbeat_at,version:VERSION,status:state.status,loop_count:state.loop_count});
    if(state.loop_count%30===0)event('HEARTBEAT_OK','good','Heartbeat alive',{route:routeProof()});
    persist();
  }
  function start(){
    state.status='RUNNING';state.started_at=state.started_at||now();event('ENGINE_STARTED','good','Watch-only engine started',{route:routeProof()});persist();
    localCheck();
  }
  function pause(){setStatus('PAUSED','User paused engine',{route:routeProof()});event('ENGINE_PAUSED','info','Engine paused by user',{})}
  function resume(){if(state.status==='PAUSED'){state.status='RUNNING';event('ENGINE_RESUMED','info','Engine resumed by user',{});persist();localCheck()}}
  function stop(){state.status='STOPPED';event('ENGINE_STOPPED','info','Engine stopped by user',{});persist()}
  function snapshot(){return JSON.parse(JSON.stringify({state,ledger:ledger()}))}

  let localTimer=null, githubTimer=null, heartbeatTimer=null;
  function installTimers(){
    if(heartbeatTimer)return;
    heartbeatTimer=setInterval(heartbeat,1000);
    localTimer=setInterval(()=>{if(state.status!=='STOPPED'&&state.status!=='PAUSED')localCheck()},10000);
    githubTimer=setInterval(()=>{if(state.status!=='STOPPED'&&state.status!=='PAUSED')githubCheck()},60000);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){setStatus('PAUSED','App hidden or backgrounded',{route:routeProof()})}else{event('APP_RESUMED','watch','App resumed; running local recovery check',{route:routeProof()});state.status='RUNNING';localCheck();githubCheck()}});
  }

  window.PMPContinuousGuardianEngineV1={version:VERSION,start,pause,resume,stop,localCheck,githubCheck,snapshot,guards:state.guards};
  write(SETTINGS_KEY,{version:VERSION,max_events:MAX_EVENTS,watch_only:true,created_at:now()});
  installTimers();
  if(read(STATE_KEY,null)&&read(STATE_KEY,null).status==='RUNNING')start();
})();
