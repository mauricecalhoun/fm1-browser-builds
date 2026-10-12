#!/usr/bin/env python3
"""Compile probe for previously audited browser-build-capable sources; no publication."""
import argparse, json, os, pathlib, subprocess, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(argv,cwd=None,timeout=120):
    try:
        p=subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout,env={k:v for k,v in os.environ.items() if k not in ('GITHUB_TOKEN','GH_TOKEN')})
        return p.returncode,p.stdout[-60000:]
    except subprocess.TimeoutExpired as e:
        return 124,'TIMEOUT: '+str(e)
    except OSError as e:
        return 125,'EXEC ERROR: '+str(e)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--id',required=True); ap.add_argument('--compile',action='store_true'); a=ap.parse_args()
    targets=json.loads((ROOT/'browser-probe-targets.json').read_text())['targets']
    target=next((x for x in targets if x['id']==a.id),None)
    if target is None: ap.error('Unknown target '+a.id)
    out=ROOT/'dist'/'browser-probes'; out.mkdir(parents=True,exist_ok=True)
    result={'id':a.id,'upstream':target['upstream'],'audited_revision':target['audited_revision'],'source_revision':None,'revision_changed':None,'entrypoints':{},'compile_attempted':False,'build_exit_code':None,'browser_assets':{},'status':'probe_error','reason':None}
    logs=[]; source=out/('source-'+a.id)
    try:
        code,output=run(['git','clone','--depth','1','--','https://github.com/'+target['upstream']+'.git',str(source)],timeout=120)
        logs.append('CLONE\n'+output)
        if code:
            result.update(status='source_unavailable',reason='Git clone failed')
        else:
            code,revision=run(['git','rev-parse','HEAD'],cwd=source,timeout=15)
            result['source_revision']=revision.strip() if code==0 else None
            result['revision_changed']=result['source_revision']!=target['audited_revision']
            checks={'generator':'tools/build.py','web_build_script':'web/emu/build.sh','web_source_dir':'web/emu'}
            result['entrypoints']={key:(source/value).exists() for key,value in checks.items()}
            if not (result['entrypoints']['generator'] and result['entrypoints']['web_build_script']):
                result.update(status='needs_adaptation',reason='Required browser generator or build script missing')
            elif not a.compile:
                result.update(status='probe_ready',reason='Build entrypoints found; compile disabled')
            else:
                result['compile_attempted']=True
                # Execute upstream build only on an isolated CI runner, never on a developer machine.
                code,output=run(['bash','-lc','python3 -c "from tools.build import generate; generate()" && sh web/emu/build.sh'],cwd=source,timeout=600)
                logs.append('BUILD\n'+output);result['build_exit_code']=code
                assets={name:(source/'build'/'emu'/name).is_file() and (source/'build'/'emu'/name).stat().st_size>0 for name in ('index.html','worklet.js','felucca.wasm')}
                result['browser_assets']=assets
                if code==0 and all(assets.values()):
                    result.update(status='compiled_unverified',reason='Required browser assets compiled; no runtime or Safari validation')
                else:
                    result.update(status='build_failed',reason='Build failed or required assets absent; inspect log')
    except Exception as exc:
        result.update(status='probe_error',reason=str(exc))
    finally:
        (out/(a.id+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        (out/(a.id+'.log')).write_text('\n'.join(logs)+'\n')
        shutil.rmtree(source,ignore_errors=True)
        print(json.dumps(result,indent=2))

if __name__=='__main__': main()
