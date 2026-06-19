(()=>{
  if(window.PMPDeepResidentNoFlashV1)return;
  window.PMPDeepResidentNoFlashV1=true;
  const COLOR_KEY='pmp_single_colors_v6',PREV_KEY='pmp_single_colors_v5';
  const DEFAULT_COLORS={accent:'#acd1fb',background:'#f3ded4',card:'#ffffff',line:'#07101c'};
  function jj(k){try{return JSON.parse(localStorage.getItem(k)||'{}')}catch(e){return{}}}
  function colors(){let c={...DEFAULT_COLORS,...jj(PREV_KEY),...jj(COLOR_KEY)};if(String(c.background).toLowerCase()==='#52b5df')c.background=DEFAULT_COLORS.background;return c}
  function deepDocuments(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>8)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(frame=>{try{let d=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(d)deepDocuments(d,depth+1,out)}catch(e){}})}catch(e){}return out}
  function textOf(x){return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}
  function applyColors(doc){try{let c=colors();let r=doc.documentElement;r.style.setProperty('--floor',c.background);r.style.setProperty('--background',c.background);r.style.setProperty('--card',c.card);r.style.setProperty('--line',c.line);r.style.setProperty('--a',c.accent);r.style.setProperty('--accent',c.accent);if(doc.body)doc.body.style.background=c.background;let m=doc.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',c.background)}catch(e){}}
  function wireBack(hostWindow,hostDoc,frame){
    try{
      const rd=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(!rd)return;
      let btn=rd.getElementById('residentBackToControl')||rd.getElementById('pmpResidentBackToControl')||rd.getElementById('pmpResidentBackToControlLive');
      const h=Array.from(rd.querySelectorAll('h1')).find(x=>/^Resident Intelligence$/i.test(textOf(x))||/Deep Resident/i.test(textOf(x)));
      if(!btn&&h){btn=rd.createElement('button');btn.id='pmpResidentBackToControlLive';btn.textContent='← Back to Control Room';h.parentNode.insertBefore(btn,h)}
      if(btn){btn.textContent='← Back to Control Room';btn.onclick=function(e){if(e)e.preventDefault();let old=hostDoc.getElementById('pmpDeepResidentOverlayCurrentV1');if(old)old.remove();try{if(typeof hostWindow.go==='function')hostWindow.go('control');else hostWindow.location.hash='#control'}catch(x){}return false};let c=colors();btn.style.background=c.accent;btn.style.color='#07101c';btn.style.border='2px solid '+c.line;btn.style.borderRadius='18px';btn.style.padding='15px';btn.style.fontWeight='950';btn.style.width='100%'}
    }catch(e){}
  }
  function openNoFlash(hostWindow,hostDoc){
    applyColors(hostDoc);
    try{if(typeof hostWindow.go==='function')hostWindow.go('control')}catch(e){}
    const existing=hostDoc.getElementById('pmpDeepResidentOverlayCurrentV1');if(existing)existing.remove();
    const c=colors();
    const overlay=hostDoc.createElement('div');overlay.id='pmpDeepResidentOverlayCurrentV1';overlay.style.position='fixed';overlay.style.inset='0';overlay.style.zIndex='999999';overlay.style.background=c.background;overlay.style.overflow='hidden';overlay.style.visibility='hidden';overlay.style.opacity='0';
    const frame=hostDoc.createElement('iframe');frame.id='pmpDeepResidentFrameCurrentV1';frame.title='Resident Intelligence';frame.src='resident.html?embedded=live-current-control&fresh=no-flash-'+Date.now();frame.style.position='fixed';frame.style.inset='0';frame.style.width='100%';frame.style.height='100%';frame.style.border='0';frame.style.background=c.background;frame.style.visibility='hidden';frame.style.opacity='0';frame.style.transition='opacity 80ms linear';
    overlay.appendChild(frame);hostDoc.body.appendChild(overlay);
    function reveal(){try{applyColors(frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document));wireBack(hostWindow,hostDoc,frame)}catch(e){}requestAnimationFrame(()=>{overlay.style.visibility='visible';overlay.style.opacity='1';frame.style.visibility='visible';frame.style.opacity='1'})}
    frame.onload=function(){reveal();setTimeout(()=>wireBack(hostWindow,hostDoc,frame),250);setTimeout(()=>wireBack(hostWindow,hostDoc,frame),800)};
    setTimeout(()=>{if(hostDoc.getElementById('pmpDeepResidentOverlayCurrentV1')&&frame.style.visibility==='hidden')reveal()},1400);
    const timer=hostWindow.setInterval(function(){if(!hostDoc.getElementById('pmpDeepResidentOverlayCurrentV1')){hostWindow.clearInterval(timer);return}wireBack(hostWindow,hostDoc,frame)},600);
    return false;
  }
  function patchDoc(hostDoc){
    try{
      const hostWindow=hostDoc.defaultView;
      if(!hostWindow)return false;
      if(typeof hostWindow.openDeepResident==='function'&&!hostWindow.__pmpDeepResidentNoFlashV1){
        hostWindow.__pmpDeepResidentNoFlashV1=true;
        hostWindow.openDeepResident=function(){return openNoFlash(hostWindow,hostDoc)};
      }
      if(!hostDoc.documentElement.dataset.pmpDeepResidentNoFlashClickV1){
        hostDoc.documentElement.dataset.pmpDeepResidentNoFlashClickV1='1';
        hostDoc.addEventListener('click',function(e){
          try{
            const target=e.target&&e.target.closest&&e.target.closest('button,[role="button"],a');
            if(!target)return;
            const t=textOf(target);
            if(!/Deep Resident/i.test(t))return;
            e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();
            return openNoFlash(hostWindow,hostDoc);
          }catch(x){}
        },true);
      }
      return true;
    }catch(e){return false}
  }
  function scan(){deepDocuments(document).forEach(patchDoc)}
  window.addEventListener('load',()=>[50,100,180,300,600,1200,2400].forEach(t=>setTimeout(scan,t)));
  setInterval(scan,500);
  scan();
})();
