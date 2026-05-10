(() => {
  const KEYS = {
    inventoryEyes: 'pmp_inventory_eyes_latest_v1',
    inventory: 'pmp_app_lossless_inventory_latest_v1',
    receipt: 'pmp_lossless_visible_compact_latest_v1'
  };
  function read(key) {
    try { return JSON.parse(localStorage.getItem(key) || 'null'); }
    catch (_) { return null; }
  }
  function deep() {
    try {
      let f = document.getElementById('app');
      let w = f && f.contentWindow;
      let d = w && (f.contentDocument || w.document);
      for (let i = 0; i < 10; i++) {
        const n = d && d.getElementById && d.getElementById('app');
        if (!n) break;
        w = n.contentWindow;
        d = n.contentDocument || w.document;
      }
      return { w, d };
    } catch (_) { return {}; }
  }
  function cleanText(el) { return (el && el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function visible(el) {
    try { return !!el && (el.offsetParent !== null || getComputedStyle(el).position === 'fixed'); }
    catch (_) { return false; }
  }
  function askText(d) {
    const a = d && d.getElementById('ask');
    return String(a && a.value || '').toLowerCase();
  }
  function wantsReadiness(q) {
    q = String(q || '').toLowerCase();
    return q.includes('lossless') && (q.includes('ready') || q.includes('readiness') || q.includes('check') || q.includes('quality'));
  }
  function drawerOpen(d) {
    if (!d) return false;
    const candidates = Array.from(d.querySelectorAll('[id*="resident"],[id*="launcher"],[class*="drawer"],[class*="modal"],[class*="overlay"],.float,.panel'));
    for (const el of candidates) {
      const t = cleanText(el).toLowerCase();
      if (!t) continue;
      if (!visible(el)) continue;
      if ((t.includes('talk normally') && t.includes('your messages move into chat')) ||
          (t.includes('packet request') && t.includes('copy work')) ||
          (t.includes('launcher') && t.includes('reload') && t.includes('last good'))) return true;
    }
    return false;
  }
  function findBridge(d) {
    return d && d.getElementById('bridge');
  }
  function findCopyButton(d) {
    if (!d) return null;
    for (const b of Array.from(d.querySelectorAll('button'))) {
      if (/Copy Lossless Report|Copy Current|Copy Green Box/i.test(cleanText(b))) return b;
    }
    return null;
  }
  function findImproveButton(d) {
    if (!d) return null;
    for (const b of Array.from(d.querySelectorAll('button'))) {
      if (/Improve Lossless Quality/i.test(cleanText(b))) return b;
    }
    return null;
  }
  function statusLine(checks) {
    return checks.every(c => c.pass) ? 'READY' : 'NOT_READY';
  }
  function buildReport(trigger) {
    const o = deep();
    const d = o.d;
    const invEyes = read(KEYS.inventoryEyes);
    const inv = read(KEYS.inventory);
    const receipt = read(KEYS.receipt);
    const bridge = findBridge(d);
    const copyBtn = findCopyButton(d);
    const improveBtn = findImproveButton(d);
    let topReady = false;
    try { topReady = !!(window.top && window.top.PMP_TOP_LOSSLESS_FULL_MODULAR_READY); } catch (_) {}
    let topCopyFn = false;
    try { topCopyFn = !!(window.top && typeof window.top.pmpTopLosslessCopyAndOpen === 'function'); } catch (_) {}
    let topBuildFn = false;
    try { topBuildFn = !!(window.top && typeof window.top.pmpTopLosslessBuildPacket === 'function'); } catch (_) {}
    const isBridge = !!(bridge && bridge.classList.contains('on'));
    const isDrawerOpen = drawerOpen(d);
    const checks = [
      { name: 'Inventory Eyes latest report exists', pass: !!invEyes, detail: invEyes ? (invEyes.version || invEyes.type || 'present') : 'missing ' + KEYS.inventoryEyes },
      { name: 'Lossless inventory report exists', pass: !!inv, detail: inv ? (inv.version || inv.type || 'present') : 'missing ' + KEYS.inventory },
      { name: 'Lossless receipt exists', pass: !!receipt, detail: receipt ? (receipt.type || 'present') : 'missing ' + KEYS.receipt },
      { name: 'Improve Lossless Quality button exists', pass: !!improveBtn, detail: improveBtn ? cleanText(improveBtn) : 'missing' },
      { name: 'Copy Lossless Report button exists', pass: !!copyBtn, detail: copyBtn ? cleanText(copyBtn) : 'missing' },
      { name: 'Top-shell lossless loader ready', pass: topReady, detail: topReady ? 'loaded' : 'not reported ready yet' },
      { name: 'Top-shell packet builder exists', pass: topBuildFn, detail: topBuildFn ? 'available' : 'not available from Resident layer' },
      { name: 'Top-shell copy/open function exists', pass: topCopyFn, detail: topCopyFn ? 'available' : 'not available from Resident layer' },
      { name: 'Bridge screen is active', pass: isBridge, detail: isBridge ? 'Bridge active' : 'not on Bridge screen' },
      { name: 'Resident/Launcher drawer not open for final manual tap', pass: !isDrawerOpen, detail: isDrawerOpen ? 'drawer open; close it before final manual tap' : 'no drawer blocking Bridge' }
    ];
    const ready = statusLine(checks);
    const summary = ready === 'READY'
      ? 'Ready. Tap Copy Lossless Report manually to write to the vault. Do not use Resident Copy Work for the vault-write test.'
      : 'Not ready. Run Improve Lossless Quality on Bridge, close drawers, then check again.';
    return {
      type: 'PMP_RESIDENT_LOSSLESS_READINESS_CHECK',
      version: '1.0.0',
      built_at: new Date().toISOString(),
      trigger: trigger || 'resident',
      status: ready,
      summary,
      checks,
      manual_final_step: 'User manually taps Copy Lossless Report. Resident must not claim the Shortcut completed the vault write.',
      after_manual_step: 'After the Shortcut finishes, ask ChatGPT to check the vault current record.',
      guardrail: 'Resident Copy Work copies diagnostic work only and can overwrite the clipboard, so do not use Copy Work during the vault-write test.'
    };
  }
  function showReport(report) {
    const o = deep();
    const d = o.d;
    if (!d) return;
    const reply = d.getElementById('residentReply');
    const work = d.getElementById('residentWork');
    if (reply) reply.textContent = report.summary;
    if (work) {
      work.classList.remove('hidden');
      work.textContent = JSON.stringify(report, null, 2);
    }
    try {
      localStorage.setItem('pmp_resident_lossless_readiness_latest_v1', JSON.stringify(report));
    } catch (_) {}
  }
  function patch() {
    const o = deep();
    const w = o.w, d = o.d;
    if (!w || !d) return;
    w.pmpResidentCheckLosslessReadiness = function () {
      const r = buildReport('manual_function');
      showReport(r);
      return r;
    };
    if (!w.__pmpResidentLosslessReadinessRunPatched) {
      w.__pmpResidentLosslessReadinessRunPatched = true;
      const oldRun = typeof w.residentRun === 'function' ? w.residentRun : null;
      w.residentRun = function () {
        const q = askText(d);
        if (wantsReadiness(q) || (q.includes('copy lossless') && q.includes('resident'))) {
          const r = buildReport('resident_question');
          showReport(r);
          return r;
        }
        if (oldRun) return oldRun.apply(this, arguments);
      };
    }
    for (const b of Array.from(d.querySelectorAll('button'))) {
      const t = cleanText(b);
      if (t === 'Run' && !b.dataset.losslessReadinessRun) {
        b.dataset.losslessReadinessRun = '1';
        b.addEventListener('click', e => {
          const q = askText(d);
          if (wantsReadiness(q) || (q.includes('copy lossless') && q.includes('resident'))) {
            e.preventDefault();
            e.stopImmediatePropagation();
            showReport(buildReport('run_button_capture'));
          }
        }, true);
      }
    }
  }
  setInterval(patch, 700);
  setTimeout(patch, 200);
  window.pmpResidentLosslessReadinessPatch = patch;
})();
