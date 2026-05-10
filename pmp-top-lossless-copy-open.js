(() => {
  const SHORTCUT_URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent('PMP Vault GitHub Writer');
  function copyFallback(text) {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      ta.remove();
      return true;
    } catch (_) { return false; }
  }
  function innerDoc() {
    try {
      const frame = document.getElementById('app');
      let d = frame && (frame.contentDocument || frame.contentWindow.document);
      for (let i = 0; i < 8; i++) {
        const n = d && d.getElementById && d.getElementById('app');
        if (!n) break;
        d = n.contentDocument || n.contentWindow.document;
      }
      return d;
    } catch (_) { return null; }
  }
  function status(msg) {
    const d = innerDoc();
    if (!d) return;
    const r = d.getElementById('residentReply');
    const c = d.getElementById('controlStatus');
    if (r) r.textContent = msg;
    if (c) c.textContent = msg;
  }
  function run() {
    const builder = window.pmpTopLosslessBuildPacket;
    const text = typeof builder === 'function' ? builder() : null;
    if (!text) {
      status('No full report found. Run Improve Lossless Quality first.');
      return false;
    }
    copyFallback(text);
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).catch(() => {});
    status('Copied Vault Write Packet. Opening PMP Vault GitHub Writer Shortcut.');
    window.location.href = SHORTCUT_URL;
    return true;
  }
  window.pmpTopLosslessCopyAndOpen = run;
})();
