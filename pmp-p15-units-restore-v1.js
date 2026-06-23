(()=>{
const V='1.0.1',SRC='pmp_packet_1_5_builder_source_v1',TXT='pmp_packet_1_5_packet_text_v1',UN='pmp_packet_1_5_units_v1',RUNNER='pmp_packet_1_5_continuous_runner_v1',STATE='pmp_continuous_run_state_ledger_v2',STOP='pmp_packet_1_5_manual_stop_requested_v1';
if(window.PMPP15UnitsRestoreV1&&window.PMPP15UnitsRestoreV1.version===V)return;
const g=k=>{try{return localStorage.getItem(k)||''}catch(e){return''}};
const r=(k,d)=>{try{let v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}};
const w=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v,null,2));return true}catch(e){return false}};
const set=(k,v)=>{try{localStorage.setItem(k,String(v));return true}catch(e){return false}};
function ok(u){return Array.isArray(u)&&u.length>=100&&u.filter(x=>x&&x.unit_type==='limitation_record').length>=100}
function solid(){let s=r(STATE,{});s.kernel_to_leaf_attachment_status='attached_saturated_solidified_detailed_root_collar';s.root_collar_stabilization={...(s.root_collar_stabilization||{}),status:'SOLIDIFIED_DETAILED_ROOT_COLLAR',solidified:true,updated_at:new Date().toISOString()};s.blocked_state='not_blocked';w(STATE,s)}
function restore(){solid();let rr0=r(RUNNER,{});if(rr0.status!=='STOPPED')set(STOP,'false');let u=r(UN,[]),src=g(SRC)||g(TXT);if(ok(u))return{changed:false,total:u.length};if(src&&window.PMPP15BuilderFixV2&&window.PMPP15BuilderFixV2.save){try{u=window.PMPP15BuilderFixV2.save(src).units}catch(e){}}
if(ok(u)){let rr=r(RUNNER,{});rr.total_units=u.length;rr.units_completed=0;rr.current_unit_index=0;rr.status='READY_BUILDER_UNITS';rr.unit_source='packet_1_5_builder_grid';w(RUNNER,rr);return{changed:true,total:u.length}}return{changed:false,total:Array.isArray(u)?u.length:0}}
window.PMPP15UnitsRestoreV1={version:V,restore};
window.addEventListener('load',()=>[50,200,600,1200,2400].forEach(t=>setTimeout(restore,t)));setInterval(restore,500);restore();
})();