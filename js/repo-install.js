import {install,decode64} from './app.js';
const select=document.querySelector('#engine-select'),button=document.querySelector('#repo-install'),info=document.querySelector('#engine-info');
function reset(){button.disabled=!select.value;button.textContent='Install';}
select.addEventListener('change',reset);
window.addEventListener('fm1-catalog-loaded',reset);
async function json(url){const r=await fetch(url,{cache:'no-store'});const data=await r.json();if(!r.ok)throw Error(data.error||`HTTP ${r.status}`);return data;}
async function bytes(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`Asset download HTTP ${r.status}`);return new Uint8Array(await r.arrayBuffer());}
function hex(buffer){return [...new Uint8Array(buffer)].map(b=>b.toString(16).padStart(2,'0')).join('');}
button.addEventListener('click',async()=>{
 const id=select.value;if(!id)return;
 button.disabled=true;button.textContent='Installing…';
 try{
  info.textContent='Looking for a published browser build…';
  const result=await json(`/api/repository/${encodeURIComponent(id)}`);
  if(!result.available){info.textContent=result.reason||'Browser port needed. No compatible build is published.';return;}
  info.textContent=`Downloading verified browser engine from ${result.repo} (${result.version})…`;
  const base=`/api/repository/${encodeURIComponent(id)}/asset/`;
  const [packageBytes,checksumBytes]=await Promise.all([bytes(base+result.package_asset_id),bytes(base+result.checksum_asset_id)]);
  const expected=new TextDecoder().decode(checksumBytes).trim().match(/^[a-fA-F0-9]{64}/)?.[0]?.toLowerCase();
  if(!expected)throw Error('Invalid SHA-256 checksum asset');
  const actual=hex(await crypto.subtle.digest('SHA-256',packageBytes));
  if(actual!==expected)throw Error('SHA-256 mismatch: package rejected');
  const p=JSON.parse(new TextDecoder().decode(packageBytes));
  if(p.format!=='fm1-web-package-v1'||!Array.isArray(p.files)||p.id!==id)throw Error('Invalid or mismatched browser package');
  const files=p.files.map(x=>[x.path,new Blob([decode64(x.base64)])]);
  await install(p,files);
  info.textContent=`Installed ${p.name} (${p.version}). Select Play in Lab.`;
 }catch(err){info.textContent=`Installation: ${err.message}`;}
 finally{reset();}
});
reset();
