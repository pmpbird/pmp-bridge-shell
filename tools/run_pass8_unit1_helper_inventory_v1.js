#!/usr/bin/env node
'use strict';
const crypto=require('crypto');
const fs=require('fs');
const path=require('path');
const vm=require('vm');
const {execFileSync}=require('child_process');
const ROOT=path.resolve(__dirname,'..');
const RULES='pmp-pass8-helper-rules-v1.js';
const LEGACY='pmp-helper-registry-v1.js';

function stable(value){
  if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
  if(value&&typeof value==='object'){
    return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+stable(value[key])).join(',')+'}';
  }
  return JSON.stringify(value);
}
function digest(value){
  return crypto.createHash('sha256').update(
    Buffer.isBuffer(value)?value:Buffer.from(stable(value))
  ).digest('hex');
}
function shaFile(relative){
  return crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,relative))).digest('hex');
}
function tree(){
  return execFileSync('git',['ls-tree','-r','--name-only','HEAD'],{cwd:ROOT,encoding:'utf8'})
    .trim().split('\n').filter(Boolean);
}
function sandboxRun(relative){
  const rows=new Map();
  const storage={
    setItem(key,value){rows.set(String(key),String(value))},
    getItem(key){return rows.has(String(key))?rows.get(String(key)):null},
    removeItem(key){rows.delete(String(key))}
  };
  const document={querySelectorAll(){return []}};
  const host={localStorage:storage,document};
  host.top=host;
  host.window=host;
  const context={
    window:host,
    localStorage:storage,
    document,
    setTimeout(){return 0},
    clearTimeout(){},
    console:{log(){},warn(){},error(){}},
    Date,
    JSON,
    Array,
    Object,
    String,
    Number,
    Boolean,
    RegExp,
    Math
  };
  vm.runInNewContext(fs.readFileSync(path.join(ROOT,relative),'utf8'),context,{
    filename:relative,
    timeout:1000
  });
  return {host,rows};
}
function parsed(rows,key){
  const value=rows.get(key);
  if(typeof value!=='string')throw new Error(`missing sandbox storage ${key}`);
  return JSON.parse(value);
}

