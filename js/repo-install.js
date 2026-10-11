import {install,decode64} from './app.js';
const select=document.querySelector('#engine-select'),button=document.querySelector('#repo-install'),info=document.querySelector('#engine-info');
let availability=null, checkedId='';
function reset(){availability=null;checkedId='';button.disabled=!select.value;button.textContent='Find browser build';}
select.addEventListener('change',reset);
window.addEventListener('fm1-catalog-loaded',reset);
async function json(url){const r=await fetch(url,{cache:'no-store'});const data=await r.json();if(!r.ok)throw Error(data.error||`HTTP ${r.status}`);return data;}
async function bytes(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`Asset download HTTP ${r.status}`);return new Uint8Array(await r.arrayBuffer());}
function hex(buffer){return [...new Uint8Array(buffer)].map(b=>b.toString(16).padStart(2,'0')).join('');}
button.addEventListener('click',async()=>{
 const id=select.value;if(!id)return;
 button.disabled=true;
 try{
  if(checkedId!==id||!availability){info.textContent='Checking upstream GitHub releases for a verified browser build…';
   const result=await json(`/api/repository/${encodeURIComponent(id)}`);
   checkedId=id;availability=result.available?result:null;
   if(!availability){info.textContent=result.reason||'No browser build published.';button.textContent='Find browser build';return;}
   info.textContent=`Verified browser package published by ${result.repo} (${result.version}).`;
   button.textContent='Install browser engine';return;
  }
  info.textContent='Downloading browser firmware and checksum…';
  const base=`/api/repository/${encodeURIComponent(id)}/asset/`;
  const [packageBytes,checksumBytes]=await Promise.all([bytes(base+availability.package_asset_id),bytes(base+availability.checksum_asset_id)]);
  const expected=new TextDecoder().decode(checksumBytes).trim().match(/^[a-fA-F0-9]{64}/)?.[0]?.toLowerCase();
  if(!expected)throw Error('Invalid .sha256 checksum asset');
  const actual=hex(await crypto.subtle.digest('SHA-256',packageBytes));
  if(actual!==expected)throw Error('SHA-256 mismatch: package rejected');
  const p=JSON.parse(new TextDecoder().decode(packageBytes));
  if(p.format!=='fm1-web-package-v1'||!Array.isArray(p.files)||p.id!==id)throw Error('Invalid or mismatched browser package');
  const files=p.files.map(x=>[x.path,new Blob([decode64(x.base64)])]);
  await install(p,files);
  info.textContent=`Installed ${p.name}. Select Play in Lab.`;
  reset();
 }catch(err){info.textContent=`Repository installation: ${err.message}`;}
 finally{button.disabled=!select.value;}
});
reset();
