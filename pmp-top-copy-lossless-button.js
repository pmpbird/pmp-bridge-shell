(() => {
  let topButton = null;
  const READY_KEY = 'pmp_resident_lossless_readiness_latest_v1';
  function inner() {
    try {
      const frame = document.getElementById('app');
      let w = frame && frame.contentWindow;
      let d = w && (frame.contentDocument || w.document);
      for (let i = 0; i < 8; i++) {
        const n = d && d.getElementById && d.getElementById('app');
        if (!n) break;
        w = n.contentWindow;
        d = n.contentDocument || w.document;
      }
      return { w, d };
    } catch (_) { return {}; }
  }
  function clean(el) { return (el && el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function shown(el) { try { return !!el && (el.offsetParent !== null || getComputedStyle(el).position === 'fixed'); } catch (_) { return false; } }
  function latestReadyInResident() {
    try {
      const r = JSON.parse(localStorage.getItem(READY_KEY) || 'null');
      if (!r || r.status !== 'READY_IN_RESIDENT') return false;
      const age = Date.now() - Date.parse(r.built_at || 0);
      return Number.isFinite(age) && age >= 0 && age < 10 * 60 * 1000;
    } catch (_) { return false; }
  }
  function activeBridgeCopyButton(d) {
    if (!d) return null;
    const bridge = d.getElementById('bridge');
    if (!bridge || !bridge.classList.contains('on')) return null;
    for (const b of Array.from(d.querySelectorAll('button'))) {
      const t = clean(b);
      if (/Copy Lossless Report|Copy Current|Copy Green Box/i.test(t)) return b;
    }
    return null;
  }
  function residentDrawer(d) {
    if (!d) return null;
    const candidates = Array.from(d.querySelectorAll('[id*="resident"],[class*="drawer"],.float,.panel'));
    for (const el of candidates) {
      if (!shown(el)) continue;
      const t = clean(el).toLowerCase();
      if ((t.includes('talk normally') && t.includes('your messages move into chat')) ||
          (t.includes('packet request') && t.includes('copy work'))) return el;
    }
    return null;
  }
  function launcherDrawer(d) {
    if (!d) return null;
    const candidates = Array.from(d.querySelectorAll('[id*="launcher"],[class*="drawer"],.float,.panel'));
    for (const el of candidates) {
      if (!shown(el)) continue;
      const t = clean(el).toLowerCase();
      if (t.includes('launcher') && t.includes('reload') && t.includes('last good')) return el;
    }
    return null;
  }
  function residentAnchor(d) {
    if (!latestReadyInResident()) return null;
    const drawer = residentDrawer(d);
    if (!drawer) return null;
    const buttons = Array.from(drawer.querySelectorAll('button'));
    let after = null;
    for (const b of buttons) {
      const t = clean(b);
      if (/Copy Work|Show Work|Run/i.test(t)) after = b;
    }
    const r = (after || drawer).getBoundingClientRect();
    const dr = drawer.getBoundingClientRect();
    const top = after ? Math.min(r.bottom + 8, dr.bottom - 80) : dr.top + 76;
    return { left: Math.round(dr.left + 14), top: Math.round(top), width: Math.round(Math.max(260, dr.width - 28)), height: 68 };
  }
  function bridgeAnchor(d) {
    if (residentDrawer(d) || launcherDrawer(d)) return null;
    const target = activeBridgeCopyButton(d);
    if (!target) return null;
    const r = target.getBoundingClientRect();
    return { left: Math.round(r.left), top: Math.round(r.top), width: Math.round(r.width), height: Math.round(r.height) };
  }
  function make() {
    if (topButton) return topButton;
    topButton = document.createElement('button');
    topButton.id = 'pmpTopCopyLosslessButton';
    topButton.type = 'button';
    topButton.innerHTML = '<span class="pmpCopyIcon">⧉</span><span class="pmpCopyText"><span class="pmpCopyTitle">Copy Lossless Report</span><small>Open Vault Shortcut</small></span><span class="pmpCopyArrow">›</span>';
    topButton.style.position = 'fixed';
    topButton.style.zIndex = '999999';
    topButton.style.display = 'none';
    topButton.style.boxSizing = 'border-box';
    topButton.style.border = '0';
    topButton.style.borderRadius = '22px';
    topButton.style.background = '#a1fcfd';
    topButton.style.color = '#101827';
    topButton.style.fontFamily = '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif';
    topButton.style.fontWeight = '950';
    topButton.style.boxShadow = '0 8px 20px rgba(0,0,0,.25)';
    topButton.style.padding = '0 14px';
    topButton.style.overflow = 'hidden';
    topButton.style.webkitAppearance = 'none';
    topButton.style.gridTemplateColumns = '40px 1fr 22px';
    topButton.style.alignItems = 'center';
    topButton.style.columnGap = '10px';
    topButton.style.textAlign = 'left';
    topButton.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      if (typeof window.pmpTopLosslessCopyAndOpen === 'function') window.pmpTopLosslessCopyAndOpen();
    }, true);
    document.body.appendChild(topButton);
    return topButton;
  }
  function styleChildren(b) {
    const icon = b.querySelector('.pmpCopyIcon');
    const textSpan = b.querySelector('.pmpCopyText');
    const title = b.querySelector('.pmpCopyTitle');
    const small = b.querySelector('small');
    const arrow = b.querySelector('.pmpCopyArrow');
    if (icon) { icon.style.fontSize = '23px'; icon.style.lineHeight = '1'; icon.style.textAlign = 'center'; icon.style.display = 'block'; }
    if (textSpan) { textSpan.style.display = 'block'; textSpan.style.minWidth = '0'; textSpan.style.textAlign = 'left'; }
    if (title) { title.style.display = 'block'; title.style.fontSize = '16px'; title.style.lineHeight = '1.12'; title.style.fontWeight = '950'; title.style.whiteSpace = 'nowrap'; title.style.overflow = 'hidden'; title.style.textOverflow = 'ellipsis'; }
    if (small) { small.style.display = 'block'; small.style.fontSize = '11px'; small.style.lineHeight = '1.12'; small.style.fontWeight = '800'; small.style.opacity = '.82'; small.style.marginTop = '3px'; small.style.whiteSpace = 'nowrap'; small.style.overflow = 'hidden'; small.style.textOverflow = 'ellipsis'; }
    if (arrow) { arrow.style.fontSize = '30px'; arrow.style.fontWeight = '900'; arrow.style.lineHeight = '1'; arrow.style.textAlign = 'right'; arrow.style.opacity = '.85'; }
  }
  function update() {
    const o = inner();
    const d = o.d;
    const b = make();
    const pos = residentAnchor(d) || bridgeAnchor(d);
    if (!pos) { b.style.display = 'none'; return; }
    b.style.display = 'grid';
    b.style.left = pos.left + 'px';
    b.style.top = pos.top + 'px';
    b.style.width = pos.width + 'px';
    b.style.height = pos.height + 'px';
    styleChildren(b);
  }
  window.pmpRefreshTopCopyLosslessButton = update;
  setInterval(update, 250);
  setTimeout(update, 100);
})();
