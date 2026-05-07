export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const json = (body, status = 200) => new Response(JSON.stringify(body, null, 2), {
      status,
      headers: { "content-type": "application/json; charset=utf-8", ...cors }
    });

    const store = env && env.PMP_STORE;
    async function getStored(key, fallback) {
      if (!store) return fallback;
      const raw = await store.get(key);
      if (!raw) return fallback;
      try { return JSON.parse(raw); } catch { return fallback; }
    }
    async function setStored(key, value) {
      if (!store) return false;
      await store.put(key, JSON.stringify(value));
      return true;
    }

    const defaultPointer = {
      type: "PMP_BACKEND_LATEST_POINTER",
      latest: "pmp-clean-v21.html",
      last_good: "pmp-clean-v21.html",
      health_required: true,
      fallback_enabled: true,
      blocked_detours: ["safe-writer"],
      updated_at: new Date().toISOString(),
      backend_storage: !!store
    };

    if (path === "/" || path === "/api") {
      return json({
        type: "PMP_BACKEND_STATUS",
        status: "ok",
        backend: "Cloudflare Worker compatible",
        storage_bound: !!store,
        endpoints: [
          "GET /api/latest",
          "POST /api/latest",
          "POST /api/truth",
          "GET /api/truth/latest",
          "GET /api/code-safety",
          "POST /api/code-safety",
          "POST /api/resident-learning",
          "GET /api/resident-learning/latest"
        ],
        safe_boundary: "Backend supports update truth and memory. It does not make material official PMP automatically."
      });
    }

    if (path === "/api/latest" && request.method === "GET") {
      const pointer = await getStored("latest_pointer", defaultPointer);
      return json(pointer);
    }

    if (path === "/api/latest" && request.method === "POST") {
      const body = await request.json().catch(() => null);
      if (!body || !body.latest) return json({ error: "latest is required" }, 400);
      const old = await getStored("latest_pointer", defaultPointer);
      const next = {
        ...old,
        ...body,
        type: "PMP_BACKEND_LATEST_POINTER",
        updated_at: new Date().toISOString(),
        backend_storage: !!store
      };
      const persisted = await setStored("latest_pointer", next);
      return json({ status: persisted ? "saved" : "accepted_not_persisted_no_store_binding", pointer: next });
    }

    if (path === "/api/truth" && request.method === "POST") {
      const body = await request.json().catch(() => null);
      if (!body) return json({ error: "valid JSON body required" }, 400);
      const entry = { type: "PMP_BACKEND_TRUTH_ENTRY", received_at: new Date().toISOString(), report: body };
      const persisted = await setStored("truth_latest", entry);
      return json({ status: persisted ? "saved" : "accepted_not_persisted_no_store_binding", entry });
    }

    if (path === "/api/truth/latest" && request.method === "GET") {
      const entry = await getStored("truth_latest", { type: "PMP_BACKEND_TRUTH_ENTRY", status: "none_saved_yet" });
      return json(entry);
    }

    if (path === "/api/code-safety" && request.method === "GET") {
      const safety = await getStored("code_safety", {
        type: "PMP_BACKEND_CODE_SAFETY_STATUS",
        state: "UNKNOWN_LOCAL_ONLY",
        last_good: "pmp-clean-v21.html",
        latest_allowed: true,
        reason: "No backend code-safety status saved yet. Launcher should still use local health checks."
      });
      return json(safety);
    }

    if (path === "/api/code-safety" && request.method === "POST") {
      const body = await request.json().catch(() => null);
      if (!body) return json({ error: "valid JSON body required" }, 400);
      const status = { type: "PMP_BACKEND_CODE_SAFETY_STATUS", updated_at: new Date().toISOString(), ...body };
      const persisted = await setStored("code_safety", status);
      return json({ status: persisted ? "saved" : "accepted_not_persisted_no_store_binding", code_safety: status });
    }

    if (path === "/api/resident-learning" && request.method === "POST") {
      const body = await request.json().catch(() => null);
      if (!body) return json({ error: "valid JSON body required" }, 400);
      const entry = { type: "PMP_BACKEND_RESIDENT_LEARNING_ENTRY", received_at: new Date().toISOString(), learning: body, official: false };
      const persisted = await setStored("resident_learning_latest", entry);
      return json({ status: persisted ? "saved" : "accepted_not_persisted_no_store_binding", entry });
    }

    if (path === "/api/resident-learning/latest" && request.method === "GET") {
      const entry = await getStored("resident_learning_latest", { type: "PMP_BACKEND_RESIDENT_LEARNING_ENTRY", status: "none_saved_yet" });
      return json(entry);
    }

    return json({ error: "not_found", path }, 404);
  }
};
