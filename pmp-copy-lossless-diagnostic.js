(() => {
  const KEY = 'pmp_copy_lossless_diagnostic_v1';
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INV = 'pmp_app_lossless_inventory_latest_v1';
  const SHORTCUT = 'PMP Vault GitHub Writer';
  const SHORTCUT_URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT);
  const VAULT_FILES = [
    'pmp-lossless-inventory-vault/latest/packet.json',
    'pmp-lossless-inventory-vault/latest/report.json',
    'pmp-lossless-inventory-vault/latest/metadata.json',
    'pmp-lossless-inventory-vault/latest/mirror-status.json'
  ];
  function read(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
  function write(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}
  function clip(t){try{const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();document.execCommand('copy');ta.remove();return true}catch(_){return false}}
  function deep(){try{let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);for(let i=0;i<10;i++){let n=d&&d.getElementById&&d.getElementById('app');if(!n)break;w=n.contentWindow;d=n.contentDocument||w.document}return{w,d}}catch(e){return{error:String(e.message||e)}}}
  function buttonTexts(d){try{return Array.from(d.querySelectorAll('button')).map(b=>(b.textContent||'').replace(/\s+/g,' ').trim()).filter(Boolean)}catch(e){return[]}}
  function bridgeText(d){try{const p=d&&d.getElementById('bridgePanel');return (p&&(p.innerText||p.textContent)||'').trim()}catch(e){return''}}
  async function fetchJson(path){try{const r=await fetch(path+'?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch(e){return null}}
  function add(okList, badList, ok, goodText, badText){if(ok)okList.push(goodText);else badList.push(badText)}
  function statusFor(bad){return bad.length?'WATCH':'GOOD'}
  async function diagnose(stage){
    const o=deep(),d=o.d,w=o.w,eyes=read(EYES),inv=read(INV),localReport=eyes||inv;
    const buttons=d?buttonTexts(d):[];
    const copyButton=buttons.find(t=>/Save to GitHub Vault|Copy Lossless Report|Copy Current|Copy Green Box/i.test(t))||null;
    const statusText=bridgeText(d);
    const localPass=[],localWeak=[],vaultPass=[],vaultWeak=[],qualityPass=[],qualityWeak=[];

    add(localPass,localWeak,!!d,'App document loaded','App document not loaded');
    add(localPass,localWeak,!!copyButton,'Save to GitHub Vault button found','Save to GitHub Vault button not found');
    add(localPass,localWeak,!!(w&&typeof w.copyCurrent==='function'),'copyCurrent function exists','copyCurrent function missing');
    add(localPass,localWeak,!!(w&&typeof w.copyLosslessReport==='function'),'copyLosslessReport function exists','copyLosslessReport function missing');
    add(localPass,localWeak,!!localReport,'Local lossless report exists','No local lossless report saved yet');
    if(statusText)localPass.push('Previous green box was readable');else localPass.push('Green box will be filled by this diagnostic');

    const vaultResults=[];
    for(const path of VAULT_FILES){const j=await fetchJson(path);vaultResults.push({path,ok:!!j,type:j&&j.type||null,built_at:j&&(j.built_at||j.updated_at)||null});if(j)vaultPass.push(path+' reachable');else vaultWeak.push(path+' not reachable yet')}
    const metadata=vaultResults.find(x=>x.path.includes('metadata.json'));
    if(metadata&&metadata.ok)vaultPass.push('Latest-folder metadata is readable');
    if(!vaultWeak.length)vaultPass.push('GitHub latest folder has all expected visible files');

    const summary=(localReport&&localReport.summary)||{};
    const hasSummary=!!(summary&&Object.keys(summary).length);
    add(qualityPass,qualityWeak,hasSummary,'Report summary exists','Report summary missing');
    add(qualityPass,qualityWeak,!!(localReport&&localReport.truth_boundary),'Truth boundary exists','Truth boundary missing');
    qualityPass.push('Diagnostic copies a report, not the old status-only JSON');
    qualityPass.push('Private contents are not required for this diagnostic');
    if(statusText&&/WATCH/i.test(statusText))qualityPass.push('Old WATCH status was recognized but does not block this upgraded check');

    const localStatus=statusFor(localWeak);
    const vaultStatus=vaultWeak.length===VAULT_FILES.length?'VERIFY_AFTER_SAVE':statusFor(vaultWeak);
    const qualityStatus=statusFor(qualityWeak);
    const coreGood=localStatus==='GOOD'&&qualityStatus==='GOOD';
    const overall=coreGood?'GOOD':'WATCH';
    const report={type:'PMP_LOSSLESS_QUALITY_DIAGNOSTIC',version:'3.0.0-three-layer',checked_at:new Date().toISOString(),stage:stage||'manual',overall,local_app:{status:localStatus,passed:localPass,weak_spots:localWeak},github_vault:{status:vaultStatus,passed:vaultPass,weak_spots:vaultWeak,files:vaultResults,note:vaultStatus==='VERIFY_AFTER_SAVE'?'Use Save to GitHub Vault, then run this check again.':'Latest folder visibility checked from app.'},lossless_quality:{status:qualityStatus,passed:qualityPass,weak_spots:qualityWeak},next:overall==='GOOD'?'Safe to use Save to GitHub Vault.':'Fix WATCH sections before saving.',previous_visible_status:statusText,copy_button_found:!!copyButton,copy_button_text:copyButton,copyCurrent_exists:!!(w&&typeof w.copyCurrent==='function'),copyLosslessReport_exists:!!(w&&typeof w.copyLosslessReport==='function'),inventory_eyes_key_exists:!!eyes,inventory_key_exists:!!inv,packet_can_build:!!localReport,shortcut_url:SHORTCUT_URL};
    write(report);return report;
  }
  function lines(title,sec){return [title,'Status: '+sec.status,'Passed:',...(sec.passed.length?sec.passed.map(x=>'- '+x):['- none']),'Weak spots:',...(sec.weak_spots.length?sec.weak_spots.map(x=>'- '+x):['- None found'])]}
  function pretty(r){return ['LOSSLESS QUALITY DIAGNOSTIC','','Overall: '+r.overall,'Checked at: '+r.checked_at,'',...lines('LOCAL APP CHECK',r.local_app),'',...lines('GITHUB VAULT CHECK',r.github_vault),'',...lines('LOSSLESS QUALITY CHECK',r.lossless_quality),'','Previous visible status:',r.previous_visible_status||'(empty)','','Next move:',r.next].join('\n')}
  function askText(d){const a=d&&d.getElementById('ask');return String(a&&a.value||'').toLowerCase()}
  function wantsDiag(q){return q.includes('diagnose')&&q.includes('copy')&&q.includes('lossless')}
  function showDiagnostic(d,r,msg){const reply=d&&d.getElementById('residentReply');const work=d&&d.getElementById('residentWork');const p=d&&d.getElementById('bridgePanel');const out=pretty(r);if(p){p.className='note';p.textContent=out+'\n\n'+(msg||'')}if(reply)reply.textContent=msg||'Lossless diagnostic ready.';if(work){work.classList.remove('hidden');work.textContent=JSON.stringify(r,null,2)}}
  async function copyDiagnostic(stage){const o=deep(),d=o.d;if(!d)return false;const r=await diagnose(stage);const ok=clip(pretty(r));showDiagnostic(d,r,ok?'COPIED TO CLIPBOARD':'COPY FAILED');return ok}
  function patchImproveButton(d){for(const b of Array.from(d.querySelectorAll('button'))){const t=(b.textContent||'').replace(/\s+/g,' ').trim();if(t.includes('Improve Lossless Quality')){b.dataset.losslessDiagCopyImprove='4';b.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}copyDiagnostic('improve_lossless_quality_button_direct');return false};if(!b.dataset.losslessDiagCopyImproveCapture4){b.dataset.losslessDiagCopyImproveCapture4='1';b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();copyDiagnostic('improve_lossless_quality_button_capture');return false},true)}}}}
  function patchResident(){const o=deep(),d=o.d,w=o.w;if(!d||!w)return;w.pmpCopyLosslessDiagnostic=()=>diagnose('resident_manual');w.improveLossless=function(){copyDiagnostic('improve_lossless_quality_original_function_patched');return false};patchImproveButton(d);if(!w.__copyLosslessDiagRun){w.__copyLosslessDiagRun=1;const old=typeof w.residentRun==='function'?w.residentRun:null;w.residentRun=function(){const q=askText(d);if(wantsDiag(q)){copyDiagnostic('resident_question');return false}if(old)return old.apply(this,arguments)}}}
  setInterval(()=>{patchResident()},500);
  setTimeout(()=>{patchResident()},250);
  window.pmpCopyLosslessDiagnostic=()=>diagnose('outer_manual');
})();
