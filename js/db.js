export const DB_NAME = 'fm1-firmware-lab-v1';
export function openDB() { return new Promise((resolve,reject)=>{const r=indexedDB.open(DB_NAME,2);r.onupgradeneeded=()=>{const d=r.result;if(!d.objectStoreNames.contains('packages'))d.createObjectStore('packages',{keyPath:'id'});if(!d.objectStoreNames.contains('files'))d.createObjectStore('files',{keyPath:'key'});if(!d.objectStoreNames.contains('backups'))d.createObjectStore('backups',{keyPath:'id'});};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});}
export function request(r){return new Promise((ok,bad)=>{r.onsuccess=()=>ok(r.result);r.onerror=()=>bad(r.error);});}
export async function listPackages(){const d=await openDB();try{return await request(d.transaction('packages').objectStore('packages').getAll());}finally{d.close();}}
export async function installPackage(meta,files){
 const d=await openDB();try{
  const tx=d.transaction(['packages','files','backups'],'readwrite');
  const done=new Promise((ok,bad)=>{tx.oncomplete=ok;tx.onerror=()=>bad(tx.error);tx.onabort=()=>bad(tx.error);});
  const p=tx.objectStore('packages'),f=tx.objectStore('files'),b=tx.objectStore('backups');
  const old=await request(p.get(meta.id));
  if(old){
   const saved=[];for(const path of old.paths){const record=await request(f.get(meta.id+'/'+path));if(record)saved.push({path,blob:record.blob});}
   b.put({id:meta.id,meta:old,files:saved,backedUpAt:Date.now()});
   for(const path of old.paths)f.delete(meta.id+'/'+path);
  }
  for(const [path,blob] of files)f.put({key:meta.id+'/'+path,blob});
  p.put({...meta,paths:files.map(([path])=>path),installedAt:Date.now()});
  await done;
 }finally{d.close();}
}
export async function listBackups(){const d=await openDB();try{return await request(d.transaction('backups').objectStore('backups').getAll());}finally{d.close();}}
export async function rollbackPackage(id){
 const d=await openDB();try{
  const tx=d.transaction(['packages','files','backups'],'readwrite');
  const done=new Promise((ok,bad)=>{tx.oncomplete=ok;tx.onerror=()=>bad(tx.error);tx.onabort=()=>bad(tx.error);});
  const p=tx.objectStore('packages'),f=tx.objectStore('files'),b=tx.objectStore('backups');
  const backup=await request(b.get(id));if(!backup)throw Error('No rollback available');
  const current=await request(p.get(id));if(current)for(const path of current.paths)f.delete(id+'/'+path);
  for(const {path,blob} of backup.files)f.put({key:id+'/'+path,blob});
  p.put(backup.meta);b.delete(id);await done;
 }finally{d.close();}
}
export async function removePackage(id){const d=await openDB();try{const tx=d.transaction(['packages','files'],'readwrite');const done=new Promise((ok,bad)=>{tx.oncomplete=ok;tx.onerror=()=>bad(tx.error);});const p=tx.objectStore('packages'),f=tx.objectStore('files');const old=await request(p.get(id));if(old){for(const path of old.paths)f.delete(id+'/'+path);p.delete(id);}await done;}finally{d.close();}}
