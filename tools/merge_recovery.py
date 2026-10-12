#!/usr/bin/env python3
import argparse,json,pathlib,collections
p=argparse.ArgumentParser();p.add_argument('directory',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
ids=('fimba','fomni','fumi','x0x');results=[]
for id in ids:
 f=a.directory/(id+'.json')
 if not f.exists(): results.append({'id':id,'status':'missing_artifact'})
 else:
  try: results.append(json.loads(f.read_text()))
  except (OSError,ValueError) as e: results.append({'id':id,'status':'invalid_artifact','reason':str(e)})
report={'evaluated':len(results),'summary':dict(collections.Counter(x['status'] for x in results)),'candidates':results,'note':'No experimental package published. Alternative WASM outputs need worklet/runtime compatibility verification.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary'],indent=2))
if any(x['status'] in ('missing_artifact','invalid_artifact') for x in results):raise SystemExit(1)
