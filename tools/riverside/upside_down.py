"""The Upside Down: a dark October version of the town (extras.upside_down).

Each scenery layer and town section is drawn as it is on a fall day, then
color graded to a dim blue gray (grade()), and dark vines are drawn over the
ground and the walls (vines()). The vines are masked to the shape of the
layer, so they stop at the roof lines and the tops of the hills. There is
one image for each layer, <layer>_upside.png, used at every time of day.

The other images:
- sky_upside.png: a dark sky with a red glow near the horizon
- clouds_upside.png: a dark storm deck with a red glow under the clouds
- bolt_<n>.png: red lightning bolts that flash in the clouds
- spores_a.png, spores_b.png: specks that float up the screen
- street_lamp_upside.png: a dark lamp post with a vine around it

components/scene/upsidedown.brs shows them in October.
"""
import io
import math
import random
from PIL import Image, ImageChops, ImageEnhance
from .art import render, hex_rgb as rgb
from .scenery import puff, wrap

# The grade: how much color is kept, how bright the result is, and the tint
# it is multiplied by
KEEP_COLOR = 0.18
BRIGHTNESS = 0.62
TINT = (150, 168, 200)

# Vine colors. They are not graded.
VINE = "#0F0A0C"
VINE_EDGE = "#2E2024"
VINE_VEIN = "#4E2A31"
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
def vine_points(rnd, x, y, angle, length, ymin, ymax, step=4.0):
    """Points along a vine that starts at (x, y) and grows in the direction
    angle (in radians). The amount it turns changes slowly, so it bends in
    smooth curves. It turns back at the tile edges and at ymin and ymax."""
    pts, a, turn = [(x, y)], angle, rnd.uniform(-0.03, 0.03)
    for _ in range(int(length / step)):
        turn = min(max(turn + rnd.uniform(-0.012, 0.012), -0.045), 0.045)
        # Bend, but keep the general direction
        a += turn
        a = a * 0.96 + angle * 0.04
        x += math.cos(a) * step
        y += math.sin(a) * step
        if x < X_MIN or x > X_MAX:
            a = angle = math.pi - a
            x = min(max(x, X_MIN), X_MAX)
        if y < ymin or y > ymax:
            a = angle = -a
            turn = -turn
            y = min(max(y, ymin), ymax)
        pts.append((x, y))
    return pts

def ribbon(pts, w0, w1, fill, opacity=1):
    """A filled shape along pts that narrows from width w0 to width w1."""
    n = len(pts)
    if n < 2:
        return ""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]
        bx, by = pts[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        # Narrow quickly near the tip
        t = i / (n - 1)
        w = (w1 + (w0 - w1) * (1 - t) ** 0.8) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in left + right[::-1]) + " Z"
    op = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    return f'<path d="{d}" fill="{fill}"{op}/>'

def vine(rnd, x, y, angle, length, w0, ymin, ymax, depth=1):
    """One vine with a few side shoots. The shoots have their own shoots, down
    to depth levels."""
    pts = vine_points(rnd, x, y, angle, length, ymin, ymax)
    # A lighter edge, a dark body, and a faint shine along the top side
    shine = [(px - w0 * 0.12, py - w0 * 0.12) for px, py in pts]
    # A round end where the vine starts
    x0, y0 = pts[0]
    out = (f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{w0 / 2 + 1.25:.1f}" fill="{VINE_EDGE}"/>'
           + ribbon(pts, w0 + 2.5, 1.5, VINE_EDGE) + f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{w0 / 2:.1f}" fill="{VINE}"/>'
           + ribbon(pts, w0, 0.8, VINE)
           + ribbon(shine[: len(pts) * 3 // 4], w0 * 0.25, 0.3, VINE_VEIN, 0.7))
    if depth > 0:
        for _ in range(rnd.randint(1, 2)):
            i = rnd.randint(len(pts) // 4, max(len(pts) // 4, len(pts) * 3 // 4))
            if i < 1 or i >= len(pts):
                continue
            (ax, ay), (bx, by) = pts[i - 1], pts[i]
            a = math.atan2(by - ay, bx - ax) + rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.9)
            w = w0 * (1 - i / len(pts)) ** 0.8 * 0.7
            if w > 2:
                out += vine(rnd, bx, by, a, length * rnd.uniform(0.35, 0.6), w, ymin, ymax, depth - 1)
    return out

def goo(rnd, n, ymin, ymax):
    """Dark patches on the ground."""
    out = ""
    for _ in range(n):
        x, y = rnd.uniform(X_MIN + 40, X_MAX - 40), rnd.uniform(ymin, ymax)
        out += (f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(30, 90):.0f}" ry="{rnd.uniform(5, 14):.0f}" '
                f'fill="{GOO}" fill-opacity="{rnd.uniform(0.35, 0.6):.2f}"/>')
    return out

def town_vines(seed):
    """Vines for one town section: patches and vines along the road and the
    sidewalk, and vines that climb the walls from the sidewalk."""
    rnd = random.Random(seed)
    out = goo(rnd, 16, 905, 1070)
    for _ in range(11):
        # Along the road and the sidewalk
        out += vine(rnd, rnd.uniform(X_MIN, X_MAX), rnd.uniform(915, 1072), rnd.choice((0, math.pi)) + rnd.uniform(-0.15, 0.15),
                    rnd.uniform(300, 640), rnd.uniform(14, 24), 905, 1078)
    for _ in range(14):
        # Up the walls, from the sidewalk. The mask stops them at the roof lines.
        out += vine(rnd, rnd.uniform(X_MIN, X_MAX), rnd.uniform(928, 945), -math.pi / 2 + rnd.uniform(-0.5, 0.5),
                    rnd.uniform(160, 360), rnd.uniform(11, 18), 560, 1000)
    return out

def hills_vines(seed):
    """Thinner vines across the hills, because they are farther away."""
    rnd = random.Random(seed)
    out = ""
    for _ in range(16):
        out += vine(rnd, rnd.uniform(X_MIN, X_MAX), rnd.uniform(760, 905), rnd.choice((0, math.pi)) + rnd.uniform(-0.3, 0.3),
                    rnd.uniform(200, 420), rnd.uniform(5, 8), 700, 908)
    return out

def with_vines(base, vines_svg, vb, w, h):
    """base graded, with the vines drawn over it only where base is not
    clear."""
    out = grade(base)
    v = to_image(vines_svg, vb, w, h)
    v.putalpha(ImageChops.multiply(v.getchannel("A"), base.getchannel("A")))
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

def lamp_vine(x):
    """A vine that winds up a street lamp post (see street_lamp() in
    buildings.py)."""
    pts = []
    for i in range(60):
        t = i / 59
        y = 934 - t * 118
        pts.append((x + math.sin(t * math.pi * 5) * 5, y))
    return ribbon(pts, 5, 1.5, VINE_EDGE) + ribbon(pts, 3.6, 1, VINE)
