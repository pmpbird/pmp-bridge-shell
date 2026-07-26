'use strict';
const assert=require('assert');
const path=require('path');
const fs=require('fs');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-diagnostic-journal-contract-v1.js'),'utf8');
const api=require(path.join(ROOT,'pmp-diagnostic-journal-contract-v1.js'));
let assertions=0;
function check(value,message){assert.ok(value,message);assertions++}
function equal(actual,expected,message){assert.deepStrictEqual(actual,expected,message);assertions++}
function event(overrides){
  return Object.assign({
    type:'PMP_DIAGNOSTIC_JOURNAL_ENTRY_V1',
    version:'1.0.0',
    event_id:'evt-001',
    observed_at:'2026-07-26T08:00:00.000Z',
    fact_kind:'OBSERVED_FACT',
    severity:'INFO',
    code:'MOUNT_READY',
    source:{owner:'mount_registry_owner',component:'mount_runtime',channel:'owner_event'},
    provenance:{trust:'OWNER_ATTESTED',evidence_refs:['receipt:001']},
    subject:{system:'mount_registry',operation_id:'op-001'},
    summary:'Mount became ready',
    details:{state:'READY',duration_ms:25}
  },overrides||{});
}

equal(api.version,'1.0.0');
equal(api.entryType,'PMP_DIAGNOSTIC_JOURNAL_ENTRY_V1');
equal(api.snapshotType,'PMP_DIAGNOSTIC_JOURNAL_SNAPSHOT_V1');
equal(api.factKinds,['OBSERVED_FACT','DERIVED_FACT','INFERRED_CONCLUSION']);
equal(api.trustLevels,['OWNER_ATTESTED','SYSTEM_VERIFIED','OBSERVER_REPORTED','INFERRED']);
equal(api.severityLevels,['DEBUG','INFO','NOTICE','WARNING','ERROR','CRITICAL']);
equal(api.limits.default_capacity,256);
equal(api.limits.max_capacity,4096);
equal(api.redaction.marker,'[REDACTED]');

const journal=api.createJournal({capacity:3,retention_ms:1000});
equal(journal.diagnostics().entry_count,0);
equal(journal.diagnostics().last_sequence,0);
equal(journal.diagnostics().capacity,3);
equal(journal.diagnostics().retention_ms,1000);
equal(journal.diagnostics().side_effects.persisted_user_data_writes,0);

let result=journal.append(event(),'2026-07-26T08:00:00.100Z');
equal(result.accepted,true);
equal(result.idempotent,false);
equal(result.sequence,1);
equal(result.evicted,0);
equal(result.expired,0);
equal(journal.read().length,1);
equal(journal.read()[0].fact_kind,'OBSERVED_FACT');
equal(journal.read()[0].provenance.trust,'OWNER_ATTESTED');

const copy=journal.read();
copy[0].summary='changed outside';
equal(journal.read()[0].summary,'Mount became ready');

result=journal.append(event(),'2026-07-26T08:00:00.100Z');
equal(result.accepted,true);
equal(result.idempotent,true);
equal(result.sequence,1);
equal(journal.read().length,1);

const conflict=journal.append(event({summary:'different'}),'2026-07-26T08:00:00.200Z');
equal(conflict.accepted,false);
equal(conflict.rejection.code,'CONFLICTING_DUPLICATE');
equal(journal.read().length,1);

result=journal.append(event({
  event_id:'evt-002',
  observed_at:'2026-07-26T08:00:00.200Z',
  fact_kind:'DERIVED_FACT',
  provenance:{trust:'SYSTEM_VERIFIED',evidence_refs:['evt-001']},
  code:'MOUNT_DURATION_CLASS',
  summary:'Mount duration classified'
}),'2026-07-26T08:00:00.300Z');
equal(result.accepted,true);
equal(result.sequence,2);

