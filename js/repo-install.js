import {install,decode64} from './app.js';
import {listPackages} from './db.js';
const select=document.querySelector('#engine-select'),button=document.querySelector('#repo-install'),info=document.querySelector('#engine-info');
let generation=0, candidate=null, busy=false;
async function json(url){const r=await fetch(url,{cache:'no-store'});const data=await r.json();if(!r.ok)throw Error(data.error||`HTTP ${r.status}`);return data;}
async function bytes(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`Asset download HTTP ${r.status}`);return new Uint8Array(await r.arrayBuffer());}
function hex(buffer){return [...new Uint8Array(buffer)].map(b=>b.toString(16).padStart(2,'0')).join('');}
function show(label,disabled){button.textContent=label;button.disabled=disabled;}
async function check(){
 const token=++generation,id=select.value;candidate=null;
 if(!id){show('Select firmware',true);return;}
 show('Checking builds…',true);
 try{
  const result=await json(`/api/repository/${encodeURIComponent(id)}`);
  if(token!==generation)return;
  if(!result.available){show('Browser port needed',true);button.title=result.reason||'';return;}
  const installed=(await listPackages()).find(p=>p.id===id);
  if(token!==generation)return;
  candidate=result;
  const releaseRev=(result.version||'').split('-web-')[1]||'';
  const installedRev=installed?.version||'';
  if(installed && releaseRev===installedRev){show('Installed · current',true);return;}
  show(installed?'Update':'Install',false);
 }catch(e){if(token!==generation)return;show('Check unavailable',true);button.title=e.message;}
}
select.addEventListener('change',check);
window.addEventListener('fm1-catalog-loaded',check);
window.addEventListener('fm1-packages-changed',check);
document.querySelector('#check-updates').addEventListener('click',check);
button.addEventListener('click',async()=>{
 const id=select.value,result=candidate;if(!id||!result||busy)return;
 busy=true;show('Installing…',true);
 try{
  info.textContent=`Downloading browser build ${result.version} from ${result.repo}…`;
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
  info.textContent=`Installed ${p.name} (${p.version}). Ready to Play in Lab.`;
 }catch(err){info.textContent=`Installation: ${err.message}`;}
 finally{busy=false;check();}
});
check();
