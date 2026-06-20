(()=>{
  if(window.PMPCRDStableHelperV1)return;
  window.PMPCRDStableHelperV1=true;
  const OLD=['Auto','mated',' Plan'].join('');
  const NEW=['Continuous',' Run',' Dashboard'].join('');
  function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
  function label(d){try{Array.from(d.getElementsByTagName('button')).forEach(b=>{let text=String(b.textContent||'');if(text.indexOf(OLD)<0)return;Array.from(b.querySelectorAll('span')).forEach(s=>{if(String(s.textContent||'').trim()===OLD)s.textContent=NEW});});}catch(e){}}
  function scan(){docs(document).forEach(label)}
  window.addEventListener('load',()=>[50,250,900,2500].forEach(t=>setTimeout(scan,t)));
  document.addEventListener('click',()=>setTimeout(scan,80),true);
  scan();
})();
