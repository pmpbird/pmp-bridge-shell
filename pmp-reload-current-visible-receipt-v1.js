(()=>{
  const V='1.0.0-reload-current-visible-receipt';
  const RECEIPT='pmp_reload_current_v1_receipt';
  const TEST='pmp_current_screen_test_engine_v1_last_report';
  const SNAP='pmp_reload_current_live_snapshot_v12_last_kept';
  const UI='data-pmp-reload-current-visible-receipt-v1';
  function T(){try{return top||window}catch(e){return window}}
  function get(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
  function docs(d,a,n){a=a||[];n=n||0;if(!d||n>10)return a;try{a.push(d);d.querySelectorAll('iframe').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
  function text(v){return String(v||'').replace(/\s+/g,' ').trim()}
  function node(d,anchor){try{let n=d.querySelector('['+UI+']');if(n)return n;n=d.createElement('div');n.setAttribute(UI,'1');n.style.cssText='font-size:12px;line-height:1.35;white-space:pre-wrap;margin:6px 0;padding:7px 9px;border:1px solid rgba(0,0,0,.18);border-radius:10px;background:rgba(255,255,255,.62);color:inherit;max-width:100%;overflow-wrap:anywhere';if(anchor&&anchor.parentNode)anchor.insertAdjacentElement('afterend',n);return n}catch(e){return null}}
  function summary(){let r=get(RECEIPT),t=get(TEST),s=get(SNAP),out=[];out.push('Reload Current Receipt');if(r){out.push('Status: '+(r.status||'UNKNOWN'));if(r.pass===true)out.push('Restore: PASS');else if(r.pass===false)out.push('Restore: NEEDS ATTENTION');if(r.page)out.push('Page: '+r.page);if(r.bank_detail)out.push('Bank: '+r.bank_detail);if(r.page_seen!==undefined)out.push('Page seen: '+!!r.page_seen);if(r.bank_seen!==undefined)out.push('Bank seen: '+!!r.bank_seen)}else out.push('Status: no reload receipt yet');let ct=(r&&r.current_screen_test)||null;if(ct){out.push('Current screen test: '+(ct.status||'RECORDED'));if(ct.pass===true)out.push('Current screen pass: true');else if(ct.pass===false)out.push('Current screen pass: false');if(ct.page)out.push('Detected page: '+ct.page);if(typeof ct.hidden_background_elements==='number')out.push('Hidden elements: '+ct.hidden_background_elements);if(typeof ct.script_count==='number')out.push('Loaded scripts: '+ct.script_count)}else if(t){out.push('Current screen test: '+(t.status||'RECORDED'));if(t.current_screen&&t.current_screen.page)out.push('Detected page: '+t.current_screen.page);if(t.code_inventory&&typeof t.code_inventory.script_count==='number')out.push('Loaded scripts: '+t.code_inventory.script_count)}if(s){out.push('Kept snapshot: yes');out.push('Snapshot key: '+SNAP)}else out.push('Kept snapshot: none yet');out.push('Test report key: '+TEST);return out.join('\n')}
  function paint(d){try{let anchors=[...d.querySelectorAll('[data-bank-reload-current-button-v1],button,a')].filter(x=>x.matches('[data-bank-reload-current-button-v1]')||/reload current/i.test(text(x.textContent)));anchors.forEach(a=>{let n=node(d,a);if(n)n.textContent=summary()})}catch(e){}}
  function scan(){docs(T().document).forEach(paint)}
  T().PMPReloadCurrentVisibleReceiptV1={version:V,scan,summary};
  addEventListener('load',()=>[250,900,1800,3500,6500].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,1500);
  scan();
})();
