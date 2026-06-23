(()=>{
const V='1.0.0';
if(window.PMPControlScrollHoldV1&&window.PMPControlScrollHoldV1.version===V)return;
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function spots(doc){let out=[];try{let w=doc.defaultView;out.push({el:w,x:w.scrollX,y:w.scrollY});Array.from(doc.querySelectorAll('*')).forEach(el=>{if((el.scrollTop||el.scrollLeft)&&el.scrollHeight>el.clientHeight){out.push({el,x:el.scrollLeft,y:el.scrollTop})}})}catch(e){}return out}
function take(){let all=[];docs(document).forEach(d=>all=all.concat(spots(d)));return all}
function put(all){all.forEach(s=>{try{s.el.scrollTo?s.el.scrollTo(s.x,s.y):(s.el.scrollLeft=s.x,s.el.scrollTop=s.y)}catch(e){}})}
function hold(){let s=take();try{let a=document.activeElement;if(a&&a.blur)a.blur()}catch(e){};[0,40,90,160,260,420,650].forEach(t=>setTimeout(()=>put(s),t))}
function attach(doc){try{let p=doc.getElementById('pmpContinuousRunDashboardScreenV1');if(!p||p.dataset.scrollHold)return;p.dataset.scrollHold='true';p.addEventListener('pointerdown',e=>{if(e.target&&e.target.closest&&e.target.closest('button'))hold()},true);p.addEventListener('click',e=>{if(e.target&&e.target.closest&&e.target.closest('button'))hold()},true)}catch(e){}}
function scan(){docs(document).forEach(attach)}
window.PMPControlScrollHoldV1={version:V,scan,hold};window.addEventListener('load',()=>[100,300,800,1600,3000].forEach(t=>setTimeout(scan,t)));setInterval(scan,1500);scan();
})();