"""Generates every image in images/ from the drawings defined in this file.

Run from the repository root:
    python3 tools/generate_images.py

Requires: pip install cairosvg pillow fonttools
"""
import cairosvg, io, math, random, os
from PIL import Image, ImageOps
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
BUILD = os.path.join(ROOT, "build")
os.makedirs(OUT, exist_ok=True)
os.makedirs(BUILD, exist_ok=True)
ACCENT = "#E8703F"
P = {
 "day": dict(sky="#C9DAEA", horizon="#EEF3F8", cloud="#FFFFFF", far="#A9C0D2", mid="#6F93AE", snow="#FFFFFF",
   hillFar="#7FA487", hill="#5E8B6B", tree="#3F6B52", river="#4A82A8", riverHi="#A9C8DD",
   houseA="#F8FAFC", houseB="#ECEFF3", wall2="#D9E2EA", roof="#34495E", window="#9DB6C9",
   sidewalk="#D9E2EA", curb="#B7C4CF", road="#3E4A53", roadLine="#F8FAFC", clockFace="#F8FAFC"),
 "dusk": dict(sky="#5E6F93", horizon="#F2A27E", cloud="#F3D6CC", far="#7A8BA8", mid="#56708C", snow="#E8D9D3",
   hillFar="#5E7C6C", hill="#4A6A58", tree="#34523F", river="#5C7493", riverHi="#F2B79C",
   houseA="#E3E1E4", houseB="#D4D3DA", wall2="#C3C6D0", roof="#2A3F50", window="#F6C46A",
   sidewalk="#BFC6CF", curb="#9CA6B1", road="#333E47", roadLine="#E3E1E4", clockFace="#F6E7B0"),
 "night": dict(sky="#16242F", horizon="#34495E", cloud="#3A4E5E", far="#3A5468", mid="#2E465A", snow="#9FB2C2",
   hillFar="#2F4A3F", hill="#263E34", tree="#1D3229", river="#34495E", riverHi="#6E8BA3",
   houseA="#5B6770", houseB="#4E5A63", wall2="#46525C", roof="#1A2A36", window="#F6C46A",
   sidewalk="#5B6770", curb="#46525C", road="#20282E", roadLine="#C9D2DA", clockFace="#F6C46A"),
}

# Seasons. Each season lists day colors that replace palette values. The dusk
# and night colors are worked out by darkening each day color the same way the
# summer palette darkens it (see season_palette). "summer" uses the palette as
# it is. Keys that are not in P (leaf, leaf2, blossom, trunk) are darkened like
# "tree".
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

# Layers that have a different image for some seasons. A layer that is not
# listed, or a season that is not in its list, uses the summer drawing saved
# without a season in the file name. components/MainScene.brs has the same
# list in m.seasonalLayers.
SEASONAL = {"far": ["winter"], "far_b": ["winter"], "near": ["winter"], "near_b": ["winter"], "hills": SEASONS, "town_a": SEASONS, "town_b": SEASONS, "town_c": SEASONS, "town_d": SEASONS}

# Store sign fonts. Most are variable fonts (one file covers a range of weights).
# Kaushan Script and Alegreya Sans Medium have one weight, so the weight value is
# ignored for them. They are
# stored in tools/fonts under the SIL Open Font License. Text is converted to
# outlines here, so the images look the same on every computer.
FONT_DIR = os.path.join(ROOT, "tools", "fonts")
FONTS = {"oswald": "Oswald-Variable.ttf", "playfair": "PlayfairDisplay-Variable.ttf",
         "cinzel": "Cinzel-Variable.ttf", "script": "DancingScript-Variable.ttf",
         "kaushan": "KaushanScript-Regular.ttf", "alegreya": "AlegreyaSans-Medium.ttf",
         "signika": "Signika-Variable.ttf", "cabin": "Cabin-Variable.ttf", "hanken": "HankenGrotesk-Variable.ttf",
         "pacifico": "Pacifico-Regular.ttf", "amatic": "AmaticSC-Bold.ttf", "fredoka": "Fredoka-Variable.ttf",
         "lora": "Lora-Italic-Variable.ttf", "montserrat": "Montserrat-Variable.ttf", "raleway": "Raleway-Variable.ttf",
         "comfortaa": "Comfortaa-Variable.ttf", "josefin": "JosefinSans-Variable.ttf", "quicksand": "Quicksand-Variable.ttf",
         "bitter": "Bitter-Variable.ttf", "sharetech": "ShareTechMono-Regular.ttf",
         "graduate": "Graduate-Regular.ttf"}
_glyphs = {}

def glyphs(font, weight):
    key = (font, weight)
    if key not in _glyphs:
        f = TTFont(os.path.join(FONT_DIR, FONTS[font]))
        gs = f.getGlyphSet(location={"wght": weight}) if "fvar" in f else f.getGlyphSet()
        _glyphs[key] = (f.getBestCmap(), gs, f["head"].unitsPerEm)
    return _glyphs[key]

def text_width(label, font, weight, size, spacing=0):
    cmap, gs, upm = glyphs(font, weight)
    k = size / upm
    return sum(gs[cmap[ord(ch)]].width * k for ch in label) + spacing * (len(label) - 1)

def text(label, font, weight, size, cx, y, fill, spacing=0, outline=None, outline_width=0):
    """Draws label as outlines, centered on cx, with its baseline at y. If
    outline is a color, each letter also gets an outline of that color and of
    outline_width pixels, drawn behind the letter."""
    cmap, gs, upm = glyphs(font, weight)
    k = size / upm
    names = [cmap[ord(ch)] for ch in label]
    x = cx - text_width(label, font, weight, size, spacing) / 2
    d = ""
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        d += pen.getCommands()
        x += gs[n].width * k + spacing
    if outline:
        return (f'<path d="{d}" fill="{outline}" stroke="{outline}" stroke-width="{outline_width * 2}" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="{fill}"/>')
    return f'<path d="{d}" fill="{fill}"/>'

def svg(content, vb, w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{content}</svg>'

def save(content, vb, w, h, name):
    cairosvg.svg2png(bytestring=svg(content, vb, w, h).encode(), write_to=os.path.join(OUT, name))

def clouds(p, season):
    c = p["cloud"]
    return f'''<g fill="{c}">
<circle cx="360" cy="200" r="38"/><circle cx="420" cy="182" r="52"/><circle cx="480" cy="200" r="40"/><rect x="322" y="200" width="196" height="38" rx="19"/>
<circle cx="1050" cy="150" r="30"/><circle cx="1100" cy="136" r="42"/><circle cx="1150" cy="150" r="32"/><rect x="1020" y="150" width="162" height="30" rx="15"/>
<circle cx="1640" cy="300" r="34"/><circle cx="1695" cy="284" r="46"/><circle cx="1750" cy="300" r="34"/><rect x="1606" y="300" width="178" height="34" rx="17"/></g>'''

def snow_caps(points, t, fill, min_rise=30):
    """Snow on every peak of a mountain outline. t is how far down each slope the
    snow reaches. Peaks that rise less than min_rise pixels above a neighbor
    point (small bumps such as Lion's Head) get no snow cap."""
    out = ""
    for i in range(1, len(points) - 1):
        (lx, ly), (px, py), (rx, ry) = points[i - 1], points[i], points[i + 1]
        if ly - py < min_rise or ry - py < min_rise:
            continue
        ax, ay = px + (lx - px) * t, py + (ly - py) * t
        bx, by = px + (rx - px) * t, py + (ry - py) * t
        zig = []
        for k in range(1, 5):
            f = k / 5
            zig.append(f"{ax + (bx - ax) * f:.0f},{ay + (by - ay) * f + (6 if k % 2 else -4):.0f}")
        out += f'<polygon points="{px},{py} {ax:.0f},{ay:.0f} {" ".join(zig)} {bx:.0f},{by:.0f}" fill="{fill}"/>'
    return out

# The center mountains are shaped like Table Mountain in South Africa, seen
# from the city: a gentle slope up to a rocky peak (Devil's Peak), the long
# flat top with steep cliffs at each end, a dip, and a smaller pointed peak
# (Lion's Head). The flat top points all have the same y value, so
# snow_caps() does not treat them as peaks.
TABLE_TOP = (746, 1066, 310)   # left x, right x, y of the flat top
FAR_PTS = [(0,470),(140,400),(260,450),(420,330),(560,430),
           # Devil's Peak
           (612,408),(668,384),(688,364),(700,352),(712,346),(722,352),(730,349),
           # Left cliff, flat top, right cliff
           (736,326),(742,314),(TABLE_TOP[0],TABLE_TOP[2]),(TABLE_TOP[1],TABLE_TOP[2]),(1072,316),(1080,344),(1090,360),
           # The dip, then Lion's Head
           (1112,372),(1136,380),(1154,377),(1172,358),(1186,336),(1198,326),(1208,342),(1230,372),(1270,400),
           (1320,430),(1480,320),(1640,400),(1780,360),(1920,470)]
def far(p, season):
    pts = " ".join(f"{x},{y}" for x, y in FAR_PTS)
    s = f'<polygon fill="{p["far"]}" points="0,720 {pts} 1920,720"/>'
    if season == "winter":
        s += snow_caps(FAR_PTS, 0.4, p["snow"])
        # Snow along the flat top and over the top of each cliff
        l, r, y = TABLE_TOP
        zig = " ".join(f"{x},{y + (12 if i % 2 else 7)}" for i, x in enumerate(range(r - 16, l + 16, -24)))
        s += f'<polygon points="{l - 8},{y + 6} {l},{y} {r},{y} {r + 8},{y + 8} {r + 2},{y + 14} {zig} {l - 2},{y + 14}" fill="{p["snow"]}"/>'
    return s

NEAR_PTS = [(0,560),(180,470),(320,540),(500,420),(680,560),(820,500),(960,600),(1080,520),(1260,410),(1440,540),(1600,460),(1760,520),(1920,560)]
def near(p, season):
    pts = " ".join(f"{x},{y}" for x, y in NEAR_PTS)
    s = f'<polygon fill="{p["mid"]}" points="0,760 {pts} 1920,760"/>'
    if season == "winter":
        return s + snow_caps(NEAR_PTS, 0.5, p["snow"])
    return s + f'''<g fill="{p["snow"]}"><polygon points="180,470 130,495 150,492 165,502 182,492 200,502 230,495"/>
<polygon points="500,420 448,455 470,450 488,462 506,450 526,462 545,455"/>
<polygon points="1260,410 1203,445 1225,440 1242,452 1262,440 1284,452 1308,445"/></g>'''

# Second far and near mountain tiles, so the mountains repeat half as often.
# Their edge heights match the first tiles (470 for far, 560 for near), so the
# tiles join without a seam in any order. There is no Table Mountain here.
FAR_B_PTS = [(0,470),(150,410),(300,440),(470,350),(620,420),(780,330),(930,400),(1080,320),(1240,410),
             (1400,360),(1560,430),(1700,370),(1820,420),(1920,470)]
def far_b(p, season):
    pts = " ".join(f"{x},{y}" for x, y in FAR_B_PTS)
    s = f'<polygon fill="{p["far"]}" points="0,720 {pts} 1920,720"/>'
    if season == "winter":
        s += snow_caps(FAR_B_PTS, 0.4, p["snow"])
    return s

NEAR_B_PTS = [(0,560),(160,480),(330,530),(520,430),(700,540),(860,470),(1000,580),(1140,500),(1320,420),
              (1500,530),(1660,450),(1800,510),(1920,560)]
def near_b(p, season):
    pts = " ".join(f"{x},{y}" for x, y in NEAR_B_PTS)
    s = f'<polygon fill="{p["mid"]}" points="0,760 {pts} 1920,760"/>'
    # Small snow caps on the highest peaks in other seasons, like the first tile
    return s + snow_caps(NEAR_B_PTS, 0.5 if season == "winter" else 0.22, p["snow"])

TREES = [(60,692),(110,686),(170,680),(240,672),(300,668),(620,662),(680,664),(740,658),
         (1300,668),(1360,682),(1420,692),(1700,724),(1780,724),(1860,714)]
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

def pine(x, b, p, season):
    s = f'<polygon points="{x},{b-52} {x-16},{b} {x+16},{b}" fill="{p["tree"]}"/>'
    if season == "winter":
        s += (f'<polygon points="{x},{b-52} {x-7},{b-36} {x},{b-39} {x+7},{b-36}" fill="{p["snow"]}"/>'
              f'<path d="M{x-12},{b-12} L{x-4},{b-15}" stroke="{p["snow"]}" stroke-width="3" stroke-linecap="round"/>')
    return s

def hills(p, season):
    t = "".join(pine(x, b, p, season) for x, b in TREES)
    return f'''<path fill="{p["hillFar"]}" d="M0,700 C300,620 600,660 960,640 C1300,620 1620,780 1920,700 L1920,910 L0,910 Z"/>
<path fill="{p["hill"]}" d="M0,780 C400,720 700,760 960,740 C1300,720 1520,840 1920,780 L1920,910 L0,910 Z"/>
{t}{round_tree(420, 796, 36, 30, p, season)}{round_tree(1500, 800, 36, 30, p, season)}
<path fill="{p["river"]}" d="M958,647 C935,668 1000,695 900,730 C760,780 640,800 560,900 L1080,900 C1100,820 1180,790 1240,750 C1320,700 1060,675 1000,662 C985,656 968,650 958,647 Z"/>
<g stroke="{p["riverHi"]}" stroke-width="4" stroke-linecap="round" fill="none">
<path d="M962,672 L980,672"/><path d="M930,700 L972,700"/><path d="M860,758 L930,758"/><path d="M1010,770 L1080,770"/><path d="M760,832 L850,832"/><path d="M930,850 L1030,850"/></g>'''

def sign(x, y, w, h, fill, label, font, weight, size, ty, spacing=2):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>'
            + text(label, font, weight, size, x + w / 2, ty, "#F8FAFC", spacing))

