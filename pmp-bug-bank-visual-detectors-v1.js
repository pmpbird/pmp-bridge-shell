(()=>{
'use strict';
const V='1.0.0-cross-bank-and-level-wrap';
const KNOWN='pmp_bug_bank_known_types_v1',EVID='pmp_bug_bank_symptom_evidence_v1',ACTIVE='pmp_bug_bank_active_bugs_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function load(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function mergeKey(x){return String(x.signature||x.id||x.type||x.kind||JSON.stringify(x).slice(0,120))}
function add(k,row,limit){let a=load(k,[]);if(!Array.isArray(a))a=[];let key=mergeKey(row),hit=a.find(x=>mergeKey(x)===key);if(hit){Object.assign(hit,row,{last_seen:new Date().toISOString(),seen:Number(hit.seen||1)+1})}else a.push(Object.assign({created_at:new Date().toISOString(),seen:1},row));save(k,a.slice(-(limit||80)))}
function record(type,where,how,detail,active){let row={id:'visual_'+type.toLowerCase().replace(/[^a-z0-9]+/g,'_'),type,where,where_seen:where,how_it_happens:how,severity:'high',signature:type+'|'+where,fix_rule:'Enforce bank owner boundaries and keep display owner scoped to the selected bank only.',detail,last_seen:new Date().toISOString(),bug_bank_section:'Known Bug Types'};add(KNOWN,row,80);add(EVID,Object.assign({},row,{bug_bank_section:'Symptom Evidence',evidence_source:'visual detector'}),80);if(active)add(ACTIVE,Object.assign({},row,{bug_bank_section:'Active Bugs Found'}),40)}
function bankTitle(d){let b=d.getElementById('bank');return b?clean((b.querySelector('[data-bank-detail-title]')||{}).textContent||''):''}
function detectCrossBank(d){let b=d.getElementById('bank');if(!b)return;let title=bankTitle(d);let bug=b.querySelector('[data-bug-bank-owner-v1]');let helper=b.querySelector('[data-helper-bank-live-inspector-v2]');if(bug&&title!=='Bug Bank'){record('Cross-Bank Bug Bank Surface Leak','Bank / '+(title||'unknown bank'),'Bug Bank UI rendered while a different bank was selected.',{selected_bank:title},true);bug.remove()}if(helper&&title!=='Helper Bank'){record('Cross-Bank Helper Surface Leak','Bank / '+(title||'unknown bank'),'Helper Bank UI rendered while a different bank was selected.',{selected_bank:title},true);helper.remove()}}
function isLevelText(el){let t=clean(el.textContent||'');return /^Level\s+(?:[0-9]+[A-Z]?|30B)\s*[:—-]/i.test(t)}
function isWrapped(el){try{let cs=(el.ownerDocument.defaultView||window).getComputedStyle(el);let lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2||20;return el.getBoundingClientRect().height>lh*1.55}catch(e){return false}}
function detectLevelWrap(d){let b=d.getElementById('bank');if(!b||bankTitle(d)!=='Continuous Run Bank')return;let wrapped=[];Array.from(b.querySelectorAll('h1,h2,h3,h4,p,b,strong')).forEach(el=>{try{if(isLevelText(el)&&isWrapped(el))wrapped.push(clean(el.textContent).slice(0,120))}catch(e){}});if(wrapped.length)record('Continuous Run Level Card Wrap Drift','Continuous Run Bank','Level card text wrapped into multiple lines after the single-line card layout was expected to stay stable.',{wrapped},true)}
function scan(){docs(T().document).forEach(d=>{detectCrossBank(d);detectLevelWrap(d)});try{localStorage.setItem('pmp_bug_bank_visual_detectors_v1_receipt',JSON.stringify({type:'PMP_BUG_BANK_VISUAL_DETECTORS_V1',version:V,at:new Date().toISOString(),rule:'Bug Bank now watches cross-bank surface leaks and Continuous Run level wrap drift.'}))}catch(e){}}
window.PMPBugBankVisualDetectorsV1={version:V,scan};
try{let mo=new MutationObserver(()=>setTimeout(scan,60));mo.observe(document.documentElement,{childList:true,subtree:true,characterData:true})}catch(e){}
window.addEventListener('load',()=>[100,300,800,1600,3200,6000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();