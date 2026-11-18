"""Shared drawing helpers: palettes, colors, fonts, text, and small details
used by the scenery and the buildings."""
import math
import os
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ACCENT = "#E8703F"
ICON = "#6E7A85"      # Gray for the icons in shop windows
DARK = "#1F2A33"
# Car windows. Every car, including the special cars, uses this black.
CAR_GLASS = "#111417"
WHITE = "#F8FAFC"

P = {
 "day": dict(sky="#C9DAEA", horizon="#EEF3F8", cloud="#FFFFFF", far="#A9C0D2", mid="#6F93AE", snow="#FFFFFF",
   hillFar="#7FA487", hill="#5E8B6B", tree="#3F6B52", river="#4A82A8", riverHi="#A9C8DD",
   houseA="#F8FAFC", houseB="#ECEFF3", wall2="#D9E2EA", roof="#34495E", window="#9DB6C9",
   sidewalk="#D9E2EA", curb="#B7C4CF", road="#3E4A53", roadLine="#F8FAFC", clockFace="#F8FAFC",
   cloudGray="#D5DCE2", skyGray="#A7B3BE", horizonGray="#D6DCE1"),
 "dusk": dict(sky="#5E6F93", horizon="#F2A27E", cloud="#F3D6CC", far="#7A8BA8", mid="#56708C", snow="#E8D9D3",
   hillFar="#5E7C6C", hill="#4A6A58", tree="#34523F", river="#5C7493", riverHi="#F2B79C",
   houseA="#E3E1E4", houseB="#D4D3DA", wall2="#C3C6D0", roof="#2A3F50", window="#F6C46A",
   sidewalk="#BFC6CF", curb="#9CA6B1", road="#333E47", roadLine="#E3E1E4", clockFace="#F6E7B0",
   cloudGray="#B4A9B0", skyGray="#5F6578", horizonGray="#B39A93"),
 "night": dict(sky="#16242F", horizon="#34495E", cloud="#3A4E5E", far="#3A5468", mid="#2E465A", snow="#9FB2C2",
   hillFar="#2F4A3F", hill="#263E34", tree="#1D3229", river="#34495E", riverHi="#6E8BA3",
   houseA="#5B6770", houseB="#4E5A63", wall2="#46525C", roof="#1A2A36", window="#F6C46A",
   sidewalk="#5B6770", curb="#46525C", road="#20282E", roadLine="#C9D2DA", clockFace="#F6C46A",
   cloudGray="#33424E", skyGray="#1D262E", horizonGray="#2E3943"),
}

# Seasons. Each season lists day colors that replace palette values. The dusk
# and night colors are worked out by darkening each day color the same way the
# summer palette darkens it (see season_palette). "summer" uses the palette as
# it is. Keys that are not in P (leaf, leaf2, trunk) are darkened like "tree".
SEASONS = ["spring", "summer", "fall", "winter"]
SEASON_COLORS = {
 "spring": dict(hillFar="#8DB58F", hill="#6FA374", leaf="#7DBB6E", leaf2="#F2B8C6", trunk="#6B5442"),
 "summer": dict(leaf="#3F6B52", leaf2="#3F6B52", trunk="#3F6B52"),
 "fall": dict(hillFar="#A39A5E", hill="#8E8A4E", leaf="#D9822B", leaf2="#B5523F", trunk="#6B5442"),
 "winter": dict(hillFar="#CFDBE6", hill="#DDE6EE", river="#8FB3CC", leaf="#3F6B52", leaf2="#3F6B52", trunk="#6B5442"),
}
SEASON_BASE_KEY = {"leaf": "tree", "leaf2": "tree", "trunk": "tree"}

def hex_rgb(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)]

def season_palette(pal, season):
    p = dict(P[pal])
    for key, day in SEASON_COLORS[season].items():
        base = SEASON_BASE_KEY.get(key, key)
        ratio = [n / max(d, 1) for n, d in zip(hex_rgb(P[pal][base]), hex_rgb(P["day"][base]))]
        p[key] = "#" + "".join(f"{min(255, round(c * r)):02X}" for c, r in zip(hex_rgb(day), ratio))
    return p

