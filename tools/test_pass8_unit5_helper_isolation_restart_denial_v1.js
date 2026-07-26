#!/usr/bin/env node
'use strict';
const assert=require('assert');
const path=require('path');
const runner=require('./run_pass8_unit5_helper_isolation_restart_denial_v1.js');
const unit2=require('./run_pass8_unit2_helper_capability_contract_v1.js');
const runtime=require('../pmp-helper-owner-integration-v1.js');
const ROOT=path.resolve(__dirname,'..');
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}
const result=runner.scenarioResult();

equal(result.type,runner.TYPE,'result type');
equal(result.version,runner.VERSION,'result version');
equal(result.status,'PASS','result status');
equal(runner.verifyResultHash(result),true,'result hash');
equal(result.registration.helpers.length,12,'twelve eligible registrations');
equal(result.registration.codes.length,12,'twelve registration outcomes');
equal(result.registration.codes.every(code=>code==='HELPER_REGISTERED'),true,'all eligible register');
equal(result.registration.registered_count,12,'twelve registered');
equal(result.registration.diagnostic_registered_count,12,'twelve visible read only');
equal(result.registration.authority_grants,0,'zero authority grants');
equal(result.registration.behavior_authorizations,0,'zero behavior authorizations');

const eligible=unit2.inventory().declared.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY');
equal(result.registration.helpers,eligible.map(row=>row.helper_id),'exact eligible helper order');
equal(result.held.length,2,'two held declarations');
equal(result.held.find(row=>row.helper_id==='legacy_helper_registry').code,'REJECTED_LEGACY_HELPER_HELD','legacy denied');
equal(result.held.find(row=>row.helper_id==='safe_writer_current_return_fix').code,'REJECTED_HELPER_CONFLICT_HELD','Safe Writer conflict denied');
equal(result.unknown.length,9,'nine unknown sources');
equal(result.unknown.map(row=>row.file).sort(),unit2.contract().unknown_helper_sources.slice().sort(),'exact unknown sources');
equal(result.unknown.every(row=>row.code==='REJECTED_UNKNOWN_HELPER'),true,'unknowns denied');

equal(result.owner_absence.length,12,'owner absence all eligible');
equal(result.owner_absence.every(row=>row.code==='REJECTED_SECTION_OWNER_NOT_REGISTERED'),true,'missing owners denied');
equal(result.binding_denials.length,96,'eight binding faults for twelve helpers');
for(const row of result.binding_denials){
  equal(row.code,row.expected,`${row.helper_id} ${row.fault} denial`);
}
for(const helper of eligible){
  const rows=result.binding_denials.filter(row=>row.helper_id===helper.helper_id);
  equal(rows.length,8,'eight binding faults '+helper.helper_id);
  equal(new Set(rows.map(row=>row.fault)).size,8,'unique binding faults '+helper.helper_id);
}

equal(result.growth.length,12,'growth matrix all eligible');
const growth=result.growth.find(row=>row.helper_id==='continuous_run_bank_order_frame_loader');
equal(growth.growth_source,'continuous_run_frame_loader','exact growth source');
equal(growth.code,'HELPER_GROWTH_RECORDED_NO_AUTHORITY','declared growth observed');
equal(growth.accepted,true,'growth observation accepted');
equal(growth.authority_granted,false,'growth no authority');
equal(growth.behavior_authorized,false,'growth no behavior');
const nonGrowth=result.growth.filter(row=>row.helper_id!=='continuous_run_bank_order_frame_loader');
equal(nonGrowth.length,11,'eleven non-growth helpers');
equal(nonGrowth.every(row=>row.accepted===false),true,'non-growth denied');
equal(nonGrowth.every(row=>row.code==='REJECTED_GROWTH_OBSERVER_AUTHORITY'),true,'non-growth code');

equal(result.duplicate_sequence.accepted,'HELPER_REGISTERED','duplicate seed');
equal(result.duplicate_sequence.duplicate,'DUPLICATE_EVENT_IGNORED','identical duplicate');
equal(result.duplicate_sequence.conflicting,'REJECTED_DUPLICATE_EVENT_CONFLICT','conflicting duplicate');
equal(result.duplicate_sequence.update,'HELPER_UPDATED','sequence update');
equal(result.duplicate_sequence.stale,'REJECTED_STALE_SEQUENCE','stale denied');
equal(result.duplicate_sequence.gap,'REJECTED_SEQUENCE_GAP','gap denied');
equal(result.duplicate_sequence.chain,'REJECTED_EVENT_CHAIN','chain denied');
equal(result.duplicate_sequence.snapshot.counts.accepted,2,'only two accepted in sequence matrix');
equal(result.duplicate_sequence.snapshot.counts.duplicates,1,'one duplicate');
equal(result.duplicate_sequence.snapshot.registered.length,1,'one sequence helper');
for(const value of Object.values(result.duplicate_sequence.snapshot.side_effects)){
  equal(value,0,'sequence external effect zero');
}

