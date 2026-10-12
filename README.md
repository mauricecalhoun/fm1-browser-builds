# FM-1 Firmware Lab v1.4 — Declarative browser build recipes

This release replaces the hard-coded GitHub Actions build matrix with `recipes.json`.

## What is actually supported
- Felucca: **enabled**, built from the original upstream source.
- SLOOP: **enabled**, built from the bundled v0.5 browser-port snapshot (not auto-synced to upstream).
- Salt, WaveLoop, Rainbow: **candidate Felucca family**, not yet validated or installable.
- Floyd FM, SLOOP DX7 Banks, SLOOP DX: **candidate SLOOP family**, not yet validated or installable.
- Other catalog entries: tracked/audited, no browser recipe yet.

**No new browser ports are claimed in v1.4.** Family similarity is a hypothesis requiring actual source review, adaptation, and Safari validation. This release is the reusable recipe infrastructure, not an automatic firmware-to-WASM converter.

## Deploy
Copy the entire extracted project, including `.github`, into your existing `fm1-browser-builds` clone, commit and push. Do not remove existing GitHub releases.

```bash
python3 tools/recipe_matrix.py --validate
python3 tools/recipe_matrix.py
```

Run **Build all supported FM-1 browser engines** under GitHub Actions. It reads the matrix dynamically from `recipes.json`, builds both enabled engines, and produces `fm1-browser-compatibility`. Run **Track all FM-1 upstream repositories** to see candidate family metadata in the tracking report.

To enable a new recipe, first implement a compatible build handler in `tools/ci_build_engine.sh`, validate its browser output, then add an enabled recipe to `recipes.json`. Candidate entries are intentionally excluded from the build matrix.

Run the local UI with `python3 server.py`, open `http://localhost:8000` in Safari. Existing IndexedDB installations are preserved when origin and port stay the same.
