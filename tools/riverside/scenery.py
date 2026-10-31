"""The scenery layers behind the town: sky, clouds, mountains, hills with the
river, and the street."""
import random
from .art import wall, round_tree, pine, bicycle, hex_rgb
from . import buildings

def sky(p, overcast=False):
    """The sky gradient. With overcast on, it uses the gray sky colors."""
    top, bottom = (p["skyGray"], p["horizonGray"]) if overcast else (p["sky"], p["horizon"])
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="0.62" stop-color="{bottom}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

# Cloud levels, from the fewest clouds to the most. MainScene.brs picks one
# from the cloud cover in the weather (see cloudLevel() there) and shows
# clouds_<level>_<period>.png. "few" is also used before the first weather
# request finishes.
CLOUD_LEVELS = ["few", "scattered", "broken", "overcast"]

def puff(cx, cy, s, fill):
    """One cloud: three circles on a rounded base, s times the size of the
    middle cloud in the "few" image. It is 220 * s pixels wide, and it goes
    from 70 * s pixels above cy to 38 * s pixels below it."""
    return (f'<g fill="{fill}"><circle cx="{cx - 60 * s:.0f}" cy="{cy:.0f}" r="{38 * s:.0f}"/>'
            f'<circle cx="{cx:.0f}" cy="{cy - 18 * s:.0f}" r="{52 * s:.0f}"/>'
            f'<circle cx="{cx + 60 * s:.0f}" cy="{cy:.0f}" r="{40 * s:.0f}"/>'
            f'<rect x="{cx - 98 * s:.0f}" y="{cy:.0f}" width="{196 * s:.0f}" height="{38 * s:.0f}" rx="{19 * s:.0f}"/></g>')

def shaded_puff(cx, cy, s, p):
    """A cloud with a gray underside, for the broken and overcast levels."""
    return puff(cx, cy + 8 * s, s, p["cloudGray"]) + puff(cx, cy, s, p["cloud"])

def wrap(svg):
    """Draws svg three times: moved 1920 pixels left, in place, and moved 1920
    pixels right. Anything that crosses x=0 or x=1920 then shows on the other
    side too, in the same order, so the tile joins up at the edges."""
    return f'<g transform="translate(-1920,0)">{svg}</g>{svg}<g transform="translate(1920,0)">{svg}</g>'

def deck(p):
    """A gray cloud layer across the whole top of the clouds band, with a bumpy
    lower edge and a darker underside. The bumps are about 80 pixels apart."""
    rnd = random.Random(41)
    bumps = [(i * 80 + rnd.randint(-20, 20), rnd.randint(30, 52), rnd.randint(-8, 10)) for i in range(24)]
    def row(y, fill):
        return f'<g fill="{fill}">' + "".join(f'<circle cx="{x}" cy="{y + dy}" r="{r}"/>' for x, r, dy in bumps) + "</g>"
    # The top of the layer starts at the color of the overcast sky at y=90
    # (see sky()), so there is no line where the clouds image starts.
    sky_top = mix(p["skyGray"], p["horizonGray"], 90 / (1080 * 0.62))
    return (row(222, p["cloudDark"])
            + f'<linearGradient id="deck" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky_top}"/>'
            + f'<stop offset="0.5" stop-color="{p["cloudGray"]}"/></linearGradient>'
            + '<rect x="-40" y="90" width="2000" height="120" fill="url(#deck)"/>'
            + row(206, p["cloudGray"]))

def mix(a, b, t):
    """The color t of the way from color a to color b."""
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(hex_rgb(a), hex_rgb(b)))

