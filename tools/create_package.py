#!/usr/bin/env python3
"""Package a compiled browser firmware directory for the FM-1 Firmware Lab installer."""
import argparse,base64,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--id',required=True);p.add_argument('--name',required=True);p.add_argument('--version',default='1.0');p.add_argument('--entry',default='index.html');p.add_argument('--output',type=Path);a=p.parse_args()
root=a.directory.resolve();files=[]
for f in sorted(root.rglob('*')):
    if f.is_file() and not f.is_symlink():
        path=f.relative_to(root).as_posix()
        if path.startswith('.') or '/.' in path:continue
        files.append({'path':path,'base64':base64.b64encode(f.read_bytes()).decode('ascii')})
if not (root/a.entry).is_file():p.error('entry file missing')
out=a.output or Path(a.id+'.fm1pkg');out.write_text(json.dumps({'format':'fm1-web-package-v1','id':a.id,'name':a.name,'version':a.version,'entry':a.entry,'files':files},separators=(',',':')))
print(f'Created {out}: {len(files)} files, {out.stat().st_size:,} bytes')
