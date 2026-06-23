(()=>{
const V='1.0.0',URL='pmp-p15-runner-clean-v1.html';
if(window.PMPP15CleanRunnerLinkV1&&window.PMPP15CleanRunnerLinkV1.version===V)return;
function docs(root,d,o){o=o||[];d=d||0;if(!root||d>8)return o;try{o.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,o)}catch(e){}})}catch(e){}return o}
function install(doc){let page=doc.getElementById('pmpContinuousRunDashboardScreenV1');if(!page||page.querySelector('[data-p15-clean-runner-link]'))return;let card=page.querySelector('.card')||page;let b=doc.createElement('button');b.className='mini';b.setAttribute('data-p15-clean-runner-link','');b.textContent='Packet 1.5 Clean Runner';b.onclick=()=>{try{window.open(URL+'?fresh='+Date.now(),'_blank')}catch(e){location.href=URL+'?fresh='+Date.now()}};let before=page.querySelector('[data-crd-more]')||page.querySelector('[data-p15-runner]');card.insertBefore(b,before||null)}
function scan(){docs(document).forEach(install)}
window.PMPP15CleanRunnerLinkV1={version:V,scan};window.addEventListener('load',()=>[100,300,800,1600].forEach(t=>setTimeout(scan,t)));setInterval(scan,1500);scan();
})();