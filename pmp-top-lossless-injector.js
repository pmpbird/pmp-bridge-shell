(() => {
  function inject() {
    try {
      const topDoc = window.top && window.top.document;
      if (!topDoc || topDoc.getElementById('pmpTopLosslessFullModularLoader')) return;
      const s = topDoc.createElement('script');
      s.id = 'pmpTopLosslessFullModularLoader';
      s.src = 'pmp-top-lossless-loader.js?fresh=full-modular-v1';
      topDoc.head.appendChild(s);
    } catch (_) {}
  }
  setTimeout(inject, 200);
  setInterval(inject, 1200);
})();
