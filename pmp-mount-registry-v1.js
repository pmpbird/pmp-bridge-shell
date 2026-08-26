(()=>{
'use strict';
const V='1.7.0-registry-completeness-semantics-20260826A';
const OWNER='pmp-mount-registry-v1';
const K={registry:'pmp_mount_registry_v1',receipt:'pmp_mount_registry_v1_receipt',snapshot:'pmp_mount_registry_live_snapshot_v1',missing:'pmp_mount_registry_missing_expected_v1'};
function list(s){return Array.from(new Set(String(s||'').trim().split(/\s+/).filter(Boolean)))}
const STATIC_CURRENT=list(`
pmp-app-current.html
pmp-current-map-v12.json
pmp-route-guardian-current-loader-v22.html
pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html
pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html
pmp-current-inner-cleanbug-rgcontrols-v23.html
pmp-current-inner-cleanbug-rgcontrols-v4.html
pmp-home-single-v6.html
pmp-runtime-integrity-manifest-v1.json
pmp-integrity-service-worker-v1.js
pmp-app-orchestrator-ownership-registry-v1.json
pmp-service-worker-cache-governor-v1.js
pmp-pass75-reload-runtime-platform-gate-v1.js
pmp-pass75-runtime-platform-v1.js
pmp-safe-area-surface-fill-v1.js
pmp-app-orchestrator-v1.js
pmp-pass8-helper-rules-v1.js
pmp-pass2-atlas-adapter-v2.js
pmp-mount-registry-v1.js
pmp-authority-rules-v1.js
pmp-active-bug-found-contract-v1.js
pmp-bug-watch-passive-capture-v1.js
pmp-safe-writer-current-return-fix-v1.js
pmp-phase8-atlas-marker-v1.js
pmp-pass1r-version-aligner-v1.js
pmp-pass1w-live-proof-reader-v1.js
pmp-active-path-discovery-machine-v1.js
pmp-active-path-discovery-zip-export-v2.js
pmp-continuous-run-bank-order-frame-loader-v1.js
pmp-current-screen-pointer-v1.js
pmp-reload-world-from-map-v1.js
pmp-reload-current-live-update-marker-v1.json
pmp-helper-registry-v1.js
pmp-section-owner-registry-v1.js
pmp-owner-diagnostics-host-v1.js
pmp-owner-diagnostics-foundation-v1.js
pmp-pass7-registry-runtime-probe-v1.js
pmp-universal-growth-awareness-v1.js
pmp-pass7-coverage-lock-v1.js
pmp-pass7-certification-gate-v1.js
pmp-bank-zero-loading-flash-guard-v1.js
pmp-master-bank-tab-v1.js
pmp-bank-mode1-hide-unchecked-v1.js
pmp-bank-screen-owner-v1.js
pmp-continuous-run-level-ui-scope-v1.js
pmp-continuous-run-state-bank-v1.js
pmp-continuous-run-dashboard-stable-v1.js
pmp-master-bank-inventory-router-v1.js
pmp-bank-inventory-readonly-projection-v1.js
pmp-bank-owner-projection-refresh-v1.js
pmp-crd-prestyle-v1.js
pmp-bug-bank-storage-migration-v1.js
pmp-bug-bank-owner-v1.js
pmp-bug-bank-black-row-style-v1.js
pmp-bug-bank-family-view-v1.js
pmp-bug-bank-visual-detectors-v1.js
pmp-bug-bank-current-active-cleaner-v1.js
pmp-bug-bank-legacy-overflow-active-blocker-v1.js
pmp-bug-bank-fix-active-stabilizer-v1.js
pmp-helper-bank-live-inspector-v2.js
pmp-helper-problem-memory-v1.js
pmp-helper-problem-type-seeds-v1.js
pmp-helper-problem-type-only-v1.js
pmp-helper-problem-display-sync-v1.js
pmp-hidden-safe-writer-surface-cleaner-v1.js
pmp-bug-lab-secret-control-owner-v1.js
pmp-mold-to-app-flow-owner-v1.js
pmp-continuous-run-bank-transfer-store-v2.js
pmp-continuous-run-bank-verify-receipt-fix-v1.js
pmp-continuous-run-bank-zip-importer-v1.js
pmp-continuous-run-bank-must-source-zip-v1.js
pmp-bank-scoped-test-data-cleaner-v1.js
pmp-connections-bank-packet-delete-v1.js
pmp-connections-bank-packet-name-v1.js
pmp-connections-bank-inventory-off-v1.js
pmp-connections-copy-output-fix-v1.js
pmp-connections-request-prompt-schema-v1.js
pmp-connections-request-prompt-complete-v1.js
pmp-p15-builder-fix-v2.js
pmp-p15-units-restore-v1.js
pmp-p15-proof-section-v1.js
pmp-p15-continuous-runner-stable-v1.js
pmp-resident-continuous-run-status-reader-v1.js
pmp-resident-cr-status-router-v1.js
pmp-continuous-run-single-line-hold-v1.js
`);
const SUPPORT_REACHABLE=list(`
bug-memory-current-clean-v1.html
code-safety-v13.html
pmp-current-inner-cleanbug-rgcontrols-v2.html
resident.html
code-safety.html
pmp-route-guardian-v1.js
pmp.html
safe-writer.html
safety.html
pmp-bank-project-registry-v1.js
pmp-bank-reload-current-button-v1.js
pmp-continuous-run-bank-stable-status-owner-v1.js
pmp-current-inner-cleanbug-rgcontrols-v3.html
pmp-current-page-code-scope-v1.js
pmp-launcher-reload-current-bridge-v1.js
pmp-layout-guard-v1.js
pmp-level10-random-source-certification-v1.js
pmp-level11-startup-certification-guard-v1.js
pmp-level16-source-bound-startup-enforcement-v1.js
pmp-level18-source-recertification-required-gate-v1.js
pmp-level20-certification-chain-summary-lock-v1.js
pmp-level22-exportable-certification-receipt-v1.js
pmp-level23-export-receipt-integrity-check-v1.js
pmp-level25-receipt-bundle-v1.js
pmp-level26-portable-packet-integrity-check-v1.js
pmp-level28-one-tap-final-export-bundle-v1.js
pmp-level29-cold-start-verification-proof-v1.js
pmp-level30-final-seal-done-lock-v1.js
pmp-phase1-migrate-v1.js
pmp-private-backup-lite-v1.js
pmp-reload-current-visible-receipt-v1.js
pmp-request-packet-guard-v1.js
pmp-service-worker-v1.js
pmp-source-pdf-text-level2c-v1.js
pmp-source-reference-gate-level4-v1.js
pmp-source-text-reader-level3-v1.js
pmp-source-zip-extractor-level2b-v1.js
pmp-source-zip-reader-level2-v1.js
safe-writer-v14.html
bug-lab-mirror-v1.html
bug-lab-mixer-known-types-v1.html
pmp-control-room-cleanup-v1.js
pmp-current-truth-face.js
pmp-lossless-copy-fix.js
pmp-native-contrast-bridge-v2.js
pmp-phase1-source-intake-current-v1.js
pmp-phase2-private-window-adapter-v1.js
pmp-private-claim-controls-v1.js
pmp-private-medium-buttons-v1.js
pmp-private-one-button-pages-v2.js
pmp-private-simple-source-ui-v1.js
pmp-private-source-loader-v1.js
pmp-route-code-map-v1.json
pmp-route-guardian-action-v2.html
pmp-top-lossless-injector.js
pmp-visual-cleanup-v1.js
pmp-lossless-inventory-vault/current.json
pmp-native-contrast-current.json
pmp-phase1-private-window-single-v1.js
pmp-phase10-current-only-freeze-decision-v1.js
pmp-phase2-runtime-verification-v1.js
pmp-phase3-hook-readiness-v1.js
pmp-phase3-hook-validation-execution-v1.js
pmp-phase4-real-app-proof-execution-v1.js
pmp-phase4-real-app-proof-readiness-v1.js
pmp-phase5-current-clean-decision-v1.js
pmp-phase5-current-clean-readiness-v1.js
pmp-phase6-freeze-readiness-v1.js
pmp-phase7-full-transfer-proof-execution-v1.js
pmp-phase7-full-transfer-proof-readiness-v1.js
pmp-phase9-current-only-freeze-readiness-v1.js
pmp-private-field-extractor-v1.js
pmp-route-code-map-adapter-v1.js
pmp-top-lossless-loader.js
`);
const RECOVERY_REACHABLE=list(`
pmp-route-guardian-last-good-clean-v1.js
pmp-current-inner-cleanbug-rgcontrols-v16.html
pmp-route-guardian-last-good-v3-button-v1.js
pmp-route-guardian-last-good-v1.html
pmp-route-guardian-last-good-v18.html
pmp-route-guardian-recovery-tools-v8.html
pmp-move-ledger-candidate-follow-v1.html
pmp-route-guardian-current-loader-v14.html
pmp-current-inner-cleanbug-rgcontrols-v9.html
pmp-current-inner-cleanbug-rgcontrols-v13.html
`);
const HISTORIC=list(`
pmp-current-map-v11.json pmp-current-map-v10.json pmp-current-map-v9.json pmp-current-map.json
pmp-route-guardian-current-loader-v21.html pmp-route-guardian-current-loader-v20.html pmp-route-guardian-current-loader-v19.html pmp-route-guardian-current-loader-v18.html pmp-route-guardian-current-loader-v17.html pmp-route-guardian-current-loader-v15.html
pmp-current-reload-owner-v29.html pmp-current-reload-owner-v29-permanent-update-gate-20260706f.html pmp-current-reload-owner-v29-cachelift-20260706b.html pmp-current-reload-owner-v28.html pmp-current-reload-owner-v27.html
pmp-current-inner-cleanbug-rgcontrols-v29.html pmp-current-inner-cleanbug-rgcontrols-v26.html pmp-current-inner-cleanbug-rgcontrols-v24.html
`);
const INTENTIONAL_OUTSIDE=list(`
GO_TO_SAFETY.html
Index.html
automation/controller/v1/controller-contract.json
automation/engine/v1/engine-policy.json
automation/engine/v1/free-in-app-engine-contract.json
automation/engine/v1/universal-contract.json
automation/plans/packet-01-5.v1.json
automation/state/active-plan.json
automation/state/controller-status.json
automation/state/free-in-app-engine-status.json
automation/state/usage-ledger.json
bm.html
bridge-cloak.html
bug-memory-current-clean-v2.html
bug-memory-hub-link-v1.html
hard-fresh.html
pmp-continuous-run-helper-conflict-blocker-v1.js
pmp-current-inner.html
pmp-helper-bank-live-inspector-v1.js
pmp-helper-symptom-watcher-v1.js
pmp-inventory-eyes-manifest-v1.0.0.json
pmp-p15-helper-tidy-v1.js
`);
const BUCKETS=[
{id:'ACTIVE_CURRENT_APP',rule:'Current v30 live route, protected control-plane runtime, Pass 8 helper rules, and work surface.'},
{id:'SUPPORT_REACHABLE',rule:'Reachable current-tool and support dependencies registered for discovery truth; not boot authority.'},
{id:'RECOVERY_REACHABLE',rule:'Current Map-declared recovery and fallback references; reachable evidence only and never current boot authority.'},
{id:'LIVE_RUNTIME_OBSERVED',rule:'Files currently observed in the running page/frames.'},
{id:'HISTORIC_SUPPORT_ONLY',rule:'Old current-chain files retained for inspection; not boot authority.'},
{id:'INTENTIONAL_OUTSIDE_ACTIVE_ATLAS',rule:'Known reachable references intentionally excluded from active/mount authority. They receive no mount slot and may not become boot, owner, or helper authority merely by being referenced.'}
];
function now(){return new Date().toISOString()}
function T(){try{return top||window}catch(e){return window}}
function put(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function cleanPath(x){x=String(x||'').replace(/&amp;/g,'&').trim().split('#')[0].split('?')[0].replace(/^\.\//,'').replace(/^\//,'');if(/^https?:/i.test(x)||x.includes('://')||x.includes('..'))return'';let m=x.match(/^[a-zA-Z0-9._\/-]+\.(?:html|js|json)$/i);return m?x:''}
function uniq(a){return Array.from(new Set((a||[]).map(cleanPath).filter(Boolean))).sort()}
function docs(root,out,depth){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe,frame')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,out,depth+1)}catch(e){}})}catch(e){}return out}
function liveFiles(){let out=[];docs(T().document).forEach(d=>{try{out.push(cleanPath(String(d.location&&d.location.pathname||'').split('/').pop()));Array.from(d.querySelectorAll('script[src],iframe[src],frame[src],a[href]')).forEach(el=>out.push(cleanPath(el.getAttribute('src')||el.getAttribute('href')||'')))}catch(e){}});return uniq(out)}
function row(path,bucket){return{path,bucket,group:bucket.toLowerCase()}}
function sid(bucket,path){return(bucket+'_'+path).toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'')}
function slot(bucket,path){return{id:sid(bucket,path),bucket,owner:bucket+' File Owner',parent:'active_path_atlas',selectors:[],files:[path],policy:'Atlas record only; no route mutation.'}}
function currentFiles(){return uniq(STATIC_CURRENT.concat(liveFiles()))}
function registry(){
let active=currentFiles(),support=uniq(SUPPORT_REACHABLE),recovery=uniq(RECOVERY_REACHABLE),historic=uniq(HISTORIC),outside=uniq(INTENTIONAL_OUTSIDE),live=liveFiles();
let files=active.map(p=>row(p,'ACTIVE_CURRENT_APP')).concat(support.map(p=>row(p,'SUPPORT_REACHABLE'))).concat(recovery.map(p=>row(p,'RECOVERY_REACHABLE'))).concat(historic.map(p=>row(p,'HISTORIC_SUPPORT_ONLY'))).concat(outside.map(p=>row(p,'INTENTIONAL_OUTSIDE_ACTIVE_ATLAS')));
let classification={ACTIVE_CURRENT_APP:active,SUPPORT_REACHABLE:support,RECOVERY_REACHABLE:recovery,LIVE_RUNTIME_OBSERVED:live,HISTORIC_SUPPORT_ONLY:historic,INTENTIONAL_OUTSIDE_ACTIVE_ATLAS:outside,EXTERNAL_TOOL_SURFACE:[],UNKNOWN_DO_NOT_MOUNT:[]};
return{type:'PMP_ACTIVE_PATH_ATLAS_V1',version:V,owner:OWNER,updated_at:now(),mode:'active_path_registry_only',scope:'v30 current-chain atlas with reachable support, explicit recovery semantics, and known non-authoritative exclusions.',rule:'Passive atlas only. Records current, support, recovery, historic, and intentional-outside reference truth for discovery and App Orchestrator. No route mutation, no Bank rebuild, no storage migration, and no authority is granted by registry presence.',default_for_unlisted_files:'NON_BOOT_OUTSIDE_ACTIVE_ATLAS',atlas_buckets:BUCKETS,repo_file_classification:classification,files,slots:files.filter(f=>f.bucket!=='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS').map(f=>slot(f.bucket,f.path)),storage_owners:[],indexeddb_owners:[],keys:K,active_discovery_merge:{version:'1.2.0-registry-completeness-semantics-20260826A',current_route:'pmp-app-current.html -> route guardian v22 -> map v12 -> reload owner v30 -> current inner v30',active_count:active.length,support_count:support.length,recovery_count:recovery.length,historic_count:historic.length,intentional_outside_count:outside.length,live_runtime_observed_count:live.length}}}
function snapshot(){let r=registry();return{type:'PMP_ACTIVE_PATH_ATLAS_LIVE_SNAPSHOT_V1',version:V,owner:OWNER,at:now(),mode:'active_path_scan_only',atlas_buckets:BUCKETS,repo_file_classification:r.repo_file_classification,documents:[],slot_status:r.slots,storage_keys:[],expected_files:r.files.map(x=>Object.assign({},x,{observed_now:r.repo_file_classification.LIVE_RUNTIME_OBSERVED.indexOf(x.path)>=0,expected_at_boot:x.bucket==='ACTIVE_CURRENT_APP'})),missing_expected:[],indexeddb_owners:[],rule:r.rule}}
function scan(reason){let r=registry(),s=snapshot();put(K.registry,r);put(K.snapshot,s);put(K.missing,s.missing_expected);put(K.receipt,{type:'PMP_ACTIVE_PATH_ATLAS_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'passive_only',slot_count:r.slots.length,active_file_count:r.repo_file_classification.ACTIVE_CURRENT_APP.length,support_file_count:r.repo_file_classification.SUPPORT_REACHABLE.length,recovery_file_count:r.repo_file_classification.RECOVERY_REACHABLE.length,historic_file_count:r.repo_file_classification.HISTORIC_SUPPORT_ONLY.length,intentional_outside_file_count:r.repo_file_classification.INTENTIONAL_OUTSIDE_ACTIVE_ATLAS.length,live_runtime_observed_count:r.repo_file_classification.LIVE_RUNTIME_OBSERVED.length,atlas_file_count:r.files.length,atlas_bucket_count:r.atlas_buckets.length,missing_expected_count:0,current_route:r.active_discovery_merge.current_route,rule:r.rule,side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted'}});return{registry:r,snapshot:s}}
window.PMPMountRegistryV1={version:V,owner:OWNER,mode:'active_path_registry_only',keys:K,registry,scan,snapshot,atlasBuckets:BUCKETS,rule:'v30 current path atlas with reachable support, recovery semantics, and explicit non-authoritative exclusions'};
[0,90,270,630,990,1800,2700,3600,6300,9000,18000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));setInterval(()=>scan('slow_watch_9000'),9000);scan('initial');
})();
