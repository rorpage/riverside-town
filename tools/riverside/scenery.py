"""The scenery layers behind the town: sky, clouds, mountains, hills with the
river, and the street."""
import random
from .art import wall, round_tree, pine, is_dark, bicycle

def sky(p):
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sky"]}"/>'
            f'<stop offset="0.62" stop-color="{p["horizon"]}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

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

# Far mountains, first tile. With table_mountain on, the center mountains are
# shaped like Table Mountain seen from Cape Town: a gentle slope up to Devil's
# Peak, the long flat top with steep cliffs at each end, a dip, and Lion's
# Head. The flat top points all have the same y value, so snow_caps() does not
# treat them as peaks. With it off, there is one ordinary peak in the center.
TABLE_TOP = (746, 1066, 310)   # left x, right x, y of the flat top
FAR_PTS_TABLE = [(0,470),(140,400),(260,450),(420,330),(560,430),
           # Devil's Peak
           (612,408),(668,384),(688,364),(700,352),(712,346),(722,352),(730,349),
           # Left cliff, flat top, right cliff
           (736,326),(742,314),(TABLE_TOP[0],TABLE_TOP[2]),(TABLE_TOP[1],TABLE_TOP[2]),(1072,316),(1080,344),(1090,360),
           # The dip, then Lion's Head
           (1112,372),(1136,380),(1154,377),(1172,358),(1186,336),(1198,326),(1208,342),(1230,372),(1270,400),
           (1320,430),(1480,320),(1640,400),(1780,360),(1920,470)]
FAR_PTS_PLAIN = [(0,470),(140,400),(260,450),(420,330),(560,430),(700,380),(860,300),(1000,410),
                 (1160,350),(1320,430),(1480,320),(1640,400),(1780,360),(1920,470)]

def far(p, season, table_mountain=True):
    pts_list = FAR_PTS_TABLE if table_mountain else FAR_PTS_PLAIN
    pts = " ".join(f"{x},{y}" for x, y in pts_list)
    s = f'<polygon fill="{p["far"]}" points="0,720 {pts} 1920,720"/>'
    if season == "winter":
        s += snow_caps(pts_list, 0.4, p["snow"])
        if table_mountain:
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
# tiles join without a seam in any order.
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
def radio_tower(x, base, p):
    """A tall radio tower on a far ridge, with red and white bands and a red
    light on top that is lit at dusk and night. It is drawn at the distance of
    the near mountains, so it is thin."""
    top = base - 168
    red, white = wall("#C0392B", p), wall("#F8FAFC", p)
    s = ""
    bands = 8
    for i in range(bands):
        y0 = base - (base - top) * i / bands
        y1 = base - (base - top) * (i + 1) / bands
        w0 = 13 - 10 * i / bands
        w1 = 13 - 10 * (i + 1) / bands
        c = red if i % 2 == 0 else white
        s += f'<polygon points="{x - w0:.1f},{y0:.1f} {x + w0:.1f},{y0:.1f} {x + w1:.1f},{y1:.1f} {x - w1:.1f},{y1:.1f}" fill="none" stroke="{c}" stroke-width="1.6"/>'
        s += f'<line x1="{x - w0:.1f}" y1="{y0:.1f}" x2="{x + w1:.1f}" y2="{y1:.1f}" stroke="{c}" stroke-width="1"/>'
    s += f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top - 8}" stroke="{red}" stroke-width="1.6"/>'
    if is_dark(p):
        s += (f'<circle cx="{x}" cy="{top - 9}" r="6" fill="#E74C3C" fill-opacity="0.3"/>'
              f'<circle cx="{x}" cy="{top - 9}" r="2.2" fill="#E74C3C"/>')
    return s

# The radio tower stands in the valley at x=1000 of the second near tile,
# where the mountain is at y=580, so its top (y=412) is inside the near
# layer's crop, which starts at y=400.
RADIO_TOWER = (1000, 584)

def near_b(p, season, tower=False):
    pts = " ".join(f"{x},{y}" for x, y in NEAR_B_PTS)
    s = f'<polygon fill="{p["mid"]}" points="0,760 {pts} 1920,760"/>'
    # Small snow caps on the highest peaks in other seasons, like the first tile
    s += snow_caps(NEAR_B_PTS, 0.5 if season == "winter" else 0.22, p["snow"])
    return s + (radio_tower(*RADIO_TOWER, p) if tower else "")

TREES = [(60,692),(110,686),(170,680),(240,672),(300,668),(620,662),(680,664),(740,658),
         (1300,668),(1360,682),(1420,692),(1700,724),(1780,724),(1860,714)]

