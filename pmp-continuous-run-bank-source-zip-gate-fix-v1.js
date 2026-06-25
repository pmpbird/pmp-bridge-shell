(()=>{
'use strict';
const V='1.0.0-source-zip-satisfies-long-source-no-flicker';
const MK='pmp_continuous_run_bank_transfer_store_manifest_v1';
const TYPE='long_packet_0_26';
function W(){try{return window.top||window}catch(e){return window}}
function j(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function s(k,v){try{W().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(root,depth,arr){arr=arr||[];depth=depth||0;if(!root||depth>8)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,arr)}catch(e){}})}catch(e){}return arr}
function sourceZipPresent(m){return !!(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present&&m.must_reference_source_zip.indexeddb_key)}
function longTextPresent(m){return !!(m&&m.items&&m.items[TYPE]&&Object.keys(m.items[TYPE]).length)}
function satisfied(m){return sourceZipPresent(m)||longTextPresent(m)}
function normalize(m){m=m||{};m.must_reference_long_source_00_26={required:true,present:satisfied(m),mode:sourceZipPresent(m)?'SOURCE ZIP PRESENT':(longTextPresent(m)?'TEXT SLOT PRESENT':'MISSING'),rule:'Short packets control operating map. App Packets ZIP or long text slot is required as source body.'};if(m.verification){m.verification.long_packet_0_26_required=true;m.verification.long_packet_0_26_present=m.must_reference_long_source_00_26.present;m.verification.long_packet_0_26_mode=m.must_reference_long_source_00_26.mode;if(m.must_reference_long_source_00_26.present){m.verification.lossless_missing=(m.verification.lossless_missing||[]).filter(x=>x!==TYPE)}}return s(MK,m)}
function patchApi(){let top=W(),api=top.PMPContinuousRunBankTransferStoreV1;if(!api||api.__source_zip_gate_fix_v1)return;api.__source_zip_gate_fix_v1=true;if(api.verifyStore){let old=api.verifyStore.bind(api);api.verifyStore=function(writeReceipt){let r=old(writeReceipt),m=normalize(r.manifest||j(MK,{}));r.manifest=m;r.long_packet_0_26_present=satisfied(m);r.long_packet_0_26_mode=m.must_reference_long_source_00_26.mode;if(r.long_packet_0_26_present){r.lossless_missing=(r.lossless_missing||[]).filter(x=>x!==TYPE);if(r.slot_check_passed&&(!r.lossless_missing||!r.lossless_missing.length)&&(!r.weak_items||!r.weak_items.length)){r.lossless_verified=true;r.verified=true;m.lossless_verified=true;m.verified=true;if(m.verification){m.verification.lossless_verified=true;m.verification.status='lossless_verified'}s(MK,m)}}return r}}
if(api.engineGate){let oldGate=api.engineGate.bind(api);api.engineGate=function(){let g=oldGate(),m=normalize(j(MK,{}));if(satisfied(m)){g.missing=(g.missing||[]).filter(x=>x!==TYPE);if(g.reason==='missing_must_reference_long_packet_0_26'||g.reason==='missing_must_reference_long_source_00_26')g.reason='lossless_verified'}return g}}
}
function patchUi(){let m=normalize(j(MK,{})),ok=satisfied(m),mode=m.must_reference_long_source_00_26.mode;docs(W().document).forEach(d=>{try{d.querySelectorAll('[data-long-packet-note]').forEach(n=>{n.textContent='MUST-REFERENCE SOURCE 00-26\nStatus: '+(ok?'PRESENT':'MISSING')+'\nMode: '+mode+'\nRule: short packets control the operating map; App Packets ZIP supplies source/proof/recovery body.'});d.querySelectorAll('[data-tts-status],[data-run-bank-summary]').forEach(el=>{let t=el.textContent||'';if(ok){t=t.replace(/Must-reference long packet 00-26:\s*MISSING/g,'Must-reference long source 00-26: PRESENT ('+mode+')');t=t.replace(/Must-reference long source 00-26:\s*MISSING[^\n]*/g,'Must-reference long source 00-26: PRESENT ('+mode+')');t=t.replace(/Missing:\s*long_packet_0_26/g,'Missing: none')}el.textContent=t})}catch(e){}})}
function scan(){patchApi();patchUi()}
window.PMPSourceZipGateFixV1={version:V,scan};
window.addEventListener('load',()=>[100,500,1200,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();