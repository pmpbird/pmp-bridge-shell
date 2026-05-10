(() => {
  function inject() {
    try {
      const topDoc = window.top && window.top.document;
      if (!topDoc) return;
      const old = topDoc.getElementById('pmpTopLosslessFullModularLoader');
      if (old) old.remove();
      const s = topDoc.createElement('script');
      s.id = 'pmpTopLosslessFullModularLoader';
      s.src = 'pmp-top-lossless-loader.js?fresh=' + encodeURIComponent('loader-' + Date.now() + '-' + Math.random().toString(36).slice(2));
      topDoc.head.appendChild(s);
    } catch (_) {}
  }
  setTimeout(inject, 200);
  setInterval(inject, 5000);
})();
