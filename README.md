# FM-1 Firmware Lab v2.1 — Four native-WASM engines and combobox improvements

Adds four experimental build recipes to the existing seven engines, preserving their native WASM names:

- FiMba-1: `kalimba.wasm`
- FoMni: `omni.wasm`
- FuMi-1: `fumi.wasm`
- X0X: `x0x.wasm`

The normal **Build all supported FM-1 browser engines** GitHub Action now compiles and packages these engines. Its build script checks that each native WASM file exists, starts with the WASM magic bytes, and is referenced by its browser HTML/worklet. Existing seven recipes default to `felucca.wasm`. The installer and release discovery logic remain unchanged. New packages still require Safari testing; no claim of runtime compatibility is made.

The firmware combobox opens the **full list on click or focus**, supports typing to filter, and uses a centered SVG chevron instead of a font glyph.

## Install

Extract into your existing `mauricecalhoun/fm1-browser-builds` checkout (do not replace the repository `.git` folder). Then:

```sh
python3 tools/recipe_matrix.py --validate
git add -A
git commit -m "Add four native-WASM browser engines and fix combobox"
git push origin main
```

From GitHub Actions, run **Build all supported FM-1 browser engines**. After the four new experimental releases are published, open the Lab, select each firmware, click **Install**, then **Play in Lab**. Safari playback and controls must be verified before marking any new engine as confirmed playable.

## Notes

- Existing seven engines and package schema are preserved.
- Upstream firmware source is cloned and built in GitHub Actions; no precompiled WASM is included in this ZIP.
- A successful GitHub build is not a guarantee that audio starts in Safari.
