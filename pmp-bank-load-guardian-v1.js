(()=>{
'use strict';
const V='1.0.3-includes-native-load-order-repair-receipt-20260710A';
const OWNER='pmp-bank-load-guardian-v1';
const KEY='pmp_bank_load_guardian_v1_receipt';
const REPORT='pmp_bank_load_guardian_v1_report';
const HOME_RECEIPT='pmp_bank_home_visibility_guard_v1_receipt';
const HOME_REPORT='pmp_bank_home_visibility_guard_v1_report';
const NATIVE_RECEIPT='pmp_bank_native_load_order_repair_v1_receipt';
const NATIVE_REPORT='pmp_bank_native_load_order_repair_v1_report';
const BANKS=[
 {title:'World Bank',sub:'records: 0 · references: 0'},
 {title:'Continuous Run Bank',sub:'records: 0 · references: 0'},
 {title:'Connections Bank',sub:'records: 0 · references: 0'},
 {title:'Library Bank',sub:'records: 0 · references: 0'},
 {title:'Workshop Bank',sub:'records: 0 · references: 0'},
 {title:'Control Bank',sub:'records: 0 · references: 0'}
];
let lastBlankAt=0;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function txt(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function visible(w,el){try{let r=el.getBoundingClientRect(),cs=w.getComputedStyle(el);return r.width>40&&r.height>20&&cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>0&&r.bottom>0&&r.top<(w.innerHeight||900)}catch(e){return false}}
function isDiagOrNav(el){try{if(el.closest&&el.closest('#pmpDiagnosticsScreenV1'))return true;if(el.id==='pmpDiagnosticsTabBtn')return true;let tag=(el.tagName||'').toLowerCase();if(tag==='nav'||tag==='footer')return true}catch(e){}return false}
function hasBankTitle(t){return /(^|\s)Bank(\s|$)/i.test(t)}
function hasBankSubtitle(t){return /Master Bank Inventory and source-bank routing/i.test(t)}
function hasInventoryText(t){return /World Bank|Continuous Run Bank|Connections Bank|Library Bank|Workshop Bank|Control Bank|records:\s*0\s*·\s*references:/i.test(t)}
function isActiveBankScreenText(t){return hasBankTitle(t)&&hasBankSubtitle(t)}
function relatedBankLoad(){return {home_visibility_guard_receipt:read(HOME_RECEIPT)||{status:'not_run_or_no_receipt_yet',key:HOME_RECEIPT},home_visibility_guard_report:read(HOME_REPORT)||{status:'not_run_or_no_report_yet',key:HOME_REPORT},native_load_order_repair_receipt:read(NATIVE_RECEIPT)||{status:'not_run_or_no_receipt_yet',key:NATIVE_RECEIPT},native_load_order_repair_report:read(NATIVE_REPORT)||{status:'not_run_or_no_report_yet',key:NATIVE_REPORT}}}
function bankScreenCandidates(){let out=[];docs(T().document).forEach(d=>{try{let w=d.defaultView||T();let els=Array.from(d.querySelectorAll('main,section,[data-page],.screen,.page,.card,body>div,body'));els.forEach(el=>{if(isDiagOrNav(el)||!visible(w,el))return;let t=txt(el);if(isActiveBankScreenText(t)){let score=0;if(/^Bank\b/i.test(t))score+=10;if(hasInventoryText(t))score+=5;let r=el.getBoundingClientRect();out.push({d,w,el,t,score,top:r.top,height:r.height,width:r.width})}})}catch(e){}});out.sort((a,b)=>b.score-a.score||a.top-b.top||a.t.length-b.t.length);return out}
function cardHTML(){return '<div id="pmpBankLoadGuardianInventoryV1" data-pmp-bank-load-guardian="true">'+BANKS.map(b=>'<button class="big green" type="button" data-pmp-bank-load-guardian-card="'+b.title.replace(/"/g,'')+'"><span class="icon">▣</span><span>'+b.title+'<small>'+b.sub+'</small></span><span class="chev">›</span></button>').join('')+'</div>'}
function safeFindMount(el){try{let existing=el.querySelector('#pmpBankLoadGuardianInventoryV1');if(existing)return {mount:existing,exists:true};let buttons=Array.from(el.querySelectorAll('button,.big,[role="button"]')).filter(x=>/World Bank|Continuous Run Bank|Connections Bank|Library Bank|Workshop Bank|Control Bank/i.test(txt(x)));if(buttons.length)return {mount:null,exists:true};let headings=Array.from(el.querySelectorAll('h1,h2,p,div')).filter(x=>/Master Bank Inventory and source-bank routing/i.test(txt(x)));let sub=headings[0];return {mount:sub&&sub.parentElement||el,exists:false}}catch(e){return{mount:el,exists:false}}}
function baseSideEffects(){return {route_change:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',bank_delete:'not_attempted',bank_records_change:'not_attempted'}}
function evaluate(reason){let cands=bankScreenCandidates();let active=cands[0]||null;let report={type:'PMP_BANK_LOAD_GUARDIAN_V1_REPORT',version:V,owner:OWNER,at:now(),reason:reason||'evaluate',status:'BANK_LOAD_GUARDIAN_READY',bank_shell_visible:false,bank_inventory_visible:false,blank_bank_shell_detected:false,active_bank_screen_candidate_count:cands.length,action:'none',related_receipts:relatedBankLoad(),side_effects:baseSideEffects()};
 if(active){report.bank_shell_visible=true;report.bank_inventory_visible=hasInventoryText(active.t);report.blank_bank_shell_detected=!report.bank_inventory_visible;report.bank_text_sample=active.t.slice(0,320);report.active_bank_candidate={score:active.score,top:Math.round(active.top),height:Math.round(active.height),width:Math.round(active.width)};}
 put(REPORT,report);return report}
function receipt(status,extra,side){let r=Object.assign({type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status,related_receipts:relatedBankLoad(),side_effects:side||baseSideEffects()},extra||{});put(KEY,r);return r}
function repairIfBlank(reason){let r=evaluate(reason||'repair_check');if(!r.bank_shell_visible||r.bank_inventory_visible){lastBlankAt=0;receipt(r.bank_shell_visible?'no_blank_bank_repair_needed':'no_active_bank_screen_detected',{bank_shell_visible:r.bank_shell_visible,bank_inventory_visible:r.bank_inventory_visible,blank_bank_shell_detected:r.blank_bank_shell_detected},r.side_effects);return r}
 let age=lastBlankAt?Date.now()-lastBlankAt:0;if(!lastBlankAt){lastBlankAt=Date.now();receipt('blank_bank_detected_waiting_for_native_inventory',{bank_shell_visible:true,bank_inventory_visible:false,blank_bank_shell_detected:true,wait_ms_before_guardian:1000},r.side_effects);return r}
 if(age<1000){receipt('blank_bank_waiting',{elapsed_ms:age,bank_shell_visible:true,bank_inventory_visible:false,blank_bank_shell_detected:true},r.side_effects);return r}
 let c=bankScreenCandidates()[0];if(!c){lastBlankAt=0;return r}let sf=safeFindMount(c.el);if(sf.exists){lastBlankAt=0;return evaluate('native_inventory_appeared')}
 try{let wrap=c.d.createElement('div');wrap.innerHTML=cardHTML();let inv=wrap.firstElementChild;let mount=sf.mount||c.el;mount.appendChild(inv);lastBlankAt=0;let out=evaluate('guardian_restored_visible_inventory');out.action='restored_visible_inventory_cards_only';out.guardian_note='Restored missing visible Bank inventory card surface after native inventory stayed blank. Did not modify Bank records, IndexedDB, or storage.';out.related_receipts=relatedBankLoad();put(REPORT,out);receipt('blank_bank_shell_repaired_visible_inventory_only',{action:out.action,bank_shell_visible:true,bank_inventory_visible:true,blank_bank_shell_detected:false},out.side_effects);return out}catch(e){receipt('repair_failed',{error:String(e&&e.message||e)},r.side_effects);return r}}
function run(reason){return repairIfBlank(reason||'run')}
window.PMPBankLoadGuardianV1={version:V,owner:OWNER,run,evaluate,rule:'Active Bank screen only. Detects Bank by actual Bank title plus Bank subtitle, excluding Diagnostics and nav. Report includes Bank Home Visibility Guard and Native Bank Load Order Repair receipts/reports. Does not change records, IndexedDB, storage, or routes.'};try{T().PMPBankLoadGuardianV1=window.PMPBankLoadGuardianV1}catch(e){};
[250,700,1200,2200,4200].forEach(t=>setTimeout(()=>run('startup_'+t),t));setInterval(()=>run('interval'),1800);
})();