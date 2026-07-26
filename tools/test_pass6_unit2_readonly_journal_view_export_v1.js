#!/usr/bin/env node
'use strict';

const assert=require('assert');
const fs=require('fs');
const path=require('path');
const vm=require('vm');
const ROOT=path.resolve(__dirname,'..');
const contractSource=fs.readFileSync(
  path.join(ROOT,'pmp-diagnostic-journal-contract-v1.js'),
  'utf8'
);
const contract=require(path.join(ROOT,'pmp-diagnostic-journal-contract-v1.js'));
const modulePath=path.join(ROOT,'pmp-diagnostic-journal-readonly-view-export-v1.js');
const source=fs.readFileSync(modulePath,'utf8');
const ownerSource=fs.readFileSync(path.join(ROOT,'pmp-diagnostics-owner-v1.js'),'utf8');
const innerSource=fs.readFileSync(
  path.join(ROOT,'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'),
  'utf8'
);
const viewExport=require(modulePath);
let assertions=0;

function same(actual,expected,label){
  assertions++;
  assert.deepStrictEqual(actual,expected,label);
}
function yes(value,label){
  assertions++;
  assert(value,label);
}
function no(value,label){
  assertions++;
  assert(!value,label);
}
function includes(value,expected,label){
  assertions++;
  assert(String(value).includes(expected),label);
}

same(viewExport.version,'1.0.0','module version');
same(viewExport.viewType,'PMP_DIAGNOSTIC_JOURNAL_READONLY_VIEW_V1','view type');
same(viewExport.exportType,'PMP_DIAGNOSTIC_JOURNAL_BOUNDED_EXPORT_V1','export type');
same(viewExport.limits.default_visible_entries,64,'default visible');
same(viewExport.limits.maximum_visible_entries,128,'maximum visible');
same(viewExport.limits.default_export_entries,128,'default export');
same(viewExport.limits.maximum_export_entries,256,'maximum export');
same(viewExport.limits.maximum_export_bytes,262144,'maximum bytes');
yes(Object.isFrozen(viewExport),'module frozen');
yes(Object.isFrozen(viewExport.limits),'limits frozen');

const unavailable=viewExport.create(null);
same(unavailable.available,false,'unavailable adapter');
const unavailableView=unavailable.read();
same(unavailableView.status,'JOURNAL_UNAVAILABLE','unavailable read status');
same(unavailableView.available,false,'unavailable read available');
same(unavailableView.visible_entry_count,0,'unavailable count');
same(unavailableView.entries,[],'unavailable entries');
same(unavailableView.side_effects.journal_appends,0,'unavailable appends');
same(unavailableView.side_effects.persisted_user_data_writes,0,'unavailable user writes');
const unavailableExport=unavailable.exportBundle({created_at:'2026-07-26T09:30:00Z'});
same(unavailableExport.ok,false,'unavailable export');
same(unavailableExport.status,'JOURNAL_UNAVAILABLE','unavailable export status');
same(unavailableExport.bytes,0,'unavailable export bytes');
same(unavailableExport.text,'','unavailable export text');

const journal=contract.createJournal({capacity:256,retention_ms:86400000});
const adapter=viewExport.create(journal);
same(adapter.available,true,'available adapter');
yes(Object.isFrozen(adapter),'adapter frozen');

const empty=adapter.read();
same(empty.type,viewExport.viewType,'empty type');
same(empty.version,'1.0.0','empty version');
same(empty.status,'READY_EMPTY','empty status');
same(empty.available,true,'empty available');
same(empty.entry_count,0,'empty total');
same(empty.visible_entry_count,0,'empty visible');
same(empty.entries,[],'empty entries');
same(empty.disclosure.contract_redaction_required,true,'contract redaction');
same(empty.disclosure.raw_unvalidated_entries_exposed,false,'raw hidden');
same(empty.disclosure.maximum_visible_entries,128,'visible disclosure bound');
same(empty.disclosure.entries_truncated,false,'empty not truncated');
same(empty.side_effects.journal_appends,0,'empty no appends');
same(empty.side_effects.journal_restores,0,'empty no restores');
same(empty.side_effects.local_storage_writes,0,'empty no local storage');
same(empty.side_effects.indexed_db_writes,0,'empty no indexed db');
same(empty.side_effects.network_requests,0,'empty no network');
same(empty.side_effects.dom_mutations,0,'empty no dom');
same(empty.side_effects.route_changes,0,'empty no route');
same(empty.side_effects.repairs,0,'empty no repair');
same(empty.side_effects.persisted_user_data_writes,0,'empty no user writes');
yes(Object.isFrozen(empty),'empty frozen');
yes(Object.isFrozen(empty.side_effects),'empty side effects frozen');

