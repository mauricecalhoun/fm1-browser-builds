#!/usr/bin/env python3
"""Generate a checksum-pinned registry from compiled .fm1pkg files for static hosting."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('packages',nargs='+',type=Path);p.add_argument('--base-url',required=True,help='HTTPS base URL hosting the packages');p.add_argument('--output',default='registry.json',type=Path);a=p.parse_args()
if not a.base_url.startswith('https://'):p.error('base-url must be HTTPS')
entries=[]
for path in a.packages:
    raw=path.read_bytes();pkg=json.loads(raw)
    if pkg.get('format')!='fm1-web-package-v1':p.error(f'Invalid package: {path}')
    entries.append({'id':pkg['id'],'name':pkg['name'],'version':pkg['version'],'url':a.base_url.rstrip('/')+'/'+path.name,'sha256':hashlib.sha256(raw).hexdigest()})
a.output.write_text(json.dumps({'schema':1,'packages':entries},indent=2)+'\n')
print(f'Wrote {a.output} with {len(entries)} package(s)')
