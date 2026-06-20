(()=>{
 if(window.PMPCRDCardV1)return;window.PMPCRDCardV1=true;
 function q(s){return String(s==null?'':s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
 function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
 function turn(e,o){let s=String(o.status||'');if(!/VERIFIED|COMPILED|FAILED/.test(s))return;let t=o.verified?'Verified':o.compiled?'Compiled':'Needs attention';let next=o.next_step||'Verify before continuing';let rows=[['Status',t],['Continuation',o.continuation_allowed?'allowed':o.compiled?'waiting for verification':'not allowed'],['Boundary','hidden'],['Free-only',o.free_only===false?'no':'yes'],['Locks held',o.locks_held===false?'no':'yes'],['Outside path','blocked'],['Next action',next]];e.dataset.rawResult=JSON.stringify(o,null,2);e.innerHTML='<div style="font-size:22px;font-weight:950;margin-bottom:12px">'+q(t)+'</div>'+rows.map(r=>'<div style="display:grid;grid-template-columns:140px 1fr;gap:8px;border-top:1px solid rgba(255,255,255,.35);padding:9px 0"><div style="opacity:.9">'+q(r[0])+'</div><div>'+q(r[1])+'</div></div>').join('')}
 function clean(d){try{let e=d.getElementById('pmpApEngineOut');if(!e||e.dataset.busy==='1')return;let raw=(e.textContent||'').trim();if(raw[0]!=='{')return;let o=JSON.parse(raw);e.dataset.busy='1';turn(e,o);setTimeout(()=>delete e.dataset.busy,0)}catch(x){}}
 function wire(d){try{let e=d.getElementById('pmpApEngineOut');if(!e||e.dataset.cardWatch==='1')return;e.dataset.cardWatch='1';new MutationObserver(()=>clean(d)).observe(e,{childList:true,subtree:true,characterData:true});clean(d)}catch(x){}}
 function scan(){docs(document).forEach(wire)}
 window.addEventListener('load',()=>[40,120,300,800,1600,3200].forEach(t=>setTimeout(scan,t)));
 document.addEventListener('click',()=>setTimeout(scan,20),true);
 setInterval(scan,900);scan();
})();