function event(id,kind,trust,severity,code,at,details,refs){
  return {
    type:contract.entryType,
    version:contract.version,
    event_id:id,
    observed_at:at,
    fact_kind:kind,
    severity,
    code,
    source:{owner:'diagnostics_owner',component:'unit_test',channel:'isolated'},
    provenance:{trust,evidence_refs:refs||[]},
    subject:{kind:'test_subject',id},
    summary:'bounded journal test '+id,
    details
  };
}

same(journal.append(
  event(
    'p6u2-observed-001','OBSERVED_FACT','OWNER_ATTESTED','INFO','OBSERVED_READY',
    '2026-07-26T09:30:01Z',
    {status:'ready',password:'DO_NOT_EXPOSE_PASSWORD',nested:{token:'DO_NOT_EXPOSE_TOKEN'}}
  ),
  '2026-07-26T09:30:02Z'
).accepted,true,'append observed');
same(journal.append(
  event(
    'p6u2-derived-002','DERIVED_FACT','SYSTEM_VERIFIED','NOTICE','DERIVED_READY',
    '2026-07-26T09:30:03Z',
    {status:'derived',sequence:2},
    ['audit/pass6/unit2-derived-evidence.json']
  ),
  '2026-07-26T09:30:04Z'
).accepted,true,'append derived');
same(journal.append(
  event(
    'p6u2-inferred-003','INFERRED_CONCLUSION','INFERRED','WARNING','INFERRED_REVIEW',
    '2026-07-26T09:30:05Z',
    {status:'review'},
    ['p6u2-observed-001','p6u2-derived-002']
  ),
  '2026-07-26T09:30:06Z'
).accepted,true,'append inferred');

const populated=adapter.read({limit:3});
same(populated.status,'READY_WITH_ENTRIES','populated status');
same(populated.entry_count,3,'populated total');
same(populated.visible_entry_count,3,'populated visible');
same(populated.entries.map(row=>row.event_id),[
  'p6u2-observed-001','p6u2-derived-002','p6u2-inferred-003'
],'stable entry order');
same(populated.entries[0].details.password,'[REDACTED]','password redacted');
same(populated.entries[0].details.nested.token,'[REDACTED]','token redacted');
no(JSON.stringify(populated).includes('DO_NOT_EXPOSE_PASSWORD'),'password absent');
no(JSON.stringify(populated).includes('DO_NOT_EXPOSE_TOKEN'),'token absent');
same(populated.counts.fact_kind.OBSERVED_FACT,1,'observed count');
same(populated.counts.fact_kind.DERIVED_FACT,1,'derived count');
same(populated.counts.fact_kind.INFERRED_CONCLUSION,1,'inferred count');
same(populated.counts.trust.OWNER_ATTESTED,1,'owner trust count');
same(populated.counts.trust.SYSTEM_VERIFIED,1,'system trust count');
same(populated.counts.trust.INFERRED,1,'inferred trust count');
same(populated.counts.severity.INFO,1,'info count');
same(populated.counts.severity.NOTICE,1,'notice count');
same(populated.counts.severity.WARNING,1,'warning count');
same(populated.journal_status.entry_count,3,'journal status count');
same(populated.disclosure.entries_truncated,false,'all visible');
yes(Object.isFrozen(populated.entries),'entries frozen');
yes(Object.isFrozen(populated.entries[0]),'entry frozen');
same(adapter.read({limit:1}).entries[0].event_id,'p6u2-inferred-003','tail limit');
same(adapter.read({fact_kind:'OBSERVED_FACT'}).visible_entry_count,1,'fact filter');
same(adapter.read({severity:'NOTICE'}).entries[0].event_id,'p6u2-derived-002','severity filter');
same(adapter.read({code:'INFERRED_REVIEW'}).entries[0].event_id,'p6u2-inferred-003','code filter');
same(adapter.read({limit:0}).visible_entry_count,0,'zero limit');
same(adapter.read({limit:0}).disclosure.entries_truncated,true,'zero truncated');

