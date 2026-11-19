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
import random
import sys
from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riverside import art, scenery, buildings, layout, sprites, previews, upside_down
from riverside.art import P, SEASONS, LIGHT_STYLES, BLINK_GROUPS, season_palette, christmas_palette, render
from riverside.config import load, ConfigError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = "abcde"

# Layers that have a different image in each season. MainScene.brs builds
# the same list from the number of town sections.
SEASONAL = {"far": ["winter"], "far_b": ["winter"], "near": ["winter"], "near_b": ["winter"], "hills": SEASONS, "hills_b": SEASONS,
            "hills_c": SEASONS}

# Each layer is cropped to the band it uses: name -> (y, height). These must
# match the strips in components/MainScene.xml.
CROPS = {"clouds": (90, 255), "far": (295, 425), "far_b": (295, 425), "near": (400, 360), "near_b": (400, 360),
         "hills": (420, 490), "hills_b": (420, 490), "hills_c": (420, 490), "town": (550, 530)}

def pet_size(images, pet):
    """The size of an animal on screen. Animal images are saved at the size
    they are shown (see PET_SCALE in sprites.py), so this is the image size."""
    with Image.open(os.path.join(images, pet["image"] + ".png")) as im:
        return im.size

def light_styles(town, i):
    """The style of Christmas lights for each building in town section i. With
    christmas_lights "mixed", each building with lights gets a style picked at
    random, but never the same style as the building with lights before it.
    The random numbers start from the section number, so a building has the
    same style in every image."""
    style = town["extras"]["christmas_lights"]
    if style != "mixed":
        return [style] * len(town["sections"][i])
    rnd, prev, out = random.Random(i), None, []
    for b, x in town["sections"][i]:
        if b["type"] in buildings.LIT:
            prev = rnd.choice([s for s in LIGHT_STYLES if s != prev])
        out.append(prev)
    return out

BLINK_SHARE = 0.25   # The share of the buildings with lights whose lights blink

def blinking(town):
    """The buildings whose Christmas lights blink, as a set of (section,
    index in section). A quarter of the buildings with lights (at least one)
    blink; the lights on the others stay on. They are spread along the
    street: the buildings with lights are split into equal runs, and one
    building in each run is picked at random. The random numbers always start
    from the same value, so the same buildings blink in every image."""
    lit = [(i, j) for i, section in enumerate(town["sections"]) for j, (b, x) in enumerate(section)
           if b["type"] in buildings.LIT]
    if not lit:
        return set()
    n = max(1, round(len(lit) * BLINK_SHARE))
    rnd = random.Random(7)
    return {lit[int(len(lit) * (k + rnd.random()) / n)] for k in range(n)}

def town_section(town, i, p, season):
    section = town["sections"][i]
    if not p.get("christmas"):
        return "".join(buildings.draw(b, x, p, season) for b, x in section) + street_layer(town, i, p, season)
    styles, blinks = light_styles(town, i), blinking(town)
    out = ""
    for j, ((b, x), style) in enumerate(zip(section, styles)):
        bp = dict(p, light_style=style)
        if (i, j) not in blinks:
            # The lights on this building do not blink, so every bulb is on
            bp["lit"] = (0, 1, 2)
        out += buildings.draw(b, x, bp, season)
    return out + street_layer(town, i, p, season)

def street_layer(town, i, p, season):
    section = town["sections"][i]
    return (scenery.street(p, season, 11 + i)
            + buildings.sidewalk_shadows(section, p) + buildings.sidewalk_bikes(section, p, season, town["extras"]))

def christmas_seasons(town):
    """The seasons that need a Christmas image of each town section: the
    seasons December can fall in, and winter, because the ground shows snow
    while it is snowing. components/scene/christmas.brs reads this list as
    christmasSeasons in
    town_config.json."""
    if not town["extras"]["christmas"]:
        return []
    if not town["extras"]["seasons"]:
        return ["summer", "winter"]
    # December 1 to 20 is fall and December 21 to 31 is winter. In the southern
    # hemisphere they are spring and summer.
    return ["fall", "winter"] if town["hemisphere"] == "north" else ["spring", "summer", "winter"]

def write_lamps(town, out):
    """The street lamp images, one for each time of day, and one with snow on
    the lantern for each time of day. With extras.christmas on, each also has
    a December image with a wreath on the post. components/scene/sidewalk.brs
    adds them to
    townStrip at the x values in lamps in town_config.json."""
    left, top, w, h = buildings.LAMP_BOX
    kinds = [("", lambda p: p)]
    if town["extras"]["christmas"]:
        kinds.append(("_christmas", christmas_palette))
    for pal in P:
        for name, palette in kinds:
            for season, suffix in (("summer", ""), ("winter", "_winter")):
                render(buildings.street_lamp(0, palette(P[pal]), season), f"{left} {top} {w} {h}", w, h,
                       os.path.join(out, f"street_lamp{name}{suffix}_{pal}.png"))