result=journal.append(event({
  event_id:'evt-003',
  observed_at:'2026-07-26T08:00:00.300Z',
  fact_kind:'INFERRED_CONCLUSION',
  provenance:{trust:'INFERRED',evidence_refs:['evt-001','evt-002']},
  code:'POSSIBLE_SLOW_OWNER',
  summary:'Owner may be slow'
}),'2026-07-26T08:00:00.400Z');
equal(result.accepted,true);
equal(result.sequence,3);
equal(journal.read({fact_kind:'INFERRED_CONCLUSION'}).length,1);
equal(journal.read({severity:'INFO'}).length,3);
equal(journal.read({code:'MOUNT_READY'}).length,1);
equal(journal.read({limit:2}).map(x=>x.sequence),[2,3]);

const inferredTrust=journal.append(event({
  event_id:'evt-bad-inferred',
  fact_kind:'INFERRED_CONCLUSION',
  provenance:{trust:'OWNER_ATTESTED',evidence_refs:['evt-001']}
}),'2026-07-26T08:00:00.500Z');
equal(inferredTrust.accepted,false);
equal(inferredTrust.rejection.code,'INFERENCE_TRUST_REQUIRED');

const inferredBasis=journal.append(event({
  event_id:'evt-bad-basis',
  fact_kind:'INFERRED_CONCLUSION',
  provenance:{trust:'INFERRED',evidence_refs:[]}
}),'2026-07-26T08:00:00.500Z');
equal(inferredBasis.accepted,false);
equal(inferredBasis.rejection.code,'INFERENCE_BASIS_REQUIRED');

const factTrust=journal.append(event({
  event_id:'evt-bad-fact',
  provenance:{trust:'INFERRED',evidence_refs:['x']}
}),'2026-07-26T08:00:00.500Z');
equal(factTrust.accepted,false);
equal(factTrust.rejection.code,'FACT_CANNOT_USE_INFERRED_TRUST');

const derivedBasis=journal.append(event({
  event_id:'evt-bad-derived',
  fact_kind:'DERIVED_FACT',
  provenance:{trust:'SYSTEM_VERIFIED',evidence_refs:[]}
}),'2026-07-26T08:00:00.500Z');
equal(derivedBasis.accepted,false);
equal(derivedBasis.rejection.code,'DERIVED_BASIS_REQUIRED');

const unknown=journal.append(Object.assign(event({event_id:'evt-unknown'}),{extra:true}),'2026-07-26T08:00:00.500Z');
equal(unknown.accepted,false);
equal(unknown.rejection.code,'UNKNOWN_FIELD');

const future=journal.append(event({
  event_id:'evt-future',
  observed_at:'2026-07-26T09:00:00.000Z'
}),'2026-07-26T08:00:00.500Z');
equal(future.accepted,false);
equal(future.rejection.code,'FUTURE_OBSERVATION');

const regression=journal.append(event({
  event_id:'evt-regression',
  observed_at:'2026-07-26T07:59:59.000Z'
}),'2026-07-26T08:00:00.050Z');
equal(regression.accepted,false);
equal(regression.rejection.code,'RECORDED_TIME_REGRESSION');
equal(journal.read().length,3);

const redacting=api.createJournal({capacity:2,retention_ms:10000});
result=redacting.append(event({
  event_id:'evt-secret',
  summary:'Bearer abcdefghijklmnopqrstuvwxyz',
  subject:{system:'diagnostics',absolute_path:'/Users/private/file'},
  details:{
    token:'secret-token',
    password:'secret-password',
    safe:'visible',
    nested:{email:'person@example.com',value:'safe'}
  }
}),'2026-07-26T08:00:00.100Z');
equal(result.accepted,true);
const protectedEntry=redacting.read()[0];
equal(protectedEntry.summary,'[REDACTED]');
equal(protectedEntry.subject.absolute_path,'[REDACTED]');
equal(protectedEntry.details.token,'[REDACTED]');
equal(protectedEntry.details.password,'[REDACTED]');
equal(protectedEntry.details.safe,'visible');
equal(protectedEntry.details.nested.email,'[REDACTED]');
check(protectedEntry.redaction.redacted>=5);

const long='x'.repeat(600);
redacting.append(event({
  event_id:'evt-long',
  observed_at:'2026-07-26T08:00:00.200Z',
  summary:'bounded',
  details:{long,array:Array.from({length:40},(_,i)=>i)}
}),'2026-07-26T08:00:00.200Z');
equal(redacting.read()[1].details.long.length,513);
equal(redacting.read()[1].details.array.length,32);
check(redacting.read()[1].redaction.truncated>=1);
check(redacting.read()[1].redaction.dropped>=8);

