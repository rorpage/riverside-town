"""Small images that are not scenery: the sun, moon, and stars, the weather
effects, the airplane, the cars, and the animals. MainScene.brs places them."""
import os
import random
from PIL import Image, ImageOps
from .art import P, ACCENT, GLASS, DARK, render

DARK_EYE = "#1F2A33"

# Animals are drawn in a larger box and saved at the size they are shown on
# screen, so the screensaver never scales them: PET_SCALE times the box size,
# and SMALL_PET times that for the small size (name_small.png).
PET_SCALE, SMALL_PET = 0.55, 0.65

# Dog breeds: body and dark colors, ears ("floppy" or "pointy"), leg length,
# body length, tail ("up", "curl", or "short"), size, and markings
DOGS = {
    "yellow_lab": dict(body="#D9B26A", dark="#B98F45"),
    "black_lab": dict(body="#2A2D31", dark="#1B1D20"),
    "chocolate_lab": dict(body="#6B4430", dark="#4E2F20"),
    "beagle": dict(body="#F2EDE4", dark="#B7773D", size=0.8, leg=7, saddle="#2B2118", head="#B7773D"),
    "corgi": dict(body="#D9893A", dark="#B86E28", size=0.8, leg=4, ears="pointy", tail="short", belly="#F4F1EA"),
    "dalmatian": dict(body="#F4F1EA", dark="#22272B", leg=10, spots="#22272B", outline="#B9B2A6", far="#D9D4CA"),
    "dachshund": dict(body="#8B4A26", dark="#6A3519", size=0.8, leg=3.5, length=1.25),
    "husky": dict(body="#7D8790", dark="#5B646C", ears="pointy", tail="curl", belly="#F4F1EA"),
}

def dog(body, dark, ears="floppy", leg=9, length=1.0, tail="up", size=1.0, spots=None, saddle=None, head=None,
        belly=None, outline=None, far=None):
    """Returns the SVG for one dog, and its image width and height. The dog is
    drawn in units, with its feet on the line y = 19 + leg, and moved down 5
    units so pointed ears fit."""
    head = head or body
    rx = 12 * length
    cx = 30 - rx
    s = ""
    # Tail
    tx = cx - rx + 2
    if tail == "up":
        s += f'<path d="M{tx},14 Q{tx - 5},10 {tx - 4},3" stroke="{body}" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
    elif tail == "curl":
        s += f'<path d="M{tx},13 Q{tx - 7},10 {tx - 4},4 Q{tx},2 {tx + 2},7" stroke="{body}" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
    else:
        s += f'<path d="M{tx},14 L{tx - 3},12" stroke="{body}" stroke-width="3" stroke-linecap="round"/>'
    # Legs: two at the back and two at the front, the far ones darker
    y0 = 19
    far = far or dark
    for lx, c in ((cx - rx + 4, far), (cx - rx + 7.5, body), (cx + rx - 7, far), (cx + rx - 3.5, body)):
        s += f'<rect x="{lx:.1f}" y="{y0 - 2}" width="3" height="{leg + 2}" rx="1.2" fill="{belly if belly and c == body else c}"/>'
    # Body, markings, neck, and head
    s += f'<ellipse cx="{cx:.1f}" cy="15" rx="{rx:.1f}" ry="6.5" fill="{body}"/>'
    if belly:
        s += f'<ellipse cx="{cx + 2:.1f}" cy="18.5" rx="{rx * 0.8:.1f}" ry="3" fill="{belly}"/>'
    if saddle:
        s += f'<ellipse cx="{cx - 1:.1f}" cy="11.5" rx="{rx * 0.7:.1f}" ry="3.5" fill="{saddle}"/>'
    if spots:
        for sx, sy, r in ((-6, 12, 1.4), (-2, 16, 1.1), (3, 11, 1.3), (6, 15.5, 1.0), (-9, 15, 1.0), (1, 14, 0.9)):
            s += f'<circle cx="{cx + sx * length:.1f}" cy="{sy}" r="{r}" fill="{spots}"/>'
    hx = cx + rx + 2
    s += (f'<path d="M{cx + rx - 5:.1f},12 L{hx - 1:.1f},6 L{hx + 3:.1f},9 L{cx + rx:.1f},17 Z" fill="{head}"/>'
          f'<circle cx="{hx:.1f}" cy="7" r="5.2" fill="{head}"/>'
          f'<ellipse cx="{hx + 5:.1f}" cy="9" rx="3.6" ry="2.6" fill="{belly or head}"/>'
          f'<circle cx="{hx + 8:.1f}" cy="8.2" r="1.2" fill="{DARK_EYE}"/>'
          f'<circle cx="{hx + 1.5:.1f}" cy="5.8" r="0.9" fill="{DARK_EYE}"/>')
    if spots:
        s += f'<circle cx="{hx - 1:.1f}" cy="4" r="0.9" fill="{spots}"/>'
    if belly:
        s += f'<path d="M{hx - 0.5:.1f},6 Q{hx + 2:.1f},11 {hx + 4:.1f},11.5 L{hx + 1:.1f},12 Z" fill="{belly}"/>'
    if ears == "floppy":
        ear = spots or dark
        s += f'<ellipse cx="{hx - 2.5:.1f}" cy="8" rx="2" ry="4" fill="{ear}" transform="rotate(12 {hx - 2.5:.1f} 8)"/>'
    else:
        s += (f'<polygon points="{hx - 4:.1f},4 {hx - 3.5:.1f},-3 {hx:.1f},2.5" fill="{head}"/>'
              f'<polygon points="{hx - 1:.1f},2 {hx + 1:.1f},-4 {hx + 3:.1f},2.5" fill="{head}"/>')
    if outline:
        s = f'<g stroke="{outline}" stroke-width="0.6">{s}</g>'
    k = 2 * size
    w, h = round(48 * k), round((19 + leg + 5.5) * k)
    return f'<g transform="scale({k}) translate(0,5)">{s}</g>', w, h

