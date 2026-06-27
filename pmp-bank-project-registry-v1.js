(()=>{
'use strict';
const V='1.0.3-data-only-bank-screen-owner';
const K='pmp_bank_project_registry_v1';
const R='pmp_bank_project_registry_v1_receipt';
const CORE={'bank-project-bank-system-000001':1,'bank-project-resident-system-000002':1,'bank-project-continuous-run-engine-000003':1};
function W(){try{return window.top||window}catch(e){return window}}
function get(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function put(k,v){try{W().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function hash(s){let x=2166136261;s=String(s||'');for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)}return(x>>>0).toString(16).padStart(8,'0')}
function idFrom(name){let base=clean(name).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'project';return 'bank-project-'+base+'-'+hash(base).slice(0,6)}
function seed(){let now=new Date().toISOString();return {type:'BANK_PROJECT_REGISTRY_V1',version:V,rule:'Bank is information only. It stores projects, packets, proof, receipts, source info, and history. It does not do engine work.',created_at:now,updated_at:now,projects:[{id:'bank-project-bank-system-000001',name:'Bank System',category:'Information Bank',status:'active',item_count:0,created_at:now,updated_at:now},{id:'bank-project-resident-system-000002',name:'Resident System',category:'Resident',status:'active',item_count:0,created_at:now,updated_at:now},{id:'bank-project-continuous-run-engine-000003',name:'Continuous Run Engine',category:'Engine',status:'paused',item_count:0,created_at:now,updated_at:now}]}}
function reg(){let r=get(K,null);if(!r||!Array.isArray(r.projects))r=seed();return r}
function save(r,action){r.version=V;r.updated_at=new Date().toISOString();put(K,r);put(R,{type:'BANK_PROJECT_REGISTRY_RECEIPT_V1',version:V,at:new Date().toISOString(),registry_key:K,project_count:r.projects.length,action:action||'save',rule:'Registry write only updates the Bank project registry namespace.'});return r}
function upsert(name,cat,status){let r=reg(),n=clean(name),now=new Date().toISOString();if(!n)return r;let id=idFrom(n),p=r.projects.find(x=>x.id===id||clean(x.name).toLowerCase()===n.toLowerCase());if(!p){p={id,name:n,category:clean(cat)||'General',status:clean(status)||'active',item_count:0,created_at:now,updated_at:now};r.projects.push(p)}else{p.name=n;p.category=clean(cat)||p.category||'General';p.status=clean(status)||p.status||'active';p.updated_at=now}r.projects.sort((a,b)=>String(a.category).localeCompare(String(b.category))||String(a.name).localeCompare(String(b.name)));return save(r,'save_project')}
function del(id){let r=reg(),p=r.projects.find(x=>x.id===id);if(!p)return {r,msg:'Project not found.'};if(CORE[id])return {r,msg:'Protected core project cannot be deleted.'};r.projects=r.projects.filter(x=>x.id!==id);return {r:save(r,'delete_project'),msg:'Deleted: '+p.name}}
function scan(){save(reg(),'scan_data_only');return false}
W().PMPBankProjectRegistryV1={version:V,data_only:true,registry:reg,saveProject:upsert,deleteProject:del,last:()=>get(K,null),scan};
scan();
})();
