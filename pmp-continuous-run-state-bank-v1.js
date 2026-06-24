(function(){
  'use strict';
  const OWNER='pmp-continuous-run-state-bank-v1';
  const STATE_KEY='pmp_continuous_run_state_bank_v1';
  const RECEIPTS_KEY='pmp_continuous_run_state_receipts_v1';
  const MANIFEST_KEY='pmp_continuous_run_state_manifest_v1';
  const VERSION='1.0.9-dashboard-owned-api';
  function now(){return new Date().toISOString()}
  function parse(k,fallback){try{const v=localStorage.getItem(k);return v?JSON.parse(v):fallback}catch(e){return fallback}}
  function save(k,v){localStorage.setItem(k,JSON.stringify(v,null,2));return v}
  function hash(s){let h=2166136261;s=String(s||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,'0')}
  function clone(x){try{return JSON.parse(JSON.stringify(x))}catch(e){return x}}
  function defaults(){return{type:'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1',version:VERSION,owner:OWNER,created_at:now(),updated_at:now(),manual_clear_required:true,current_packet:'',current_item:'',packet_queue:[],packet_1_5_active_items:[],last_valid_receipt:null,next_safe_action:'',blocked_items:[],watch_items:[],passed_items:[],helper_owner_registry:{},context_recovery_state:{status:'not_checked',last_check_at:null,missing:[]},last_run_status:'not_started',last_stop_reason:'',last_resume_point:'',export_snapshot:null,notes:''}}
  function readRunState(){const s=parse(STATE_KEY,null);if(s&&s.type){return s}return save(STATE_KEY,defaults())}
  function readReceipts(){const r=parse(RECEIPTS_KEY,[]);return Array.isArray(r)?r:[]}
  function buildManifest(state,receipts){const st=JSON.stringify(state||readRunState());const rt=JSON.stringify(receipts||readReceipts());return{type:'PMP_CONTINUOUS_RUN_STATE_MANIFEST_V1',owner:OWNER,at:now(),state_key:STATE_KEY,receipts_key:RECEIPTS_KEY,manifest_key:MANIFEST_KEY,state_chars:st.length,receipt_count:(receipts||readReceipts()).length,state_hash:hash(st),receipts_hash:hash(rt),manual_clear_required:true}}
  function writeManifest(){return save(MANIFEST_KEY,buildManifest(readRunState(),readReceipts()))}
  function appendReceipt(receipt){const receipts=readReceipts();const r=Object.assign({type:'PMP_RUN_STATE_RECEIPT',owner:OWNER,at:now()},receipt||{});r.id=r.id||('run_receipt_'+Date.now()+'_'+Math.random().toString(16).slice(2));receipts.push(r);save(RECEIPTS_KEY,receipts);const state=readRunState();state.last_valid_receipt=r;state.updated_at=now();save(STATE_KEY,state);writeManifest();return r}
  function writeRunState(update,receipt){const state=Object.assign(readRunState(),clone(update||{}));state.version=VERSION;state.updated_at=now();save(STATE_KEY,state);const r=appendReceipt(Object.assign({type:'PMP_RUN_STATE_UPDATED',update_keys:Object.keys(update||{})},receipt||{}));return{state:readRunState(),receipt:r,manifest:writeManifest()}}
  function setCurrentPacket(packetId){return writeRunState({current_packet:String(packetId||'')},{type:'PMP_CURRENT_PACKET_SET',packet:String(packetId||'')})}
  function setCurrentItem(itemId){return writeRunState({current_item:String(itemId||'')},{type:'PMP_CURRENT_ITEM_SET',item:String(itemId||'')})}
  function setNextAction(action){return writeRunState({next_safe_action:String(action||'')},{type:'PMP_NEXT_SAFE_ACTION_SET',next_safe_action:String(action||'')})}
  function setPacketQueue(queue){return writeRunState({packet_queue:Array.isArray(queue)?queue:[]},{type:'PMP_PACKET_QUEUE_SET',count:Array.isArray(queue)?queue.length:0})}
  function setActiveItems(items){return writeRunState({packet_1_5_active_items:Array.isArray(items)?items:[]},{type:'PMP_ACTIVE_ITEMS_SET',count:Array.isArray(items)?items.length:0})}
  function addUnique(list,item){const s=readRunState();const arr=Array.isArray(s[list])?s[list]:[];const id=(item&&item.id)||String(item||'');if(!arr.some(x=>((x&&x.id)||String(x))===id))arr.push(item);return arr}
  function markItemPassed(itemId,note){return writeRunState({passed_items:addUnique('passed_items',{id:String(itemId||''),note:String(note||''),at:now()})},{type:'PMP_ITEM_PASSED',item:String(itemId||'')})}
  function markItemBlocked(itemId,reason){return writeRunState({blocked_items:addUnique('blocked_items',{id:String(itemId||''),reason:String(reason||''),at:now()})},{type:'PMP_ITEM_BLOCKED',item:String(itemId||''),reason:String(reason||'')})}
  function markItemWatch(itemId,reason){return writeRunState({watch_items:addUnique('watch_items',{id:String(itemId||''),reason:String(reason||''),at:now()})},{type:'PMP_ITEM_WATCH',item:String(itemId||''),reason:String(reason||'')})}
  function setHelperOwner(surface,helperId){const s=readRunState();const reg=s.helper_owner_registry||{};reg[String(surface||'unknown')]=String(helperId||'');return writeRunState({helper_owner_registry:reg},{type:'PMP_HELPER_OWNER_SET',surface:String(surface||''),helper:String(helperId||'')})}
  function recordStop(reason){const s=readRunState();const rp=((s.current_packet||'')+' / '+(s.current_item||'')).trim();return writeRunState({last_run_status:'stopped',last_stop_reason:String(reason||'manual_or_unknown'),last_resume_point:rp==='/'?'':rp},{type:'PMP_RUN_STOP_RECORDED',reason:String(reason||'manual_or_unknown')})}
  function recordResume(){return writeRunState({last_run_status:'resumed',last_stop_reason:'',context_recovery_state:{status:'resume_recorded',last_check_at:now(),missing:[]}},{type:'PMP_RUN_RESUME_RECORDED'})}
  function exportResumePack(){const state=readRunState();const receipts=readReceipts();const manifest=buildManifest(state,receipts);save(MANIFEST_KEY,manifest);return{type:'PMP_CONTINUOUS_RUN_RESUME_PACK_V1',owner:OWNER,exported_at:now(),state,receipts,manifest}}
  function clearCurrentState(){const old=readRunState();const removed=readReceipts().length;const s=defaults();s.created_at=old.created_at||s.created_at;s.updated_at=now();save(STATE_KEY,s);save(RECEIPTS_KEY,[]);const manifest=writeManifest();return{ok:true,changed:true,removed_receipts:removed,state:s,manifest}}
  function manualClear(confirmText){if(String(confirmText)!=='MANUAL CLEAR RUN STATE')return{ok:false,reason:'confirmation_required',required:'MANUAL CLEAR RUN STATE'};localStorage.removeItem(STATE_KEY);localStorage.removeItem(RECEIPTS_KEY);localStorage.removeItem(MANIFEST_KEY);return{ok:true,cleared_at:now()}}
  function patch(){readRunState();writeManifest()}
  window.PMPContinuousRunStateBankV1={version:VERSION,owner:OWNER,keys:{STATE_KEY,RECEIPTS_KEY,MANIFEST_KEY},readRunState,readReceipts,writeRunState,appendReceipt,setCurrentPacket,setCurrentItem,setNextAction,setPacketQueue,setActiveItems,markItemPassed,markItemBlocked,markItemWatch,setHelperOwner,recordStop,recordResume,exportResumePack,clearCurrentState,manualClear,writeManifest,buildManifest,patch};
  patch();
})();