def street(p, season):
    walk = p["snow"] if season == "winter" else p["sidewalk"]
    s = (f'<rect x="0" y="900" width="1920" height="36" fill="{walk}"/><rect x="0" y="936" width="1920" height="6" fill="{p["curb"]}"/>'
         f'<rect x="0" y="942" width="1920" height="138" fill="{p["road"]}"/>'
         f'<path d="M0,1011 L1920,1011" stroke="{p["roadLine"]}" stroke-width="6" stroke-dasharray="60 36" fill="none"/>')
    if season == "fall":
        # Fallen leaves on the sidewalk
        rnd = random.Random(11)
        for _ in range(60):
            x, y = rnd.randint(20, 1900), rnd.randint(904, 932)
            c = rnd.choice([p["leaf"], p["leaf2"], "#E0B040"])
            s += f'<ellipse cx="{x}" cy="{y}" rx="5" ry="2.5" fill="{c}" transform="rotate({rnd.randint(0, 180)} {x} {y})"/>'
    return s

# Snow on roofs in winter. Each returns "" in other seasons.
def snow_flat(season, p, x, y, w):
    return f'<rect x="{x - 2}" y="{y - 6}" width="{w + 4}" height="9" rx="4" fill="{p["snow"]}"/>' if season == "winter" else ""

def snow_ridge(season, p, *pts):
    if season != "winter":
        return ""
    d = " ".join(f"{x},{y}" for x, y in pts)
    return f'<polyline points="{d}" fill="none" stroke="{p["snow"]}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'

def pumpkins(season, x, y=900):
    if season != "fall":
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

def arch(x, y, w, h, fill):
    """A window or door with a round top. (x, y) is the top left corner."""
    r = w / 2
    return f'<path d="M{x},{y+h} L{x},{y+r} A{r},{r} 0 0 1 {x+w},{y+r} L{x+w},{y+h} Z" fill="{fill}"/>'

# House wall colors, written as day colors. wall() darkens a day color for
# dusk and night the same way the palette darkens the white house color.
HOUSE_COLORS = {"5401": "#F3E3B8", "135": "#CFE3D4", "5334": "#D6E4F0", "312": "#F2D4D7",
                "402": "#E8DCCB", "527": "#DCD6EC", "612": "#F8FAFC", "1120": "#CFE6E3", "67": "#F7C9B6"}

# Store wall colors, written as day colors and darkened with wall() like the houses
STORE_COLORS = {"longs": "#F6D9C8", "books": "#DCCBB2", "egineering": "#D2D4E2", "lukes": "#EAD7B4", "kroger": "#E2E7EE",
                "cabanas": "#D6EEF0", "art": "#F2E4C6", "photo": "#D3D8DE", "pet": "#DCEFD6", "mama": "#F3DCB6",
                "holycross": "#C98A74", "its": "#D8CFC2", "chick": "#F8FAFC", "covenant": "#D9C39A"}

def wall(day, p):
    ratio = [n / d for n, d in zip(hex_rgb(p["houseA"]), hex_rgb(P["day"]["houseA"]))]
    return "#" + "".join(f"{min(255, round(c * r)):02X}" for c, r in zip(hex_rgb(day), ratio))

