(() => {
  const VERSION = '1.1.0-mirror-only-save-click-diagnostic';
  const MIRROR_PAGE = 'pmp-continuous-guardian-mirror-v1.html';
  if (!String(location.pathname || '').includes(MIRROR_PAGE)) return;

  let saveDiag = {
    found: 'not checked',
    tap_detected: 'not tested',
    handler: 'not checked',
    shortcut_attempt: 'not triggered by diagnostic',
    failure_reason: 'not checked'
  };

  function $(id){return document.getElementById(id)}
  function engine(){return window.PMPContinuousGuardianEngineV1 || null}
  function snap(){const g=engine(); if(!g || !g.snapshot) return null; try{return g.snapshot()}catch(_){return null}}
  function set(id,value){const el=$(id); if(el) el.textContent = String(value == null ? '—' : value)}
  function run(name){
    const g = engine();
    if (g && typeof g[name] === 'function') {
      try {
        const r = g[name]();
        if (r && typeof r.then === 'function') r.then(refresh).catch(refresh);
      } catch (_) {}
    }
    refresh();
  }
  function getDeepDoc(){
    try{
      let f = document.getElementById('app');
      let w = f && f.contentWindow;
      let d = w && (f.contentDocument || w.document);
      for(let i=0;i<10;i++){
        const n = d && d.getElementById && d.getElementById('app');
        if(!n) break;
        w = n.contentWindow;
        d = n.contentDocument || w.document;
      }
      return { w, d };
    }catch(e){return { error: String(e && e.message || e) }}
  }
  function allButtons(d){
    try{return Array.from(d.querySelectorAll('button')).filter(Boolean)}catch(_){return[]}
  }
  function findSaveButton(){
    const o = getDeepDoc();
    const d = o.d;
    if(!d) return { found:false, reason:o.error || 'app document not reachable' };
    const btn = allButtons(d).find(b => /Save\s+to\s+GitHub\s+Vault/i.test((b.textContent || '').replace(/\s+/g,' ')));
    if(!btn) return { found:false, reason:'Save to GitHub Vault button not found' };
    return { found:true, button:btn, doc:d };
  }
  function diagnoseSaveClick(){
    const r = findSaveButton();
    if(!r.found){
      saveDiag = { found:'NO', tap_detected:'NO', handler:'UNKNOWN', shortcut_attempt:'NOT TRIGGERED', failure_reason:r.reason };
      refresh();
      return;
    }
    const b = r.button;
    const rect = b.getBoundingClientRect ? b.getBoundingClientRect() : null;
    let visible = 'UNKNOWN', enabled = 'UNKNOWN', top = 'UNKNOWN';
    try { visible = !!(rect && rect.width > 0 && rect.height > 0); } catch(_) {}
    try { enabled = !b.disabled; } catch(_) {}
    try {
      const cx = rect.left + rect.width/2, cy = rect.top + rect.height/2;
      const topEl = r.doc.elementFromPoint(cx, cy);
      top = (topEl === b || b.contains(topEl)) ? 'YES' : 'NO';
    } catch(_) {}
    const inlineHandler = !!(b.onclick || b.getAttribute('onclick'));
    saveDiag = {
      found: 'YES',
      tap_detected: saveDiag.tap_detected || 'not tested',
      handler: inlineHandler ? 'INLINE FOUND' : 'NOT DIRECTLY INTROSPECTABLE',
      shortcut_attempt: 'NOT TRIGGERED BY DIAGNOSTIC',
      failure_reason: visible !== true ? 'button not visibly measurable' : enabled !== true ? 'button disabled' : top === 'NO' ? 'button may be covered or not topmost at center' : 'none found by passive check'
    };
    try{
      if(!b.__pmpMirrorSaveDiagListener){
        b.__pmpMirrorSaveDiagListener = true;
        b.addEventListener('click', () => {
          saveDiag.tap_detected = new Date().toISOString();
          saveDiag.shortcut_attempt = 'USER CLICK DETECTED; DIAGNOSTIC DID NOT TRIGGER IT';
          setTimeout(refresh,50);
        }, true);
      }
    }catch(_){}
    refresh();
  }
  function refresh(){
    const g = engine();
    const s = snap();
    set('cgeEngine', g ? (g.version || 'loaded') : 'loading');
    set('cgeState', s && s.state && s.state.status || 'WAITING');
    set('cgeHeartbeat', s && s.state && s.state.last_heartbeat_at || '—');
    set('cgeLocalStatus', s && s.state && s.state.local && s.state.local.status || '—');
    set('cgeGithubStatus', s && s.state && s.state.github && s.state.github.status || '—');
    set('cgeLedger', s && Array.isArray(s.ledger) ? s.ledger.length : 0);
    set('cgeSaveDiag', 'FOUND: '+saveDiag.found+' | TAP: '+saveDiag.tap_detected+' | HANDLER: '+saveDiag.handler+' | SHORTCUT: '+saveDiag.shortcut_attempt+' | REASON: '+saveDiag.failure_reason);
  }
  function install(){
    if ($('cgePanel')) return;
    const style = document.createElement('style');
    style.textContent = `
      #cgePanel{position:fixed;left:10px;right:10px;bottom:10px;z-index:2147483647;background:rgba(255,255,255,.96);border:3px solid #07101c;border-radius:18px;padding:10px;box-shadow:0 8px 24px rgba(0,0,0,.22);font-size:12px;font-weight:900;color:#07101c;max-height:42vh;overflow:auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      #cgePanel .cgeTop{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:8px}
      #cgePanel .cgeTitle{font-size:13px}#cgePanel .cgeGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:8px}
      #cgePanel button{border:2px solid #07101c;border-radius:12px;background:#acd1fb;font-weight:950;padding:8px 6px;color:#07101c}
      #cgePanel .cgeStats{display:grid;grid-template-columns:1fr 1fr;gap:5px}#cgePanel .cgeStat{background:#f6f6f6;border:1px solid #07101c;border-radius:10px;padding:5px;min-height:26px}
      #cgePanel .wide{grid-column:1/-1}
      #cgePanel.mini .cgeGrid,#cgePanel.mini .cgeStats{display:none}
    `;
    document.head.appendChild(style);
    const panel = document.createElement('div');
    panel.id = 'cgePanel';
    panel.setAttribute('aria-label','Mirror-only Guardian Test Panel');
    panel.innerHTML = `
      <div class="cgeTop"><div class="cgeTitle">MIRROR-ONLY GUARDIAN TEST PANEL</div><button id="cgeMini" type="button">MINI</button></div>
      <div class="cgeGrid">
        <button id="cgeStart" type="button">START</button>
        <button id="cgePause" type="button">PAUSE</button>
        <button id="cgeResume" type="button">RESUME</button>
        <button id="cgeStop" type="button">STOP</button>
        <button id="cgeLocal" type="button">LOCAL CHECK</button>
        <button id="cgeGithub" type="button">GITHUB CHECK</button>
        <button id="cgeSave" type="button">SAVE DIAG</button>
      </div>
      <div class="cgeStats">
        <div class="cgeStat">STATE<br><span id="cgeState">WAITING</span></div>
        <div class="cgeStat">LAST HEARTBEAT<br><span id="cgeHeartbeat">—</span></div>
        <div class="cgeStat">LOCAL STATUS<br><span id="cgeLocalStatus">—</span></div>
        <div class="cgeStat">GITHUB STATUS<br><span id="cgeGithubStatus">—</span></div>
        <div class="cgeStat">LEDGER COUNT<br><span id="cgeLedger">0</span></div>
        <div class="cgeStat">ENGINE<br><span id="cgeEngine">loading</span></div>
        <div class="cgeStat wide">SAVE CLICK DIAGNOSTIC<br><span id="cgeSaveDiag">not checked</span></div>
      </div>
    `;
    document.body.appendChild(panel);
    $('cgeStart').onclick = () => run('start');
    $('cgePause').onclick = () => run('pause');
    $('cgeResume').onclick = () => run('resume');
    $('cgeStop').onclick = () => run('stop');
    $('cgeLocal').onclick = () => run('localCheck');
    $('cgeGithub').onclick = () => run('githubCheck');
    $('cgeSave').onclick = () => diagnoseSaveClick();
    $('cgeMini').onclick = () => panel.classList.toggle('mini');
    refresh();
    setInterval(refresh,1000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
  window.PMPGuardianMirrorTestPanelV1 = { version: VERSION, refresh, diagnoseSaveClick };
})();
