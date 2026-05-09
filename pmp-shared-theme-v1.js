(()=>{
  const COLOR_KEY='pmp_single_colors_v6';
  const PREV_KEY='pmp_single_colors_v5';
  const READ_KEY='pmp_readability_layer_v6';
  const DEFAULT={accent:'#a1fcfd',background:'#52b5df',card:'#46a9d3',line:'#ffffff'};
  function read(k,f){try{const v=localStorage.getItem(k);return v?JSON.parse(v):f}catch(e){return f}}
  function clean(c){return{accent:(c&&c.accent)||DEFAULT.accent,background:(c&&c.background)||DEFAULT.background,card:(c&&c.card)||DEFAULT.card,line:(c&&c.line)||DEFAULT.line}}
  function theme(){return clean({...read(PREV_KEY,{}),...read(COLOR_KEY,{})})}
  function readLevel(){const r=read(READ_KEY,{value:50});const v=+r.value;return Number.isFinite(v)?Math.max(0,Math.min(100,v)):50}
  function hex(h){h=(h||'#000').replace('#','');if(h.length===3)h=h.split('').map(x=>x+x).join('');const n=parseInt(h,16);return{r:(n>>16)&255,g:(n>>8)&255,b:n&255}}
  function toHex(c){const f=x=>Math.max(0,Math.min(255,Math.round(x))).toString(16).padStart(2,'0');return'#'+f(c.r)+f(c.g)+f(c.b)}
  function lum(h){const c=hex(h);const a=[c.r,c.g,c.b].map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]}
  function mix(a,b,t){const x=hex(a),y=hex(b);return toHex({r:x.r+(y.r-x.r)*t,g:x.g+(y.g-x.g)*t,b:x.b+(y.b-x.b)*t})}
  function bestText(bg){return lum(bg)>.48?'#071523':'#f8fbff'}
  function safeMeta(color){let m=document.querySelector('meta[name="theme-color"]');if(!m){m=document.createElement('meta');m.name='theme-color';document.head.appendChild(m)}m.content=color}
  function apply(){
    const c=theme(), v=readLevel(), t=v/100, strong=Math.pow(t,.72);
    const bgText=bestText(c.background), cardText=bestText(c.card), accentText=bestText(c.accent);
    const panel=mix(c.card,bgText==='#071523'?'#000000':'#ffffff',.12+.24*strong);
    const input=mix('#0c141e',bgText==='#071523'?'#ffffff':'#000000',.03+.18*strong);
    const note=mix('#123024',bgText==='#071523'?'#ffffff':'#000000',.02+.14*strong);
    const soft=mix(panel,bgText==='#071523'?'#000000':'#ffffff',.08+.16*strong);
    const line=v<5?c.line:mix(c.line,bgText==='#071523'?'#071523':'#ffffff',.02+.08*strong);
    const root=document.documentElement.style;
    root.setProperty('--a',c.accent);
    root.setProperty('--bg',c.background);
    root.setProperty('--floor',c.background);
    root.setProperty('--card',c.card);
    root.setProperty('--themeLine',c.line);
    root.setProperty('--line',line);
    root.setProperty('--text',cardText);
    root.setProperty('--pageText',bgText);
    root.setProperty('--buttonText',accentText);
    root.setProperty('--panel',panel);
    root.setProperty('--input',input);
    root.setProperty('--noteBg',note);
    root.setProperty('--softPanel',soft);
    root.setProperty('--muted',cardText==='#071523'?mix('#234a5d','#071523',.35+.35*strong):mix('#c9d9e6','#ffffff',.25+.45*strong));
    root.setProperty('--shadow','0 '+(8+Math.round(16*strong))+'px '+(18+Math.round(28*strong))+'px rgba(0,0,0,'+(.16+.28*strong)+')');
    root.setProperty('--miniShadow','0 '+(4+Math.round(8*strong))+'px '+(12+Math.round(18*strong))+'px rgba(0,0,0,'+(.14+.24*strong)+')');
    root.setProperty('--radius','28px');
    document.body.style.background=c.background;
    safeMeta(c.background);
  }
  function installBaseCss(){
    if(document.getElementById('pmpSharedThemeCss'))return;
    const s=document.createElement('style');s.id='pmpSharedThemeCss';s.textContent=`
      *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
      html,body{margin:0;min-height:100%;background:var(--floor);color:var(--pageText);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;-webkit-text-size-adjust:100%}
      body{padding:calc(env(safe-area-inset-top) + 46px) 16px calc(env(safe-area-inset-bottom) + 32px)}
      .pmp-wrap{max-width:920px;margin:0 auto}
      .pmp-toprail{position:fixed;left:0;right:0;top:0;z-index:50;height:calc(env(safe-area-inset-top) + 58px);background:linear-gradient(var(--floor),rgba(255,255,255,.08));pointer-events:none}
      .pmp-topbtn{position:fixed;top:calc(env(safe-area-inset-top) + 8px);z-index:60;background:var(--a);color:var(--buttonText);border:3px solid var(--line);border-radius:999px;padding:9px 16px;font-weight:950;font-size:17px;box-shadow:var(--shadow);text-decoration:none;min-height:42px;display:flex;align-items:center;justify-content:center}
      .pmp-launcher{left:16px}.pmp-resident{right:16px}
      .card,.pmp-card{background:var(--panel);color:var(--text);border:4px solid var(--line);border-radius:var(--radius);padding:22px;margin:18px 0;box-shadow:var(--shadow)}
      h1{font-size:42px;line-height:1.02;margin:0 0 8px;color:var(--text)}h2{font-size:28px;margin:0 0 12px;color:var(--text)}
      .sub,.pmp-sub{font-size:20px;font-weight:850;color:var(--muted);line-height:1.32;margin:0 0 14px}
      button,a.btn,.pmp-btn{border:0;border-radius:20px;background:var(--a);color:var(--buttonText);font-weight:950;font-size:19px;padding:17px 18px;min-height:64px;box-shadow:inset 0 -2px 0 rgba(0,0,0,.14),var(--miniShadow);text-align:center;text-decoration:none;display:flex;align-items:center;justify-content:center;line-height:1.18;width:100%}
      .big,.pmp-big{font-size:24px;min-height:86px}.soft,.pmp-soft{background:var(--softPanel);color:var(--text);border:2px solid rgba(255,255,255,.20)}
      .grid,.pmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.stack,.pmp-stack{display:grid;gap:14px}
      textarea,input,select{width:100%;background:var(--input);color:#f5fbff;border:2px solid rgba(255,255,255,.22);border-radius:18px;padding:14px;font-size:16px;font-family:inherit}
      textarea{min-height:190px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
      .status,.note,.pmp-status{white-space:pre-wrap;background:var(--noteBg);border:3px solid var(--line);border-radius:20px;padding:16px;color:#d7ffe8;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto;max-height:360px}
      .warn,.pmp-warn{background:#3b2a0c;color:#ffe8b3}.helper,.pmp-helper{background:var(--input);border-left:6px solid var(--a);border-radius:18px;padding:14px;color:#eaf7ff;line-height:1.35;font-size:18px}
      .panel{display:none;margin-top:14px}.panel.on{display:block}.small{font-size:14px;color:var(--muted)}
      @media(max-width:700px){.grid,.pmp-grid{grid-template-columns:1fr}h1{font-size:34px}}
    `;document.head.appendChild(s);
  }
  function installTopTabs(){
    if(document.querySelector('.pmp-toprail'))return;
    const rail=document.createElement('div');rail.className='pmp-toprail';
    const l=document.createElement('a');l.className='pmp-topbtn pmp-launcher';l.textContent='Launcher';l.href='pmp-home-single-v12.html#control';
    const r=document.createElement('button');r.className='pmp-topbtn pmp-resident';r.textContent='Resident';r.onclick=()=>{alert('Resident tab is present. Shared Resident drawer is the next tool-layer upgrade.')};
    document.body.prepend(rail,l,r);
  }
  window.PMPTheme={apply,installBaseCss,installTopTabs,theme,readLevel};
  function boot(){installBaseCss();installTopTabs();apply()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
  window.addEventListener('storage',apply);
})();
