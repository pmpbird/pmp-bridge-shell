(()=>{
'use strict';
const V='1.0.3-rg21';
const RG='pmp-route-guardian-current-loader-v21.html';
let busy=false,last=0;
function page(){try{return /^#(world|bridge|library|workshop|control|bank)$/i.test(location.hash)?location.hash:'#control'}catch(e){return'#control'}}
function go(e){
 if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}
 let n=Date.now();if(busy||n-last<1200)return false;busy=true;last=n;
 let url=RG+'?from=reload-current&fresh='+V+'-'+Date.now()+page();
 try{localStorage.setItem('pmp_reload_current_v1_receipt',JSON.stringify({type:'PMP_RELOAD_CURRENT_V1_RECEIPT',version:V,target:RG,launch_url:url,at:new Date().toISOString()},null,2))}catch(x){}
 try{(window.top||window).location.href=url}catch(x){location.href=url}
 return false;
}
function t(x){return String((x&&x.textContent)||x&&x.value||'').toLowerCase().trim()}
function is(b){let s=t(b),o=String(b&&b.getAttribute&&b.getAttribute('onclick')||'').toLowerCase();return s==='reload'||s==='reload current'||s.includes('reload current')||o.includes('reloadapp')||b&&b.getAttribute&&b.getAttribute('data-launcher-reload-current')}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>8)return a;try{a.push(d);d.querySelectorAll('iframe').forEach(f=>{try{if(f.contentDocument)docs(f.contentDocument,a,n+1)}catch(e){}})}catch(e){}return a}
function patch(d){try{let w=d.defaultView;if(w)w.reloadApp=function(){return go(null)};d.querySelectorAll('button,a,input,[role="button"],[data-launcher-reload-current]').forEach(b=>{if(is(b)){b.setAttribute('data-launcher-reload-current','1');b.onclick=function(e){return go(e)}}});if(!d.__reloadWorldMap){d.__reloadWorldMap=1;d.addEventListener('click',e=>{let b=e.target&&e.target.closest&&e.target.closest('button,a,input,[role="button"]');if(is(b))return go(e)},true)}}catch(e){}}
function scan(){try{docs(top.document).forEach(patch)}catch(e){patch(document)}}
addEventListener('load',scan);setInterval(scan,500);scan();
})();