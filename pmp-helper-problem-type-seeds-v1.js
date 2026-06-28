(()=>{
'use strict';
const V='1.0.1-launcher-reload-cleanup-seed';
const KEY='pmp_helper_problem_memory_types_v1';
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]').filter(Boolean)}catch(e){return[]}}
function save(x){try{localStorage.setItem(KEY,JSON.stringify((x||[]).slice(-60)))}catch(e){}}
function seedType(row){let list=load();let old=list.find(x=>x.signature===row.signature||x.type===row.type);if(old){old.how_it_happens=row.how_it_happens;old.fix_rule=row.fix_rule;old.last_seeded_at=row.last_seeded_at;old.seeded=true;old.where=row.where||old.where;old.severity=row.severity||old.severity;save(list);return old}list.push(row);save(list);return row}
function now(){return new Date().toISOString()}
function seed(){
seedType({id:'seed_display_sync_fighting_v1',auto:true,seeded:true,type:'Display Sync Fighting',how_it_happens:'A helper repeatedly rewrites visible text or counts while another helper is also rendering that same screen area, causing the button/count to flicker or bounce between values.',signature:'Display Sync Fighting|Helper UI count display',where:'Helper Bank Problems Found button',severity:'medium',created_at:now(),last_seen:now(),last_seeded_at:now(),seen:1,fix_rule:'Do not live-rewrite the visible button DOM over and over. Patch the single count source behind the render, then let the inspector render normally.'});
seedType({id:'seed_launcher_reload_control_removed_v1',auto:true,seeded:true,type:'Launcher Control Removed By Overbroad Cleanup',how_it_happens:'A helper cleanup rule removes buttons by visible text, such as Reload Current or Test Current Page, instead of limiting cleanup to its own owned screen area. After repeated reload cycles it can catch the Launcher reload button and make it disappear.',signature:'Launcher Control Removed By Overbroad Cleanup|Reload Current button',where:'Launcher Reload Current button',severity:'high',created_at:now(),last_seen:now(),last_seeded_at:now(),seen:1,fix_rule:'Never remove global Launcher controls by text from a bank/display helper. Scope cleanup to the helper owner container, and guard repeated reload taps so overlapping reload cycles cannot race.'});
}
window.PMPHelperProblemTypeSeedsV1={version:V,seed};
seed();
})();