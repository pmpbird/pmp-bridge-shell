(() => {
  const KEY = 'pmp_copy_lossless_diagnostic_v1';
  const EYES = 'pmp_inventory_eyes_latest_v1';
  const INV = 'pmp_app_lossless_inventory_latest_v1';
  const LAST_SAVE = 'pmp_last_save_to_github_vault_press_v1';
  const SHORTCUT = 'PMP Vault GitHub Writer';
  const SHORTCUT_URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT);
  const DIAG_LABEL = 'Lossless Quality Diagnostics';
  const DIAG_LABEL_RE = /Improve\s+Lossless\s+Quality|Lossless\s+Quality\s+Diagnostics/i;
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
  function ms(t){const n=Date.parse(t||'');return Number.isFinite(n)?n:NaN}
  function notOlder(fileTime, expectedTime){const f=ms(fileTime),e=ms(expectedTime);return Number.isFinite(f)&&Number.isFinite(e)&&f+5000>=e}
  function fileStamp(path,j){if(!j)return null;if(path.includes('metadata.json'))return j.updated_at||j.packet_built_at||j.report_built_at||j.built_at||null;return j.built_at||j.updated_at||j.packet_built_at||j.report_built_at||null}
  function isDiagButtonText(t){return DIAG_LABEL_RE.test(String(t||'').replace(/\s+/g,' ').trim())}
  function renameDiagButton(b){
    try{
      const spans=Array.from(b.querySelectorAll('span'));
      const labelSpan=spans.find(s=>!(s.classList&&s.classList.contains('icon'))&&!(s.classList&&s.classList.contains('chev')));
      if(labelSpan){
        const textNode=Array.from(labelSpan.childNodes).find(n=>n.nodeType===3&&isDiagButtonText(n.nodeValue));
        if(textNode) textNode.nodeValue=DIAG_LABEL;
        else if(isDiagButtonText(labelSpan.textContent||'')) labelSpan.insertBefore(document.createTextNode(DIAG_LABEL), labelSpan.firstChild||null);
        return;
      }
      if(isDiagButtonText(b.textContent||'')) b.textContent=DIAG_LABEL;
    }catch(_){}
  }
  async function diagnose(stage){
    const o=deep(),d=o.d,w=o.w,eyes=read(EYES),inv=read(INV),localReport=eyes||inv,lastSave=read(LAST_SAVE);
    const buttons=d?buttonTexts(d):[];
    const copyButton=buttons.find(t=>/Save to GitHub Vault|Copy Lossless Report|Copy Current|Copy Green Box/i.test(t))||null;
    const diagButton=buttons.find(isDiagButtonText)||null;
    const statusText=bridgeText(d);
    const localPass=[],localWeak=[],vaultPass=[],vaultWeak=[],qualityPass=[],qualityWeak=[];

    add(localPass,localWeak,!!d,'App document loaded','App document not loaded');
    add(localPass,localWeak,!!copyButton,'Save to GitHub Vault button found','Save to GitHub Vault button not found');
    add(localPass,localWeak,!!diagButton,'Lossless Quality Diagnostics button found','Lossless Quality Diagnostics button not found');
    add(localPass,localWeak,!!(w&&typeof w.copyCurrent==='function'),'copyCurrent function exists','copyCurrent function missing');
    add(localPass,localWeak,!!(w&&typeof w.copyLosslessReport==='function'),'copyLosslessReport function exists','copyLosslessReport function missing');
    add(localPass,localWeak,!!localReport,'Local lossless report exists','No local lossless report saved yet');
    if(statusText)localPass.push('Previous green box was readable');else localPass.push('Green box will be filled by this diagnostic');

    const vaultResults=[];
    for(const path of VAULT_FILES){
      const j=await fetchJson(path);
      const stamp=fileStamp(path,j);
      vaultResults.push({path,ok:!!j,type:j&&j.type||null,time:stamp,packet_built_at:j&&j.packet_built_at||null,report_built_at:j&&j.report_built_at||null,updated_at:j&&j.updated_at||null});
      if(j)vaultPass.push(path+' reachable');else vaultWeak.push(path+' not reachable yet');
    }
    const packet=vaultResults.find(x=>x.path.includes('packet.json'));
    const reportFile=vaultResults.find(x=>x.path.includes('report.json'));
    const metadata=vaultResults.find(x=>x.path.includes('metadata.json'));
    if(metadata&&metadata.ok)vaultPass.push('Latest-folder metadata is readable');
    if(!vaultWeak.length)vaultPass.push('GitHub latest folder has all expected visible files');

    const expectedTime=lastSave&&(lastSave.packet_built_at||lastSave.pressed_at)||null;
    if(!lastSave||!expectedTime){
      vaultWeak.push('No recent Save to GitHub Vault press recorded in this app session; freshness cannot be proven yet');
    }else{
      vaultPass.push('Most recent Save press recorded: '+(lastSave.pressed_at||expectedTime));
      vaultPass.push('Expected packet time: '+expectedTime);
      add(vaultPass,vaultWeak,notOlder(packet&&packet.time,expectedTime),'latest packet time matches or follows most recent save','latest packet is older than most recent save');
      add(vaultPass,vaultWeak,notOlder(reportFile&&reportFile.time,expectedTime),'latest report time matches or follows most recent save','latest report is older than most recent save');
      const metaPacketTime=metadata&&(metadata.packet_built_at||metadata.time);
      add(vaultPass,vaultWeak,notOlder(metaPacketTime,expectedTime),'latest metadata packet time matches or follows most recent save','latest metadata does not match most recent save');
    }

    const summary=(localReport&&localReport.summary)||{};
    const hasSummary=!!(summary&&Object.keys(summary).length);
    add(qualityPass,qualityWeak,hasSummary,'Report summary exists','Report summary missing');
    add(qualityPass,qualityWeak,!!(localReport&&localReport.truth_boundary),'Truth boundary exists','Truth boundary missing');
    qualityPass.push('Diagnostic copies a report, not the old status-only JSON');
    qualityPass.push('Private contents are not required for this diagnostic');
    if(statusText&&/WATCH/i.test(statusText))qualityPass.push('Old WATCH status was recognized but does not block this upgraded check');

    const localStatus=statusFor(localWeak);
    const vaultStatus=statusFor(vaultWeak);
    const qualityStatus=statusFor(qualityWeak);
    const overall=(localStatus==='GOOD'&&vaultStatus==='GOOD'&&qualityStatus==='GOOD')?'GOOD':'WATCH';
    const freshness={last_save_pressed_at:lastSave&&lastSave.pressed_at||null,expected_packet_time:expectedTime,latest_packet_time:packet&&packet.time||null,latest_report_time:reportFile&&reportFile.time||null,latest_metadata_time:metadata&&metadata.time||null,latest_metadata_packet_time:metadata&&metadata.packet_built_at||null,latest_metadata_report_time:metadata&&metadata.report_built_at||null};
    const report={type:'PMP_LOSSLESS_QUALITY_DIAGNOSTIC',version:'3.2.0-button-label-lossless-quality-diagnostics',checked_at:new Date().toISOString(),stage:stage||'manual',overall,local_app:{status:localStatus,passed:localPass,weak_spots:localWeak},github_vault:{status:vaultStatus,passed:vaultPass,weak_spots:vaultWeak,files:vaultResults,freshness,note:vaultStatus==='GOOD'?'Latest files match the most recent recorded save.':'Save freshness is not proven yet.'},lossless_quality:{status:qualityStatus,passed:qualityPass,weak_spots:qualityWeak},next:overall==='GOOD'?'Safe to use Save to GitHub Vault.':'Fix WATCH sections, or press Save to GitHub Vault and run this check again after GitHub updates.',previous_visible_status:statusText,copy_button_found:!!copyButton,copy_button_text:copyButton,diagnostic_button_found:!!diagButton,diagnostic_button_text:diagButton,copyCurrent_exists:!!(w&&typeof w.copyCurrent==='function'),copyLosslessReport_exists:!!(w&&typeof w.copyLosslessReport==='function'),inventory_eyes_key_exists:!!eyes,inventory_key_exists:!!inv,packet_can_build:!!localReport,shortcut_url:SHORTCUT_URL};
    write(report);return report;
  }
  function lines(title,sec){return [title,'Status: '+sec.status,'Passed:',...(sec.passed.length?sec.passed.map(x=>'- '+x):['- none']),'Weak spots:',...(sec.weak_spots.length?sec.weak_spots.map(x=>'- '+x):['- None found'])]}
  function freshnessLines(f){return ['FRESHNESS PROOF','Last Save press: '+(f.last_save_pressed_at||'(none recorded)'),'Expected packet time: '+(f.expected_packet_time||'(none recorded)'),'Latest packet time: '+(f.latest_packet_time||'(missing)'),'Latest report time: '+(f.latest_report_time||'(missing)'),'Latest metadata time: '+(f.latest_metadata_time||'(missing)')]}
  function pretty(r){return ['LOSSLESS QUALITY DIAGNOSTIC','','Overall: '+r.overall,'Checked at: '+r.checked_at,'',...lines('LOCAL APP CHECK',r.local_app),'',...lines('GITHUB VAULT CHECK',r.github_vault),'',...freshnessLines(r.github_vault.freshness),'',...lines('LOSSLESS QUALITY CHECK',r.lossless_quality),'','Previous visible status:',r.previous_visible_status||'(empty)','','Next move:',r.next].join('\n')}
  function askText(d){const a=d&&d.getElementById('ask');return String(a&&a.value||'').toLowerCase()}
  function wantsDiag(q){return q.includes('diagnose')&&q.includes('copy')&&q.includes('lossless')}
  function showDiagnostic(d,r,msg){const reply=d&&d.getElementById('residentReply');const work=d&&d.getElementById('residentWork');const p=d&&d.getElementById('bridgePanel');const out=pretty(r);if(p){p.className='note';p.textContent=out+'\n\n'+(msg||'')}if(reply)reply.textContent=msg||'Lossless diagnostic ready.';if(work){work.classList.remove('hidden');work.textContent=JSON.stringify(r,null,2)}}
  async function copyDiagnostic(stage){const o=deep(),d=o.d;if(!d)return false;const r=await diagnose(stage);const ok=clip(pretty(r));showDiagnostic(d,r,ok?'COPIED TO CLIPBOARD':'COPY FAILED');return ok}
  function patchImproveButton(d){for(const b of Array.from(d.querySelectorAll('button'))){const t=(b.textContent||'').replace(/\s+/g,' ').trim();if(isDiagButtonText(t)){renameDiagButton(b);b.dataset.losslessDiagCopyImprove='6';b.onclick=function(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}copyDiagnostic('lossless_quality_diagnostics_button_direct');return false};if(!b.dataset.losslessDiagCopyImproveCapture6){b.dataset.losslessDiagCopyImproveCapture6='1';b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();copyDiagnostic('lossless_quality_diagnostics_button_capture');return false},true)}}}}
  function patchResident(){const o=deep(),d=o.d,w=o.w;if(!d||!w)return;w.pmpCopyLosslessDiagnostic=()=>diagnose('resident_manual');w.improveLossless=function(){copyDiagnostic('lossless_quality_diagnostics_original_function_patched');return false};patchImproveButton(d);if(!w.__copyLosslessDiagRun){w.__copyLosslessDiagRun=1;const old=typeof w.residentRun==='function'?w.residentRun:null;w.residentRun=function(){const q=askText(d);if(wantsDiag(q)){copyDiagnostic('resident_question');return false}if(old)return old.apply(this,arguments)}}}
  setInterval(()=>{patchResident()},500);
  setTimeout(()=>{patchResident()},250);
  window.pmpCopyLosslessDiagnostic=()=>diagnose('outer_manual');
})();