def wall(day, p):
    """Darkens a day color for dusk and night the same way the palette darkens
    the white house color."""
    ratio = [n / d for n, d in zip(hex_rgb(p["houseA"]), hex_rgb(P["day"]["houseA"]))]
    return "#" + "".join(f"{min(255, round(c * r)):02X}" for c, r in zip(hex_rgb(day), ratio))

# ---------- Fonts and text ----------
# The fonts are stored in tools/fonts under the SIL Open Font License. Most are
# variable fonts (one file covers a range of weights); for the ones with one
# weight, the weight value is ignored. Text is converted to outlines, so the
# images look the same on every computer.
FONT_DIR = os.path.join(TOOLS, "fonts")
FONTS = {"oswald": "Oswald-Variable.ttf", "playfair": "PlayfairDisplay-Variable.ttf",
         "cinzel": "Cinzel-Variable.ttf", "script": "DancingScript-Variable.ttf",
         "kaushan": "KaushanScript-Regular.ttf", "alegreya": "AlegreyaSans-Medium.ttf",
         "signika": "Signika-Variable.ttf", "cabin": "Cabin-Variable.ttf", "hanken": "HankenGrotesk-Variable.ttf",
         "pacifico": "Pacifico-Regular.ttf", "amatic": "AmaticSC-Bold.ttf", "fredoka": "Fredoka-Variable.ttf",
         "lora": "Lora-Italic-Variable.ttf", "montserrat": "Montserrat-Variable.ttf", "raleway": "Raleway-Variable.ttf",
         "comfortaa": "Comfortaa-Variable.ttf", "josefin": "JosefinSans-Variable.ttf", "quicksand": "Quicksand-Variable.ttf",
         "bitter": "Bitter-Variable.ttf", "sharetech": "ShareTechMono-Regular.ttf", "graduate": "Graduate-Regular.ttf",
         "racing": "RacingSansOne-Regular.ttf"}
_glyphs = {}

def glyphs(font, weight):
    key = (font, weight)
    if key not in _glyphs:
        f = TTFont(os.path.join(FONT_DIR, FONTS[font]))
        gs = f.getGlyphSet(location={"wght": weight}) if "fvar" in f else f.getGlyphSet()
        _glyphs[key] = (f.getBestCmap(), gs, f["head"].unitsPerEm)
    return _glyphs[key]

def curly_apostrophes(label):
    """Uses a curly apostrophe in place of a straight one."""
    return label.replace("'", "\u2019")

def check_text(label, font):
    """Returns the characters in label that font cannot draw."""
    cmap = glyphs(font, 400)[0]
    return sorted({ch for ch in curly_apostrophes(label) if ord(ch) not in cmap})

def text_width(label, font, weight, size, spacing=0):
    cmap, gs, upm = glyphs(font, weight)
    k = size / upm
    label = curly_apostrophes(label)
    return sum(gs[cmap[ord(ch)]].width * k for ch in label) + spacing * (len(label) - 1)

def fit_size(label, font, weight, size, max_width, spacing=0, smallest=9):
    """The largest size up to size at which label fits in max_width."""
    while size > smallest and text_width(label, font, weight, size, spacing) > max_width:
        size -= 0.5
    return size

def text(label, font, weight, size, cx, y, fill, spacing=0, outline=None, outline_width=0):
    """Draws label as outlines, centered on cx, with its baseline at y. If
    outline is a color, each letter also gets an outline of that color and of
    outline_width pixels, drawn behind the letter."""
    label = curly_apostrophes(label)
    if not label:
        return ""
    cmap, gs, upm = glyphs(font, weight)
    k = size / upm
    x = cx - text_width(label, font, weight, size, spacing) / 2
    d = ""
    for ch in label:
        n = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        d += pen.getCommands()
        x += gs[n].width * k + spacing
    if outline:
        return (f'<path d="{d}" fill="{outline}" stroke="{outline}" stroke-width="{outline_width * 2}" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="{fill}"/>')
    return f'<path d="{d}" fill="{fill}"/>'

