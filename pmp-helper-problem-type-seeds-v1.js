(()=>{
'use strict';
const V='1.0.0-display-sync-fighting-seed';
const KEY='pmp_helper_problem_memory_types_v1';
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]').filter(Boolean)}catch(e){return[]}}
function save(x){try{localStorage.setItem(KEY,JSON.stringify((x||[]).slice(-40)))}catch(e){}}
function seedType(row){let list=load();let old=list.find(x=>x.signature===row.signature||x.type===row.type);if(old){old.how_it_happens=row.how_it_happens;old.fix_rule=row.fix_rule;old.last_seeded_at=row.last_seeded_at;old.seeded=true;save(list);return old}list.push(row);save(list);return row}
function seed(){seedType({id:'seed_display_sync_fighting_v1',auto:true,seeded:true,type:'Display Sync Fighting',how_it_happens:'A helper repeatedly rewrites visible text or counts while another helper is also rendering that same screen area, causing the button/count to flicker or bounce between values.',signature:'Display Sync Fighting|Helper UI count display',where:'Helper Bank Problems Found button',severity:'medium',created_at:new Date().toISOString(),last_seen:new Date().toISOString(),last_seeded_at:new Date().toISOString(),seen:1,fix_rule:'Do not live-rewrite the visible button DOM over and over. Patch the single count source behind the render, then let the inspector render normally.'})}
window.PMPHelperProblemTypeSeedsV1={version:V,seed};
seed();
})();