(()=>{
const V='1.0.0',KEY='pmp_packet_1_5_helper_tidy_v1';
if(window.PMPP15HelperTidyV1&&window.PMPP15HelperTidyV1.version===V)return;
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function note(){try{localStorage.setItem(KEY,JSON.stringify({status:'STABLE_PACKET_1_5_RUNNER_SURFACE',updated_at:new Date().toISOString()},null,2))}catch(e){}}
function tidy(doc){let page=doc.getElementById('pmpContinuousRunDashboardScreenV1');if(!page)return;page.dataset.p15HelperTidy='true';Array.from(page.querySelectorAll('[data-p15-runner]')).forEach(n=>{try{n.parentNode&&n.parentNode.removeChild(n)}catch(e){}});Array.from(page.querySelectorAll('[data-p15-clean-runner-link]')).forEach(n=>{try{n.parentNode&&n.parentNode.removeChild(n)}catch(e){}});let s=Array.from(page.querySelectorAll('[data-p15-stable-runner]'));for(let i=1;i<s.length;i++){try{s[i].parentNode&&s[i].parentNode.removeChild(s[i])}catch(e){}}}
function scan(){note();docs(document).forEach(tidy)}
window.PMPP15HelperTidyV1={version:V,scan};window.addEventListener('load',()=>[50,150,300,700,1200,2400].forEach(t=>setTimeout(scan,t)));setInterval(scan,900);scan();
})();