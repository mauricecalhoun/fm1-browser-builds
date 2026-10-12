#!/usr/bin/env python3
"""Inspect an upstream browser build and discover WASM output without assuming its name.
Read-only: does not rename or publish assets.
"""
import argparse, hashlib, json, pathlib, re
p=argparse.ArgumentParser();p.add_argument('root',type=pathlib.Path);p.add_argument('--id',required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--build-exit-code',type=int,default=0);a=p.parse_args()
root=a.root.resolve();build=root/'build'/'emu'; entries=[]; refs=[]
for f in sorted(root.rglob('*')):
 if not f.is_file() or f.is_symlink() or '.git' in f.parts:continue
 rel=f.relative_to(root).as_posix()
 if len(entries)>=8000:break
 if f.stat().st_size>50_000_000:continue
 if f.suffix.lower() in ('.wasm','.js','.html') or ('build' in f.parts and len(entries)<8000):
  item={'path':rel,'bytes':f.stat().st_size}
  if f.suffix.lower()=='.wasm':item['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
  entries.append(item)
 if f.suffix.lower() in ('.js','.html') and f.stat().st_size<2_000_000:
  try: content=f.read_text(encoding='utf-8')
  except UnicodeError:continue
  for match in re.finditer(r'[\w./-]+\.wasm',content):
   refs.append({'source':rel,'wasm_reference':match.group(0)})
wasm=[x for x in entries if x['path'].lower().endswith('.wasm')]
required={name:(build/name).is_file() and (build/name).stat().st_size>0 for name in ('index.html','worklet.js','felucca.wasm')}
if a.build_exit_code!=0: status='compile_failed'
elif all(required.values()): status='compiled_unverified'
elif not wasm: status='wasm_not_found'
else: status='alternate_wasm_detected'
result={'id':a.id,'build_exit_code':a.build_exit_code,'status':status,'required_assets':required,'wasm_candidates':wasm,'wasm_references':refs[:100],'files':entries,'note':'Alternative WASM is not proven compatible. Never rename/publish automatically; inspect worklet loading and runtime.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'id':a.id,'status':status,'wasm_candidates':wasm,'wasm_references':refs[:20]},indent=2))