same(adapter.read({limit:-1}).status,'INVALID_LIMIT','negative view limit');
same(adapter.read({limit:129}).status,'INVALID_LIMIT','large view limit');
same(adapter.read({fact_kind:'FACT'}).status,'INVALID_FACT_KIND','bad fact kind');
same(adapter.read({severity:'SEVERE'}).status,'INVALID_SEVERITY','bad severity');
same(adapter.read({code:''}).status,'INVALID_CODE','empty code');
same(adapter.read({unknown:true}).status,'INVALID_OPTIONS','unknown view option');

const exportAt='2026-07-26T09:31:00Z';
const exported=adapter.exportBundle({created_at:exportAt,limit:3});
same(exported.ok,true,'export okay');
same(exported.status,'READY_WITH_ENTRIES','export status');
same(exported.type,viewExport.exportType,'export result type');
yes(exported.bytes>0,'export bytes positive');
yes(exported.bytes<=viewExport.limits.maximum_export_bytes,'export byte bounded');
same(Buffer.byteLength(exported.text,'utf8'),exported.bytes,'export byte identity');
same(exported.bundle.type,viewExport.exportType,'bundle type');
same(exported.bundle.version,'1.0.0','bundle version');
same(exported.bundle.created_at,exportAt,'bundle time');
same(exported.bundle.source_contract.contract_version,contract.version,'contract version linked');
same(exported.bundle.source_contract.entry_type,contract.entryType,'entry type linked');
same(exported.bundle.filter.requested_limit,3,'requested limit recorded');
same(exported.bundle.bounds.maximum_entries,256,'entry bound recorded');
same(exported.bundle.bounds.maximum_bytes,262144,'byte bound recorded');
same(exported.bundle.bounds.selected_before_byte_bound,3,'selected count');
same(exported.bundle.bounds.exported_entries,3,'export count');
same(exported.bundle.bounds.omitted_for_byte_bound,0,'no byte omissions');
same(exported.bundle.bounds.journal_entries_not_selected,0,'no selection omissions');
same(exported.bundle.entries.length,3,'bundle entries');
same(exported.bundle.disclosure.contract_redaction_required,true,'export redaction');
same(exported.bundle.disclosure.raw_unvalidated_entries_exposed,false,'export raw hidden');
same(exported.bundle.disclosure.persisted_user_data_included,false,'no user data');
same(exported.bundle.side_effects.journal_appends,0,'export no append');
same(exported.bundle.side_effects.network_requests,0,'export no network');
same(exported.bundle.side_effects.persisted_user_data_writes,0,'export no user write');
yes(/^[0-9a-f]{16}$/.test(exported.bundle.integrity.entries_fingerprint),'entry fingerprint');
yes(/^[0-9a-f]{16}$/.test(exported.bundle.integrity.bundle_fingerprint),'bundle fingerprint');
includes(exported.text,'\"PMP_DIAGNOSTIC_JOURNAL_BOUNDED_EXPORT_V1\"','text type');
no(exported.text.includes('DO_NOT_EXPOSE_PASSWORD'),'export password absent');
no(exported.text.includes('DO_NOT_EXPOSE_TOKEN'),'export token absent');
same(
  adapter.exportBundle({created_at:exportAt,limit:3}).text,
  exported.text,
  'deterministic export'
);
yes(Object.isFrozen(exported),'export result frozen');
yes(Object.isFrozen(exported.bundle),'export bundle frozen');
yes(Object.isFrozen(exported.bundle.entries),'export entries frozen');

same(adapter.exportBundle({created_at:'bad'}).status,'INVALID_CREATED_AT','bad export time');
same(adapter.exportBundle({created_at:exportAt,limit:257}).status,'INVALID_LIMIT','large export limit');
same(adapter.exportBundle({created_at:exportAt,unknown:true}).status,'INVALID_OPTIONS','unknown export option');

