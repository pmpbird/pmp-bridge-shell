(()=>{
  const text=x=>(x&&x.textContent||'').replace(/\s+/g,' ').trim();
  function main(b,label){if(!b)return;b.textContent=label;b.className='big';b.style.cssText+=';width:100%;min-height:74px;font-size:22px;font-weight:950;display:block;'}
  function gone(x){if(!x)return;x.remove?x.remove():x.style.display='none'}
  function fix(d){try{
    const source=d.getElementById('pmpSourceLoaderPageV1');
    if(source){
      const note=source.querySelector('.note');
      if(note)note.textContent='Paste one Manifest or BODY text, then press the button. The app verifies, stores, receipts, and extracts with watch.';
      const load=source.querySelector('#pmpSourceLoadV1');
      main(load,'Load Source Text');
      const grid=load&&load.parentElement;if(grid){grid.style.display='block';grid.style.gridTemplateColumns='1fr'}
      gone(source.querySelector('#pmpSourceCopyStateV1'));
      gone(source.querySelector('#pmpSourceBack2V1'));
    }
    const field=d.getElementById('pmpFieldExtractionPageV1');
    if(field){
      const note=field.querySelector('.note');
      if(note)note.textContent='Press once to extract fields from loaded source text. This stays with watch and does not claim final validation.';
      const run=field.querySelector('#pmpFieldExtractRunV1');
      main(run,'Extract Fields');
      const grid=run&&run.parentElement;if(grid){grid.style.display='block';grid.style.gridTemplateColumns='1fr'}
      gone(field.querySelector('#pmpFieldExtractCopyV1'));
      gone(field.querySelector('#pmpFieldExtractBack2V1'));
    }
  }catch(e){}}
  function inner(){try{let f=document.getElementById('app');return f&&(f.contentDocument||f.contentWindow.document)}catch(e){return null}}
  function run(){fix(document);let d=inner();if(d)fix(d)}
  window.PMPOneButtonPrivatePagesV2={run,fix};
  window.addEventListener('load',()=>{setTimeout(run,50);setTimeout(run,300);setTimeout(run,900);setTimeout(run,1800)});
  document.addEventListener('click',()=>setTimeout(run,30),true);
  setInterval(run,250);
})();