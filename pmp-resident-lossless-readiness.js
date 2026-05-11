(() => {
  const KEYS = {
    inventoryEyes: 'pmp_inventory_eyes_latest_v1',
    inventory: 'pmp_app_lossless_inventory_latest_v1',
    receipt: 'pmp_lossless_visible_compact_latest_v1'
  };
  const ARM_KEY = 'pmp_resident_lossless_copy_arm_v1';
  function read(key) { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch (_) { return null; } }
  function write(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) {} }
  function deep() { try { let f = document.getElementById('app'), w = f && f.contentWindow, d = w && (f.contentDocument || w.document); for (let i = 0; i < 10; i++) { const n = d && d.getElementById && d.getElementById('app'); if (!n) break; w = n.contentWindow; d = n.contentDocument || w.document; } return { w, d }; } catch (_) { return {}; } }
  function cleanText(el) { return (el && el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function visible(el) { try { return !!el && (el.offsetParent !== null || getComputedStyle(el).position === 'fixed'); } catch (_) { return false; } }
  function askText(d) { const a = d && d.getElementById('ask'); return String(a && a.value || '').toLowerCase(); }
  function wantsReadiness(q) { q = String(q || '').toLowerCase(); return q.includes('lossless') && (q.includes('ready') || q.includes('readiness') || q.includes('check') || q.includes('quality')); }
  function drawerState(d) {
    let resident = false, launcher = false;
    if (!d) return { resident, launcher };
    const residentCandidates = Array.from(d.querySelectorAll('[id*="resident"],[class*="drawer"],.float'));
    for (const el of residentCandidates) {
      const t = cleanText(el).toLowerCase();
      if (!t || !visible(el)) continue;
      if ((t.includes('talk normally') && t.includes('your messages move into chat')) || (t.includes('packet request') && t.includes('copy work'))) resident = true;
    }
    const launcherCandidates = Array.from(d.querySelectorAll('[id*="launcher"],[class*="drawer"],.float'));
    for (const el of launcherCandidates) {
      const t = cleanText(el).toLowerCase();
      if (!t || !visible(el)) continue;
      if (t.includes('reload') && t.includes('last good') && !t.includes('lossless_readiness_check')) launcher = true;
    }
    return { resident, launcher };
  }
  function findBridge(d) { return d && d.getElementById('bridge'); }
  function findCopyButton(d) { if (!d) return null; for (const b of Array.from(d.querySelectorAll('button'))) if (/Copy Lossless Report|Copy Current|Copy Green Box/i.test(cleanText(b))) return b; return null; }
  function findImproveButton(d) { if (!d) return null; for (const b of Array.from(d.querySelectorAll('button'))) if (/Improve Lossless Quality/i.test(cleanText(b))) return b; return null; }
  function armResidentCopy() { write(ARM_KEY, { type: 'PMP_RESIDENT_LOSSLESS_COPY_ARM', armed_at: new Date().toISOString(), expires_at: new Date(Date.now() + 10 * 60 * 1000).toISOString(), reason: 'READY_IN_RESIDENT readiness check passed' }); }
  function buildReport(trigger) {
    const o = deep(), d = o.d;
    const invEyes = read(KEYS.inventoryEyes), inv = read(KEYS.inventory), receipt = read(KEYS.receipt);
    const bridge = findBridge(d), copyBtn = findCopyButton(d), improveBtn = findImproveButton(d), drawers = drawerState(d);
    let topReady = false, topCopyFn = false, topBuildFn = false;
    try { topReady = !!(window.top && window.top.PMP_TOP_LOSSLESS_FULL_MODULAR_READY); } catch (_) {}
    try { topCopyFn = !!(window.top && typeof window.top.pmpTopLosslessCopyAndOpen === 'function'); } catch (_) {}
    try { topBuildFn = !!(window.top && typeof window.top.pmpTopLosslessBuildPacket === 'function'); } catch (_) {}
    const isBridge = !!(bridge && bridge.classList.contains('on'));
    const coreChecks = [
      { name: 'Inventory Eyes latest report exists', pass: !!invEyes, detail: invEyes ? (invEyes.version || invEyes.type || 'present') : 'missing ' + KEYS.inventoryEyes },
      { name: 'Lossless inventory report exists', pass: !!inv, detail: inv ? (inv.version || inv.type || 'present') : 'missing ' + KEYS.inventory },
      { name: 'Lossless receipt exists', pass: !!receipt, detail: receipt ? (receipt.type || 'present') : 'missing ' + KEYS.receipt },
      { name: 'Improve Lossless Quality button exists', pass: !!improveBtn, detail: improveBtn ? cleanText(improveBtn) : 'missing' },
      { name: 'Copy Lossless Report button exists', pass: !!copyBtn, detail: copyBtn ? cleanText(copyBtn) : 'missing' },
      { name: 'Top-shell lossless loader ready', pass: topReady, detail: topReady ? 'loaded' : 'not reported ready yet' },
      { name: 'Top-shell packet builder exists', pass: topBuildFn, detail: topBuildFn ? 'available' : 'not available from Resident layer' },
      { name: 'Top-shell copy/open function exists', pass: topCopyFn, detail: topCopyFn ? 'available' : 'not available from Resident layer' }
    ];
    const coreReady = coreChecks.every(c => c.pass);
    const screenCheck = { name: 'Bridge or Resident path available', pass: isBridge || drawers.resident, detail: drawers.resident ? 'Resident path active' : isBridge ? 'Bridge active' : 'not on Bridge and Resident not open' };
    const launcherCheck = { name: 'Launcher is not blocking final tap', pass: !drawers.launcher, detail: drawers.launcher ? 'Launcher blocks final tap' : 'Launcher not blocking final tap' };
    const checks = coreChecks.concat([screenCheck, launcherCheck]);
    const ready = coreReady && screenCheck.pass && launcherCheck.pass;
    const status = ready ? (drawers.resident ? 'READY_IN_RESIDENT' : 'READY') : 'NOT_READY';
    if (status === 'READY_IN_RESIDENT') armResidentCopy();
    const summary = status === 'READY_IN_RESIDENT'
      ? 'Ready in Resident. Tap the Copy Lossless Report button shown in Resident to write to the vault. Do not press Copy Work during the vault-write test.'
      : status === 'READY'
        ? 'Ready. Tap Copy Lossless Report to write to the vault. Do not use Resident Copy Work for the vault-write test.'
        : 'Not ready. Run Improve Lossless Quality on Bridge, then check again.';
    return { type: 'PMP_RESIDENT_LOSSLESS_READINESS_CHECK', version: '1.3.0-arm-resident-button', built_at: new Date().toISOString(), trigger: trigger || 'resident', status, summary, resident_open: drawers.resident, launcher_open: drawers.launcher, core_ready: coreReady, final_tap_available: ready, resident_copy_button_armed: status === 'READY_IN_RESIDENT', checks, manual_final_step: 'Tap Copy Lossless Report as a real top-shell tap. This can be done from Bridge or from the Resident-visible Copy Lossless button.', after_manual_step: 'After the Shortcut finishes, ask ChatGPT to check the vault current record.', guardrail: 'Resident Copy Work copies diagnostic work only and can overwrite the clipboard, so do not use Copy Work during the vault-write test.' };
  }
  function showReport(report) { const o = deep(), d = o.d; if (!d) return; const reply = d.getElementById('residentReply'), work = d.getElementById('residentWork'); if (reply) reply.textContent = report.summary; if (work) { work.classList.remove('hidden'); work.textContent = JSON.stringify(report, null, 2); } write('pmp_resident_lossless_readiness_latest_v1', report); }
  function patch() { const o = deep(), w = o.w, d = o.d; if (!w || !d) return; w.pmpResidentCheckLosslessReadiness = function () { const r = buildReport('manual_function'); showReport(r); return r; }; if (!w.__pmpResidentLosslessReadinessRunPatched) { w.__pmpResidentLosslessReadinessRunPatched = true; const oldRun = typeof w.residentRun === 'function' ? w.residentRun : null; w.residentRun = function () { const q = askText(d); if (wantsReadiness(q) || (q.includes('copy lossless') && q.includes('resident'))) { const r = buildReport('resident_question'); showReport(r); return r; } if (oldRun) return oldRun.apply(this, arguments); }; } for (const b of Array.from(d.querySelectorAll('button'))) { const t = cleanText(b); if (t === 'Run' && !b.dataset.losslessReadinessRun) { b.dataset.losslessReadinessRun = '1'; b.addEventListener('click', e => { const q = askText(d); if (wantsReadiness(q) || (q.includes('copy lossless') && q.includes('resident'))) { e.preventDefault(); e.stopImmediatePropagation(); showReport(buildReport('run_button_capture')); } }, true); } } }
  setInterval(patch, 700); setTimeout(patch, 200); window.pmpResidentLosslessReadinessPatch = patch;
})();
