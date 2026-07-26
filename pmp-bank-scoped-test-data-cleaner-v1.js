(()=>{
'use strict';
const V='3.0.0-pass9-unit3-delete-default-deny';
const denial={type:'PMP_BANK_SCOPED_TEST_DATA_CLEANER_V2',version:V,status:'DELETE_DENIED_BY_DEFAULT',canonical_owner:'bank_screen_owner',at:new Date().toISOString(),reason:'Legacy broad Bank cleanup is held. Use an exact user-confirmed owner action for one record.',legacy_dom_painter_disabled:true,recurring_scan_disabled:true,automatic_test_data_delete:false,bulk_record_delete:false,storage_migration:false,effects:{dom_mutations:0,storage_writes:0,storage_deletes:0,bank_mutations:0,persisted_user_data_changed:false}};
function scan(){return denial}
function candidates(){return[]}
window.PMPBankScopedTestDataCleanerV1={version:V,mode:'PASSIVE_DELETE_DEFAULT_DENY',scan,candidates,last:()=>denial,rule:'Legacy broad cleanup is disabled. Exact user-confirmed owner actions are required; no recurring painter or automatic deletion remains.'};
})();
