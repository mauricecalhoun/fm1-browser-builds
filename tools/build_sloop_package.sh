#!/usr/bin/env bash
# Create an installable SLOOP browser emulator package from a built emulator folder or source ZIP.
set -euo pipefail
if (( $# < 1 || $# > 2 )); then
  echo 'Usage: bash tools/build_sloop_package.sh /path/to/build/emu [output.fm1pkg]' >&2
  echo '   or: bash tools/build_sloop_package.sh /path/to/sloop-browser-port-v0.5-source.zip [output.fm1pkg]' >&2
  exit 2
fi
INPUT="$1"
LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${2:-$PWD/sloop.fm1pkg}"
[[ -e "$INPUT" ]] || { echo "Not found: $INPUT" >&2; exit 1; }
TEMP=''
cleanup(){ [[ -z "$TEMP" ]] || rm -rf "$TEMP"; }
trap cleanup EXIT
if [[ -d "$INPUT" ]]; then
  BUILD="$(cd "$INPUT" && pwd)"
else
  command -v unzip >/dev/null || { echo 'Missing unzip' >&2; exit 1; }
  command -v emcc >/dev/null || { echo 'Missing emcc: activate Emscripten first' >&2; exit 1; }
  TEMP="$(mktemp -d)"
  unzip -q "$INPUT" -d "$TEMP"
  SOURCE="$(find "$TEMP" -type f -path '*/web/emu/build.sh' -print -quit)"
  [[ -n "$SOURCE" ]] || { echo 'ZIP does not contain web/emu/build.sh' >&2; exit 1; }
  SOURCE="${SOURCE%/web/emu/build.sh}"
  if [[ ! -f "$SOURCE/build/gen/felucca_tables.h" ]]; then
    echo 'Generating SLOOP browser assets…'
    (cd "$SOURCE" && python3 -c 'from tools.build import generate; generate()')
  fi
  (cd "$SOURCE" && sh web/emu/build.sh)
  BUILD="$SOURCE/build/emu"
fi
for name in index.html worklet.js felucca.wasm; do
  [[ -s "$BUILD/$name" ]] || { echo "Missing required emulator file: $BUILD/$name" >&2; exit 1; }
done
python3 "$LAB_DIR/tools/create_package.py" "$BUILD" --id sloop --name SLOOP --version '0.5-browser-port' --output "$OUT"
echo "Ready: $OUT"
echo 'Import the package in Manage installed firmware, then select SLOOP and Launch in Lab.'
