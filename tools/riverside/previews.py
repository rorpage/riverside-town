"""Preview images: full screen pictures of the town, made from the same
drawings as the screensaver, with the cars, animals, and clock panel placed
like MainScene.brs places them.

composite() draws one town section with the scenery behind it. The files in
the build folder are for checking the art. preview() draws a screen with the
clock panel and cars, for the README.
"""
import io
import os
import random
from PIL import Image
from . import scenery, buildings
from .art import ACCENT, season_palette, svg, render, text, text_width
import cairosvg

LETTERS = "abcde"

# Car sizes and wheel positions. These copy m.carDefs in components/MainScene.brs.
CARS = {"sedan": (280, 104, [(62, 80), (218, 80)], 22, 102), "van": (310, 130, [(66, 104), (246, 104)], 24, 128),
        "jeep": (270, 140, [(68, 108), (214, 108)], 28, 136), "truck": (300, 130, [(70, 104), (238, 104)], 24, 128),
        "sports": (304, 104, [(64, 84), (234, 84)], 18, 102), "buggy": (250, 112, [(52, 84), (198, 84)], 26, 110),
        "aston": (300, 106, [(86, 84), (244, 84)], 19, 103), "herbie": (270, 106, [(62, 86), (217, 86)], 19, 105),
        "kitt": (300, 92, [(67, 69), (228, 69)], 18, 87), "ecto1": (360, 150, [(82, 124), (293, 124)], 18, 142),
        "delorean": (310, 112, [(76, 85), (245, 85)], 18, 103), "mcqueen": (300, 106, [(75, 71), (245, 71)], 28, 99),
        "mustang": (310, 96, [(71, 77), (243, 77)], 18, 95)}
# Special cars have their own wheel image, like wheelUri() in MainScene.brs
SPECIAL = {"aston", "herbie", "kitt", "ecto1", "delorean", "mcqueen", "mustang"}
PARK_SCALE = 0.78  # Copies parkCar() in MainScene.brs

def car_sprite(images, name, left):
    w, h, wheels, r, bottom = CARS[name]
    car = Image.new("RGBA", (w, h))
    car.alpha_composite(Image.open(os.path.join(images, f"car_{name}{'_left' if left else ''}.png")).convert("RGBA"))
    wheel = Image.open(os.path.join(images, f"wheel_{name}.png" if name in SPECIAL else "wheel.png")).convert("RGBA").resize((r * 2, r * 2), Image.LANCZOS)
    for wx, wy in wheels:
        car.alpha_composite(wheel, ((w - wx if left else wx) - r, wy - r))
    return car, bottom

def paste_car(im, images, name, x, ground, scale, left=False):
    car, bottom = car_sprite(images, name, left)
    car = car.resize((round(car.width * scale), round(car.height * scale)), Image.LANCZOS)
    im.alpha_composite(car, (round(x), round(ground - bottom * scale)))

def parked(town, images, im, section, name):
    """Adds the parked car if the gas station is in this section."""
    x = town["parked_car_x"]
    if x >= 0 and x // 1920 == section:
        w = CARS[name][0]
        paste_car(im, images, name, x % 1920 - w * PARK_SCALE / 2, 898, PARK_SCALE)

def lamps(town, section, p, season):
    """The street lamps in one town section, drawn last, in front of the
    animals and the parked car, like MainScene.brs adds them."""
    xs = [x - section * 1920 for x in town["lamps"] if x // 1920 == section]
    return buildings.street_lamps(xs, p, "winter" if season == "winter" else "summer")

def lamps_image(town, section, p, season):
    return Image.open(io.BytesIO(render(lamps(town, section, p, season), "0 0 1920 1080", 1920, 1080))).convert("RGBA")

def mountains(town, p, season):
    mtn = season if season == "winter" else "summer"
    return (scenery.clouds(p, season) + scenery.far(p, mtn, town["extras"]["table_mountain"]) + scenery.near(p, mtn)
            + scenery.hills(p, season, town["extras"]["kayaks"], town["extras"]["bikes"], town["radio_station"]))

def composite(town, layers, pal, section, season, images=None, car=None):
    """One town section with the scenery behind it. car is the name of a car to
    park at the gas station, or None; images is the folder with the car images."""
    p = season_palette(pal, season)
    full = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/><stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#g)"/><circle cx="220" cy="180" r="64" fill="{ACCENT}"/>'
            + mountains(town, p, season) + layers[f"town_{LETTERS[section]}"](p, season))
    im = Image.open(io.BytesIO(render(full, "0 0 1920 1080", 1920, 1080))).convert("RGBA")
    if car:
        parked(town, images, im, section, car)
    im.alpha_composite(lamps_image(town, section, p, season))
    return im