equal(result.revocation.outcomes.map(row=>row.code),[
  'HELPER_REGISTERED','HELPER_REVOKED','HELPER_UPDATED','REJECTED_STALE_REVOCATION'
],'revocation outcomes');
equal(result.revocation.snapshot.revoked.pass2_atlas_adapter,1,'revocation epoch');
equal(result.revocation.snapshot.registered[0].status,'REVOKED_STATIC_EVENT_ONLY','revoked status persists');
equal(result.revocation.snapshot.registered[0].source_version,'source:after-revocation','post-revocation evidence update only');
equal(result.revocation.snapshot.registered[0].behavior_authorized,false,'revoked behavior false');
equal(result.revocation.view.revoked_count,1,'revocation visible');
equal(result.revocation.view.revoked[0].behavior_authorized,false,'view no revoked behavior');
equal(result.revocation.view.disclosure.capability_ids_exposed,false,'revocation view hides capability');

equal(result.restart.package.type,runtime.journalVersion,'restart package version');
equal(result.restart.package.entry_count,12,'restart package entries');
equal(result.restart.exact.restored,true,'exact restart');
equal(result.restart.exact.code,'RESTART_REPLAY_ACCEPTED','exact restart code');
equal(result.restart.exact.operation_ids.length,12,'restart operation identities');
equal(result.restart.exact.registered.length,12,'restart registered exact');
equal(result.restart.tamper_cases.length,4,'four tamper cases');
for(const row of result.restart.tamper_cases){
  equal(row.code,row.expected,'tamper code '+row.fault);
  equal(row.restored,false,'tamper not restored '+row.fault);
  equal(row.registered_after,0,'tamper empty registrations '+row.fault);
  equal(row.journal_after,0,'tamper empty journal '+row.fault);
}
equal(result.restart.missing_owner.restored,false,'restart missing owner denied');
equal(result.restart.missing_owner.code,'RESTART_REJECTED_JOURNAL_EVENT','restart missing owner code');
equal(result.restart.missing_owner.rejected_code,'REJECTED_SECTION_OWNER_NOT_REGISTERED','restart missing owner reason');
equal(result.restart.missing_owner.registered_after,0,'restart missing owner empty state');
equal(result.restart.missing_owner.journal_after,0,'restart missing owner empty journal');

equal(result.bounded_diagnostics.status,'READY_WITH_REGISTERED_HELPERS','bounded diagnostics ready');
equal(result.bounded_diagnostics.visible_event_count,128,'bounded diagnostics count');
equal(result.bounded_diagnostics.events_truncated,true,'bounded diagnostics truncated');
equal(result.bounded_diagnostics.first_visible_operation,'op:p8u5:bounded:3','bounded newest window');
equal(result.bounded_diagnostics.disclosure.capability_ids_exposed,false,'bounded cap IDs hidden');
equal(result.bounded_diagnostics.disclosure.helper_source_hashes_exposed,false,'bounded hashes hidden');
equal(result.bounded_diagnostics.disclosure.raw_authority_payloads_exposed,false,'bounded authority hidden');
equal(result.bounded_diagnostics.disclosure.source_versions_exposed,false,'bounded source version hidden');
for(const value of Object.values(result.bounded_diagnostics.side_effects)){
  equal(value,0,'bounded diagnostics external effect zero');
}
check(/^[0-9a-f]{64}$/.test(result.bounded_diagnostics.serialized_sha256),'bounded diagnostics digest');

for(const [key,value] of Object.entries(result.effects)){
  equal(value,false,'effect false '+key);
}
check(result.claim_ceiling.includes('No Helper behavior is activated'),'claim ceiling Helper');
check(result.claim_ceiling.includes('no Bank or Continuous Run repair'),'claim ceiling Bank');
check(result.claim_ceiling.includes('no live observation'),'claim ceiling observation');
check(result.claim_ceiling.includes('formal proof'),'claim ceiling proof');
equal(runtime.helpers.length,14,'production runtime still fourteen declarations');
equal(runtime.unknownSources.length,9,'production runtime still nine unknowns');
equal(runtime.helpers.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY').length,12,'production runtime still twelve eligible');
equal(runtime.helpers.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY').length,2,'production runtime still two held');

console.log(`PASS: P8-U5 Helper isolation, restart, growth, revocation, and denial proof (${assertions}/${assertions})`);
