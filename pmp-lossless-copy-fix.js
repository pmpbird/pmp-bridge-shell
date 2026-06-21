(() => {
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INVENTORY = 'pmp_app_lossless_inventory_latest_v1';
  const LAST_SAVE = 'pmp_last_save_to_github_vault_press_v1';
  const SHORTCUT = 'PMP Vault GitHub Writer';
  const SHORTCUT_URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT);
  const VAULT_CURRENT = 'pmp-lossless-inventory-vault/current.json';
  const VAULT_HISTORY = 'pmp-lossless-inventory-vault/history/';
  function read(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (_) { return null; } }
  function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}}
  function now() { return new Date().toISOString(); }
  function deep() {
    try {
      let iframe = document.getElementById('app');
      let win = iframe && iframe.contentWindow;
      let doc = win && (iframe.contentDocument || win.document);
      for (let i = 0; i < 10; i++) {
        const nested = doc && doc.getElementById && doc.getElementById('app');
        if (!nested) break;
        win = nested.contentWindow;
        doc = nested.contentDocument || win.document;
      }
      return { win, doc };
    } catch (_) { return {}; }
  }
  function status(msg) {
    const d = deep().doc;
    if (!d) return;
    const c = d.getElementById('controlStatus');
    const r = d.getElementById('residentReply');
    if (c) c.textContent = msg;
    if (r) r.textContent = msg;
  }
  function packetText() {
    const inv = read(EYES) || read(INVENTORY);
    if (!inv) return null;
    const stamp = now();
    const report = {
      type: 'PMP_LOSSLESS_REPORT_WITH_INVENTORY_EYES',
      built_at: stamp,
      inventory_eyes_captured: true,
      inventory_key: INVENTORY,
      inventory_eyes_key: EYES,
      privacy: 'localStorage key names only; private values not captured. Apple Notes/private Bug Memory not scanned.',
      scan_summary: inv.summary || {},
      truth_boundary: inv.truth_boundary || '',
      inventory_eyes: inv
    };
    return JSON.stringify({
      type: 'PMP_LOSSLESS_VAULT_WRITE_PACKET',
      version: '1.5.0-record-save-press-time',
      built_at: stamp,
      writer_name: 'Vault GitHub Writer',
      shortcut_name: SHORTCUT,
      storage_area: 'PMP Lossless Inventory Vault',
      target_current: VAULT_CURRENT,
      target_history: VAULT_HISTORY + stamp.replace(/[:.]/g, '-') + '.json',
      write_instruction: 'Shortcut reads this packet from clipboard and posts packet/report to the GitHub Issue Inbox. Do not write private Bug Memory or private values.',
      privacy_gate: {
        private_bug_memory: false,
        apple_notes_contents: false,
        tokens: false,
        passwords: false,
        secrets: false,
        private_values: false,
        localStorage_key_names_only: true
      },
      report
    }, null, 2);
  }
  function fallbackCopy(txt) {
    try {
      const ta = document.createElement('textarea');
      ta.value = txt;
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
  function openShortcutNow() {
    try { window.top.location.href = SHORTCUT_URL; return true; } catch (_) {}
    try { window.parent.location.href = SHORTCUT_URL; return true; } catch (_) {}
    try { location.href = SHORTCUT_URL; return true; } catch (_) {}
    return false;
  }
  function copyAndOpen() {
    const txt = packetText();
    if (!txt) { status('No full report found. Run Improve Lossless Quality first.'); return false; }
    const press = now();
    let built = null;
    try{built = JSON.parse(txt).built_at || null}catch(_){built=null}
    save(LAST_SAVE,{pressed_at:press,packet_built_at:built,source:'Save to GitHub Vault',shortcut_name:SHORTCUT});
    fallbackCopy(txt);
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).catch(()=>{});
    status('Copied Vault Write Packet. Opening PMP Vault GitHub Writer Shortcut.');
    openShortcutNow();
    return true;
  }
  function patch() {
    const o = deep();
    const d = o.doc, w = o.win;
    if (!d || !w) return;
    w.copyCurrent = copyAndOpen;
    w.copyLosslessReport = copyAndOpen;
    for (const b of Array.from(d.querySelectorAll('button'))) {
      const t = (b.textContent || '').replace(/\s+/g, ' ').trim();
      if (/Copy Lossless Report|Copy Current|Copy Green Box/i.test(t) && !b.dataset.losslessDirectTapOpen) {
        b.dataset.losslessDirectTapOpen = '1';
        b.addEventListener('click', e => {
          e.preventDefault();
          e.stopImmediatePropagation();
          copyAndOpen();
        }, true);
      }
    }
  }
  setInterval(patch, 500);
  setTimeout(patch, 300);
  window.pmpLosslessCopyFix = copyAndOpen;
})();
