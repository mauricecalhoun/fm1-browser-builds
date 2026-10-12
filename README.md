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
