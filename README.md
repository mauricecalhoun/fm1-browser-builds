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
