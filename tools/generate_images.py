"""Generates every image in images/ from the drawings defined in this file.

Run from the repository root:
    python3 tools/generate_images.py

Requires: pip install cairosvg pillow fonttools
"""
import cairosvg, random, os
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
   sidewalk="#D9E2EA", curb="#B7C4CF", road="#3E4A53", roadLine="#F8FAFC"),
 "dusk": dict(sky="#5E6F93", horizon="#F2A27E", cloud="#F3D6CC", far="#7A8BA8", mid="#56708C", snow="#E8D9D3",
   hillFar="#5E7C6C", hill="#4A6A58", tree="#34523F", river="#5C7493", riverHi="#F2B79C",
   houseA="#E3E1E4", houseB="#D4D3DA", wall2="#C3C6D0", roof="#2A3F50", window="#F6C46A",
   sidewalk="#BFC6CF", curb="#9CA6B1", road="#333E47", roadLine="#E3E1E4"),
 "night": dict(sky="#16242F", horizon="#34495E", cloud="#3A4E5E", far="#3A5468", mid="#2E465A", snow="#9FB2C2",
   hillFar="#2F4A3F", hill="#263E34", tree="#1D3229", river="#34495E", riverHi="#6E8BA3",
   houseA="#5B6770", houseB="#4E5A63", wall2="#46525C", roof="#1A2A36", window="#F6C46A",
   sidewalk="#5B6770", curb="#46525C", road="#20282E", roadLine="#C9D2DA"),
}

# Store sign fonts. Most are variable fonts (one file covers a range of weights).
# Kaushan Script and Alegreya Sans Medium have one weight, so the weight value is
# ignored for them. They are
# stored in tools/fonts under the SIL Open Font License. Text is converted to
# outlines here, so the images look the same on every computer.
FONT_DIR = os.path.join(ROOT, "tools", "fonts")
FONTS = {"oswald": "Oswald-Variable.ttf", "playfair": "PlayfairDisplay-Variable.ttf",
         "cinzel": "Cinzel-Variable.ttf", "script": "DancingScript-Variable.ttf",
         "kaushan": "KaushanScript-Regular.ttf", "alegreya": "AlegreyaSans-Medium.ttf",
         "signika": "Signika-Variable.ttf", "cabin": "Cabin-Variable.ttf", "hanken": "HankenGrotesk-Variable.ttf"}
_glyphs = {}

def glyphs(font, weight):
    key = (font, weight)
    if key not in _glyphs:
        f = TTFont(os.path.join(FONT_DIR, FONTS[font]))
        gs = f.getGlyphSet(location={"wght": weight}) if "fvar" in f else f.getGlyphSet()
        _glyphs[key] = (f.getBestCmap(), gs, f["head"].unitsPerEm)
    return _glyphs[key]

def text(label, font, weight, size, cx, y, fill, spacing=0):
    """Draws label as outlines, centered on cx, with its baseline at y."""
    cmap, gs, upm = glyphs(font, weight)
    k = size / upm
    names = [cmap[ord(ch)] for ch in label]
    width = sum(gs[n].width * k for n in names) + spacing * (len(names) - 1)
    x = cx - width / 2
    d = ""
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        d += pen.getCommands()
        x += gs[n].width * k + spacing
    return f'<path d="{d}" fill="{fill}"/>'

