(()=>{
'use strict';
const V='1.0.0-long-packet-00-26-store-option';
const OPT_VALUE='long_packet_0_26';
const OPT_LABEL='Long Packet 00-26 / Full Raw Notes';
function docs(root,depth,arr){arr=arr||[];depth=depth||0;if(!root||depth>8)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let doc=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(doc)docs(doc,depth+1,arr)}catch(e){}})}catch(e){}return arr}
function patchSelect(doc){try{doc.querySelectorAll('[data-tts-kind]').forEach(select=>{if(select.querySelector('option[value="'+OPT_VALUE+'"]'))return;let opt=doc.createElement('option');opt.value=OPT_VALUE;opt.textContent=OPT_LABEL;select.appendChild(opt)})}catch(e){}}
function patchImporter(doc){try{let box=doc.querySelector('[data-temp-transfer-store]');if(!box||box.querySelector('[data-long-packet-note]'))return;let note=doc.createElement('pre');note.className='note';note.setAttribute('data-long-packet-note','');note.textContent='Optional source archive slot available: '+OPT_VALUE+'\nUse it for the full long packet 00-26 notes. It stores source body without changing Lossless Verified requirements.';box.appendChild(note)}catch(e){}}
function scan(){docs(document).forEach(doc=>{patchSelect(doc);patchImporter(doc)})}
window.PMPLongPacketStoreOptionV1={version:V,scan,type:OPT_VALUE,label:OPT_LABEL};
window.addEventListener('load',()=>[100,500,1200,2500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1500);
scan();
})();