#!/usr/bin/env python3
"""Builds a complete Riverside Town screensaver from a town.json file.

This is the command the Docker image runs. It copies the screensaver code
(manifest, source, and components) to a temporary folder, generates the
images for the town into it, and writes:
- OUT/riverside-town.zip: the screensaver, ready to install on a Roku
- OUT/previews/: preview images of the town

Usage:
    python3 tools/build_town.py [--config town.json] [--out out]
"""
import argparse
import os
import shutil
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_images
from riverside.config import ConfigError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = ["manifest", "source", "components"]

def main():
    ap = argparse.ArgumentParser(description="Build a Riverside Town screensaver zip from town.json.")
    ap.add_argument("--config", default="town.json", help="the town.json file (default: town.json)")
    ap.add_argument("--out", default="out", help="the folder for the zip and the previews (default: out)")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        pkg = os.path.join(tmp, "package")
        os.makedirs(pkg)
        for name in PACKAGE:
            src = os.path.join(ROOT, name)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(pkg, name))
            else:
                shutil.copy(src, os.path.join(pkg, name))
        previews = os.path.join(args.out, "previews")
        try:
            generate_images.build(args.config, pkg, previews)
        except ConfigError as e:
            print("Error:", e, file=sys.stderr)
            sys.exit(1)
        # The composites are for checking the art while working on the
        # generator. Only the screen previews are kept.
        for f in os.listdir(previews):
            if f.startswith("composite_"):
                os.remove(os.path.join(previews, f))
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, "riverside-town.zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name in PACKAGE + ["images"]:
                top = os.path.join(pkg, name)
                if os.path.isfile(top):
                    z.write(top, name)
                    continue
                for folder, _, files in os.walk(top):
                    for f in sorted(files):
                        if f == ".DS_Store":
                            continue
                        full = os.path.join(folder, f)
                        z.write(full, os.path.relpath(full, pkg))
    print("Wrote", path, "and the previews in", previews)

if __name__ == "__main__":
    main()