def clouds(p, season, level="few"):
    """The clouds layer for one cloud level (see CLOUD_LEVELS). The clouds
    band is y=90 to y=345 (CROPS in generate_images.py)."""
    c = p["cloud"]
    few = f'''<g fill="{c}">
<circle cx="360" cy="200" r="38"/><circle cx="420" cy="182" r="52"/><circle cx="480" cy="200" r="40"/><rect x="322" y="200" width="196" height="38" rx="19"/>
<circle cx="1050" cy="150" r="30"/><circle cx="1100" cy="136" r="42"/><circle cx="1150" cy="150" r="32"/><rect x="1020" y="150" width="162" height="30" rx="15"/>
<circle cx="1640" cy="300" r="34"/><circle cx="1695" cy="284" r="46"/><circle cx="1750" cy="300" r="34"/><rect x="1606" y="300" width="178" height="34" rx="17"/></g>'''
    if level == "few":
        return few
    if level == "scattered":
        # The three clouds of "few" plus four more
        return wrap(few + "".join(puff(x, y, s, c) for x, y, s in
                                  ((150, 290, 0.8), (760, 250, 1.0), (1380, 190, 0.9), (1880, 170, 0.75))))
    if level == "broken":
        # Larger clouds with gray undersides, close enough to touch in places
        spots = ((80, 200, 1.2), (330, 290, 0.9), (560, 190, 1.35), (820, 260, 1.1), (1050, 170, 1.2),
                 (1280, 280, 1.0), (1500, 190, 1.3), (1730, 270, 1.05), (1900, 175, 0.8))
        return wrap("".join(shaded_puff(x, y, s, p) for x, y, s in spots))
    # Overcast: the gray layer, with some lower gray clouds under it
    lower = ((200, 290, 0.9), (700, 296, 1.0), (1180, 285, 0.85), (1650, 296, 1.0))
    return wrap(deck(p) + "".join(puff(x, y + 8 * s, s, p["cloudDark"]) + puff(x, y, s, p["cloudGray"]) for x, y, s in lower))

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
def near_b(p, season):
    pts = " ".join(f"{x},{y}" for x, y in NEAR_B_PTS)
    s = f'<polygon fill="{p["mid"]}" points="0,760 {pts} 1920,760"/>'
    # Small snow caps on the highest peaks in other seasons, like the first tile
    return s + snow_caps(NEAR_B_PTS, 0.5 if season == "winter" else 0.22, p["snow"])

TREES = [(60,692),(110,686),(170,680),(240,672),(300,668),(620,662),(680,664),(740,658),
         (1300,668),(1360,682),(1420,692),(1700,724),(1780,724),(1860,714)]

# Kayaks pulled up on the grass beside the river, in every season but winter.
# There is only one river, on hills tile A, so all the kayaks are there. Each
# is (center x, center y, angle in degrees, color, size). The ones higher up
# the river are farther away, so they are smaller. The colors are day colors,
# darkened for dusk and night with wall() like the buildings.
KAYAKS = [(676, 806, -14, "#D9452F", 1), (1172, 846, 22, "#F2B33D", 1), (1218, 806, 18, "#2E86C1", 1),
          (1290, 798, -10, "#27AE60", 1), (822, 736, -6, "#8E44AD", 0.75), (788, 756, 8, "#F2B33D", 0.75),
          (1290, 714, 10, "#D9452F", 0.7), (884, 699, -4, "#2E86C1", 0.6)]
def kayaks(p, season, places=KAYAKS):
    if season == "winter":
        return ""
    s = ""
    for cx, cy, angle, color, size in places:
        c = wall(color, p)
        paddle = wall("#5B6770", p)
        s += (f'<g transform="translate({cx},{cy}) rotate({angle}) scale({size})">'
              # Hull with pointed ends, a dark cockpit, and a paddle lying beside it
              f'<path d="M-36,0 Q-18,-7 0,-7 Q18,-7 36,0 Q18,6 0,6 Q-18,6 -36,0 Z" fill="{c}"/>'
              f'<ellipse cx="2" cy="-1" rx="8" ry="3" fill="#1F2A33"/>'
              f'<line x1="-26" y1="10" x2="26" y2="10" stroke="{paddle}" stroke-width="2"/>'
              f'<ellipse cx="-28" cy="10" rx="4" ry="2" fill="{paddle}"/><ellipse cx="28" cy="10" rx="4" ry="2" fill="{paddle}"/>'
              '</g>')
    return s

# Two bikes parked beside the radio station, on the top of the near hill, far
# away, so they are small. Each is (x of the left end, color, facing left).
# They are only drawn with the radio station, and not in winter.
RADIO_BIKES = [(545, "#C0392B", False), (590, "#2E86C1", True)]
def radio_bikes(p, season):
    if season == "winter":
        return ""
    # 0.7 is BIKE_SCALE in buildings.py times about RADIO_SCALE, the size of
    # things at the distance of the hills
    return "".join(bicycle(x, near_hill_y(x + 21) + 3, 0.7, wall(c, p), left) for x, c, left in RADIO_BIKES)

