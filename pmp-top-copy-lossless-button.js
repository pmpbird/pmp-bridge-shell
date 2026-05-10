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
    topButton.innerHTML = '⧉ Copy Lossless Report<small style="display:block;font-weight:800;opacity:.85">Open Vault Shortcut</small>';
    topButton.style.position = 'fixed';
    topButton.style.zIndex = '999999';
    topButton.style.display = 'none';
    topButton.style.border = '0';
    topButton.style.borderRadius = '22px';
    topButton.style.background = '#a1fcfd';
    topButton.style.color = '#101827';
    topButton.style.fontWeight = '950';
    topButton.style.fontSize = '16px';
    topButton.style.boxShadow = '0 8px 20px rgba(0,0,0,.25)';
    topButton.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      if (typeof window.pmpTopLosslessCopyAndOpen === 'function') window.pmpTopLosslessCopyAndOpen();
    }, true);
    document.body.appendChild(topButton);
    return topButton;
  }
  function update() {
    const o = inner();
    const target = bridgeCopyButton(o.d);
    const b = make();
    if (!target) { b.style.display = 'none'; return; }
    const r = target.getBoundingClientRect();
    b.style.display = 'block';
    b.style.left = Math.round(r.left) + 'px';
    b.style.top = Math.round(r.top) + 'px';
    b.style.width = Math.round(r.width) + 'px';
    b.style.height = Math.round(r.height) + 'px';
  }
  setInterval(update, 300);
  setTimeout(update, 200);
})();