# The town layer is three different 1920 pixel tiles, A, B, then C, so the
# street is 5760 pixels long before it repeats.
def town(p, season):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    def house(x, y, w, roofPeak, win1, win2, doorX, winY, number, font, weight=600, upper=None):
        """upper is the y of a second row of windows above the first, or None."""
        up = "" if upper is None else (f'<rect x="{win1}" y="{upper}" width="44" height="40" fill="{Wn}"/><rect x="{win2}" y="{upper}" width="44" height="40" fill="{Wn}"/>'
                                       + flower_box(season, p, win1, upper + 40) + flower_box(season, p, win2, upper + 40))
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{900-y}" fill="{wall(HOUSE_COLORS[number], p)}"/>'
                f'<polygon points="{x-12},{y} {x+w//2},{roofPeak} {x+w+12},{y}" fill="{R}"/>'
                + snow_ridge(season, p, (x - 10, y - 3), (x + w // 2, roofPeak - 3), (x + w + 10, y - 3)) +
                f'<rect x="{win1}" y="{winY}" width="44" height="40" fill="{Wn}"/><rect x="{win2}" y="{winY}" width="44" height="40" fill="{Wn}"/>'
                + flower_box(season, p, win1, winY + 40) + flower_box(season, p, win2, winY + 40) +
                f'<rect x="{doorX}" y="830" width="40" height="70" fill="{R}"/>'
                # House number plaque above the door
                f'<rect x="{doorX-2}" y="808" width="44" height="18" rx="3" fill="{R}"/>'
                + text(number, font, weight, 14, doorX + 20, 822, "#F8FAFC", 1)
                + pumpkins(season, doorX + 54) + up)
    s = house(40, 750, 200, 680, 62, 174, 120, 780, "5401", "signika", 500)
    s += (f'<rect x="270" y="650" width="240" height="250" fill="{wall(STORE_COLORS["longs"], p)}"/><rect x="266" y="650" width="248" height="14" fill="{R}"/>'
          + snow_flat(season, p, 266, 650, 248)
          + f'<rect x="300" y="672" width="44" height="40" fill="{Wn}"/><rect x="436" y="672" width="44" height="40" fill="{Wn}"/>' + snow_flat(season, p, 276, 790, 228)
          + sign(296, 724, 188, 44, R, "Long\u2019s Donuts", "script", 700, 28, 755, 0) +
          f'<polygon points="280,790 500,790 510,822 270,822" fill="{ACCENT}"/>'
          f'<rect x="290" y="832" width="130" height="58" fill="{Wn}"/><rect x="440" y="832" width="46" height="68" fill="{R}"/>')
    s += house(540, 670, 180, 604, 562, 654, 610, 760, "135", "hanken", 300, upper=692)
    # Book store: the display window shows rows of book spines
    spines = ""
    colors = ["#B5523F", "#4A82A8", "#6B7B3A", "#F6C46A", "#34495E", "#C9D2DA"]
    for row, (top, base) in enumerate([(850, 868), (872, 890)]):
        bx = 904 + row * 4
        i = row * 2
        while bx < 1004:
            bw = [8, 10, 7, 9][i % 4]
            bh = base - top - [0, 3, 1, 4, 2][i % 5]
            spines += f'<rect x="{bx}" y="{base-bh}" width="{bw}" height="{bh}" fill="{colors[i % len(colors)]}"/>'
            bx += bw + 2
            i += 1
    s += (f'<rect x="880" y="670" width="220" height="230" fill="{wall(STORE_COLORS["books"], p)}"/><rect x="876" y="670" width="228" height="14" fill="{R}"/>'
          + snow_flat(season, p, 876, 670, 228) + snow_flat(season, p, 892, 808, 196) +
          f'<rect x="906" y="698" width="48" height="48" fill="{Wn}"/><rect x="1026" y="698" width="48" height="48" fill="{Wn}"/>'
          # Two lines: a small FOREVER above a large BOOKS
          + sign(906, 752, 168, 52, "#6B4A3A", "FOREVER", "playfair", 700, 14, 770, 5)
          + text("BOOKS", "playfair", 800, 26, 990, 797, "#F8FAFC", 4) +
          f'<polygon points="890,808 1090,808 1098,836 882,836" fill="{p["mid"]}"/>'
          f'<rect x="900" y="846" width="110" height="48" fill="{Wn}"/>{spines}'
          f'<rect x="900" y="868" width="110" height="4" fill="{R}"/><rect x="900" y="890" width="110" height="4" fill="{R}"/>'
          f'<rect x="1030" y="840" width="46" height="60" fill="{R}"/>')
    s += (f'<rect x="1120" y="710" width="260" height="190" fill="{wall(STORE_COLORS["egineering"], p)}"/><rect x="1116" y="710" width="268" height="14" fill="{R}"/>'
          + snow_flat(season, p, 1116, 710, 268) + snow_flat(season, p, 1132, 800, 236)
          # E-gineering, a computer store, with green letters like an old
          # computer screen and a small gray computer icon in the window
          + f'<rect x="1150" y="732" width="200" height="50" rx="4" fill="#1F2A33"/>'
          + text("E-gineering", "sharetech", 400, 28, 1250, 767, "#7CF29A") +
          f'<polygon points="1130,800 1370,800 1378,828 1122,828" fill="{R}"/>'
          f'<rect x="1140" y="838" width="150" height="56" fill="{Wn}"/><rect x="1310" y="834" width="46" height="66" fill="{R}"/>'
          # Monitor with its screen cut out in the window color, a stand, and a keyboard
          f'<rect x="1197" y="846" width="36" height="25" rx="2" fill="{ICON}"/><rect x="1201" y="850" width="28" height="17" fill="{Wn}"/>'
          f'<rect x="1212" y="871" width="6" height="6" fill="{ICON}"/><rect x="1204" y="877" width="22" height="3" rx="1" fill="{ICON}"/>'
          f'<rect x="1193" y="883" width="44" height="6" rx="1.5" fill="{ICON}"/>')
    s += house(1410, 690, 190, 622, 1432, 1534, 1485, 770, "5334", "cabin", upper=708)
    s += (f'<rect x="1630" y="636" width="250" height="264" fill="{wall(STORE_COLORS["lukes"], p)}"/><rect x="1626" y="636" width="258" height="14" fill="{R}"/>'
          + snow_flat(season, p, 1626, 636, 258)
          + f'<rect x="1660" y="660" width="48" height="40" fill="{Wn}"/><rect x="1772" y="660" width="48" height="40" fill="{Wn}"/>' + snow_flat(season, p, 1642, 820, 226) +
          f'<rect x="1660" y="716" width="48" height="44" fill="{Wn}"/><rect x="1772" y="716" width="48" height="44" fill="{Wn}"/>'
          + sign(1680, 768, 150, 46, R, "Luke\u2019s", "kaushan", 400, 32, 802, 1) +
          f'<polygon points="1640,820 1870,820 1878,846 1632,846" fill="{ACCENT}"/>'
          f'<rect x="1650" y="854" width="140" height="42" fill="{Wn}"/><rect x="1806" y="852" width="46" height="48" fill="{R}"/>'
          # Luke's Diner in Gilmore Girls is in the old Williams Hardware
          # building, and the old lettering is still on the window
          + text("WILLIAMS", "oswald", 500, 11, 1720, 869, ICON, 3)
          + text("HARDWARE", "oswald", 600, 16, 1720, 887, ICON, 2))
    return s + street(p, season)

def town_b(p, season):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    RED, GOLD, BLUE = "#B5523F", "#F6C46A", "#4A82A8"
    # Church: bell tower with a spire and a cross, and a nave with stained glass windows
    s = (f'<rect x="166" y="760" width="264" height="140" fill="{A}"/>'
         f'<polygon points="156,762 300,692 440,762" fill="{R}"/>'
         f'<rect x="70" y="690" width="100" height="210" fill="{A}"/>'
         + snow_ridge(season, p, (160, 759), (300, 689), (436, 759)) +
         f'<polygon points="62,692 120,590 178,692" fill="{R}"/>'
         + snow_ridge(season, p, (66, 689), (120, 594), (174, 689)) +
         f'<rect x="116" y="556" width="8" height="38" fill="{R}"/><rect x="106" y="566" width="28" height="8" fill="{R}"/>'
         + arch(100, 708, 40, 56, R) +
         f'<g stroke="{A}" stroke-width="3"><line x1="104" y1="738" x2="136" y2="738"/><line x1="104" y1="750" x2="136" y2="750"/></g>'
         f'<circle cx="120" cy="790" r="13" fill="{GOLD}"/><circle cx="120" cy="790" r="6" fill="{RED}"/>'
         + arch(98, 826, 44, 74, R))
    s += sign(196, 768, 204, 30, R, "New City", "alegreya", 400, 22, 790, 2)
    for wx in (196, 280, 364):
        s += (arch(wx, 806, 36, 66, BLUE) + f'<rect x="{wx+12}" y="826" width="12" height="46" fill="{RED}"/>'
              f'<circle cx="{wx+18}" cy="822" r="7" fill="{GOLD}"/>'
              f'<g stroke="{R}" stroke-width="2"><line x1="{wx}" y1="846" x2="{wx+36}" y2="846"/><line x1="{wx}" y1="860" x2="{wx+36}" y2="860"/></g>')
    s += f'<rect x="60" y="892" width="120" height="8" fill="{p["curb"]}"/>'
    # Gas station: price sign, canopy over one pump, and a small Kroger store.
    # The parked car is added by MainScene.brs so it can change each time.
    # Price sign: $2.05 with a small 9 at the top right for the 9/10 of a cent
    priceW = text_width("$2.05", "oswald", 500, 22, 1)
    nineW = text_width("9", "oswald", 500, 11)
    priceX = 484 - (priceW + 2 + nineW) / 2
    s += (f'<rect x="480" y="746" width="8" height="154" fill="{W2}"/>'
          f'<rect x="448" y="690" width="72" height="62" rx="4" fill="{R}"/>'
          + text("GAS", "oswald", 700, 20, 484, 714, ACCENT, 2)
          + text("$2.05", "oswald", 500, 22, priceX + priceW / 2, 742, "#F8FAFC", 1)
          + text("9", "oswald", 500, 11, priceX + priceW + 2 + nineW / 2, 731, "#F8FAFC") +
          f'<rect x="556" y="772" width="12" height="128" fill="{W2}"/><rect x="912" y="772" width="12" height="128" fill="{W2}"/>'
          f'<rect x="520" y="740" width="440" height="34" fill="{R}"/><rect x="520" y="766" width="440" height="8" fill="{ACCENT}"/>'
          + snow_flat(season, p, 520, 740, 440) + snow_flat(season, p, 448, 690, 72)
          + text("FUEL STOP", "oswald", 600, 22, 740, 762, "#F8FAFC", 5) +
          f'<rect x="578" y="886" width="62" height="14" fill="{p["curb"]}"/>'
          f'<rect x="588" y="812" width="40" height="76" fill="{B}"/><rect x="588" y="812" width="40" height="10" fill="{ACCENT}"/>'
          f'<rect x="594" y="828" width="28" height="18" fill="{Wn}"/>'
          f'<path d="M628,836 Q646,840 642,870" stroke="#1F2A33" stroke-width="4" fill="none"/>'
          f'<rect x="980" y="770" width="200" height="130" fill="{wall(STORE_COLORS["kroger"], p)}"/><rect x="976" y="770" width="208" height="14" fill="{R}"/>'
          + snow_flat(season, p, 976, 770, 208)
          + sign(1006, 792, 148, 36, "#1F4E9C", "Kroger", "oswald", 600, 22, 818, 2) +
          f'<rect x="996" y="842" width="96" height="50" fill="{Wn}"/><rect x="1110" y="836" width="46" height="64" fill="{R}"/>')
    # Hill Valley Courthouse Mall from Back to the Future: stone front with
    # columns and steps, and a clock tower stopped at 10:04
    cx, cy, cr = 1500, 636, 28
    clock = f'<circle cx="{cx}" cy="{cy}" r="{cr}" fill="{p["clockFace"]}" stroke="{R}" stroke-width="3"/>'
    for i in range(12):
        a = math.radians(i * 30)
        r1 = cr - (7 if i % 3 == 0 else 5)
        clock += (f'<line x1="{cx + r1 * math.sin(a):.1f}" y1="{cy - r1 * math.cos(a):.1f}" '
                  f'x2="{cx + (cr - 3) * math.sin(a):.1f}" y2="{cy - (cr - 3) * math.cos(a):.1f}" stroke="{R}" stroke-width="2"/>')
    for deg, length, width in (((10 + 4 / 60) * 30, 14, 4), (4 * 6, 21, 3)):
        a = math.radians(deg)
        clock += (f'<line x1="{cx}" y1="{cy}" x2="{cx + length * math.sin(a):.1f}" y2="{cy - length * math.cos(a):.1f}" '
                  f'stroke="{R}" stroke-width="{width}" stroke-linecap="round"/>')
    clock += f'<circle cx="{cx}" cy="{cy}" r="3" fill="{R}"/>'
    s += (f'<rect x="1456" y="600" width="88" height="112" fill="{A}"/>'
          f'<rect x="1448" y="592" width="104" height="10" fill="{W2}"/>'
          f'<rect x="1470" y="574" width="60" height="18" fill="{A}"/>'
          + arch(1478, 578, 12, 14, R) + arch(1494, 578, 12, 14, R) + arch(1510, 578, 12, 14, R) +
          f'<polygon points="1462,575 1500,552 1538,575" fill="{R}"/>'
          + snow_ridge(season, p, (1466, 572), (1500, 555), (1534, 572)) + snow_flat(season, p, 1448, 592, 104)
          + clock +
          f'<rect x="1250" y="888" width="500" height="12" fill="{p["curb"]}"/><rect x="1262" y="876" width="476" height="12" fill="{W2}"/>'
          f'<rect x="1280" y="730" width="440" height="146" fill="{A}"/>'
          f'<polygon points="1262,712 1500,672 1738,712" fill="{B}"/>'
          f'<polygon points="1300,706 1500,680 1700,706" fill="none" stroke="{W2}" stroke-width="4"/>'
          + snow_ridge(season, p, (1266, 709), (1456, 678)) + snow_ridge(season, p, (1544, 678), (1734, 709)) +
          f'<rect x="1270" y="708" width="460" height="24" fill="{W2}"/>'
          + text("HILL VALLEY COURTHOUSE MALL", "cinzel", 700, 18, 1500, 727, R, 2))
    for cx in (1320, 1392, 1464, 1536, 1608, 1680):
        s += (f'<rect x="{cx-11}" y="740" width="22" height="136" fill="{B}"/>'
              f'<rect x="{cx-15}" y="732" width="30" height="8" fill="{W2}"/><rect x="{cx-15}" y="868" width="30" height="8" fill="{W2}"/>')
    for wx in (1356, 1428, 1572, 1644):
        s += arch(wx - 15, 760, 30, 80, Wn)
    s += arch(1478, 796, 44, 80, R)
    s += pumpkins(season, 1540) + pumpkins(season, 160)
    # Trees
    s += round_tree(1820, 900, 64, 36, p, season) + round_tree(1207, 900, 54, 26, p, season)
    return s + street(p, season)

# Gray used for the icons in shop windows (the art palette and the camera)
ICON = "#6E7A85"

# Town section C: five houses and five shops. The houses are narrower than the
# ones in section A so all ten buildings fit in 1920 pixels.
def town_parts(p, season):
    """Building helpers shared by town sections C and D."""
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    def small_house(x, w, y, peak, number, font, weight):
        """A house. A house whose wall starts at y=700 or higher gets a second
        row of windows."""
        rows = [y + 18] + ([762] if y <= 700 else [])
        doorX = x + w // 2 - 20
        wins = "".join(f'<rect x="{x + 10}" y="{r}" width="40" height="38" fill="{Wn}"/><rect x="{x + w - 50}" y="{r}" width="40" height="38" fill="{Wn}"/>'
                       + flower_box(season, p, x + 10, r + 38, 40) + flower_box(season, p, x + w - 50, r + 38, 40) for r in rows)
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{900 - y}" fill="{wall(HOUSE_COLORS[number], p)}"/>'
                f'<polygon points="{x - 8},{y} {x + w // 2},{peak} {x + w + 8},{y}" fill="{R}"/>'
                + snow_ridge(season, p, (x - 6, y - 3), (x + w // 2, peak - 3), (x + w + 6, y - 3)) + wins +
                f'<rect x="{doorX}" y="830" width="40" height="70" fill="{R}"/>'
                f'<rect x="{doorX - 2}" y="808" width="44" height="18" rx="3" fill="{R}"/>'
                + text(number, font, weight, 14, doorX + 20, 822, "#F8FAFC", 1)
                + pumpkins(season, doorX + 50))

    def awning(x, w, colors):
        """A striped awning over a shop window, from y=800 to y=828."""
        n = len(colors) * 3
        out = ""
        for i in range(n):
            t0, t1 = x + 10 + (w - 20) * i / n, x + 10 + (w - 20) * (i + 1) / n
            b0, b1 = x + w * i / n, x + w * (i + 1) / n
            out += f'<polygon points="{t0:.1f},800 {t1:.1f},800 {b1:.1f},828 {b0:.1f},828" fill="{colors[i % len(colors)]}"/>'
        return out + snow_flat(season, p, x + 8, 800, w - 16)

    def shop(x, w, top, wall, upper=None):
        """Walls, roof edge, display window, and door. upper is the y of a row
        of two upper windows, or None. Returns the drawing and the display
        window's x, y, width, and height for what is inside it."""
        win = (x + 12, 838, w - 78, 56)
        up = "" if upper is None else (f'<rect x="{x + 24}" y="{upper}" width="42" height="38" fill="{Wn}"/>'
                                       f'<rect x="{x + w - 66}" y="{upper}" width="42" height="38" fill="{Wn}"/>')
        body = (f'<rect x="{x}" y="{top}" width="{w}" height="{900 - top}" fill="{wall}"/>' + up +
                f'<rect x="{x - 4}" y="{top}" width="{w + 8}" height="14" fill="{R}"/>' + snow_flat(season, p, x - 4, top, w + 8) +
                f'<rect x="{win[0]}" y="{win[1]}" width="{win[2]}" height="{win[3]}" fill="{Wn}"/>'
                f'<rect x="{x + w - 56}" y="834" width="42" height="66" fill="{R}"/>')
        return body, win

    return small_house, awning, shop

def town_c(p, season):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    small_house, awning, shop = town_parts(p, season)

    s = small_house(24, 150, 740, 676, "312", "raleway", 700)

    # Cabana's ice cream shop, with a big cone on the roof
    body, (wx, wy, ww, wh) = shop(192, 196, 716, wall(STORE_COLORS["cabanas"], p))
    s += (f'<polygon points="282,712 298,712 290,742" fill="#D9A55B"/><circle cx="284" cy="704" r="10" fill="#F2B8C6"/><circle cx="296" cy="704" r="10" fill="#B8E2C8"/>'
          f'<circle cx="290" cy="694" r="10" fill="#F6E7B0"/>' + body
          + sign(214, 742, 152, 46, "#E86A92", "Cabana\u2019s", "pacifico", 400, 26, 774, 0)
          + awning(192, 196, ["#E86A92", A]))
    for i, (cx, c1, c2) in enumerate(((wx + 22, "#F2B8C6", "#F6E7B0"), (wx + 58, "#B8E2C8", "#F2B8C6"), (wx + 94, "#F6E7B0", "#B8E2C8"))):
        s += (f'<polygon points="{cx - 8},{wy + 26} {cx + 8},{wy + 26} {cx},{wy + 50}" fill="#D9A55B"/>'
              f'<circle cx="{cx}" cy="{wy + 22}" r="9" fill="{c1}"/><circle cx="{cx}" cy="{wy + 12}" r="7" fill="{c2}"/>')

    s += small_house(406, 150, 680, 614, "402", "comfortaa", 700)

    # Art supply store. A small gray painter's palette and brush in the window,
    # drawn like an icon. The paint spots and thumb hole are cut out in the
    # window color.
    body, (wx, wy, ww, wh) = shop(574, 196, 652, wall(STORE_COLORS["art"], p), upper=676)
    px, py, k = wx + ww / 2 - 6, wy + wh / 2, 0.6
    def pt(dx, dy):
        return f"{px + dx * k:.1f},{py + dy * k:.1f}"
    s += (body + sign(596, 730, 152, 50, "#6B4A3A", "ART SUPPLIES", "amatic", 700, 32, 766, 2)
          + f'<polygon points="584,800 760,800 768,828 576,828" fill="{p["mid"]}"/>' + snow_flat(season, p, 584, 800, 176)
          + f'<path d="M{pt(-34, 0)} C{pt(-36, -22)} {pt(10, -26)} {pt(30, -14)} C{pt(42, -6)} {pt(30, 4)} {pt(20, 2)} '
            f'C{pt(8, 0)} {pt(8, 14)} {pt(16, 18)} C{pt(4, 26)} {pt(-30, 24)} {pt(-34, 0)} Z" fill="{ICON}"/>'
          + f'<circle cx="{px + 14 * k:.1f}" cy="{py + 8 * k:.1f}" r="{5 * k:.1f}" fill="{Wn}"/>')
    for dx, dy in ((-24, -2), (-14, -14), (2, -16), (18, -10), (-20, 12)):
        s += f'<circle cx="{px + dx * k:.1f}" cy="{py + dy * k:.1f}" r="{4.5 * k:.1f}" fill="{Wn}"/>'
    s += (f'<line x1="{px + 40 * k:.1f}" y1="{py + 22 * k:.1f}" x2="{px + 62 * k:.1f}" y2="{py - 20 * k:.1f}" stroke="{ICON}" stroke-width="3" stroke-linecap="round"/>'
          f'<path d="M{pt(60, -16)} L{pt(68, -28)} L{pt(64, -15)} Z" fill="{ICON}"/>')

    # Photography store. A small gray camera in the window, drawn like an icon.
    # The lens and flash are cut out in the window color.
    body, (wx, wy, ww, wh) = shop(788, 196, 712, wall(STORE_COLORS["photo"], p))
    cx, cy = wx + ww // 2, wy + wh // 2 + 2
    s += (body + sign(810, 736, 152, 46, "#1F2A33", "PHOTO", "montserrat", 700, 26, 768, 6)
          + f'<polygon points="798,800 974,800 982,828 790,828" fill="{R}"/>' + snow_flat(season, p, 798, 800, 176)
          + f'<rect x="{cx - 20}" y="{cy - 10}" width="40" height="24" rx="4" fill="{ICON}"/><rect x="{cx - 15}" y="{cy - 15}" width="11" height="6" rx="1.5" fill="{ICON}"/>'
            f'<rect x="{cx + 8}" y="{cy - 7}" width="8" height="4" rx="1" fill="{Wn}"/>'
            f'<circle cx="{cx}" cy="{cy + 2}" r="8" fill="{Wn}"/><circle cx="{cx}" cy="{cy + 2}" r="5" fill="{ICON}"/>')

    s += small_house(1002, 150, 745, 680, "527", "josefin", 600)

    # Pet shop. A fish bowl, a puppy, and a kitten in the window, and a paw
    # print on the sign.
    body, (wx, wy, ww, wh) = shop(1170, 196, 664, wall(STORE_COLORS["pet"], p), upper=684)
    s += (body + sign(1192, 734, 152, 46, "#4A82A8", "", "fredoka", 600, 22, 764)
          + text("PET SHOP", "fredoka", 600, 20, 1252, 763, "#F8FAFC", 2)
          + awning(1170, 196, ["#4A82A8", A]))
    qx, qy = 1325, 757
    s += f'<ellipse cx="{qx}" cy="{qy + 4}" rx="6" ry="5" fill="#F8FAFC"/>'
    for dx, dy in ((-7, -4), (-2.5, -8), (2.5, -8), (7, -4)):
        s += f'<ellipse cx="{qx + dx}" cy="{qy + dy}" rx="2.2" ry="3" fill="#F8FAFC"/>'
    # A small table across the window. The fish bowl and the animals sit on it.
    base = wy + wh - 12
    s += (f'<rect x="{wx + 4}" y="{base}" width="{ww - 8}" height="4" rx="1" fill="#8C5A3C"/>'
          f'<rect x="{wx + 10}" y="{base + 4}" width="4" height="{wy + wh - base - 4}" fill="#6B4A3A"/>'
          f'<rect x="{wx + ww - 14}" y="{base + 4}" width="4" height="{wy + wh - base - 4}" fill="#6B4A3A"/>')
    fx, fy = wx + 18, base - 14
    s += (f'<circle cx="{fx}" cy="{fy}" r="13" fill="#A9D4EC" fill-opacity="0.9"/><rect x="{fx - 8}" y="{fy - 15}" width="16" height="4" rx="2" fill="#A9D4EC"/>'
          f'<ellipse cx="{fx - 1}" cy="{fy + 1}" rx="5" ry="3" fill="#E8913A"/><polygon points="{fx + 3},{fy + 1} {fx + 8},{fy - 2} {fx + 8},{fy + 4}" fill="#E8913A"/>')
    # Puppy, sitting and facing right
    dx = wx + 56
    PUP, PUPD = "#B07A4A", "#7A4E2C"
    s += (f'<ellipse cx="{dx}" cy="{base - 9}" rx="10" ry="9" fill="{PUP}"/>'
          f'<path d="M{dx - 9},{base - 8} Q{dx - 17},{base - 14} {dx - 15},{base - 20}" stroke="{PUP}" stroke-width="3" fill="none" stroke-linecap="round"/>'
          f'<circle cx="{dx + 6}" cy="{base - 21}" r="8" fill="{PUP}"/><ellipse cx="{dx + 14}" cy="{base - 18}" rx="5" ry="3.5" fill="{PUP}"/>'
          f'<ellipse cx="{dx + 2}" cy="{base - 20}" rx="3" ry="6" fill="{PUPD}"/>'
          f'<circle cx="{dx + 9}" cy="{base - 23}" r="1.4" fill="#1F2A33"/><circle cx="{dx + 18}" cy="{base - 19}" r="1.6" fill="#1F2A33"/>'
          f'<rect x="{dx + 2}" y="{base - 6}" width="4" height="6" rx="1.5" fill="{PUP}"/><rect x="{dx + 7}" y="{base - 6}" width="4" height="6" rx="1.5" fill="{PUP}"/>')
    # Kitten, sitting and facing left, with its tail curled up
    kx = wx + 92
    KIT, KITD = "#E8913A", "#C8662E"
    s += (f'<path d="M{kx + 7},{base - 4} Q{kx + 18},{base - 6} {kx + 14},{base - 18}" stroke="{KIT}" stroke-width="3" fill="none" stroke-linecap="round"/>'
          f'<ellipse cx="{kx}" cy="{base - 8}" rx="8" ry="8" fill="{KIT}"/>'
          f'<circle cx="{kx - 3}" cy="{base - 19}" r="6.5" fill="{KIT}"/>'
          f'<polygon points="{kx - 9},{base - 22} {kx - 8},{base - 30} {kx - 3},{base - 25}" fill="{KIT}"/>'
          f'<polygon points="{kx - 1},{base - 25} {kx + 3},{base - 30} {kx + 3},{base - 21}" fill="{KIT}"/>'
          f'<path d="M{kx - 4},{base - 12} L{kx + 4},{base - 12}" stroke="{KITD}" stroke-width="2"/><path d="M{kx - 5},{base - 7} L{kx + 5},{base - 7}" stroke="{KITD}" stroke-width="2"/>'
          f'<circle cx="{kx - 6}" cy="{base - 20}" r="1.2" fill="#1F2A33"/><circle cx="{kx - 1}" cy="{base - 20}" r="1.2" fill="#1F2A33"/>')

    # Mama BreeBree's, an Italian restaurant, with an awning in the colors of
    # the Italian flag and a table with a checkered tablecloth in the window
    body, (wx, wy, ww, wh) = shop(1384, 216, 640, wall(STORE_COLORS["mama"], p), upper=666)
    s += (body + sign(1392, 726, 200, 50, "#2F5D3A", "Mama BreeBree\u2019s", "lora", 600, 21, 758, 0.5)
          + awning(1384, 216, ["#2F8F4E", A, "#C0392B"]))
    tx, ty = wx + 18, wy + 30
    for row in range(2):
        for col in range(8):
            c = "#C0392B" if (row + col) % 2 == 0 else "#F8FAFC"
            s += f'<rect x="{tx + col * 12}" y="{ty + row * 8}" width="12" height="8" fill="{c}"/>'
    s += (f'<rect x="{tx + 6}" y="{ty + 16}" width="4" height="10" fill="#6B4A3A"/><rect x="{tx + 86}" y="{ty + 16}" width="4" height="10" fill="#6B4A3A"/>'
          f'<rect x="{tx + 30}" y="{ty - 16}" width="7" height="16" rx="2" fill="#2F5D3A"/><rect x="{tx + 32}" y="{ty - 22}" width="3" height="7" fill="#2F5D3A"/>'
          f'<rect x="{tx + 58}" y="{ty - 10}" width="4" height="10" fill="#F8FAFC"/><ellipse cx="{tx + 60}" cy="{ty - 13}" rx="2" ry="3" fill="#F6C46A"/>')

    s += small_house(1618, 150, 690, 624, "612", "quicksand", 700)
    s += small_house(1786, 120, 750, 690, "1120", "bitter", 600)
    return s + street(p, season)

# Town section D: Holy Cross school, house 67, the ITS church, Chick-fil-A
# with its drive-through, Covenant school, and Cedarville, a university
# building in the style of the old library.
def town_d(p, season):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    small_house, awning, shop = town_parts(p, season)

    def school(x, w, color, name, font, weight, size, gable_top):
        """A two-story school with a center entrance. Returns the drawing and
        the x of the center of the entrance."""
        cx = x + w // 2
        ex0, ex1 = cx - 70, cx + 70
        out = (f'<rect x="{x}" y="700" width="{w}" height="200" fill="{color}"/>'
               f'<rect x="{x - 4}" y="700" width="{w + 8}" height="12" fill="{R}"/>' + snow_flat(season, p, x - 4, 700, w + 8))
        for wx in (x + 12, x + 44, ex1 + 8, ex1 + 40):
            for wy in (726, 784):
                out += f'<rect x="{wx}" y="{wy}" width="24" height="36" fill="{Wn}"/><rect x="{wx}" y="{wy + 17}" width="24" height="2" fill="{color}"/>'
        out += (f'<rect x="{ex0}" y="672" width="140" height="228" fill="{wall(HOUSE_COLORS["612"], p)}"/>'
                f'<polygon points="{ex0 - 6},672 {cx},{gable_top} {ex1 + 6},672" fill="{R}"/>'
                + snow_ridge(season, p, (ex0 - 4, 669), (cx, gable_top - 3), (ex1 + 4, 669))
                + sign(ex0 + 8, 690, 124, 30, R, name, font, weight, size, 711, 1) +
                f'<rect x="{ex0 + 26}" y="734" width="36" height="40" fill="{Wn}"/><rect x="{ex1 - 62}" y="734" width="36" height="40" fill="{Wn}"/>'
                + arch(cx - 28, 820, 56, 80, R) + f'<rect x="{cx - 1}" y="836" width="2" height="64" fill="{color}"/>'
                f'<rect x="{ex0 - 6}" y="892" width="152" height="8" fill="{p["curb"]}"/>')
        return out, cx

    # Holy Cross school, with a cross over the entrance
    body, cx = school(20, 300, wall(STORE_COLORS["holycross"], p), "HOLY CROSS", "playfair", 700, 15, 636)
    s = body + f'<rect x="{cx - 3}" y="602" width="6" height="36" fill="{R}"/><rect x="{cx - 11}" y="612" width="22" height="6" fill="{R}"/>'

    s += small_house(338, 150, 720, 656, "67", "montserrat", 700)

    # The ITS church: a stone church with a square bell tower and pointed windows
    C = wall(STORE_COLORS["its"], p)
    s += (f'<rect x="566" y="740" width="190" height="160" fill="{C}"/>'
          f'<polygon points="558,742 661,690 764,742" fill="{R}"/>' + snow_ridge(season, p, (562, 739), (661, 687), (760, 739)) +
          f'<rect x="508" y="640" width="64" height="260" fill="{C}"/>'
          f'<polygon points="502,642 540,596 578,642" fill="{R}"/>' + snow_ridge(season, p, (506, 639), (540, 599), (574, 639)) +
          f'<rect x="537" y="570" width="6" height="30" fill="{R}"/><rect x="530" y="578" width="20" height="6" fill="{R}"/>'
          f'<path d="M526,700 L526,676 L540,660 L554,676 L554,700 Z" fill="{R}"/>'
          f'<path d="M524,900 L524,846 L540,826 L556,846 L556,900 Z" fill="{R}"/>'
          + sign(600, 752, 122, 34, R, "ITS", "cinzel", 700, 24, 778, 6))
    for wx in (590, 646, 702):
        s += (f'<path d="M{wx},874 L{wx},816 L{wx + 13},798 L{wx + 26},816 L{wx + 26},874 Z" fill="#4A82A8"/>'
              f'<rect x="{wx + 11}" y="812" width="4" height="62" fill="#F6C46A"/><rect x="{wx}" y="842" width="26" height="3" fill="{R}"/>')

    # Chick-fil-A: a red roof with the name on it, big windows, and a
    # drive-through window on the right side
    RED = "#D62E3C"
    CW = wall(STORE_COLORS["chick"], p)
    s += (f'<rect x="784" y="752" width="256" height="148" fill="{CW}"/>'
          f'<polygon points="776,754 1048,754 1032,708 792,708" fill="{RED}"/>' + snow_flat(season, p, 792, 708, 240)
          + text("Chick-fil-A", "script", 700, 34, 912, 744, "#F8FAFC") +
          f'<rect x="800" y="790" width="70" height="80" fill="{Wn}"/><rect x="882" y="790" width="70" height="80" fill="{Wn}"/>'
          f'<rect x="834" y="790" width="2" height="80" fill="{CW}"/><rect x="916" y="790" width="2" height="80" fill="{CW}"/>'
          f'<rect x="964" y="830" width="34" height="70" fill="{R}"/>'
          # Drive-through window with a small awning, on the right end of the building
          f'<rect x="1006" y="806" width="28" height="40" fill="{Wn}"/><rect x="1002" y="798" width="36" height="8" fill="{RED}"/>'
          + snow_flat(season, p, 1002, 798, 36) +
          f'<rect x="1054" y="770" width="4" height="130" fill="{R}"/><polygon points="1046,766 1094,766 1094,786 1046,786" fill="{RED}"/>'
          + text("DRIVE THRU", "oswald", 600, 9, 1070, 780, "#F8FAFC", 0.5))

    # Covenant school, with a small bell tower
    body, cx = school(1150, 300, wall(STORE_COLORS["covenant"], p), "COVENANT", "raleway", 800, 15, 646)
    s += (body + f'<rect x="{cx - 14}" y="620" width="28" height="30" fill="{wall(HOUSE_COLORS["612"], p)}"/>'
          f'<path d="M{cx - 8},650 L{cx - 8},634 A8,8 0 0 1 {cx + 8},634 L{cx + 8},650 Z" fill="{R}"/>'
          f'<polygon points="{cx - 18},622 {cx},600 {cx + 18},622" fill="{R}"/>' + snow_ridge(season, p, (cx - 16, 620), (cx, 603), (cx + 16, 620)))

    # Cedarville: stone front with columns, steps, and the name in blue and
    # yellow letters in a letterman (college jersey) style
    s += (f'<rect x="1490" y="888" width="410" height="12" fill="{p["curb"]}"/><rect x="1500" y="876" width="390" height="12" fill="{W2}"/>'
          f'<rect x="1514" y="744" width="362" height="132" fill="{A}"/>'
          f'<polygon points="1498,728 1695,684 1892,728" fill="{B}"/>'
          f'<polygon points="1530,722 1695,692 1860,722" fill="none" stroke="{W2}" stroke-width="4"/>'
          + snow_ridge(season, p, (1502, 725), (1695, 687), (1888, 725)) +
          f'<rect x="1504" y="724" width="382" height="26" fill="{W2}"/>'
          + text("CEDARVILLE", "graduate", 400, 21, 1695, 745, "#F6C445", 2, "#1F4E9C", 2))
    for cx in (1546, 1608, 1670, 1720, 1782, 1844):
        s += (f'<rect x="{cx - 10}" y="756" width="20" height="120" fill="{B}"/>'
              f'<rect x="{cx - 14}" y="750" width="28" height="7" fill="{W2}"/><rect x="{cx - 14}" y="869" width="28" height="7" fill="{W2}"/>')
    for wx in (1577, 1639, 1751, 1813):
        s += arch(wx - 13, 776, 26, 74, Wn)
    s += arch(1676, 806, 38, 70, R) + pumpkins(season, 1630, 876)
    return s + street(p, season)

def sky(p):
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/>'
            f'<stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

# Layer crops: name -> (function, y, height)
CROPS = {"clouds": (clouds, 90, 255), "far": (far, 295, 425), "far_b": (far_b, 295, 425),
         "near": (near, 400, 360), "near_b": (near_b, 400, 360),
         "hills": (hills, 600, 310), "town_a": (town, 550, 530), "town_b": (town_b, 550, 530),
         "town_c": (town_c, 550, 530),
         "town_d": (town_d, 550, 530)}
# Remove old scenery images so a layer that gains seasons does not leave
# unused files behind in the Roku zip.
for f in os.listdir(OUT):
    if f.split("_")[0] in ("clouds", "far", "near", "hills", "town", "sky") and f.endswith(".png"):
        os.remove(os.path.join(OUT, f))
for pal in P:
    save(sky(P[pal]), "0 0 8 1080", 8, 1080, f"sky_{pal}.png")
    for name, (fn, y, h) in CROPS.items():
        seasons = SEASONAL.get(name, [])
        for season in seasons:
            save(fn(season_palette(pal, season), season), f"0 {y} 1920 {h}", 1920, h, f"{name}_{season}_{pal}.png")
        if len(seasons) < len(SEASONS):
            save(fn(P[pal], "summer"), f"0 {y} 1920 {h}", 1920, h, f"{name}_{pal}.png")

random.seed(7)
stars = "".join(f'<circle cx="{random.randint(10,1910)}" cy="{random.randint(10,390)}" r="{random.choice([1.5,2,2.5])}" fill="#F8FAFC"/>' for _ in range(70))
save(stars, "0 0 1920 400", 1920, 400, "stars.png")
save(f'<circle cx="70" cy="70" r="64" fill="{ACCENT}"/>', "0 0 140 140", 140, 140, "sun.png")
save('<circle cx="70" cy="70" r="64" fill="#ECEFF3"/><circle cx="50" cy="58" r="12" fill="#D9E2EA"/><circle cx="88" cy="90" r="9" fill="#D9E2EA"/><circle cx="92" cy="48" r="6" fill="#D9E2EA"/>',
     "0 0 140 140", 140, 140, "moon.png")

# Rain and snow tiles, 960x540, wrap vertically so they loop without a seam
def wrap(make, n):
    out = ""
    for _ in range(n):
        x, y = random.randint(0, 960), random.randint(0, 540)
        for dy in (-540, 0, 540):
            out += make(x, y + dy)
    return out
rain = wrap(lambda x, y: f'<line x1="{x}" y1="{y}" x2="{x-5}" y2="{y+26}" stroke="#C9DAEA" stroke-opacity="0.55" stroke-width="2" stroke-linecap="round"/>', 150)
save(rain, "0 0 960 540", 960, 540, "rain.png")
snow = wrap(lambda x, y: f'<circle cx="{x}" cy="{y}" r="{random.choice([2,2.5,3,3.5])}" fill="#FFFFFF" fill-opacity="0.85"/>', 170)
save(snow, "0 0 960 540", 960, 540, "snow.png")

# Season effects. Falling leaves use the same 960x540 wrapping tile as rain
# and snow. Fireflies are two 960x200 images that fade in and out in turn.
def leaf(x, y):
    c = random.choice(["#D9822B", "#B5523F", "#E0B040", "#C8662E"])
    return f'<ellipse cx="{x}" cy="{y}" rx="7" ry="3.5" fill="{c}" transform="rotate({random.randint(0, 180)} {x} {y})"/>'
save(wrap(leaf, 28), "0 0 960 540", 960, 540, "leaves.png")
for n in ("a", "b"):
    flies = ""
    for _ in range(16):
        x, y = random.randint(10, 950), random.randint(10, 190)
        flies += f'<circle cx="{x}" cy="{y}" r="6" fill="#F6E7B0" fill-opacity="0.25"/><circle cx="{x}" cy="{y}" r="2.2" fill="#F6E7B0"/>'
    save(flies, "0 0 960 200", 960, 200, f"fireflies_{n}.png")
# Fog: an 8 px wide gradient, stretched across the screen like the sky
save('<defs><linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0.3" stop-color="#E3E9EE" stop-opacity="0"/>'
     '<stop offset="0.62" stop-color="#E3E9EE" stop-opacity="0.75"/><stop offset="1" stop-color="#E3E9EE" stop-opacity="0.5"/></linearGradient></defs>'
     '<rect width="8" height="1080" fill="url(#f)"/>', "0 0 8 1080", 8, 1080, "fog.png")

# Cessna airplane for the sky. It is drawn at twice the size it is shown
# (112x44 for a 56x22 poster) so its edges stay smooth. left=True draws it
# facing left. Planes have a red light on the left wingtip and a green light on
# the right wingtip. A plane flying to the right shows its right side to the
# viewer, so the near light is green; flying to the left, it is red. For this
# reason the left image is drawn again instead of mirrored. The lights show at dusk and
# night. The white strobe on the tail is a separate image that blinks.
def cessna(pal, left):
    p = P[pal]
    body, stripe = p["houseA"], p["roof"]
    s = (f'<polygon points="8,24 6,4 16,4 28,22" fill="{body}"/>'
         f'<ellipse cx="17" cy="24" rx="11" ry="2.5" fill="{stripe}"/>'
         f'<path d="M8,26 L24,21 L62,18 Q82,15 94,18 L104,22 Q108,25 104,28 L90,31 L40,31 Z" fill="{body}"/>'
         f'<path d="M14,27 L100,26" stroke="{stripe}" stroke-width="2.5"/>'
         f'<rect x="46" y="14" width="44" height="6" rx="2" fill="{body}"/>'
         f'<line x1="62" y1="19" x2="70" y2="29" stroke="{stripe}" stroke-width="1.5"/>'
         f'<polygon points="72,19 88,19 96,23 72,23" fill="{"#C9DAEA" if pal == "day" else stripe}"/>'
         f'<line x1="74" y1="31" x2="72" y2="37" stroke="{stripe}" stroke-width="2"/><line x1="96" y1="29" x2="97" y2="37" stroke="{stripe}" stroke-width="2"/>'
         f'<circle cx="72" cy="38" r="3" fill="#1F2A33"/><circle cx="97" cy="38" r="3" fill="#1F2A33"/>'
         '<ellipse cx="108" cy="24" rx="1.5" ry="10" fill="#9DB6C9" fill-opacity="0.6"/>')
    if pal != "day":
        light = "#E74C3C" if left else "#2ECC71"
        if pal == "night":
            # Brighter at night: a wider glow and a light center
            s += (f'<circle cx="48" cy="16" r="11" fill="{light}" fill-opacity="0.25"/><circle cx="48" cy="16" r="7" fill="{light}" fill-opacity="0.5"/>'
                  f'<circle cx="48" cy="16" r="4" fill="{light}"/><circle cx="48" cy="16" r="1.8" fill="#FFFFFF" fill-opacity="0.8"/>')
        else:
            s += f'<circle cx="48" cy="16" r="3" fill="{light}"/><circle cx="48" cy="16" r="6" fill="{light}" fill-opacity="0.3"/>'
    if left:
        s = f'<g transform="translate(112,0) scale(-1,1)">{s}</g>'
    return s
for pal in P:
    save(cessna(pal, False), "0 0 112 44", 112, 44, f"plane_{pal}.png")
    save(cessna(pal, True), "0 0 112 44", 112, 44, f"plane_left_{pal}.png")
save('<circle cx="8" cy="8" r="7" fill="#FFFFFF" fill-opacity="0.35"/><circle cx="8" cy="8" r="3" fill="#FFFFFF"/>', "0 0 16 16", 16, 16, "plane_strobe.png")
# A larger, brighter flash for night, shown at 16x16 instead of 8x8
save('<circle cx="16" cy="16" r="15" fill="#FFFFFF" fill-opacity="0.18"/><circle cx="16" cy="16" r="9" fill="#FFFFFF" fill-opacity="0.4"/>'
     '<circle cx="16" cy="16" r="4.5" fill="#FFFFFF"/>', "0 0 32 32", 32, 32, "plane_strobe_night.png")

# Wheel (drawn separately so it can spin)
save('<circle cx="32" cy="32" r="32" fill="#1F2A33"/><circle cx="32" cy="32" r="18" fill="#C9D2DA"/>'
     '<g stroke="#5B6770" stroke-width="4"><line x1="32" y1="16" x2="32" y2="48"/><line x1="16" y1="32" x2="48" y2="32"/></g>'
     '<circle cx="32" cy="32" r="6" fill="#5B6770"/>', "0 0 64 64", 64, 64, "wheel.png")

GLASS, DARK = "#C9DAEA", "#1F2A33"
def wells(pts, r):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{DARK}"/>' for x, y in pts)

# The roof is toward the back and the windshield slopes a long way forward, so
# the front (right side) is easy to see.
sedan = (f'<path fill="#4A82A8" d="M6,72 L6,56 Q8,40 30,38 L70,36 L90,10 Q94,6 104,6 L156,6 Q166,6 174,12 L236,38 L262,40 Q276,42 276,56 L276,72 Q276,80 268,80 L14,80 Q6,80 6,72 Z"/>'
         f'<polygon points="80,36 98,12 136,12 136,36" fill="{GLASS}"/><polygon points="142,12 168,12 222,36 142,36" fill="{GLASS}"/>'
         '<line x1="139" y1="38" x2="139" y2="76" stroke="#34495E" stroke-width="2"/>'
         '<rect x="266" y="46" width="10" height="8" fill="#F6C46A"/><rect x="6" y="46" width="8" height="10" fill="#C0392B"/>'
         + wells([(62, 80), (218, 80)], 26))
save(sedan, "0 0 280 104", 280, 104, "car_sedan.png")

van = ('<path fill="#F2F4F6" d="M6,24 Q6,10 20,10 L222,10 Q232,10 240,18 L288,64 Q302,70 302,84 L302,100 Q302,106 296,106 L12,106 Q6,106 6,100 Z"/>'
       '<rect x="6" y="78" width="296" height="8" fill="#4A82A8"/>'
       f'<polygon points="236,22 282,64 236,64" fill="{GLASS}"/>'
       f'<rect x="20" y="22" width="60" height="36" rx="4" fill="{GLASS}"/><rect x="90" y="22" width="60" height="36" rx="4" fill="{GLASS}"/><rect x="160" y="22" width="66" height="36" rx="4" fill="{GLASS}"/>'
       '<line x1="156" y1="20" x2="156" y2="100" stroke="#B7C4CF" stroke-width="2"/>'
       '<rect x="292" y="72" width="10" height="10" fill="#F6C46A"/><rect x="6" y="60" width="6" height="14" fill="#C0392B"/>'
       + wells([(66, 104), (246, 104)], 28))
save(van, "0 0 310 130", 310, 130, "car_van.png")

OL, OLD = "#6B7B3A", "#4A5528"
jeep = (f'<circle cx="22" cy="80" r="22" fill="{DARK}"/><circle cx="22" cy="80" r="9" fill="#5B6770"/>'
        f'<path fill="{OL}" d="M20,62 L186,62 L194,52 L256,58 Q262,60 262,68 L262,100 Q262,106 256,106 L26,106 Q20,106 20,100 Z"/>'
        f'<path d="M105,62 L105,24 L190,18" stroke="{OLD}" stroke-width="7" fill="none" stroke-linejoin="round"/>'
        f'<polygon points="180,62 188,62 198,16 191,14" fill="{OLD}"/>'
        f'<rect x="120" y="42" width="28" height="22" rx="3" fill="{OLD}"/>'
        f'<circle cx="257" cy="76" r="6" fill="#F6C46A"/>'
        + wells([(68, 108), (214, 108)], 33) +
        f'<path d="M30,108 A38,38 0 0 1 106,108" stroke="{OLD}" stroke-width="9" fill="none"/>'
        f'<path d="M176,108 A38,38 0 0 1 252,108" stroke="{OLD}" stroke-width="9" fill="none"/>')
save(jeep, "0 0 270 140", 270, 140, "car_jeep.png")

TR, TRD = "#B5523F", "#8C3B2E"
truck = (f'<rect x="8" y="50" width="112" height="46" rx="4" fill="{TR}"/>'
         f'<path fill="{TR}" d="M120,96 L120,22 Q120,8 136,8 L170,8 Q184,8 186,22 L190,48 L190,96 Z"/>'
         f'<rect x="132" y="18" width="44" height="28" rx="6" fill="{GLASS}"/>'
         f'<path fill="{TR}" d="M188,48 L264,54 Q278,56 280,68 L282,96 L188,96 Z"/>'
         + wells([(70, 104), (238, 104)], 27) +
         f'<path fill="{TRD}" d="M28,106 A42,36 0 0 1 112,106 Z" fill-rule="evenodd"/>'
         f'<path fill="{TRD}" d="M196,106 A42,36 0 0 1 280,106 Z"/>'
         f'<rect x="106" y="98" width="94" height="6" fill="{TRD}"/>'
         '<circle cx="272" cy="70" r="9" fill="#C9D2DA"/><circle cx="272" cy="70" r="6" fill="#F6E7B0"/>'
         '<rect x="276" y="92" width="16" height="8" rx="3" fill="#C9D2DA"/><rect x="2" y="88" width="10" height="8" rx="3" fill="#C9D2DA"/>')
save(truck, "0 0 300 130", 300, 130, "car_truck.png")

# Sports car in the style of a Bugatti: low and long, two-tone blue, a curved
# line on the side, and a horseshoe-shaped grille at the front
SP, SPD, CHROME = "#2C6BB3", "#16294A", "#C9D2DA"
# The roof peak is toward the back and the windshield is long and low, so the
# front (right side) is easy to see. The hood is lower than the rear deck.
# The body is moved down 16 px so it sits close to the ground.
sports = ('<g transform="translate(0,16)">'
          f'<path fill="{SP}" d="M8,72 L8,46 Q10,40 24,38 L84,36 Q108,22 142,20 Q170,20 196,30 L252,46 L284,52 Q296,55 296,64 L296,72 Q296,80 288,80 L16,80 Q8,80 8,72 Z"/>'
          f'<path fill="{SPD}" d="M134,21 Q170,20 196,30 L252,46 L284,52 Q296,55 296,64 L296,72 Q296,80 288,80 L160,80 Q132,80 130,60 Q128,38 134,21 Z"/>'
          f'<path fill="{GLASS}" d="M100,38 Q120,27 142,26 Q166,26 192,34 L236,47 L104,44 Z"/>'
          f'<path d="M136,22 Q128,42 130,60 Q132,76 152,78" stroke="{CHROME}" stroke-width="4" fill="none" stroke-linecap="round"/>'
          f'<path fill="{DARK}" d="M100,54 L118,51 L120,64 L102,64 Z"/>'
          f'<path d="M290,58 Q296,58 296,64 Q296,70 290,70" stroke="{CHROME}" stroke-width="3" fill="{DARK}"/>'
          '<rect x="266" y="55" width="18" height="4" rx="2" fill="#F6C46A"/><rect x="8" y="44" width="14" height="4" fill="#C0392B"/></g>'
          + wells([(64, 84), (234, 84)], 22))
save(sports, "0 0 304 104", 304, 104, "car_sports.png")

# VW dune buggy: an open body with round fenders over the wheels, a green arch
# over the seats, and the engine showing at the back
BG, BGD = "#8BC34A", "#5E8F2E"
buggy = (f'<path d="M8,74 L8,62 Q10,54 22,52 L66,52 L70,58 L178,58 Q226,58 240,70 L242,80 L10,80 Z" fill="{BG}"/>'
         f'<path d="M14,84 A38,38 0 0 1 90,84 L82,84 A30,30 0 0 0 22,84 Z" fill="{BGD}"/>'
         f'<path d="M160,84 A38,38 0 0 1 236,84 L228,84 A30,30 0 0 0 168,84 Z" fill="{BGD}"/>'
         # A green arch over the seats, in the same color and thickness as the
         # fenders. Its ends sit on the top middle of each fender (x=52 and
         # x=198, the wheel centers).
         f'<path d="M48,50 A77,46 0 0 1 202,50 L194,50 A69,38 0 0 0 56,50 Z" fill="{BGD}"/>'
         f'<rect x="112" y="36" width="12" height="22" rx="3" fill="#34495E"/>'
         f'<rect x="4" y="54" width="18" height="16" rx="3" fill="#5B6770"/><rect x="0" y="66" width="10" height="4" rx="2" fill="#9CA6B1"/>'
         f'<circle cx="214" cy="56" r="6" fill="#F6C46A"/><rect x="8" y="62" width="6" height="8" fill="#C0392B"/>'
         + wells([(52, 84), (198, 84)], 28))
save(buggy, "0 0 250 112", 250, 112, "car_buggy.png")

# Animals that sit on the sidewalk. MainScene.brs places them at random spots
# when the screensaver starts. They are drawn larger than they are shown
# (42x45 for cats and 45x28 for guinea pigs) so their edges stay smooth. They
# are shown a little larger than their real size next to the cars, so they
# are easy to see.
def cat(body, dark, eyes, stripes=False):
    s = (f'<path d="M7,30 Q-1,28 2,18" stroke="{body}" stroke-width="3" fill="none" stroke-linecap="round"/>'
         f'<ellipse cx="13" cy="23" rx="9" ry="8" fill="{body}"/>'
         f'<circle cx="20" cy="12" r="6.5" fill="{body}"/>'
         f'<polygon points="15,9 16,1 20,6" fill="{body}"/><polygon points="21,6 25,1 26,9" fill="{body}"/>'
         f'<rect x="15" y="27" width="3.5" height="5" rx="1.5" fill="{body}"/><rect x="20" y="27" width="3.5" height="5" rx="1.5" fill="{body}"/>'
         f'<circle cx="18" cy="11" r="1.3" fill="{eyes}"/><circle cx="23" cy="11" r="1.3" fill="{eyes}"/>')
    if stripes:
        s += "".join(f'<path d="M{x},16 Q{x + 2},23 {x},29" stroke="{dark}" stroke-width="2" fill="none"/>' for x in (8, 12, 16))
        s += "".join(f'<line x1="{x}" y1="6.5" x2="{x}" y2="9" stroke="{dark}" stroke-width="1"/>' for x in (18.5, 20.5, 22.5))
    return f'<g transform="scale(2)">{s}</g>'
save(cat("#22272B", "#22272B", "#F6C46A"), "0 0 60 64", 60, 64, "cat_black.png")
save(cat("#5F676E", "#3E444A", "#15181B", True), "0 0 60 64", 60, 64, "cat_gray.png")
save(cat("#9A6B42", "#2B2118", "#F6C46A", True), "0 0 60 64", 60, 64, "cat_tabby.png")

def guinea_pig(body, spots):
    s = (f'<ellipse cx="15" cy="12" rx="13" ry="7.5" fill="{body}"/>'
         + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}"/>' for x, y, rx, ry, c in spots) +
         f'<ellipse cx="25" cy="12" rx="6" ry="5.5" fill="{body}"/>'
         + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}"/>' for x, y, rx, ry, c in spots if x > 21) +
         '<ellipse cx="22" cy="7" rx="2.5" ry="2" fill="#C88A6E"/><circle cx="26.5" cy="10.5" r="1.2" fill="#1F2A33"/>'
         '<circle cx="30" cy="13" r="0.9" fill="#C88A6E"/>'
         f'<rect x="8" y="17" width="3" height="3" rx="1" fill="#C88A6E"/><rect x="20" y="17" width="3" height="3" rx="1" fill="#C88A6E"/>')
    return f'<g transform="scale(2)">{s}</g>'
