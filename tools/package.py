#!/usr/bin/env python3
"""Populate a deploy-only FM-1 site from independently compiled WASM emulators."""
import argparse, json, shutil
from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--sloop-build',type=Path,help='Directory containing SLOOP felucca.wasm, index.html, worklet.js, fonts/')
p.add_argument('--felucca-build',type=Path,help='Directory containing Felucca felucca.wasm, index.html, worklet.js, fonts/')
a=p.parse_args()
entries=[]
for key,name,source in [('sloop','SLOOP',a.sloop_build),('felucca','Felucca',a.felucca_build)]:
    dst=root/'firmware'/key
    dst.mkdir(parents=True,exist_ok=True)
    if source:
        source=source.expanduser().resolve()
        for filename in ('index.html','worklet.js','felucca.wasm'):
            if not (source/filename).is_file(): p.error(f'{source}/{filename} is missing')
            shutil.copy2(source/filename,dst/filename)
        if (source/'fonts').is_dir():shutil.copytree(source/'fonts',dst/'fonts',dirs_exist_ok=True)
    ready=all((dst/n).is_file() for n in ('index.html','worklet.js','felucca.wasm'))
    entries.append(dict(id=key,name=name,description='Original firmware running in the existing FM-1 panel',entry=f'firmware/{key}/index.html',ready=ready))
(root/'firmware.json').write_text(json.dumps(dict(firmwares=entries),indent=2)+'\n')
print('Firmware status:',', '.join(f"{x['name']}={'ready' if x['ready'] else 'needs WASM'}" for x in entries))
