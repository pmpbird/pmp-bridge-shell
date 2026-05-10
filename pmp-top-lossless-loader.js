(() => {
  const files = [
    'pmp-top-lossless-packet-builder.js?fresh=full-modular-v1',
    'pmp-top-lossless-copy-open.js?fresh=full-modular-v1',
    'pmp-top-copy-lossless-button.js?fresh=full-modular-v1'
  ];
  function loadOne(src) {
    return new Promise(resolve => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
  }
  async function start() {
    for (const f of files) await loadOne(f);
    window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY = true;
    window.PMP_TOP_LOSSLESS_FULL_MODULAR_READY_AT = new Date().toISOString();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