save(guinea_pig("#E8913A", [(7, 11, 7, 6, "#22272B"), (16, 8, 4, 3, "#22272B"), (26, 10, 3, 3.5, "#22272B")]), "0 0 64 40", 64, 40, "guinea_black_orange.png")
save(guinea_pig("#F8FAFC", [(8, 10, 4, 3.5, "#E8913A"), (16, 14, 3.5, 2.5, "#E8913A"), (13, 7, 2.5, 2, "#E8913A"), (26, 9, 2.5, 2.5, "#E8913A")]), "0 0 64 40", 64, 40, "guinea_white_orange.png")

# Channel icons from a composite of the day scene
def composite(pal, tile="a", season="summer"):
    p = season_palette(pal, season)
    townFn = {"a": town, "b": town_b, "c": town_c, "d": town_d}[tile]
    mtn = season if season == "winter" else "summer"
    full = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/><stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#g)"/><circle cx="220" cy="180" r="64" fill="{ACCENT}"/>'
            + clouds(p, season) + far(p, mtn) + near(p, mtn) + hills(p, season) + townFn(p, season))
    path = os.path.join(BUILD, f"composite_{season}_{pal}_{tile}.png")
    cairosvg.svg2png(bytestring=svg(full, "0 0 1920 1080", 1920, 1080).encode(), write_to=path)
    return path