function build(){
  const tracked=tree();
  const trackedSet=new Set(tracked);
  const rulesRun=sandboxRun(RULES);
  const api=rulesRun.host.PMPPass8HelperRulesV1;
  if(!api||typeof api.getRegistry!=='function')throw new Error('Pass 8 rules API unavailable');
  const declared=JSON.parse(JSON.stringify(api.getRegistry()));
  const legacyRun=sandboxRun(LEGACY);
  const legacy=parsed(legacyRun.rows,'pmp_helper_registry_v1');
  const legacySnapshot=parsed(legacyRun.rows,'pmp_helper_registry_snapshot_v1');
  const p7=JSON.parse(fs.readFileSync(
    path.join(ROOT,'audit/pass7/pass7-section-owner-unit1-inventory-v1.json'),'utf8'
  ));
  const p7Owners=p7.inventory.declared_owners.map(row=>row.id).sort();
  const helperNamedRoot=tracked.filter(relative=>
    !relative.includes('/')&&relative.startsWith('pmp-')&&
    /helper/i.test(relative)&&/\.(?:js|mjs|cjs|html)$/.test(relative)
  ).sort();
  const declaredFiles=declared.map(row=>row.file);
  const declaredSet=new Set(declaredFiles);
  const declaredOwners=Array.from(new Set(declared.map(row=>row.owner))).sort();
  const unresolvedOwnerLabels=declaredOwners.filter(owner=>!p7Owners.includes(owner));
  const missingFiles=declaredFiles.filter(relative=>!trackedSet.has(relative)).sort();
  const duplicateIds=declared.map(row=>row.id).filter((id,index,all)=>all.indexOf(id)!==index);
  const duplicateFiles=declaredFiles.filter((file,index,all)=>all.indexOf(file)!==index);
  const helperNamedUndeclared=helperNamedRoot.filter(
    relative=>!declaredSet.has(relative)&&relative!==RULES
  );
  const storageKeys=Array.from(new Set(declared.flatMap(row=>row.storage||[]))).sort();
  const panelIds=Array.from(new Set(declared.flatMap(row=>row.panels||[]))).sort();
  const growthHelpers=declared.filter(row=>row.growth_source&&row.growth_source!=='none');
  const ownerRows=declaredOwners.map(owner=>({
    owner_label:owner,
    helper_count:declared.filter(row=>row.owner===owner).length,
    exact_p7_owner_match:p7Owners.includes(owner)
  }));
  const result={
    type:'PMP_PASS8_UNIT1_HELPER_INVENTORY_RESULT_V1',
    version:'1.0.0',
    status:'PASS',
    sources:{
      rules:RULES,
      rules_sha256:shaFile(RULES),
      legacy_registry:LEGACY,
      legacy_registry_sha256:shaFile(LEGACY),
      p7_owner_inventory:'audit/pass7/pass7-section-owner-unit1-inventory-v1.json',
      p7_owner_inventory_sha256:shaFile(
        'audit/pass7/pass7-section-owner-unit1-inventory-v1.json'
      )
    },
    declared_helpers:declared,
    owner_rows:ownerRows,
    legacy_helpers:legacy.helpers,
    legacy_snapshot_summary:legacySnapshot.summary,
    helper_named_root_sources:helperNamedRoot,
    helper_named_undeclared_sources:helperNamedUndeclared,
    unresolved_owner_labels:unresolvedOwnerLabels,
    storage_keys:storageKeys,
    panel_ids:panelIds,
    growth_helpers:growthHelpers,
    counts:{
      tracked_files:tracked.length,
      declared_helpers:declared.length,
      declared_unique_ids:new Set(declared.map(row=>row.id)).size,
      declared_unique_files:new Set(declaredFiles).size,
      declared_files_present:declaredFiles.length-missingFiles.length,
      declared_files_missing:missingFiles.length,
      accepted_helpers:declared.filter(row=>row.registration==='accepted').length,
      diagnostic_only_helpers:declared.filter(row=>row.registration==='diagnostic_only').length,
      legacy_helpers_declared:declared.filter(row=>row.registration==='legacy').length,
      growth_helpers:growthHelpers.length,
      declared_owner_labels:declaredOwners.length,
      exact_p7_owner_label_matches:declaredOwners.filter(owner=>p7Owners.includes(owner)).length,
      unresolved_owner_labels:unresolvedOwnerLabels.length,
      legacy_registry_helpers:legacy.helpers.length,
      helper_named_root_sources:helperNamedRoot.length,
      helper_named_undeclared_sources:helperNamedUndeclared.length,
      storage_keys:storageKeys.length,
      panel_ids:panelIds.length,
      duplicate_ids:duplicateIds.length,
      duplicate_files:duplicateFiles.length
    },
    conflicts:{
      missing_declared_files:missingFiles,
      duplicate_ids:duplicateIds,
      duplicate_files:duplicateFiles,
      owner_labels_not_exact_p7_ids:unresolvedOwnerLabels,
      helper_named_sources_without_pass8_declaration:helperNamedUndeclared,
      legacy_registry_parent_owner_vocabulary:'P7_OWNER_IDS',
      pass8_rules_owner_vocabulary:'NON_P7_ALIASES_AND_ADDITIONAL_DOMAINS',
      disposition:'HOLD_AS_OBSERVED_CONFLICT_NO_AUTHORITY_UNTIL_P8_U2_CONTRACT'
    },
    effects:{
      production_files_changed:false,
      browser_launched:false,
      network_requests:false,
      storage_writes:false,
      route_changes:false,
      mounts:false,
      bank_mutations:false,
      repairs:false,
      live_observation_performed:false,
      formal_proof_performed:false,
      persisted_user_data_changed:false,
      storage_migration_performed:false,
      production_behavior_activated:false
    },
    claim_ceiling:'Read-only static Helper inventory. Sandboxed source evaluation uses in-memory storage only and grants no Helper, owner, mount, route, Bank, storage, or production authority.'
  };
  result.result_sha256=digest(result);
  return result;
}
function verifyResultHash(result){
  if(!result||typeof result.result_sha256!=='string')return false;
  const copy=JSON.parse(JSON.stringify(result));
  const expected=copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy)===expected;
}
if(require.main===module)process.stdout.write(JSON.stringify(build(),null,2)+'\n');
module.exports={build,verifyResultHash,digest};
