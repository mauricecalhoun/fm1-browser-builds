import {install,decode64} from './app.js';
const status=document.querySelector('#v25-status');
for(const button of document.querySelectorAll('[data-v25-install]')){
 button.addEventListener('click',async()=>{
  const id=button.dataset.v25Install;
  if(!['hortator','jangada'].includes(id))return;
  button.disabled=true;
  try{
   status.textContent=`Loading ${id} experimental browser package…`;
   const response=await fetch(`./experimental/${id}.fm1pkg`,{cache:'no-store'});
   if(!response.ok)throw Error(`Package fetch failed: HTTP ${response.status}`);
   const p=await response.json();
   if(p.format!=='fm1-web-package-v1'||p.id!==id||!Array.isArray(p.files))throw Error('Unexpected package format or identity');
   const files=p.files.map(f=>[f.path,new Blob([decode64(f.base64)])]);
   await install({...p,name:id==='hortator'?'Hortator (experimental)':'Jangada (experimental)',description:'Experimental browser implementation. Not yet Safari-verified.'},files);
   status.textContent=`${id} installed locally. Select it in Firmware and click Play in Lab. Please test audio and controls in Safari.`;
  }catch(e){status.textContent=`${id}: ${e.message}`;}
  finally{button.disabled=false;}
 });
}