const malformedDiagnostics=viewExport.create({
  diagnostics(){return {type:'wrong'}},
  read(){return []}
});
same(malformedDiagnostics.read().status,'JOURNAL_DIAGNOSTICS_MALFORMED','malformed diagnostics');
const throwingDiagnostics=viewExport.create({
  diagnostics(){throw new Error('bounded')},
  read(){return []}
});
same(throwingDiagnostics.read().status,'JOURNAL_DIAGNOSTICS_ERROR','throwing diagnostics');
const throwingRead=viewExport.create({
  diagnostics(){return journal.diagnostics()},
  read(){throw new Error('bounded')}
});
same(throwingRead.read().status,'JOURNAL_READ_ERROR','throwing read');
const nonArrayRead=viewExport.create({
  diagnostics(){return journal.diagnostics()},
  read(){return {}}
});
same(nonArrayRead.read().status,'JOURNAL_READ_MALFORMED','non-array read');
const rawEntry=journal.read({limit:1})[0];
const malicious=JSON.parse(JSON.stringify(rawEntry));
malicious.details={password:'UNREDACTED_PASSWORD'};
const maliciousRead=viewExport.create({
  diagnostics(){return journal.diagnostics()},
  read(){return [malicious]}
});
same(
  maliciousRead.read().status,
  'JOURNAL_ENTRY_MALFORMED_OR_UNREDACTED',
  'unredacted entry rejected'
);
same(
  maliciousRead.exportBundle({created_at:exportAt}).status,
  'JOURNAL_ENTRY_MALFORMED_OR_UNREDACTED',
  'unredacted export rejected'
);

const largeJournal=contract.createJournal({capacity:256,retention_ms:86400000});
for(let index=0;index<48;index++){
  const details={};
  for(let key=0;key<24;key++)details['bounded_field_'+key]='x'.repeat(512);
  const second=String(index%60).padStart(2,'0');
  const result=largeJournal.append(
    event(
      'p6u2-large-'+String(index).padStart(3,'0'),
      'OBSERVED_FACT',
      'SYSTEM_VERIFIED',
      'DEBUG',
      'LARGE_BOUNDED_ENTRY',
      `2026-07-26T09:32:${second}Z`,
      details,
      ['audit/pass6/unit2-large-fixture.json']
    ),
    `2026-07-26T09:33:${second}Z`
  );
  same(result.accepted,true,'large append '+index);
}
const boundedExport=viewExport.create(largeJournal).exportBundle({
  created_at:'2026-07-26T09:34:00Z',
  limit:48
});
same(boundedExport.ok,true,'bounded large export');
yes(boundedExport.bytes<=viewExport.limits.maximum_export_bytes,'large export byte bound');
same(boundedExport.bundle.bounds.selected_before_byte_bound,48,'large selected');
yes(boundedExport.bundle.bounds.omitted_for_byte_bound>0,'large byte omissions');
yes(boundedExport.bundle.bounds.exported_entries<48,'large entries reduced');
same(
  boundedExport.bundle.bounds.exported_entries+
    boundedExport.bundle.bounds.omitted_for_byte_bound,
  48,
  'large omission accounting'
);
same(Buffer.byteLength(boundedExport.text,'utf8'),boundedExport.bytes,'large byte identity');
same(
  viewExport.create(largeJournal).exportBundle({
    created_at:'2026-07-26T09:34:00Z',
    limit:48
  }).text,
  boundedExport.text,
  'large export deterministic'
);

