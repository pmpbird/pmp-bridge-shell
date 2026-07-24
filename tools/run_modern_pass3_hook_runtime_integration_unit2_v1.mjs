#!/usr/bin/env node
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const scenario=process.argv[2]||'positive';
const bodies=Array.from({length:22},(_,i)=>({body_id:`BODY-${String(i).padStart(3,'0')}`,acceptance_state:'accepted',begin_marker_seen:true,end_marker_seen:true,raw_source_pointer:`ptr:BODY-${String(i).padStart(3,'0')}`}));
const supports=['app_wiring_master_index','app_wiring_phase_1','app_wiring_phase_2','app_wiring_phase_3','app_wiring_phase_4','bug_finder_runtime_plan','hook_registry','lossless_medium','mode_selection_operator_card','real_bug_batch_proof_plan','receiver_card','saved_set_guardian_card'].map(x=>({support_slot:x,raw_source_pointer:`ptr:${x}`}));
const receipts=Array.from({length:6},(_,i)=>({hook_id:`HOOK-${String(i+1).padStart(3,'0')}`,hook_name:`Hook ${i+1}`,hook_status:'wired_with_watch',validated_for_scope:false,fail_closed_rule_present:true,fail_closed_output_when_missing:'blocked',blocks_unsafe_claims:true,allows_safe_claim:true,writes_receipt:true,preserves_source_identity:true}));
const seed={
 pmp_phase1_hook_receipts_v1:receipts,
 pmp_phase2_runtime_verification_latest_v1:{verification_state:'runtime_verified_with_watch'},
 pmp_fail_closed_simulation_latest_v1:{simulation_state:'fail_closed_simulation_passed_with_watch'},
 pmp_phase1_hook_wiring_latest_v1:{phase1_wiring_state:'phase1_hooks_001_006_wired_with_watch'},
 pmp_medium_source_bodies_v1:bodies,
 pmp_medium_manifest_records_v1:[{manifest_id:'MANIFEST-001'}],
 pmp_medium_support_source_objects_v1:supports
};
switch(scenario){
 case 'missing_body': seed.pmp_medium_source_bodies_v1.pop(); break;
 case 'duplicate_body': seed.pmp_medium_source_bodies_v1.push({...seed.pmp_medium_source_bodies_v1[0]}); break;
 case 'missing_manifest': seed.pmp_medium_manifest_records_v1=[]; break;
 case 'missing_support_slot': seed.pmp_medium_support_source_objects_v1.pop(); break;
 case 'missing_body_raw_pointer': delete seed.pmp_medium_source_bodies_v1[0].raw_source_pointer; break;
 case 'missing_support_raw_pointer': delete seed.pmp_medium_support_source_objects_v1[0].raw_source_pointer; break;
 case 'missing_marker': seed.pmp_medium_source_bodies_v1[0].begin_marker_seen=false; break;
 case 'readiness_prerequisite_failure': seed.pmp_phase2_runtime_verification_latest_v1={verification_state:'blocked'}; break;
 case 'overclaim_attempt': seed.pmp_medium_manifest_records_v1[0].real_app_proof=true; break;
 case 'positive': break;
 default: throw new Error(`unknown scenario:${scenario}`);
}
class Storage{constructor(obj){this.m=new Map(Object.entries(obj).map(([k,v])=>[k,JSON.stringify(v)]));}getItem(k){return this.m.has(k)?this.m.get(k):null;}setItem(k,v){this.m.set(k,String(v));}}
const localStorage=new Storage(seed);
const node=()=>({textContent:'',style:{},appendChild(){},onclick:null});
const document={body:node(),getElementById(){return null;},createElement(){return node();}};
const context={window:{},document,localStorage,navigator:{clipboard:{writeText:async()=>{}}},console,Date,JSON,Array,Object,String,Boolean,Number,Promise,setTimeout,clearTimeout};
context.window=context;
vm.createContext(context);
for(const rel of ['pmp-phase3-hook-readiness-v1.js','pmp-phase3-hook-validation-execution-v1.js']){
 vm.runInContext(fs.readFileSync(path.join(ROOT,rel),'utf8'),context,{filename:rel});
}
const readiness=context.PMPPhase3HookReadinessV1.run(document);
const execution=context.PMPPhase3HookValidationExecutionV1.run(document);
const normalize=x=>JSON.parse(JSON.stringify(x,(k,v)=>k==='at'?'<normalized>':v));
const receipt={type:'PMP_MODERN_PASS3_HOOK_RUNTIME_INTEGRATION_UNIT2_RECEIPT_V1',scenario,readiness:normalize(readiness),execution:normalize(execution),claim_ceiling:{real_app_proof:false,current_clean:false,frozen:false,full_transfer_proof:false,full_history_lossless:false,best_in_world:false,production_activation:false}};
process.stdout.write(JSON.stringify(receipt,null,2)+'\n');
