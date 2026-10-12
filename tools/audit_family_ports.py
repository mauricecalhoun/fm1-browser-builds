#!/usr/bin/env python3
"""Non-invasive source compatibility audit for four FM-1 family candidates."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

CANDIDATES = [
    ('salt','ChanceTheMaker/Felucca','hugelton/Felucca','felucca'),
    ('floyd','renebohne/sloop-fm1','isod89/sloop-fm1','sloop'),
    ('sloopbanks','majnikool/sloop-fm1','isod89/sloop-fm1','sloop'),
    ('sloopdx','zvenson/dxsloop','isod89/sloop-fm1','sloop'),
]
MARKERS = ('CMakeLists.txt','Makefile','web/emu/build.sh','web/emu/index.html','web/emu/worklet.js','src','firmware','README.md')

def run(*args, cwd=None, timeout=100):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)

def audit(item, root):
    ident, upstream, base, family = item
    out = {'id':ident,'upstream':upstream,'base':base,'family':family,'status':'needs_manual_port_review'}
    target = root / ident
    r = run('git','clone','--depth','1',f'https://github.com/{upstream}.git',str(target), timeout=120)
    if r.returncode:
        out.update(status='clone_failed', error=r.stderr[-1200:]); return out
    head = run('git','rev-parse','HEAD',cwd=target)
    out['sha'] = head.stdout.strip()
    out['markers'] = {m:(target/m).exists() for m in MARKERS}
    wasm = sorted(str(p.relative_to(target)) for p in target.rglob('*.wasm') if '.git' not in p.parts)
    out['checked_in_wasm'] = wasm[:30]
    # Fetch the base into a separate shallow checkout to avoid making assumptions
    # about whether the candidate is a GitHub fork or shares Git history.
    baseline = root / (ident+'-baseline')
    br = run('git','clone','--depth','1',f'https://github.com/{base}.git',str(baseline),timeout=120)
    if br.returncode:
        out['baseline_error'] = br.stderr[-800:]
    else:
        def source_files(p):
            return {str(x.relative_to(p)):x.stat().st_size for x in p.rglob('*') if x.is_file() and '.git' not in x.parts}
        a,b = source_files(target),source_files(baseline)
        out['files_added_vs_base'] = sorted(set(a)-set(b))[:150]
        out['files_missing_vs_base'] = sorted(set(b)-set(a))[:150]
        out['shared_paths'] = len(set(a)&set(b))
        out['files_with_size_changes'] = sorted(k for k in set(a)&set(b) if a[k]!=b[k])[:150]
    out['notes'] = 'File inventory only. Similarity does not prove runtime/API compatibility; no package published.'
    return out

def main():
    output = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'family-port-audit.json')
    with tempfile.TemporaryDirectory(prefix='fm1-family-') as td:
        results = [audit(c,pathlib.Path(td)) for c in CANDIDATES]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'schema_version':1,'candidates':results},indent=2)+'\n')
    print(json.dumps({'output':str(output),'statuses':{r['id']:r['status'] for r in results}},indent=2))
    return 0 if all(r['status']!='clone_failed' for r in results) else 1

if __name__=='__main__':
    sys.exit(main())