for(const forbidden of [
  'localStorage',
  'sessionStorage',
  'indexedDB',
  'document.',
  'window.',
  'location.',
  'fetch(',
  'XMLHttpRequest',
  'WebSocket',
  'navigator.',
  'setTimeout(',
  'setInterval(',
  '.append(',
  '.restore('
]){
  no(source.includes(forbidden),'forbidden pure view/export token: '+forbidden);
}
same((source.match(/journal\.read\(/g)||[]).length,1,'single journal read path');
same((source.match(/journal\.diagnostics\(\)/g)||[]).length,1,'single diagnostics path');
includes(source,'contract_redaction_required:true','redaction disclosure present');
includes(source,'persisted_user_data_included:false','user-data disclosure present');
includes(source,'PMP_STABLE_FINGERPRINT_V1','non-cryptographic integrity label explicit');
includes(ownerSource,"id:'diagnostic_journal'","journal card integrated");
includes(ownerSource,'readDiagnosticJournal:journalView','journal read API integrated');
includes(ownerSource,'exportDiagnosticJournal:journalExport','journal export API integrated');
includes(ownerSource,'renderDiagnosticJournal','journal renderer integrated');
includes(ownerSource,'Copy Bounded Journal Export','bounded export action integrated');
includes(ownerSource,'capacity:256,retention_ms:604800000','bounded ephemeral journal');
includes(ownerSource,'limit:64','bounded visible read');
includes(ownerSource,'limit:128','bounded owner export');
no(ownerSource.includes('diagnosticJournal.append'),'owner cannot append');
no(ownerSource.includes('diagnosticJournal.restore'),'owner cannot restore');
no(ownerSource.includes('diagnosticJournal.snapshot'),'owner cannot snapshot');
const contractScript=innerSource.indexOf(
  'pmp-diagnostic-journal-contract-v1.js?fresh=pass6-unit2-readonly-journal-20260726A'
);
const viewScript=innerSource.indexOf(
  'pmp-diagnostic-journal-readonly-view-export-v1.js?fresh=pass6-unit2-readonly-journal-20260726A'
);
const orchestratorScript=innerSource.indexOf(
  'pmp-app-orchestrator-v1.js?fresh=app-orchestrator-final-clean-startup-certification-20260709A'
);
yes(contractScript>=0,'contract load binding present');
yes(viewScript>contractScript,'view loads after contract');
yes(orchestratorScript>viewScript,'orchestrator loads after journal APIs');
same((innerSource.match(/pmp-diagnostic-journal-contract-v1\.js\?/g)||[]).length,1,'single contract load');
same(
  (innerSource.match(/pmp-diagnostic-journal-readonly-view-export-v1\.js\?/g)||[]).length,
  1,
  'single view/export load'
);

const stored=new Map();
const windowStub={
  PMPMountLifecycleDiagnosticsViewV1:null,
  PMPMountLifecycleRuntimeV1:null,
  localStorage:{
    getItem(key){return stored.has(key)?stored.get(key):null},
    setItem(key,value){stored.set(key,String(value))}
  }
};
windowStub.top=windowStub;
const documentStub={
  querySelectorAll(selector){
    if(selector==='script[src]'){
      return [{getAttribute(){return 'pmp-bank-continuous-run-owner-split-diagnostic-v1.js'}}];
    }
    return [];
  },
  head:{appendChild(){throw new Error('unexpected script append')}},
  documentElement:{appendChild(){throw new Error('unexpected script append')}}
};
windowStub.window=windowStub;
windowStub.document=documentStub;
windowStub.navigator={};
windowStub.console=console;
windowStub.setTimeout=function(){throw new Error('unexpected timer')};
windowStub.clearTimeout=function(){};
const ownerContext=vm.createContext(windowStub);
vm.runInContext(contractSource,ownerContext);
vm.runInContext(source,ownerContext);
vm.runInContext(ownerSource,ownerContext);
const ownerApi=windowStub.PMPDiagnosticsOwnerV1;
yes(!!ownerApi,'owner API published');
includes(ownerApi.version,'pass6-unit2','owner P6-U2 version');
const integratedView=ownerApi.readDiagnosticJournal();
same(integratedView.status,'READY_EMPTY','integrated journal empty and ready');
same(integratedView.available,true,'integrated journal available');
same(integratedView.entry_count,0,'integrated journal has no synthetic events');
same(integratedView.side_effects.journal_appends,0,'integrated read cannot append');
const integratedExport=ownerApi.exportDiagnosticJournal();
same(integratedExport.ok,true,'integrated bounded export available');
same(integratedExport.status,'READY_EMPTY','integrated empty export status');
yes(integratedExport.bytes<=262144,'integrated export byte bounded');
same(integratedExport.bundle.bounds.exported_entries,0,'integrated export has no synthetic events');
no(
  Array.from(stored.keys()).some(key=>/diagnostic.*journal|journal.*diagnostic/i.test(key)),
  'journal is not persisted'
);

console.log(
  `PASS: P6-U2 read-only diagnostic journal view and bounded export (${assertions}/${assertions})`
);