im = Image.open(composite("day")).convert("RGB")
crop = im.crop((240, 0, 1680, 1080))
crop.resize((290, 218), Image.LANCZOS).save(os.path.join(OUT, "icon_hd.png"))
crop.resize((540, 405), Image.LANCZOS).save(os.path.join(OUT, "icon_fhd.png"))
for f in os.listdir(BUILD):
    os.remove(os.path.join(BUILD, f)) if f.startswith("composite_") else None
for season in SEASONS:
    for pal in ("day", "night"):
        for tile in ("a", "b", "c", "d"):
            composite(pal, tile, season)

# Mirrored car bodies for the far lane, where cars drive right to left
for n in ["sedan", "van", "jeep", "truck", "sports", "buggy"]:
    ImageOps.mirror(Image.open(os.path.join(OUT, f"car_{n}.png"))).save(os.path.join(OUT, f"car_{n}_left.png"))

# Add a parked car to the tile B previews to check its position. These numbers
# copy parkCar() and m.carDefs in components/MainScene.brs.
def park_preview(pal, name, w, h, wheels, r, bottom):
    path = os.path.join(BUILD, f"composite_summer_{pal}_b.png")
    im = Image.open(path).convert("RGBA")
    car = Image.new("RGBA", (w, h))
    car.alpha_composite(Image.open(os.path.join(OUT, f"car_{name}.png")).convert("RGBA").resize((w, h)))
    wheel = Image.open(os.path.join(OUT, "wheel.png")).convert("RGBA").resize((r * 2, r * 2))
    for wx, wy in wheels:
        car.alpha_composite(wheel, (wx - r, wy - r))
    s = 0.78
    car = car.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im.alpha_composite(car, (round(780 - w * s / 2), round(898 - bottom * s)))
    im.save(path)
