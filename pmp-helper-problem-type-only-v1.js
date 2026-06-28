(()=>{
'use strict';
const V='1.0.0-type-only-memory';
const KEY='pmp_helper_problem_memory_types_v1';
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function typeOf(x){return clean(x&&x.type||x&&x.kind||x&&x.problem||x&&x.check||'Unknown helper problem type')}
function whyOf(a,b){return clean(a&&a.how_it_happens||a&&a.why||b&&b.how_it_happens||b&&b.why||'')}
function normalizeList(list){let map={};(Array.isArray(list)?list:[]).filter(Boolean).forEach(x=>{let type=typeOf(x),key=type.toLowerCase();let old=map[key]||{};let seen=Math.max(Number(old.seen||0),0)+Math.max(Number(x.seen||1),1);map[key]={id:old.id||x.id||('type_'+Date.now()+'_'+Object.keys(map).length),auto:true,type,signature:'type:'+type.toLowerCase(),where:old.where||clean(x.where||'helper memory'),severity:old.severity||x.severity||'medium',how_it_happens:whyOf(x,old),fix_rule:clean(x.fix_rule||old.fix_rule||''),created_at:old.created_at||x.created_at||new Date().toISOString(),last_seen:x.last_seen||x.at||old.last_seen||new Date().toISOString(),seen};});return Object.keys(map).sort().map(k=>{let x=map[k];Object.keys(x).forEach(p=>{if(x[p]===''||x[p]==null)delete x[p]});return x}).slice(-60)}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){return[]}}
function write(list){try{nativeSet.call(localStorage,KEY,JSON.stringify(normalizeList(list)))}catch(e){}}
const nativeSet=localStorage.setItem;
try{localStorage.setItem=function(k,v){if(String(k)===KEY){try{return nativeSet.call(this,k,JSON.stringify(normalizeList(JSON.parse(v||'[]'))))}catch(e){return nativeSet.call(this,k,v)}}return nativeSet.apply(this,arguments)}}catch(e){}
function normalize(){write(load())}
window.PMPHelperProblemTypeOnlyV1={version:V,normalize,normalizeList};
window.addEventListener('load',()=>[200,900,2500,5000].forEach(t=>setTimeout(normalize,t)));
setInterval(normalize,5000);normalize();
})();