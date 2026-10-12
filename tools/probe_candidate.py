#!/usr/bin/env python3
"""Isolated CI compatibility probe. Never publishes candidate packages."""
import argparse, json, os, pathlib, subprocess, time, traceback

ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(cmd, cwd=None, timeout=180, log=None):
    try:
        p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout,env={k:v for k,v in os.environ.items() if k not in ('GH_TOKEN','GITHUB_TOKEN')})
        output=p.stdout[-30000:]
        if log: log.write_text(output)
        return p.returncode,output
    except subprocess.TimeoutExpired as e:
        output='TIMEOUT: '+str(e)
        if log: log.write_text(output)
        return 124,output

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True)
    p.add_argument('--probe',action='store_true',help='Execute upstream generator/build only if expected Felucca browser build layout exists')
    a=p.parse_args()
    data=json.loads((ROOT/'recipes.json').read_text())
    candidate=next((c for c in data['candidates'] if c['id']==a.id),None)
    if not candidate:
        p.error(f"Unknown candidate: {a.id}. Check recipes.json candidates")
    repo=candidate.get('upstream', '').replace('https://github.com/', '').strip('/')
    if not repo or '/' not in repo:
        p.error(f"Candidate {a.id} missing upstream repo in recipes.json")
    out=ROOT/'dist'/'candidate-probes'; out.mkdir(parents=True,exist_ok=True)
    source=out/('source-'+a.id)
    result={'id':a.id,'family':candidate['family'],'upstream':repo,'source_revision':None,'structural_checks':{},'probe_attempted':False,'build_exit_code':None,'browser_assets':{},'status':'source_unavailable','reason':None}
    log=out/(a.id+'.log')
    try:
        code,txt=run(['git','clone','--depth','1','--','https://github.com/'+repo+'.git',str(source)],timeout=120,log=log)
        if code:
            result['reason']='git clone failed'; return
        code,rev=run(['git','rev-parse','HEAD'],cwd=source,timeout=15)
        result['source_revision']=rev.strip() if code==0 else None
        checks={
            'generator':'tools/build.py',
            'web_build_script':'web/emu/build.sh',
            'web_source_dir':'web/emu',
            'firmware_source_dir':'firmware/src',
            'build_manifest':'web/emu/Makefile',
        }
        result['structural_checks']={k:(source/v).exists() for k,v in checks.items()}
        can_probe=result['structural_checks']['generator'] and result['structural_checks']['web_build_script']
        if not can_probe:
            result['status']='needs_adaptation'
            result['reason']='Missing upstream browser generator or web/emu/build.sh; no compile attempted'
        elif not a.probe:
            result['status']='probe_ready'
            result['reason']='Browser build entrypoints found; execution not enabled'
        else:
            result['probe_attempted']=True
            # Run upstream build in disposable GitHub runner with read-only token and no secrets.
            code,txt=run(['bash','-lc','python3 -c "from tools.build import generate; generate()" && sh web/emu/build.sh'],cwd=source,timeout=420,log=log)
            result['build_exit_code']=code
            assets={name:(source/'build'/'emu'/name).is_file() and (source/'build'/'emu'/name).stat().st_size>0 for name in ['index.html','worklet.js','felucca.wasm']}
            result['browser_assets']=assets
            if code==0 and all(assets.values()):
                result['status']='compiled_unverified'
                result['reason']='Browser assets compiled; runtime, behavior and Safari installation NOT validated'
            else:
                result['status']='build_failed'
                result['reason']='Compiler failed or expected browser assets absent; see log'
    except Exception as e:
        result['status']='probe_error'; result['reason']=str(e)
    finally:
        (out/(a.id+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))

if __name__=='__main__': main()