park_preview("day", "van", 310, 130, [(66, 104), (246, 104)], 24, 128)
park_preview("night", "sedan", 280, 104, [(62, 80), (218, 80)], 22, 102)

# ---------- README previews ----------
# Images for README.md, written to docs/. Each shows a 1920 px wide part of the
# 3840 px street, starting at x (0 is town section A, 1920 is section B), with
# the clock panel and a few cars, so it looks like the real screen. docs/ is not part of
# the Roku zip. The car sizes copy m.carDefs in components/MainScene.brs.
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)
CARS = {"sedan": (280, 104, [(62, 80), (218, 80)], 22, 102), "van": (310, 130, [(66, 104), (246, 104)], 24, 128),
        "jeep": (270, 140, [(68, 108), (214, 108)], 28, 136), "truck": (300, 130, [(70, 104), (238, 104)], 24, 128),
        "sports": (304, 104, [(64, 84), (234, 84)], 18, 102), "buggy": (250, 112, [(52, 84), (198, 84)], 26, 110)}

def car_sprite(name, left):
    w, h, wheels, r, bottom = CARS[name]
    car = Image.new("RGBA", (w, h))
    car.alpha_composite(Image.open(os.path.join(OUT, f"car_{name}{'_left' if left else ''}.png")).convert("RGBA"))
    wheel = Image.open(os.path.join(OUT, "wheel.png")).convert("RGBA").resize((r * 2, r * 2), Image.LANCZOS)
    for wx, wy in wheels:
        car.alpha_composite(wheel, ((w - wx if left else wx) - r, wy - r))
    return car, bottom

