#!/usr/bin/env python3
"""Verify that the compiled browser assets retain their expected native WASM name."""
import argparse
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('directory',type=Path)
p.add_argument('--wasm',required=True)
a=p.parse_args()
for filename in ('index.html','worklet.js',a.wasm):
    f=a.directory/filename
    if not f.is_file() or not f.stat().st_size:p.error(f'Missing or empty browser asset: {f}')
references=[]
for filename in ('index.html','worklet.js'):
    if a.wasm in (a.directory/filename).read_text(errors='replace'):references.append(filename)
if not references:p.error(f'Neither HTML nor worklet references {a.wasm}; inspect loader before publishing')
if (a.directory/a.wasm).read_bytes()[:4]!=b'\x00asm':p.error(f'{a.wasm} is not a WebAssembly binary')
print(f'Verified native WASM {a.wasm} referenced by {", ".join(references)}')
