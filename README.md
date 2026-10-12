# FM-1 Firmware Lab v1.6 — experimental Rainbow and WaveLoop browser packages

The compatibility probes compiled **Rainbow Mode** and **WaveLoop FM-1** from their original source repositories. This version adds their `upstream-felucca` build recipes to the shared GitHub Actions matrix. Their release notes explicitly identify them as **experimental / Safari unverified**. The existing Felucca and SLOOP recipes are unchanged.

## Deploy
Copy this project (including `.github`) into your existing `fm1-browser-builds` clone. Run:

```bash
python3 tools/recipe_matrix.py --validate
git add -A
git commit -m "Build experimental Rainbow and WaveLoop browser packages"
git push origin main
```

Run **Build all supported FM-1 browser engines** under GitHub Actions. It should attempt Felucca, SLOOP, Rainbow, and WaveLoop. Inspect the jobs; only successful builds will publish packages. Download the updated compatibility report.

## Safari test
Run `python3 server.py` and open `http://localhost:8000`. Select Rainbow Mode or WaveLoop FM-1, then Install and Play in Lab. Verify UI launches, controls respond, audio is produced, and there are no console errors. Installation does not establish behavioral parity with hardware firmware.

**Do not describe these two engines as Safari validated until you've tested them.** Releases are intentionally discoverable by the existing installer; release notes flag them experimental. No upstream changes are pushed back to authors' repositories.

## Known limits
The two builds were compilation-tested by GitHub Actions, not by Safari. `compiled_unverified` does not prove sound output or functional equivalence. The other four candidate variants remain disabled. The Lab uses a bundled fallback catalog; if the live catalog has different IDs for these entries, installation lookup may need mapping.


## v1.7 — All firmware source audit

GitHub Actions → **Audit all FM-1 firmware sources** → **Run workflow**.
The workflow checks all entries in the live firmware catalog, preserves the four existing recipes, and performs **read-only source inspection** of the remaining projects. Download `fm1-all-firmware-source-audit` (JSON and Markdown) from the run artifacts.

Classification: `browser_build_detected` means a known browser build layout exists (not compiled or tested); `family_adapter_review` means a family-specific port may be reusable (not confirmed); `new_browser_port_required` means no known family adapter; `source_unavailable` means the clone failed.

This workflow does not execute upstream build scripts, publish packages, or change existing playable engines. The source-audit step requires internet access and can fail if upstream repositories are unavailable.


## v1.8 — Seven browser-build compile probes

The v1.7 audit identified seven repositories with browser build entrypoints.
`browser-probe-targets.json` records the repository and audited revision for each.
The new GitHub Actions workflow **Probe seven browser-ready FM-1 sources**
checks out each upstream repo on a disposable runner, optionally executes its browser
build, checks `index.html`, `worklet.js`, and `felucca.wasm`, and uploads logs plus
a strict seven-result summary artifact `fm1-seven-browser-probe-report`.

The workflow **does not publish or install** any candidate. Compiling is not Safari validation.
The source revision is recorded, and drift since the audit is flagged.
To run: copy this project into your existing `fm1-browser-builds` repository, push,
then Actions → Probe seven browser-ready FM-1 sources → Run workflow (compile enabled).
Download the report artifact and upload `browser-probe-report.json` to this chat.

The existing four engine recipes and browser Lab remain unchanged.


## v1.9 — publish three + diagnose four

The existing **Build all supported FM-1 browser engines** workflow now includes experimental recipes for GHOULBOX, JIANT FM, and MAKU. They were compiled in the v1.8 probe but are **not Safari-verified**. The existing workflow builds, packages, checksums, and publishes immutable release assets.

Run **Diagnose four FM-1 browser asset builds** to inspect FiMba-1, FoMni, FuMi-1, and X0X. This workflow inventories actual build outputs, especially alternate WASM filenames and paths. It does not publish or silently rename files.

**Security:** GitHub Actions executes third-party build code on disposable hosted runners. Review source and workflow permissions before dispatch; avoid self-hosted runners and credentials.

**Deployment:** Copy this ZIP over your current repository (including `.github`), commit and push. Run the two workflows. Test each experimental published engine in Safari before declaring support.
