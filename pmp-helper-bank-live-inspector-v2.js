(()=>{
'use strict';
const V='2.1.0-helper-only';
const TYPES=['bank','level','request','open','screen','check','other'];
const LABEL={bank:'Bank Helpers',level:'Level Helpers',request:'Request Helpers',open:'Open / Reload Helpers',screen:'Screen Helpers',check:'Check Helpers',other:'Other Helpers'};
const HELP={bank:'Bank pages, bank records, and bank buttons.',level:'Levels, Resident, source ZIP, and Continuous Run.',request:'Requests, packets, prompts, and connection material.',open:'Opening pages, reload, Route Guardian, and launcher.',screen:'Layout, visual placement, screen tabs, and styling.',check:'Tests, receipts, proof, locks, and certification.',other:'Helpers that do not clearly fit another group yet.'};
function T(){try{return top||window}catch(e){return window}}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function filename(src){try{return String(src||'').split('/').pop().split('?')[0]}catch(e){return String(src||'')}}
function cls(x){let n=String(x||'').toLowerCase();if(/connection|request|packet|prompt/.test(n))return'request';if(/level|source|resident|continuous/.test(n))return'level';if(/route|guardian|safe|reload|launcher/.test(n))return'open';if(/screen|layout|style|ui|tab/.test(n))return'screen';if(/test|verify|receipt|proof|cert/.test(n))return'check';if(/bank/.test(n))return'bank';return'other'}
function scripts(){let out=[],seen={};docs(T().document).forEach((d,i)=>{try{Array.from(d.scripts||[]).forEach(s=>{let src=s.getAttribute('src')||'';if(!src)return;let f=filename(src);if(/^pmp-helper-bank-live-inspector-v\d+\.js$/i.test(f))return;let k=i+'|'+f+'|'+src;if(seen[k])return;seen[k]=1;out.push({file:f,frame:i,type:cls(f)})})}catch(e){}});return out}
function objects(){let out=[],seen={};docs(T().document).forEach((d,i)=>{try{let w=d.defaultView||d.parentWindow||T();Object.keys(w).filter(k=>/^PMP/.test(k)&&!/^PMPHelperBankLiveInspectorV\d+/.test(k)).forEach(k=>{let id=i+'|'+k;if(seen[id])return;seen[id]=1;let v=w[k],ver='',keys=[];try{ver=v&&v.version||'';keys=v&&typeof v==='object'?Object.keys(v).slice(0,24):[]}catch(e){}out.push({name:k,version:ver,frame:i,keys,type:cls(k)})})}catch(e){}});return out}
function stored(){try{let r=T().PMPMasterBankInventoryRouterV1||window.PMPMasterBankInventoryRouterV1;if(r&&r.helpers){let h=r.helpers();return Array.isArray(h.helpers)?h.helpers.map(x=>Object.assign({type:cls(x.helper_id||'stored helper')},x)):[]}}catch(e){}return[]}
function doms(){let rows=[],count={};docs(T().document).forEach((d,i)=>{try{Array.from(d.querySelectorAll('*')).forEach(el=>{try{if(el.closest&&el.closest('[data-helper-bank-live-inspector-v2]'))return}catch(e){}Array.from(el.attributes||[]).forEach(a=>{let n=a.name;if(!/^data-/.test(n))return;if(/^(data-bank-screen-owner-v1|data-continuous-run-level-ui-scope-v1|data-cr-level|data-source-|data-level|data-resident|data-request|data-bso|data-run-bank|data-bank-|data-route|data-launcher|data-current|data-helper)/.test(n)){let k=i+'|'+n+'|'+(a.value||'');count[k]=(count[k]||0)+1}})})}catch(e){}});Object.keys(count).sort().forEach(k=>{let p=k.split('|'),frame=p[0],sel=p[1]+(p[2]?'='+p[2]:'');rows.push({selector:sel,count:count[k],frame:frame,type:cls(sel)})});return rows}
function live(){let S=scripts(),O=objects(),R=stored(),D=doms();return{version:V,scripts:S,objects:O,stored:R,dom:D,summary:{loaded_files:S.length,running_helpers:O.length,saved_helper_records:R.length,screen_helper_areas:D.length,mode:'helper inventory only'}}}
function total(t,d){return d.scripts.filter(x=>x.type===t).length+d.objects.filter(x=>x.type===t).length+d.stored.filter(x=>x.type===t).length+d.dom.filter(x=>x.type===t).length}
const W='box-sizing:border-box;max-width:100%;min-width:0;overflow-wrap:anywhere;word-break:break-word;white-space:normal;overflow:hidden';
const BOX=W+';padding:10px;border-radius:14px;border:3px solid rgba(0,0,0,.22);background:rgba(255,255,255,.72);display:grid;gap:8px';
const APPTAB=W+';width:100%;min-height:58px;padding:8px 12px;border-radius:18px;border:4px solid #000;background:#b9d8ff;color:#07111d;font-weight:900;font-size:.98em;text-align:center;box-shadow:0 6px 12px rgba(0,0,0,.12)';
const APPSEL=APPTAB+';outline:4px solid rgba(0,0,0,.18);background:#a9cef7';
const BLACK=W+';display:block;width:100%;padding:14px 16px;border-radius:16px;border:3px solid #000;background:#172235;color:#fff;font-weight:900;font-size:1.05em;text-align:center;list-style:none;box-shadow:0 6px 14px rgba(0,0,0,.16)';
function rows(arr,cols){if(!arr.length)return'<p class="sub" style="'+W+'">None here yet.</p>';return'<div style="'+W+';display:grid;gap:6px">'+arr.map(r=>'<div style="'+W+';border:1px solid rgba(0,0,0,.12);border-radius:10px;padding:8px;background:rgba(255,255,255,.5)">'+cols.map(c=>'<div><b>'+esc(c[0])+':</b> '+esc(typeof c[1]==='function'?c[1](r):r[c[1]])+'</div>').join('')+'</div>').join('')+'</div>'}
function fold(title,body){return'<details style="'+W+'"><summary style="'+BLACK+'">'+esc(title)+'</summary><div style="'+BOX+';margin-top:8px">'+body+'</div></details>'}
function detail(t,d){let R=d.stored.filter(x=>x.type===t),O=d.objects.filter(x=>x.type===t),S=d.scripts.filter(x=>x.type===t),D=d.dom.filter(x=>x.type===t);return'<div style="'+BOX+';margin-top:8px"><p class="sub" style="'+W+'">'+esc(HELP[t])+'</p>'+fold('Saved — '+R.length,rows(R,[['name','helper_id'],['bank','owning_bank'],['from','source_tab']]))+fold('Running — '+O.length,rows(O,[['name','name'],['version','version'],['tools',r=>(r.keys||[]).join(', ')]]))+fold('Loaded Files — '+S.length,rows(S,[['file','file'],['frame','frame']]))+fold('Screen Areas — '+D.length,rows(D,[['screen part','selector'],['frame','frame'],['count','count']]))+'</div>'}
function render(d,sel){sel=sel||'';let stack=TYPES.map(t=>'<div style="'+W+';display:grid;gap:8px"><button type="button" data-helper-tab="'+t+'" style="'+(t===sel?APPSEL:APPTAB)+'"><span style="display:block">'+esc(LABEL[t])+' — '+total(t,d)+'</span></button>'+(t===sel?detail(t,d):'')+'</div>').join('');return'<div data-helper-bank-live-inspector-v2 data-helper-selected="'+esc(sel)+'" style="'+W+';display:grid;gap:10px;margin-top:10px"><section style="'+BOX+'"><h2 style="margin:0">Live Helper Bank Inspector</h2><p class="sub" style="'+W+'">Helper Bank shows helper inventory only. Bug information lives in Bug Bank.</p><pre class="note" style="max-width:100%;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word">'+esc(JSON.stringify(d.summary,null,2))+'</pre><div class="grid"><button class="mini" data-helper-bank-refresh>Refresh Live Helper Map</button><button class="mini" data-helper-bank-copy>Copy Live Helper Map</button></div></section><section style="'+W+';display:grid;gap:12px">'+stack+'</section></div>'}
function bind(h,doc){Array.from(h.querySelectorAll('[data-helper-tab]')).forEach(b=>b.onclick=e=>{e&&e.preventDefault();let current=h.getAttribute('data-helper-selected')||'',clicked=b.getAttribute('data-helper-tab')||'',sel=current===clicked?'':clicked;h.outerHTML=render(live(),sel);let n=doc.querySelector('[data-helper-bank-live-inspector-v2]');if(n)bind(n,doc)});let ref=h.querySelector('[data-helper-bank-refresh]'),copy=h.querySelector('[data-helper-bank-copy]');if(ref)ref.onclick=e=>{e&&e.preventDefault();let sel=h.getAttribute('data-helper-selected')||'';h.outerHTML=render(live(),sel);let n=doc.querySelector('[data-helper-bank-live-inspector-v2]');if(n)bind(n,doc)};if(copy)copy.onclick=async e=>{e&&e.preventDefault();try{await navigator.clipboard.writeText(JSON.stringify(live(),null,2));copy.textContent='Copied'}catch(x){}}}
function renderInto(doc){
  try{
    let bank=doc&&doc.getElementById&&doc.getElementById('bank');
    if(!bank)return{status:'bank_unavailable'};
    let title=(bank.querySelector('[data-bank-detail-title]')||{}).textContent||'';
    if(clean(title)!=='Helper Bank')return{status:'not_helper_bank'};
    let pre=bank.querySelector('[data-bank-helper]');
    if(!pre)return{status:'owner_slot_unavailable'};
    pre.style.display='none';
    let h=bank.querySelector('[data-helper-bank-live-inspector-v2]');
    if(!h){
      let div=doc.createElement('div');
      div.innerHTML=render(live(),'');
      pre.insertAdjacentElement('afterend',div.firstElementChild);
      h=bank.querySelector('[data-helper-bank-live-inspector-v2]');
    }
    if(h)bind(h,doc);
    return{status:'rendered_by_bank_owner_request'};
  }catch(error){return{status:'render_failed',error:String(error&&error.message||error)}}
}
window.PMPHelperBankLiveInspectorV2={
  version:V,
  owner:'bank_screen_owner',
  role:'read_only_inventory_provider_and_owner_requested_presenter',
  live,
  renderInto,
  rule:'Never scans, hides, replaces, mounts, or repaints unless the Bank owner explicitly supplies its document.'
};
})();
