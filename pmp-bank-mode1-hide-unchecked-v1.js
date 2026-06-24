(()=>{
'use strict';
const V='1.6.0-dark-list-scoped';
function docs(root,d,a){a=a||[];d=d||0;if(!root||d>8)return a;try{a.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{let z=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(z)docs(z,d+1,a)}catch(e){}})}catch(e){}return a}
function set(el,k,v){try{el.style.setProperty(k,v,'important')}catch(e){}}
function text(el){set(el,'color','#fff');set(el,'-webkit-text-fill-color','#fff');set(el,'text-shadow','none');set(el,'font-weight','850')}
function skin(box){try{let list=box.querySelector('[data-clean-list]');if(list){list.className='note';set(list,'background','var(--noteBg,#123024)');set(list,'color','#fff');set(list,'border-color','var(--line)');set(list,'padding','14px');set(list,'margin','10px 0');text(list)}box.querySelectorAll('[data-clean-list] label,[data-clean-list] span,[data-clean-list] small,[data-clean-list] div').forEach(text);box.querySelectorAll('[data-clean-list] label').forEach(x=>{set(x,'display','grid');set(x,'grid-template-columns','44px 1fr');set(x,'gap','10px');set(x,'align-items','center');set(x,'margin','10px 0')})}catch(e){}}
function apply(doc){try{doc.querySelectorAll('[data-bank-delete-modes]').forEach(box=>{skin(box);let mode=box.getAttribute('data-mode')||'test';box.querySelectorAll('[data-clean-item]').forEach(input=>{let label=input.closest('label');if(!label)return;if(mode==='test'&&!input.checked){label.style.display='none';label.setAttribute('data-mode1-hidden','1')}else if(label.getAttribute('data-mode1-hidden')==='1'){label.style.display='grid';label.removeAttribute('data-mode1-hidden')}});let note=box.querySelector('[data-clean-list]');if(note&&mode==='test'&&!box.querySelector('[data-mode1-note]')){let p=doc.createElement('div');p.setAttribute('data-mode1-note','1');p.className='note';p.style.margin='8px 0';p.style.padding='10px';p.textContent='Mode 1 shows only auto-selected obvious test data. Use Mode 2 for manual review.';note.prepend(p);skin(box)}})}catch(e){}}
function scan(){docs(document).forEach(apply)}
window.PMPBankMode1HideUncheckedV1={version:V,scan};
window.addEventListener('load',()=>[50,250,900,1600].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();