(() => {
  const SHORTCUT = 'PMP Vault GitHub Writer';
  const URL = 'shortcuts://run-shortcut?name=' + encodeURIComponent(SHORTCUT);
  function deep(){try{let f=document.getElementById('app'),w=f&&f.contentWindow,d=w&&(f.contentDocument||w.document);for(let i=0;i<10;i++){let n=d&&d.getElementById&&d.getElementById('app');if(!n)break;w=n.contentWindow;d=n.contentDocument||w.document}return{w,d}}catch(e){return{}}}
  function add(){const o=deep(),d=o.d;if(!d||d.getElementById('pmpVaultShortcutDirectLink'))return;const panel=d.getElementById('bridgePanel');if(!panel)return;const a=d.createElement('a');a.id='pmpVaultShortcutDirectLink';a.href=URL;a.textContent='Open Vault Shortcut';a.style.display='block';a.style.marginTop='12px';a.style.padding='14px';a.style.border='2px solid var(--line,#fff)';a.style.borderRadius='16px';a.style.background='var(--a,#a1fcfd)';a.style.color='var(--buttonText,#101827)';a.style.fontWeight='950';a.style.textAlign='center';a.style.textDecoration='none';panel.insertAdjacentElement('afterend',a)}
  setInterval(add,700);setTimeout(add,300);window.pmpOpenVaultShortcutUrl=URL;
})();
