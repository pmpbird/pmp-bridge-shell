#!/usr/bin/env node
import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('pmp-route-guardian-current-loader-v22.html','utf8');
const map=JSON.parse(fs.readFileSync('pmp-current-map-v12.json','utf8'));
function extract(name){
  const marker=`function ${name}(`, start=html.indexOf(marker);
  if(start<0)throw new Error(`missing function ${name}`);
  const brace=html.indexOf('{',start); let depth=0;
  for(let i=brace;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  throw new Error(`unclosed function ${name}`);
}
const source=[extract('handoffError'),extract('consumeCurrentAppHandoff')].join('\n');
function RouteError(code,message,details){this.code=code;this.message=message;this.details=details||null;}
const storageWrites=[]; const navigationAssignments=[];
const context={
  resolver:{RouteError,handoffType:'PMP_ROUTE_HANDOFF_V1',mapPath:'pmp-current-map-v12.json'},
  location:{pathname:`/${map.route_guardian.path}`},decodeURIComponent,Object,
  localStorage:{setItem:(...args)=>storageWrites.push(args)},
  navigationAssignments
};
vm.createContext(context); vm.runInContext(source,context);
const canonical={type:'PMP_ROUTE_HANDOFF_V1',role:'current_app',map_path:'pmp-current-map-v12.json',map_version:String(map.app_version),route_epoch:String(map.route_epoch),path:String(map.current_app.path)};
function runCase(name,handoff,pathname=`/${map.route_guardian.path}`){
  context.location.pathname=pathname;
  const beforeStorage=storageWrites.length,beforeNav=navigationAssignments.length;
  try{
    const result=context.consumeCurrentAppHandoff({map},handoff);
    return {name,accepted:true,contract:JSON.parse(JSON.stringify(result.contract)),storage_delta:storageWrites.length-beforeStorage,navigation_delta:navigationAssignments.length-beforeNav};
  }catch(error){
    return {name,accepted:false,code:String(error&&error.code||'ERROR'),storage_delta:storageWrites.length-beforeStorage,navigation_delta:navigationAssignments.length-beforeNav};
  }
}
const cases=[];
cases.push(runCase('canonical_current_map_handoff',canonical));
for(const field of ['type','role','map_path','map_version','route_epoch','path']){const h={...canonical};delete h[field];cases.push(runCase(`missing_${field}`,h));}
for(const [name,field,value] of [
 ['wrong_type','type','OTHER'],['wrong_role','role','reload_owner'],['wrong_map_path','map_path','pmp-current-map-v11.json'],
 ['wrong_map_version','map_version','stale'],['wrong_route_epoch','route_epoch','stale'],['wrong_destination','path','pmp-current-reload-owner-v27.html'],
 ['historical_map','map_path','pmp-current-map-v10.json'],['hard_coded_destination','path','hard-coded.html'],['saved_route_destination','path','saved-route.html'],
 ['owner_destination','path','owner.html'],['pointer_destination','path','pointer.html'],['implicit_fallback_destination','path','fallback.html']
])cases.push(runCase(name,{...canonical,[field]:value}));
cases.push(runCase('wrong_source_consumer',canonical,'/not-route-guardian.html'));
const positive=cases[0]; if(!positive.accepted)throw new Error('canonical handoff rejected');
for(const c of cases.slice(1))if(c.accepted)throw new Error(`invalid handoff accepted: ${c.name}`);
for(const c of cases)if(c.storage_delta!==0||c.navigation_delta!==0)throw new Error(`side effect detected: ${c.name}`);
const receipt={type:'PMP_PASS3_UNIT3_ISOLATED_HANDOFF_PROOF_V1',status:'PASS',scope:'isolated_node_vm_only',canonical_accepts:1,fail_closed_rejections:cases.length-1,total_cases:cases.length,zero_navigation_assignments:true,zero_persisted_user_data_writes:true,cases};
fs.writeFileSync('audit/pass3/pass3-route-guardian-handoff-unit3-isolated-proof-v1.json',JSON.stringify(receipt,null,2)+'\n');
console.log(`PASS: ${receipt.canonical_accepts} canonical handoff accepted; ${receipt.fail_closed_rejections} invalid handoffs rejected; zero side effects`);
