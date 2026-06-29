(()=>{
'use strict';
const V='1.3.4-no-auto-dom-move';
const MK='pmp_continuous_run_bank_transfer_store_manifest_v1';
const DB='pmp_continuous_run_bank_source_pdf_text_db_v1';
const OS='texts';
function W(){try{return window.top||window}catch(e){return window}}
function j(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function openDB(){return new Promise((res,rej)=>{try{let q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{try{q.result.createObjectStore(OS)}catch(e){}};q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('text DB open failed'))}catch(e){rej(e)}})}
async function get(k){let db=await openDB();return await new Promise((res,rej)=>{let q=db.transaction(OS,'readonly').objectStore(OS).get(k);q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error||Error('text read failed'))})}
function idx(){let m=j(MK,{}),x=m.source_pdf_text_level2c||m.source_pdf_text_level2d||{};return Array.isArray(x.notes)?x.notes:[]}
async function all(){let out=[];for(const n of idx()){let key=n.indexeddb_key||('source_pdf_note_text:'+n.note_id+':latest');try{let r=await get(key);if(r)out.push(r)}catch(e){}}out.sort((a,b)=>(a.order_index||0)-(b.order_index||0));return out}
function small(s,n){s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n)+'…':s}
async function verify(){let a=await all(),withText=a.filter(x=>String(x.text||'').trim()).length;return 'Level 3 Source Text Reader\nRecords: '+a.length+' / 29\nNotes with text: '+withText+' / 29\nStatus: '+(a.length===29&&withText===29?'READY':'INCOMPLETE')}
async function search(q){q=String(q||'').trim().toLowerCase();if(!q)return 'Type search words first.';let a=await all(),hits=[];for(const r of a){let t=String(r.text||''),lo=t.toLowerCase(),i=lo.indexOf(q);if(i>=0)hits.push('Order '+String(r.order_index).padStart(2,'0')+' | Note '+r.note_id+' — '+small(t.slice(Math.max(0,i-80),i+160),240))}return hits.length?('Search hits: '+hits.length+'\n\n'+hits.join('\n\n')):'No hits.'}
async function openNote(q){q=String(q||'').trim().toLowerCase();if(!q)return 'Enter note number or id. Use 00 for Note 00 or 1 for Note 01.';let a=await all(),r=null;if(/^\d+$/.test(q)){let n=parseInt(q,10);if(q.length===1)q=String(n).padStart(2,'0')}r=a.find(x=>String(x.note_id).toLowerCase()===q||String(x.note_number).toLowerCase()===q);if(!r)return 'Note not found.';return 'Note '+r.note_id+'\nFile: '+r.file_name+'\nChars: '+r.characters+'\n\n'+String(r.text||'').trim()}
function scan(){try{localStorage.setItem('pmp_source_text_reader_level3_v1_receipt',JSON.stringify({type:'PMP_SOURCE_TEXT_READER_LEVEL3_V1',version:V,at:new Date().toISOString(),status:'api_only_no_auto_dom_move',rule:'Level 3 no longer auto-creates, appends, or reparents DOM panels. A single layout owner must render it.'}))}catch(e){}}
window.PMPSourceTextReaderLevel3V1={version:V,scan,verify,search,openNote,all,dom_auto_move:false};
window.addEventListener('load',scan);
scan();
})();