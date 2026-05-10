(() => {
  let topButton = null;
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
  function bridgeCopyButton(d) {
    if (!d) return null;
    const bridge = d.getElementById('bridge');
    if (!bridge || !bridge.classList.contains('on')) return null;
    for (const b of Array.from(d.querySelectorAll('button'))) {
      const t = (b.textContent || '').replace(/\s+/g, ' ').trim();
      if (/Copy Lossless Report|Copy Current|Copy Green Box/i.test(t)) return b;
    }
    return null;
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
    const text = b.querySelector('.pmpCopyText');
    const title = b.querySelector('.pmpCopyTitle');
    const small = b.querySelector('small');
    const arrow = b.querySelector('.pmpCopyArrow');
    if (icon) { icon.style.fontSize = '23px'; icon.style.lineHeight = '1'; icon.style.textAlign = 'center'; icon.style.display = 'block'; }
    if (text) { text.style.display = 'block'; text.style.minWidth = '0'; text.style.textAlign = 'left'; }
    if (title) { title.style.display = 'block'; title.style.fontSize = '16px'; title.style.lineHeight = '1.12'; title.style.fontWeight = '950'; title.style.whiteSpace = 'nowrap'; title.style.overflow = 'hidden'; title.style.textOverflow = 'ellipsis'; }
    if (small) { small.style.display = 'block'; small.style.fontSize = '11px'; small.style.lineHeight = '1.12'; small.style.fontWeight = '800'; small.style.opacity = '.82'; small.style.marginTop = '3px'; small.style.whiteSpace = 'nowrap'; small.style.overflow = 'hidden'; small.style.textOverflow = 'ellipsis'; }
    if (arrow) { arrow.style.fontSize = '30px'; arrow.style.fontWeight = '900'; arrow.style.lineHeight = '1'; arrow.style.textAlign = 'right'; arrow.style.opacity = '.85'; }
  }
  function update() {
    const o = inner();
    const target = bridgeCopyButton(o.d);
    const b = make();
    if (!target) { b.style.display = 'none'; return; }
    const r = target.getBoundingClientRect();
    b.style.display = 'grid';
    b.style.left = Math.round(r.left) + 'px';
    b.style.top = Math.round(r.top) + 'px';
    b.style.width = Math.round(r.width) + 'px';
    b.style.height = Math.round(r.height) + 'px';
    styleChildren(b);
  }
  window.pmpRefreshTopCopyLosslessButton = update;
  setInterval(update, 250);
  setTimeout(update, 100);
})();
