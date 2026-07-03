(()=>{
'use strict';
const V='1.0.0-active-bug-found-contract';
const OWNER='pmp-active-bug-found-contract-v1';
const KEY='pmp_bug_bank_active_bugs_v1';
const NOTE='Shapes Active Bugs Found records and keeps repeated symptoms together.';
const STAT=['active','triage','hold','resolved','rejected'];
function n(){return new Date().toISOString()}
function c(s){return String(s==null?'':s).replace(/\s+/g,' ').trim()}
function m(s){return c(s).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function r(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function w(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function sig(x){return c(x.signature||[x.type||x.kind||x.problem||'active bug',x.where_seen||x.where||'runtime',x.symptom||x.how_it_happens||''].join('|')).slice(0,240)}
function bid(s){let h=0;for(let i=0;i<s.length;i++)h=((h<<5)-h+s.charCodeAt(i))|0;return'BUG-'+Math.abs(h).toString(36).toUpperCase()}
function src(x){let q=m(x.source||x.evidence_source||'');if(q.indexOf('visual')>-1)return'visual detector';if(q.indexOf('watch')>-1)return'bug watch';if(q.indexOf('manual')>-1)return'manual';if(q.indexOf('diagnostic')>-1)return'diagnostic';return'unknown'}
function shape(x){x=x||{};let s=sig(x),st=m(x.status||'active');if(STAT.indexOf(st)<0)st='active';return{bug_id:x.bug_id||bid(s),status:st,severity:m(x.severity||x.level||'medium')||'medium',source:src(x),where_seen:c(x.where_seen||x.where||'Runtime'),symptom:c(x.symptom||x.how_it_happens||x.type||'Active bug symptom'),evidence:x.evidence||x.detail||{},owner_guess:c(x.owner_guess||x.owner||''),affected_area:c(x.affected_area||x.where||x.where_seen||'Runtime'),safe_to_ignore:!!x.safe_to_ignore,blocks_next_pass:!!x.blocks_next_pass,first_seen:x.first_seen||x.created_at||x.at||x.last_seen||n(),last_seen:x.last_seen||x.at||n(),seen_count:Number(x.seen_count||x.seen||1)||1,work_allowed:x.work_allowed===true,notes:Array.isArray(x.notes)?x.notes:[],signature:s,bug_bank_section:'Active Bugs Found',contract_version:V,raw_source:x.raw_source||x}}
function merge(list){let map={},out=[];(Array.isArray(list)?list:[]).filter(Boolean).map(shape).forEach(x=>{let k=x.signature||x.bug_id;if(map[k]){map[k].last_seen=x.last_seen;map[k].seen_count=Number(map[k].seen_count||1)+Number(x.seen_count||1);map[k].blocks_next_pass=!!(map[k].blocks_next_pass||x.blocks_next_pass);if(!Object.keys(map[k].evidence||{}).length)map[k].evidence=x.evidence}else{map[k]=x;out.push(x)}});return out.slice(-120)}
function normalize(){let before=r(KEY,[]),after=merge(before);w(KEY,after);let receipt={type:'PMP_ACTIVE_BUG_FOUND_CONTRACT_RECEIPT_V1',version:V,owner:OWNER,at:n(),before_count:Array.isArray(before)?before.length:0,after_count:after.length,blocker_count:after.filter(x=>x.blocks_next_pass).length,note:NOTE};w('pmp_active_bug_found_contract_v1_receipt',receipt);return receipt}
function add(row){let a=r(KEY,[]);if(!Array.isArray(a))a=[];a.push(row||{});w(KEY,merge(a));return normalize()}
function report(){let a=r(KEY,[]);return{type:'PMP_ACTIVE_BUG_FOUND_CONTRACT_REPORT_V1',version:V,owner:OWNER,active_key:KEY,count:Array.isArray(a)?a.length:0,statuses:STAT,note:NOTE}}
window.PMPActiveBugFoundContractV1={version:V,owner:OWNER,shape,normalize,add,report};
[0,500,1500,3500].forEach(t=>setTimeout(normalize,t));
window.addEventListener('load',()=>setTimeout(normalize,900));
})();
