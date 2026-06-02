(()=>{
  const KEYS={
    hooks:'pmp_medium_hook_slots_v1',
    watches:'pmp_medium_watch_items_v1',
    proofs:'pmp_medium_proof_objects_v1',
    claims:'pmp_medium_claim_controls_v1',
    receipts:'pmp_medium_transfer_receipts_v1'
  };
  const HOOK_COUNT=50;
  const WATCH_COUNT=22;
  function read(k,f){try{const v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
  function write(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){return false}}
  function now(){return new Date().toISOString()}
  function pad(n){return String(n).padStart(3,'0')}
  function addReceipt(kind,summary){let a=read(KEYS.receipts,[]);if(!Array.isArray(a))a=[];if(a.some(r=>r&&r.kind===kind))return;a.push({receipt_id:'receipt_'+Date.now(),type:'PMP_PRIVATE_CLAIM_CONTROL_RECEIPT_V1',kind,summary,created_at:now(),source:'pmp-private-claim-controls-v1',safe_claim:'Claim-control seed records were created locally.',do_not_claim:'Do not call this proof collected, hook wired, watch cleared, real app validated, frozen, or broad all-bug approved.'});write(KEYS.receipts,a.slice(-160))}
  function hookClaim(i){const id='HOOK-'+pad(i);return{claim_id:'CLAIM-HOOK-'+pad(i),claim_text:id+' may report only specified / allowed_with_watch until proof is collected.',claim_type:'hook_claim_ceiling_seed',hook_id:id,watch_item_id:null,proof_required:'PROOF-HOOK-'+pad(i),proof_collected:'none',allowed_state:'blocked_until_proof',downgrade_required:'yes',safe_replacement_claim:id+' is specified locally; not wired or validated.',blocked_reason:'Hook proof object has no collected proof yet.',blocked_claims:['wired','validated','real_app_tested','complete','current_clean','frozen','broad_all_bug_approved'],safe_claim:'Claim control exists for '+id+' but allows only specified/not validated wording.',do_not_claim:'Do not claim '+id+' is wired, validated, proof-passed, or real-app tested from this seed.',lossless_status:'claim_control_seed_created_not_proven',claim_control_version:'v1'}}
  function watchClaim(i,w){const wid=(w&&w.watch_item_id)||('WATCH-'+pad(i));return{claim_id:'CLAIM-'+wid,claim_text:wid+' may not clear, promote, or downgrade without receipt proof.',claim_type:'watch_claim_ceiling_seed',hook_id:(w&&w.primary_hook)||'HOOK-006',watch_item_id:wid,proof_required:'PROOF-'+wid,proof_collected:'none',allowed_state:'open_watch_only',downgrade_required:'yes_if_claim_is_stronger_than_watch_proof',safe_replacement_claim:wid+' remains open/watch until clearance proof exists.',blocked_reason:(w&&w.blocked_stronger_claim)||'Watch item has no clearance proof yet.',blocked_claims:[(w&&w.blocked_stronger_claim)||'watch cleared without proof'],safe_claim:'Claim control exists for '+wid+' but watch remains open.',do_not_claim:'Do not claim '+wid+' cleared, validated, manifest-current, source-clean, or proof-passed from this seed.',lossless_status:'claim_control_seed_created_not_proven',claim_control_version:'v1'}}
  function ensureClaimControls(){
    const watches=read(KEYS.watches,[]);
    let existing=read(KEYS.claims,[]);if(!Array.isArray(existing))existing=[];
    const by={};existing.forEach(c=>{if(c&&c.claim_id)by[c.claim_id]=c});
    for(let i=1;i<=HOOK_COUNT;i++){const s=hookClaim(i),c=by[s.claim_id]||{};by[s.claim_id]={...s,...c,claim_id:s.claim_id,claim_control_seed:true}}
    for(let i=1;i<=WATCH_COUNT;i++){const w=Array.isArray(watches)?watches[i-1]:null;const s=watchClaim(i,w),c=by[s.claim_id]||{};by[s.claim_id]={...s,...c,claim_id:s.claim_id,claim_control_seed:true}}
    const ordered=[];for(let i=1;i<=HOOK_COUNT;i++)ordered.push(by['CLAIM-HOOK-'+pad(i)]);for(let i=1;i<=WATCH_COUNT;i++)ordered.push(by['CLAIM-WATCH-'+pad(i)]);
    write(KEYS.claims,ordered);
    addReceipt('claim_controls_seed_created','Created 72 claim-control seed records: 50 hook claim ceilings and 22 watch claim ceilings. No claim is proven or promoted yet.');
    return claimControlState();
  }
  function claimControlState(){const cc=read(KEYS.claims,[]);const a=Array.isArray(cc)?cc:[];return{expected_claim_controls:HOOK_COUNT+WATCH_COUNT,claim_control_records:a.length,claim_control_seed_records:a.filter(c=>c&&c.claim_control_seed).length,hook_claim_controls:a.filter(c=>String(c&&c.claim_id||'').startsWith('CLAIM-HOOK-')).length,watch_claim_controls:a.filter(c=>String(c&&c.claim_id||'').startsWith('CLAIM-WATCH-')).length,proved_or_allowed_clean:a.filter(c=>c&&c.allowed_state==='allowed_clean').length,claim_control_claim_ceiling:'claim_controls_seeded_no_claims_promoted',next_missing_step:'transfer_receipt_builder'} }
  function patchMedium(){
    try{ensureClaimControls()}catch(e){}
    const m=window.PMPPrivateMediumButtonsV1;
    if(m&&!m.ensureClaimControls){m.ensureClaimControls=ensureClaimControls;m.claimControlState=claimControlState}
  }
  window.PMPPrivateClaimControlsV1={ensureClaimControls,claimControlState,patchMedium};
  window.addEventListener('load',()=>{setTimeout(patchMedium,200);setTimeout(patchMedium,900);setTimeout(patchMedium,1900)});
  setInterval(patchMedium,1000);
})();