# ---------- SVG and PNG ----------
def svg(content, vb, w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{content}</svg>'

def render(content, vb, w, h, path=None):
    """Renders SVG content to a PNG file, or returns the PNG bytes."""
    data = svg(content, vb, w, h).encode()
    if path:
        cairosvg.svg2png(bytestring=data, write_to=path)
        return path
    return cairosvg.svg2png(bytestring=data)

def shift(content, dx):
    return f'<g transform="translate({dx:.1f},0)">{content}</g>' if dx else content

# ---------- Small details ----------
def arch(x, y, w, h, fill):
    """A window or door with a round top. (x, y) is the top left corner."""
    r = w / 2
    return f'<path d="M{x},{y+h} L{x},{y+r} A{r},{r} 0 0 1 {x+w},{y+r} L{x+w},{y+h} Z" fill="{fill}"/>'

def sign(x, y, w, h, fill, label, font, weight, size, ty, spacing=2, color=WHITE):
    """A sign board with text. The text shrinks to fit the board."""
    size = fit_size(label, font, weight, size, w - 14, spacing)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>'
            + text(label, font, weight, size, x + w / 2, ty, color, spacing))

# Seasonal details. Each returns "" in the seasons it does not belong to.
def snow_flat(season, p, x, y, w):
    return f'<rect x="{x - 2}" y="{y - 6}" width="{w + 4}" height="9" rx="4" fill="{p["snow"]}"/>' if season == "winter" else ""

def snow_ridge(season, p, *pts):
    if season != "winter":
        return ""
    d = " ".join(f"{x},{y}" for x, y in pts)
    return f'<polyline points="{d}" fill="none" stroke="{p["snow"]}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'

def pumpkins(season, p, x, y=900):
    """Two pumpkins in fall. They are put away in December, when the town has
    its Christmas decorations."""
    if season != "fall" or is_christmas(p):
        return ""
    return (f'<ellipse cx="{x}" cy="{y - 8}" rx="11" ry="8" fill="#D9822B"/><rect x="{x - 1}" y="{y - 19}" width="3" height="5" fill="#4A5528"/>'
            f'<ellipse cx="{x + 18}" cy="{y - 6}" rx="8" ry="6" fill="#E8913A"/><rect x="{x + 17}" y="{y - 15}" width="3" height="4" fill="#4A5528"/>')

def flower_box(season, p, x, y, w=44):
    if season != "spring":
        return ""
    s = f'<rect x="{x - 2}" y="{y}" width="{w + 4}" height="8" fill="#8C5A3C"/>'
    for i, c in enumerate(["#F2B8C6", "#F6C46A", "#E8703F", "#F8FAFC", "#F2B8C6", "#F6C46A"]):
        s += f'<circle cx="{x + 4 + i * (w - 8) / 5:.0f}" cy="{y - 2}" r="4" fill="{c}"/>'
    return s

# ---------- Christmas ----------
# In December, town images drawn with christmas_palette() have Christmas
# lights on the buildings, garland on the gazebo and the columned hall, and
# wreaths on the street lamps. The lights are lit at dusk and night.
BULBS = ["#E74C3C", "#2ECC71", "#3D8BEB", "#F4C430", "#E67E22"]   # Red, green, blue, yellow, orange
WARM_WHITE = "#FFF4D6"
# The bulb colors for each style of lights. A building uses one style.
LIGHT_STYLES = {"rainbow": BULBS, "white": [WARM_WHITE], "red_white": ["#E74C3C", WARM_WHITE]}
# Each bulb is in one of three groups, picked from its position. Group 0 stays
# on. Groups 1 and 2 blink: the town images draw them off, and MainScene.brs
# turns them on and off at random with small images of the lit bulbs (see
# write_blink() in generate_images.py).
BLINK_GROUPS = 3
GARLAND = "#2F6B3A"
GARLAND_DARK = "#1E4A28"
BERRY = "#C0392B"

