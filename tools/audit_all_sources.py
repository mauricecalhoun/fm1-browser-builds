#!/usr/bin/env python3
"""Read-only architecture inventory for all unported FM-1 catalog entries.

No upstream code is executed. A structural match is not a working browser port.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'https://fm1.designburgapps.com/catalog.json'
FAMILIES = {'felucca': 'upstream-felucca', 'sloop': 'bundled-sloop-port'}
MARKERS = {
    'felucca_browser_generator': 'tools/build.py',
    'felucca_browser_build': 'web/emu/build.sh',
    'felucca_web_source': 'web/emu',
    'firmware_source': 'firmware/src',
    'platformio': 'platformio.ini',
    'cmake': 'CMakeLists.txt',
    'makefile': 'Makefile',
    'arduino': 'arduino',
}

def catalog():
    override = os.environ.get('FM1_CATALOG_FILE')
    if override:
        return json.loads(Path(override).read_text())['firmwares']
    request = urllib.request.Request(CATALOG, headers={'User-Agent':'FM1-Firmware-Lab-Audit/1.7'})
    with urllib.request.urlopen(request, timeout=35) as response:
        return json.load(response)['firmwares']

def inspect(item, candidates, output):
    fid = item['id']
    upstream = (item.get('repo') or '').removeprefix('https://github.com/').strip('/')
    family = candidates.get(fid, {}).get('family')
    result = {'id':fid,'name':item.get('name',fid),'upstream':upstream,
              'family_hint':family,'source_revision':None,'source_available':False,
              'markers':{},'file_counts':{},'possible_adapter':FAMILIES.get(family),
              'status':'source_unavailable','next_action':'Review upstream source and licensing',
              'error':None}
    source = output / 'sources' / fid
    if not upstream or upstream.count('/') != 1:
        result['error']='Missing or invalid GitHub repository';return result
    try:
        process=subprocess.run(['git','clone','--depth','1','--filter=blob:none','--',
                                'https://github.com/'+upstream+'.git',str(source)],
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=100)
        if process.returncode:
            result['error']=process.stderr[-1200:];return result
        result['source_available']=True
        rev=subprocess.run(['git','-C',str(source),'rev-parse','HEAD'],capture_output=True,text=True,check=True)
        result['source_revision']=rev.stdout.strip()
        result['markers']={key:(source/path).exists() for key,path in MARKERS.items()}
        counts={ext:0 for ext in ('.c','.cpp','.h','.hpp','.py','.js','.ts','.ino')}
        # Exclude .git and generated dependencies; bounded metadata-only traversal.
        for i,p in enumerate(source.rglob('*')):
            if i>25000:break
            if '.git' in p.parts or 'node_modules' in p.parts or not p.is_file():continue
            if p.suffix.lower() in counts:counts[p.suffix.lower()]+=1
        result['file_counts']=counts
        m=result['markers']
        if m['felucca_browser_generator'] and m['felucca_browser_build']:
            result['status']='browser_build_detected'
            result['next_action']='Run isolated compile probe, then validate Safari audio and UI'
        elif family:
            result['status']='family_adapter_review'
            result['next_action']='Diff hardware APIs and audio/display behavior against existing '+family+' browser port'
        else:
            result['status']='new_browser_port_required'
            result['next_action']='Map audio, input, display and storage hardware dependencies; design new browser adapter'
    except (subprocess.SubprocessError,OSError) as exc:
        result['error']=str(exc)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='dist/all-firmware-audit.json')
    p.add_argument('--keep-sources',action='store_true')
    args=p.parse_args()
    registry=json.loads((ROOT/'recipes.json').read_text())
    recipes={r['id']:r for r in registry['recipes']}
    candidates={r['id']:r for r in registry['candidates']}
    entries=catalog()
    output=ROOT/'dist'/'source-audit';output.mkdir(parents=True,exist_ok=True)
    results=[]
    for entry in entries:
        fid=entry['id']
        if fid in recipes:
            results.append({'id':fid,'name':entry.get('name',fid),'upstream':entry.get('repo'),
                            'status':'existing_recipe','recipe':recipes[fid]['recipe'],
                            'source_available':None,'next_action':'Retain current working browser recipe'})
        else:
            result=inspect(entry,candidates,output)
            results.append(result)
            print(fid, result['status'],flush=True)
    if not args.keep_sources:
        import shutil
        shutil.rmtree(output/'sources',ignore_errors=True)
    summary={}
    for result in results:summary[result['status']]=summary.get(result['status'],0)+1
    report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'catalog_count':len(entries),'existing_recipes':len(recipes),
            'summary':summary,'firmwares':results,
            'note':'Read-only structural inspection. No browser compatibility or Safari playback inferred.'}
    path=ROOT/args.output;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n')
    md=['# FM-1 firmware source audit','',f'Catalog: {len(entries)} | Existing recipes: {len(recipes)}','',
        '| Firmware | Status | Possible adapter | Next action |','|---|---|---|---|']
    for r in results:
        md.append('| '+ ' | '.join(str(r.get(k) or '—').replace('|','/') for k in ('name','status','possible_adapter','next_action'))+' |')
    path.with_suffix('.md').write_text('\n'.join(md)+'\n')
    print('Summary:',json.dumps(summary,sort_keys=True))
    if len(entries)!=22:print('WARNING: live catalog has',len(entries),'entries (previously 22)')

if __name__=='__main__':main()
