import {installPackage, listPackages} from './db.js';
const status = document.querySelector('#v25-status');
function decode64(s){const raw=atob(s), bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);return bytes;}
function validPath(p){return typeof p==='string'&&!!p&&!p.startsWith('/')&&!p.includes('\\')&&!p.split('/').some(x=>!x||x==='..')&&!p.startsWith('__installed__/');}
for(const button of document.querySelectorAll('[data-v25-install]')){
 button.addEventListener('click',async()=>{
  const id=button.dataset.v25Install;if(!['hortator','jangada'].includes(id))return;
  button.disabled=true;
  try{
   status.textContent=`Loading ${id} experimental browser package…`;
   const response=await fetch(`./experimental/${id}.fm1pkg`,{cache:'no-store'});
   if(!response.ok)throw Error(`Package fetch failed: HTTP ${response.status}`);
   const p=await response.json();
   if(p.format!=='fm1-web-package-v1'||p.id!==id||!Array.isArray(p.files))throw Error('Unexpected package format or identity');
   const entry=p.entry||'index.html';
   if(!validPath(entry)||!p.files.length||p.files.some(f=>!validPath(f.path)||typeof f.base64!=='string')||!p.files.some(f=>f.path===entry))throw Error('Invalid package paths or missing entry HTML');
   const paths=new Set();let total=0;
   const files=p.files.map(f=>{if(paths.has(f.path))throw Error('Duplicate package path');paths.add(f.path);const blob=new Blob([decode64(f.base64)]);total+=blob.size;return [f.path,blob];});
   if(total>150*1024*1024)throw Error('Package too large');
   if((await listPackages()).some(x=>x.id===id)&&!confirm(`Replace installed ${id}?`))return;
   await installPackage({id,name:id==='hortator'?'Hortator (experimental)':'Jangada (experimental)',version:p.version||'experimental',entry,description:'Experimental browser implementation; Safari playback not verified.',source:p.source||''},files);
   window.dispatchEvent(new Event('fm1-packages-changed'));
   const select=document.querySelector('#engine-select');
   if(select){select.value=id;select.dispatchEvent(new Event('change',{bubbles:true}));}
   status.textContent=`${id} installed. Select it from Firmware and click Play in Lab.`;
  }catch(e){status.textContent=`${id}: ${e.message}`;console.error('v2.5 installation error:',e);}
  finally{button.disabled=false;}
 });
}