def christmas_palette(p, lit=(0, 1, 2)):
    """A copy of palette p that tells the drawings to add the Christmas
    decorations. lit lists the bulb groups that are on at dusk and night."""
    return dict(p, christmas=True, lit=tuple(lit))

def bulb_group(x, y):
    """The blink group of the bulb at (x, y). The numbers mix the position up,
    so bulbs next to each other are usually in different groups."""
    return (((round(x * 10) * 73856093) ^ (round(y * 10) * 19349663)) >> 5) % BLINK_GROUPS

def is_christmas(p):
    return p.get("christmas", False)

def along(pts, spacing, offset=0):
    """Points every spacing pixels along the line through pts, starting offset
    pixels from the first point."""
    out, d = [], offset
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        while d <= seg:
            t = d / seg if seg else 0
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            d += spacing
        d -= seg
    return out

def swags(x0, x1, y, sag, n):
    """The points of n swags that hang between x0 and x1, each one fixed at y
    at both ends and sag pixels lower in the middle."""
    pts = []
    for i in range(n):
        a = x0 + (x1 - x0) * i / n
        b = x0 + (x1 - x0) * (i + 1) / n
        for k in range(8 if i < n - 1 else 9):
            t = k / 8
            pts.append((a + (b - a) * t, y + 4 * sag * t * (1 - t)))
    return pts

def scallops(x0, x1, y, sag=5, width=40):
    """Swags about width pixels wide between x0 and x1."""
    return swags(x0, x1, y, sag, max(1, round((x1 - x0) / width)))