def paste_car(im, name, x, ground, scale, left=False):
    car, bottom = car_sprite(name, left)
    car = car.resize((round(car.width * scale), round(car.height * scale)), Image.LANCZOS)
    im.alpha_composite(car, (round(x), round(ground - bottom * scale)))

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

def preview(pal, season, clock, temp, cond, fx=None, x=1920, plane=None, pets=(), near_car="sports"):
    """plane is the (x, y) of an airplane to draw, or None. pets is a list of
    (image name, x) for animals on the sidewalk, like placeAnimals() in
    MainScene.brs. near_car is the car in the near lane."""
    p = season_palette(pal, season)
    mtn = season if season == "winter" else "summer"
    def four(fn, *args):
        body = fn(*args)
        return body + "".join(f'<g transform="translate({dx},0)">{body}</g>' for dx in (1920, 3840, 5760))
    # The full 7680 px street: town sections A, B, C, and D
    def ab(fn_a, fn_b, *args):
        a, b = fn_a(*args), fn_b(*args)
        return a + "".join(f'<g transform="translate({dx},0)">{body}</g>' for dx, body in ((1920, b), (3840, a), (5760, b)))
    strip = (four(clouds, p, season) + ab(far, far_b, p, mtn) + ab(near, near_b, p, mtn) + four(hills, p, season)
             + town(p, season) + f'<g transform="translate(1920,0)">{town_b(p, season)}</g>'
             + f'<g transform="translate(3840,0)">{town_c(p, season)}</g>'
             + f'<g transform="translate(5760,0)">{town_d(p, season)}</g>')
    # The sky, stars, and sun or moon, placed like applyScene() in MainScene.brs,
    # with the scenery on top
    sky_im = Image.new("RGBA", (1920, 1080))
    stars_im = Image.open(os.path.join(OUT, "stars.png")).convert("RGBA")
    if pal != "day":
        if pal == "dusk":
            stars_im.putalpha(stars_im.getchannel("A").point(lambda v: v * 0.35))
        sky_im.alpha_composite(stars_im, (0, 0))
    body, pos = ("moon.png", (150, 100)) if pal == "night" else ("sun.png", (150, 110) if pal == "day" else (180, 340))
    sky_im.alpha_composite(Image.open(os.path.join(OUT, body)).convert("RGBA"), pos)
    back = Image.open(os.path.join(OUT, f"sky_{pal}.png")).convert("RGBA").resize((1920, 1080))
    back.alpha_composite(sky_im)
    scenery = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg(strip, "0 0 7680 1080", 7680, 1080).encode()))).convert("RGBA")
    back.alpha_composite(scenery.crop((x, 0, x + 1920, 1080)))
    im = back
    if season == "summer" and pal == "night":
        im.alpha_composite(Image.open(os.path.join(OUT, "fireflies_a.png")).convert("RGBA").resize((1920, 400)), (0, 540))
    if plane:
        im.alpha_composite(Image.open(os.path.join(OUT, f"plane_{pal}.png")).convert("RGBA").resize((56, 22), Image.LANCZOS), plane)
    # Cars: one parked at the gas station (if it is in view), one in each lane
    if 1920 - 600 < x < 3840:
        paste_car(im, "van", 1920 + 780 - x - 310 * 0.78 / 2, 898, 0.78)
    paste_car(im, "truck", 1150, 1002, 0.86, left=True)
    paste_car(im, near_car, 420, 1072, 1.0)
    for name, px in pets:
        pet = Image.open(os.path.join(OUT, f"{name}.png")).convert("RGBA")
        pet = pet.resize((round(pet.width * 0.7), round(pet.height * 0.7)), Image.LANCZOS)
        im.alpha_composite(pet, (px, 924 - pet.height))
    if fx:
        im.alpha_composite(Image.open(os.path.join(OUT, f"{fx}.png")).convert("RGBA").resize((1920, 1080)))
    # The panel's first position in m.infoSpots
    px = 1260
    pan = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg(panel(clock, temp, cond, px), "0 0 1920 1080", 1920, 1080).encode()))).convert("RGBA")
    im.alpha_composite(pan)
    return im.convert("RGB")

