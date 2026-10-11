import {firmwareTitle} from './names.js';
import {listPackages} from './db.js';
const select=document.querySelector('#engine-select'),frame=document.querySelector('#engine-frame'),empty=document.querySelector('#engine-empty'),info=document.querySelector('#engine-info');
const launchButton=document.querySelector('#engine-launch'),openButton=document.querySelector('#engine-open'),reloadButton=document.querySelector('#engine-reload');
let packages=[],catalog=[];
function safeUrl(url){try{const u=new URL(url);return u.protocol==='https:'?u.href:null;}catch{return null;}}
function urlFor(p){return './__installed__/'+encodeURIComponent(p.id)+'/'+p.entry.split('/').map(encodeURIComponent).join('/');}
function selected(){return {pkg:packages.find(p=>p.id===select.value),entry:catalog.find(f=>f.id===select.value)};}
function updateControls(){const {pkg,entry}=selected();launchButton.disabled=!pkg;launchButton.textContent='Play in Lab';openButton.hidden=true;reloadButton.disabled=!pkg;info.textContent=pkg?`✓ ${pkg.name} ${pkg.version} installed. Ready to play inside the Lab.`:entry?`${firmwareTitle(entry)} · No compatible browser engine installed. Hardware firmware packages cannot run in Safari.`:'Choose a firmware.';const state=document.querySelector('#firmware-state');if(state){state.textContent=pkg?'✓ Installed':'Not installed';state.className=pkg?'rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300':'rounded-full border border-line px-3 py-1 text-xs text-slate-400';}}
async function refresh(){const previous=select.value;packages=await listPackages();const ids=new Set();select.replaceChildren(new Option('Choose firmware…',''));for(const f of catalog){ids.add(f.id);const p=packages.find(x=>x.id===f.id);select.add(new Option(`${p?'✓ Installed · ':''}${firmwareTitle(f)}`,f.id));}for(const p of packages){if(!ids.has(p.id))select.add(new Option(`✓ Installed · ${firmwareTitle(p)}`,p.id));}if([...select.options].some(o=>o.value===previous))select.value=previous;else if(packages.length===1)select.value=packages[0].id;updateControls();}
function launch(){const {pkg,entry}=selected();if(pkg){frame.src=urlFor(pkg);frame.hidden=false;empty.hidden=true;info.textContent=`Running ${pkg.name} ${pkg.version} from IndexedDB. Stop playback before switching.`;history.replaceState(null,'','#'+encodeURIComponent(pkg.id));}else{info.textContent='No browser-compatible build installed for this firmware.';}}
launchButton.addEventListener('click',launch);
reloadButton.addEventListener('click',()=>{if(!frame.hidden)frame.src=frame.src;else launch();});
openButton.addEventListener('click',()=>{const {pkg,entry}=selected();const url=pkg?urlFor(pkg):safeUrl(entry?.play)||safeUrl(entry?.source||(entry?.repo?'https://github.com/'+entry.repo:null));if(url)window.open(url,'_blank','noopener,noreferrer');});
select.addEventListener('change',()=>{if(!frame.hidden){frame.src='about:blank';frame.hidden=true;empty.hidden=false;}updateControls();window.dispatchEvent(new CustomEvent('fm1-selection-changed',{detail:{id:select.value}}));});
window.addEventListener('fm1-catalog-loaded',e=>{catalog=e.detail;refresh().catch(err=>info.textContent=err.message);});
window.addEventListener('fm1-packages-changed',()=>refresh().catch(err=>info.textContent=err.message));
refresh().then(()=>{const requested=decodeURIComponent(location.hash.slice(1));if(packages.some(p=>p.id===requested)){select.value=requested;launch();}}).catch(err=>info.textContent=err.message);
