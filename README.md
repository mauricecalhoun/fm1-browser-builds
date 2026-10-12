# FM-1 Firmware Lab v1.3 — Upstream tracking and automatic install/update states

Builds for Felucca and SLOOP remain as in v1.2. The existing daily matrix workflow continues to build supported engines; immutable release tags avoid republishing unchanged revisions.

## New

- `track-upstreams.yml` audits all live catalog entries daily or on demand. It records upstream default-branch HEAD and published browser revision, with an artifact `fm1-upstream-tracking`.
- **Important:** only Felucca currently builds from upstream source; its revision can be compared to upstream HEAD. SLOOP builds from a bundled browser-port snapshot; changes to the SLOOP hardware repo do not imply that the port was updated.
- Safari install button automatically checks for releases when selection changes and shows Install / Update / Installed · current / Browser port needed. Package integrity verification remains required.
- Version label and source/release metadata updated.

## Deploy

Copy all files (including hidden `.github/`) into your existing `fm1-browser-builds` clone, commit and push. In Actions, run **Track all FM-1 upstream repositories**. Run `python3 server.py` and open `http://localhost:8000` in Safari. Preserve the origin/port to retain IndexedDB installs.

## Limitations

No new firmware engines are ported in v1.3. The tracker is a status report, not an automatic compatibility converter. GitHub rate limits can affect auditing 22 repositories. Safari runtime regression tests are not yet automated. Build jobs are not triggered directly by the tracking workflow; the existing daily build schedule handles upstream Felucca changes.