def save_doc(im, name, width):
    im.resize((width, width * 9 // 16), Image.LANCZOS).save(os.path.join(DOCS, name), optimize=True)

save_doc(preview("day", "summer", "10:04 AM", "84\u00b0F", "Clear", plane=(560, 262)), "preview.png", 1280)
for season, temp, cond, fx in (("spring", "62\u00b0F", "Partly cloudy", None), ("summer", "84\u00b0F", "Clear", None),
                               ("fall", "55\u00b0F", "Mostly clear", "leaves"), ("winter", "28\u00b0F", "Overcast", None)):
    save_doc(preview("day", season, "10:04 AM", temp, cond, fx), f"preview_{season}.png", 640)
for pal, clock in (("day", "10:04 AM"), ("dusk", "7:12 PM"), ("night", "10:42 PM")):
    save_doc(preview(pal, "summer", clock, "78\u00b0F", "Clear", x=0), f"preview_{pal}.png", 640)
# Town section C (the houses, Cabana's, and the other shops on the third block)
save_doc(preview("day", "summer", "10:04 AM", "84\u00b0F", "Clear", x=3840), "preview_section_c.png", 1280)
save_doc(preview("night", "fall", "10:42 PM", "48\u00b0F", "Clear", "leaves", x=3840), "preview_section_c_fall_night.png", 640)
save_doc(preview("day", "winter", "10:04 AM", "28\u00b0F", "Overcast", x=3840), "preview_section_c_winter.png", 640)
# Town section D, with the buggy and the animals
d_pets = [("cat_black", 240), ("guinea_black_orange", 560), ("cat_tabby", 1060), ("guinea_white_orange", 1400), ("cat_gray", 1760)]
save_doc(preview("day", "summer", "10:04 AM", "84\u00b0F", "Clear", x=5760, pets=d_pets, near_car="buggy"), "preview_section_d.png", 1280)
save_doc(preview("night", "winter", "10:42 PM", "26\u00b0F", "Clear", x=5760, pets=d_pets, near_car="buggy"), "preview_section_d_winter_night.png", 640)
save_doc(preview("day", "spring", "10:04 AM", "62\u00b0F", "Partly cloudy", x=5760, pets=d_pets, near_car="buggy"), "preview_section_d_spring.png", 640)

print("Wrote", len(os.listdir(OUT)), "images to", OUT)
