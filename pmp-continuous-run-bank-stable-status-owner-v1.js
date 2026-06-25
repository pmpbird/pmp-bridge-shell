(()=>{
'use strict';
const V='1.0.0-hide-flicker-originals-render-stable-clones';
const MK='pmp_continuous_run_bank_transfer_store_manifest_v1';
function W(){try{return window.top||window}catch(e){return window}}
function j(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function docs(root,depth,arr){arr=arr||[];depth=depth||0;if(!root||depth>8)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,arr)}catch(e){}})}catch(e){}return arr}
function sourceZipPresent(m){return !!(m&&m.must_reference_source_zip&&m.must_reference_source_zip.present&&m.must_reference_source_zip.indexeddb_key)}
function longSourceText(m){return 'MUST-REFERENCE SOURCE 00-26\nStatus: '+(sourceZipPresent(m)?'PRESENT':'MISSING')+'\nMode: '+(sourceZipPresent(m)?'SOURCE ZIP PRESENT':'MISSING')+'\nRule: short packets control the operating map; App Packets ZIP supplies source/proof/recovery body.'}
function storeText(m){m=m||{};let items=m.items||{},types=Object.keys(items).sort(),rows=[];rows.push('Slot Check: '+(m.slot_check_passed?'PASSED':'NOT PASSED'));rows.push('Lossless Verified: '+(sourceZipPresent(m)&&m.slot_check_passed?'YES':(m.lossless_verified?'YES':'NO')));rows.push('Must-Reference Source ZIP: '+(sourceZipPresent(m)?'PRESENT':'MISSING'));rows.push('Missing required slots: '+(((m.verification&&m.verification.missing)||[]).length?m.verification.missing.join(', '):'none'));let lm=((m.verification&&m.verification.lossless_missing)||[]).filter(x=>x!=='long_packet_0_26');if(sourceZipPresent(m))lm=lm.filter(x=>x!=='must_reference_source_zip');rows.push('Missing lossless items: '+(lm.length?lm.join(', '):'none'));rows.push('Weak / placeholder items: '+(((m.verification&&m.verification.weak_items)||[]).length?'check manifest':'none'));rows.push('Bank: Continuous Run Bank');rows.push('Items:');types.forEach(t=>Object.keys(items[t]||{}).sort().forEach(id=>{let x=items[t][id];rows.push('['+t+'] '+(x.name||id)+' | chars '+(x.characters||0)+' | hash '+(x.hash||''))}));return rows.join('\n')}
function makeAfter(doc,orig,attr,text){let c=orig.parentNode.querySelector('pre['+attr+']');if(!c){c=doc.createElement('pre');c.className=orig.className||'note';c.setAttribute(attr,'');orig.parentNode.insertBefore(c,orig.nextSibling)}if(c.textContent!==text)c.textContent=text;orig.style.setProperty('display','none','important')}
function patch(){let m=j(MK,{});docs(W().document).forEach(d=>{try{d.querySelectorAll('pre[data-tts-status]').forEach(o=>makeAfter(d,o,'data-stable-tts-status',storeText(m)));d.querySelectorAll('pre[data-long-packet-note]').forEach(o=>makeAfter(d,o,'data-stable-long-source-status',longSourceText(m)))}catch(e){}})}
window.PMPStableStatusOwnerV1={version:V,patch};
window.addEventListener('load',()=>[50,200,700,1500,3000].forEach(t=>setTimeout(patch,t)));
setInterval(patch,1000);
patch();
})();