def svg(content, vb, w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{content}</svg>'

def save(content, vb, w, h, name):
    cairosvg.svg2png(bytestring=svg(content, vb, w, h).encode(), write_to=os.path.join(OUT, name))

def clouds(p):
    c = p["cloud"]
    return f'''<g fill="{c}">
<circle cx="360" cy="200" r="38"/><circle cx="420" cy="182" r="52"/><circle cx="480" cy="200" r="40"/><rect x="322" y="200" width="196" height="38" rx="19"/>
<circle cx="1050" cy="150" r="30"/><circle cx="1100" cy="136" r="42"/><circle cx="1150" cy="150" r="32"/><rect x="1020" y="150" width="162" height="30" rx="15"/>
<circle cx="1640" cy="300" r="34"/><circle cx="1695" cy="284" r="46"/><circle cx="1750" cy="300" r="34"/><rect x="1606" y="300" width="178" height="34" rx="17"/></g>'''

def far(p):
    return f'<polygon fill="{p["far"]}" points="0,720 0,470 140,400 260,450 420,330 560,430 700,380 860,300 1000,410 1160,350 1320,430 1480,320 1640,400 1780,360 1920,470 1920,720"/>'

def near(p):
    return f'''<polygon fill="{p["mid"]}" points="0,760 0,560 180,470 320,540 500,420 680,560 820,500 960,600 1080,520 1260,410 1440,540 1600,460 1760,520 1920,560 1920,760"/>
<g fill="{p["snow"]}"><polygon points="180,470 130,495 150,492 165,502 182,492 200,502 230,495"/>
<polygon points="500,420 448,455 470,450 488,462 506,450 526,462 545,455"/>
<polygon points="1260,410 1203,445 1225,440 1242,452 1262,440 1284,452 1308,445"/></g>'''

TREES = [(60,692),(110,686),(170,680),(240,672),(300,668),(620,662),(680,664),(740,658),
         (1300,668),(1360,682),(1420,692),(1700,724),(1780,724),(1860,714)]
def hills(p):
    t = "".join(f'<polygon points="{x},{b-52} {x-16},{b} {x+16},{b}"/>' for x,b in TREES)
    return f'''<path fill="{p["hillFar"]}" d="M0,700 C300,620 600,660 960,640 C1300,620 1620,780 1920,700 L1920,910 L0,910 Z"/>
<path fill="{p["hill"]}" d="M0,780 C400,720 700,760 960,740 C1300,720 1520,840 1920,780 L1920,910 L0,910 Z"/>
<g fill="{p["tree"]}">{t}<rect x="414" y="760" width="12" height="36"/><circle cx="420" cy="748" r="30"/>
<rect x="1494" y="764" width="12" height="36"/><circle cx="1500" cy="752" r="30"/></g>
<path fill="{p["river"]}" d="M958,647 C935,668 1000,695 900,730 C760,780 640,800 560,900 L1080,900 C1100,820 1180,790 1240,750 C1320,700 1060,675 1000,662 C985,656 968,650 958,647 Z"/>
<g stroke="{p["riverHi"]}" stroke-width="4" stroke-linecap="round" fill="none">
<path d="M962,672 L980,672"/><path d="M930,700 L972,700"/><path d="M860,758 L930,758"/><path d="M1010,770 L1080,770"/><path d="M760,832 L850,832"/><path d="M930,850 L1030,850"/></g>'''

def sign(x, y, w, h, fill, label, font, weight, size, ty, spacing=2):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>'
            + text(label, font, weight, size, x + w / 2, ty, "#F8FAFC", spacing))

def street(p):
    return (f'<rect x="0" y="900" width="1920" height="36" fill="{p["sidewalk"]}"/><rect x="0" y="936" width="1920" height="6" fill="{p["curb"]}"/>'
            f'<rect x="0" y="942" width="1920" height="138" fill="{p["road"]}"/>'
            f'<path d="M0,1011 L1920,1011" stroke="{p["roadLine"]}" stroke-width="6" stroke-dasharray="60 36" fill="none"/>')

def arch(x, y, w, h, fill):
    """A window or door with a round top. (x, y) is the top left corner."""
    r = w / 2
    return f'<path d="M{x},{y+h} L{x},{y+r} A{r},{r} 0 0 1 {x+w},{y+r} L{x+w},{y+h} Z" fill="{fill}"/>'

