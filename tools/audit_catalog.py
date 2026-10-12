#!/usr/bin/env python3
"""Audit every firmware in the live Hub against published browser release assets.
This does NOT claim hardware firmware can run in a browser.
"""
import json,os,urllib.request,pathlib,datetime
hub='https://fm1.designburgapps.com/catalog.json'
repo=os.getenv('BUILD_REPO','mauricecalhoun/fm1-browser-builds')
headers={'User-Agent':'FM1-Browser-Build-Audit','Accept':'application/vnd.github+json'}
if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:return json.load(r)
items=get(hub)['firmwares']
releases=get('https://api.github.com/repos/'+repo+'/releases?per_page=100')
registry=json.loads(pathlib.Path('recipes.json').read_text())
supported={x['id']:x['recipe'] for x in registry['recipes'] if x['state']=='enabled'}
candidates={x['id']:x['family'] for x in registry['candidates']}
report=[]
for f in items:
    fid=f['id'];found=None
    for r in releases:
        if r.get('draft') or r.get('prerelease'):continue
        names={a['name'] for a in r.get('assets',[])}
        if fid+'.fm1pkg' in names and fid+'.fm1pkg.sha256' in names:
            found={'tag':r['tag_name'],'url':r['html_url']};break
    report.append({'id':fid,'name':f.get('name',fid),'upstream':f.get('repo'), 'status':'published' if found else ('build_not_published' if fid in supported else 'browser_port_needed'), 'recipe':supported.get(fid), 'candidate_family':candidates.get(fid), 'browser_release':found})
path=pathlib.Path('dist/compatibility.json');path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps({'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'build_repo':repo,'firmwares':report},indent=2)+'\n')
print('Catalog entries:',len(report),'Published browser builds:',sum(x['status']=='published' for x in report))
for x in report:print(x['id'],x['status'])
