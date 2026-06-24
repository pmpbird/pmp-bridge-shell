(()=>{
'use strict';
const V='1.2.0-force-white-text-fill';
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function force(el){try{el.style.setProperty('color','#fff','important');el.style.setProperty('-webkit-text-fill-color','#fff','important');el.style.setProperty('text-shadow','0 1px 2px #000','important')}catch(e){}}
function paint(box){try{force(box);box.querySelectorAll('label,small,div,p,span,b,strong,em,pre').forEach(force);let list=box.querySelector('[data-clean-list]');if(list)force(list)}catch(e){}}
function apply(doc){try{doc.querySelectorAll('[data-bank-delete-modes]').forEach(box=>{paint(box);let mode=box.getAttribute('data-mode')||'test';box.querySelectorAll('[data-clean-item]').forEach(input=>{let label=input.closest('label');if(!label)return;force(label);if(mode==='test'&&!input.checked){label.style.display='none';label.setAttribute('data-mode1-hidden','1')}else if(label.getAttribute('data-mode1-hidden')==='1'){label.style.display='block';label.removeAttribute('data-mode1-hidden')}});let note=box.querySelector('[data-clean-list]');if(note&&mode==='test'&&!box.querySelector('[data-mode1-note]')){let p=doc.createElement('div');p.setAttribute('data-mode1-note','1');p.style.margin='8px 0';p.textContent='Mode 1 shows only auto-selected obvious test data. Use Mode 2 for manual review.';note.prepend(p);force(p)}})}catch(e){}}
function scan(){docs(document).forEach(apply)}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[50,250,900,1600].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();