# The town layer is two different 1920 pixel tiles, A then B, so the street is
# 3840 pixels long before it repeats.
def town(p):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    def house(x, y, w, roofPeak, win1, win2, doorX, winY, number, font, weight=600):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{900-y}" fill="{A}"/>'
                f'<polygon points="{x-12},{y} {x+w//2},{roofPeak} {x+w+12},{y}" fill="{R}"/>'
                f'<rect x="{win1}" y="{winY}" width="44" height="40" fill="{Wn}"/><rect x="{win2}" y="{winY}" width="44" height="40" fill="{Wn}"/>'
                f'<rect x="{doorX}" y="830" width="40" height="70" fill="{R}"/>'
                # House number plaque above the door
                f'<rect x="{doorX-2}" y="808" width="44" height="18" rx="3" fill="{R}"/>'
                + text(number, font, weight, 14, doorX + 20, 822, "#F8FAFC", 1))
    s = house(40, 750, 200, 680, 62, 174, 120, 780, "5401", "signika")
    s += (f'<rect x="270" y="700" width="240" height="200" fill="{B}"/><rect x="266" y="700" width="248" height="14" fill="{R}"/>'
          + sign(300, 724, 180, 44, R, "Bakery", "script", 700, 34, 757, 1) +
          f'<polygon points="280,790 500,790 510,822 270,822" fill="{ACCENT}"/>'
          f'<rect x="290" y="832" width="130" height="58" fill="{Wn}"/><rect x="440" y="832" width="46" height="68" fill="{R}"/>')
    s += house(540, 730, 180, 664, 562, 654, 610, 760, "135", "hanken", 300)
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
    s += (f'<rect x="880" y="670" width="220" height="230" fill="{W2}"/><rect x="876" y="670" width="228" height="14" fill="{R}"/>'
          f'<rect x="906" y="698" width="48" height="48" fill="{Wn}"/><rect x="1026" y="698" width="48" height="48" fill="{Wn}"/>'
          + sign(906, 756, 168, 44, "#6B4A3A", "BOOKS", "playfair", 800, 28, 788, 4) +
          f'<polygon points="890,808 1090,808 1098,836 882,836" fill="{p["mid"]}"/>'
          f'<rect x="900" y="846" width="110" height="48" fill="{Wn}"/>{spines}'
          f'<rect x="900" y="868" width="110" height="4" fill="{R}"/><rect x="900" y="890" width="110" height="4" fill="{R}"/>'
          f'<rect x="1030" y="840" width="46" height="60" fill="{R}"/>')
    s += (f'<rect x="1120" y="710" width="260" height="190" fill="{B}"/><rect x="1116" y="710" width="268" height="14" fill="{R}"/>'
          # Two lines: Luke's Diner in Gilmore Girls is in the old Williams Hardware building
          + sign(1150, 730, 200, 54, "#4A82A8", "WILLIAMS", "oswald", 500, 16, 749, 5)
          + text("HARDWARE", "oswald", 600, 26, 1250, 777, "#F8FAFC", 4) +
          f'<polygon points="1130,800 1370,800 1378,828 1122,828" fill="{R}"/>'
          f'<rect x="1140" y="838" width="150" height="56" fill="{Wn}"/><rect x="1310" y="834" width="46" height="66" fill="{R}"/>')
    s += house(1410, 740, 190, 672, 1432, 1534, 1485, 770, "5334", "cabin")
    s += (f'<rect x="1630" y="690" width="250" height="210" fill="{W2}"/><rect x="1626" y="690" width="258" height="14" fill="{R}"/>'
          f'<rect x="1660" y="716" width="48" height="44" fill="{Wn}"/><rect x="1772" y="716" width="48" height="44" fill="{Wn}"/>'
          + sign(1680, 768, 150, 46, R, "Luke\u2019s", "kaushan", 400, 32, 802, 1) +
          f'<polygon points="1640,820 1870,820 1878,846 1632,846" fill="{ACCENT}"/>'
          f'<rect x="1650" y="854" width="140" height="42" fill="{Wn}"/><rect x="1806" y="852" width="46" height="48" fill="{R}"/>')
    return s + street(p)

