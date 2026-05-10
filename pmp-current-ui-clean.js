(() => {
  function deep() {
    try {
      const f = document.getElementById('app');
      const w = f && f.contentWindow;
      const d = w && (f.contentDocument || w.document);
      return { w, d };
    } catch (_) { return {}; }
  }
  function cleanText(s) {
    return String(s || '').replace(/single-file v6|PMP Home Single v6|v6 home|v6 target|pmp-home-single-v6\.html/gi, 'PMP Current');
  }
  function patch() {
    const { d } = deep();
    if (!d || !d.body) return;
    if (d.title && /v6/i.test(d.title)) d.title = 'PMP Current';
    for (const el of Array.from(d.querySelectorAll('h1,p,div,small,span,button,.sub,.note,.statusbar'))) {
      if (!el || !el.childNodes) continue;
      for (const n of Array.from(el.childNodes)) {
        if (n.nodeType === 3 && /v6|single-file|pmp-home-single-v6/i.test(n.nodeValue || '')) n.nodeValue = cleanText(n.nodeValue);
      }
    }
    for (const btn of Array.from(d.querySelectorAll('button'))) {
      const t = (btn.textContent || '').replace(/\s+/g, ' ').trim();
      if (/Prepare Project Export/i.test(t)) {
        btn.style.display = 'none';
        btn.setAttribute('aria-hidden', 'true');
      }
      if (/Copy Current|Copy Green Box/i.test(t)) {
        const spans = Array.from(btn.querySelectorAll('span'));
        if (spans.length >= 2) spans[1].innerHTML = 'Copy Lossless Report<small>Open Vault Shortcut</small>';
        else btn.textContent = 'Copy Lossless Report';
      }
      if (/Automatic App Update/i.test(t)) {
        const small = btn.querySelector('small');
        if (small) small.textContent = 'check current app, stay inside PMP';
      }
    }
    const worldSub = Array.from(d.querySelectorAll('p.sub')).find(x => /Clean PMP Current|PMP Current|single-file/i.test(x.textContent || ''));
    if (worldSub && /single-file|v6/i.test(worldSub.textContent || '')) worldSub.textContent = 'PMP Current. One Home Screen app. Internal versions stay hidden.';
  }
  setInterval(patch, 700);
  setTimeout(patch, 250);
  setTimeout(patch, 1200);
})();
