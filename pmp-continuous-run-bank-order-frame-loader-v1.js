(()=>{
'use strict';
const V='1.1.3-pass7-controlled-diagnostics-host-loader';
const SCRIPTS=[
  {id:'pmpBankZeroLoadingFlashGuardV1DirectFrame',src:'pmp-bank-zero-loading-flash-guard-v1.js',fresh:'zero-loading-flash-guard-v100-20260629A'},
  {id:'pmpMasterBankTabV1DirectFrameRefresh142',src:'pmp-master-bank-tab-v1.js',fresh:'master-bank-tab-v142-dedupe-cardize-levels-20260629A'},
  {id:'pmpBankMode1HideUncheckedV1DirectFrameRefresh',src:'pmp-bank-mode1-hide-unchecked-v1.js',fresh:'top-tools-before-level3-order-v430-20260629B'},
  {id:'pmpBankScreenOwnerV1DirectFrame',src:'pmp-bank-screen-owner-v1.js',fresh:'bank-screen-owner-v106-persistent-bank-detail-scan-20260629D'},
  {id:'pmpContinuousRunLevelUIScopeV1DirectFrame',src:'pmp-continuous-run-level-ui-scope-v1.js',fresh:'level-ui-scope-v118-level3plus-containment-guard-20260629E'},
  {id:'pmpSectionOwnerRegistryV1DirectFrame',src:'pmp-section-owner-registry-v1.js',fresh:'pass7-patch1-boundary-audit-key-hardening-20260706B'},
  {id:'pmpOwnerDiagnosticsHostV1DirectFrame',src:'pmp-owner-diagnostics-host-v1.js',fresh:'pass7-controlled-diagnostics-host-20260706A'},
  {id:'pmpOwnerDiagnosticsFoundationV1DirectFrame',src:'pmp-owner-diagnostics-foundation-v1.js',fresh:'pass7-diagnostics-receipt-only-until-hosted-20260706G'},
  {id:'pmpHelperRegistryV1DirectFrame',src:'pmp-helper-registry-v1.js',fresh:'pass7-patch3-passive-helper-registry-20260706A'},
  {id:'pmpUniversalGrowthAwarenessV1DirectFrame',src:'pmp-universal-growth-awareness-v1.js',fresh:'pass7-patch4-universal-growth-awareness-20260706A'},
  {id:'pmpPass7CoverageLockV1DirectFrame',src:'pmp-pass7-coverage-lock-v1.js',fresh:'pass7-patch5-coverage-lock-20260706A'},
  {id:'pmpPass7CertificationGateV1DirectFrame',src:'pmp-pass7-certification-gate-v1.js',fresh:'pass7-patch6-certification-gate-20260706A'}
];
function now(){return new Date().toISOString()}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>10)return a;try{a.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,a,n+1)}catch(e){}})}catch(e){}return a}
function inject(d){if(!d||!d.body)return 0;let made=0;SCRIPTS.forEach(s=>{try{let old=d.getElementById(s.id);if(old)return;let x=d.createElement('script');x.id=s.id;x.src=s.src+'?fresh='+s.fresh+'-'+Date.now();d.body.appendChild(x);made++}catch(e){}});return made}
function scan(){let made=0;docs(document).forEach(d=>{made+=inject(d)});try{localStorage.setItem('pmp_continuous_run_bank_order_frame_loader_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_BANK_ORDER_FRAME_LOADER_V1',version:V,at:now(),scripts:SCRIPTS.map(x=>x.src),new_injections:made,note:'Loads all Pass 7 passive systems. Diagnostics host is created only on Control route; diagnostics stays receipt-only until hosted.',pass7_diagnostics_host:'pmp-owner-diagnostics-host-v1.js creates explicit Control-only host',pass7_patch1:'pmp-section-owner-registry-v1.js loaded as passive proof layer only',pass7_patch2:'pmp-owner-diagnostics-foundation-v1.js loaded as read-only receipt foundation only unless hosted',pass7_patch3:'pmp-helper-registry-v1.js loaded as passive helper truth table only',pass7_patch4:'pmp-universal-growth-awareness-v1.js loaded as passive growth awareness only',pass7_patch5:'pmp-pass7-coverage-lock-v1.js loaded as passive coverage lock only',pass7_patch6:'pmp-pass7-certification-gate-v1.js loaded as passive certification gate only',side_effects:{route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false,diagnostic_repair_attempted:false,helper_takeover_attempted:false,growth_auto_create_attempted:false,coverage_lock_repair_attempted:false,certification_repair_attempted:false,generic_diagnostics_panel_injection_attempted:false}},null,2))}catch(e){}}
window.PMPContinuousRunBankOrderFrameLoaderV1={version:V,scan,pass7_diagnostics_host:'control route only',pass7_patch1:'loads passive section owner registry',pass7_patch2:'loads diagnostics receipt foundation only unless hosted',pass7_patch3:'loads passive helper registry',pass7_patch4:'loads passive universal growth awareness',pass7_patch5:'loads passive coverage lock',pass7_patch6:'loads passive certification gate'};
window.addEventListener('load',()=>[0,25,50,100,200,400,900,1800,3200].forEach(t=>setTimeout(scan,t)));
setInterval(scan,600);
scan();
})();