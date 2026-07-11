(function(){
  'use strict';
  const V='2.0.0-a002-p4-map-tool-route';
  const OWNER='pmp-safe-writer-current-return-fix-v1';
  const KEY='pmp_safe_writer_current_return_fix_v1_receipt';
  const RESOLVER_SRC='pmp-current-route-resolver-v1.js';
  const RULE='Finds the Open Safe Writer button and opens the Current Map tool_routes.safe_writer handoff at the top app level. No storage overwrite, Bank rebuild, or fallback route.';
  function T(){try{return top||window}catch(e){return window}}
  function now(){return new Date().toISOString()}
  function txt(el){return String(el&&el.textContent||'').replace(/\s+/g,' ').trim()}
  function save(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
  function isSafeWriter(el){if(!el)return false;const t=txt(el).toLowerCase(),c=String(el.getAttribute&&el.getAttribute('onclick')||el.onclick||'').toLowerCase();return t.includes('open safe writer')||c.includes('safe-writer-v14.html')}
  function resolverGlobal(){return T().PMPCurrentRouteResolver||window.PMPCurrentRouteResolver||null}
  function ensureResolver(){let t=T(),r=resolverGlobal();if(r)return Promise.resolve(r);if(t.__PMPEnsureCurrentRouteResolverV1Promise)return t.__PMPEnsureCurrentRouteResolverV1Promise;t.__PMPEnsureCurrentRouteResolverV1Promise=new Promise((resolve,reject)=>{let done=false,timer=null;function finish(err){if(done)return;let x=resolverGlobal();if(!err&&x){done=true;if(timer)clearInterval(timer);try{t.PMPCurrentRouteResolver=x}catch(e){}resolve(x);return}if(err){done=true;if(timer)clearInterval(timer);reject(err)}}try{let d=t.document||document,s=Array.from(d.querySelectorAll('script[src]')).find(x=>String(x.getAttribute('src')||'').includes(RESOLVER_SRC));if(!s){s=d.createElement('script');s.src=RESOLVER_SRC+'?fresh=a002-p4-safe-writer-open-'+Date.now();s.async=true;s.onerror=()=>finish(new Error('resolver_script_load_failed'));(d.head||d.documentElement).appendChild(s)}let n=0;timer=setInterval(()=>{if(resolverGlobal())return finish();if(++n>100)finish(new Error('resolver_api_timeout'))},25)}catch(e){finish(e)}});return t.__PMPEnsureCurrentRouteResolverV1Promise}
  async function openSafeWriter(e){try{if(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation&&e.stopImmediatePropagation()}}catch(_e){}try{const resolver=await ensureResolver(),loaded=await resolver.load(),tool=resolver.resolve(loaded.map,'tool_routes.safe_writer'),ret=resolver.resolve(loaded.map,'current_app'),url=resolver.buildUrl(tool,{fresh:'a002-p4-'+tool.route_epoch+'-'+Date.now(),from:'control-open',return_role:ret.role,return_hash:'#control',map_version:tool.map_version,route_epoch:tool.route_epoch},'');save({type:'PMP_SAFE_WRITER_CURRENT_RETURN_FIX_RECEIPT_V2',version:V,owner:OWNER,status:'MAP_TOOL_HANDOFF_READY',tool_role:tool.role,tool_path:tool.path,return_role:ret.role,return_path:ret.path,launch_url:url,at:now(),rule:RULE});try{T().location.href=url}catch(_e){location.href=url}}catch(error){let r=resolverGlobal(),d=r?r.diagnostic(error,'safe_writer_open'):{type:'PMP_ROUTE_FAIL_CLOSED_DIAGNOSTIC_V1',context:'safe_writer_open',message:String(error&&error.message||error),action:'navigation_blocked_no_fallback_consulted'};save({type:'PMP_SAFE_WRITER_CURRENT_RETURN_FIX_RECEIPT_V2',version:V,owner:OWNER,status:'FAIL_CLOSED',diagnostic:d,at:now(),rule:RULE})}return false}
  function patchDoc(d){let n=0;try{d.querySelectorAll('button,a,[onclick]').forEach(el=>{if(isSafeWriter(el)&&el.dataset.pmpSafeWriterCurrentReturnFix!=='2'){el.dataset.pmpSafeWriterCurrentReturnFix='2';el.onclick=openSafeWriter;try{el.setAttribute('data-safe-writer-return','current-map-current-app')}catch(_e){}n++}})}catch(_e){}return n}
  function walk(w,depth){let n=0;if(depth>8)return 0;try{n+=patchDoc(w.document)}catch(_e){}try{for(let i=0;i<w.frames.length;i++)n+=walk(w.frames[i],depth+1)}catch(_e){}return n}
  function scan(){const patched=walk(window,0);return save({type:'PMP_SAFE_WRITER_CURRENT_RETURN_FIX_RECEIPT_V2',version:V,owner:OWNER,status:'PATCHED_MAP_DELEGATE',at:now(),patched_count:patched,rule:RULE})}
  let runs=0;function loop(){runs++;scan();if(runs<60)setTimeout(loop,700)}
  window.PMPSafeWriterCurrentReturnFixV1={version:V,owner:OWNER,scan,openSafeWriter,rule:RULE};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loop,{once:true});else loop();
})();
