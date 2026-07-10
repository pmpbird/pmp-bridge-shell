(()=>{
'use strict';
const V='1.0.0-control-legacy-diagnostics-quarantine-20260710A';
const OWNER='pmp-control-legacy-diagnostics-quarantine-v1';
const KEY='pmp_control_legacy_diagnostics_quarantine_v1_receipt';
const MARK='data-pmp-control-legacy-diagnostics-quarantined';
const PATTERNS=[
 /Owner Diagnostics/i,
 /Copy Startup Audit/i,
 /Copy Receipt Summary/i,
 /Copy Smoke Test Proof/i,
 /Copy Bank\s*\/\s*Continuous\s*Run Diagnostics/i,
 /PMP_OWNER_DIAGNOSTICS_FOUNDATION/i,
 /PASS7_CERTIFIED/i,
 /passive proof packet for ChatGPT/i,
 /Pass 4C Continuous Run scoped proof/i
];
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function text(x){return String((x&&x.textContent)||'').replace(/\s+/g,' ').trim()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function visible(w,el){try{let r=el.getBoundingClientRect(),cs=w.getComputedStyle(el);return r.width>10&&r.height>10&&cs.display!=='none'&&cs.visibility!=='hidden'&&r.bottom>0&&r.top<(w.innerHeight||900)}catch(e){return false}}
function activeControl(d){try{let c=d.getElementById('control');if(c&&c.classList&&c.classList.contains('on'))return c;let tabs=Array.from(d.querySelectorAll('.tab.on,[data-tab="control"].on'));if(tabs.length&&c)return c}catch(e){}return null}
function matchDiag(t){return PATTERNS.some(p=>p.test(t))}
function chooseBlock(el,control){let n=el;for(let i=0;i<6&&n&&n!==control;i++,n=n.parentElement){let t=text(n);if(t.length>60&&t.length<9000&&(matchDiag(t)||/Diagnostics/i.test(t)&&/Copy|PASS7|Receipt|Smoke Test|Continuous Run Diagnostics/i.test(t))){return n}}return el}
function quarantineDoc(d,reason){let w=d.defaultView||T(),control=activeControl(d);if(!control||!visible(w,control))return {control_visible:false,quarantined:0};let changed=0,seen=[];
 Array.from(control.querySelectorAll('h1,h2,h3,p,button,pre,section,div')).forEach(el=>{try{if(el.closest&&el.closest('#pmpDiagnosticsScreenV1'))return;if(el.getAttribute&&el.getAttribute(MARK)==='true')return;let t=text(el);if(!matchDiag(t))return;let block=chooseBlock(el,control);if(!block||block===control)return;if(block.getAttribute(MARK)==='true')return;block.setAttribute(MARK,'true');block.style.display='none';changed++;seen.push(t.slice(0,120))}catch(e){}});
 return {control_visible:true,quarantined:changed,samples:seen.slice(0,8)}
}
function run(reason){let total=0,docs_seen=0,samples=[];docs(T().document).forEach(d=>{try{let r=quarantineDoc(d,reason||'run');if(r.control_visible)docs_seen++;total+=r.quarantined||0;samples=samples.concat(r.samples||[])}catch(e){}});let receipt={type:'PMP_CONTROL_LEGACY_DIAGNOSTICS_QUARANTINE_V1_RECEIPT',version:V,owner:OWNER,at:now(),reason:reason||'run',status:'CONTROL_LEGACY_DIAGNOSTICS_QUARANTINE_ACTIVE',control_docs_seen:docs_seen,quarantined_count:total,samples:samples.slice(0,10),rule:'Scoped quarantine only. Hides legacy diagnostics still rendered in Control Room. Does not move panels, does not touch Bank, does not touch Diagnostics tab, does not rebuild, migrate storage, write IndexedDB, or change routes.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',diagnostics_tab_dom_patch:'not_attempted',panel_move:'not_attempted',storage_migration:'not_attempted',indexeddb_write:'not_attempted',ownership_takeover:'not_attempted'}};put(KEY,receipt);return receipt}
window.PMPControlLegacyDiagnosticsQuarantineV1={version:V,owner:OWNER,run,rule:'Scoped Control-only quarantine for legacy diagnostics.'};try{T().PMPControlLegacyDiagnosticsQuarantineV1=window.PMPControlLegacyDiagnosticsQuarantineV1}catch(e){};
[120,300,700,1400,2600,4200,7000].forEach(t=>setTimeout(()=>run('startup_'+t),t));setInterval(()=>run('interval'),1500);
})();