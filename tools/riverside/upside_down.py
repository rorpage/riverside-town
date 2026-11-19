"""The Upside Down: a dark October version of the town (extras.upside_down).

Each scenery layer and town section is drawn as it is on a fall day, then
color graded to a dim blue gray (grade()), and dark vines are drawn over it
(town_layer() and hills_layer()). The vines on the town are placed from the
outline of each building (building_vines()). There is one image for each
layer, <layer>_upside.png, used at every time of day.

The other images:
- sky_upside.png: a dark sky with a red glow near the horizon
- clouds_upside.png: a dark storm deck with a red glow under the clouds
- bolt_<n>.png: red lightning bolts that flash in the clouds
- spores_a.png, spores_b.png: specks that float up the screen
- street_lamp_upside.png: a dark lamp post with a vine wound around it

components/scene/upsidedown.brs switches to them at random times in October.
"""
import io
import math
import random
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from .art import render, hex_rgb as rgb
from .scenery import puff, wrap
from . import buildings

# The grade: how much color is kept, how bright the result is, and the tint
# it is multiplied by
KEEP_COLOR = 0.18
BRIGHTNESS = 0.62
TINT = (150, 168, 200)

# Vine colors. They are not graded.
VINE = "#1B1215"
VINE_DARK = "#0A0608"
VINE_LIGHT = "#4A3036"
GOO = "#1E1418"

SKY_TOP = "#0B1017"
SKY_GLOW = "#3A161D"   # At 0.62 of the height, like the other skies
CLOUD = "#24222C"
CLOUD_GLOW = "#6B1E27"
BOLT = "#FF3B3B"
BOLT_CORE = "#FFE1E1"
SPORE = "#B8B4BC"

# Tiles join at x=0 and x=1920, so no vine may cross them
X_MIN, X_MAX = 24, 1896

def grade(im):
    """The Upside Down color grade for an RGBA image."""
    rgb = im.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(KEEP_COLOR)
    rgb = ImageEnhance.Brightness(rgb).enhance(BRIGHTNESS)
    rgb = ImageChops.multiply(rgb, Image.new("RGB", rgb.size, TINT))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out

def to_image(content, vb, w, h):
    return Image.open(io.BytesIO(render(content, vb, w, h))).convert("RGBA")

# ---------- Vines ----------
# The vines are placed from the outline of each building, which is read from
# the rendered image: they wrap around the corners of the walls and around
# thin posts, run along the roof lines with loops and tendrils hanging down,
# and grow along the bottom of the walls as thick roots. More roots cross the
# road. Every vine is a smooth curve that gets thinner toward its ends, with a
# dark outline, a highlight on its upper side, and a soft shadow on the wall.

def smooth(pts, n=3):
    """Rounds the corners of a line (Chaikin's method)."""
    for _ in range(n):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            out += [(ax * 0.75 + bx * 0.25, ay * 0.75 + by * 0.25), (ax * 0.25 + bx * 0.75, ay * 0.25 + by * 0.75)]
        out.append(pts[-1])
        pts = out
    return pts

def ribbon(pts, width, fill, opacity=1, dx=0, dy=0):
    """A filled shape along pts. width(t) is the width at t, from 0 at the
    first point to 1 at the last."""
    n = len(pts)
    if n < 2:
        return ""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]
        bx, by = pts[min(i + 1, n - 1)]
        d = math.hypot(bx - ax, by - ay) or 1
        nx, ny = -(by - ay) / d, (bx - ax) / d
        w = width(i / (n - 1)) / 2
        left.append((x + nx * w + dx, y + ny * w + dy))
        right.append((x - nx * w + dx, y - ny * w + dy))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in left + right[::-1]) + " Z"
    op = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    return f'<path d="{d}" fill="{fill}"{op}/>'

def strand(pts, width, shadow=True):
    """One vine along pts with width function width(t): a shadow, a dark
    outline, the body, and a highlight on its upper left side."""
    out = ribbon(pts, lambda t: width(t) + 1, "#000000", 0.28, 3, 3) if shadow else ""
    return (out + ribbon(pts, lambda t: width(t) + 2.2, VINE_DARK) + ribbon(pts, width, VINE)
            + ribbon(pts, lambda t: width(t) * 0.22, VINE_LIGHT, 0.45, -1, -1))

