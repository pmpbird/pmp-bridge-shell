(()=>{
'use strict';
const V='1.0.0-blank-bank-shell-inventory-guardian-20260710A';
const OWNER='pmp-bank-load-guardian-v1';
const KEY='pmp_bank_load_guardian_v1_receipt';
const REPORT='pmp_bank_load_guardian_v1_report';
const BANKS=[
 {title:'World Bank',sub:'records: 0 · references: 0'},
 {title:'Continuous Run Bank',sub:'records: 0 · references: 0'},
 {title:'Connections Bank',sub:'records: 0 · references: 0'},
 {title:'Library Bank',sub:'records: 0 · references: 0'},
 {title:'Workshop Bank',sub:'records: 0 · references: 0'},
 {title:'Control Bank',sub:'records: 0 · references: 0'}
];
let lastBlankAt=0,lastRepairAt=0;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function txt(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function visible(w,el){try{let r=el.getBoundingClientRect(),cs=w.getComputedStyle(el);return r.width>40&&r.height>20&&cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>0&&r.bottom>0&&r.top<(w.innerHeight||900)}catch(e){return false}}
function isBankScreenText(t){return /\bBank\b/.test(t)&&/Master Bank Inventory and source-bank routing/i.test(t)}
function hasInventoryText(t){return /World Bank|Continuous Run Bank|Connections Bank|Library Bank|Workshop Bank|Control Bank/i.test(t)}
function bankScreenCandidates(){let out=[];docs(T().document).forEach(d=>{try{let w=d.defaultView||T();Array.from(d.querySelectorAll('section,.screen,.card,main,div')).forEach(el=>{if(!visible(w,el))return;if(el.closest&&el.closest('#pmpDiagnosticsScreenV1'))return;let t=txt(el);if(isBankScreenText(t))out.push({d,w,el,t})})}catch(e){}});out.sort((a,b)=>a.t.length-b.t.length);return out}
function cardHTML(){return '<div id="pmpBankLoadGuardianInventoryV1" data-pmp-bank-load-guardian="true">'+BANKS.map(b=>'<button class="big green" type="button" data-pmp-bank-load-guardian-card="'+b.title.replace(/"/g,'')+'"><span class="icon">▣</span><span>'+b.title+'<small>'+b.sub+'</small></span><span class="chev">›</span></button>').join('')+'</div>'}
function safeFindMount(el){try{let existing=el.querySelector('#pmpBankLoadGuardianInventoryV1');if(existing)return {mount:existing,exists:true};let buttons=Array.from(el.querySelectorAll('button,.big,[role="button"]')).filter(x=>/World Bank|Continuous Run Bank|Connections Bank|Library Bank|Workshop Bank|Control Bank/i.test(txt(x)));if(buttons.length)return {mount:null,exists:true};let sub=Array.from(el.querySelectorAll('p,.sub,div,h1,h2')).find(x=>/Master Bank Inventory and source-bank routing/i.test(txt(x)));return {mount:sub&&sub.parentElement||el,exists:false}}catch(e){return{mount:el,exists:false}}}
function evaluate(reason){let cands=bankScreenCandidates();let active=cands[0]||null;let report={type:'PMP_BANK_LOAD_GUARDIAN_V1_REPORT',version:V,owner:OWNER,at:now(),reason:reason||'evaluate',status:'BANK_LOAD_GUARDIAN_READY',bank_shell_visible:!!active,bank_inventory_visible:false,blank_bank_shell_detected:false,action:'none',side_effects:{route_change:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',bank_delete:'not_attempted',bank_records_change:'not_attempted'}};
 if(active){report.bank_inventory_visible=hasInventoryText(active.t);report.blank_bank_shell_detected=!report.bank_inventory_visible;report.bank_text_sample=active.t.slice(0,260);}
 put(REPORT,report);return report}
function repairIfBlank(reason){let r=evaluate(reason||'repair_check');if(!r.bank_shell_visible||r.bank_inventory_visible){put(KEY,{type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'no_blank_bank_repair_needed',bank_shell_visible:r.bank_shell_visible,bank_inventory_visible:r.bank_inventory_visible,side_effects:r.side_effects});return r}
 let age=lastBlankAt?Date.now()-lastBlankAt:0;if(!lastBlankAt){lastBlankAt=Date.now();put(KEY,{type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'blank_bank_detected_waiting_for_native_inventory',bank_shell_visible:true,bank_inventory_visible:false,wait_ms_before_guardian:900,side_effects:r.side_effects});return r}
 if(age<900){put(KEY,{type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'blank_bank_waiting',elapsed_ms:age,side_effects:r.side_effects});return r}
 let c=bankScreenCandidates()[0];if(!c){lastBlankAt=0;return r}let sf=safeFindMount(c.el);if(sf.exists){lastBlankAt=0;return evaluate('native_inventory_appeared')}
 try{let wrap=c.d.createElement('div');wrap.innerHTML=cardHTML();let inv=wrap.firstElementChild;let mount=sf.mount||c.el;mount.appendChild(inv);lastRepairAt=Date.now();lastBlankAt=0;let out=evaluate('guardian_restored_visible_inventory');out.action='restored_visible_inventory_cards_only';out.guardian_note='Restored missing Bank inventory card surface after native inventory stayed blank. Did not modify Bank records or storage.';put(REPORT,out);put(KEY,{type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'blank_bank_shell_repaired_visible_inventory_only',action:out.action,bank_shell_visible:true,bank_inventory_visible:true,side_effects:out.side_effects});return out}catch(e){put(KEY,{type:'PMP_BANK_LOAD_GUARDIAN_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'repair_failed',error:String(e&&e.message||e),side_effects:r.side_effects});return r}}
function run(reason){return repairIfBlank(reason||'run')}
window.PMPBankLoadGuardianV1={version:V,owner:OWNER,run,evaluate,rule:'Fixes only blank visible Bank inventory shell by restoring visible inventory cards. Does not change records, IndexedDB, storage, routes, or Bank data.'};try{T().PMPBankLoadGuardianV1=window.PMPBankLoadGuardianV1}catch(e){};
[250,700,1200,2200,4200].forEach(t=>setTimeout(()=>run('startup_'+t),t));setInterval(()=>run('interval'),1800);
})();
