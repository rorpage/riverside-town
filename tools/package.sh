#!/usr/bin/env bash
# Builds riverside-town.zip, the file to upload to a Roku in developer mode.
#
# Run from anywhere:
#     ./tools/package.sh
#
# The zip is written to the repository root. It holds only the files the Roku
# needs (manifest, source, components, images), with the manifest at the top
# level of the zip. Any older zip with the same name is replaced.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZIP="$ROOT/riverside-town.zip"

if ! command -v zip > /dev/null; then
    echo "Error: the zip command is not installed." >&2
    exit 1
fi

cd "$ROOT"
for item in manifest source components images; do
    if [ ! -e "$item" ]; then
        echo "Error: $item is missing from $ROOT." >&2
        exit 1
    fi
done

rm -f "$ZIP"
zip -r -q "$ZIP" manifest source components images -x "*.DS_Store"

echo "Wrote $ZIP ($(du -h "$ZIP" | cut -f1))"