def panel(clock, temp, cond, px):
    """The clock and weather panel, drawn like the info group in MainScene.xml.
    px is its left edge, one of the x values in m.infoSpots."""
    big = text_width(clock, "hanken", 700, 54)
    tw = text_width(temp, "hanken", 700, 54)
    cw = text_width(cond, "hanken", 400, 30)
    return (f'<rect x="{px}" y="60" width="580" height="150" fill="#34495E" fill-opacity="0.5"/>'
            + text(clock, "hanken", 700, 54, px + 28 + big / 2, 134, "#F8FAFC")
            + text(temp, "hanken", 700, 54, px + 552 - tw / 2, 134, "#F8FAFC")
            + text(cond, "hanken", 400, 30, px + 28 + cw / 2, 184, "#ECEFF3"))

def clock_text(town, h, m):
    if town["clock"] == "24h":
        return f"{h}:{m:02d}"
    return f"{(h - 1) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"

def temp_text(town, f):
    if town["temperature"] == "C":
        return f"{round((f - 32) * 5 / 9)}\u00b0C"
    return f"{f}\u00b0F"

def preview(town, layers, images, pal, season, hour, temp, cond, section, fx=None, plane=None, pets=(), near_car="sports",
            clouds="few"):
    """One screen of the town, showing town section number section. plane is
    the (x, y) of an airplane, or None. pets is a list of (animal, x), where
    animal is an entry of town["pets"]. clouds is a cloud level from
    scenery.CLOUD_LEVELS; with "overcast", the sky is gray, the stars are
    hidden, and the sun or moon is dim, like applyScene() in MainScene.brs."""
    overcast = clouds == "overcast"
    p = season_palette(pal, season)
    sky_im = Image.new("RGBA", (1920, 1080))
    stars = Image.open(os.path.join(images, "stars.png")).convert("RGBA")
    if pal != "day" and not overcast:
        if pal == "dusk":
            stars.putalpha(stars.getchannel("A").point(lambda v: v * 0.35))
        sky_im.alpha_composite(stars, (0, 0))
    # The sun or moon, placed like applyScene() in MainScene.brs
    body, pos = ("moon.png", (150, 100)) if pal == "night" else ("sun.png", (150, 110) if pal == "day" else (180, 340))
    body_im = Image.open(os.path.join(images, body)).convert("RGBA")
    if overcast:
        body_im.putalpha(body_im.getchannel("A").point(lambda v: v * 0.35))
    sky_im.alpha_composite(body_im, pos)
    im = Image.open(os.path.join(images, f"sky_{'overcast_' if overcast else ''}{pal}.png")).convert("RGBA").resize((1920, 1080))
    im.alpha_composite(sky_im)
    # The far and near mountains change tiles part way along the street, so
    # the previews show the B tiles for odd sections, like the real strip
    mtn = season if season == "winter" else "summer"
    far = scenery.far(p, mtn, town["extras"]["table_mountain"]) if section % 2 == 0 else scenery.far_b(p, mtn)
    near = scenery.near(p, mtn) if section % 2 == 0 else scenery.near_b(p, mtn)
    # The hills change tiles too, A, B, then C; only the first has the radio station
    tile = "abc"[section % 3]
    hills = scenery.hills(p, season, town["extras"]["kayaks"], town["extras"]["bikes"], town["radio_station"], tile)
    light = scenery.radio_light(town["radio_station"]) if tile == "a" and pal != "day" else None
    if light:
        hills += f'<circle cx="{light[0]}" cy="{light[1]}" r="7" fill="#E74C3C" fill-opacity="0.35"/><circle cx="{light[0]}" cy="{light[1]}" r="3" fill="#FF6B5B"/>'
    art_svg = (scenery.clouds(p, season, clouds) + far + near + hills
               + layers[f"town_{LETTERS[section]}"](p, season))
    im.alpha_composite(Image.open(io.BytesIO(render(art_svg, "0 0 1920 1080", 1920, 1080))).convert("RGBA"))
    if season == "summer" and pal == "night" and town["extras"]["fireflies"]:
        im.alpha_composite(Image.open(os.path.join(images, "fireflies_a.png")).convert("RGBA").resize((1920, 400)), (0, 540))
    if plane and town["extras"]["airplane"]:
        im.alpha_composite(Image.open(os.path.join(images, f"plane_{pal}.png")).convert("RGBA").resize((56, 22), Image.LANCZOS), plane)
    for animal, px in pets:
        # Animal images are saved at the size they are shown. Some animals have
        # a darker image for night, like in MainScene.brs.
        name = animal["image"]
        if pal == "night" and os.path.exists(os.path.join(images, f"{name}_night.png")):
            name += "_night"
        pet = Image.open(os.path.join(images, f"{name}.png")).convert("RGBA")
        im.alpha_composite(pet, (px, 924 - pet.height))
    parked(town, images, im, section, "van" if pal == "day" else "sedan")
    im.alpha_composite(lamps_image(town, section, p, season))
    cars = town["cars"]
    far_car = "truck" if "truck" in cars else cars[-1]
    near_car = near_car if near_car in cars else cars[0]
    # With drive_on "right", the near lane drives to the right and the far lane to the left
    near_left = town["drive_on"] == "left"
    paste_car(im, images, far_car, 1150, 1002, 0.86, left=not near_left)
    paste_car(im, images, near_car, 420, 1072, 1.0, left=near_left)
    if fx and (fx != "leaves" or town["extras"]["falling_leaves"]):
        im.alpha_composite(Image.open(os.path.join(images, f"{fx}.png")).convert("RGBA").resize((1920, 1080)))
    # The panel at its first position in m.infoSpots
    clock = clock_text(town, *hour)
    im.alpha_composite(Image.open(io.BytesIO(render(panel(clock, temp_text(town, temp), cond, 1260), "0 0 1920 1080", 1920, 1080))).convert("RGBA"))
    return im.convert("RGB")