# Kayaks pulled up on the grass beside the river, in every season but winter.
# Each is (center x, center y, angle in degrees, color). The colors are day
# colors, darkened for dusk and night with wall() like the buildings.
KAYAKS = [(676, 806, -14, "#D9452F"), (1172, 846, 22, "#F2B33D"), (1218, 806, 18, "#2E86C1")]
def kayaks(p, season):
    if season == "winter":
        return ""
    s = ""
    for cx, cy, angle, color in KAYAKS:
        c = wall(color, p)
        paddle = wall("#5B6770", p)
        s += (f'<g transform="translate({cx},{cy}) rotate({angle})">'
              # Hull with pointed ends, a dark cockpit, and a paddle lying beside it
              f'<path d="M-36,0 Q-18,-7 0,-7 Q18,-7 36,0 Q18,6 0,6 Q-18,6 -36,0 Z" fill="{c}"/>'
              f'<ellipse cx="2" cy="-1" rx="8" ry="3" fill="#1F2A33"/>'
              f'<line x1="-26" y1="10" x2="26" y2="10" stroke="{paddle}" stroke-width="2"/>'
              f'<ellipse cx="-28" cy="10" rx="4" ry="2" fill="{paddle}"/><ellipse cx="28" cy="10" rx="4" ry="2" fill="{paddle}"/>'
              '</g>')
    return s

# Two people riding bikes on the hills, far away, so they are small. Each is
# (x of the left end, ground y, color, facing left). They are not drawn in
# winter.
CYCLISTS = [(250, 734, "#C0392B", False), (1610, 762, "#2E86C1", True)]
def cyclists(p, season):
    if season == "winter":
        return ""
    return "".join(bicycle(x, y, 0.42, wall(c, p), left, (wall(c, p), wall("#E0B89A", p), wall("#34495E", p)))
                   for x, y, c, left in CYCLISTS)

def hills(p, season, with_kayaks=True, with_cyclists=False):
    t = "".join(pine(x, b, p, season) for x, b in TREES)
    s = f'''<path fill="{p["hillFar"]}" d="M0,700 C300,620 600,660 960,640 C1300,620 1620,780 1920,700 L1920,910 L0,910 Z"/>
<path fill="{p["hill"]}" d="M0,780 C400,720 700,760 960,740 C1300,720 1520,840 1920,780 L1920,910 L0,910 Z"/>
{t}{round_tree(420, 796, 36, 30, p, season)}{round_tree(1500, 800, 36, 30, p, season)}
<path fill="{p["river"]}" d="M958,647 C935,668 1000,695 900,730 C760,780 640,800 560,900 L1080,900 C1100,820 1180,790 1240,750 C1320,700 1060,675 1000,662 C985,656 968,650 958,647 Z"/>
<g stroke="{p["riverHi"]}" stroke-width="4" stroke-linecap="round" fill="none">
<path d="M962,672 L980,672"/><path d="M930,700 L972,700"/><path d="M860,758 L930,758"/><path d="M1010,770 L1080,770"/><path d="M760,832 L850,832"/><path d="M930,850 L1030,850"/></g>'''
    return s + (kayaks(p, season) if with_kayaks else "") + (cyclists(p, season) if with_cyclists else "")

def street(p, season, seed=11):
    """The sidewalk, curb, and road at the bottom of every town section. The
    road line's dash pattern repeats every 96 pixels, which divides 1920, so
    the sections join without a seam."""
    walk = p["snow"] if season == "winter" else p["sidewalk"]
    s = (f'<rect x="0" y="900" width="1920" height="36" fill="{walk}"/><rect x="0" y="936" width="1920" height="6" fill="{p["curb"]}"/>'
         f'<rect x="0" y="942" width="1920" height="138" fill="{p["road"]}"/>'
         f'<path d="M0,1011 L1920,1011" stroke="{p["roadLine"]}" stroke-width="6" stroke-dasharray="60 36" fill="none"/>')
    if season == "fall":
        # Fallen leaves on the sidewalk
        rnd = random.Random(seed)
        for _ in range(60):
            x, y = rnd.randint(20, 1900), rnd.randint(904, 932)
            c = rnd.choice([p["leaf"], p["leaf2"], "#E0B040"])
            s += f'<ellipse cx="{x}" cy="{y}" rx="5" ry="2.5" fill="{c}" transform="rotate({rnd.randint(0, 180)} {x} {y})"/>'
    return s
