"""Generates every image in images/ from the drawings defined in this file.

Run from the repository root:
    python3 tools/generate_images.py

Requires: pip install cairosvg pillow
"""
import cairosvg, random, os
from PIL import Image, ImageOps
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
FONT = "DejaVu Sans"

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

def sign(x, y, w, h, fill, label, size, cx, ty):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>'
            f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="{FONT}" font-weight="bold" font-size="{size}" letter-spacing="2" fill="#F8FAFC">{label}</text>')

def town(p):
    A, B, W2, R, Wn = p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]
    def house(x, y, w, roofPeak, win1, win2, doorX, winY):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{900-y}" fill="{A}"/>'
                f'<polygon points="{x-12},{y} {x+w//2},{roofPeak} {x+w+12},{y}" fill="{R}"/>'
                f'<rect x="{win1}" y="{winY}" width="44" height="40" fill="{Wn}"/><rect x="{win2}" y="{winY}" width="44" height="40" fill="{Wn}"/>'
                f'<rect x="{doorX}" y="830" width="40" height="70" fill="{R}"/>')
    s = house(40, 750, 200, 680, 62, 174, 120, 780)
    s += (f'<rect x="270" y="700" width="240" height="200" fill="{B}"/><rect x="266" y="700" width="248" height="14" fill="{R}"/>'
          + sign(300, 724, 180, 44, R, "BAKERY", 24, 390, 755) +
          f'<polygon points="280,790 500,790 510,822 270,822" fill="{ACCENT}"/>'
          f'<rect x="290" y="832" width="130" height="58" fill="{Wn}"/><rect x="440" y="832" width="46" height="68" fill="{R}"/>')
    s += house(540, 730, 180, 664, 562, 654, 610, 760)
    s += (f'<rect x="880" y="670" width="220" height="230" fill="{W2}"/><rect x="876" y="670" width="228" height="14" fill="{R}"/>'
          f'<rect x="906" y="698" width="48" height="48" fill="{Wn}"/><rect x="1026" y="698" width="48" height="48" fill="{Wn}"/>'
          + sign(910, 758, 160, 40, R, "BOOKS", 22, 990, 786) +
          f'<polygon points="890,808 1090,808 1098,836 882,836" fill="{p["mid"]}"/>'
          f'<rect x="900" y="846" width="110" height="48" fill="{Wn}"/><rect x="1030" y="840" width="46" height="60" fill="{R}"/>')
    s += (f'<rect x="1120" y="710" width="260" height="190" fill="{B}"/><rect x="1116" y="710" width="268" height="14" fill="{R}"/>'
          + sign(1150, 734, 200, 44, "#4A82A8", "HARDWARE", 22, 1250, 764) +
          f'<polygon points="1130,800 1370,800 1378,828 1122,828" fill="{R}"/>'
          f'<rect x="1140" y="838" width="150" height="56" fill="{Wn}"/><rect x="1310" y="834" width="46" height="66" fill="{R}"/>')
    s += house(1410, 740, 190, 672, 1432, 1534, 1485, 770)
    s += (f'<rect x="1630" y="690" width="250" height="210" fill="{W2}"/><rect x="1626" y="690" width="258" height="14" fill="{R}"/>'
          f'<rect x="1660" y="716" width="48" height="44" fill="{Wn}"/><rect x="1772" y="716" width="48" height="44" fill="{Wn}"/>'
          + sign(1680, 772, 150, 40, R, "CAF&#201;", 22, 1755, 800) +
          f'<polygon points="1640,820 1870,820 1878,846 1632,846" fill="{ACCENT}"/>'
          f'<rect x="1650" y="854" width="140" height="42" fill="{Wn}"/><rect x="1806" y="852" width="46" height="48" fill="{R}"/>')
    s += (f'<rect x="0" y="900" width="1920" height="36" fill="{p["sidewalk"]}"/><rect x="0" y="936" width="1920" height="6" fill="{p["curb"]}"/>'
          f'<rect x="0" y="942" width="1920" height="138" fill="{p["road"]}"/>'
          f'<path d="M0,1011 L1920,1011" stroke="{p["roadLine"]}" stroke-width="6" stroke-dasharray="60 36" fill="none"/>')
    return s

def sky(p):
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/>'
            f'<stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

# Layer crops: name -> (function, y, height)
CROPS = {"clouds": (clouds, 90, 255), "far": (far, 295, 425), "near": (near, 400, 360),
         "hills": (hills, 600, 310), "town": (town, 660, 420)}
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
def composite(pal):
    p = P[pal]
    full = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/><stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#g)"/><circle cx="1500" cy="220" r="64" fill="{ACCENT}"/>'
            + clouds(p) + far(p) + near(p) + hills(p) + town(p))
    path = os.path.join(BUILD, f"composite_{pal}.png")
    cairosvg.svg2png(bytestring=svg(full, "0 0 1920 1080", 1920, 1080).encode(), write_to=path)
    return path
im = Image.open(composite("day")).convert("RGB")
crop = im.crop((240, 0, 1680, 1080))
crop.resize((290, 218), Image.LANCZOS).save(os.path.join(OUT, "icon_hd.png"))
crop.resize((540, 405), Image.LANCZOS).save(os.path.join(OUT, "icon_fhd.png"))
composite("night")

# Mirrored car bodies for the far lane, where cars drive right to left
for n in ["sedan", "van", "jeep", "truck"]:
    ImageOps.mirror(Image.open(os.path.join(OUT, f"car_{n}.png"))).save(os.path.join(OUT, f"car_{n}_left.png"))

print("Wrote", len(os.listdir(OUT)), "images to", OUT)
