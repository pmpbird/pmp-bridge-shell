(()=>{
'use strict';
const V='1.0.0-diagnostics-writer-trace-20260730L';
const KEY='pmp_diagnostics_writer_trace_v1';
const SCREEN_ID='pmpDiagnosticsScreenV1';
const BUTTON_ID='pmpDiagnosticsWriterTraceCopyV1';
const MAX=240;
const patched=new WeakSet();
const observed=new WeakSet();
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function pathOf(w){try{return String(w.location&&w.location.pathname||'')}catch(_){return 'inaccessible'}}
function read(){try{return JSON.parse(T().localStorage.getItem(KEY)||'[]')}catch(_){return []}}
function write(rows){try{T().localStorage.setItem(KEY,JSON.stringify(rows.slice(-MAX),null,2))}catch(_){}return rows}
function classify(html){const s=String(html||'');if(s.includes('Running current live diagnostics'))return'WHOLE_APP_RUNNING';if(s.includes('Whole App Health'))return'WHOLE_APP_HEALTH';if(s.includes('data-diag-consolidated="whole_app"'))return'DIAGNOSTICS_HOME_CONSOLIDATED';if(s.includes('App Health Summary'))return'DIAGNOSTICS_HOME_OWNER';if(s.includes('pmpDiagHealthRowV1'))return'WHOLE_APP_HEALTH_ROWS';return'OTHER'}
function record(w,operation,target,value,extra){const rows=read();rows.push({type:'PMP_DIAGNOSTICS_WRITER_TRACE_EVENT_V1',version:V,at:now(),performance_ms:(()=>{try{return Number(w.performance.now().toFixed(3))}catch(_){return null}})(),frame_path:pathOf(w),operation,target_id:target&&target.id||null,target_class:target&&target.className||null,classification:classify(value),value_length:String(value==null?'':value).length,stack:String(new Error('DIAGNOSTICS_WRITE_TRACE').stack||'').split('\n').slice(1,14),extra:extra||null});write(rows)}
function patchWindow(w){if(!w||patched.has(w))return;try{
  const proto=w.Element&&w.Element.prototype;
  if(!proto)return;
  const desc=Object.getOwnPropertyDescriptor(proto,'innerHTML');
  if(desc&&desc.get&&desc.set&&!proto.__pmpDiagnosticsTraceInnerHTML){
    Object.defineProperty(proto,'innerHTML',{configurable:desc.configurable,enumerable:desc.enumerable,get:desc.get,set:function(value){if(this&&this.id===SCREEN_ID)record(w,'innerHTML_set',this,value);return desc.set.call(this,value)}});
    Object.defineProperty(proto,'__pmpDiagnosticsTraceInnerHTML',{value:true,configurable:true});
  }
  const originalReplace=proto.replaceChildren;
  if(originalReplace&&!proto.__pmpDiagnosticsTraceReplaceChildren){proto.replaceChildren=function(...nodes){if(this&&this.id===SCREEN_ID)record(w,'replaceChildren',this,nodes.map(n=>n&&n.outerHTML||n&&n.textContent||String(n)).join(''));return originalReplace.apply(this,nodes)};Object.defineProperty(proto,'__pmpDiagnosticsTraceReplaceChildren',{value:true,configurable:true})}
  const originalInsert=proto.insertAdjacentHTML;
  if(originalInsert&&!proto.__pmpDiagnosticsTraceInsertAdjacentHTML){proto.insertAdjacentHTML=function(position,text){if(this&&this.id===SCREEN_ID)record(w,'insertAdjacentHTML',this,text,{position});return originalInsert.call(this,position,text)};Object.defineProperty(proto,'__pmpDiagnosticsTraceInsertAdjacentHTML',{value:true,configurable:true})}
  patched.add(w);
}catch(error){record(window,'patch_error',null,'',{error:String(error&&error.message||error),frame_path:pathOf(w)})}}
function observeDocument(w){let d;try{d=w.document}catch(_){return}if(!d||observed.has(d))return;observed.add(d);try{const observer=new w.MutationObserver(records=>{for(const r of records){const target=r.target&&r.target.nodeType===1?r.target:r.target&&r.target.parentElement;if(target&&(target.id===SCREEN_ID||target.closest&&target.closest('#'+SCREEN_ID))){const screen=d.getElementById(SCREEN_ID);record(w,'mutation_observer',screen,screen&&screen.innerHTML||'',{mutation_type:r.type,added_nodes:r.addedNodes&&r.addedNodes.length||0,removed_nodes:r.removedNodes&&r.removedNodes.length||0});break}}});observer.observe(d.documentElement||d,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']})}catch(error){record(w,'observer_error',null,'',{error:String(error&&error.message||error)})}}
function walk(w,depth,seen){if(!w||depth>10||seen.includes(w))return;seen.push(w);patchWindow(w);observeDocument(w);try{w.document.querySelectorAll('iframe,frame').forEach(f=>{try{walk(f.contentWindow,depth+1,seen)}catch(_){}})}catch(_){}}
function installAll(){walk(T(),0,[]);installButton()}
async function copy(){const report={type:'PMP_DIAGNOSTICS_WRITER_TRACE_REPORT_V1',version:V,generated_at:now(),events:read(),boundaries:{read_only:true,no_navigation_change:true,no_owner_or_helper_change:true,no_route_change:true,no_storage_migration:true}};const text=JSON.stringify(report,null,2);try{await navigator.clipboard.writeText(text);return true}catch(_){}try{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok}catch(_){return false}}
function installButton(){let d;try{d=T().document}catch(_){d=document}if(!d||d.getElementById(BUTTON_ID))return;const b=d.createElement('button');b.id=BUTTON_ID;b.type='button';b.textContent='Copy Writer Trace';b.style.cssText='position:fixed;right:10px;top:calc(env(safe-area-inset-top,0px) + 10px);z-index:2147483647;padding:8px 10px;border:2px solid #07101c;border-radius:12px;background:#fff3de;color:#07101c;font:700 12px/1.1 system-ui;display:none';b.onclick=async()=>{b.textContent=await copy()?'Trace Copied':'Copy Failed';setTimeout(()=>b.textContent='Copy Writer Trace',1500)};(d.body||d.documentElement).appendChild(b);const sync=()=>{let visible=false;try{for(const w of [T(),window]){const s=w.document&&w.document.getElementById(SCREEN_ID);if(s&&s.classList.contains('on'))visible=true}}catch(_){}b.style.display=visible?'block':'none'};setInterval(sync,150);sync()}
const api={version:V,install:installAll,events:read,clear:()=>write([]),copy,report:()=>({type:'PMP_DIAGNOSTICS_WRITER_TRACE_REPORT_V1',version:V,generated_at:now(),events:read()}),rule:'Read-only trace of writes to the Diagnostics screen. It does not prevent, replace, navigate, or repair any writer.'};
window.PMPDiagnosticsWriterTraceV1=api;try{T().PMPDiagnosticsWriterTraceV1=api}catch(_){}
write([]);installAll();[100,300,800,1600,3000,6000,10000,15000].forEach(ms=>setTimeout(installAll,ms));window.addEventListener('pageshow',installAll);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')installAll()});
})();