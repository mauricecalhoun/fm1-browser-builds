#!/usr/bin/env python3
"""Validate the recipe registry and emit GitHub Actions matrix JSON."""
import json,pathlib,sys
p=pathlib.Path(__file__).resolve().parent.parent/'recipes.json'
data=json.loads(p.read_text())
assert data['schema_version']==1
ids=set(); enabled=[]
allowed={'upstream-felucca','bundled-sloop-port'}
for item in data['recipes']:
    assert item['id'] not in ids and item['id'] and item['state'] in ('enabled','experimental')
    assert item['recipe'] in allowed, f"Unknown recipe: {item['recipe']}"
    assert '/' in item['upstream']
    ids.add(item['id'])
    enabled.append({'id':item['id'],'name':item['name'],'recipe':item['recipe'],'source':item['upstream'],'state':item['state'],'wasm':item.get('wasm','felucca.wasm')})
for item in data['candidates']:
    assert item['id'] not in ids and item['state']=='evaluation_needed'
    ids.add(item['id'])
if len(sys.argv)>1 and sys.argv[1]=='--validate':
    print(f'Validated {len(enabled)} enabled recipes and {len(data["candidates"])} candidates')
else:
    print(json.dumps({'include':enabled},separators=(',',':')))
