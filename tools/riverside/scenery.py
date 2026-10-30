"""The scenery layers behind the town: sky, clouds, mountains, hills with the
river, and the street."""
import random
from .art import WHITE, wall, round_tree, pine, is_dark, bicycle, text, fit_size, snow_flat, snow_ridge, pumpkins

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
def near_b(p, season):
    pts = " ".join(f"{x},{y}" for x, y in NEAR_B_PTS)
    s = f'<polygon fill="{p["mid"]}" points="0,760 {pts} 1920,760"/>'
    # Small snow caps on the highest peaks in other seasons, like the first tile
    return s + snow_caps(NEAR_B_PTS, 0.5 if season == "winter" else 0.22, p["snow"])

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

# Two people riding bikes on the top of the near hill, far away, so they are
# small. Each is (x of the left end, color, facing left). They are not drawn
# in winter.
CYCLISTS = [(560, "#C0392B", False), (1610, "#2E86C1", True)]
def cyclists(p, season):
    if season == "winter":
        return ""
    return "".join(bicycle(x, near_hill_y(x + 12) + 3, 0.42, wall(c, p), left, (wall(c, p), wall("#E0B89A", p), wall("#34495E", p)))
                   for x, c, left in CYCLISTS)

# ---------- gazebo ----------
def gazebo_width(s):
    return 262 + (150 if s.get("name") else 0)

def town_sign(s, x, p, season):
    """A sign in a white frame with lattice below it, like a town welcome sign."""
    white = wall(WHITE, p)
    board = s.get("sign_color", "#2F5F9E")
    out = (f'<rect x="{x + 6}" y="762" width="9" height="138" fill="{white}"/><rect x="{x + 125}" y="762" width="9" height="138" fill="{white}"/>'
           f'<circle cx="{x + 10.5}" cy="758" r="6" fill="{white}"/><circle cx="{x + 129.5}" cy="758" r="6" fill="{white}"/>'
           f'<rect x="{x + 2}" y="768" width="136" height="66" fill="{white}"/><rect x="{x + 7}" y="773" width="126" height="56" fill="{board}"/>'
           + snow_flat(season, p, x + 2, 768, 136))
    size = fit_size(s["name"], s["font"], s["weight"], 19, 114, 1)
    out += text(s["name"], s["font"], s["weight"], size, x + 70, 800, WHITE, 1)
    if s.get("small_line"):
        small = fit_size(s["small_line"], s["font"], 600, 10, 110, 1.5)
        out += (f'<line x1="{x + 20}" y1="807" x2="{x + 120}" y2="807" stroke="{WHITE}" stroke-width="0.8"/>'
                + text(s["small_line"], s["font"], 600, small, x + 70, 821, WHITE, 1.5))
    # Lattice under the sign
    out += f'<g stroke="{white}" stroke-width="2"><rect x="{x + 15}" y="840" width="110" height="46" fill="none"/>'
    for i in range(-4, 12):
        x0 = x + 15 + i * 12
        out += f'<line x1="{x0}" y1="886" x2="{x0 + 46}" y2="840"/><line x1="{x0}" y1="840" x2="{x0 + 46}" y2="886"/>'
    out += '</g>'
    return (f'<defs><clipPath id="lattice{x}"><rect x="{x + 15}" y="840" width="110" height="46"/></clipPath></defs>'
            + out.replace('<g stroke="', f'<g clip-path="url(#lattice{x})" stroke="', 1)
            + f'<rect x="{x + 15}" y="840" width="110" height="46" fill="none" stroke="{white}" stroke-width="2"/>'
            + pumpkins(season, x + 50))

