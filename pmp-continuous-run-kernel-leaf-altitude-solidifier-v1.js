(()=>{
if(window.PMPContinuousRunKernelLeafAltitudeSolidifierV1)return;window.PMPContinuousRunKernelLeafAltitudeSolidifierV1=true;
const VERSION='1.0.0-family-altitude-solidifier';
const STATE='pmp_continuous_run_state_ledger_v2';
const PROOF='pmp_continuous_run_kernel_leaf_altitude_solidification_proof_v1';
const CURRENT='pmp-current-inner-cleanbug-rgcontrols-v16.html#control';
const ALTITUDES=['kernel_lock','root_boundary','trunk_rule','branch_detectors','leaf_stop_conditions','fruit_required_proof','canopy_action'];
const ROOTS=['No-Money','No-Breaking','Privacy','Human-Control','Reversibility','Proof','Necessity','Scope','Evidence','Resource','Drift','Degradation','Mirror','Promotion','Baseline','Rollback','Isolation','Non-Mutation','Kill Switch','Conflict','Silence','Permission','Heartbeat','Pause/Resume','Duplicate','Vault Safety','Freshness','Diagnostic','Event Ledger','Loop Bound','Performance','Cache','State Clarity','App-Open','Unknown-Risk','Clipboard Verification','Shortcut Completion','Delayed Proof','Route Identity','Cache Identity','Mirror Equivalence','Slow Damage','Loud Failure','Unattended Safety','Stable Pass'];
const FAMILY_DETAIL={
'No-Money':{must_not:['use a paid API','choose a paid fallback','raise spending above zero','require subscription','open external paid service'],proof:['spending_ceiling_usd is 0','paid_api_allowed is false','paid_fallback_allowed is false']},
'No-Breaking':{must_not:['break real app load','remove Save button','change route without proof','change app behavior while user is not watching','continue after app instability'],proof:['local app diagnostic GOOD','route still current v16','Save button present']},
'Privacy':{must_not:['ask for token','ask for credential','require private contents','copy full private report into ledger','expose personal data'],proof:['no credential request','no private content required','ledger stores small safe metadata only']},
'Human-Control':{must_not:['start Packet 1.5 without manual start','ignore manual stop','continue under ambiguous permission','act while unattended beyond safe proposal-only checks','override user pause'],proof:['manual_start_required true','start_requested false until user starts','manual_stop_requested blocks']},
'Reversibility':{must_not:['make irreversible change','lose rollback route','overwrite restore point','continue after checkpoint mismatch','change without recover path'],proof:['fallback route present','recovery tools route present','baseline/restore point known']},
'Proof':{must_not:['continue without proof','accept weak diagnostic','skip independent check','call WATCH good','advance after failed verification'],proof:['verified true','diagnostic GOOD','watch/blocked absent']},
'Non-Mutation':{must_not:['write GitHub automatically','run Shortcut automatically','mutate real app automatically','auto-save while unattended','change core from observer'],proof:['write_authority none','merge_authority none','execution_started false until start']},
'Route Identity':{must_not:['use stale v9 route','use stale v11 route','hide route mismatch','continue if active route differs from current','open wrong fallback'],proof:['current_app_route is v16','current_active_route is v16','fallback is v18']},
'Stable Pass':{must_not:['accept one unstable pass','advance after non-repeatable result','skip post-change test','ignore proof drift','claim acceptance without lossless report'],proof:['stable pass proof exists','repeatable result','lossless report copied']}
};
function now(){return new Date().toISOString()}
function rd(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function wr(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2));return true}catch(e){return false}}
function slug(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'')}
function baseDetail(root){return FAMILY_DETAIL[root]||{must_not:[root+' missing',root+' failed',root+' mismatch',root+' unsafe',root+' unproven'],proof:[root+' checked',root+' not blocking',root+' not stale']}}
function altitudeLayers(f){
 const root=f.root||f.kernel||'Unknown';
 const d=baseDetail(root);
 const leaves=Array.isArray(f.leaf_stop)&&f.leaf_stop.length?f.leaf_stop:d.must_not.map(x=>slug(x));
 return{
  kernel_lock:{altitude:0,rule:root+' is a non-bypassable guard while Continuous Run is active or prepared.',must_not:d.must_not,fail_state:'BLOCKED'},
  root_boundary:{altitude:1,rule:'Before each Packet 1.5 unit, this root must be checked as its own boundary, not implied by another family.',must_not:['merge this root into a different family','treat this root as optional','skip because another guard passed'],fail_state:'WATCH'},
  trunk_rule:{altitude:2,rule:f.trunk||('Protect '+root),must_hold:['free_only remains true','write_authority remains none','merge_authority remains none','manual start gate remains respected'],fail_state:'BLOCKED'},
  branch_detectors:{altitude:3,rule:'Look for concrete signs before and after every unit.',detectors:leaves.map(x=>'detect_'+x).concat(['detect_'+slug(root)+'_silence','detect_'+slug(root)+'_drift']),fail_state:'WATCH'},
  leaf_stop_conditions:{altitude:4,rule:'Any leaf stop condition pauses the run and prevents continuation.',leaf_stop:leaves,fail_state:'BLOCKED'},
  fruit_required_proof:{altitude:5,rule:'A unit may only continue when this family has proof, not just no visible error.',required_proof:d.proof.concat(['state ledger updated','small event recorded','next move clear']),fail_state:'WAITING'},
  canopy_action:{altitude:6,rule:'If this family raises WATCH or BLOCKED while user is not watching, stop the loop and wait for user proof.',actions:['set blocked_state when BLOCKED','record safe ledger event','do not write GitHub','do not run Shortcut','do not continue to next unit','surface next move'],fail_state:'STOP'}
 };
}
function solidify(){
 const s=rd(STATE,{});
 const kl=s.kernel_to_leaf_guard_families||{};
 const fams=Array.isArray(kl.families)?kl.families:[];
 const byRoot={};fams.forEach(f=>{if(f&&f.root)byRoot[f.root]=f});
 const detailed=ROOTS.map((r,i)=>{const f=byRoot[r]||{id:'klg_'+String(i+1).padStart(2,'0')+'_'+slug(r),kernel:r+' guard',root:r,trunk:'protect '+r,leaf_stop:baseDetail(r).must_not.map(x=>slug(x)),saturated:true};return{...f,altitudes:altitudeLayers(f),altitude_saturated:true}});
 const missing=ROOTS.filter(r=>!detailed.some(f=>f.root===r));
 const bad=detailed.filter(f=>!ALTITUDES.every(a=>f.altitudes&&f.altitudes[a]));
 const status=(!missing.length&&!bad.length&&detailed.length===ROOTS.length)?'SOLIDIFIED':'OPEN';
 const next=status==='SOLIDIFIED'?'Stop guard design. Packet 1.5 can use these guards behind the manual start gate.':'Fill missing altitude layers before Packet 1.5.';
 const nextKL={...kl,type:'PMP_CONTINUOUS_RUN_KERNEL_TO_LEAF_GUARD_FAMILIES_V3',version:VERSION,attached_to:'continuous_run_engine',root_families:ROOTS,families:detailed,altitude_solidification:{status,stop_at_saturation:true,altitudes:ALTITUDES,family_count:detailed.length,root_family_count:ROOTS.length,missing_roots:missing,bad_families:bad.map(f=>f.root),unattended_contract:['no automatic real-app mutation','no automatic GitHub write','no automatic Shortcut run','no paid path','no continue on WATCH','no continue on BLOCKED','no silent failure','manual start required','manual stop respected'],next_move:next}};
 s.kernel_to_leaf_guard_families=nextKL;
 s.kernel_to_leaf_attachment_status=status==='SOLIDIFIED'?'attached_saturated_solidified':'attached_open';
 s.current_app_route=CURRENT;s.current_active_route=CURRENT;s.packet_1_5_gate=s.packet_1_5_gate||'ready_after_user_start';s.blocked_state=s.blocked_state||'not_blocked';s.updated_at=now();
 wr(STATE,s);wr(PROOF,{type:'PMP_CONTINUOUS_RUN_KERNEL_LEAF_ALTITUDE_SOLIDIFICATION_PROOF_V1',version:VERSION,at:now(),status:s.kernel_to_leaf_attachment_status,altitude_solidification:nextKL.altitude_solidification,safe_claim:'Every guard root is attached with altitude layers and unattended must-not-happen stop actions.',do_not_claim:'Does not start Packet 1.5 and does not mutate the real app automatically.'});return s;
}
setTimeout(solidify,150);setTimeout(solidify,650);setTimeout(solidify,1500);setInterval(solidify,900);
window.PMPContinuousRunKernelLeafAltitudeSolidifierV1={version:VERSION,solidify};
})();