(()=>{
if(window.PMPLastGoodLabelV11)return;window.PMPLastGoodLabelV11=true;
const CURRENT='pmp-current-inner-cleanbug-rgcontrols-v11.html#control';
const TARGET='pmp-route-guardian-last-good-v18.html';
function allDocs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>8)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)allDocs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function label(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
function save(){try{localStorage.setItem('pmp_route_guardian_current_before_last_good_v1',CURRENT);localStorage.setItem('pmp_route_guardian_current_before_last_good',CURRENT);localStorage.setItem('pmp_route_guardian_current_target',CURRENT)}catch(e){}}
function openIt(doc){save();let url=TARGET+'?from=current-v11&return='+encodeURIComponent(CURRENT)+'&fresh='+Date.now();try{(doc.defaultView||window).top.location.href=url}catch(e){try{doc.location.href=url}catch(_){location.href=url}}return false}
function patch(doc){try{Array.from(doc.querySelectorAll('button')).forEach(b=>{let t=label(b);if(t==='Last Good'||t==='Route Guardian Last Good'||b.dataset.pmpRouteGuardianLastGood==='true'){b.textContent='Route Guardian Last Good';b.dataset.pmpRouteGuardianLastGood='true';b.onclick=e=>{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}return openIt(doc)}}})}catch(e){}}
function run(){save();allDocs(document).forEach(patch)}
window.addEventListener('load',()=>[80,250,600,1200,2400,4200].forEach(t=>setTimeout(run,t)));
setInterval(run,700);run();
})();