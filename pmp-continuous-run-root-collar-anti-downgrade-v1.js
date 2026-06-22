(()=>{
if(window.PMPContinuousRunRootCollarAntiDowngradeV1)return;
const VERSION='1.0.0-root-collar-anti-downgrade';
window.PMPContinuousRunRootCollarAntiDowngradeV1={version:VERSION};
const STATE='pmp_continuous_run_state_ledger_v2';
const STATE1='pmp_continuous_run_state_ledger_v1';
const PROOF='pmp_continuous_run_root_collar_anti_downgrade_proof_v1';
const CURRENT='pmp-current-inner-cleanbug-rgcontrols-v16.html#control';
function now(){return new Date().toISOString()}
function rd(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function wr(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2));return true}catch(e){return false}}
function isRootCollar(s){const k=(s&&s.kernel_to_leaf_guard_families)||{};return String(s&&s.kernel_to_leaf_attachment_status||'').includes('root_collar')||String(k.type||'').includes('V6')||String((k.root_collar_stabilization||{}).status||'').includes('ROOT_COLLAR')}
function repair(){let before=rd(STATE,{});let beforeStatus=before.kernel_to_leaf_attachment_status||'';let beforeType=(before.kernel_to_leaf_guard_families||{}).type||'';let usedStabilizer=false;if(window.PMPContinuousRunRootCollarStabilizerV1&&typeof window.PMPContinuousRunRootCollarStabilizerV1.stabilize==='function'&&!isRootCollar(before)){before=window.PMPContinuousRunRootCollarStabilizerV1.stabilize();usedStabilizer=true}
let after=rd(STATE,before);after.current_app_route=CURRENT;after.current_active_route=CURRENT;after.blocked_state=after.blocked_state||'not_blocked';if(isRootCollar(after)){after.kernel_to_leaf_attachment_status='attached_saturated_solidified_detailed_root_collar'}after.updated_at=now();wr(STATE,after);wr(STATE1,after);wr(PROOF,{type:'PMP_CONTINUOUS_RUN_ROOT_COLLAR_ANTI_DOWNGRADE_PROOF_V1',version:VERSION,at:now(),before_status:beforeStatus,before_type:beforeType,after_status:after.kernel_to_leaf_attachment_status,after_type:(after.kernel_to_leaf_guard_families||{}).type||'',used_root_collar_stabilizer:usedStabilizer,anti_downgrade_active:true,safe_claim:'If an older saturated V2 guard appears, this repair re-applies or preserves the detailed root-collar guard before the runner starts or continues.',do_not_claim:'Does not start Packet 1.5, does not write GitHub, does not run Shortcut, and does not mutate the real app automatically.'});return after}
[120,300,700,1300,2400,4200].forEach(t=>setTimeout(repair,t));setInterval(repair,250);
window.PMPContinuousRunRootCollarAntiDowngradeV1={version:VERSION,repair};
})();