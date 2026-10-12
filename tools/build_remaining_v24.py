#!/usr/bin/env python3
"""Attempt 11 independent FM-1 browser builds; package only validated file sets.
Run in disposable CI: upstream build scripts are untrusted code.
"""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, traceback

TARGETS = {
 'salt': ('ChanceTheMaker/Felucca','web/audio'),
 'floyd': ('renebohne/sloop-fm1',None),
 'sloopbanks': ('majnikool/sloop-fm1',None),
 'sloopdx': ('zvenson/dxsloop',None),
 'zp12': ('zvenson/zp12',None),
 'hortator': ('deadactive/hortator','web/sim'),
 'jangada': ('zednaked/jangada','web/studio'),
 'melodee': ('keremimo/melodee',None),
 'choralroot': ('Quixotic7/ChoralRootFM1','tools/emu'),
 'dinghy': ('zvenson/dinghy',None),
 'chord': ('math0ne/fm1-chord',None),
}

def run(args, cwd=None, timeout=420):
 try:
  p=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
  return p.returncode,p.stdout[-60000:]
 except subprocess.TimeoutExpired as e:
  return 124,'Timed out: '+str(e)

def main():
 p=argparse.ArgumentParser();p.add_argument('--id',choices=TARGETS,required=True);p.add_argument('--out',default='dist/v24');a=p.parse_args()
 out=pathlib.Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 ident=a.id;repo,hint=TARGETS[ident];source=out/'source';result={'id':ident,'upstream':repo,'status':'not_attempted','published':False,'safari_verified':False,'attempts':[],'revision':None,'package':None}
 def attempt(label,cmd,cwd,timeout=420):
  code,log=run(cmd,cwd,timeout);(out/(label+'.log')).write_text(log)
  result['attempts'].append({'step':label,'exit_code':code,'log':label+'.log'})
  return code
 try:
  if attempt('clone',['git','clone','--depth','1','https://github.com/'+repo+'.git',str(source)],out,180):
   result['status']='clone_failed';return
  result['revision']=run(['git','rev-parse','HEAD'],source,15)[1].strip()
  # Explicit build attempts, never claim hardware-only firmware is a browser engine.
  if (source/'tools/build.py').is_file():
   attempt('generate',[sys.executable,'-c','from tools.build import generate; generate()'],source,120)
  scripts=[]
  if (source/'web/emu/build.sh').is_file():scripts.append('web/emu/build.sh')
  if ident=='choralroot' and (source/'tools/emu/build.sh').is_file():scripts.append('tools/emu/build.sh')
  for i,script in enumerate(scripts):
   attempt('browser-build-'+str(i),['bash',script],source,420)
  # For JS/browser-native implementations, stage only their own browser subtree.
  candidates=[]
  if (source/'build/emu/index.html').is_file():candidates.append(source/'build/emu')
  if ident=='salt':
   # Salt has a browser audio engine, not a proven complete browser UI.
   if (source/'web/audio/engine.wasm').is_file():result['audio_wasm_sha256']=hashlib.sha256((source/'web/audio/engine.wasm').read_bytes()).hexdigest()
  if ident=='hortator':candidates.append(source/'web/sim')
  if ident=='jangada':candidates.append(source/'web/studio')
  if ident=='choralroot':candidates.extend([source/'tools/emu/build',source/'tools/emu/web'])
  valid=None
  for folder in candidates:
   if not (folder/'index.html').is_file():continue
   # Require native audio runtime, not a web-based installer/editor only.
   js=list(folder.rglob('worklet.js'))
   wasm=list(folder.rglob('*.wasm'))
   if not js:continue
   if ident in ('choralroot','salt') and not wasm:continue
   valid=folder;break
  if valid:
   staging=out/'stage';shutil.copytree(valid,staging,dirs_exist_ok=True)
   # Restrict package contents to web assets; never include secrets or source control.
   allowed={'.html','.js','.mjs','.css','.wasm','.json','.svg','.png','.jpg','.jpeg','.webp','.woff','.woff2','.ttf','.wav','.bin'}
   for f in list(staging.rglob('*')):
    if f.is_file() and (f.suffix.lower() not in allowed or f.stat().st_size>25_000_000):f.unlink()
   pkg=out/(ident+'.fm1pkg')
   maker=pathlib.Path(__file__).resolve().with_name('create_package.py')
   if maker.is_file() and attempt('package',[sys.executable,str(maker),str(staging),'--id',ident,'--name',ident,'--version',result['revision'][:12],'--output',str(pkg)],out,60)==0:
    result['package']=pkg.name;result['status']='packaged_unverified'
   else:result['status']='package_failed'
  else:
   result['status']='browser_port_required' if not candidates else 'browser_assets_incomplete'
  result['candidate_directories']=[str(x.relative_to(source)) for x in candidates if x.exists()]
 finally:
  (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({k:result[k] for k in ('id','status','package')},indent=2))

if __name__=='__main__':main()
