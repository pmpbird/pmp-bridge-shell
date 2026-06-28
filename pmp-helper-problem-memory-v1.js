(()=>{
'use strict';
const V='1.1.0-auto-problem-memory';
const KEY='pmp_helper_problem_memory_v1';
const ACTIVE='pmp_helper_problem_memory_active_v1';
let baseLive=null,lastSnap=null,lastUserAt=0,lastLearnAt=0;
function T(){try{return top||window}catch(e){return window}}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]').filter(Boolean)}catch(e){return[]}}
function save(x){try{localStorage.setItem(KEY,JSON.stringify((x||[]).slice(-80)))}catch(e){}}
function activeLoad(){try{return JSON.parse(localStorage.getItem(ACTIVE)||'[]').filter(Boolean)}catch(e){return[]}}
function activeSave(x){try{localStorage.setItem(ACTIVE,JSON.stringify((x||[]).slice(-30)))}catch(e){}}
function now(){return Date.now()}
function markUser(){lastUserAt=now()}
['click','touchstart','keydown','input','change','pointerdown'].forEach(ev=>{try{T().document.addEventListener(ev,markUser,true)}catch(e){}});
function rawLive(){try{if(!baseLive){let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;baseLive=api&&api.live}if(baseLive)return baseLive()}catch(e){}return{summary:{},scripts:[],objects:[],dom:[],problems:[],checks:[]}}
function names(a,k){return(a||[]).map(x=>x&&x[k]).filter(Boolean)}
function textHash(s){let h=0;String(s||'').slice(0,4000).split('').forEach(ch=>{h=((h<<5)-h)+ch.charCodeAt(0);h|=0});return String(h)}
function metrics(){let m={height:0,width:0,overflow:0,blank_buttons:0,visible_buttons:0,levelish:0,text_hash:'0'};let txt='';docs(T().document).forEach(doc=>{try{let bank=doc.getElementById('bank');if(!bank)return;let r=bank.getBoundingClientRect();m.height=Math.max(m.height,Math.round(r.height||0));m.width=Math.max(m.width,Math.round(r.width||0));txt+=' '+clean(bank.innerText||'').slice(0,3500);Array.from(bank.querySelectorAll('*')).forEach(el=>{try{if(el.closest&&el.closest('[data-helper-bank-live-inspector-v2],[data-helper-problem-memory-v1]'))return;let cs=getComputedStyle(el),rr=el.getBoundingClientRect();let vis=cs.display!=='none'&&cs.visibility!=='hidden'&&rr.width>0&&rr.height>0;if(!vis)return;if(el.scrollWidth>el.clientWidth+8)m.overflow++;let attrs=[].slice.call(el.attributes||[]).map(a=>a.name+'='+a.value).join(' ');if(/data-(cr-level|source-|level\d|resident-l30b|level30)/i.test(attrs))m.levelish++;}catch(e){}});Array.from(bank.querySelectorAll('button')).forEach(b=>{try{if(b.closest&&b.closest('[data-helper-bank-live-inspector-v2],[data-helper-problem-memory-v1]'))return;let cs=getComputedStyle(b),rr=b.getBoundingClientRect();let vis=cs.display!=='none'&&cs.visibility!=='hidden'&&rr.width>0&&rr.height>0;if(vis){m.visible_buttons++;if(!clean(b.textContent))m.blank_buttons++}}catch(e){}})}catch(e){}});m.text_hash=textHash(txt);return m}
function snap(){let d=rawLive(),m=metrics();return{at:new Date().toISOString(),t:now(),summary:d.summary||{},files:names(d.scripts,'file'),objects:names(d.objects,'name'),dom:names(d.dom,'selector'),problems:(d.problems||[]).map(x=>x.problem||x.check).filter(Boolean),checks:(d.checks||[]).filter(x=>x.status==='PROBLEM').map(x=>x.check).filter(Boolean),metrics:m}}
function sig(kind,where){return kind+'|'+where}
function symptom(kind,where,why,severity,before,after){return{kind,where,why,severity:severity||'medium',signature:sig(kind,where),before:before||{},after:after||{},at:new Date().toISOString()}}
function diff(a,b){let out=[];if(!a||!b)return out;let quiet=now()-lastUserAt>2200;let am=a.metrics||{},bm=b.metrics||{};let as=a.summary||{},bs=b.summary||{};if(quiet&&Math.abs((bm.height||0)-(am.height||0))>180)out.push(symptom('Auto-detected screen height jump','Bank screen','The Bank screen changed height without a recent tap/input.', 'medium',am,bm));
if(quiet&&Math.abs((bm.levelish||0)-(am.levelish||0))>=2)out.push(symptom('Auto-detected level/card count changed','Continuous Run Bank','The number of visible level-like cards changed without a recent tap/input.', 'high',am,bm));
if(quiet&&Math.abs((bs.screen_areas||0)-(as.screen_areas||0))>=3)out.push(symptom('Auto-detected screen-owner count drift','Helper screen map','The helper screen-area count changed without a recent tap/input.', 'high',as,bs));
if(quiet&&Math.abs((bs.running||0)-(as.running||0))>=2)out.push(symptom('Auto-detected running-helper count drift','Running helpers','The number of running helpers changed without a recent tap/input.', 'medium',as,bs));
if((bm.overflow||0)>0)out.push(symptom('Auto-detected overflow/clipping','Bank screen','A visible screen part is wider than its box.', 'medium',{},bm));
if((bm.blank_buttons||0)>0)out.push(symptom('Auto-detected blank button','Bank screen','A visible button has no label.', 'medium',{},bm));
if(quiet&&am.text_hash&&bm.text_hash&&am.text_hash!==bm.text_hash&&Math.abs((bm.height||0)-(am.height||0))>50)out.push(symptom('Auto-detected screen rebuilt itself','Bank screen','Visible Bank text/layout changed without a recent tap/input.', 'medium',am,bm));
return out}
function learn(sym){let list=load();let existing=list.find(x=>x.signature===sym.signature);if(existing){existing.last_seen=sym.at;existing.seen=(existing.seen||1)+1;existing.after=sym.after;save(list);return existing}
let mem={id:'auto_'+now(),auto:true,name:sym.kind,happened:sym.why,signature:sym.signature,where:sym.where,severity:sym.severity,created_at:sym.at,last_seen:sym.at,seen:1,before:sym.before,after:sym.after};list.push(mem);save(list);return mem}
function detectLearned(s){return load().map(m=>{let match=false,why='';let mm=s.metrics||{},ss=s.summary||{};if(/^Auto-detected overflow/.test(m.name)&&mm.overflow>0){match=true;why='overflow is visible again'}
else if(/^Auto-detected blank button/.test(m.name)&&mm.blank_buttons>0){match=true;why='blank button is visible again'}
else if(/^Auto-detected level\/card count/.test(m.name)&&m.after&&Math.abs((mm.levelish||0)-(m.after.levelish||0))>=2){match=true;why='level/card count moved near a learned bad pattern'}
else if(/^Auto-detected screen-owner/.test(m.name)&&m.after&&Math.abs((ss.screen_areas||0)-(m.after.screen_areas||0))>=3){match=true;why='screen-owner count drift matches a learned problem'}
return Object.assign({},m,{match,why})}).filter(x=>x.match)}
function tick(){let s=snap();let syms=diff(lastSnap,s);lastSnap=s;if(syms.length&&now()-lastLearnAt>2000){lastLearnAt=now();syms.forEach(learn)}let learned=detectLearned(s);let active=syms.concat(learned.map(x=>symptom('Learned problem detected: '+x.name,x.where||'learned memory',x.why||x.happened,x.severity||'medium',{},x.after||{})));activeSave(active);return active}
function patchInspector(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||api.__problemMemoryPatched||!api.live)return;let original=api.live.bind(api);baseLive=original;api.live=function(){let d=original();let active=activeLoad();if(active.length){d.problems=(d.problems||[]).concat(active.map(x=>({problem:x.kind,severity:x.severity||'medium',where:x.where,count:1,why:x.why})));d.checks=(d.checks||[]).concat(active.map(x=>({check:'Auto Problem Memory: '+x.kind,status:'PROBLEM',severity:x.severity||'medium',where:x.where,count:1,why:x.why})));d.summary=d.summary||{};d.summary.problems=(d.problems||[]).length;d.summary.auto_learned_problems=active.length}d.summary=d.summary||{};d.summary.learned_problem_patterns=load().length;return d};api.__problemMemoryPatched=true}catch(e){}}
const W='box-sizing:border-box;max-width:100%;min-width:0;overflow-wrap:anywhere;word-break:break-word;white-space:normal;overflow:hidden';
const BOX=W+';padding:10px;border-radius:14px;border:3px solid rgba(0,0,0,.22);background:rgba(255,255,255,.72);display:grid;gap:8px';
function render(){let active=activeLoad(),list=load();return'<div data-helper-problem-memory-v1 style="'+W+';display:grid;gap:10px;margin-top:10px"><section style="'+BOX+'"><h2 style="margin:0">Auto Problem Memory</h2><p class="sub" style="'+W+'">No typing needed. The app watches for unknown symptoms, remembers the pattern, and sends matching problems into Problems Found.</p><p class="sub" style="'+W+'">Active auto problems: '+active.length+' / Learned patterns: '+list.length+'</p></section></div>'}
function bind(host,doc){}
function install(doc,force){try{let bank=doc.getElementById('bank');if(!bank)return;let title=(bank.querySelector('[data-bank-detail-title]')||{}).textContent||'';if(clean(title)!=='Helper Bank')return;let anchor=bank.querySelector('[data-helper-bank-live-inspector-v2]')||bank.querySelector('[data-bank-helper]');if(!anchor)return;let host=bank.querySelector('[data-helper-problem-memory-v1]');if(host&&!force)return;if(!host){let div=doc.createElement('div');div.innerHTML=render();anchor.insertAdjacentElement('beforebegin',div.firstElementChild)}else host.outerHTML=render()}catch(e){}}
function scan(){patchInspector();tick();docs(T().document).forEach(d=>install(d,true))}
window.PMPHelperProblemMemoryV1={version:V,scan,snapshot:snap,learned:load,active:activeLoad,forget:()=>{save([]);activeSave([])}};
window.addEventListener('load',()=>[700,1600,3000,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,2500);scan();
})();