# The radio station stands on the near hill to the left of the river, where
# the hill is nearly flat and high enough to show above most roofs. It is
# drawn at RADIO_SCALE, because the hills are farther away than the street,
# with its tall tower behind it. RADIO_X is the center of the station.
RADIO_X, RADIO_SCALE = 400, 0.55
# The tower stands behind the right half of the station, TOWER_DX pixels to the
# right of the station's center. Both of its legs reach the ground behind the
# building, so the whole building is in front of the tower. It is drawn before
# the near hill, so the hill covers the bottom of its legs.
TOWER_DX = 70

# Hill outlines, as lists of cubic curves: (start, control 1, control 2, end).
# Every outline starts at the same height and slope and ends at the same height
# and slope, so the tiles join without a seam in any order: the far hill starts
# at (0,700) toward (300,620) and ends at (1920,700) from (1620,780); the near
# hill starts at (0,780) toward (400,720) and ends at (1920,780) from (1520,840).
FAR_HILL = [((0, 700), (300, 620), (600, 660), (960, 640)), ((960, 640), (1300, 620), (1620, 780), (1920, 700))]
NEAR_HILL = [((0, 780), (400, 720), (700, 760), (960, 740)), ((960, 740), (1300, 720), (1520, 840), (1920, 780))]
# Tile C has its own outlines, with more and rounder hills, and no river
FAR_HILL_C = [((0, 700), (300, 620), (420, 600), (640, 630)), ((640, 630), (860, 660), (980, 590), (1240, 610)),
              ((1240, 610), (1440, 625), (1620, 780), (1920, 700))]
NEAR_HILL_C = [((0, 780), (200, 750), (300, 700), (480, 705)), ((480, 705), (660, 710), (720, 780), (900, 785)),
               ((900, 785), (1080, 790), (1150, 700), (1350, 705)), ((1350, 705), (1450, 708), (1520, 840), (1920, 780))]

def hill_path(curves, fill):
    """A filled hill shape: the outline, then down to y=910 and back."""
    d = f"M{curves[0][0][0]},{curves[0][0][1]}" + "".join(
        f" C{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]}" for _, a, b, c in curves)
    return f'<path fill="{fill}" d="{d} L1920,910 L0,910 Z"/>'

def curve_y(curves, x):
    """The y of a hill outline at x."""
    p0, p1, p2, p3 = next((c for c in curves if x <= c[3][0]), curves[-1])
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        bx = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        lo, hi = (t, hi) if bx < x else (lo, t)
    return (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]

def near_hill_y(x, curves=NEAR_HILL):
    """The y of the top of the near hill at x."""
    return curve_y(curves, x)

def lowest_ground(center, half):
    """The lowest point of the near hill between center - half and center + half."""
    return max(near_hill_y(center + half * i / 10) for i in range(-10, 11))

def tower_place(spec):
    """The left edge and top of the tower's box, for the radio station in spec."""
    k = RADIO_SCALE
    x = RADIO_X + TOWER_DX
    ground = lowest_ground(x, buildings.TOWER_W / 2 * k) + 10
    return x - buildings.TOWER_W / 2 * k, ground - buildings.TOWER_GROUND * k

def radio_light(spec):
    """The center of the tower's blinking light, in screen coordinates, or None
    if the station has no tower. MainScene.brs puts tower_light.png there."""
    if not spec or not spec.get("tower", True):
        return None
    left, top = tower_place(spec)
    k = RADIO_SCALE
    return round(left + buildings.TOWER_W / 2 * k), round(top + buildings.TOWER_LIGHT_Y * k)

def radio_tower(p, spec):
    if not spec.get("tower", True):
        return ""
    left, top = tower_place(spec)
    return (f'<g transform="translate({left:.1f},{top:.1f}) scale({RADIO_SCALE})">'
            + buildings.tower_svg(p, light=False) + '</g>')

