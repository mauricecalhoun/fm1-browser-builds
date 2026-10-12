#!/usr/bin/env python3
"""Idempotently add experimental install controls without replacing existing Lab files."""
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));a=p.parse_args()
root=a.root; index=root/'index.html'; src=index.read_text()
section='''<section id="v25-experiments" class="rounded-2xl border border-line bg-panel p-5"><h2 class="text-lg font-semibold text-white">Experimental browser engines · v2.5</h2><p class="mt-1 text-sm text-slate-400">Hortator and Jangada were packaged in CI but have not been Safari playback-verified. Install locally, then select the engine above and click Play in Lab.</p><div class="mt-3 flex flex-wrap gap-2"><button type="button" data-v25-install="hortator" class="rounded-lg border border-amber-400/40 bg-amber-400/10 px-4 py-2 text-sm text-amber-200">Install Hortator (experimental)</button><button type="button" data-v25-install="jangada" class="rounded-lg border border-amber-400/40 bg-amber-400/10 px-4 py-2 text-sm text-amber-200">Install Jangada (experimental)</button></div><p id="v25-status" role="status" class="mt-2 text-sm text-slate-300"></p></section>'''
if 'id="v25-experiments"' not in src:
 src=src.replace('</main>',section+'</main>',1)
if 'src="./js/v25-experiments.js"' not in src:
 src=src.replace('</body>','<script type="module" src="./js/v25-experiments.js"></script></body>',1)
index.write_text(src)
(root/'js').mkdir(exist_ok=True)
(root/'js'/'v25-experiments.js').write_text((Path(__file__).resolve().parents[1]/'js'/'v25-experiments.js').read_text())
(root/'experimental').mkdir(exist_ok=True)
for name in ('hortator','jangada'):
 (root/'experimental'/f'{name}.fm1pkg').write_bytes((Path(__file__).resolve().parents[1]/'experimental'/f'{name}.fm1pkg').read_bytes())
print('Installed v2.5 experimental browser package controls into',root)
