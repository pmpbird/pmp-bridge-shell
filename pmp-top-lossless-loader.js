(() => {
  const files = [
    'pmp-top-lossless-packet-builder.js',
    'pmp-top-lossless-copy-open.js',
    'pmp-top-copy-lossless-button.js'
  ];
  function fresh(src) {
    return src + '?fresh=' + encodeURIComponent('top-lossless-' + Date.now() + '-' + Math.random().toString(36).slice(2));
  }
  function removeOld(id) {
    try { const old = document.getElementById(id); if (old) old.remove(); } catch (_) {}
  }
  function loadOne(src, index) {
    return new Promise(resolve => {
      const id = 'pmpTopLosslessScript' + index;
      removeOld(id);
      const s = document.createElement('script');
      s.id = id;
      s.src = fresh(src);
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
  }
  async function start() {
    for (let i = 0; i < files.length; i++) await loadOne(files[i], i);
    window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY = true;
    window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY_AT = new Date().toISOString();
  }
  window.pmpReloadTopLosslessFullModular = start;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
