window.PMPNativeContrastBridgeV2=(function(){
const COLOR_KEY='pmp_single_colors_v6',PREV_KEY='pmp_single_colors_v5',READ_KEY='pmp_readability_layer_v6';
const DEFAULT={accent:'#acd1fb',background:'#f3ded4',card:'#ffffff',line:'#07101c'};
function j(k){try{return JSON.parse(localStorage.getItem(k)||'{}')}catch(e){return{}}}
function cleanColor(v,f){v=String(v||'').trim();return /^#[0-9a-fA-F]{6}$/.test(v)?v:f}
function rawColors(){return{...DEFAULT,...j(PREV_KEY),...j(COLOR_KEY)}}
function colors(){let c=rawColors();let bg=cleanColor(c.background,DEFAULT.background);let card=cleanColor(c.card,DEFAULT.card);let accent=cleanColor(c.accent,DEFAULT.accent);let line=cleanColor(c.line,DEFAULT.line);if(bg.toLowerCase()==='#52b5df')bg=DEFAULT.background;if(card.toLowerCase()==='#46a9d3')card=DEFAULT.card;if(accent.toLowerCase()==='#a1fcfd')accent=DEFAULT.accent;return{accent,background:bg,card,line}}
function readLevel(){let r=j(READ_KEY);let v=Number.isFinite(+r.value)?+r.value:50;return Math.max(0,Math.min(100,v))}
function css(){let c=colors(),r=readLevel();let bw=r>=85?3:2;return `:root{--a:${c.accent}!important;--bg:${c.background}!important;--floor:${c.background}!important;--card:${c.card}!important;--line:${c.line}!important;--text:#07101c!important;--muted:#234a5d!important;--panel:#172234!important;--input:#0c141e!important;--buttonText:#07101c!important;--noteBg:#123024!important;--tabBg:#ffffff!important;--borderWidth:${bw}px!important;--buttonBorder:2px!important;--shadow:0 14px 34px #0003!important;--miniShadow:0 3px 12px #0002!important}
html,body,#gate,iframe#app{background:var(--floor)!important;color:var(--text)!important}
body:before{background:var(--floor)!important}
.wrap{background:var(--floor)!important}
.card,#card{background:var(--card)!important;border-color:var(--line)!important;color:var(--text)!important}
#card{box-shadow:var(--shadow)!important}
h1,h2,.sub,.txt{color:var(--text)!important}
.badge,.tiny,.float,.big,button:not(.dark):not(.tab):not(.mini){background:var(--a)!important;color:var(--buttonText)!important;border-color:var(--line)!important}
.big{border:2px solid var(--line)!important}
.dark,.mini,.panel,.dock,.drawer,.drop{background:var(--panel)!important;color:#eef4fb!important;border-color:var(--line)!important}
#colorPanel{background:transparent!important;border:0!important;box-shadow:none!important;padding:0!important;color:var(--text)!important}
#colorPanel .mini{background:var(--a)!important;color:var(--buttonText)!important;border:2px solid var(--line)!important}
#colorBody.panel,#colorBody{background:var(--card)!important;color:var(--text)!important;border-color:var(--line)!important}
.note,.reply,.status{background:var(--noteBg)!important;color:#d8ffe2!important;border-color:var(--line)!important}
.warn{background:var(--panel)!important;color:#eef4fb!important;border-color:var(--line)!important}
input,textarea,select,pre{background:var(--input)!important;color:#eef4fb!important;border-color:var(--line)!important}
.chip{background:var(--input)!important;color:#d8ffe2!important;border-color:var(--line)!important}
.pill.ok,.ok{background:#123024!important;color:#d8ffe2!important}.pill.bad,.bad,.diagnostic,.block{background:#351414!important;color:#ffd1d1!important;border-color:#ff9a9a!important}
.tabs{background:#ffffff!important;border-top:0!important;border-left:0!important;border-right:0!important;border-bottom:0!important;box-shadow:0 -8px 24px #0002!important}
.tab{background:transparent!important;border:0!important;box-shadow:none!important;outline:0!important}
.tab.on{color:var(--a)!important;text-shadow:none!important}
#repoFrame{background:var(--floor)!important}
#secretPanel{background:var(--card)!important;border-color:var(--line)!important;color:var(--text)!important}
#secretPanel h1,#secretPanel h2{color:var(--text)!important}#secretOut{background:var(--noteBg)!important;color:#d8ffe2!important;border-color:var(--line)!important}`}
function applyDoc(doc,label){try{if(!doc||!doc.head)return false;let st=doc.getElementById('pmp-native-contrast-bridge-v2-style');if(!st){st=doc.createElement('style');st.id='pmp-native-contrast-bridge-v2-style';doc.head.appendChild(st)}st.textContent=css();let c=colors();let m=doc.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',c.background);doc.documentElement.dataset.pmpNativeContrastBridgeV2=label||'applied';return true}catch(e){return false}}
function applyChildFrames(doc){let ok=0;try{Array.from((doc||document).querySelectorAll('iframe')).forEach(f=>{try{if(applyDoc(f.contentDocument||f.contentWindow.document,'child-frame'))ok++}catch(e){}})}catch(e){}return ok}
function apply(){let main=applyDoc(document,'main');let frames=applyChildFrames(document);return{type:'PMP_NATIVE_CONTRAST_BRIDGE_REPORT',version:'2.0.0-direct-native-visuals',built_at:new Date().toISOString(),main_applied:main,child_frames_applied:frames,readability:readLevel(),colors:colors(),rule:'Read-only visual bridge. Does not change route, map, cache, storage, or app state except reading existing local color settings.'}}
function start(){apply();setTimeout(apply,50);setTimeout(apply,250);setTimeout(apply,800);setTimeout(apply,1600);setInterval(apply,2000)}
return{apply,start,colors,readLevel};
})();try{window.PMPNativeContrastBridgeV2.start()}catch(e){}