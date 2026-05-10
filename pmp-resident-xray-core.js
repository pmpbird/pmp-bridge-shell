(() => {
  const XRAY_KEY = 'pmp_resident_xray_context_v1';
  const XRAY_HISTORY_KEY = 'pmp_resident_xray_history_v1';
  const XRAY_RULE_KEY = 'pmp_resident_xray_rule_v1';
  const INVENTORY_EYES_KEY = 'pmp_inventory_eyes_latest_v1';
  const MANIFEST_PATH = 'pmp-inventory-eyes-manifest-v1.0.0.json';
  const VAULT_CURRENT_PATH = 'pmp-lossless-inventory-vault/current.json';
  const CURRENT_MAP_PATH = 'pmp-current-map.json';

  function now() { return new Date().toISOString(); }
  function shortText(value, limit = 220) {
    return String(value || '').replace(/\s+/g, ' ').trim().slice(0, limit);
  }
  function safeJsonRead(key, fallback = null) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (_) { return fallback; }
  }
  function safeJsonWrite(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) {}
  }
  function storageKeyMap() {
    try {
      return Object.keys(localStorage).sort().map(key => ({
        key,
        classification: /bug|private|token|pass|secret|memory|notes/i.test(key) ? 'private_or_sensitive_key_name_only' : 'public_safe_key_name_only',
        value_captured: false
      }));
    } catch (_) { return []; }
  }
  function findInner() {
    try {
      let iframe = document.getElementById('app');
      let win = iframe && iframe.contentWindow;
      let doc = win && (iframe.contentDocument || win.document);
      for (let i = 0; i < 8; i++) {
        const nested = doc && doc.getElementById && doc.getElementById('app');
        if (!nested) break;
        win = nested.contentWindow;
        doc = nested.contentDocument || win.document;
      }
      return { win, doc };
    } catch (error) {
      return { error: String(error && error.message || error) };
    }
  }
  function nodeSummary(el, index) {
    const rect = (() => { try { return el.getBoundingClientRect(); } catch (_) { return null; } })();
    return {
      index,
      tag: (el.tagName || '').toLowerCase(),
      id: el.id || null,
      class_name: String(el.className || '').slice(0, 180),
      text: shortText(el.innerText || el.textContent || el.value || el.getAttribute('aria-label') || '', 260),
      href: el.getAttribute && el.getAttribute('href') || null,
      onclick: el.getAttribute && shortText(el.getAttribute('onclick') || '', 220) || null,
      type: el.getAttribute && el.getAttribute('type') || null,
      name: el.getAttribute && el.getAttribute('name') || null,
      placeholder: el.getAttribute && el.getAttribute('placeholder') || null,
      visible: !!(rect && rect.width >= 0 && rect.height >= 0 && el.offsetParent !== null),
      rect: rect ? { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) } : null
    };
  }
  function collectDom(doc) {
    if (!doc || !doc.querySelectorAll) return { error: 'no_document_available' };
    const all = Array.from(doc.querySelectorAll('*'));
    const interactiveSelector = 'button,a[href],input,textarea,select,[onclick],[role="button"],[tabindex]';
    const interactive = Array.from(doc.querySelectorAll(interactiveSelector)).map(nodeSummary);
    const screens = Array.from(doc.querySelectorAll('.screen,[data-screen],section')).map((el, index) => ({
      index,
      id: el.id || null,
      class_name: String(el.className || '').slice(0, 180),
      active: String(el.className || '').split(/\s+/).includes('on') || el.getAttribute('aria-current') === 'true',
      visible: el.offsetParent !== null,
      heading: shortText((el.querySelector('h1,h2,h3') || {}).textContent || '', 160),
      text_sample: shortText(el.innerText || el.textContent || '', 500)
    }));
    const visibleText = shortText(doc.body && doc.body.innerText || '', 2500);
    return {
      title: doc.title || '',
      location_hash: location.hash || '',
      total_nodes: all.length,
      screens,
      interactive_count: interactive.length,
      interactive,
      forms: {
        inputs: Array.from(doc.querySelectorAll('input')).map(nodeSummary),
        textareas: Array.from(doc.querySelectorAll('textarea')).map(nodeSummary),
        selects: Array.from(doc.querySelectorAll('select')).map(nodeSummary)
      },
      structural_counts: {
        cards: doc.querySelectorAll('.card').length,
        panels: doc.querySelectorAll('.panel,.dock').length,
        notes: doc.querySelectorAll('.note,.warn,.reply,.statusbar').length,
        drawers: doc.querySelectorAll('.drawer').length,
        tabs: doc.querySelectorAll('.tabs,.tab').length,
        links: doc.querySelectorAll('a[href]').length,
        buttons: doc.querySelectorAll('button').length
      },
      visible_text_sample: visibleText
    };
  }
  async function fetchJson(path) {
    try {
      const res = await fetch(path + '?fresh=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) throw new Error(String(res.status));
      return await res.json();
    } catch (error) {
      return { unavailable: true, path, error: String(error && error.message || error) };
    }
  }
  function manifestSummary(manifest) {
    const paths = Array.isArray(manifest && manifest.paths) ? manifest.paths : [];
    const rules = manifest && manifest.classification_rules || {};
    const active = new Set(rules.current_active || []);
    const helper = new Set(rules.helper_not_user_facing || []);
    const archive = new Set(rules.likely_archive_or_test || []);
    return {
      path: MANIFEST_PATH,
      available: !manifest.unavailable,
      manifest_type: manifest.type || null,
      manifest_version: manifest.version || null,
      path_count: paths.length,
      active_count: paths.filter(p => active.has(p)).length,
      helper_count: paths.filter(p => helper.has(p)).length,
      archive_or_test_count: paths.filter(p => archive.has(p)).length,
      paths: paths.map(path => ({
        path,
        status: active.has(path) ? 'active_current' : helper.has(path) ? 'helper_not_user_facing' : archive.has(path) ? 'archive_or_test' : 'known_inventory_path'
      }))
    };
  }
  function routeFindings(dom, manifest) {
    const paths = new Set((manifest && manifest.paths) || []);
    const links = (((dom || {}).interactive) || []).filter(x => x.href);
    return links.map(link => {
      const href = String(link.href || '').split('#')[0].split('?')[0];
      const external = /^https?:|^mailto:|^tel:|^shortcuts:/i.test(href);
      const localHtml = /\.html$/i.test(href);
      return {
        text: link.text,
        href: link.href,
        route_kind: external ? 'external_or_scheme' : localHtml ? 'local_html' : href ? 'local_or_hash' : 'empty',
        manifest_known: localHtml ? paths.has(href) : null,
        possible_missing_local_file: localHtml ? !paths.has(href) : false
      };
    });
  }
  async function buildXRay(trigger = 'background') {
    const inner = findInner();
    const dom = collectDom(inner.doc);
    const manifest = await fetchJson(MANIFEST_PATH);
    const currentMap = await fetchJson(CURRENT_MAP_PATH);
    const vaultCurrent = await fetchJson(VAULT_CURRENT_PATH);
    const manifestView = manifestSummary(manifest);
    const inventoryEyesLatest = safeJsonRead(INVENTORY_EYES_KEY, null);
    const context = {
      type: 'PMP_RESIDENT_HIDDEN_XRAY_CONTEXT',
      version: '1.0.0-hidden-resident-core',
      built_at: now(),
      trigger,
      purpose: 'Hidden behind-the-scenes app awareness for Resident during normal conversation.',
      mode: 'safe_observable_app_map',
      scope_rule: 'Dynamically inspect every safe browser-observable part of the app instead of relying on a fixed hand-written list.',
      privacy_boundary: {
        captures_app_structure: true,
        captures_storage_key_names_only: true,
        captures_private_values: false,
        captures_apple_notes_contents: false,
        captures_tokens_passwords_secrets: false
      },
      inventory_boundary: {
        inventory_eyes_key: INVENTORY_EYES_KEY,
        inventory_eyes_preserved: true,
        resident_xray_key: XRAY_KEY,
        rule: 'Resident X-Ray is separate from Inventory Eyes. Lossless Quality still owns vault-grade Inventory Eyes reports.'
      },
      current_app_map: currentMap,
      live_app: dom,
      manifest_inventory: manifestView,
      route_findings: routeFindings(dom, manifestView),
      storage_keys: storageKeyMap(),
      vault_current_summary: vaultCurrent && !vaultCurrent.unavailable ? {
        type: vaultCurrent.type || null,
        status: vaultCurrent.status || null,
        current_record_id: vaultCurrent.current_record_id || null,
        scan_summary: vaultCurrent.scan_summary || null
      } : vaultCurrent,
      inventory_eyes_latest_summary: inventoryEyesLatest ? {
        available: true,
        type: inventoryEyesLatest.type || null,
        version: inventoryEyesLatest.version || null,
        built_at: inventoryEyesLatest.built_at || null,
        summary: inventoryEyesLatest.summary || null
      } : { available: false },
      resident_readiness: {
        xray_available: true,
        resident_can_use_context_key: XRAY_KEY,
        normal_conversation_should_use_xray: true
      }
    };
    safeJsonWrite(XRAY_KEY, context);
    safeJsonWrite(XRAY_RULE_KEY, {
      type: 'PMP_RESIDENT_XRAY_RULE',
      version: '1.0.0',
      updated_at: context.built_at,
      rule: 'Resident should use hidden X-Ray context automatically during normal conversation. Do not make the user operate an X-Ray dashboard unless they ask.',
      inventory_boundary: context.inventory_boundary
    });
    const history = safeJsonRead(XRAY_HISTORY_KEY, []);
    if (Array.isArray(history)) {
      history.push({ built_at: context.built_at, trigger, total_nodes: dom.total_nodes || null, interactive_count: dom.interactive_count || null, manifest_paths: manifestView.path_count || null });
      safeJsonWrite(XRAY_HISTORY_KEY, history.slice(-20));
    }
    return context;
  }
  function patchResident() {
    const inner = findInner();
    const win = inner.win, doc = inner.doc;
    if (!win || !doc || win.__pmpResidentXRayCorePatched) return;
    win.__pmpResidentXRayCorePatched = true;
    const oldRun = typeof win.residentRun === 'function' ? win.residentRun : null;
    win.residentRun = function patchedResidentRun() {
      buildXRay('resident_run_before_answer');
      if (oldRun) return oldRun.apply(this, arguments);
      const reply = doc.getElementById('residentReply');
      if (reply) reply.textContent = 'Resident X-Ray context refreshed.';
    };
  }
  function start() {
    buildXRay('initial_load');
    patchResident();
    setInterval(() => buildXRay('background_refresh'), 15000);
    setInterval(patchResident, 2000);
    window.pmpResidentXRayRefresh = () => buildXRay('manual_refresh');
    window.pmpResidentXRayRead = () => safeJsonRead(XRAY_KEY, null);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
