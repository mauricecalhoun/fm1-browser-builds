#!/usr/bin/env python3
import json, pathlib, sys
src=pathlib.Path(sys.argv[1]); dest=pathlib.Path(sys.argv[2]); dest.parent.mkdir(parents=True,exist_ok=True)
results=[]
for p in sorted(src.rglob('*.json')):
    try: results.append(json.loads(p.read_text()))
    except (ValueError,OSError): pass
expected={c['id'] for c in json.loads((pathlib.Path(__file__).resolve().parents[1]/'recipes.json').read_text())['candidates']}
found={r.get('id') for r in results}
missing=sorted(expected-found)
if missing:
    raise SystemExit(f'Missing probe results for {len(missing)} candidate(s): {", ".join(missing)}; check probe logs and artifact uploads')
summary={}
for r in results: summary[r['status']]=summary.get(r['status'],0)+1
report={'evaluated':len(results),'summary':summary,'candidates':results,'note':'compiled_unverified is NOT installable or Safari-validated; no candidate packages are published.'}
dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
