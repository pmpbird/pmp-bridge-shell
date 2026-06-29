(()=>{
'use strict';
const V='1.0.0-direct-frame-owner-loader';
const SCRIPTS=[
  {id:'pmpBankScreenOwnerV1DirectFrame',src:'pmp-bank-screen-owner-v1.js',fresh:'bank-screen-owner-v106-persistent-bank-detail-scan-20260629D'},
  {id:'pmpContinuousRunLevelUIScopeV1DirectFrame',src:'pmp-continuous-run-level-ui-scope-v1.js',fresh:'level-ui-scope-v117-restore-missing-level1-level2-20260629D'}
];
function now(){return new Date().toISOString()}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>10)return a;try{a.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,a,n+1)}catch(e){}})}catch(e){}return a}
function inject(d){if(!d||!d.body)return 0;let made=0;SCRIPTS.forEach(s=>{try{if(d.getElementById(s.id))return;let x=d.createElement('script');x.id=s.id;x.src=s.src+'?fresh='+s.fresh+'-'+Date.now();d.body.appendChild(x);made++}catch(e){}});return made}
function scan(){let made=0;docs(document).forEach(d=>{made+=inject(d)});try{localStorage.setItem('pmp_continuous_run_bank_order_frame_loader_v1_receipt',JSON.stringify({type:'PMP_CONTINUOUS_RUN_BANK_ORDER_FRAME_LOADER_V1',version:V,at:now(),scripts:SCRIPTS.map(x=>x.src),new_injections:made},null,2))}catch(e){}}
window.PMPContinuousRunBankOrderFrameLoaderV1={version:V,scan};
window.addEventListener('load',()=>[100,400,900,1800,3200].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1200);
scan();
})();