def write(out):
    def save(content, vb, w, h, name):
        render(content, vb, w, h, os.path.join(out, name))

    def save_pet(content, w, h, name):
        for suffix, k in (("", PET_SCALE), ("_small", PET_SCALE * SMALL_PET)):
            save(content, f"0 0 {w} {h}", round(w * k), round(h * k), f"{name}{suffix}.png")

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
    # The blinking red light on top of the radio tower, shown at 24x24
    save('<circle cx="24" cy="24" r="22" fill="#E74C3C" fill-opacity="0.18"/><circle cx="24" cy="24" r="13" fill="#E74C3C" fill-opacity="0.4"/>'
         '<circle cx="24" cy="24" r="6" fill="#FF6B5B"/>', "0 0 48 48", 48, 48, "tower_light.png")

    # Wheel (drawn separately so it can spin)
    save('<circle cx="32" cy="32" r="32" fill="#1F2A33"/><circle cx="32" cy="32" r="18" fill="#C9D2DA"/>'
         '<g stroke="#5B6770" stroke-width="4"><line x1="32" y1="16" x2="32" y2="48"/><line x1="16" y1="32" x2="48" y2="32"/></g>'
         '<circle cx="32" cy="32" r="6" fill="#5B6770"/>', "0 0 64 64", 64, 64, "wheel.png")

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

    # DeLorean time machine from the first Back to the Future movie: a stainless
    # steel wedge with a gull-wing door, black louvers on the rear slope, and a
    # black strip along the bottom. The time machine parts are the ribbed plutonium
    # reactor on the rear deck (not the Mr. Fusion from the end of the movie and
    # the second movie), a bank of vents at the back, copper coils on the rear
    # side, and a pipe along the side. A town must list it in "cars"; it is not on by default.
    ST, STD, TRIM, PIPE = "#BCC3C9", "#9AA3AA", "#3E4449", "#5B646C"
    delorean = (f'<path fill="{ST}" d="M8,76 L8,52 Q8,46 14,46 L62,44 L102,22 Q106,20 112,20 L156,20 Q162,20 166,24 L206,44 L282,56 Q294,58 294,64 L294,74 Q294,80 286,80 L14,80 Q8,80 8,76 Z"/>'
                f'<path fill="{STD}" d="M8,62 L294,66 L294,74 Q294,80 286,80 L14,80 Q8,80 8,76 Z"/>'
                f'<rect x="12" y="70" width="278" height="8" fill="{TRIM}"/>'
                f'<polygon points="110,26 154,25 196,44 112,44" fill="{GLASS}"/>'
                f'<path d="M106,24 L106,66 M200,44 L204,66" stroke="#868F96" stroke-width="1.5" fill="none"/>'
                + "".join(f'<line x1="{66 + i * 7}" y1="{44 - i * 3.7:.1f}" x2="{70 + i * 7}" y2="{46 - i * 3.7:.1f}" stroke="{TRIM}" stroke-width="2.5"/>' for i in range(6)) +
                f'<path fill="#6E777F" d="M16,46 L16,37 Q16,32 22,32 L56,32 Q62,32 62,37 L62,46 Z"/>'
                + "".join(f'<line x1="{x}" y1="33" x2="{x}" y2="45" stroke="#545C63" stroke-width="2"/>' for x in range(22, 60, 6)) +
                f'<rect x="31" y="36" width="16" height="6" fill="#E0B040"/><polygon points="35,42 39,36 43,42" fill="{DARK}"/>'
                + "".join(f'<rect x="0" y="{y}" width="20" height="5" rx="2" fill="{PIPE}"/><rect x="0" y="{y}" width="3" height="5" fill="{DARK}"/>' for y in (38, 45, 52)) +
                f'<rect x="38" y="59" width="186" height="5" rx="2.5" fill="{PIPE}"/>'
                + "".join(f'<line x1="{x}" y1="52" x2="{x}" y2="64" stroke="#B87333" stroke-width="2"/>' for x in (26, 30, 34)) +
                '<rect x="282" y="60" width="11" height="4" fill="#F6C46A"/><rect x="8" y="62" width="6" height="7" fill="#C0392B"/>'
                + wells([(66, 84), (232, 84)], 24))
    save(delorean, "0 0 300 106", 300, 106, "car_delorean.png")

    # Animals that sit or stand on the sidewalk. MainScene.brs places them at
    # random spots when the screensaver starts. They are drawn larger than they
    # are shown (0.7 times the image size, and 0.75 times that for a small
    # animal) so their edges stay smooth. They are shown a little larger than
    # their real size next to the cars, so they are easy to see.
    def cat(body, dark, eyes, stripes=False, white=None, outline=None):
        """white is a color for the chest, muzzle, and paws. outline draws a thin
        line around a light cat so it shows against the sidewalk."""
        s = (f'<path d="M7,30 Q-1,28 2,18" stroke="{body}" stroke-width="3" fill="none" stroke-linecap="round"/>'
             f'<ellipse cx="13" cy="23" rx="9" ry="8" fill="{body}"/>'
             f'<circle cx="20" cy="12" r="6.5" fill="{body}"/>'
             f'<polygon points="15,9 16,1 20,6" fill="{body}"/><polygon points="21,6 25,1 26,9" fill="{body}"/>'
             f'<rect x="15" y="27" width="3.5" height="5" rx="1.5" fill="{body}"/><rect x="20" y="27" width="3.5" height="5" rx="1.5" fill="{body}"/>'
             f'<circle cx="18" cy="11" r="1.3" fill="{eyes}"/><circle cx="23" cy="11" r="1.3" fill="{eyes}"/>')
        if stripes:
            s += "".join(f'<path d="M{x},16 Q{x + 2},23 {x},29" stroke="{dark}" stroke-width="2" fill="none"/>' for x in (8, 12, 16))
            s += "".join(f'<line x1="{x}" y1="6.5" x2="{x}" y2="9" stroke="{dark}" stroke-width="1"/>' for x in (18.5, 20.5, 22.5))
        if white:
            s += (f'<ellipse cx="18" cy="23" rx="4.5" ry="6" fill="{white}"/><ellipse cx="21" cy="14.5" rx="3.2" ry="2.4" fill="{white}"/>'
                  f'<rect x="15" y="29.5" width="3.5" height="2.5" rx="1.2" fill="{white}"/><rect x="20" y="29.5" width="3.5" height="2.5" rx="1.2" fill="{white}"/>'
                  f'<circle cx="18" cy="11" r="1.3" fill="{eyes}"/><circle cx="23" cy="11" r="1.3" fill="{eyes}"/>')
        if outline:
            s = f'<g stroke="{outline}" stroke-width="0.7">{s}</g>'
        return f'<g transform="scale(2)">{s}</g>'
    save_pet(cat("#22272B", "#22272B", "#F6C46A"), 60, 64, "cat_black")
    save_pet(cat("#5F676E", "#3E444A", "#15181B", True), 60, 64, "cat_gray")
    save_pet(cat("#9A6B42", "#2B2118", "#F6C46A", True), 60, 64, "cat_tabby")
    save_pet(cat("#F4F1EA", "#F4F1EA", "#F2B33D", outline="#B9B2A6"), 60, 64, "cat_white")
    save_pet(cat("#6E767D", "#6E767D", "#F2B33D", white="#F4F1EA"), 60, 64, "cat_gray_white")

    # Dogs, standing and facing right. Each breed is the same drawing with its
    # own body length, legs, ears, tail, colors, and markings. size is how big
    # the breed is, compared with a lab.
    for name, d in DOGS.items():
        body, w, h = dog(**d)
        save_pet(body, w, h, f"dog_{name}")

    def guinea_pig(body, spots):
        s = (f'<ellipse cx="15" cy="12" rx="13" ry="7.5" fill="{body}"/>'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}"/>' for x, y, rx, ry, c in spots) +
             f'<ellipse cx="25" cy="12" rx="6" ry="5.5" fill="{body}"/>'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}"/>' for x, y, rx, ry, c in spots if x > 21) +
             '<ellipse cx="22" cy="7" rx="2.5" ry="2" fill="#C88A6E"/><circle cx="26.5" cy="10.5" r="1.2" fill="#1F2A33"/>'
             '<circle cx="30" cy="13" r="0.9" fill="#C88A6E"/>'
             f'<rect x="8" y="17" width="3" height="3" rx="1" fill="#C88A6E"/><rect x="20" y="17" width="3" height="3" rx="1" fill="#C88A6E"/>')
        return f'<g transform="scale(2)">{s}</g>'
    save_pet(guinea_pig("#E8913A", [(7, 11, 7, 6, "#22272B"), (16, 8, 4, 3, "#22272B"), (26, 10, 3, 3.5, "#22272B")]), 64, 40, "guinea_black_orange")
    save_pet(guinea_pig("#F8FAFC", [(8, 10, 4, 3.5, "#E8913A"), (16, 14, 3.5, 2.5, "#E8913A"), (13, 7, 2.5, 2, "#E8913A"), (26, 9, 2.5, 2.5, "#E8913A")]), 64, 40, "guinea_white_orange")


    # Mirrored car bodies for the far lane, where cars drive right to left
    for n in ["sedan", "van", "jeep", "truck", "sports", "buggy", "delorean"]:
        ImageOps.mirror(Image.open(os.path.join(out, f"car_{n}.png"))).save(os.path.join(out, f"car_{n}_left.png"))