def radio_scene(p, season, spec):
    """The radio station on the hill. Its ground line is the lowest point of the
    hill under the base, so no part of the base is above the ground."""
    k = RADIO_SCALE
    half = buildings.radio_width(spec) / 2 * k
    ground = lowest_ground(RADIO_X, half) + 1
    return (f'<g transform="translate({RADIO_X - half:.1f},{ground - 900 * k:.1f}) scale({k})">'
            + buildings.radio_draw(spec, 0, p, season) + '</g>')

# The second hills tile. It has the same hills as tile A, so the tiles join,
# with trees in other places, and no river, kayaks, or radio station.
TREES_B = [(40,694),(150,682),(210,676),(330,666),(560,662),(650,662),(780,656),
           (1250,664),(1330,676),(1480,700),(1560,712),(1650,722),(1830,718),
           (95,700),(270,680),(440,670),(1400,700),(1610,728),(1760,734),
           (900,650),(1000,648),(1100,650)]
ROUND_TREES_B = [(280, 794), (690, 790), (1060, 794), (1530, 818), (1700, 806)]

# The third hills tile has its own hill shapes and no river. Its pines stand in
# groups on the far hill, and its round trees on the near hill. The y of each
# tree is worked out from the hill outlines, so every tree stands on the ground.
PINES_C = [(x, round(curve_y(FAR_HILL_C, x)) + dy) for x, dy in
           ((50, 12), (110, 20), (165, 10), (380, 8), (430, 18), (480, 10), (535, 22),
            (760, 14), (815, 8), (1020, 10), (1075, 20), (1130, 12), (1185, 24), (1300, 12),
            (1560, 16), (1620, 26), (1690, 18), (1850, 14))]
ROUND_TREES_C = [(x, round(curve_y(NEAR_HILL_C, x)) + dy) for x, dy in
                 ((250, 40), (640, 30), (980, 36), (1400, 34), (1760, 30))]

def hills_c(p, season):
    """The third hills tile (hills_c): its own hill shapes, more trees, and no
    river."""
    return (hill_path(FAR_HILL_C, p["hillFar"]) + hill_path(NEAR_HILL_C, p["hill"])
            + "".join(pine(x, y, p, season) for x, y in PINES_C)
            + "".join(round_tree(x, y, 36, 30, p, season) for x, y in ROUND_TREES_C))

def hills(p, season, with_kayaks=True, with_bikes=False, radio=None, tile="a"):
    """One hills tile. tile "a" has the river, the kayaks, and the radio
    station, if there is one; tile "b" (hills_b) has other trees and no river;
    tile "c" (hills_c) has its own hill shapes. With with_bikes on, two bikes
    are parked beside the radio station."""
    if tile == "c":
        return hills_c(p, season)
    b = tile == "b"
    if b:
        radio = None
    t = "".join(pine(x, y, p, season) for x, y in (TREES_B if b else TREES))
    rounds = ROUND_TREES_B if b else [(130 if radio else 420, 796), (1500, 800)]
    s = f'''<path fill="{p["hillFar"]}" d="M0,700 C300,620 600,660 960,640 C1300,620 1620,780 1920,700 L1920,910 L0,910 Z"/>
{radio_tower(p, radio) if radio else ""}<path fill="{p["hill"]}" d="M0,780 C400,720 700,760 960,740 C1300,720 1520,840 1920,780 L1920,910 L0,910 Z"/>
{t}{radio_scene(p, season, radio) if radio else ""}{"".join(round_tree(x, y, 36, 30, p, season) for x, y in rounds)}'''
    if b:
        return s
    river = f'''<path fill="{p["river"]}" d="M958,647 C935,668 1000,695 900,730 C760,780 640,800 560,900 L1080,900 C1100,820 1180,790 1240,750 C1320,700 1060,675 1000,662 C985,656 968,650 958,647 Z"/>
<g stroke="{p["riverHi"]}" stroke-width="4" stroke-linecap="round" fill="none">
<path d="M962,672 L980,672"/><path d="M930,700 L972,700"/><path d="M860,758 L930,758"/><path d="M1010,770 L1080,770"/><path d="M760,832 L850,832"/><path d="M930,850 L1030,850"/></g>'''
    return (s + river + (kayaks(p, season) if with_kayaks else "")
            + (radio_bikes(p, season) if with_bikes and radio else ""))

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