def lumpy(rnd, wmax, ends="tip"):
    """A width function. "tip" is thickest at the start and thin at the end;
    "both" is thin at both ends. The width changes a little along the vine, so
    it does not look like a tube."""
    k1, k2, ph1, ph2 = rnd.uniform(9, 15), rnd.uniform(23, 31), rnd.uniform(0, 6), rnd.uniform(0, 6)
    def w(t):
        shape = (1 - t) ** 0.75 if ends == "tip" else math.sin(math.pi * t) ** 0.55
        return max(0.8, wmax * shape * (1 + 0.1 * math.sin(k1 * t + ph1) + 0.06 * math.sin(k2 * t + ph2)))
    return w

def curl(x, y, a, r, side):
    """Points of a small spiral at the tip of a tendril, starting at (x, y)
    in the direction a."""
    pts = []
    turn = a - side * math.pi / 2
    cx, cy = x - math.cos(turn) * r, y - math.sin(turn) * r
    for i in range(1, 22):
        t = i / 21
        ang = turn + side * t * math.pi * 1.6
        rr = r * (1 - 0.65 * t)
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    return pts

def tendril(rnd, x, y, length, w):
    """A tendril that hangs down from (x, y), swaying a little, with a curl
    at its tip."""
    side, sway, ph = rnd.choice((-1, 1)), rnd.uniform(4, 10), rnd.uniform(0, 6)
    pts = [(x + sway * math.sin(ph + t / 18) - sway * math.sin(ph), y + t) for t in range(0, int(length), 4)]
    if len(pts) < 2:
        return ""
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    pts += curl(bx, by, math.atan2(by - ay, bx - ax), rnd.uniform(3, 6), side)
    return strand(pts, lumpy(rnd, w))

def loop(rnd, xa, ya, xb, yb, w):
    """A vine that hangs in a loop between two points on a roof line."""
    sag = rnd.uniform(12, 28)
    pts = []
    for i in range(25):
        t = i / 24
        pts.append((xa + (xb - xa) * t, ya + (yb - ya) * t + sag * math.sin(math.pi * t)))
    return strand(pts, lumpy(rnd, w, "both"))

def wander(rnd, x0, y0, x1, y1, amp, waves):
    """A smooth line from (x0, y0) to (x1, y1) that bends from side to side."""
    ph1, ph2 = rnd.uniform(0, 6), rnd.uniform(0, 6)
    length = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    pts = []
    n = max(8, int(length / 6))
    for i in range(n + 1):
        t = i / n
        off = amp * (math.sin(waves * math.pi * t + ph1) * 0.7 + math.sin(waves * 2.3 * math.pi * t + ph2) * 0.3)
        off *= math.sin(math.pi * t) ** 0.5
        pts.append((min(max(x0 + (x1 - x0) * t + nx * off, X_MIN), X_MAX), y0 + (y1 - y0) * t + ny * off))
    return pts

def wrap_arcs(rnd, cx, ybot, ytop, reach, pitch, w, back=None):
    """A vine wound around something upright at x = cx, from ybot up to ytop.
    The front half of each turn is drawn; it reaches reach pixels to each
    side. With back set to a color, the back half of each turn is drawn too,
    in that color, as a separate string (returned second), for drawing
    behind a post."""
    front, behind = "", ""
    s, k = 0.0, 0
    width = lumpy(rnd, w)
    total = ybot - ytop
    while s < total:
        pts = []
        for i in range(13):
            t = i / 12
            ph = math.pi * t
            pts.append((cx - reach * math.cos(ph) * (1 if k % 2 == 0 else -1), ybot - s - pitch / 2 * t))
        ww = width(min(1, s / total))
        arc = lambda t, ww=ww: ww * (0.55 + 0.45 * math.sin(math.pi * t))
        if k % 2 == 0:
            front += strand(pts, arc)
        elif back:
            behind += ribbon(pts, lambda t, ww=ww: ww * 0.8, back)
        s += pitch / 2
        k += 1
    return front, behind

def corner_wrap(rnd, edge, side, ybot, ytop, w):
    """A vine that winds around the corner of a wall at x = edge. side is 1
    for a left corner (the wall is to the right) and -1 for a right corner.
    Each turn shows as a long curve on the front of the wall, then the vine
    goes around the corner out of sight for a short distance."""
    out, y = "", ybot
    width = lumpy(rnd, w)
    while y - 30 > ytop:
        h = min(rnd.uniform(55, 95), y - ytop)
        reach = rnd.uniform(14, 26)
        lean = rnd.uniform(-0.25, 0.25)
        pts = []
        for i in range(17):
            t = i / 16
            pts.append((edge + side * (reach * math.sin(math.pi * t) + 2), y - h * (t + lean * math.sin(2 * math.pi * t) / 6)))
        ww = width((ybot - y) / max(1, ybot - ytop))
        out += strand(pts, lambda t, ww=ww: ww * (0.5 + 0.5 * math.sin(math.pi * t) ** 0.5))
        y -= h + rnd.uniform(8, 16)
    return out

