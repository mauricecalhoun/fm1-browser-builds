#!/usr/bin/env bash
# Build Felucca's own browser emulator on macOS and package it for FM-1 Firmware Lab.
set -euo pipefail
ZIP="${1:-$HOME/Downloads/Felucca-main.zip}"
OUT="${2:-$PWD/felucca.fm1pkg}"
LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
for cmd in unzip python3 emcc; do command -v "$cmd" >/dev/null || { echo "Missing $cmd" >&2; exit 1; }; done
[ -f "$ZIP" ] || { echo "Missing source ZIP: $ZIP" >&2; exit 1; }
mkdir -p "$LAB_DIR/.build"
TEMP="$(mktemp -d "$LAB_DIR/.build/felucca.XXXXXX")"
trap 'rm -rf "$TEMP"' EXIT
unzip -q "$ZIP" -d "$TEMP"
SOURCE="$TEMP/Felucca-main"
[ -f "$SOURCE/web/emu/build.sh" ] || { echo 'Not a supported Felucca source ZIP' >&2; exit 1; }
# Only generate assets required by the browser emulator; avoid the JieLi hardware build.
(cd "$SOURCE" && python3 -c 'from tools.build import generate; generate()' && sh web/emu/build.sh)
VERSION="$(sed -n 's/^#define FELUCCA_VERSION "\([^"]*\)".*/\1/p' "$SOURCE/firmware/src/felucca.c" | head -1)"
python3 "$LAB_DIR/tools/create_package.py" "$SOURCE/build/emu" --id felucca --name Felucca --version "${VERSION:-unknown}" --output "$OUT"
echo "Import $OUT into the Lab in Safari."
