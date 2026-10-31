"""Reads town.json, checks it, and fills in the defaults.

Errors are raised as ConfigError with a message that names the field, so a
person editing town.json can find the mistake.
"""
import json
import os
import urllib.parse
import urllib.request
from .art import FONTS, ACCENT, DARK, WHITE, check_text

SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "town.schema.json")

class ConfigError(Exception):
    pass

# Day colors for houses and shops that do not set their own. They are used in
# order, so buildings next to each other get different colors.
HOUSE_PALETTE = ["#F3E3B8", "#CFE3D4", "#D6E4F0", "#F2D4D7", "#E8DCCB", "#DCD6EC", "#F8FAFC", "#CFE6E3", "#F7C9B6"]
SHOP_PALETTE = ["#F6D9C8", "#DCCBB2", "#D2D4E2", "#EAD7B4", "#D6EEF0", "#F2E4C6", "#D3D8DE", "#DCEFD6", "#F3DCB6"]
SCHOOL_PALETTE = ["#C98A74", "#D9C39A", "#B9C7D6"]
# Fonts for house numbers that do not set their own, also used in order
HOUSE_FONTS = [("signika", 500), ("hanken", 600), ("cabin", 600), ("raleway", 700), ("comfortaa", 700),
               ("josefin", 600), ("quicksand", 700), ("bitter", 600), ("montserrat", 700)]

# Shop presets. Each is a shop with these options already set. Any option in
# town.json replaces the preset value.
PRESETS = {
    "bakery": dict(font="script", weight=700, stories=2),
    "bookstore": dict(font="playfair", weight=700, sign_color="#6B4A3A", window="books", awning_color="#6F93AE"),
    "diner": dict(font="kaushan", weight=400, stories=3, sign_size=32),
    "computer_store": dict(font="sharetech", weight=400, sign_color=DARK, sign_text_color="#7CF29A", window="computer"),
    "ice_cream": dict(font="pacifico", weight=400, sign_color="#E86A92", awning="striped",
                      awning_colors=["#E86A92", WHITE], window="ice_cream", roof_icon="ice_cream"),
    "art_store": dict(font="amatic", weight=700, sign_color="#6B4A3A", sign_size=32, stories=2, window="palette",
                      awning_color="#6F93AE"),
    "photo_store": dict(font="montserrat", weight=700, sign_color=DARK, letter_spacing=6, window="camera"),
    "pet_shop": dict(font="fredoka", weight=600, sign_color="#4A82A8", sign_icon="paw", awning="striped",
                     awning_colors=["#4A82A8", WHITE], window="pets", stories=2),
    "restaurant": dict(font="lora", weight=600, sign_color="#2F5D3A", awning="striped",
                       awning_colors=["#2F8F4E", WHITE, "#C0392B"], window="table", stories=2),
}

# Defaults for each building type
DEFAULTS = {
    "house": dict(width=150, weight=600),
    "shop": dict(width=210, stories=1, font="oswald", weight=600, awning="plain", awning_color=ACCENT),
    "church": dict(style="steeple", cross=True, color=WHITE, font="alegreya", weight=400),
    "school": dict(width=300, cross=False, bell_tower=False, font="playfair", weight=700),
    "columned_hall": dict(clock=False, clock_time="10:04", font="cinzel", weight=700),
    "gas_station": dict(canopy_name="FUEL STOP", store_name="MARKET", store_sign_color="#1F4E9C", price="2.05",
                        color="#E2E7EE", font="oswald", weight=600),
    "drive_through": dict(font="script", weight=700, color=WHITE, roof_color="#D62E3C"),
    "tree": dict(),
    "gazebo": dict(color="#A9553F", font="playfair", weight=700),
    "bike_rack": dict(),
    "section_break": dict(),
}

CARS = ["sedan", "van", "jeep", "truck", "sports", "buggy"]
PETS = {"cat": ["black", "gray", "tabby", "white", "gray_white"], "guinea_pig": ["black_orange", "white_orange"],
        "dog": ["yellow_lab", "black_lab", "chocolate_lab", "beagle", "corgi", "dalmatian", "dachshund", "husky"]}
