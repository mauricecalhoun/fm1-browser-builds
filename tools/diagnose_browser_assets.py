#!/usr/bin/env python3
"""Inventory browser build output without assuming the WASM filename."""
import argparse, hashlib, json, pathlib
p=argparse.ArgumentParser();p.add_argument('root',type=pathlib.Path);p.add_argument('--id',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
root=a.root.resolve(); entries=[]
for f in sorted(root.rglob('*')):
 if not f.is_file() or f.is_symlink():continue
 rel=f.relative_to(root).as_posix()
 if len(entries)>=3000:break
 item={'path':rel,'bytes':f.stat().st_size}
 if f.suffix.lower() in ('.wasm','.js','.html'):
  item['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 entries.append(item)
wasm=[x for x in entries if x['path'].lower().endswith('.wasm')]
result={'id':a.id,'files':entries,'wasm_candidates':wasm,'expected_felucca_wasm':any(x['path']=='build/emu/felucca.wasm' for x in entries),'note':'A renamed WASM is not necessarily compatible with the existing worklet. Inspect JS references and test in Safari.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'id':a.id,'files':len(entries),'wasm_candidates':wasm},indent=2))
