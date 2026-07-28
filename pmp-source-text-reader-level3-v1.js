(()=>{
'use strict';
const V='1.3.0-level3-clear-result-labels';
const MK='pmp_continuous_run_bank_transfer_store_manifest_v1';
const DB='pmp_continuous_run_bank_source_pdf_text_db_v1';
const OS='texts';
function W(){try{return window.top||window}catch(e){return window}}
function j(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function openDB(){return new Promise((res,rej)=>{try{let q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{try{q.result.createObjectStore(OS)}catch(e){}};q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('text DB open failed'))}catch(e){rej(e)}})}
async function get(k){let db=await openDB();return await new Promise((res,rej)=>{let q=db.transaction(OS,'readonly').objectStore(OS).get(k);q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('text read failed'))})}
function idx(){let m=j(MK,{}),x=m.source_pdf_text_level2c||m.source_pdf_text_level2d||{};return Array.isArray(x.notes)?x.notes:[]}
async function all(){let out=[];for(const n of idx()){let key=n.indexeddb_key||('source_pdf_note_text:'+n.note_id+':latest');try{let r=await get(key);if(r)out.push(r)}catch(e){}}out.sort((a,b)=>(a.order_index||0)-(b.order_index||0));return out}
function small(s,n){s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n)+'…':s}
async function verify(){let a=await all(),withText=a.filter(x=>String(x.text||'').trim()).length;return 'Level 3 Source Text Reader\nRecords: '+a.length+' / 29\nNotes with text: '+withText+' / 29\nStatus: '+(a.length===29&&withText===29?'READY':'INCOMPLETE')}
async function search(q){q=String(q||'').trim().toLowerCase();if(!q)return 'Type search words first.';let a=await all(),hits=[];for(const r of a){let t=String(r.text||''),lo=t.toLowerCase(),i=lo.indexOf(q);if(i>=0)hits.push('Order '+String(r.order_index).padStart(2,'0')+' | Note '+r.note_id+' — '+small(t.slice(Math.max(0,i-80),i+160),240))}return hits.length?('Search hits: '+hits.length+'\n\n'+hits.join('\n\n')):'No hits.'}
async function openNote(q){q=String(q||'').trim().toLowerCase();if(!q)return 'Enter note number or id. Use 00 for Note 00 or 1 for Note 01.';let a=await all(),r=null;if(/^\d+$/.test(q)){let n=parseInt(q,10);if(q.length===1)q=String(n).padStart(2,'0')}r=a.find(x=>String(x.note_id).toLowerCase()===q||String(x.note_number).toLowerCase()===q);if(!r)return 'Note not found.';return 'Note '+r.note_id+'\nFile: '+r.file_name+'\nChars: '+r.characters+'\n\n'+String(r.text||'').trim()}
function patch(d){let box=d.querySelector('[data-temp-transfer-store][data-v2="1"]')||d.querySelector('[data-temp-transfer-store]')||d.getElementById('bank');if(!box)return;let host=box.querySelector('[data-source-zip-levels-single]')||box;let p=box.querySelector('[data-source-text-reader-level3]')||d.querySelector('[data-source-text-reader-level3]');if(!p){p=d.createElement('div');p.setAttribute('data-source-text-reader-level3','');p.style.margin='8px 0 0';p.style.padding='8px';p.style.border='1px solid rgba(0,0,0,.08)';p.style.borderRadius='10px';p.innerHTML='<h4 style="margin:0 0 4px">Level 3 — Source Text Reader</h4><p class="sub">Part of Source ZIP Levels. Search and open the recovered source texts.</p><input data-l3-q placeholder="search or note number" style="width:100%;box-sizing:border-box;margin:4px 0;padding:8px;border-radius:8px"><div class="grid"><button class="mini" data-l3-verify>Verify 29/29</button><button class="mini" data-l3-search>Search Source Text</button><button class="mini" data-l3-open>Open Note</button></div><pre class="note" data-l3-out style="max-height:220px;overflow:auto;white-space:pre-wrap"></pre>'}
if(p.parentNode!==host)host.appendChild(p);let q=p.querySelector('[data-l3-q]'),out=p.querySelector('[data-l3-out]');p.querySelector('[data-l3-verify]').onclick=async()=>out.textContent=await verify();p.querySelector('[data-l3-search]').onclick=async()=>out.textContent=await search(q.value);p.querySelector('[data-l3-open]').onclick=async()=>out.textContent=await openNote(q.value);if(!out.textContent)verify().then(t=>{out.textContent=t}).catch(e=>{out.textContent='Level 3 not ready: '+e.message})}
function scan(){docs(W().document).forEach(d=>{try{patch(d)}catch(e){}})}
window.PMPSourceTextReaderLevel3V1={version:V,scan,verify,search,openNote,all};
function bind(){
  scan();
  try{
    let frame=document.getElementById('app');
    if(frame&&!frame.dataset.pmpSourceTextReaderOwnerBound){
      frame.dataset.pmpSourceTextReaderOwnerBound='1';
      frame.addEventListener('load',scan);
    }
  }catch(e){}
}
window.addEventListener('pmp:bank-owner-slot-ready',scan);
window.addEventListener('load',bind,{once:true});
bind();
})();
