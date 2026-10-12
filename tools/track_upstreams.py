#!/usr/bin/env python3
"""Report source HEADs, published revisions, and recipe eligibility. No speculative builds."""
import datetime,json,os,pathlib,urllib.request,urllib.error,urllib.parse
repo=os.getenv('BUILD_REPO','mauricecalhoun/fm1-browser-builds')
headers={'User-Agent':'FM1-Lab-Upstream-Tracker','Accept':'application/vnd.github+json'}
if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=25) as r:return json.load(r)
items=get('https://fm1.designburgapps.com/catalog.json')['firmwares']
releases=get('https://api.github.com/repos/'+repo+'/releases?per_page=100')
results=[]
for item in items:
    fid=item['id'];upstream=item.get('repo');record={'id':fid,'upstream':upstream,'head':None,'published_revision':None,'recipe':None,'status':'port_needed'}
    if fid=='felucca':record['recipe']='upstream-felucca'
    elif fid=='sloop':record['recipe']='bundled-sloop-port'
    for rel in releases:
        names={a.get('name') for a in rel.get('assets',[])}
        if not rel.get('draft') and not rel.get('prerelease') and {fid+'.fm1pkg',fid+'.fm1pkg.sha256'}<=names:
            record['published_revision']=rel.get('tag_name','').split('-web-')[-1]
            record['release_url']=rel.get('html_url');break
    if upstream and '/' in upstream:
        try:
            metadata=get('https://api.github.com/repos/'+upstream)
            branch=metadata.get('default_branch','main')
            commit=get('https://api.github.com/repos/'+upstream+'/commits/'+urllib.parse.quote(branch,safe=''))
            record['head']=commit['sha'][:12]
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,KeyError,ValueError) as exc:record['source_error']=str(exc)
    if record['recipe']=='upstream-felucca':
        record['status']='up_to_date' if record['head'] and record['head']==record['published_revision'] else 'rebuild_needed' if record['head'] else 'source_unavailable'
    elif record['recipe']=='bundled-sloop-port':record['status']='published_snapshot' if record['published_revision'] else 'build_needed'
    results.append(record)
path=pathlib.Path('dist/upstream-tracking.json');path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps({'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'build_repo':repo,'firmwares':results},indent=2)+'\n')
print('Tracked',len(results),'firmware; Felucca:',next(x['status'] for x in results if x['id']=='felucca'))
