# FM-1 Firmware Lab v2.0 — Asset Recovery

Seven engines are now user-confirmed playable in Safari: Felucca, SLOOP, Rainbow, WaveLoop, GHOULBOX, JIANT FM, MAKU.

This release adds **Recover four FM-1 browser builds** workflow. It runs isolated upstream builds for FiMba-1, FoMni, FuMi-1 and X0X, captures compiler logs, inventories generated `.wasm` files (regardless of filename or directory), and finds `.wasm` references in HTML/JS. A combined `fm1-four-recovery-report` artifact includes `recovery-report.json`; four per-engine artifacts include the logs, revisions and detailed inventories.

The four projects previously exited with status 0, but lacked the expected `build/emu/felucca.wasm`. The workflow distinguishes a genuine missing WASM from a differently named output. **It does not automatically rename, package, or publish unknown binaries.** The runtime must be verified first.

## Install
Unzip into the existing `mauricecalhoun/fm1-browser-builds` checkout, preserving `.github`. Run:

```bash
python3 tools/recipe_matrix.py --validate
git add -A
git commit -m "Add v2.0 four-engine WASM recovery diagnostics"
git push origin main
```

Open GitHub Actions > **Recover four FM-1 browser builds** > **Run workflow**. Download `fm1-four-recovery-report` and upload `recovery-report.json` here, ideally with one of the detailed per-engine artifacts if a WASM is discovered under an unexpected name.

## Notes
- No change to the seven published build recipes or existing browser player.
- Existing diagnostic workflow remains available.
- Compile success and WASM discovery do not imply Safari compatibility.
