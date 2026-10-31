#!/usr/bin/env python3
"""Builds the images for Riverside Town from a town.json file.

Usage, from the repository root:
    python3 tools/generate_images.py [--config town.json] [--package DIR] [--docs DIR] [--build DIR]

It writes:
- DIR/images/: every image the screensaver uses
- DIR/components/town_config.json: the settings MainScene.brs reads
- the title in DIR/manifest
- preview images in --build (default build/), and the README previews in
  --docs if it is given

DIR is the folder that holds manifest, source, components, and images. It is
the repository root unless --package is given.
"""
import argparse
import io
import json
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riverside import art, scenery, buildings, layout, sprites, previews
from riverside.art import P, SEASONS, season_palette, render
from riverside.config import load, ConfigError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = "abcde"

# Layers that have a different image in each season. MainScene.brs builds
# the same list from the number of town sections.
SEASONAL = {"far": ["winter"], "far_b": ["winter"], "near": ["winter"], "near_b": ["winter"], "hills": SEASONS, "hills_b": SEASONS}

# Each layer is cropped to the band it uses: name -> (y, height). These must
# match the strips in components/MainScene.xml.
CROPS = {"clouds": (90, 255), "far": (295, 425), "far_b": (295, 425), "near": (400, 360), "near_b": (400, 360),
         "hills": (420, 490), "hills_b": (420, 490), "town": (550, 530)}

def pet_size(images, pet):
    """The size of an animal on screen. Animal images are saved at the size
    they are shown (see PET_SCALE in sprites.py), so this is the image size."""
    with Image.open(os.path.join(images, pet["image"] + ".png")) as im:
        return im.size

def town_section(town, i, p, season):
    section = town["sections"][i]
    return ("".join(buildings.draw(b, x, p, season) for b, x in section) + scenery.street(p, season, 11 + i)
            + buildings.sidewalk_bikes(section, p, season, town["extras"])
            + (buildings.street_lamps(p, season) if town["extras"]["street_lights"] else ""))

def layers(town):
    """Returns name -> drawing function(p, season) for every scenery layer."""
    ex = town["extras"]
    out = {"clouds": scenery.clouds,
           "far": lambda p, s: scenery.far(p, s, ex["table_mountain"]), "far_b": scenery.far_b,
           "near": scenery.near, "near_b": scenery.near_b,
           "hills": lambda p, s: scenery.hills(p, s, ex["kayaks"], ex["bikes"], town["radio_station"]),
           "hills_b": lambda p, s: scenery.hills(p, s, ex["kayaks"], ex["bikes"], tile="b")}
    for i in range(len(town["sections"])):
        out[f"town_{LETTERS[i]}"] = lambda p, s, i=i: town_section(town, i, p, s)
    return out

def write_images(town, out):
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))
    for pal in P:
        render(scenery.sky(P[pal]), "0 0 8 1080", 8, 1080, os.path.join(out, f"sky_{pal}.png"))
        for name, fn in layers(town).items():
            y, h = CROPS["town" if name.startswith("town") else name]
            seasons = SEASONS if name.startswith("town") else SEASONAL.get(name, [])
            vb = f"0 {y} 1920 {h}"
            for season in seasons:
                render(fn(season_palette(pal, season), season), vb, 1920, h, os.path.join(out, f"{name}_{season}_{pal}.png"))
            if len(seasons) < len(SEASONS):
                render(fn(P[pal], "summer"), vb, 1920, h, os.path.join(out, f"{name}_{pal}.png"))
    sprites.write(out)

def write_icons(town, out, build_dir):
    im = previews.composite(town, layers(town), "day", 0, "summer")
    crop = im.convert("RGB").crop((240, 0, 1680, 1080))
    crop.resize((290, 218), Image.LANCZOS).save(os.path.join(out, "icon_hd.png"))
    crop.resize((540, 405), Image.LANCZOS).save(os.path.join(out, "icon_fhd.png"))

def runtime_config(town, images):
    """The settings MainScene.brs reads from components/town_config.json."""
    ex = town["extras"]
    pets = []
    for pet in town["pets"]:
        w, h = pet_size(images, pet)
        pets.append({"image": pet["image"], "w": w, "h": h})
    return {
        "title": town["title"], "lat": str(town["lat"]), "lon": str(town["lon"]),
        "temperatureUnit": "celsius" if town["temperature"] == "C" else "fahrenheit",
        "clock24": town["clock"] == "24h", "hemisphere": town["hemisphere"],
        "sections": len(town["sections"]), "cars": town["cars"], "pets": pets,
        "parkedCarX": town["parked_car_x"], "radioLight": radio_light(town),
        "airplane": ex["airplane"], "fireflies": ex["fireflies"], "fallingLeaves": ex["falling_leaves"],
        "seasons": ex["seasons"],
    }

def radio_light(town):
    """Where MainScene.brs puts the blinking light on the radio tower: [x, y]
    in hills strip coordinates (the strip starts at screen y=CROPS["hills"]),
    or [] if there is no tower."""
    light = scenery.radio_light(town["radio_station"])
    return [light[0], light[1] - CROPS["hills"][0]] if light else []

def write_manifest(path, title):
    with open(path) as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("title=") or line.startswith("screensaver_title="):
            lines[i] = line.split("=")[0] + "=" + title
    with open(path, "w") as f:
        f.write("\n".join(lines))

def build(config, package, build_dir, docs=None):
    """Builds everything for the town in config into the package folder.
    Returns the town settings. Raises ConfigError for a mistake in town.json."""
    town = load(config)
    layout.layout(town)
    images = os.path.join(package, "images")
    write_images(town, images)
    write_icons(town, images, build_dir)
    with open(os.path.join(package, "components", "town_config.json"), "w") as f:
        json.dump(runtime_config(town, images), f, indent=2)
        f.write("\n")
    write_manifest(os.path.join(package, "manifest"), town["title"])
    previews.write_all(town, layers(town), images, build_dir, docs)
    n = len(town["sections"])
    print(f"Built {town['title']}: {sum(len(s) for s in town['sections'])} buildings and trees in {n} town section{'s' if n > 1 else ''}.")
    return town

def main():
    ap = argparse.ArgumentParser(description="Build the Riverside Town images from town.json.")
    ap.add_argument("--config", default=os.path.join(ROOT, "town.json"), help="the town.json file (default: town.json in the repository root)")
    ap.add_argument("--package", default=ROOT, help="the folder with manifest, source, and components (default: the repository root)")
    ap.add_argument("--build", default=os.path.join(ROOT, "build"), help="where to write preview images for checking (default: build/)")
    ap.add_argument("--docs", help="where to write the README preview images (for example: docs)")
    args = ap.parse_args()
    try:
        build(args.config, args.package, args.build, args.docs)
    except ConfigError as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
