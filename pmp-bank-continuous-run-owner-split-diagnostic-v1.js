(()=>{
'use strict';
const V='1.0.0-bank-continuous-run-owner-split-diagnostic-20260709A';
const OWNER='pmp-bank-continuous-run-owner-split-diagnostic-v1';
const KEY='pmp_bank_continuous_run_owner_split_diagnostic_v1';
const RECEIPT='pmp_bank_continuous_run_owner_split_diagnostic_receipt_v1';
const COPY='pmp_bank_continuous_run_owner_split_diagnostic_copy_v1';
const LEVELS=['Level 1','Level 2','Level 3','Level 4','Level 4B','Level 5','Level 30','Level 30B','Resident Startup Gate','Resident Use Mode','Request Intake'];
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function txt(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function deepest(){let d=T().document,w=T();for(let i=0;i<10;i++){try{let frames=Array.from(d.querySelectorAll('iframe,frame')).filter(f=>{try{return f.contentDocument&&f.contentDocument.body}catch(e){return false}});if(!frames.length)break;let f=frames[frames.length-1];w=f.contentWindow;d=f.contentDocument||w.document}catch(e){break}}return{w,d}}
function visible(w,el){try{let r=el.getBoundingClientRect(),cs=w.getComputedStyle(el);return r.width>5&&r.height>5&&cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>0&&r.bottom>0&&r.top<(w.innerHeight||900)}catch(e){return false}}
function allVisibleTexts(){let o=deepest(),arr=[];docs(o.d).forEach(d=>{try{let w=d.defaultView||o.w;Array.from(d.querySelectorAll('body *')).forEach(el=>{let t=txt(el);if(t&&t.length<240&&visible(w,el))arr.push(t)})}catch(e){}});return Array.from(new Set(arr))}
function findVisible(patterns){let o=deepest(),hits=[];docs(o.d).forEach(d=>{try{let w=d.defaultView||o.w;Array.from(d.querySelectorAll('body *')).forEach(el=>{let t=txt(el);if(!t||!visible(w,el))return;for(const p of patterns){if(p.test(t)){let r=el.getBoundingClientRect();hits.push({text:t.slice(0,180),tag:el.tagName,top:Math.round(r.top),height:Math.round(r.height),width:Math.round(r.width)});break}}})}catch(e){}});return hits.slice(0,30)}
function countContaining(texts,rx){return texts.filter(t=>rx.test(t)).length}
function evaluate(){let texts=allVisibleTexts();let bankVisible=countContaining(texts,/\bBank\b/i)>0;let continuousVisible=countContaining(texts,/Continuous Run/i)>0;let bankHome=countContaining(texts,/Master Bank Inventory/i)>0||countContaining(texts,/World Bank/i)>0;let continuousBank=countContaining(texts,/Continuous Run Bank/i)>0;let deleteTools=countContaining(texts,/Bank Delete Tools/i)>0;let runStateDetail=countContaining(texts,/Run State Detail/i)>0;let levelHits={};LEVELS.forEach(l=>levelHits[l]=countContaining(texts,new RegExp(l.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'i')));
let level3plusVisible=['Level 3','Level 4','Level 4B','Level 5','Level 30','Level 30B','Resident Startup Gate','Resident Use Mode','Request Intake'].filter(k=>levelHits[k]>0);
let duplicatePanels=[];Object.keys(levelHits).forEach(k=>{if(levelHits[k]>1)duplicatePanels.push({panel:k,count:levelHits[k]})});
let helperRules=read('pmp_pass8_helper_rules_receipt_v1');let mount=read('pmp_mount_registry_v1_receipt');let app=read('pmp_app_orchestrator_v1_receipt');let diagnosticsOwner=read('pmp_diagnostics_owner_v1_receipt');
let checks={
 bank_owner_surface_visible:bankVisible?'observed':'not_currently_visible',
 bank_home_or_shell_visible:bankHome?'observed':'not_currently_visible',
 continuous_run_bank_visible:continuousBank?'observed':'not_currently_visible',
 continuous_run_content_visible:continuousVisible?'observed':'not_currently_visible',
 level3plus_gated:level3plusVisible.length===0?'passed_or_not_open':'needs_review_visible_'+level3plusVisible.join('_'),
 duplicate_continuous_run_panels:duplicatePanels.length===0?'none_observed':'needs_review',
 bank_delete_tools_after_run_state_detail:'not_evaluated_until_continuous_run_detail_visible',
 helpers_random_bank_dom_patching:helperRules&&helperRules.status==='PASS8_HELPER_RULES_ACTIVE'?'bounded_by_helper_rules':'needs_review',
 diagnostics_owner_present:diagnosticsOwner&&diagnosticsOwner.status==='DIAGNOSTICS_OWNER_ACTIVE'?'present':'needs_review',
 mount_registry_present:mount&&mount.version?'present':'needs_review',
 app_orchestrator_background_only:app&&app.copy_contract&&app.copy_contract.background_diagnostic_only==='yes'?'yes':'needs_review'
};
let status='BANK_CONTINUOUS_RUN_OWNER_SPLIT_DIAGNOSTIC_READY';
let needsReview=Object.values(checks).some(v=>String(v).indexOf('needs_review')>-1);
let visualScope=bankVisible||continuousVisible?'visual_context_available':'visual_context_not_open';
let report={type:'PMP_BANK_CONTINUOUS_RUN_OWNER_SPLIT_DIAGNOSTIC_V1',version:V,owner:OWNER,at:now(),status,visual_scope:visualScope,read_only:'yes',normal_home:'Diagnostics → Bank / Continuous Run Visual State',purpose:'Permanent diagnostic for Bank Owner / Continuous Run Owner split. This is not a pass-numbered diagnostic.',checks,observed:{bank_visible:bankVisible,bank_home_visible:bankHome,continuous_run_visible:continuousVisible,continuous_run_bank_visible:continuousBank,bank_delete_tools_visible:deleteTools,run_state_detail_visible:runStateDetail,level_hits:levelHits,level3plus_visible:level3plusVisible,duplicate_panel_candidates:duplicatePanels,bank_related_hits:findVisible([/Bank/i,/Continuous Run/i,/Master Bank/i,/Run State/i,/Level 3/i,/Level 30B/i])},interpretation:{bank_owner_expected:'Bank Owner owns Bank bottom tab, Bank shell, Bank home, bank list, detail wrapper, open bank state, and handoff slot.',continuous_run_owner_expected:'Continuous Run Owner owns Continuous Run content inside the Bank Owner slot, panel order, readiness state, Level 1-30/30B content, Resident Startup Gate, Resident Use Mode, and Request Intake.',pass9_use:'Pass 9 certification may read this permanent diagnostic, but this diagnostic itself is not Pass 9.'},side_effects:{route_change:'not_attempted',boot_surface_replacement:'not_attempted',runtime_surface_replacement:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',panel_move:'not_attempted',panel_hide:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted'}};
put(KEY,report);put(RECEIPT,{type:'PMP_BANK_CONTINUOUS_RUN_OWNER_SPLIT_DIAGNOSTIC_RECEIPT_V1',version:V,owner:OWNER,at:now(),status,visual_scope:visualScope,checks,side_effects:report.side_effects});return report}
function copyReport(){let r=evaluate();let text=JSON.stringify(r,null,2);let result='not_confirmed';try{let ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','readonly');ta.style.position='fixed';ta.style.left='12px';ta.style.top='12px';ta.style.width='2px';ta.style.height='2px';ta.style.opacity='0.01';ta.style.zIndex='2147483647';ta.style.fontSize='16px';document.body.appendChild(ta);ta.focus();ta.select();ta.setSelectionRange(0,ta.value.length);result=document.execCommand&&document.execCommand('copy')?'copied':'not_confirmed';ta.remove()}catch(e){}try{if(result!=='copied'&&navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(text)}catch(e){}put(COPY,{type:'PMP_BANK_CONTINUOUS_RUN_OWNER_SPLIT_DIAGNOSTIC_COPY_V1',version:V,owner:OWNER,at:now(),result,status:r.status,visual_scope:r.visual_scope});return {result,report:r}}
window.PMPBankContinuousRunOwnerSplitDiagnosticV1={version:V,owner:OWNER,run:evaluate,evaluate,copyReport,keys:{report:KEY,receipt:RECEIPT,copy:COPY},rule:'Permanent read-only diagnostic owned by Diagnostics Owner. No Bank rebuild, no DOM patch, no panel move, no route change, no storage migration.'};try{T().PMPBankContinuousRunOwnerSplitDiagnosticV1=window.PMPBankContinuousRunOwnerSplitDiagnosticV1}catch(e){};
setTimeout(()=>evaluate(),250);setTimeout(()=>evaluate(),1500);
})();
