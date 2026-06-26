(()=>{
'use strict';
const V='1.0.0-level11-startup-certification-guard';
const L10K='pmp_level10_full_chain_certification_lock_v1';
const L11K='pmp_level11_startup_certification_guard_v1';
function W(){try{return window.top||window}catch(e){return window}}
function read(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function write(k,v){try{W().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function hash(s){let h=2166136261;s=String(s||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,'0')}
function latest10(){let x=read(L10K,null);return x&&(x.latest||x)}
function good10(c){return !!(c&&c.status==='FULL_CHAIN_CERTIFIED'&&c.strict_note_match_required===true&&c.real_source_test==='PASS'&&c.fake_block_test==='PASS'&&Number(c.coverage_passes)>=Number(c.coverage_target||4)&&c.hash)}
function check(){let c=latest10(),old=read(L11K,{}),ok=good10(c),last=ok?c:(old.last_good||null);let r={level:11,type:'STARTUP_CERTIFICATION_GUARD',version:V,checked_at:new Date().toISOString(),status:ok?'STARTUP_CERTIFIED':'STARTUP_NOT_CERTIFIED',resident_allowed:!!ok,latest_level10_status:c&&c.status||'NONE',latest_level10_hash:c&&c.hash||null,last_good:last,last_good_hash:last&&last.hash||null,guard_hash:hash(JSON.stringify({ok,c,last,version:V})),rule:'Resident starts only when the latest Level 10 strict certification is present and passing. Last-good is kept as audit memory.'};return write(L11K,r)}
function text(x){if(!x)return 'Level 11 ready.';if(x.status==='STARTUP_CERTIFIED')return 'Level 11\nStatus: STARTUP CERTIFIED\nResident allowed: YES\nLatest Level 10 hash: '+(x.latest_level10_hash||'none')+'\nLast-good hash: '+(x.last_good_hash||'none')+'\nGuard hash: '+(x.guard_hash||'none');return 'Level 11\nStatus: STARTUP NOT CERTIFIED\nResident allowed: NO\nLatest Level 10 status: '+(x.latest_level10_status||'NONE')+'\nLast-good retained: '+(x.last_good_hash?'YES':'NO')+'\nLast-good hash: '+(x.last_good_hash||'none')+'\nGuard hash: '+(x.guard_hash||'none')}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function badge(){return '<div data-l11-badge style="margin:4px 0 8px;padding:8px;border-radius:10px;border:2px solid rgba(0,0,0,.18);font-weight:950">Level 11: Startup Certification Guard + Last-Good Lock — READY</div>'}
function section(){return '<div data-level11-startup-guard style="margin-top:8px;padding:8px;border-radius:10px;border:1px solid rgba(0,0,0,.08)"><h4 style="margin:0 0 4px">Level 11 — Startup Certification Guard + Last-Good Lock</h4><p class="sub">Uses the latest Level 10 strict certification to decide startup readiness.</p><div class="grid"><button class="mini" data-l11-run>Run Startup Guard</button><button class="mini" data-l11-view>View Last-Good Lock</button></div><pre class="note" data-l11-out style="max-height:300px;overflow:auto;white-space:pre-wrap">Level 11 ready. Startup guard also runs automatically.</pre></div>'}
function patch(d){let root=d.querySelector('[data-source-reference-gate-level4]');if(!root)return;let h=root.querySelector('h4');if(h&&!root.querySelector('[data-l11-badge]'))h.insertAdjacentHTML('afterend',badge());if(!root.querySelector('[data-level11-startup-guard]'))root.insertAdjacentHTML('beforeend',section());let out=root.querySelector('[data-l11-out]'),run=root.querySelector('[data-l11-run]'),view=root.querySelector('[data-l11-view]');if(run)run.onclick=()=>{out.textContent=text(check())};if(view)view.onclick=()=>{out.textContent=text(read(L11K,null))}}
function scan(){docs(W().document).forEach(d=>{try{patch(d)}catch(e){}})}
function startup(){let r=check();try{W().PMPResidentStartupCertificationGuard=r;W().PMPResidentStartupAllowed=!!r.resident_allowed}catch(e){}return r}
W().PMPStartupCertificationGuardLevel11V1={version:V,guard:startup,view:()=>read(L11K,null),render:text};
window.addEventListener('load',()=>[300,1000,2500,5000].forEach(t=>setTimeout(()=>{scan();startup()},t)));
setInterval(scan,1000);setTimeout(startup,1500);scan();
})();