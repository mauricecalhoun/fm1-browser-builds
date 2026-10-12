#!/usr/bin/env python3
"""Inspect all eleven unported FM-1 engines; never claim a browser port from file presence."""
import hashlib, json, pathlib, subprocess, sys, tempfile

CANDIDATES = [
 ('salt','ChanceTheMaker/Felucca','felucca'),
 ('floyd','renebohne/sloop-fm1','sloop'),
 ('sloopbanks','majnikool/sloop-fm1','sloop'),
 ('sloopdx','zvenson/dxsloop','sloop'),
 ('zp12','zvenson/zp12','independent'),
 ('hortator','deadactive/hortator','independent'),
 ('jangada','zednaked/jangada','independent'),
 ('melodee','keremimo/melodee','independent'),
 ('choralroot','Quixotic7/ChoralRootFM1','independent'),
 ('dinghy','zvenson/dinghy','independent'),
 ('chord','math0ne/fm1-chord','independent'),
]
EXTS = {'.c','.cc','.cpp','.h','.hpp','.js','.mjs','.html','.sh','.py','.wasm'}

def run(*args, cwd=None):
    return subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180)

def audit(candidate, root):
    ident, repo, family = candidate
    entry = {'id':ident,'upstream':repo,'family':family,'status':'inspection_pending','safari_verified':False,'published':False}
    dest = root / ident
    try:
        result = run('git','clone','--depth','1','--filter=blob:none',f'https://github.com/{repo}.git',str(dest))
        if result.returncode:
            entry.update(status='clone_failed',error=result.stderr[-1500:]);return entry
        entry['sha']=run('git','rev-parse','HEAD',cwd=dest).stdout.strip()
        files=[p for p in dest.rglob('*') if p.is_file() and '.git' not in p.parts]
        entry['source_files']=sum(p.suffix in {'.c','.cc','.cpp'} for p in files)
        entry['wasm_assets']=[{'path':str(p.relative_to(dest)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.suffix=='.wasm'][:40]
        entry['browser_files']=[str(p.relative_to(dest)) for p in files if p.suffix in {'.js','.mjs','.html'} and ('web' in p.parts or 'emu' in p.parts)][:80]
        entry['build_scripts']=[str(p.relative_to(dest)) for p in files if p.name in {'build.sh','CMakeLists.txt','Makefile','build.py','package.json'}][:40]
        entry['audio_worklets']=[str(p.relative_to(dest)) for p in files if 'worklet' in p.name.lower()][:30]
        entry['candidate_entrypoints']=[str(p.relative_to(dest)) for p in files if p.name in {'index.html','browser.js','worklet.js'}][:40]
        entry['status']='browser_assets_present_review_required' if entry['wasm_assets'] and entry['candidate_entrypoints'] else 'browser_port_required'
        entry['notes']='Inventory only. Browser assets do not prove a full Safari firmware emulator; no compilation or publishing performed.'
    except Exception as e:
        entry.update(status='inspection_error',error=str(e))
    return entry

def main():
    output=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'remaining-11-report.json')
    with tempfile.TemporaryDirectory(prefix='fm1-v23-') as td:
        entries=[audit(c,pathlib.Path(td)) for c in CANDIDATES]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'schema_version':1,'goal':'22 Safari-verified engines','existing_verified':11,'remaining':entries},indent=2)+'\n')
    print(json.dumps({'total':len(entries),'statuses':{x['id']:x['status'] for x in entries}},indent=2))
    return 1 if any(x['status'] in {'clone_failed','inspection_error'} for x in entries) else 0

if __name__=='__main__':sys.exit(main())
