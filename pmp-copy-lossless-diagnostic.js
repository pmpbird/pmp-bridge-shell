(() => {
  const KEY = 'pmp_copy_lossless_diagnostic_v1';
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INV = 'pmp_app_lossless_inventory_latest_v1';
  const SHORTCUT = 'PMP Vault GitHub Writer';
  const SHORTCUT_URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT);
  function read(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
  function write(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}
  function deep(){try{let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);for(let i=0;i<10;i++){let n=d&&d.getElementById&&d.getElementById('app');if(!n)break;w=n.contentWindow;d=n.contentDocument||w.document}return{w,d}}catch(e){return{error:String(e.message||e)}}}
  function buttonTexts(d){try{return Array.from(d.querySelectorAll('button')).map(b=>(b.textContent||'').replace(/\s+/g,' ').trim()).filter(Boolean)}catch(e){return[]}}
  function diagnose(stage){const o=deep(),d=o.d,w=o.w,eyes=read(EYES),inv=read(INV);const buttons=d?buttonTexts(d):[];const copyButton=buttons.find(t=>/Copy Lossless Report|Copy Current|Copy Green Box/i.test(t))||null;const report={type:'PMP_COPY_LOSSLESS_DIAGNOSTIC',version:'1.0.0',checked_at:new Date().toISOString(),stage:stage||'manual',loaded_document:!!d,deep_error:o.error||null,copy_button_found:!!copyButton,copy_button_text:copyButton,copyCurrent_exists:!!(w&&typeof w.copyCurrent==='function'),copyLosslessReport_exists:!!(w&&typeof w.copyLosslessReport==='function'),inventory_eyes_key_exists:!!eyes,inventory_key_exists:!!inv,packet_can_build:!!(eyes||inv),shortcut_url:SHORTCUT_URL,likely_stop:(!d?'no_loaded_document':!copyButton?'button_not_found':!(eyes||inv)?'no_inventory_report_saved':'shortcut_launch_or_ios_scheme_layer'),buttons_sample:buttons.slice(0,40)};write(report);return report}
  function patchResident(){const o=deep(),d=o.d,w=o.w;if(!d||!w||w.__copyLosslessDiag)return;w.__copyLosslessDiag=1;w.pmpCopyLosslessDiagnostic=()=>diagnose('resident_manual');const old=typeof w.residentRun==='function'?w.residentRun:null;w.residentRun=function(){const ask=d.getElementById('ask');const q=(ask&&ask.value||'').toLowerCase();if(q.includes('diagnose')&&q.includes('copy')&&q.includes('lossless')){const r=diagnose('resident_question');const reply=d.getElementById('residentReply');const work=d.getElementById('residentWork');if(reply)reply.textContent='Copy Lossless diagnostic complete. Tap Show Work, then Copy Work.';if(work){work.classList.remove('hidden');work.textContent=JSON.stringify(r,null,2)}return r}if(old)return old.apply(this,arguments)}}
  setInterval(()=>{diagnose('background');patchResident()},1000);
  setTimeout(()=>{diagnose('initial');patchResident()},500);
  window.pmpCopyLosslessDiagnostic=()=>diagnose('outer_manual');
})();
