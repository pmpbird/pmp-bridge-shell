(()=>{
'use strict';
const V='1.0.0-save-delete-copy-returned-packet';
const STORE_KEY='pmp.chatMemoryVault.v1';
function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function readStore(w){try{return JSON.parse(w.localStorage.getItem(STORE_KEY)||'{}')||{}}catch(e){return {}}}
function writeStore(w,s){try{w.localStorage.setItem(STORE_KEY,JSON.stringify(s));return true}catch(e){return false}}
function cleanJsonText(t){t=String(t||'').trim();if(t.startsWith('```')){t=t.replace(/^```[a-zA-Z0-9_-]*\s*/,'').replace(/```$/,'').trim()}return t}
function parsePacket(t){const raw=cleanJsonText(t);const obj=JSON.parse(raw);if(!obj||typeof obj!=='object')throw new Error('Returned packet is not a JSON object.');const id=String(obj.project_state_id||obj?.search_surface?.primary_lookup_key||'').trim();if(!id)throw new Error('Missing project_state_id.');return {id,obj,raw}}
function latestRecord(store,id){const list=store[id]||[];return list[list.length-1]||null}
function packetSummary(obj){const id=obj.project_state_id||'';const name=obj.project_name||obj?.source_identity_capture?.source_project_name_if_known||'';const kind=obj.project_kind||'';const level=obj?.quality_truth?.quality_level||'UNKNOWN';return {id,name,kind,level}}
function futureText(rec){const obj=rec.parsed||{};const s=packetSummary(obj);return [
'PMP FUTURE CHAT READBACK PACKET',
'',
'Instruction: Read this stored PMP memory packet before continuing. Continue from the packet. Do not guess missing history. Treat it as candidate outside-source memory unless receiver_safe_handoff says otherwise.',
'',
'project_state_id: '+(s.id||rec.project_state_id||''),
'project_name: '+(s.name||''),
'project_kind: '+(s.kind||''),
'quality_level: '+(s.level||'UNKNOWN'),
'',
'Use order:',
'1. source_identity_capture',
'2. transfer_body_capture',
'3. memory_deposit_layer.full_memory_recovery',
'4. packet_tracks',
'5. quality_truth',
'6. search_surface',
'7. receiver_safe_handoff',
'8. next_move',
'',
'Stored packet JSON:',
JSON.stringify(obj,null,2)
].join('\n')}
async function copyText(w,text){try{await w.navigator.clipboard.writeText(text);return true}catch(e){try{const ta=w.document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';w.document.body.appendChild(ta);ta.focus();ta.select();const ok=w.document.execCommand('copy');ta.remove();return ok}catch(x){return false}}}
function status(d,msg){const out=d.getElementById('connOut');if(out)out.textContent=msg;}
function setBox(d,text){const box=d.getElementById('connBox');if(box){box.value=text;box.dispatchEvent(new Event('input',{bubbles:true}));}}
function refreshSelect(w,d,sel){const store=readStore(w);const ids=Object.keys(store).sort();const current=sel.value;sel.innerHTML='';const blank=d.createElement('option');blank.value='';blank.textContent=ids.length?'Saved packets':'No saved packets';sel.appendChild(blank);ids.forEach(id=>{const rec=latestRecord(store,id);const o=d.createElement('option');o.value=id;const count=(store[id]||[]).length;const name=rec&&rec.parsed&&(rec.parsed.project_name||rec.parsed?.source_identity_capture?.source_project_name_if_known)||'';o.textContent=id+(name?' — '+name:'')+(count>1?' ('+count+' versions)':'');sel.appendChild(o)});if(ids.includes(current))sel.value=current;}
function buildPanel(w,d,box){if(d.getElementById('pmpChatMemoryVaultControls'))return;const wrap=d.createElement('div');wrap.id='pmpChatMemoryVaultControls';wrap.style.cssText='margin:10px 0;padding:10px;border:1px solid rgba(0,0,0,.18);border-radius:12px;background:rgba(255,255,255,.55);font:13px system-ui,-apple-system,BlinkMacSystemFont,sans-serif;color:#1f1b18;';const title=d.createElement('div');title.textContent='Chat Memory Vault';title.style.cssText='font-weight:700;margin-bottom:8px;';const row=d.createElement('div');row.style.cssText='display:flex;gap:8px;flex-wrap:wrap;align-items:center;';const sel=d.createElement('select');sel.id='pmpMemoryVaultSelect';sel.style.cssText='max-width:100%;flex:1 1 190px;padding:8px;border-radius:9px;border:1px solid rgba(0,0,0,.2);background:#fff;';const btnSave=d.createElement('button');btnSave.type='button';btnSave.textContent='Save Returned Packet';const btnCopy=d.createElement('button');btnCopy.type='button';btnCopy.textContent='Copy for Future Chat';const btnDelete=d.createElement('button');btnDelete.type='button';btnDelete.textContent='Delete Returned Packet';[btnSave,btnCopy,btnDelete].forEach(b=>{b.style.cssText='padding:8px 10px;border-radius:9px;border:1px solid rgba(0,0,0,.2);background:#fff;'});row.append(sel,btnSave,btnCopy,btnDelete);wrap.append(title,row);box.parentNode.insertBefore(wrap,box);
function selectedRecord(){const store=readStore(w);const id=sel.value;return id?latestRecord(store,id):null}
btnSave.onclick=()=>{try{const p=parsePacket(box.value);const store=readStore(w);const rec={project_state_id:p.id,saved_at:new Date().toISOString(),raw:p.raw,parsed:p.obj,official_status:p.obj?.memory_deposit_layer?.pmp_storage_instruction?.official_status||'candidate_only'};store[p.id]=store[p.id]||[];store[p.id].push(rec);if(writeStore(w,store)){refreshSelect(w,d,sel);sel.value=p.id;status(d,'Saved returned packet under '+p.id+'.');}else status(d,'Could not save packet. Browser storage may be blocked.')}catch(e){status(d,'Save failed: '+e.message)}};
btnCopy.onclick=async()=>{let rec=selectedRecord();if(!rec){try{const p=parsePacket(box.value);rec={project_state_id:p.id,raw:p.raw,parsed:p.obj,saved_at:new Date().toISOString()}}catch(e){status(d,'Copy failed: choose a saved packet or paste valid returned JSON.');return}}const text=futureText(rec);const ok=await copyText(w,text);setBox(d,text);status(d,ok?'Copied future-chat packet.':'Prepared future-chat packet in box; copy manually if needed.');};
btnDelete.onclick=()=>{const id=sel.value;if(!id){status(d,'Choose a saved packet to delete.');return}const store=readStore(w);if(!store[id]){status(d,'Saved packet not found.');refreshSelect(w,d,sel);return}delete store[id];if(writeStore(w,store)){refreshSelect(w,d,sel);status(d,'Deleted returned packet '+id+'.')}else status(d,'Delete failed. Browser storage may be blocked.');};
refreshSelect(w,d,sel);
}
function patchWindow(w,d){if(!w||!d||!d.getElementById)return;const box=d.getElementById('connBox');if(!box)return;buildPanel(w,d,box)}
function scan(){docs(document).forEach(d=>{try{patchWindow(d.defaultView,d)}catch(e){}})}
window.PMPConnectionsMemoryVaultV1={version:V,scan};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
window.addEventListener('load',()=>[50,150,400,900,1800].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);
})();