def christmas_lights(pts, p, spacing=11, start=0):
    """A string of bulbs on a thin wire along the line through pts, in the
    building's style of lights (light_style in p, set by town_section() in
    generate_images.py). start picks the color of the first bulb, so strings
    next to each other do not all begin with the same color. At dusk and
    night, the bulbs in the groups in p["lit"] glow and the others are off."""
    dark = is_dark(p)
    colors = LIGHT_STYLES[p.get("light_style", "rainbow")]
    wire = wall("#24332A", p)
    out = ('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
           + f'" fill="none" stroke="{wire}" stroke-width="1.2" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(along(pts, spacing, spacing / 2)):
        c = colors[(start + i) % len(colors)]
        lit = dark and bulb_group(x, y) in p.get("lit", (0, 1, 2))
        if lit:
            out += f'<circle cx="{x:.1f}" cy="{y + 2:.1f}" r="5.5" fill="{c}" fill-opacity="0.35"/>'
        else:
            c = wall(c, p)
        out += f'<ellipse cx="{x:.1f}" cy="{y + 2:.1f}" rx="2" ry="2.7" fill="{c}"/>'
    return out

def garland(pts, p, width=7):
    """A rope of evergreen garland along the line through pts, with red
    berries."""
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out = (f'<polyline points="{d}" fill="none" stroke="{wall(GARLAND, p)}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<polyline points="{d}" fill="none" stroke="{wall(GARLAND_DARK, p)}" stroke-width="{width - 2}" stroke-dasharray="2 3" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(along(pts, 13, 6)):
        out += f'<circle cx="{x + (1.5 if i % 2 else -1.5):.1f}" cy="{y + (1 if i % 2 else -1):.1f}" r="1.6" fill="{wall(BERRY, p)}"/>'
    return out

def bow(x, y, p, size=1.0):
    """A red bow with its knot at (x, y) and two short tails below it."""
    k = size
    c = wall(BERRY, p)
    return (f'<polygon points="{x},{y} {x - 7 * k:.1f},{y - 4 * k:.1f} {x - 7 * k:.1f},{y + 4 * k:.1f}" fill="{c}"/>'
            f'<polygon points="{x},{y} {x + 7 * k:.1f},{y - 4 * k:.1f} {x + 7 * k:.1f},{y + 4 * k:.1f}" fill="{c}"/>'
            f'<polygon points="{x - 1 * k:.1f},{y} {x - 5 * k:.1f},{y + 9 * k:.1f} {x - 2 * k:.1f},{y + 8 * k:.1f}" fill="{c}"/>'
            f'<polygon points="{x + 1 * k:.1f},{y} {x + 5 * k:.1f},{y + 9 * k:.1f} {x + 2 * k:.1f},{y + 8 * k:.1f}" fill="{c}"/>'
            f'<circle cx="{x}" cy="{y}" r="{2 * k:.1f}" fill="{wall("#962D22", p)}"/>')

def wreath(cx, cy, r, p, width=5):
    """A round evergreen wreath with red berries and a red bow at the bottom."""
    out = (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{wall(GARLAND, p)}" stroke-width="{width}"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{wall(GARLAND_DARK, p)}" stroke-width="{width - 2}" stroke-dasharray="2 2.5"/>')
    for a in (40, 100, 160, 220, 320):
        rad = math.radians(a)
        out += f'<circle cx="{cx + r * math.cos(rad):.1f}" cy="{cy - r * math.sin(rad):.1f}" r="1.5" fill="{wall(BERRY, p)}"/>'
    return out + bow(cx, cy + r, p, max(0.5, r / 12))

def round_tree(x, ground, h, r, p, season):
    """A tree with a round top. x is the trunk center, ground is the bottom of
    the trunk, h is the trunk height, and r is the radius of the top."""
    cy = ground - h - r * 0.4
    if season == "winter":
        # Bare branches
        s = f'<g stroke="{p["trunk"]}" stroke-linecap="round" fill="none">'
        s += f'<line x1="{x}" y1="{ground}" x2="{x}" y2="{cy - r * 0.5:.0f}" stroke-width="{max(6, r // 4)}"/>'
        for dx, dy, w in ((-0.8, -0.5, 4), (0.8, -0.6, 4), (-0.5, -1.0, 3), (0.5, -1.1, 3), (0, -1.2, 3)):
            s += f'<line x1="{x}" y1="{cy + r * 0.3:.0f}" x2="{x + dx * r:.0f}" y2="{cy + dy * r * 0.8:.0f}" stroke-width="{w}"/>'
        s += '</g>'
        return s + f'<path d="M{x - r * 0.7:.0f},{cy - r * 0.35:.0f} L{x - r * 0.4:.0f},{cy - r * 0.45:.0f}" stroke="{p["snow"]}" stroke-width="3" stroke-linecap="round"/>'
    w = max(10, r // 3)
    s = (f'<rect x="{x - w // 2}" y="{ground - h}" width="{w}" height="{h}" fill="{p["trunk"]}"/>'
         f'<circle cx="{x}" cy="{cy:.0f}" r="{r}" fill="{p["leaf"]}"/>')
    if season in ("spring", "fall"):
        # Blossoms in spring, a second leaf color in fall
        for ax, ay in ((-0.5, -0.3), (0.3, -0.55), (0.55, 0.1), (-0.2, 0.35), (0.05, -0.05), (-0.6, 0.25), (0.35, 0.5)):
            s += f'<circle cx="{x + ax * r:.0f}" cy="{cy + ay * r:.0f}" r="{max(3, r // 7)}" fill="{p["leaf2"]}"/>'
    return s

# Pine trees are triangles, 52 pixels tall and 32 pixels wide, with the base
# at b. Each shape cuts no, one, or two small triangles (notches) out of the
# sides.
# A notch is (side, height above the base, depth): the notch is 8 pixels tall,
# centered at that height, and its point is depth pixels in from the edge.
PINE_SHAPES = [
    [],  # A full triangle with no notches
    [("right", 30, 4)],
    [("left", 22, 4), ("right", 34, 3)],
    [("left", 32, 4)],
    [("left", 28, 3), ("right", 16, 4)],
]

def pine_shape(x, b):
    """Picks a pine shape from the tree position, so the same tree has the
    same shape in every image. The numbers mix the position up, so trees
    next to each other usually get different shapes."""
    return PINE_SHAPES[((x * 2654435761 + b * 40503) >> 16) % len(PINE_SHAPES)]

def pine(x, b, p, season):
    notches = pine_shape(x, b)

    def edge(h):
        # Half the width of the triangle at h pixels above the base
        return 16 * (52 - h) / 52

    def side(name, sign):
        # The points down one side, from the top to the base
        pts = []
        for n, h, depth in sorted((n for n in notches if n[0] == name), key=lambda n: -n[1]):
            pts += [(x + sign * edge(h + 4), b - h - 4), (x + sign * (edge(h) - depth), b - h),
                    (x + sign * edge(h - 4), b - h + 4)]
        return pts

    pts = [(x, b - 52)] + side("right", 1) + [(x + 16, b), (x - 16, b)] + list(reversed(side("left", -1)))
    s = '<polygon points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + f'" fill="{p["tree"]}"/>'
    if season == "winter":
        s += (f'<polygon points="{x},{b-52} {x-7},{b-36} {x},{b-39} {x+7},{b-36}" fill="{p["snow"]}"/>'
              f'<path d="M{x-12},{b-12} L{x-4},{b-15}" stroke="{p["snow"]}" stroke-width="3" stroke-linecap="round"/>')
    return s

def is_dark(p):
    """True for the dusk and night palettes, when lights are on."""
    return p["window"] != P["day"]["window"]

# ---------- Shadows ----------
# Shadows are black shapes drawn with a low opacity, so they darken whatever is
# under them. The sun is in the top-left corner of the screen, so shadows fall
# down and to the right. They are lighter at dusk and night.
SHADOW_OPACITY = {"day": 0.2, "dusk": 0.15, "night": 0.12}

def shadow_opacity(p):
    if not is_dark(p):
        return SHADOW_OPACITY["day"]
    return SHADOW_OPACITY["night"] if p["sky"] == P["night"]["sky"] else SHADOW_OPACITY["dusk"]

def shadow(points, p, scale=1.0):
    """A shadow polygon through points, a list of (x, y)."""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="#000000" fill-opacity="{shadow_opacity(p) * scale:.3f}"/>'

def skewed(content, y, angle=-10):
    """Slants content like italic letters, keeping the line at y in place."""
    import math
    k = math.tan(math.radians(-angle))
    return f'<g transform="translate({k * y:.2f},0) skewX({angle})">{content}</g>'

# ---------- Bicycles ----------
# A bicycle is drawn in a 60x46 box: the wheels are at (12,38) and (46,38)
# with a radius of 10. Bikes are always parked and empty: the art has no
# people in it.
def bike_frame(color, dark=DARK):
    s = (f'<g stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" fill="none">'
         '<polyline points="12,38 26,38 22,22 12,38"/><polyline points="22,22 42,22 26,38"/>'
         '<polyline points="42,22 46,38"/></g>'
         f'<g stroke="{dark}" stroke-width="2.2" stroke-linecap="round" fill="none">'
         '<line x1="40" y1="18" x2="45" y2="17"/><line x1="42" y1="22" x2="41" y2="17"/>'
         '<line x1="18" y1="18" x2="25" y2="18"/><line x1="22" y1="22" x2="21" y2="18"/>'
         '<line x1="23" y1="41" x2="29" y2="35"/></g>')
    return s

def bike_wheels(dark=DARK, rim="#9CA6B1"):
    return "".join(f'<circle cx="{cx}" cy="38" r="9" fill="none" stroke="{dark}" stroke-width="2.4"/>'
                   f'<circle cx="{cx}" cy="38" r="7" fill="none" stroke="{rim}" stroke-width="0.8"/>'
                   f'<circle cx="{cx}" cy="38" r="1.4" fill="{rim}"/>' for cx in (12, 46))

def bicycle(x, ground, scale, color, left=False):
    """A bicycle standing on the ground line at y=ground, with its left end at
    x. scale 1 is 60 pixels wide."""
    body = bike_frame(color) + bike_wheels()
    if left:
        body = f'<g transform="translate(60,0) scale(-1,1)">{body}</g>'
    return f'<g transform="translate({x:.1f},{ground - 48 * scale:.1f}) scale({scale})">{body}</g>'