def gazebo_draw(s, x, p, season):
    """An eight-sided gazebo on a brick base, with a shingled roof, a small
    cupola on top, white posts and railings, and front steps, drawn with its
    ground at y=900. It is decorated for each season. With a name, a town sign
    stands to its left."""
    W2, R = p["wall2"], p["roof"]
    out = ""
    if s.get("name"):
        out += town_sign(s, x, p, season)
        x += 150
    white = wall(WHITE, p)
    roof = wall("#5E5850", p)
    brick = wall(s["color"], p)
    # Shadowed inside, behind the posts
    out += f'<rect x="{x + 20}" y="760" width="222" height="98" fill="{R}" fill-opacity="0.35"/>'
    for cx in (52, 210):
        out += f'<rect x="{x + cx - 3}" y="764" width="6" height="92" fill="{wall("#D9E2EA", p)}"/>'
    # Brick base and front steps
    out += (f'<rect x="{x + 10}" y="862" width="242" height="38" fill="{brick}"/>'
            f'<g stroke="{wall("#7E3F2F", p)}" stroke-width="1" stroke-opacity="0.6">'
            + "".join(f'<line x1="{x + 10}" y1="{y}" x2="{x + 252}" y2="{y}"/>' for y in (871, 880, 889)) + '</g>'
            f'<rect x="{x + 6}" y="856" width="250" height="8" fill="{white}"/>')
    for i, (w, y) in enumerate(((64, 862), (74, 874), (84, 886))):
        out += f'<rect x="{x + 131 - w / 2}" y="{y}" width="{w}" height="{900 - y}" fill="{W2}"/><rect x="{x + 131 - w / 2}" y="{y}" width="{w}" height="2" fill="{white}"/>'
    out += (f'<g stroke="{white}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{x + 97}" y1="832" x2="{x + 87}" y2="896"/><line x1="{x + 165}" y1="832" x2="{x + 175}" y2="896"/></g>')
    # Railings on each side of the steps
    for x0, x1 in ((x + 24, x + 97), (x + 165, x + 238)):
        out += f'<rect x="{x0}" y="828" width="{x1 - x0}" height="4" fill="{white}"/><rect x="{x0}" y="850" width="{x1 - x0}" height="3" fill="{white}"/>'
        out += "".join(f'<rect x="{bx}" y="832" width="2" height="18" fill="{white}"/>' for bx in range(x0 + 4, x1, 7))
    # Front posts
    posts = (22, 97, 165, 240)
    for cx in posts:
        out += f'<rect x="{x + cx - 4}" y="760" width="8" height="98" fill="{white}"/>'
    # Eave, roof, and cupola
    out += (f'<rect x="{x + 2}" y="748" width="258" height="14" fill="{white}"/>'
            + "".join(f'<path d="M{x + 6 + i * 25},762 Q{x + 18.5 + i * 25},770 {x + 31 + i * 25},762" fill="none" stroke="{white}" stroke-width="2"/>' for i in range(10)) +
            f'<polygon points="{x - 8},750 {x + 270},750 {x + 196},698 {x + 66},698" fill="{roof}"/>'
            f'<g stroke="#000" stroke-opacity="0.12" stroke-width="1.2">'
            + "".join(f'<line x1="{x - 8 + (750 - y) * 74 / 52:.1f}" y1="{y}" x2="{x + 270 - (750 - y) * 74 / 52:.1f}" y2="{y}"/>' for y in range(742, 700, -8)) + '</g>'
            f'<rect x="{x + 104}" y="672" width="54" height="28" fill="{white}"/>'
            + "".join(f'<rect x="{x + 110 + i * 15}" y="678" width="10" height="14" fill="{R}"/>' for i in range(3)) +
            f'<polygon points="{x + 96},674 {x + 166},674 {x + 150},658 {x + 112},658" fill="{roof}"/>'
            f'<rect x="{x + 112}" y="654" width="38" height="5" fill="{white}"/>'
            + snow_ridge(season, p, (x - 6, 747), (x + 66, 696), (x + 196, 696), (x + 268, 747))
            + snow_ridge(season, p, (x + 98, 671), (x + 112, 656), (x + 150, 656), (x + 164, 671)))
    # String lights along the eave at dusk and night
    if is_dark(p):
        out += "".join(f'<circle cx="{x + 8 + i * 12.4:.1f}" cy="{765 + (3 if i % 2 else 0)}" r="2" fill="#F6E7B0"/>' for i in range(21))
    # Decorations for each season
    if season == "fall":
        for a, b in zip(posts, posts[1:]):
            if a == 97:
                continue
            out += (f'<path d="M{x + a},768 Q{x + (a + b) / 2},790 {x + b},768" fill="none" stroke="#C8662E" stroke-width="5" stroke-dasharray="4 3"/>'
                    f'<path d="M{x + a},770 Q{x + (a + b) / 2},792 {x + b},770" fill="none" stroke="#B5523F" stroke-width="3" stroke-dasharray="3 5"/>')
        for cx in posts:
            out += f'<path d="M{x + cx},856 L{x + cx - 6},800 M{x + cx},856 L{x + cx + 6},804 M{x + cx},856 L{x + cx},796" stroke="#C9A55B" stroke-width="2.5"/>'
        out += (f'<rect x="{x + 18}" y="884" width="40" height="16" rx="3" fill="#D9B45B"/><rect x="{x + 204}" y="884" width="40" height="16" rx="3" fill="#D9B45B"/>'
                + pumpkins(season, x + 30, 884) + pumpkins(season, x + 186) + pumpkins(season, x + 222, 884))
    elif season == "winter":
        for cx in posts:
            out += (f'<circle cx="{x + cx}" cy="790" r="9" fill="none" stroke="#2F5D3A" stroke-width="5"/>'
                    f'<path d="M{x + cx - 4},799 L{x + cx},795 L{x + cx + 4},799" stroke="#C0392B" stroke-width="2.5" fill="none"/>')
    else:
        flowers = ["#F2B8C6", "#F6C46A", "#E8703F"] if season == "spring" else ["#E86A92", "#F8FAFC", "#B5523F"]
        for cx in (60, 131, 202):
            out += (f'<line x1="{x + cx}" y1="762" x2="{x + cx}" y2="774" stroke="{R}" stroke-width="1"/>'
                    f'<path d="M{x + cx - 8},774 Q{x + cx},786 {x + cx + 8},774 Z" fill="#6B4A3A"/>'
                    f'<circle cx="{x + cx}" cy="776" r="7" fill="#5E8B6B"/>'
                    + "".join(f'<circle cx="{x + cx + dx}" cy="{774 + dy}" r="2.4" fill="{c}"/>' for (dx, dy), c in zip(((-4, 0), (3, -2), (0, 4), (5, 3)), flowers * 2)))
    return out