def write_all(town, layers, images, build, docs=None):
    os.makedirs(build, exist_ok=True)
    for f in os.listdir(build):
        if f.endswith(".png"):
            os.remove(os.path.join(build, f))
    n = len(town["sections"])
    # Composites for checking the art: each section, in every season, by day and night
    for season in ("spring", "summer", "fall", "winter"):
        for pal in ("day", "night"):
            for i in range(n):
                im = composite(town, layers, pal, i, season, images, ("van" if pal == "day" else "sedan") if season == "summer" else None)
                im.save(os.path.join(build, f"composite_{season}_{pal}_{LETTERS[i]}.png"))
    # The README previews. The animals are shown in the last section.
    last = n - 1
    rnd = random.Random(3)
    pets = [(animal, 200 + k * 1560 // max(1, len(town["pets"]))) for k, animal in enumerate(town["pets"])]
    rnd.shuffle(pets)
    shots = [("preview.png", 1280, dict(pal="day", season="summer", hour=(10, 4), temp=84, cond="Clear", section=0, plane=(560, 262)))]
    # The cloud level matches the weather text, like cloudLevel() in MainScene.brs
    for season, temp, cond, fx, clouds in (("spring", 62, "Partly cloudy", None, "scattered"), ("summer", 84, "Clear", None, "few"),
                                           ("fall", 55, "Mostly clear", "leaves", "few"), ("winter", 28, "Overcast", None, "overcast")):
        shots.append((f"preview_{season}.png", 640, dict(pal="day", season=season, hour=(10, 4), temp=temp, cond=cond, fx=fx,
                                                         section=min(1, last), clouds=clouds)))
    for pal, hour in (("day", (10, 4)), ("dusk", (19, 12)), ("night", (22, 42))):
        shots.append((f"preview_{pal}.png", 640, dict(pal=pal, season="summer", hour=hour, temp=78, cond="Clear", section=0)))
    for i in range(n):
        shots.append((f"preview_section_{LETTERS[i]}.png", 1280,
                      dict(pal="day", season="summer", hour=(10, 4), temp=84, cond="Clear", section=i,
                           pets=pets if i == last else (), near_car="buggy" if i == last else "sports")))
    shots.append((f"preview_section_{LETTERS[last]}_winter_night.png", 640,
                  dict(pal="night", season="winter", hour=(22, 42), temp=26, cond="Clear", section=last, pets=pets, near_car="buggy")))
    for name, width, opts in shots:
        im = preview(town, layers, images, **opts)
        im.resize((width, width * 9 // 16), Image.LANCZOS).save(os.path.join(build, name), optimize=True)
        if docs:
            os.makedirs(docs, exist_ok=True)
            im.resize((width, width * 9 // 16), Image.LANCZOS).save(os.path.join(docs, name), optimize=True)