PET_IMAGE = {"cat": "cat", "guinea_pig": "guinea", "dog": "dog"}   # The first part of each image name
EXTRAS = {"airplane": True, "kayaks": True, "fireflies": True, "falling_leaves": True, "seasons": True,
          "table_mountain": False, "bikes": False, "street_lights": False}
RADIO = dict(color="#E4DCCD", font="racing", weight=400, letter_color="#D32F2F", tower=True)

# Text fields that are not drawn with the building's own font
FIELD_FONTS = {("radio_station", "small_line"): "kaushan", ("radio_station", "power"): "oswald",
               ("gas_station", "canopy_name"): "oswald"}

def validate(data):
    try:
        import jsonschema
    except ImportError:
        return
    with open(SCHEMA) as f:
        schema = json.load(f)
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        lines = []
        for e in errors[:10]:
            lines.append("  " + explain(e, jsonschema.exceptions.best_match))
        raise ConfigError("town.json has mistakes:\n" + "\n".join(lines))

def explain(e, best_match):
    """A clear message for one schema error. A building that matches none of
    the building types gets the message for the type it names."""
    path = list(e.path)
    where = "/".join(str(x) for x in path) or "(top level)"
    if path == ["location"] and e.validator == "anyOf":
        return 'location: give a "zip", or both "lat" and "lon".'
    if e.validator == "anyOf" and isinstance(e.instance, dict) and len(path) == 2 and path[0] in ("buildings", "houses"):
        kind = e.instance.get("type")
        types = sorted(DEFAULTS) + sorted(PRESETS)
        if kind not in types:
            return f"{where}: there is no building type called {kind!r}. The types are: {', '.join(types)}."
        # The errors from the part of the schema for this building's type
        def has_type(sub):
            t = sub.get("properties", {}).get("type", {})
            return kind == t.get("const") or kind in t.get("enum", [])
        match = [i for i, sub in enumerate(e.schema["anyOf"]) if has_type(sub)]
        named = [c for c in e.context if match and c.schema_path[0] == match[0]]
        detail = best_match(named or e.context)
        sub = "/".join(str(x) for x in detail.relative_path)
        return f"{where}{'/' + sub if sub else ''}: {detail.message}"
    return f"{where}: {e.message}"

def lookup_zip(zip_code, country):
    """Finds the coordinates of a ZIP or postal code. Tries the Open-Meteo
    geocoding service first, then Zippopotam.us."""
    tries = []
    q = urllib.parse.urlencode({"name": zip_code, "count": 1, "countryCode": country})
    tries.append((f"https://geocoding-api.open-meteo.com/v1/search?{q}",
                  lambda d: (d["results"][0]["latitude"], d["results"][0]["longitude"])))
    tries.append((f"https://api.zippopotam.us/{country.lower()}/{urllib.parse.quote(zip_code)}",
                  lambda d: (float(d["places"][0]["latitude"]), float(d["places"][0]["longitude"]))))
    problems = []
    for url, read in tries:
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                lat, lon = read(json.load(r))
                return round(lat, 4), round(lon, 4)
        except Exception as e:
            problems.append(f"{url.split('/')[2]}: {e}")
    raise ConfigError(f"Could not look up the coordinates for ZIP code {zip_code} ({'; '.join(problems)}). "
                      "Add \"lat\" and \"lon\" to \"location\" in town.json instead.")

def spread_houses(buildings, houses):
    """Places the houses from the "houses" list between the buildings, spread
    out as evenly as possible."""
    if not buildings:
        return list(houses)
    out = []
    step = (len(buildings) + 1) / (len(houses) + 1) if houses else 0
    hi = 0
    for i, b in enumerate(buildings):
        while hi < len(houses) and (hi + 1) * step <= i + 0.5:
            out.append(houses[hi])
            hi += 1
        out.append(b)
    return out + list(houses[hi:])