# The gazebo stands on the near hill to the left of the river, where the hill
# is high enough to show above most roofs. It is drawn at half size, because
# the hills are farther away than the street. GAZEBO_X is the center of the
# gazebo; its ground is the top of the near hill there.
GAZEBO_X, GAZEBO_SCALE = 250, 0.5

def near_hill_y(x):
    """The y of the top of the near hill at x. The hill is two curves:
    (0,780) C(400,720) (700,760) (960,740), and (960,740) C(1300,720)
    (1520,840) (1920,780)."""
    if x < 960:
        p0, p1, p2, p3 = (0, 780), (400, 720), (700, 760), (960, 740)
    else:
        p0, p1, p2, p3 = (960, 740), (1300, 720), (1520, 840), (1920, 780)
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        bx = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        lo, hi = (t, hi) if bx < x else (lo, t)
    return (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]

def gazebo_scene(p, season, spec):
    # The gazebo itself is 262 pixels wide, after the sign if there is one
    center = (150 if spec.get("name") else 0) + 131
    ground = near_hill_y(GAZEBO_X) + 6
    k = GAZEBO_SCALE
    return (f'<g transform="translate({GAZEBO_X - center * k:.1f},{ground - 900 * k:.1f}) scale({k})">'
            + gazebo_draw(spec, 0, p, season) + '</g>')

def hills(p, season, with_kayaks=True, with_cyclists=False, gazebo=None):
    t = "".join(pine(x, b, p, season) for x, b in TREES)
    s = f'''<path fill="{p["hillFar"]}" d="M0,700 C300,620 600,660 960,640 C1300,620 1620,780 1920,700 L1920,910 L0,910 Z"/>
<path fill="{p["hill"]}" d="M0,780 C400,720 700,760 960,740 C1300,720 1520,840 1920,780 L1920,910 L0,910 Z"/>
{t}{round_tree(420, 796, 36, 30, p, season)}{round_tree(1500, 800, 36, 30, p, season)}
<path fill="{p["river"]}" d="M958,647 C935,668 1000,695 900,730 C760,780 640,800 560,900 L1080,900 C1100,820 1180,790 1240,750 C1320,700 1060,675 1000,662 C985,656 968,650 958,647 Z"/>
<g stroke="{p["riverHi"]}" stroke-width="4" stroke-linecap="round" fill="none">
<path d="M962,672 L980,672"/><path d="M930,700 L972,700"/><path d="M860,758 L930,758"/><path d="M1010,770 L1080,770"/><path d="M760,832 L850,832"/><path d="M930,850 L1030,850"/></g>'''
    return (s + (gazebo_scene(p, season, gazebo) if gazebo else "") + (kayaks(p, season) if with_kayaks else "")
            + (cyclists(p, season) if with_cyclists else ""))

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