def branched(rnd, pts, w, shoots):
    """A vine along pts, thin at both ends, with side shoots that end in thin
    tips, some with a curl."""
    out = strand(pts, lumpy(rnd, w, "both"))
    for _ in range(shoots):
        i = rnd.randint(len(pts) // 5, len(pts) * 4 // 5)
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        a = math.atan2(by - ay, bx - ax) + rnd.choice((-1, 1)) * rnd.uniform(0.35, 0.8)
        length = rnd.uniform(50, 150)
        sp = wander(rnd, bx, by, bx + math.cos(a) * length, by + math.sin(a) * length, 6, 1.5)
        if rnd.random() < 0.5:
            (cx, cy), (dx, dy) = sp[-2], sp[-1]
            sp += curl(dx, dy, math.atan2(dy - cy, dx - cx), rnd.uniform(3, 5), rnd.choice((-1, 1)))
        out += strand(sp, lumpy(rnd, w * rnd.uniform(0.35, 0.55)))
    return out

def opaque(im):
    return im.getchannel("A").point(lambda v: 255 if v > 128 else 0)

def column_top(mask, x):
    """The highest opaque pixel in column x of the mask, or None."""
    box = mask.crop((x, 0, x + 1, mask.height)).getbbox()
    return box[1] if box else None

def runs(mask, y, x0, x1):
    """The opaque runs of pixels in row y between x0 and x1, as (start, end)."""
    row = [mask.getpixel((x, y)) for x in range(max(0, x0), min(mask.width, x1))]
    out, start = [], None
    for i, v in enumerate(row + [0]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((x0 + start, x0 + i))
            start = None
    return out

# Building types whose walls go down to the sidewalk. The others (the gas
# station, the drive-through, and the gazebo) get vines on their roof line and
# wrapped around their posts.
WALLED = {"house", "shop", "church", "school", "columned_hall"}
SKIP = {"tree", "bike_rack"}

def building_vines(rnd, mask, top_y, b, x0, w):
    """The vines on one building. mask is the opaque pixels of the town
    section image, which starts at screen y = top_y."""
    out = ""
    x1 = x0 + w
    def top(x):
        t = column_top(mask, int(min(max(x, 0), mask.width - 1)))
        return None if t is None else t + top_y
    walls = runs(mask, 880 - top_y, x0, x1)
    if b["type"] in WALLED and walls:
        left, right = walls[0][0], walls[-1][1] - 1
        # A thick root along the bottom of the wall
        out += strand(wander(rnd, max(X_MIN, left - 30), rnd.uniform(924, 934), min(X_MAX, right + 30),
                             rnd.uniform(924, 934), 5, 3), lumpy(rnd, rnd.uniform(10, 15), "both"))
        # Vines climb one corner, and sometimes both
        corners = [(1, left), (-1, right)]
        rnd.shuffle(corners)
        if rnd.random() < 0.6:
            corners = corners[:1]
        for side, edge in corners:
            eave = top(edge + side * 6)
            if eave is None:
                continue
            # A thin stem climbs the corner, and a thick vine winds around it,
            # up to the eave
            out += strand(wander(rnd, edge + side * 3, 932, edge + side * 5, eave + 6, 3, 2), lumpy(rnd, 4))
            out += corner_wrap(rnd, edge, side, 930, eave + 8, rnd.uniform(8, 11))
            # Then it runs along the roof line toward the middle
            run = w * rnd.uniform(0.35, 0.7)
            line, x, last = [], edge + side * 6, eave
            while abs(x - edge) < run:
                t = top(x)
                if t is None or abs(t - last) > 16:
                    break
                line.append((x, t + 5))
                last, x = t, x + side * 6
            if len(line) > 3:
                line = smooth(line, 2)
                out += strand(line, lumpy(rnd, rnd.uniform(6, 9)))
                # Loops and tendrils hang from it
                i = rnd.randint(2, 6)
                while i < len(line) - 4:
                    lx, ly = line[i]
                    if rnd.random() < 0.35 and i + 20 < len(line):
                        out += loop(rnd, lx, ly, line[i + 20][0], line[i + 20][1], rnd.uniform(4, 6))
                        i += 20
                    else:
                        if rnd.random() < 0.6:
                            out += tendril(rnd, lx, ly, rnd.uniform(14, 55), rnd.uniform(2.5, 4))
                        i += rnd.randint(10, 26)
        # One vine climbs across the wall on a wide building
        if right - left > 180:
            xa = rnd.uniform(left + 40, right - 40)
            ya = top(xa)
            if ya is not None:
                xb = min(max(xa + rnd.uniform(-90, 90), left + 20), right - 20)
                out += strand(wander(rnd, xa, 930, xb, max(ya + 30, 700), 18, 2.5), lumpy(rnd, rnd.uniform(7, 10)))
    elif b["type"] not in SKIP:
        # A vine climbs from the sidewalk, and tendrils hang from the roof line
        xa = rnd.uniform(x0 + 10, x1 - 10)
        t = top(xa)
        if t is not None and t < 880:
            out += strand(wander(rnd, xa, 932, xa + rnd.uniform(-30, 30), t + 20, 10, 2), lumpy(rnd, rnd.uniform(6, 8)))
        xs = sorted(rnd.uniform(x0 + 10, x1 - 10) for _ in range(max(2, w // 70)))
        for x in xs:
            t = top(x)
            if t is not None and t < 880:
                out += tendril(rnd, x, t + 4, rnd.uniform(20, 60), rnd.uniform(3, 5))
    return out

def town_layer(base, section, seed, y0):
    """One town section in the Upside Down. base is its image, which starts
    at screen y = y0; section is its list of (building, x)."""
    rnd = random.Random(seed)
    mask = opaque(base)
    out = goo(rnd, 10, 905, 1070)
    # Roots across the road, thin at both ends
    # One root in each fifth of the section, so they do not bunch together
    for k in range(5):
        xa = 130 + k * 340 + rnd.uniform(-40, 60)
        xb = xa + rnd.uniform(260, 420)
        if rnd.random() < 0.5:
            xa, xb = xb, xa
        pts = wander(rnd, xa, rnd.uniform(960, 1060), xb, rnd.uniform(960, 1060), rnd.uniform(8, 22), rnd.uniform(1, 2.5))
        out += branched(rnd, pts, rnd.uniform(11, 18), rnd.randint(1, 3))
    for b, x in section:
        out += building_vines(rnd, mask, y0, b, x, buildings.width(b))
    return with_vines(base, out, f"0 {y0} 1920 {base.height}", 1920, base.height)

def hills_layer(base, seed, y0):
    """A hills tile in the Upside Down: thinner vines across the hills,
    because they are farther away."""
    rnd = random.Random(seed)
    out = ""
    for _ in range(10):
        xa = rnd.uniform(X_MIN, X_MAX - 300)
        xb = min(X_MAX, xa + rnd.uniform(200, 420))
        out += strand(wander(rnd, xa, rnd.uniform(790, 900), xb, rnd.uniform(790, 900), 14, 2),
                      lumpy(rnd, rnd.uniform(4, 7), "both"), shadow=False)
    return with_vines(base, out, f"0 {y0} 1920 {base.height}", 1920, base.height)

def goo(rnd, n, ymin, ymax):
    """Dark patches on the ground."""
    out = ""
    for _ in range(n):
        x, y = rnd.uniform(X_MIN + 90, X_MAX - 90), rnd.uniform(ymin, ymax)
        out += (f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(30, 80):.0f}" ry="{rnd.uniform(5, 12):.0f}" '
                f'fill="{GOO}" fill-opacity="{rnd.uniform(0.3, 0.5):.2f}"/>')
    return out

def with_vines(base, vines_svg, vb, w, h):
    """base graded, with the vines drawn over it. The vines may reach a few
    pixels past the edge of what base shows, but no farther."""
    out = grade(base)
    v = to_image(vines_svg, vb, w, h)
    reach = opaque(base).filter(ImageFilter.MaxFilter(9))
    v.putalpha(ImageChops.multiply(v.getchannel("A"), reach))
    out.alpha_composite(v)
    return out

# ---------- Sky, clouds, lightning, and spores ----------
def sky():
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY_TOP}"/>'
            f'<stop offset="0.62" stop-color="{SKY_GLOW}"/></linearGradient></defs><rect width="8" height="1080" fill="url(#g)"/>')

def clouds():
    """A dark deck of clouds across the top, and dark clouds under it with a
    red glow on their lower edges. The clouds band is y=90 to y=345."""
    rnd = random.Random(66)
    # The deck starts at the color of the sky at y=90 (see sky()), so there is
    # no line where the clouds image starts
    sky90 = "#" + "".join(f"{round(a + (b - a) * 90 / (1080 * 0.62)):02X}" for a, b in zip(rgb(SKY_TOP), rgb(SKY_GLOW)))
    top = (f'<linearGradient id="deck" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky90}"/>'
           f'<stop offset="0.7" stop-color="{CLOUD}"/></linearGradient>'
           '<rect x="-40" y="90" width="2000" height="90" fill="url(#deck)"/>')
    bumps = "".join(f'<circle cx="{i * 80 + rnd.randint(-20, 20)}" cy="{176 + rnd.randint(-8, 10)}" r="{rnd.randint(30, 52)}"/>'
                    for i in range(24))
    spots = ((80, 230, 1.2), (330, 300, 0.9), (560, 220, 1.35), (820, 280, 1.1), (1050, 210, 1.2),
             (1280, 295, 1.0), (1500, 225, 1.3), (1730, 285, 1.05), (1900, 215, 0.8))
    glow = "".join(puff(x, y + 9, s, CLOUD_GLOW) for x, y, s in spots)
    dark = "".join(puff(x, y, s, CLOUD) for x, y, s in spots)
    # The red glow under the deck is the same bumps, 8 pixels lower
    return wrap(f'<g transform="translate(0,8)" fill="{CLOUD_GLOW}" fill-opacity="0.55">{bumps}</g>'
                + top + f'<g fill="{CLOUD}">{bumps}</g>' + f'<g opacity="0.8">{glow}</g>' + dark)

BOLT_SIZE = (420, 320)
BOLTS = 3

def bolt(seed):
    """A red lightning bolt with branches, BOLT_SIZE pixels, with a red glow
    at the top where it leaves the clouds."""
    w, h = BOLT_SIZE
    rnd = random.Random(seed)
    def path(x, y, a, length, step):
        pts = [(x, y)]
        while len(pts) * step < length:
            a2 = a + rnd.uniform(-0.7, 0.7)
            x += math.cos(a2) * step
            y += math.sin(a2) * step
            x = min(max(x, 20), w - 20)
            pts.append((x, y))
        return pts
    main = path(w / 2 + rnd.uniform(-40, 40), 30, math.pi / 2, h - 50, 18)
    lines = [(main, 1.0)]
    for _ in range(rnd.randint(2, 4)):
        i = rnd.randint(2, len(main) - 4)
        x, y = main[i]
        lines.append((path(x, y, math.pi / 2 + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.0), rnd.uniform(60, 140), 14), 0.55))
    out = (f'<defs><radialGradient id="glow"><stop offset="0" stop-color="{BOLT}" stop-opacity="0.55"/>'
           f'<stop offset="1" stop-color="{BOLT}" stop-opacity="0"/></radialGradient></defs>'
           f'<ellipse cx="{main[0][0]:.0f}" cy="40" rx="200" ry="70" fill="url(#glow)"/>')
    for pts, k in lines:
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        for width, color, op in ((22, BOLT, 0.08), (12, BOLT, 0.16), (6, BOLT, 0.45), (2.4, BOLT_CORE, 1.0)):
            out += (f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{width * k:.1f}" '
                    'stroke-linejoin="round" stroke-linecap="round"/>')
    return out

SPORES_SIZE = (960, 540)   # Shown at 1920 x 1080, to save texture memory

def spores(seed, n, rmin, rmax):
    """Specks that float in the air, for one 1920 x 1080 screen, drawn at half
    size. The image repeats from top to bottom, so specks near the top or
    bottom edge are drawn again on the other side."""
    w, h = SPORES_SIZE
    rnd = random.Random(seed)
    out = (f'<defs><radialGradient id="s"><stop offset="0" stop-color="{SPORE}" stop-opacity="1"/>'
           f'<stop offset="0.45" stop-color="{SPORE}" stop-opacity="0.6"/>'
           f'<stop offset="1" stop-color="{SPORE}" stop-opacity="0"/></radialGradient></defs>')
    for _ in range(n):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(rmin, rmax)
        op = rnd.uniform(0.25, 0.65)
        for dy in (-h, 0, h):
            if -r <= y + dy <= h + r:
                out += f'<circle cx="{x:.1f}" cy="{y + dy:.1f}" r="{r:.1f}" fill="url(#s)" opacity="{op:.2f}"/>'
    return out

def lamp_vines(x):
    """A vine wound around a street lamp post (see street_lamp() in
    buildings.py). Returns the part behind the post and the part in front of
    it."""
    rnd = random.Random(4)
    front, back = wrap_arcs(rnd, x, 932, 830, 6, 22, 4.5, back=VINE_DARK)
    tip = tendril(rnd, x + 4, 828, 26, 2.5)
    return back, front + tip
