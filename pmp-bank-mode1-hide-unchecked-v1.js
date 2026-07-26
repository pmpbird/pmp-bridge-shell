(()=>{
'use strict';
const V='5.0.0-pass9-unit3-passive-compatibility-held';
let last={type:'PMP_BANK_MODE1_HIDE_UNCHECKED_V2',version:V,status:'PASSIVE_COMPATIBILITY_HELD',canonical_owner:'continuous_run_level_owner',at:new Date().toISOString(),reason:'script_load',legacy_dom_painter_disabled:true,recurring_scan_disabled:true,project_registry_writer_disabled:true,rule:'The canonical Continuous Run Owner now renders the Bank Owner slot. This legacy painter remains as a no-effect compatibility name only.',effects:{dom_mutations:0,storage_writes:0,storage_deletes:0,bank_mutations:0,persisted_user_data_changed:false}};
function scan(reason){last=Object.assign({},last,{at:new Date().toISOString(),reason:String(reason&&reason.type||reason||'manual')});return last}
window.PMPBankMode1HideUncheckedV1={version:V,mode:'PASSIVE_COMPATIBILITY_HELD',scan,last:()=>last,rule:last.rule};
})();
