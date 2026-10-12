import {firmwareTitle,firmwareDescription} from './names.js';
// Accessible searchable combobox, synchronized with the existing firmware selector.
const select=document.querySelector('#engine-select');
const input=document.querySelector('#combo-input');
const toggle=document.querySelector('#combo-toggle');
const list=document.querySelector('#combo-options');
let active=-1;
let firmwareDetails=new Map();
window.addEventListener('fm1-catalog-loaded',e=>{firmwareDetails=new Map(e.detail.map(f=>[f.id,f]));if(!list.hidden)draw();});
function options(){return [...select.options].filter(o=>o.value);}
function selectedLabel(){const o=select.selectedOptions[0];return o?.value?o.textContent:'';}
function close(){list.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');active=-1;}
function show(){list.hidden=false;input.setAttribute('aria-expanded','true');draw();}
function choose(id){select.value=id;select.dispatchEvent(new Event('change',{bubbles:true}));input.value=selectedLabel();close();}
function draw(){const term=input.value.trim().toLowerCase();const opts=options().filter(o=>{const f=firmwareDetails.get(o.value);return !term||[o.textContent,f?.author,f?.what,f?.description,f?.repo,f?.kind].flat().filter(Boolean).join(' ').toLowerCase().includes(term);});list.replaceChildren();active=Math.min(active,opts.length-1);if(!opts.length){const msg=document.createElement('div');msg.className='px-4 py-3 text-sm text-slate-400';msg.textContent='No matching firmware';list.append(msg);return;}opts.forEach((o,i)=>{const b=document.createElement('button');b.type='button';b.id='firmware-opt-'+i;b.role='option';b.className='firmware-option flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-slate-200';b.setAttribute('aria-selected',String(select.value===o.value));const f=firmwareDetails.get(o.value);const label=document.createElement('span');label.textContent=f?firmwareTitle(f):o.textContent.replace(/^✓ Installed · /,'');const badge=document.createElement('span');badge.className=o.textContent.startsWith('✓')?'shrink-0 rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300':'shrink-0 text-xs text-slate-500';badge.textContent=o.textContent.startsWith('✓')?'✓ Installed':'Not installed';const copy=document.createElement('span');copy.className='min-w-0 flex-1';copy.append(label);if(f?.author){const meta=document.createElement('span');meta.className='block truncate text-xs text-slate-400';meta.textContent=`${f.author} · Upstream ${f.version||'unknown'}`;copy.append(meta);}if(f){const desc=document.createElement('span');desc.className='mt-1 block text-xs leading-snug text-slate-400 line-clamp-2';desc.textContent=firmwareDescription(f);copy.append(desc);}b.append(copy,badge);b.addEventListener('mousedown',e=>e.preventDefault());b.addEventListener('click',()=>choose(o.value));list.append(b);});}
function move(step){const buttons=[...list.querySelectorAll('[role=option]')];if(!buttons.length)return;active=(active+step+buttons.length)%buttons.length;buttons.forEach((b,i)=>b.classList.toggle('bg-slate-700',i===active));input.setAttribute('aria-activedescendant',buttons[active].id);buttons[active].scrollIntoView({block:'nearest'});}
input.addEventListener('focus',()=>{input.value='';active=-1;show();});
input.addEventListener('click',()=>{if(list.hidden){input.value='';active=-1;show();}});
input.addEventListener('input',()=>{active=-1;show();});
input.addEventListener('keydown',e=>{if(e.key==='Escape'){close();input.value=selectedLabel();}else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(list.hidden)show();move(e.key==='ArrowDown'?1:-1);}else if(e.key==='Enter'&&!list.hidden){e.preventDefault();const buttons=[...list.querySelectorAll('[role=option]')];if(buttons.length){const b=buttons[Math.max(0,active)];b.click();}}});
toggle.addEventListener('click',()=>{if(list.hidden){input.value='';active=-1;input.focus();show();}else{close();input.value=selectedLabel();}});
document.addEventListener('pointerdown',e=>{if(!e.target.closest('#combo-input')&&!e.target.closest('#combo-toggle')&&!e.target.closest('#combo-options')){close();input.value=selectedLabel();}});
select.addEventListener('change',()=>{input.value=selectedLabel();});
const observer=new MutationObserver(()=>{if(list.hidden)input.value=selectedLabel();else draw();});observer.observe(select,{childList:true,subtree:true});
input.value=selectedLabel();
