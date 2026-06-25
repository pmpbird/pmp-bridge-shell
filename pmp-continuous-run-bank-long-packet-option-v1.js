(()=>{
'use strict';
const V='1.2.0-source-zip-satisfies-long-reference';
const TYPE='long_packet_0_26';
const LABEL='Long Packet 00-26 / Full Raw Notes';
const MANIFEST_KEY='pmp_continuous_run_bank_transfer_store_manifest_v1';
function docs(root,depth,arr){arr=arr||[];depth=depth||0;if(!root||depth>8)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let doc=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(doc)docs(doc,depth+1,arr)}catch(e){}})}catch(e){}return arr}
function readManifest(){try{return JSON.parse(localStorage.getItem(MANIFEST_KEY)||'{}')||{}}catch(e){return{}}}
function saveManifest(m){try{localStorage.setItem(MANIFEST_KEY,JSON.stringify(m,null,2))}catch(e){}return m}
function hasLong(m){let direct=!!(m&&m.items&&m.items[TYPE]&&Object.keys(m.items[TYPE]).length);let zip=!!(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present&&m.must_reference_source_zip.indexeddb_key);return direct||zip}
function sourceMode(m){if(m&&m.items&&m.items[TYPE]&&Object.keys(m.items[TYPE]).length)return 'TEXT SLOT PRESENT';if(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present)return 'SOURCE ZIP PRESENT';return 'MISSING'}
function addLongRule(m){m=m||{};let r={type:TYPE,label:LABEL,min:1000,terms:['packet','note'],rule:'Satisfied by either long_packet_0_26 text slot OR must_reference_source_zip source archive.'};m.lossless_required=Array.isArray(m.lossless_required)?m.lossless_required:[];if(!m.lossless_required.some(x=>x&&x.type===TYPE))m.lossless_required.push(r);return m}
function enforce(res){res=res||{};let m=res.manifest||readManifest();m=addLongRule(m);let present=hasLong(m);res.long_packet_0_26_present=present;res.long_packet_0_26_mode=sourceMode(m);if(!present){res.lossless_verified=false;res.verified=false;res.lossless_missing=Array.from(new Set([].concat(res.lossless_missing||[],[TYPE])));m.lossless_verified=false;m.verified=false;m.verification=Object.assign({},m.verification||{},{status:'missing_must_reference_long_source_00_26',lossless_verified:false,verified:false,lossless_missing:res.lossless_missing,long_packet_0_26_required:true,long_packet_0_26_present:false,long_packet_0_26_mode:sourceMode(m)})}else{m.verification=Object.assign({},m.verification||{},{long_packet_0_26_required:true,long_packet_0_26_present:true,long_packet_0_26_mode:sourceMode(m)})}
res.manifest=saveManifest(m);return res}
function patchApi(){let api=window.PMPContinuousRunBankTransferStoreV1;if(!api||api.__long_packet_required_v12)return;api.__long_packet_required_v12=true;api.lossless_required=Array.isArray(api.lossless_required)?api.lossless_required:[];if(!api.lossless_required.some(x=>x&&x.type===TYPE))api.lossless_required.push({type:TYPE,label:LABEL,min:1000,terms:['packet','note']});if(api.verifyStore){let old=api.verifyStore.bind(api);api.verifyStore=function(writeReceipt){return enforce(old(writeReceipt))}}
if(api.engineGate){let oldGate=api.engineGate.bind(api);api.engineGate=function(){let g=oldGate()||{},r=api.verifyStore?api.verifyStore(false):enforce({});if(!r.long_packet_0_26_present){g.ok=false;g.lossless_verified=false;g.reason='missing_must_reference_long_source_00_26';g.message='Long Packet 00-26 source is required before Resident runs.';g.missing=Array.from(new Set([].concat(g.missing||[],[TYPE])))}return g}}
}
function patchSelect(doc){try{doc.querySelectorAll('[data-tts-kind]').forEach(select=>{if(select.querySelector('option[value="'+TYPE+'"]'))return;let opt=doc.createElement('option');opt.value=TYPE;opt.textContent=LABEL;select.appendChild(opt)})}catch(e){}}
function patchStatus(doc){try{let box=doc.querySelector('[data-temp-transfer-store]');if(!box)return;let m=addLongRule(readManifest()),present=hasLong(m),mode=sourceMode(m);saveManifest(m);let st=box.querySelector('[data-tts-status]');if(st){let t=st.textContent||'';if(!present)t=t.replace('Lossless Verified: YES','Lossless Verified: NO');t=t.replace(/\nMust-reference long packet 00-26: .*/g,'');t+='\nMust-reference long source 00-26: '+(present?'PRESENT':'MISSING')+' ('+mode+')';st.textContent=t}
let note=box.querySelector('[data-long-packet-note]');if(!note){note=doc.createElement('pre');note.className='note';note.setAttribute('data-long-packet-note','');box.appendChild(note)}note.textContent='MUST-REFERENCE SOURCE 00-26\nStatus: '+(present?'PRESENT':'MISSING')+'\nMode: '+mode+'\nRule: short packets control the operating map; long source 00-26 must be referenced as source/proof/recovery body, but must not overwrite the short map.'}catch(e){}}
function scan(){patchApi();docs(document).forEach(doc=>{patchSelect(doc);patchStatus(doc)})}
window.PMPLongPacketStoreOptionV1={version:V,scan,type:TYPE,label:LABEL,enforce};
window.addEventListener('load',()=>[100,500,1200,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1200);
scan();
})();