(()=>{
  function textOf(x){return (x&&x.textContent||'').replace(/\s+/g,' ').trim()}
  function styleMain(btn,label){
    if(!btn)return;
    btn.textContent=label;
    btn.className='big';
    btn.style.width='100%';
    btn.style.minHeight='72px';
    btn.style.fontSize='22px';
    btn.style.fontWeight='950';
    btn.style.display='block';
  }
  function hide(x){if(x){x.style.display='none';x.setAttribute('aria-hidden','true')}}
  function simplifySourceLoader(d){
    const page=d&&d.getElementById&&d.getElementById('pmpSourceLoaderPageV1');
    if(!page||page.dataset.pmpSimpleSourceUiV1==='yes')return;
    page.dataset.pmpSimpleSourceUiV1='yes';
    const note=page.querySelector('.note');
    if(note)note.textContent='Paste one Manifest or BODY text, then press the button. The app will verify, store, receipt, and extract with watch.';
    const load=page.querySelector('#pmpSourceLoadV1');
    const copy=page.querySelector('#pmpSourceCopyStateV1');
    const back2=page.querySelector('#pmpSourceBack2V1');
    const grid=load&&load.parentElement;
    if(grid){grid.style.display='block';grid.style.gridTemplateColumns='1fr'}
    styleMain(load,'Load Source Text');
    hide(copy);
    hide(back2);
    const out=page.querySelector('#pmpSourceOutputV1');
    if(out){out.style.minHeight='110px';out.style.fontSize='11px'}
  }
  function simplifyFieldExtraction(d){
    const page=d&&d.getElementById&&d.getElementById('pmpFieldExtractionPageV1');
    if(!page||page.dataset.pmpSimpleSourceUiV1==='yes')return;
    page.dataset.pmpSimpleSourceUiV1='yes';
    const note=page.querySelector('.note');
    if(note)note.textContent='Press once to extract fields from loaded source text. This stays with watch and does not claim final validation.';
    const run=page.querySelector('#pmpFieldExtractRunV1');
    const copy=page.querySelector('#pmpFieldExtractCopyV1');
    const back2=page.querySelector('#pmpFieldExtractBack2V1');
    const grid=run&&run.parentElement;
    if(grid){grid.style.display='block';grid.style.gridTemplateColumns='1fr'}
    styleMain(run,'Extract Fields');
    hide(copy);
    hide(back2);
    const out=page.querySelector('#pmpFieldExtractOutputV1');
    if(out){out.style.minHeight='150px';out.style.fontSize='11px'}
  }
  function patchDoc(d){try{simplifySourceLoader(d);simplifyFieldExtraction(d)}catch(e){}}
  function findInner(){let f=document.getElementById('app');try{return f&&(f.contentDocument||f.contentWindow.document)}catch(e){return null}}
  function run(){patchDoc(document);let d=findInner();if(d)patchDoc(d)}
  window.PMPPrivateSimpleSourceUIV1={run,simplifySourceLoader,simplifyFieldExtraction};
  window.addEventListener('load',()=>{setTimeout(run,200);setTimeout(run,800);setTimeout(run,1800)});
  setInterval(run,500);
})();