def write_blink(town, out):
    """The images that make the Christmas lights blink. For each building with
    lights, there is one image for each blink group (1 and 2) that shows only
    the lit bulbs of that group, cropped to the building. They are made by
    drawing the town section with that group lit and keeping the pixels that
    differ from the town image, so they line up with it exactly. There is an
    image for each Christmas season, at dusk and at night:
    blink_<n>_<group>_<season>_<period>.png. Returns [x, y, w, h] for each
    building n, in townStrip coordinates, for christmasBlink in
    town_config.json."""
    seasons = christmas_seasons(town)
    if not seasons:
        return []
    y0, h = CROPS["town"]
    vb = f"0 {y0} 1920 {h}"
    entries = []
    for i, section in enumerate(town["sections"]):
        fn = layers(town)[f"town_{LETTERS[i]}"]
        blinks = blinking(town)
        lit = [(b, x) for j, (b, x) in enumerate(section) if (i, j) in blinks]
        if not lit:
            continue
        # Each building's images may use the space up to halfway to the next
        # building with lights, so no image holds bulbs from a neighbor.
        edges = [0] + [(x0 + buildings.width(b0) + x1) / 2 for (b0, x0), (b1, x1) in zip(lit, lit[1:])] + [1920]
        diffs = {}
        for season in seasons:
            for pal in ("dusk", "night"):
                p = season_palette(pal, season)
                base = Image.open(io.BytesIO(render(fn(christmas_palette(p, lit=(0,)), season), vb, 1920, h))).convert("RGBA")
                for k in range(1, BLINK_GROUPS):
                    on = Image.open(io.BytesIO(render(fn(christmas_palette(p, lit=(0, k)), season), vb, 1920, h))).convert("RGBA")
                    r, g, bl, a = ImageChops.difference(on, base).split()
                    mask = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(bl, a)).point(lambda v: 255 if v else 0)
                    diffs[(season, pal, k)] = Image.composite(on, Image.new("RGBA", on.size), mask), mask
        for j in range(len(lit)):
            left, right = int(edges[j]), int(edges[j + 1])
            box = None
            for _, mask in diffs.values():
                b = mask.crop((left, 0, right, h)).getbbox()
                if b:
                    b = (b[0] + left, b[1], b[2] + left, b[3])
                    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
            if box is None:
                continue
            n = len(entries)
            for (season, pal, k), (im, _) in diffs.items():
                im.crop(box).save(os.path.join(out, f"blink_{n}_{k}_{season}_{pal}.png"), optimize=True)
            entries.append([i * 1920 + box[0], box[1], box[2] - box[0], box[3] - box[1]])
    return entries

# Layers that get an Upside Down image. The town sections are added from the
# number of sections. Every layer is drawn as on a fall day, then graded.
UPSIDE_LAYERS = ["far", "far_b", "near", "near_b", "hills", "hills_b", "hills_c"]

def upside_image(town, name):
    """One layer of the Upside Down, as a PIL image of its crop."""
    y, h = CROPS[name.split("_")[0] if name.startswith("town") else name]
    vb = f"0 {y} 1920 {h}"
    p = season_palette("day", "fall")
    base = Image.open(io.BytesIO(render(layers(town)[name](p, "fall"), vb, 1920, h))).convert("RGBA")
    if name.startswith("town"):
        i = LETTERS.index(name[-1])
        return upside_down.town_layer(base, town["sections"][i], 31 + i, y)
    if name.startswith("hills"):
        return upside_down.hills_layer(base, {"hills": 51, "hills_b": 52, "hills_c": 53}[name], y)
    return upside_down.grade(base)