def load(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Could not find {path}.")
    except json.JSONDecodeError as e:
        raise ConfigError(f"{path} is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}.")
    validate(data)
    return fill(data)

def fill(data):
    town = {"title": data.get("title", "Riverside Town")}
    units = data.get("units", {})
    town["temperature"] = units.get("temperature", "F")
    town["clock"] = units.get("clock", "12h")
    town["hemisphere"] = data.get("hemisphere", "north")
    town["cars"] = data.get("cars", CARS)
    town["extras"] = dict(EXTRAS, **data.get("extras", {}))
    # The radio station on the hill beside the river
    radio = data.get("radio_station")
    town["radio_station"] = None
    if radio:
        town["radio_station"] = spec = dict(RADIO, **radio)
        for key in ("name", "small_line", "power"):
            font = FIELD_FONTS.get(("radio_station", key), spec["font"])
            bad = check_text(str(spec[key]), font) if spec.get(key) else []
            if bad:
                raise ConfigError(f"radio_station: the font {font} cannot draw {' '.join(bad)} in \"{spec[key]}\".")
    town["pets"] = [dict(image=f"{PET_IMAGE[p['type']]}_{p['color']}" + ("_small" if p.get("size") == "small" else ""))
                    for p in data.get("pets", [])]
    for i, p in enumerate(data.get("pets", [])):
        if p["color"] not in PETS[p["type"]]:
            raise ConfigError(f"pets/{i}: a {p['type']} can be {', '.join(PETS[p['type']])}, not {p['color']}.")

    items = [{"type": "house", "number": b} if isinstance(b, (str, int)) else dict(b) for b in data.get("buildings", [])]
    houses = [{"type": "house", "number": h} if isinstance(h, (str, int)) else dict(dict(h), type="house")
              for h in data.get("houses", [])]
    items = spread_houses(items, houses)
    if not any(b["type"] != "section_break" for b in items):
        raise ConfigError("town.json needs at least one entry in \"buildings\" or \"houses\".")

    counts = {"house": 0, "shop": 0, "school": 0}
    filled = []
    for i, b in enumerate(items):
        kind = b["type"]
        if kind in PRESETS:
            spec = dict(DEFAULTS["shop"], **PRESETS[kind], **b)
            spec["preset"], spec["type"] = kind, "shop"
        else:
            spec = dict(DEFAULTS[kind], **b)
        kind = spec["type"]
        where = f"buildings/{i} ({spec.get('name', spec.get('number', kind))})"
        if kind == "house":
            spec["number"] = str(spec["number"])
            n = counts["house"]
            spec.setdefault("color", HOUSE_PALETTE[n % len(HOUSE_PALETTE)])
            if "font" not in spec:
                spec["font"], spec["weight"] = HOUSE_FONTS[n % len(HOUSE_FONTS)]
            spec.setdefault("stories", 2 if sum(ord(c) for c in spec["number"]) % 2 else 1)
            counts["house"] += 1
        elif kind == "shop":
            spec.setdefault("color", SHOP_PALETTE[counts["shop"] % len(SHOP_PALETTE)])
            counts["shop"] += 1
        elif kind == "school":
            spec.setdefault("color", SCHOOL_PALETTE[counts["school"] % len(SCHOOL_PALETTE)])
            counts["school"] += 1
        elif kind == "church" and spec["style"] == "tower":
            spec.setdefault("color", "#D8CFC2")
        if kind in ("shop", "church", "school", "columned_hall", "drive_through") and not spec.get("name"):
            raise ConfigError(f"{where}: a {kind} needs a \"name\".")
        for key in ("name", "number", "small_line", "store_name", "canopy_name", "power"):
            if spec.get(key):
                font = FIELD_FONTS.get((kind, key), spec.get("font"))
                if font not in FONTS:
                    raise ConfigError(f"{where}: there is no font called {font}. The fonts are: {', '.join(sorted(FONTS))}.")
                bad = check_text(str(spec[key]), font)
                if bad:
                    raise ConfigError(f"{where}: the font {font} cannot draw {' '.join(bad)} in \"{spec[key]}\".")
        filled.append(spec)
    town["buildings"] = filled
    # The location is looked up last, so a mistake in the buildings is
    # reported even without a network connection
    loc = data["location"]
    if "lat" in loc and "lon" in loc:
        town["lat"], town["lon"] = loc["lat"], loc["lon"]
    else:
        town["lat"], town["lon"] = lookup_zip(str(loc["zip"]), loc.get("country", "US"))
    return town
