#!/usr/bin/env bash
set -euo pipefail
: "${ENGINE_ID:?}" "${ENGINE_NAME:?}" "${RECIPE:?}"
mkdir -p dist upstream
case "$RECIPE" in
  upstream-felucca)
    git clone --depth 1 "https://github.com/${UPSTREAM_REPO}.git" upstream/engine
    REV="$(git -C upstream/engine rev-parse --short=12 HEAD)"
    (cd upstream/engine && python3 -c 'from tools.build import generate; generate()' && sh web/emu/build.sh)
    BUILD="upstream/engine/build/emu"
    ;;
  bundled-sloop-port)
    ZIP="ports/sloop-browser-port-v0.5-source.zip"
    test -s "$ZIP" || { echo "Missing SLOOP browser port: $ZIP" >&2; exit 1; }
    REV="$(sha256sum "$ZIP" | cut -c1-12)"
    unzip -q "$ZIP" -d upstream
    ROOT="$(find upstream -type f -path '*/web/emu/build.sh' -print -quit)"
    test -n "$ROOT" || { echo 'SLOOP browser port missing build script' >&2; exit 1; }
    ROOT="${ROOT%/web/emu/build.sh}"
    (cd "$ROOT" && python3 -c 'from tools.build import generate; generate()' && sh web/emu/build.sh)
    BUILD="$ROOT/build/emu"
    ;;
  *) echo "Unsupported browser recipe: $RECIPE" >&2; exit 2;;
esac
for file in index.html worklet.js felucca.wasm; do
  test -s "$BUILD/$file" || { echo "Missing browser asset: $BUILD/$file" >&2; exit 1; }
done
python3 tools/create_package.py "$BUILD" --id "$ENGINE_ID" --name "$ENGINE_NAME" --version "$REV" --output "dist/${ENGINE_ID}.fm1pkg"
(cd dist && sha256sum "${ENGINE_ID}.fm1pkg" > "${ENGINE_ID}.fm1pkg.sha256")
echo "rev=$REV" >> "$GITHUB_OUTPUT"