def write_upside(town, out):
    """The Upside Down images for October (extras.upside_down). See
    tools/riverside/upside_down.py."""
    names = UPSIDE_LAYERS + [f"town_{LETTERS[i]}" for i in range(len(town["sections"]))]
    for name in names:
        upside_image(town, name).save(os.path.join(out, f"{name}_upside.png"), optimize=True)
    render(upside_down.sky(), "0 0 8 1080", 8, 1080, os.path.join(out, "sky_upside.png"))
    y, h = CROPS["clouds"]
    render(upside_down.clouds(), f"0 {y} 1920 {h}", 1920, h, os.path.join(out, "clouds_upside.png"))
    bw, bh = upside_down.BOLT_SIZE
    for n in range(upside_down.BOLTS):
        render(upside_down.bolt(n + 1), f"0 0 {bw} {bh}", bw, bh, os.path.join(out, f"bolt_{n}.png"))
    sw, sh = upside_down.SPORES_SIZE
    render(upside_down.spores(5, 70, 1.0, 2.2), f"0 0 {sw} {sh}", sw, sh, os.path.join(out, "spores_a.png"))
    render(upside_down.spores(9, 26, 2.4, 4.5), f"0 0 {sw} {sh}", sw, sh, os.path.join(out, "spores_b.png"))
    if town["extras"]["street_lights"]:
        left, top, w, h = buildings.LAMP_BOX
        vb = f"{left} {top} {w} {h}"
        back, front = upside_down.lamp_vines(0)
        lamp = Image.open(io.BytesIO(render(buildings.street_lamp(0, P["day"], "summer"), vb, w, h))).convert("RGBA")
        lamp = upside_down.grade(lamp)
        # The back of the vine is behind the post, and the front is in front of it
        out_im = Image.open(io.BytesIO(render(back, vb, w, h))).convert("RGBA")
        out_im.alpha_composite(lamp)
        out_im.alpha_composite(Image.open(io.BytesIO(render(front, vb, w, h))).convert("RGBA"))
        lamp = out_im
        lamp.save(os.path.join(out, "street_lamp_upside.png"), optimize=True)

def layers(town):
    """Returns name -> drawing function(p, season) for every scenery layer."""
    ex = town["extras"]
    out = {f"clouds_{level}": (lambda p, s, level=level: scenery.clouds(p, s, level)) for level in scenery.CLOUD_LEVELS}
    out.update({"far": lambda p, s: scenery.far(p, s, ex["table_mountain"]), "far_b": scenery.far_b,
           "near": scenery.near, "near_b": scenery.near_b,
           "hills": lambda p, s: scenery.hills(p, s, ex["kayaks"], ex["bikes"], town["radio_station"]),
           "hills_b": lambda p, s: scenery.hills(p, s, ex["kayaks"], ex["bikes"], tile="b"),
           "hills_c": lambda p, s: scenery.hills(p, s, ex["kayaks"], ex["bikes"], tile="c")})
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
        render(scenery.sky(P[pal], overcast=True), "0 0 8 1080", 8, 1080, os.path.join(out, f"sky_overcast_{pal}.png"))
        for name, fn in layers(town).items():
            # The town sections share one crop, and so do the cloud levels
            y, h = CROPS[name.split("_")[0] if name.startswith(("town", "clouds")) else name]
            seasons = SEASONS if name.startswith("town") else SEASONAL.get(name, [])
            vb = f"0 {y} 1920 {h}"
            for season in seasons:
                render(fn(season_palette(pal, season), season), vb, 1920, h, os.path.join(out, f"{name}_{season}_{pal}.png"))
            if len(seasons) < len(SEASONS):
                render(fn(P[pal], "summer"), vb, 1920, h, os.path.join(out, f"{name}_{pal}.png"))
            if name.startswith("town"):
                # The December images, with the Christmas decorations. Only
                # the bulbs in group 0 are lit; the others blink (see
                # write_blink).
                for season in christmas_seasons(town):
                    render(fn(christmas_palette(season_palette(pal, season), lit=(0,)), season), vb, 1920, h,
                           os.path.join(out, f"{name}_christmas_{season}_{pal}.png"))
    town["blink"] = write_blink(town, out)
    sprites.write(out)
    if town["extras"]["street_lights"]:
        write_lamps(town, out)
    if town["extras"]["upside_down"]:
        write_upside(town, out)

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
        night = os.path.exists(os.path.join(images, pet["image"] + "_night.png"))
        pets.append({"image": pet["image"], "w": w, "h": h, "night": night})
    return {
        "title": town["title"], "lat": str(town["lat"]), "lon": str(town["lon"]),
        "temperatureUnit": "celsius" if town["temperature"] == "C" else "fahrenheit",
        "clock24": town["clock"] == "24h", "hemisphere": town["hemisphere"],
        "driveOn": town["drive_on"],
        "sections": len(town["sections"]), "cars": town["cars"], "specialCars": town["special_cars"], "pets": pets,
        "parkedCarX": town["parked_car_x"], "radioLight": radio_light(town), "lamps": town["lamps"],
        "airplane": ex["airplane"], "fireflies": ex["fireflies"], "fallingLeaves": ex["falling_leaves"],
        "seasons": ex["seasons"], "christmasSeasons": christmas_seasons(town),
        "christmasBlink": town.get("blink", []), "upsideDown": ex["upside_down"],
    }

def radio_light(town):
    """Where components/scene/scenery.brs puts the blinking light on the radio tower: [x, y]
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
