(()=>{
'use strict';
const VERSION='1.0.9-v30-current-chain-atlas-aligned-20260709A';
const REPORT_KEY='pmp_active_path_discovery_report_v1';
const RECEIPT_KEY='pmp_active_path_discovery_receipt_v1';
const COPY_RECEIPT_KEY='pmp_active_path_discovery_copy_receipt_v1';
function list(s){return Array.from(new Set(String(s||'').trim().split(/\s+/).filter(Boolean)))}
const CURRENT_BOOT_ROOT=list(`
pmp-app-current.html
pmp-current-map-v12.json
pmp-route-guardian-current-loader-v22.html
pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html
pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html
pmp-current-inner-cleanbug-rgcontrols-v23.html
pmp-home-single-v6.html
`);
const HISTORIC_CURRENT_REFERENCES=list(`
pmp-current-map-v11.json
pmp-current-map-v10.json
pmp-current-map-v9.json
pmp-current-map.json
pmp-route-guardian-current-loader-v15.html
pmp-route-guardian-current-loader-v17.html
pmp-route-guardian-current-loader-v18.html
pmp-route-guardian-current-loader-v19.html
pmp-route-guardian-current-loader-v20.html
pmp-route-guardian-current-loader-v21.html
pmp-current-reload-owner-v27.html
pmp-current-reload-owner-v28.html
pmp-current-reload-owner-v29.html
pmp-current-reload-owner-v29-permanent-update-gate-20260706f.html
pmp-current-inner-cleanbug-rgcontrols-v24.html
pmp-current-inner-cleanbug-rgcontrols-v26.html
pmp-current-inner-cleanbug-rgcontrols-v29.html
`);
const MAX=260;
let LAST=null;
function topWin(){try{return top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function cleanPath(x){x=String(x||'').replace(/&amp;/g,'&').trim().split('#')[0].split('?')[0].replace(/^\.\//,'').replace(/^\//,'');if(/^https?:/i.test(x)||x.includes('://')||x.includes('..'))return'';let m=x.match(/^[a-zA-Z0-9._\/-]+\.(?:html|js|json)$/i);return m?x:''}
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean))).sort()}
function eachDoc(fn){let seen=[];function walk(w,n){if(!w||n>12||seen.includes(w))return;seen.push(w);try{if(w.document)fn(w.document,w);Array.from(w.document.querySelectorAll('iframe,frame')).forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}walk(window,0);try{walk(topWin(),0)}catch(e){}}
function liveFiles(){let out=[];eachDoc((d,w)=>{try{out.push(cleanPath(String(w.location&&w.location.pathname||'').split('/').pop()));Array.from(d.querySelectorAll('script[src],iframe[src],frame[src],a[href]')).forEach(el=>out.push(cleanPath(el.getAttribute('src')||el.getAttribute('href')||'')))}catch(e){}});return uniq(out)}
function atlasPaths(){let r=null;try{if(window.PMPMountRegistryV1&&typeof window.PMPMountRegistryV1.registry==='function')r=window.PMPMountRegistryV1.registry()}catch(e){}if(!r){try{let tw=topWin();if(tw.PMPMountRegistryV1&&typeof tw.PMPMountRegistryV1.registry==='function')r=tw.PMPMountRegistryV1.registry()}catch(e){}}
if(!r){try{r=JSON.parse(localStorage.getItem('pmp_mount_registry_v1')||'null')}catch(e){}}
if(!r){try{r=JSON.parse(topWin().localStorage.getItem('pmp_mount_registry_v1')||'null')}catch(e){}}
let files=[];if(r&&Array.isArray(r.files))files=files.concat(r.files.map(f=>f&&f.path).filter(Boolean));if(r&&r.repo_file_classification){Object.keys(r.repo_file_classification).forEach(k=>{let a=r.repo_file_classification[k];if(Array.isArray(a))files=files.concat(a)})}
return uniq(files.map(cleanPath))}
function extract(text){let out=[];String(text||'').replace(/['"`(=\s]([a-zA-Z0-9._\/-]+\.(?:html|js|json))(?=$|[?#'"`\s)>,;])/gi,(m,p)=>{out.push(cleanPath(p));return m});String(text||'').replace(/(?:src|href)\s*=\s*['"]([^'"]+)['"]/gi,(m,p)=>{out.push(cleanPath(p));return m});return uniq(out)}
function lane(path,from){let p=String(path||'').toLowerCase(),f=String(from||'').toLowerCase();if(/test|candidate|repo-index|route-health|path-certifier|simulation|diagnostic|archive|history|old-panel|last-known|legacy/.test(p))return'legacy_or_test_candidate';if(HISTORIC_CURRENT_REFERENCES.includes(path))return'legacy_or_test_candidate';if(/last-good|recovery|restore|safe-writer|code-safety|safety|resident|clean-v21|clean-v22/.test(p)||/last-good|recovery/.test(f))return'fallback_or_recovery_candidate';if(CURRENT_BOOT_ROOT.includes(path))return'current_boot_root';return'direct_current_candidate'}
function canFollow(path,depth,sourceLane){if(depth>2)return false;if(/legacy_or_test/.test(sourceLane))return false;if(/fallback_or_recovery/.test(sourceLane)&&depth>1)return false;if(/current-inner\.html|home-single-v1[024]|route-guardian-v1|current-inner-cleanbug-rgcontrols-v(2|9|13|16)\.html|index\.html|bm\.html|private-bug|resident-notes|zip-xray/.test(path))return false;return true}
async function fetchText(path){let r=await fetch(path+'?active_path_discovery='+Date.now(),{cache:'no-store'});let text=await r.text().catch(()=>'');return{ok:r.ok,status:r.status,text}}
async function run(){let started=now(),atlas=atlasPaths(),live=liveFiles(),q=[],seen={},edges=[],rows=[],dead=[];function push(path,from,depth){path=cleanPath(path);if(!path||seen[path]||q.some(x=>x.path===path))return;let ln=from?lane(path,from):(CURRENT_BOOT_ROOT.includes(path)?'current_boot_root':lane(path,''));q.push({path,from:from||'',depth:depth||0,lane:ln})}
CURRENT_BOOT_ROOT.concat(live).forEach(p=>push(p,'',0));while(q.length&&rows.length<MAX){let item=q.shift(),path=item.path;if(!path||seen[path])continue;seen[path]=true;let rec={path,from:item.from,depth:item.depth,lane:item.lane,ok:false,status:0,found:[],in_atlas:atlas.includes(path),live_now:live.includes(path)};try{let got=await fetchText(path);rec.ok=got.ok;rec.status=got.status;if(got.ok){rec.found=extract(got.text);rec.found.forEach(p=>{let ln=lane(p,path);edges.push({from:path,to:p,lane:ln});if(canFollow(p,item.depth+1,ln))push(p,path,item.depth+1)})}else dead.push({path,status:got.status,lane:item.lane,from:item.from})}catch(e){rec.error=String(e&&e.message||e);dead.push({path,error:rec.error,lane:item.lane,from:item.from})}rows.push(rec)}
let reachable=uniq(rows.filter(r=>r.ok).map(r=>r.path));let liveMissing=live.filter(p=>!atlas.includes(p));let directMissing=rows.filter(r=>r.ok&&r.lane==='direct_current_candidate'&&!atlas.includes(r.path)).map(r=>r.path);let fallbackMissing=rows.filter(r=>r.ok&&r.lane==='fallback_or_recovery_candidate'&&!atlas.includes(r.path)).map(r=>r.path);let legacyMissing=rows.filter(r=>r.ok&&r.lane==='legacy_or_test_candidate'&&!atlas.includes(r.path)).map(r=>r.path);let hard=uniq(liveMissing.concat(directMissing));let oldAsRoot=uniq(rows.filter(r=>HISTORIC_CURRENT_REFERENCES.includes(r.path)&&r.lane==='current_boot_root').map(r=>r.path));
let report={type:'PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1',version:VERSION,owner:'pmp-active-path-discovery-machine-v1',started_at:started,finished_at:now(),mode:'passive_discovery_only',rule:'Reads active v30 app files and records a report only. No fixing, moving, deleting, Bank rebuild, route change, or app data migration.',pass_alignment:{goal:'Frozen path truth alignment. v22/map12/reload-owner-v30/current-inner-v30 are the current boot chain; v21/v29 and older are historic/support only.',current_boot_root:CURRENT_BOOT_ROOT,historic_current_references_not_boot_root:HISTORIC_CURRENT_REFERENCES,historic_reference_current_boot_root_count:oldAsRoot.length,historic_reference_current_boot_root:oldAsRoot},scanned_count:rows.length,reachable_count:reachable.length,atlas_count:atlas.length,hard_missing_count:hard.length,live_runtime_missing_count:liveMissing.length,direct_current_missing_count:uniq(directMissing).length,fallback_or_recovery_missing_count:uniq(fallbackMissing).length,legacy_or_test_missing_count:uniq(legacyMissing).length,dead_reference_count:dead.length,hard_missing:hard,live_runtime_missing:liveMissing,direct_current_missing:uniq(directMissing),fallback_or_recovery_missing:uniq(fallbackMissing),legacy_or_test_missing:uniq(legacyMissing),dead_references:dead,reachable_files:reachable,live_files:live,edges,scanned:rows,freeze_gate:{pass:hard.length===0&&oldAsRoot.length===0,rule:'Freeze only if hard_missing_count is zero and historic current references are not classified as current_boot_root.'}};
LAST=report;try{localStorage.setItem(REPORT_KEY,JSON.stringify(report,null,2));localStorage.setItem(RECEIPT_KEY,JSON.stringify({type:'PMP_ACTIVE_PATH_DISCOVERY_RECEIPT_V1',version:VERSION,at:now(),hard_missing_count:hard.length,dead_reference_count:dead.length,historic_reference_current_boot_root_count:oldAsRoot.length,freeze_gate_pass:report.freeze_gate.pass},null,2))}catch(e){}window.PMPActivePathDiscoveryReportV1=report;mount();return report}
function summary(r){if(!r)return'Waiting for discovery scan...';let old=(r.pass_alignment&&typeof r.pass_alignment.historic_reference_current_boot_root_count==='number')?' · old-as-root: '+r.pass_alignment.historic_reference_current_boot_root_count:'';return 'hard missing: '+r.hard_missing_count+' · live: '+r.live_runtime_missing_count+' · direct: '+r.direct_current_missing_count+' · fallback: '+r.fallback_or_recovery_missing_count+' · legacy/test: '+r.legacy_or_test_missing_count+' · dead: '+r.dead_reference_count+old}
function val(x){return x==null?'':String(x)}
function compactProof(r){return ['PMP_DISCOVERY_FREEZE_PROOF_V1','report_version: '+val(r&&r.version),'finished_at: '+val(r&&r.finished_at),'hard_missing_count: '+val(r&&r.hard_missing_count),'live_runtime_missing_count: '+val(r&&r.live_runtime_missing_count),'direct_current_missing_count: '+val(r&&r.direct_current_missing_count),'fallback_or_recovery_missing_count: '+val(r&&r.fallback_or_recovery_missing_count),'legacy_or_test_missing_count: '+val(r&&r.legacy_or_test_missing_count),'dead_reference_count: '+val(r&&r.dead_reference_count),'historic_reference_current_boot_root_count: '+val(r&&r.pass_alignment&&r.pass_alignment.historic_reference_current_boot_root_count),'freeze_gate_pass: '+val(r&&r.freeze_gate&&r.freeze_gate.pass),'side_effects: no_fix no_move no_delete no_reroute no_bank_rebuild no_storage_migration'].join('\n')}
async function copyText(d,txt){try{await navigator.clipboard.writeText(txt)}catch(e){let ta=d.createElement('textarea');ta.value=txt;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.left='-9999px';d.body.appendChild(ta);ta.select();d.execCommand('copy');ta.remove()}}
async function copyNow(d,r,out){r=r||LAST||await run();let txt=compactProof(r);await copyText(d,txt);try{localStorage.setItem(COPY_RECEIPT_KEY,JSON.stringify({type:'PMP_ACTIVE_PATH_DISCOVERY_COPY_RECEIPT_V1',version:VERSION,at:now(),mode:'compact_freeze_proof_no_download',hard_missing_count:r.hard_missing_count,dead_reference_count:r.dead_reference_count,freeze_gate_pass:r.freeze_gate&&r.freeze_gate.pass,text_length:txt.length},null,2))}catch(e){}if(out)out.textContent='Discovery Freeze Proof copied. '+summary(r)+' · freeze_gate_pass: '+(r.freeze_gate&&r.freeze_gate.pass)}
function button(d,text,fn){let b=d.createElement('button');b.type='button';b.textContent=text;b.style.cssText='width:100%;border:2px solid var(--line,#07101c);border-radius:16px;padding:12px;margin:8px 0;background:var(--a,#acd1fb);color:var(--buttonText,#101827);font:inherit;font-weight:950;text-align:left';b.onclick=fn;return b}
function mount(){let report=LAST;eachDoc(d=>{try{let target=d.querySelector('#control .card')||d.querySelector('[data-screen="control"] .card')||d.querySelector('#control');if(!target)return;let card=d.getElementById('pmpActivePathDiscoveryCardV1');if(!card){card=d.createElement('div');card.id='pmpActivePathDiscoveryCardV1';card.style.cssText='background:var(--card,#fff);color:var(--text,#101827);border:2px solid var(--line,#07101c);border-radius:20px;padding:12px;margin:10px 0;white-space:pre-wrap';let title=d.createElement('b');title.textContent='Active Path Discovery';let out=d.createElement('div');out.id='pmpActivePathDiscoveryOutV1';card.appendChild(title);card.appendChild(out);card.appendChild(button(d,'Copy Discovery Freeze Proof',()=>copyNow(d,LAST,out)));card.appendChild(button(d,'Run Discovery Again',async()=>{out.textContent='Running discovery...';let r=await run();out.textContent=summary(r)}));target.appendChild(card)}let out=card.querySelector('#pmpActivePathDiscoveryOutV1');if(out)out.textContent=summary(report);Array.from(card.querySelectorAll('button')).forEach(b=>{if(/^Copy Discovery/i.test(b.textContent||''))b.textContent='Copy Discovery Freeze Proof'})}catch(e){}})}
window.PMPActivePathDiscoveryMachineV1={version:VERSION,run,mount,reportKey:REPORT_KEY,currentBootRoot:CURRENT_BOOT_ROOT,historicCurrentReferences:HISTORIC_CURRENT_REFERENCES,copyNow};
setTimeout(run,3500);[1000,2500,4500,7000,10000,15000,22000,30000,45000,60000].forEach(t=>setTimeout(mount,t));setInterval(mount,5000);
})();