export default {
  async fetch(request, env) {
    const allowedOrigins = [
      'https://pmpbird.github.io',
      'https://pmpbird.github.io/pmp-bridge-shell'
    ];

    const origin = request.headers.get('Origin') || '';
    const allowOrigin = origin && origin.startsWith('https://pmpbird.github.io')
      ? origin
      : 'https://pmpbird.github.io';

    const corsHeaders = {
      'Access-Control-Allow-Origin': allowOrigin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-PMP-Vault-Writer-Key',
      'Access-Control-Max-Age': '86400'
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    const url = new URL(request.url);
    if (url.pathname !== '/vault/write') {
      return json({ ok: false, error: 'NOT_FOUND', expected_path: '/vault/write' }, 404, corsHeaders);
    }

    if (request.method !== 'POST') {
      return json({ ok: false, error: 'METHOD_NOT_ALLOWED' }, 405, corsHeaders);
    }

    if (!env.GITHUB_TOKEN || !env.VAULT_WRITE_KEY) {
      return json({ ok: false, error: 'WORKER_NOT_CONFIGURED', missing: ['GITHUB_TOKEN or VAULT_WRITE_KEY'] }, 500, corsHeaders);
    }

    const suppliedKey = request.headers.get('X-PMP-Vault-Writer-Key') || '';
    if (suppliedKey !== env.VAULT_WRITE_KEY) {
      return json({ ok: false, error: 'UNAUTHORIZED' }, 401, corsHeaders);
    }

    let packet;
    try {
      packet = await request.json();
    } catch (error) {
      return json({ ok: false, error: 'BAD_JSON', detail: String(error && error.message || error) }, 400, corsHeaders);
    }

    const validation = validatePacket(packet);
    if (!validation.ok) {
      return json({ ok: false, error: 'PACKET_VALIDATION_FAILED', reasons: validation.reasons }, 400, corsHeaders);
    }

    const repoOwner = env.GITHUB_OWNER || 'pmpbird';
    const repoName = env.GITHUB_REPO || 'pmp-bridge-shell';
    const branch = env.GITHUB_BRANCH || 'main';
    const currentPath = 'pmp-lossless-inventory-vault/current.json';
    const historyPath = sanitizeHistoryPath(packet.target_history);
    const reportText = JSON.stringify(packet.report, null, 2) + '\n';

    const currentWrite = await putGitHubFile({
      token: env.GITHUB_TOKEN,
      owner: repoOwner,
      repo: repoName,
      path: currentPath,
      branch,
      content: reportText,
      message: 'Vault GitHub Writer: update current lossless inventory report'
    });

    let historyWrite = null;
    if (historyPath) {
      historyWrite = await putGitHubFile({
        token: env.GITHUB_TOKEN,
        owner: repoOwner,
        repo: repoName,
        path: historyPath,
        branch,
        content: reportText,
        message: 'Vault GitHub Writer: add lossless inventory report history'
      });
    }

    return json({
      ok: true,
      type: 'PMP_VAULT_GITHUB_WRITER_RECEIPT',
      writer_name: 'Vault GitHub Writer',
      built_at: new Date().toISOString(),
      current_report: currentPath,
      current_commit: currentWrite.commit_sha || null,
      history_report: historyPath,
      history_commit: historyWrite && historyWrite.commit_sha || null,
      privacy_gate_passed: true,
      report_type: packet.report && packet.report.type,
      report_built_at: packet.report && packet.report.built_at,
      scan_summary: packet.report && packet.report.scan_summary || null
    }, 200, corsHeaders);
  }
};

function validatePacket(packet) {
  const reasons = [];
  if (!packet || typeof packet !== 'object') reasons.push('packet is not an object');
  if (packet && packet.type !== 'PMP_LOSSLESS_VAULT_WRITE_PACKET') reasons.push('wrong packet.type');
  if (packet && packet.writer_name !== 'Vault GitHub Writer') reasons.push('wrong writer_name');
  if (packet && packet.storage_area !== 'PMP Lossless Inventory Vault') reasons.push('wrong storage_area');
  if (packet && packet.target_current !== 'pmp-lossless-inventory-vault/current.json') reasons.push('wrong target_current');
  if (packet && packet.target_history && !String(packet.target_history).startsWith('pmp-lossless-inventory-vault/history/')) reasons.push('bad target_history folder');

  const gate = packet && packet.privacy_gate;
  if (!gate || typeof gate !== 'object') reasons.push('missing privacy_gate');
  if (gate) {
    if (gate.private_bug_memory !== false) reasons.push('privacy_gate.private_bug_memory must be false');
    if (gate.apple_notes_contents !== false) reasons.push('privacy_gate.apple_notes_contents must be false');
    if (gate.tokens !== false) reasons.push('privacy_gate.tokens must be false');
    if (gate.passwords !== false) reasons.push('privacy_gate.passwords must be false');
    if (gate.secrets !== false) reasons.push('privacy_gate.secrets must be false');
    if (gate.private_values !== false) reasons.push('privacy_gate.private_values must be false');
    if (gate.localStorage_key_names_only !== true) reasons.push('privacy_gate.localStorage_key_names_only must be true');
  }

  const report = packet && packet.report;
  if (!report || typeof report !== 'object') reasons.push('missing report');
  if (report && report.type !== 'PMP_LOSSLESS_REPORT_WITH_INVENTORY_EYES') reasons.push('wrong report.type');
  if (report && containsForbiddenPrivateShapes(report)) reasons.push('report contains forbidden private-looking value shapes');

  return { ok: reasons.length === 0, reasons };
}

function containsForbiddenPrivateShapes(value, path = '') {
  if (!value || typeof value !== 'object') return false;
  if (Array.isArray(value)) {
    return value.some((item, index) => containsForbiddenPrivateShapes(item, `${path}[${index}]`));
  }

  for (const [key, child] of Object.entries(value)) {
    const lower = key.toLowerCase();
    const childPath = path ? `${path}.${key}` : key;

    if (/token|password|secret|private_value|privatevalue/.test(lower)) {
      const allowedPrivacyGate = childPath.startsWith('privacy_gate') || childPath.includes('privacy');
      if (!allowedPrivacyGate && child !== false && child !== null && child !== '') return true;
    }

    if (lower === 'value_captured' && child !== false) return true;
    if (lower === 'value' && /local_storage|localstorage|bug_memory|apple_notes|secret|token|password/i.test(childPath)) return true;
    if (containsForbiddenPrivateShapes(child, childPath)) return true;
  }
  return false;
}

function sanitizeHistoryPath(path) {
  if (!path) return null;
  const clean = String(path).replace(/^\/+/, '');
  if (!clean.startsWith('pmp-lossless-inventory-vault/history/')) return null;
  if (!clean.endsWith('.json')) return null;
  if (clean.includes('..')) return null;
  return clean;
}

async function putGitHubFile({ token, owner, repo, path, branch, content, message }) {
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponentPath(path)}`;
  const existing = await fetch(`${apiUrl}?ref=${encodeURIComponent(branch)}`, {
    headers: githubHeaders(token)
  });

  let sha = undefined;
  if (existing.ok) {
    const data = await existing.json();
    sha = data.sha;
  } else if (existing.status !== 404) {
    const detail = await safeText(existing);
    throw new Error(`GitHub lookup failed for ${path}: ${existing.status} ${detail}`);
  }

  const body = {
    message,
    content: base64EncodeUtf8(content),
    branch
  };
  if (sha) body.sha = sha;

  const put = await fetch(apiUrl, {
    method: 'PUT',
    headers: githubHeaders(token),
    body: JSON.stringify(body)
  });

  if (!put.ok) {
    const detail = await safeText(put);
    throw new Error(`GitHub write failed for ${path}: ${put.status} ${detail}`);
  }

  const result = await put.json();
  return {
    path,
    commit_sha: result.commit && result.commit.sha || null,
    content_sha: result.content && result.content.sha || null
  };
}

function githubHeaders(token) {
  return {
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'PMP-Vault-GitHub-Writer'
  };
}

function encodeURIComponentPath(path) {
  return String(path).split('/').map(encodeURIComponent).join('/');
}

function base64EncodeUtf8(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

async function safeText(response) {
  try { return await response.text(); } catch (_) { return ''; }
}

function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...extraHeaders
    }
  });
}