result=redacting.append(event({
  event_id:'evt-evict',
  observed_at:'2026-07-26T08:00:00.300Z'
}),'2026-07-26T08:00:00.300Z');
equal(result.evicted,1);
equal(redacting.read().map(x=>x.event_id),['evt-long','evt-evict']);

const expiring=api.createJournal({capacity:5,retention_ms:1000});
expiring.append(event({event_id:'old'}),'2026-07-26T08:00:00.100Z');
result=expiring.append(event({
  event_id:'new',
  observed_at:'2026-07-26T08:00:02.000Z'
}),'2026-07-26T08:00:02.000Z');
equal(result.expired,1);
equal(expiring.read().map(x=>x.event_id),['new']);

const snap=redacting.snapshot('2026-07-26T08:00:00.400Z');
equal(snap.type,'PMP_DIAGNOSTIC_JOURNAL_SNAPSHOT_V1');
equal(snap.version,'1.0.0');
equal(snap.entries.length,2);
check(/^[0-9a-f]{16}$/.test(snap.integrity));
equal(JSON.stringify(snap).includes('secret-token'),false);
equal(JSON.stringify(snap).includes('person@example.com'),false);

const restored=api.createJournal({capacity:2,retention_ms:10000});
result=restored.restore(snap,'2026-07-26T08:00:00.500Z');
equal(result.restored,true);
equal(result.entries,2);
equal(restored.read(),redacting.read());
equal(restored.diagnostics().last_sequence,3);

const tampered=JSON.parse(JSON.stringify(snap));
tampered.entries[0].summary='tampered';
const before=restored.read();
result=restored.restore(tampered,'2026-07-26T08:00:00.600Z');
equal(result.restored,false);
equal(result.rejection.code,'SNAPSHOT_INTEGRITY_MISMATCH');
equal(restored.read(),before);

const configMismatch=api.createJournal({capacity:3,retention_ms:10000});
result=configMismatch.restore(snap,'2026-07-26T08:00:00.600Z');
equal(result.restored,false);
equal(result.rejection.code,'SNAPSHOT_CONFIG_MISMATCH');

assert.throws(()=>api.createJournal({capacity:0}),/INVALID_CAPACITY/);assertions++;
assert.throws(()=>api.createJournal({capacity:4097}),/INVALID_CAPACITY/);assertions++;
assert.throws(()=>api.createJournal({retention_ms:0}),/INVALID_RETENTION/);assertions++;
assert.throws(()=>api.createJournal({unknown:true}),/UNKNOWN_FIELD/);assertions++;
assert.throws(()=>journal.read({limit:4}),/INVALID_LIMIT/);assertions++;
assert.throws(()=>journal.read({unknown:true}),/UNKNOWN_FIELD/);assertions++;
assert.throws(()=>journal.snapshot('bad-time'),/INVALID_TIMESTAMP/);assertions++;

const sourceForbidden=[
  'localStorage.setItem',
  'indexedDB',
  'fetch(',
  'XMLHttpRequest',
  'document.',
  'location.',
  'postMessage(',
  'applyOwnerEvent',
  'mount(',
  'repair(',
  'route('
];
for(const token of sourceForbidden)equal(source.includes(token),false,'forbidden source token '+token);
check(source.includes('OBSERVED_FACT'));
check(source.includes('INFERRED_CONCLUSION'));
check(source.includes('SENSITIVE_KEY'));
check(source.includes('FAIL_PASSIVE_VIOLATION'));
check(Object.isFrozen(api));
check(Object.isFrozen(api.factKinds));

const status=journal.diagnostics();
equal(status.type,'PMP_DIAGNOSTIC_JOURNAL_STATUS_V1');
check(status.rejection_count>=7);
equal(status.side_effects.local_storage_writes,0);
equal(status.side_effects.indexed_db_writes,0);
equal(status.side_effects.network_requests,0);
equal(status.side_effects.dom_mutations,0);
equal(status.side_effects.route_changes,0);
equal(status.side_effects.repairs,0);

console.log(`PASS: P6-U1 diagnostic journal contract (${assertions} assertions)`);
