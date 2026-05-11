(function(){
  const BUG_MEMORY_URL = () => 'bm.html?fresh=bug-memory-direct-clean-' + Date.now();
  function deep(){
    try{
      let frame = document.getElementById('app');
      let w = frame && frame.contentWindow;
      let d = frame && (frame.contentDocument || w.document);
      for(let i=0;i<8;i++){
        const inner = d && d.getElementById && d.getElementById('app');
        if(!inner) break;
        w = inner.contentWindow;
        d = inner.contentDocument || w.document;
      }
      return {w,d};
    }catch(e){ return {}; }
  }
  function goBugMemory(){ location.href = BUG_MEMORY_URL(); }
  function patch(){
    const o = deep();
    const d = o.d, w = o.w;
    if(!d || !w) return;
    for(const b of Array.from(d.querySelectorAll('button'))){
      const t = (b.textContent || '').replace(/\s+/g,' ').trim();
      if(t === 'Bug Memory' || t.includes('Bug Memory')){
        b.dataset.pmpBugMemoryFreshRoute = '1';
        b.onclick = function(e){ if(e)e.preventDefault(); goBugMemory(); return false; };
        b.addEventListener('click', function(e){ e.preventDefault(); e.stopImmediatePropagation(); goBugMemory(); }, true);
      }
    }
    const old = typeof w.showSecret === 'function' ? w.showSecret : null;
    if(!w.__pmpBugMemoryFreshRoute){
      w.__pmpBugMemoryFreshRoute = true;
      w.showSecret = function(name){
        if(String(name) === 'Bug Memory'){ goBugMemory(); return false; }
        if(old) return old.apply(this, arguments);
      };
    }
    for(const a of Array.from(d.querySelectorAll('a[href]'))){
      const h = a.getAttribute('href') || '';
      if(h === 'bm.html' || h.includes('private-bug-memory-hub')){
        a.setAttribute('href', BUG_MEMORY_URL());
      }
    }
  }
  window.pmpOpenBugMemory = goBugMemory;
  setTimeout(patch,100);
  setTimeout(patch,500);
  setTimeout(patch,1500);
  setInterval(patch,750);
})();
