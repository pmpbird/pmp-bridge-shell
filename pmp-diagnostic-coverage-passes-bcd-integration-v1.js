(()=>{
'use strict';
const V='1.0.0-passes-bcd-integration-20260730A';
function T(){try{return window.top||window}catch(_){return window}}
function install(){const unified=T().PMPDiagnosticCoveragePassAIntegrationV1||window.PMPDiagnosticCoveragePassAIntegrationV1;return !!(unified&&typeof unified.install==='function'&&unified.install())}
window.PMPDiagnosticCoveragePassesBCDIntegrationV1={version:V,install,rule:'Compatibility shim only. All Pass A–D evidence and Whole App Health presentation are integrated by the single diagnostics renderer. No additional API or DOM wrapper is installed.'};
try{T().PMPDiagnosticCoveragePassesBCDIntegrationV1=window.PMPDiagnosticCoveragePassesBCDIntegrationV1}catch(_){}
})();