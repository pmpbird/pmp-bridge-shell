(() => {
  const SHORTCUT_NAME = 'PMP Vault GitHub Writer';
  const URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT_NAME);
  let button = null;
  function innerDoc() {
    try {
      const frame = document.getElementById('app');
      let d = frame && (frame.contentDocument || frame.contentWindow.document);
      for (let i = 0; i < 8; i++) {
        const nested = d && d.getElementById && d.getElementById('app');
        if (!nested) break;
        d = nested.contentDocument || nested.contentWindow.document;
      }
      return d;
    } catch (_) { return null; }
  }
  function makeButton() {
    if (button) return button;
    button = document.createElement('button');
    button.id = 'pmpTopVaultShortcutButton';
    button.textContent = 'Open Vault Shortcut';
    button.type = 'button';
    button.style.position = 'fixed';
    button.style.left = '14px';
    button.style.right = '14px';
    button.style.zIndex = '999999';
    button.style.display = 'none';
    button.style.padding = '14px';
    button.style.border = '2px solid #ffffff';
    button.style.borderRadius = '16px';
    button.style.background = '#a1fcfd';
    button.style.color = '#101827';
    button.style.fontWeight = '950';
    button.style.fontSize = '16px';
    button.style.boxShadow = '0 8px 20px rgba(0,0,0,.25)';
    button.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = URL;
    }, true);
    document.body.appendChild(button);
    return button;
  }
  function findBridgeToolBottom(d) {
    if (!d) return null;
    const bridge = d.getElementById('bridge');
    if (!bridge || !bridge.classList.contains('on')) return null;
    const toolstrip = bridge.querySelector('.toolstrip');
    if (!toolstrip) return null;
    const r = toolstrip.getBoundingClientRect();
    return { top: Math.round(r.bottom + 8), left: Math.round(r.left), width: Math.round(r.width) };
  }
  function update() {
    const d = innerDoc();
    const btn = makeButton();
    const pos = findBridgeToolBottom(d);
    if (!pos) { btn.style.display = 'none'; return; }
    btn.style.display = 'block';
    btn.style.top = pos.top + 'px';
    btn.style.left = Math.max(10, pos.left) + 'px';
    btn.style.width = Math.max(280, pos.width) + 'px';
    btn.style.right = 'auto';
  }
  setInterval(update, 400);
  setTimeout(update, 300);
})();
