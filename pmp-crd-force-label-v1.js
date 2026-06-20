(()=>{
  if(window.PMPCRDForceLabelV1)return;
  window.PMPCRDForceLabelV1=true;
  const OLD=['Auto','mated',' Plan'].join('');
  const NEW=['Continuous',' Run',' Dashboard'].join('');
  function docs(r,n,a){a=a||[];n=n||0;if(!r||n>9)return a;try{a.push(r);Array.from(r.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,n+1,a)}catch(e){}})}catch(e){}return a}
  function fix(d){try{Array.from(d.getElementsByTagName('button')).forEach(b=>{let text=String(b.textContent||'');if(text.indexOf(OLD)<0)return;Array.from(b.querySelectorAll('span')).forEach(s=>{if(String(s.textContent||'').trim()===OLD)s.textContent=NEW});});}catch(e){}}
  function scan(){docs(document).forEach(fix)}
  window.addEventListener('load',()=>[50,150,400,900,1800,3600,7000].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,120);
  scan();
})();