def town_b(p):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    RED, GOLD, BLUE = "#B5523F", "#F6C46A", "#4A82A8"
    # Church: bell tower with a spire and a cross, and a nave with stained glass windows
    s = (f'<rect x="166" y="760" width="264" height="140" fill="{A}"/>'
         f'<polygon points="156,762 300,692 440,762" fill="{R}"/>'
         f'<rect x="70" y="690" width="100" height="210" fill="{A}"/>'
         f'<polygon points="62,692 120,590 178,692" fill="{R}"/>'
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
    # Gas station: price sign, canopy over one pump, and a small market.
    # The parked car is added by MainScene.brs so it can change each time.
    s += (f'<rect x="483" y="746" width="8" height="154" fill="{W2}"/>'
          f'<rect x="452" y="690" width="70" height="62" rx="4" fill="{R}"/>'
          + text("GAS", "oswald", 700, 20, 487, 714, ACCENT, 2)
          + text("3.19", "oswald", 500, 22, 487, 742, "#F8FAFC", 1) +
          f'<rect x="556" y="772" width="12" height="128" fill="{W2}"/><rect x="912" y="772" width="12" height="128" fill="{W2}"/>'
          f'<rect x="520" y="740" width="440" height="34" fill="{R}"/><rect x="520" y="766" width="440" height="8" fill="{ACCENT}"/>'
          + text("FUEL STOP", "oswald", 600, 22, 740, 762, "#F8FAFC", 5) +
          f'<rect x="578" y="886" width="62" height="14" fill="{p["curb"]}"/>'
          f'<rect x="588" y="812" width="40" height="76" fill="{B}"/><rect x="588" y="812" width="40" height="10" fill="{ACCENT}"/>'
          f'<rect x="594" y="828" width="28" height="18" fill="{Wn}"/>'
          f'<path d="M628,836 Q646,840 642,870" stroke="#1F2A33" stroke-width="4" fill="none"/>'
          f'<rect x="980" y="770" width="200" height="130" fill="{B}"/><rect x="976" y="770" width="208" height="14" fill="{R}"/>'
          + sign(1006, 792, 148, 36, ACCENT, "MARKET", "oswald", 600, 22, 818, 4) +
          f'<rect x="996" y="842" width="96" height="50" fill="{Wn}"/><rect x="1110" y="836" width="46" height="64" fill="{R}"/>')
    # Library: stone front with columns, steps, and a carved name
    s += (f'<rect x="1250" y="888" width="500" height="12" fill="{p["curb"]}"/><rect x="1262" y="876" width="476" height="12" fill="{W2}"/>'
          f'<rect x="1280" y="730" width="440" height="146" fill="{A}"/>'
          f'<polygon points="1262,712 1500,646 1738,712" fill="{B}"/>'
          f'<polygon points="1300,706 1500,656 1700,706" fill="none" stroke="{W2}" stroke-width="4"/>'
          f'<rect x="1270" y="708" width="460" height="24" fill="{W2}"/>'
          + text("PUBLIC LIBRARY", "cinzel", 700, 18, 1500, 727, R, 4))
    for cx in (1320, 1392, 1464, 1536, 1608, 1680):
        s += (f'<rect x="{cx-11}" y="740" width="22" height="136" fill="{B}"/>'
              f'<rect x="{cx-15}" y="732" width="30" height="8" fill="{W2}"/><rect x="{cx-15}" y="868" width="30" height="8" fill="{W2}"/>')
    for wx in (1356, 1428, 1572, 1644):
        s += arch(wx - 15, 760, 30, 80, Wn)
    s += arch(1478, 796, 44, 80, R)
    # Trees at the end of the tile
    s += (f'<g fill="{p["tree"]}"><rect x="1814" y="836" width="12" height="64"/><circle cx="1820" cy="816" r="36"/>'
          f'<rect x="1202" y="846" width="10" height="54"/><circle cx="1207" cy="830" r="26"/></g>')
    return s + street(p)

def sky(p):
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/>'
            f'<stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

# Layer crops: name -> (function, y, height)
CROPS = {"clouds": (clouds, 90, 255), "far": (far, 295, 425), "near": (near, 400, 360),
         "hills": (hills, 600, 310), "town_a": (town, 550, 530), "town_b": (town_b, 550, 530)}
for pal, p in P.items():
    save(sky(p), "0 0 8 1080", 8, 1080, f"sky_{pal}.png")
    for name, (fn, y, h) in CROPS.items():
        save(fn(p), f"0 {y} 1920 {h}", 1920, h, f"{name}_{pal}.png")

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

# Wheel (drawn separately so it can spin)
save('<circle cx="32" cy="32" r="32" fill="#1F2A33"/><circle cx="32" cy="32" r="18" fill="#C9D2DA"/>'
     '<g stroke="#5B6770" stroke-width="4"><line x1="32" y1="16" x2="32" y2="48"/><line x1="16" y1="32" x2="48" y2="32"/></g>'
     '<circle cx="32" cy="32" r="6" fill="#5B6770"/>', "0 0 64 64", 64, 64, "wheel.png")

GLASS, DARK = "#C9DAEA", "#1F2A33"
def wells(pts, r):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{DARK}"/>' for x, y in pts)

sedan = (f'<path fill="#4A82A8" d="M6,72 L6,56 Q8,40 30,38 L70,36 L100,10 Q105,6 115,6 L180,6 Q190,6 196,12 L228,36 L262,40 Q276,42 276,56 L276,72 Q276,80 268,80 L14,80 Q6,80 6,72 Z"/>'
         f'<polygon points="80,36 104,12 144,12 144,36" fill="{GLASS}"/><polygon points="150,12 188,12 216,36 150,36" fill="{GLASS}"/>'
         '<line x1="147" y1="38" x2="147" y2="76" stroke="#34495E" stroke-width="2"/>'
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

# Channel icons from a composite of the day scene
def composite(pal, tile="a"):
    p = P[pal]
    townFn = town if tile == "a" else town_b
    full = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/><stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#g)"/><circle cx="1500" cy="220" r="64" fill="{ACCENT}"/>'
            + clouds(p) + far(p) + near(p) + hills(p) + townFn(p))
    path = os.path.join(BUILD, f"composite_{pal}_{tile}.png")
    cairosvg.svg2png(bytestring=svg(full, "0 0 1920 1080", 1920, 1080).encode(), write_to=path)
    return path
im = Image.open(composite("day")).convert("RGB")
crop = im.crop((240, 0, 1680, 1080))
crop.resize((290, 218), Image.LANCZOS).save(os.path.join(OUT, "icon_hd.png"))
crop.resize((540, 405), Image.LANCZOS).save(os.path.join(OUT, "icon_fhd.png"))
composite("day", "b")
composite("night")
composite("night", "b")

# Mirrored car bodies for the far lane, where cars drive right to left
for n in ["sedan", "van", "jeep", "truck"]:
    ImageOps.mirror(Image.open(os.path.join(OUT, f"car_{n}.png"))).save(os.path.join(OUT, f"car_{n}_left.png"))

# Add a parked car to the tile B previews to check its position. These numbers
# copy parkCar() and m.carDefs in components/MainScene.brs.
def park_preview(pal, name, w, h, wheels, r, bottom):
    path = os.path.join(BUILD, f"composite_{pal}_b.png")
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

print("Wrote", len(os.listdir(OUT)), "images to", OUT)
