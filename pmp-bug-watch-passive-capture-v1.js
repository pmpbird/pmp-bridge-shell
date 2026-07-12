(()=>{
'use strict';
const V='2.0.0-passive-capture-active-bugs-found';
const OWNER='pmp-bug-watch-passive-capture-v1';
const ACTIVE='pmp_bug_bank_active_bugs_v1';
const RECEIPT='pmp_bug_watch_passive_capture_v1_receipt';
const MAX=80;
const RULE='Passive capture pipe only. Appends bug symptoms to Bug Bank / Active Bugs Found. No fixing, deleting, moving, rerouting, rebuilding, storage clearing, or IndexedDB write.';
function T(){try{return top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function read(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function norm(s){return clean(s).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function sig(x){return String(x.signature||norm((x.type||'Bug symptom')+'|'+(x.where||x.where_seen||'runtime')+'|'+(x.how_it_happens||x.symptom||''))).slice(0,220)}
function merge(row){let a=read(ACTIVE,[]);if(!Array.isArray(a))a=[];let base=Object.assign({type:'Passive Bug Watch Capture',severity:'medium',where:'Runtime',where_seen:'Runtime',how_it_happens:'A passive bug symptom was observed.',fix_rule:'Do not auto-fix. Review the Active Bugs Found record and classify before any repair.',bug_bank_section:'Active Bugs Found',source:OWNER,passive_capture:true,created_at:now(),seen:1},row||{});base.last_seen=now();base.signature=sig(base);let hit=a.find(x=>sig(x)===base.signature);if(hit)Object.assign(hit,base,{created_at:hit.created_at||base.created_at,seen:Number(hit.seen||1)+1,last_seen:now()});else a.push(base);save(ACTIVE,a.slice(-MAX));save(RECEIPT,{type:'PMP_BUG_WATCH_PASSIVE_CAPTURE_RECEIPT_V1',version:V,owner:OWNER,at:now(),last_signature:base.signature,active_count:a.length,storage_policy:'append_merge_active_bugs_found_only',rule:RULE});return base}
function capture(type,where,how,detail,severity){return merge({type:type||'Passive Bug Watch Capture',where:where||'Runtime',where_seen:where||'Runtime',how_it_happens:how||'A passive bug symptom was observed.',detail:detail||{},severity:severity||'medium',fix_rule:'Do not auto-fix. Review the Active Bugs Found record and classify before any repair.'})}
const installed=[];
function gate(){try{return window.PMPPass2ActorAuthorizationGateV1||(T()&&T().PMPPass2ActorAuthorizationGateV1)||null}catch(e){return null}}
function installWin(w){try{if(!w||installed.indexOf(w)>-1)return;let g=gate();if(g&&typeof g.installWindow==='function')g.installWindow(w);installed.push(w);w.addEventListener('error',e=>{try{let target=e.target||{};let tag=String(target.tagName||'').toLowerCase();if(tag==='script'||tag==='link'||tag==='iframe'||tag==='frame'){capture('Resource Load Failure','Active app resource load',tag+' failed to load.',{tag,src:target.src||target.href||target.getAttribute&&target.getAttribute('src')||'',document_url:String(w.location&&w.location.href||'')},'high');return}if(e.message)capture('Runtime Error','Active app runtime',String(e.message),{filename:e.filename,lineno:e.lineno,colno:e.colno,document_url:String(w.location&&w.location.href||'')},'high')}catch(_){}} ,true);w.addEventListener('unhandledrejection',e=>{try{capture('Unhandled Promise Rejection','Active app runtime',String(e.reason&&e.reason.message||e.reason||'Unhandled promise rejection'),{document_url:String(w.location&&w.location.href||'')},'high')}catch(_){}})}catch(e){}}
function docs(root,a,n){a=a||[];n=n||0;if(!root||n>12)return a;try{let d=root.document;if(d){a.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{if(f.contentWindow)docs(f.contentWindow,a,n+1)}catch(e){}})}}catch(e){}return a}
function scan(){try{installWin(window);installWin(T());docs(T()).forEach(d=>{try{installWin(d.defaultView||d.parentWindow)}catch(e){}});save(RECEIPT,{type:'PMP_BUG_WATCH_PASSIVE_CAPTURE_RECEIPT_V1',version:V,owner:OWNER,at:now(),installed_windows:installed.length,storage_policy:'append_merge_active_bugs_found_only',rule:RULE})}catch(e){}}
window.PMPBugWatchPassiveCaptureV1={version:V,owner:OWNER,activeKey:ACTIVE,capture,scan,report:()=>({type:'PMP_BUG_WATCH_PASSIVE_CAPTURE_REPORT_V1',version:V,owner:OWNER,active_bug_count:(Array.isArray(read(ACTIVE,[]))?read(ACTIVE,[]).length:0),installed_windows:installed.length,rule:RULE,passive_only:true,no_fix:true,no_delete:true,no_move:true,no_reroute:true,no_indexeddb_write:true})};
[0,300,900,1800,3500,7000].forEach(t=>setTimeout(scan,t));
setInterval(scan,2500);scan();
})();
