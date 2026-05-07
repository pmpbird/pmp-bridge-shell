window.PMPBackend = (() => {
  const DEFAULTS = {
    enabled: false,
    base_url: "",
    fallback_to_local: true
  };
  const CONFIG_KEY = "pmp_backend_config_v1";
  function readConfig() {
    try { return { ...DEFAULTS, ...(JSON.parse(localStorage.getItem(CONFIG_KEY) || "{}")) }; }
    catch { return { ...DEFAULTS }; }
  }
  function saveConfig(config) {
    localStorage.setItem(CONFIG_KEY, JSON.stringify({ ...readConfig(), ...config }));
    return readConfig();
  }
  async function request(path, options = {}) {
    const config = readConfig();
    if (!config.enabled || !config.base_url) throw new Error("PMP backend is not enabled yet.");
    const res = await fetch(config.base_url.replace(/\/$/, "") + path, {
      ...options,
      headers: { "content-type": "application/json", ...(options.headers || {}) }
    });
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { raw: text }; }
    if (!res.ok) throw new Error(json.error || res.statusText || "Backend request failed");
    return json;
  }
  async function getLatest(localFallback) {
    try { return await request("/api/latest"); }
    catch (e) {
      if (localFallback) return localFallback;
      throw e;
    }
  }
  async function postTruth(report) {
    return request("/api/truth", { method: "POST", body: JSON.stringify(report) });
  }
  async function getCodeSafety(localFallback) {
    try { return await request("/api/code-safety"); }
    catch (e) {
      if (localFallback) return localFallback;
      throw e;
    }
  }
  async function postResidentLearning(entry) {
    return request("/api/resident-learning", { method: "POST", body: JSON.stringify(entry) });
  }
  return { readConfig, saveConfig, request, getLatest, postTruth, getCodeSafety, postResidentLearning };
})();
