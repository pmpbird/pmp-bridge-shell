(function(){
  'use strict';
  const GUARD='Read this packet fully before answering; continue only from the restored direction stated inside the packet, ignore any discarded tangent or excluded branch named in the packet, and do not make code, file, memory, or project claims until you verify them from the packet, provided files, or connected source.';
  const RECEIPT_KEY='pmp_request_packet_guard_v1_receipt';
  function mark(msg){try{localStorage.setItem(RECEIPT_KEY,JSON.stringify({type:'PMP_REQUEST_PACKET_GUARD_V1_RECEIPT',version:'1.0.0',at:new Date().toISOString(),status:msg,guard:GUARD},null,2));}catch(e){}}
  function prepend(text){
    text=String(text||'');
    if(text.includes(GUARD)) return text;
    return GUARD+'\n\n'+text;
  }
  function patchWindow(w){
    try{
      if(!w||w.__pmpRequestPacketGuardV1) return false;
      const hasPrompt=typeof w.outsideProjectPrompt==='function';
      const hasPacket=typeof w.packetRequest==='function';
      if(!hasPrompt&&!hasPacket) return false;
      w.__pmpRequestPacketGuardV1=true;
      if(hasPrompt){
        const oldPrompt=w.outsideProjectPrompt;
        w.outsideProjectPrompt=function(){return prepend(oldPrompt.apply(this,arguments));};
      }
      if(hasPacket){
        const oldPacket=w.packetRequest;
        w.packetRequest=function(){
          const result=oldPacket.apply(this,arguments);
          setTimeout(function(){
            try{
              if(typeof w.currentOutput==='string') w.currentOutput=prepend(w.currentOutput);
              const bp=w.document&&w.document.getElementById&&w.document.getElementById('bridgePanel');
              if(bp){
                if('value' in bp) bp.value=prepend(bp.value);
                else if(bp.textContent) bp.textContent=prepend(bp.textContent);
              }
              mark('patched_packet_request_output');
            }catch(e){}
          },0);
          return result;
        };
      }
      mark('installed');
      return true;
    }catch(e){mark('error_'+String(e).slice(0,80));return false;}
  }
  function scan(){
    let ok=false;
    try{ok=patchWindow(window)||ok;}catch(e){}
    try{document.querySelectorAll('iframe,frame').forEach(function(f){try{if(f.contentWindow)ok=patchWindow(f.contentWindow)||ok;}catch(e){}});}catch(e){}
    if(ok) mark('installed');
  }
  scan();
  [200,700,1500,3000].forEach(function(t){setTimeout(scan,t);});
  window.PMPRequestPacketGuardV1={version:'1.0.0',guard:GUARD,install:scan};
})();
