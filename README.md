# FM-1 Firmware Lab — hosted build foundation (v1.0-ci)

This retains the working v0.9.5 Tailwind UI, IndexedDB installs, firmware selector, and browser emulator. It adds a **real GitHub Actions Felucca WebAssembly build** and support for installing releases from a central GitHub repository. **No firmware binaries are bundled.** The workflow has not been executed here; builds and Safari playback require validation.

## One-time publisher setup (GitHub, not the Mac)

1. Create a public GitHub repository, for example `YOURNAME/fm1-browser-builds`.
2. Upload this project's files to that repository. In GitHub repository **Settings → Actions → General**, enable Actions and set workflow permissions to **Read and write permissions** (needed to create Releases).
3. Open **Actions → Build Felucca browser emulator → Run workflow**. The workflow clones `hugelton/Felucca`, generates assets, compiles its WebAssembly browser emulator using Emscripten, packages `felucca.fm1pkg` with SHA-256, and publishes both as a release. Scheduled checks run daily, and unchanged source revisions reuse their existing release.
4. On the computer running the Lab, configure the published build repository and start the server:

```bash
FM1_BROWSER_BUILD_REPO=YOURNAME/fm1-browser-builds python3 server.py
```

5. In Safari at `http://localhost:8000`, select **Felucca**, then **Find browser build**, then **Install browser engine**. The Lab checks the published release, validates its SHA-256, installs it into IndexedDB, and launches it in the existing Lab.

The environment variable is the only server configuration; **users do not need local source ZIPs, Python build dependencies, or Emscripten**. GitHub is still required to host the build workflow; this package cannot publish releases until you create and authorize the repository.

## What is and is not supported

- **Felucca:** Included CI build workflow; requires first successful GitHub Actions run.
- **SLOOP:** The existing v0.5 browser port is a modified source tree. It is **not** identical to the upstream hardware repository. A repeatable CI build must first publish the port source and track upstream changes. Existing installed SLOOP remains usable.
- **FM1-X0X and others:** Need their actual browser build procedures assessed and adapted. The catalog lists firmware, but listing does not imply browser emulation support.
- **Official M-VAVE firmware:** Hardware image; no compatible browser emulator presently provided.

Security: SHA-256 confirms downloaded bytes match the release checksum, **not publisher trust**. Use only repositories you control or trust. Browser packages contain executable JavaScript. The CI workflow uses pinned Emscripten version, but the upstream source is deliberately tracked and must be trusted.

## Development checks

```bash
python3 -m py_compile server.py tools/create_package.py
node --check js/repo-install.js
```

Use the same `http://localhost:8000` origin to preserve IndexedDB installs and saved projects. Do not clear site data.


## v1.1: Whole-catalog pipeline

- All entries in the Firmware Hub catalog are audited in a **single** scheduled GitHub Actions job (`catalog-audit.yml`). Download its `fm1-browser-compatibility` artifact to see which have published browser engines and which need ports.
- The existing Felucca build runs daily against the author's latest source and publishes a new immutable release when the source commit changes.
- The Lab's **Install** button now checks for a published browser engine and, when found, verifies and installs it in one click.
- `browser-build-matrix.json` records readiness of the bundled catalog; it is **not** a promise that all firmware compiles to WASM. Other engines, including SLOOP, still require tested CI build recipes.
- Install from the author's source through our release cache: `FM1_BROWSER_BUILD_REPO=mauricecalhoun/fm1-browser-builds python3 server.py`.

**Limitation:** GitHub Actions jobs and Safari runtime must still be tested for this revision. The catalog audit tracks all firmware; it does not build unported firmware.
