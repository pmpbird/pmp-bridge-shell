(()=>{
'use strict';
const V='1.0.2-active-until-verified-clean';
const KNOWN='pmp_bug_bank_known_types_v1',EVID='pmp_bug_bank_symptom_evidence_v1',ACTIVE='pmp_bug_bank_active_bugs_v1';
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function load(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function compactDetail(x){try{return norm(JSON.stringify(x.detail||x.raw_source||{}).slice(0,260))}catch(e){return''}}
function key(x){return [norm(x.type||x.kind||x.problem),norm(x.where||x.where_seen),norm(x.how_it_happens||x.why||x.symptom),norm(x.fix_rule),compactDetail(x)].join('|')||norm(JSON.stringify(x).slice(0,220))}
function unique(list){let seen={},out=[];(Array.isArray(list)?list:[]).filter(Boolean).forEach(x=>{let k=key(x);if(seen[k])Object.assign(seen[k],x,{seen:Math.max(Number(seen[k].seen||1),Number(x.seen||1)),last_seen:x.last_seen||seen[k].last_seen});else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function bankTitle(d){let b=d.getElementById('bank');return b?clean((b.querySelector('[data-bank-detail-title]')||{}).textContent||''):''}
function isContinuousBank(d,b){let title=bankTitle(d);let t=clean((b||{}).textContent||'').slice(0,4000);return title==='Continuous Run Bank'||/Lossless Slots ZIP Import|Continuous Run Levels|Level\s+30B|Level\s+29/i.test(t)}
function isLevelText(el){return /^Level\s+(?:[0-9]+[A-Z]?|30B)\s*[:—-]/i.test(clean(el.textContent||''))}
function wrapped(el){try{let cs=(el.ownerDocument.defaultView||window).getComputedStyle(el);let lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2||20;let r=el.getBoundingClientRect();let ws=cs.whiteSpace||'';return r.height>lh*1.45||!/nowrap/i.test(ws)}catch(e){return false}}
function baseRow(type,where,detail){return{type,where,where_seen:where,signature:type+'|'+where,detail:detail||{},bug_bank_section:'Active Bugs Found',severity:'high',how_it_happens:'A visible bank layout or ownership problem was observed and has not yet been verified clean in its owning bank.',fix_rule:'Reopen the owning bank after the fix. Keep active until that same surface verifies clean.',last_seen:new Date().toISOString(),source:'current-active-cleaner'}}
function currentAndPasses(){let current=[],passes=[];docs(T().document).forEach(d=>{let b=d.getElementById('bank');if(!b)return;let title=bankTitle(d)||'unknown bank';let bug=b.querySelector('[data-bug-bank-owner-v1]');let helper=b.querySelector('[data-helper-bank-live-inspector-v2]');let bugWhere='Bank / '+title,helperWhere='Bank / '+title;if(title!=='Bug Bank'){if(bug)current.push(baseRow('Cross-Bank Bug Bank Surface Leak',bugWhere,{selected_bank:title}));else passes.push({type:'Cross-Bank Bug Bank Surface Leak',where:bugWhere})}
if(title!=='Helper Bank'){if(helper)current.push(baseRow('Cross-Bank Helper Surface Leak',helperWhere,{selected_bank:title}));else passes.push({type:'Cross-Bank Helper Surface Leak',where:helperWhere})}
if(isContinuousBank(d,b)){let bad=[];Array.from(b.querySelectorAll('*')).forEach(el=>{try{if(isLevelText(el)&&wrapped(el))bad.push(clean(el.textContent).slice(0,140))}catch(e){}});if(bad.length)current.push(baseRow('Continuous Run Level Card Wrap Drift','Continuous Run Bank',{wrapped:bad.slice(0,30)}));else passes.push({type:'Continuous Run Level Card Wrap Drift',where:'Continuous Run Bank'})}});return{current,passes}}
function sameTypeWhere(x,y){return norm(x.type)===norm(y.type)&&norm(x.where||x.where_seen)===norm(y.where)}
function cleanAll(){save(KNOWN,unique(load(KNOWN,[])).slice(-100));save(EVID,unique(load(EVID,[])).slice(-100));let cp=currentAndPasses(),active=unique(load(ACTIVE,[]));cp.passes.forEach(p=>{active=active.filter(x=>!sameTypeWhere(x,p))});cp.current.forEach(x=>{active=active.filter(y=>!sameTypeWhere(y,x));active.push(x)});save(ACTIVE,unique(active).slice(0,40));try{localStorage.setItem('pmp_bug_bank_current_active_cleaner_v1_receipt',JSON.stringify({type:'PMP_BUG_BANK_CURRENT_ACTIVE_CLEANER_V1',version:V,at:new Date().toISOString(),current_observed:cp.current.length,verified_clean_passes:cp.passes.length,rule:'Active visual bugs remain active until the same owning surface is reopened and verified clean.'}))}catch(e){}}
window.PMPBugBankCurrentActiveCleanerV1={version:V,scan:cleanAll,currentAndPasses};
try{let mo=new MutationObserver(()=>setTimeout(cleanAll,70));mo.observe(document.documentElement,{childList:true,subtree:true,characterData:true,attributes:true})}catch(e){}
window.addEventListener('load',()=>[100,350,900,1800,3500,6500].forEach(t=>setTimeout(cleanAll,t)));
setInterval(cleanAll,650);cleanAll();
})();