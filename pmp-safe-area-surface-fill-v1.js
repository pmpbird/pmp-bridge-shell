(()=>{
'use strict';
const V='1.0.0-pmp-safe-area-surface-fill';
const OWNER='pmp-safe-area-surface-fill-v1';
const BG='#f3ded4';
const K='pmp_safe_area_surface_fill_v1_receipt';
function now(){return new Date().toISOString()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>8)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function apply(reason){let reports=[];docs(document).forEach(d=>{try{let st=d.getElementById('pmpSafeAreaSurfaceFillV1Style');if(!st){st=d.createElement('style');st.id='pmpSafeAreaSurfaceFillV1Style';(d.head||d.documentElement).appendChild(st)}st.textContent='html,body{background:'+BG+'!important;background-color:'+BG+'!important;color-scheme:light;}body:before{content:"";position:fixed;inset:-120px;z-index:-2147483647;background:'+BG+';pointer-events:none;}iframe{background:'+BG+'!important;background-color:'+BG+'!important;}';try{let m=d.querySelector('meta[name="theme-color"]');if(m)m.content=BG}catch(e){}reports.push({title:d.title||'',pass:true})}catch(e){reports.push({error:String(e&&e.message||e),pass:false})}});let r={type:'PMP_SAFE_AREA_SURFACE_FILL_V1_RECEIPT',version:V,owner:OWNER,at:now(),reason:reason||'apply',background:BG,documents:reports,rule:'Fills PMP app safe-area/top/bottom surface with app tan background. This is app theme fill, not Runtime Platform styling.',pass:reports.every(x=>x.pass)};try{localStorage.setItem(K,JSON.stringify(r,null,2));window.PMPSafeAreaSurfaceFillV1={version:V,apply,last:()=>r}}catch(e){}return r}
apply('script_load');[80,200,500,1000,2000,4000,7000].forEach(t=>setTimeout(()=>apply('repeat_'+t),t));setInterval(()=>apply('interval'),3000);
})();