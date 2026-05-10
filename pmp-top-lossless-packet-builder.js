(() => {
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INVENTORY = 'pmp_app_lossless_inventory_latest_v1';
  const CURRENT = 'pmp-lossless-inventory-vault/current.json';
  const HISTORY = 'pmp-lossless-inventory-vault/history/';
  const SHORTCUT = 'PMP Vault GitHub Writer';
  function read(key) {
    try { return JSON.parse(localStorage.getItem(key) || 'null'); }
    catch (_) { return null; }
  }
  function stamp() { return new Date().toISOString(); }
  function build() {
    const inv = read(EYES) || read(INVENTORY);
    if (!inv) return null;
    const t = stamp();
    return JSON.stringify({
      type: 'PMP_LOSSLESS_VAULT_WRITE_PACKET',
      version: '1.6.0-top-shell-full-modular',
      built_at: t,
      writer_name: 'Vault GitHub Writer',
      shortcut_name: SHORTCUT,
      storage_area: 'PMP Lossless Inventory Vault',
      target_current: CURRENT,
      target_history: HISTORY + t.replace(/[:.]/g, '-') + '.json',
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
      report: {
        type: 'PMP_LOSSLESS_REPORT_WITH_INVENTORY_EYES',
        built_at: t,
        inventory_eyes_captured: true,
        inventory_key: INVENTORY,
        inventory_eyes_key: EYES,
        resident_context_updated: true,
        privacy: 'localStorage key names only; private values not captured. Apple Notes/private Bug Memory not scanned.',
        scan_summary: inv.summary || {},
        truth_boundary: inv.truth_boundary || '',
        inventory_eyes: inv
      }
    }, null, 2);
  }
  window.pmpTopLosslessBuildPacket = build;
  try { window.top.pmpTopLosslessBuildPacket = build; } catch (_) {}
})();
