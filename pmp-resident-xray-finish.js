(() => {
  function run() {
    try {
      if (window.pmpResidentXRayRefresh) window.pmpResidentXRayRefresh();
      window.PMP_RESIDENT_XRAY_READY = true;
      window.PMP_RESIDENT_XRAY_READY_AT = new Date().toISOString();
    } catch (_) {}
  }
  setTimeout(run, 1200);
  setInterval(run, 12000);
})();
