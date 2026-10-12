#!/usr/bin/env python3
"""Require exactly one result for every expected browser-ready target."""
import json,pathlib,sys,collections
root=pathlib.Path(__file__).resolve().parents[1]
expected={x['id'] for x in json.loads((root/'browser-probe-targets.json').read_text())['targets']}
files=sorted(pathlib.Path(sys.argv[1]).rglob('*.json'))
results=[json.loads(p.read_text()) for p in files]
ids=[r.get('id') for r in results]
missing=expected-set(ids); unexpected=set(ids)-expected
if missing or unexpected or len(ids)!=len(set(ids)):
    raise SystemExit(f'Invalid probe results: missing={sorted(missing)}, unexpected={sorted(unexpected)}, duplicate IDs={sorted(k for k,v in collections.Counter(ids).items() if v>1)}')
summary=dict(collections.Counter(r['status'] for r in results))
report={'evaluated':len(results),'summary':summary,'candidates':sorted(results,key=lambda x:x['id']),'note':'compiled_unverified is not installable or Safari-validated; no packages are published.'}
out=pathlib.Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'evaluated':len(results),'summary':summary},indent=2))
