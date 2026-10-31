"""The special cars: cars from movies. MainScene.brs lists them in allCars with
special: true, and a town turns them on with "special_cars" in town.json.

Each car is drawn facing right, in the coordinates of a reference drawing that
is 6 times the size of a small picture of the car. SPECS gives the scale and
offset that turn those coordinates into the car image. The wheels are separate
images, so they can spin; each car has its own wheel image (wheel_<name>.png).

A car with text or a logo on its side (Herbie, the Ecto-1, and Lightning
McQueen) has a left image that is drawn again instead of mirrored, so the text
does not read backward. The others are mirrored in sprites.py.
"""
from .art import text

DARK = "#1F2A33"
CHROME, CHROME_D = "#E3E7EA", "#9AA3AA"
WINDOW = "#26303A"
RED_LIGHT, AMBER = "#C0392B", "#F6C46A"

# name: image width and height, scale, x and y offset, wheel centers and wheel
# radius in reference coordinates. Car coordinates are reference times scale
# plus the offset.
SPECS = {
    "aston": dict(w=300, h=106, k=0.43, tx=-12, ty=-4, wheels=[(228, 205), (595, 205)], r=45),
    "herbie": dict(w=270, h=106, k=0.42, tx=-10, ty=14, wheels=[(172, 172), (540, 172)], r=45),
    "kitt": dict(w=300, h=92, k=0.44, tx=-12, ty=4, wheels=[(180, 148), (545, 148)], r=42),
    "ecto1": dict(w=360, h=150, k=0.48, tx=-14, ty=-6, wheels=[(200, 270), (640, 270)], r=37),
    "delorean": dict(w=310, h=112, k=0.44, tx=-10, ty=-8, wheels=[(195, 212), (580, 212)], r=40),
    "mcqueen": dict(w=300, h=106, k=0.46, tx=-8, ty=-8, wheels=[(180, 171), (550, 171)], r=61),
    "mustang": dict(w=310, h=96, k=0.44, tx=-24, ty=-16, wheels=[(215, 212), (607, 212)], r=40),
}

def placed(name):
    """The car's size and wheels in image pixels: w, h, wheel centers, wheel
    radius, and the lowest pixel of the tires. These must match allCars in
    MainScene.brs and CARS in previews.py."""
    s = SPECS[name]
    k = s["k"]
    wheels = [(round(x * k + s["tx"]), round(y * k + s["ty"])) for x, y in s["wheels"]]
    r = round(s["r"] * k)
    return s["w"], s["h"], wheels, r, wheels[0][1] + r

def ref(name, content, left=False):
    """Moves content from reference coordinates into the car image. With left
    on, the car is turned to face left."""
    s = SPECS[name]
    g = f'<g transform="translate({s["tx"]},{s["ty"]}) scale({s["k"]})">{content}</g>'
    if left:
        g = f'<g transform="translate({s["w"]},0) scale(-1,1)">{g}</g>'
    return g

def wells(name, r_extra=8, stroke=None):
    """Dark wheel arches behind the wheels, in reference coordinates"""
    s = SPECS[name]
    line = f' stroke="{stroke}" stroke-width="4"' if stroke else ""
    return "".join(f'<circle cx="{x}" cy="{y}" r="{s["r"] + r_extra}" fill="{DARK}"{line}/>' for x, y in s["wheels"])

def aston():
    # Aston Martin DB5 from Goldfinger: silver birch, a long hood, a sloped
    # fastback roof, a side vent behind the front wheel, and chrome bumpers.
    BODY, LOW, LINE = "#CDD2D6", "#B3BABF", "#8E969C"
    s = (f'<path fill="{BODY}" stroke="{LINE}" stroke-width="3" d="M48,200 L44,176 Q46,146 58,130 Q78,120 120,116 '
         f'Q170,104 214,84 Q258,64 300,60 L398,59 Q414,60 424,72 L466,112 Q560,116 640,124 Q690,132 702,156 '
         f'L708,190 Q706,206 690,210 L60,212 Q48,210 48,200 Z"/>'
         f'<path fill="{LOW}" d="M47,160 L704,166 L708,190 Q706,206 690,210 L60,212 Q48,210 47,200 Z"/>'
         + wells("aston") +
         f'<path fill="{WINDOW}" d="M200,104 Q236,84 284,76 L284,118 L206,118 Z"/>'
         f'<path fill="{WINDOW}" d="M296,74 L404,72 L446,116 L296,118 Z"/>'
         f'<path d="M290,70 L290,208 M462,112 L466,208" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<rect x="300" y="132" width="22" height="5" rx="2" fill="{CHROME_D}"/>'
         f'<rect x="478" y="142" width="44" height="10" rx="4" fill="#5B646C"/>'
         f'<ellipse cx="690" cy="150" rx="10" ry="9" fill="{AMBER}" stroke="{CHROME}" stroke-width="3"/>'
         f'<rect x="48" y="140" width="10" height="24" rx="3" fill="{RED_LIGHT}"/>'
         f'<rect x="38" y="178" width="26" height="12" rx="5" fill="{CHROME}"/>'
         f'<rect x="690" y="180" width="24" height="12" rx="5" fill="{CHROME}"/>')
    return ref("aston", s), ref("aston", s, True)

def herbie(left):
    # Herbie, the Love Bug: a 1963 VW Beetle in pearl white with the number 53
    # in a circle on the door. The racing stripes run over the middle of the
    # top, so they do not show from the side.
    BODY, LINE = "#E6E4D8", "#B9B7AA"
    shape = ("M70,178 Q66,140 82,108 Q104,66 150,36 Q196,8 262,4 L330,4 Q382,8 410,34 L446,70 "
             "L440,64 C548,62 612,84 622,132 L620,170 L612,180 L80,182 Z")
    s = (f'<clipPath id="herbie_body"><path d="{shape}"/></clipPath>'
         f'<path fill="{BODY}" stroke="{LINE}" stroke-width="3" d="M70,178 Q66,140 82,108 Q104,66 150,36 '
         f'Q196,8 262,4 L330,4 Q382,8 410,34 L440,64 C548,62 612,84 622,132 L620,170 L612,180 L80,182 Z"/>'
         # Fenders, with a line where they meet the body
         f'<path fill="{BODY}" stroke="{LINE}" stroke-width="3" d="M86,184 Q86,112 166,104 Q238,104 254,184 Z"/>'
         f'<path fill="{BODY}" stroke="{LINE}" stroke-width="3" d="M466,184 Q470,106 540,102 Q606,104 622,172 L620,184 Z"/>'
         + wells("herbie", 6) +
         # Running board between the fenders
         f'<rect x="246" y="172" width="226" height="12" rx="4" fill="#2B2F33"/>'
         # Rear window: it is cut to the body shape, so it reaches the rear outline
         f'<path fill="{WINDOW}" clip-path="url(#herbie_body)" d="M96,60 L150,0 L190,0 L188,26 Q160,40 132,70 Z"/>'
         f'<path fill="{WINDOW}" d="M200,72 Q200,26 246,22 L292,20 L292,72 Z"/>'
         f'<path fill="{WINDOW}" d="M306,20 L380,22 Q398,24 408,40 L432,70 L306,72 Z"/>'
         f'<path d="M298,18 L298,172 M442,72 L446,172" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<path d="M308,84 L330,84 L326,92 L312,92 Z" fill="{CHROME_D}"/>'
         f'<rect x="196" y="78" width="248" height="4" fill="{LINE}" fill-opacity="0.6"/>'
         # Headlight on top of the front fender, and the tail light on the rear fender
         f'<ellipse cx="600" cy="128" rx="9" ry="12" fill="{AMBER}" stroke="{CHROME}" stroke-width="4"/>'
         f'<ellipse cx="90" cy="130" rx="6" ry="10" fill="{RED_LIGHT}"/>'
         # Chrome bumpers with guards
         f'<rect x="34" y="150" width="56" height="12" rx="5" fill="{CHROME}"/><rect x="40" y="136" width="10" height="34" rx="4" fill="{CHROME}"/>'
         f'<rect x="604" y="150" width="44" height="12" rx="5" fill="{CHROME}"/><rect x="626" y="136" width="10" height="34" rx="4" fill="{CHROME}"/>')
    s = ref("herbie", s, left)
    # The number on the door is added after the car is turned, so it is not
    # drawn backward
    sp = SPECS["herbie"]
    cx = sp["tx"] + 372 * sp["k"]
    if left:
        cx = sp["w"] - cx
    cy = sp["ty"] + 124 * sp["k"]
    s += (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="#FFFFFF" stroke="#1F2A33" stroke-width="2"/>'
          + text("53", "oswald", 700, 16, cx, cy + 6, "#1F2A33"))
    return s

def kitt():
    # KITT from Knight Rider: a black 1982 Pontiac Trans Am with a long pointed
    # nose and the red scanner light at the front. Light lines show the shape
    # of the black body.
    BODY, LINE = "#16191C", "#7C868E"
    s = (f'<path fill="{BODY}" stroke="{LINE}" stroke-width="4" d="M44,148 L36,128 L38,100 Q42,86 70,82 '
         f'Q140,64 214,36 Q238,26 262,24 L350,22 Q366,22 380,30 L438,58 Q560,74 640,94 Q684,106 700,128 '
         f'L696,144 Q690,154 670,158 L60,162 Q46,158 44,148 Z"/>'
         f'<path d="M44,74 L82,72 L80,84" stroke="{LINE}" stroke-width="4" fill="{BODY}"/>'
         + wells("kitt", 8, LINE) +
         f'<path fill="#4B5864" d="M262,32 L354,30 L418,74 L262,82 Z"/>'
         f'<path d="M262,32 L262,80" stroke="{BODY}" stroke-width="6"/>'
         f'<path d="M50,118 L690,116" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<path d="M256,84 L256,158 M440,78 L470,156" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<circle cx="124" cy="96" r="10" fill="none" stroke="{LINE}" stroke-width="3"/>'
         f'<rect x="270" y="100" width="20" height="6" rx="3" fill="{LINE}"/>'
         f'<path d="M396,64 L412,64 L414,76 L398,76 Z" fill="{LINE}"/>'
         f'<rect x="56" y="128" width="34" height="10" rx="3" fill="{RED_LIGHT}"/>'
         f'<rect x="626" y="126" width="24" height="7" rx="3" fill="{AMBER}"/>'
         # The scanner light on the nose
         f'<rect x="652" y="108" width="38" height="7" rx="3" fill="#FF3B30"/>'
         f'<rect x="648" y="104" width="46" height="15" rx="6" fill="#FF3B30" fill-opacity="0.35"/>')
    return ref("kitt", s), ref("kitt", s, True)

def ecto1(left):
    # The Ecto-1 from Ghostbusters: a white 1959 Cadillac ambulance with red
    # (maroon) rear panels and fins, red stripes along the side, a ladder at
    # the back, and equipment, a siren, and a yellow light on the roof. The
    # logo, a ghost in a red circle with a line across it, is on the front door.
    WHITE, LINE, MAROON = "#F4F4F1", "#BFC3C6", "#8C1C2E"
    s = (  # Antennas and equipment on the roof, drawn behind the body
         f'<path d="M160,22 L160,124 M186,30 L186,124" stroke="#5B646C" stroke-width="6" fill="none"/>'
         f'<rect x="112" y="118" width="300" height="14" rx="3" fill="#9AA3AA"/>'
         f'<rect x="224" y="88" width="96" height="30" rx="10" fill="#C9D2DA" stroke="#7D878F" stroke-width="3"/>'
         f'<rect x="236" y="70" width="44" height="22" rx="6" fill="#AEB7BF"/><path d="M300,60 L300,90" stroke="#7D878F" stroke-width="4"/>'
         f'<rect x="334" y="96" width="54" height="22" rx="6" fill="#B23A3A"/>'
         f'<path d="M388,100 L410,92 L410,124 L388,116 Z" fill="#DADFE3"/>'
         f'<rect x="438" y="98" width="30" height="24" rx="8" fill="#F2C94C"/><rect x="434" y="118" width="38" height="10" rx="3" fill="#9AA3AA"/>'
         # Body
         f'<path fill="{WHITE}" stroke="{LINE}" stroke-width="3" d="M44,268 L38,236 Q40,206 60,196 L72,150 Q78,134 104,132 '
         f'L470,132 Q486,134 496,146 L530,192 Q640,196 724,204 Q748,210 752,236 L750,260 Q746,270 730,272 L60,274 Q46,272 44,268 Z"/>'
         # Red rear panel and fin
         f'<path fill="{MAROON}" d="M74,148 Q80,134 104,134 L290,134 L290,198 L62,200 Z"/>'
         f'<path d="M62,200 Q150,192 290,198" stroke="{WHITE}" stroke-width="5" fill="none"/>'
         f'<path fill="{WINDOW}" d="M306,148 L398,148 L398,196 L306,196 Z"/>'
         f'<path fill="{WINDOW}" d="M410,148 L478,148 Q486,148 492,156 L520,196 L410,196 Z"/>'
         + wells("ecto1", 6) +
         f'<path d="M50,232 L740,228 M50,240 L740,236" stroke="{MAROON}" stroke-width="4" fill="none"/>'
         f'<path d="M300,140 L300,268 M404,140 L404,268 M528,196 L532,268" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<rect x="312" y="210" width="20" height="6" rx="3" fill="#9AA3AA"/><rect x="420" y="210" width="20" height="6" rx="3" fill="#9AA3AA"/>'
         # Ladder at the back
         f'<path d="M166,112 L166,238 M214,112 L214,238" stroke="#C9D2DA" stroke-width="7" fill="none"/>'
         + "".join(f'<path d="M166,{y} L214,{y}" stroke="#C9D2DA" stroke-width="5"/>' for y in (140, 168, 196, 224)) +
         f'<rect x="40" y="206" width="12" height="22" rx="3" fill="{RED_LIGHT}"/>'
         f'<rect x="736" y="214" width="16" height="16" rx="3" fill="{AMBER}"/>'
         f'<rect x="32" y="252" width="40" height="14" rx="6" fill="{CHROME}"/>'
         f'<rect x="716" y="248" width="42" height="16" rx="6" fill="{CHROME}"/>')
    s = ref("ecto1", s, left)
    # The logo is added after the car is turned, so its line keeps its direction
    sp = SPECS["ecto1"]
    k = sp["k"]
    cx = sp["tx"] + 476 * k
    if left:
        cx = sp["w"] - cx
    cy = sp["ty"] + 238 * k
    s += (f'<g transform="translate({cx:.1f},{cy:.1f})">'
          '<circle r="13" fill="#FFFFFF" stroke="#D32F2F" stroke-width="3"/>'
          '<path d="M-5,8 L-5,-3 Q-5,-9 0,-9 Q6,-9 6,-3 L6,4 L8,8 L3,6 L0,8 L-3,6 Z" fill="#FFFFFF" stroke="#1F2A33" stroke-width="1.2"/>'
          '<circle cx="-2" cy="-3" r="1.1" fill="#1F2A33"/><circle cx="2.5" cy="-3" r="1.1" fill="#1F2A33"/>'
          '<path d="M-9,-9 L9,9" stroke="#D32F2F" stroke-width="3"/></g>')
    return s

def delorean():
    # The DeLorean time machine from the first Back to the Future movie: a
    # stainless steel wedge with gull-wing doors and black louvers on the rear
    # slope. The time machine parts sit low on the rear deck: a vent box at the
    # back with slats that face backward, the ribbed reactor in front of it, a
    # pipe with copper coils behind the roof, and a small unit on the roof.
    ST, LOW, LINE, PART, PART_D = "#C3C9CE", "#9EA6AC", "#7F878D", "#5E676D", "#33393D"
    s = (  # Roof unit, drawn behind the body
         f'<rect x="244" y="78" width="40" height="12" rx="5" fill="#AEB6BC" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="258" y="88" width="10" height="10" fill="{LINE}"/>'
         # Body: the roof runs back into a sloped rear deck, then a short rear face
         f'<path fill="{ST}" stroke="{LINE}" stroke-width="3" d="M56,166 L52,146 L66,124 Q70,120 80,119 L250,98 '
         f'L398,96 Q410,96 420,102 L500,136 Q600,150 660,160 Q706,170 712,192 L714,214 Q710,226 694,228 L108,230 Z"/>'
         f'<path fill="{LOW}" d="M54,170 L712,180 L714,214 Q710,226 694,228 L108,230 L56,166 Z"/>'
         + wells("delorean", 6)
         # Louvers on the rear slope, on a black panel
         + f'<path fill="#2E3438" d="M120,114 L250,98 L254,108 L124,125 Z"/>'
         + "".join(f'<line x1="{170 + i * 14}" y1="{108 - i * 1.7:.1f}" x2="{176 + i * 14}" y2="{115 - i * 1.7:.1f}" stroke="#3E4449" stroke-width="3"/>' for i in range(5)) +
         # Pipe with copper coils along the rear deck
         f'<rect x="96" y="120" width="150" height="7" rx="3.5" fill="{PART_D}" transform="rotate(-7 96 120)"/>'
         + "".join(f'<line x1="{x}" y1="{126 - (x - 96) * 0.123:.1f}" x2="{x}" y2="{112 - (x - 96) * 0.123:.1f}" stroke="#B87333" stroke-width="3"/>' for x in (206, 214, 222)) +
         # Vent box at the back, with slats facing backward
         f'<path fill="{PART}" stroke="{PART_D}" stroke-width="2" d="M62,124 L70,92 Q72,86 78,86 L112,86 Q118,86 118,92 L118,120 Z"/>'
         + "".join(f'<line x1="{70 - (y - 92) * 0.25:.1f}" y1="{y}" x2="108" y2="{y}" stroke="{PART_D}" stroke-width="3"/>' for y in (96, 104, 112)) +
         # Ribbed reactor in front of the vent box
         f'<rect x="126" y="80" width="26" height="34" rx="3" fill="#B3BBC1" stroke="{PART_D}" stroke-width="2"/>'
         f'<rect x="122" y="74" width="34" height="9" rx="4" fill="#D3D8DC" stroke="{PART_D}" stroke-width="2"/>'
         + "".join(f'<line x1="127" y1="{y}" x2="151" y2="{y}" stroke="{PART_D}" stroke-width="2"/>' for y in (92, 101)) +
         f'<path fill="{WINDOW}" d="M296,106 L398,104 L462,142 L296,142 Z"/>'
         f'<path d="M262,100 L268,226 M498,138 L506,226" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<rect x="316" y="182" width="16" height="6" rx="3" fill="{LINE}"/>'
         f'<path d="M300,228 L520,228" stroke="#E3E7EA" stroke-width="5"/>'
         f'<rect x="646" y="164" width="34" height="20" rx="3" fill="#E9E2C8" stroke="{LINE}" stroke-width="2"/>'
         # Rear face: a black panel with the tail lights, and a black bumper
         # that runs up at an angle from the bottom of the car
         f'<path fill="#2E3438" d="M52,146 L66,124 Q70,120 80,119 L86,170 L56,166 Z"/>'
         f'<path fill="{RED_LIGHT}" d="M56,138 L80,136 L82,152 L54,152 Z"/>'
         f'<path fill="#2E3438" d="M56,162 L88,166 L128,229 L108,230 Z"/>'
         # Dark lower edge along the side
         f'<path fill="#3E4449" d="M112,218 L712,210 L714,214 Q710,226 694,228 L120,230 Z"/>'
         f'<rect x="696" y="202" width="20" height="12" rx="3" fill="#3E4449"/>')
    return ref("delorean", s), ref("delorean", s, True)

def mcqueen(left):
    # Lightning McQueen from Cars: a red race car with a tall spoiler, big
    # tires, a yellow and orange lightning bolt on the side, the number 95,
    # sticker headlights, and small sponsor stickers.
    RED, RED_D, YELLOW, ORANGE = "#D7261E", "#A3191A", "#F7C514", "#F0841C"
    s = (f'<path fill="{RED}" stroke="{RED_D}" stroke-width="3" d="M30,32 L76,40 L80,78 L40,96 Z"/>'
         f'<path fill="{RED}" stroke="{RED_D}" stroke-width="3" d="M58,190 Q38,170 36,140 L40,100 Q60,80 120,74 '
         f'Q180,56 220,46 Q270,32 330,28 L372,28 Q392,30 408,44 L448,96 Q540,100 600,108 Q648,118 658,150 '
         f'Q662,184 640,200 Q620,214 590,216 L90,214 Q66,206 58,190 Z"/>'
         + wells("mcqueen", 5) +
         f'<path fill="{WINDOW}" d="M210,58 Q250,44 290,40 L290,88 L206,92 Z"/>'
         f'<path fill="{WINDOW}" d="M302,38 L370,36 Q390,38 400,50 L436,96 L302,92 Z"/>'
         # Orange flame and yellow lightning bolt along the side
         f'<path fill="{ORANGE}" d="M52,112 Q140,92 280,100 L348,104 L300,150 L250,176 Q150,150 56,148 Z"/>'
         f'<path fill="{YELLOW}" d="M220,100 L430,104 L392,146 L470,148 L414,176 L478,206 L330,192 L282,170 Q250,130 220,100 Z"/>'
         f'<path fill="{YELLOW}" fill-opacity="0.85" d="M60,118 Q90,104 130,106 L118,126 Q90,124 64,132 Z"/>'
         # Sponsor stickers and the sticker headlight
         f'<rect x="440" y="114" width="56" height="8" rx="3" fill="#6EC6E8"/><rect x="448" y="150" width="30" height="8" rx="3" fill="#7B4FB0"/>'
         f'<rect x="428" y="208" width="34" height="7" rx="3" fill="#57A639"/><rect x="462" y="208" width="26" height="7" rx="3" fill="#6EC6E8"/>'
         f'<path d="M610,124 Q632,124 646,140 L620,144 Q612,134 610,124 Z" fill="{YELLOW}"/>'
         f'<path d="M640,176 Q648,186 636,196" stroke="{RED_D}" stroke-width="4" fill="none"/>')
    s = ref("mcqueen", s, left)
    # The number and the small script name are added after the car is turned,
    # so they do not read backward
    sp = SPECS["mcqueen"]
    k = sp["k"]
    def at(x, y):
        x = sp["tx"] + x * k
        return (sp["w"] - x if left else x), sp["ty"] + y * k
    nx, ny = at(330, 182)
    s += text("95", "racing", 400, 34, nx, ny, "#F28C18", outline="#7A1B12", outline_width=2.5)
    sx, sy = at(98, 120)
    s += text("Rust-eze", "script", 700, 10, sx, sy, YELLOW)
    return s

def mustang():
    # The 1969 Ford Mustang Mach 1 from John Wick: dark gray, a long hood with a
    # scoop, a fastback roof, a small spoiler, and a chrome front bumper.
    BODY, LINE = "#3A4045", "#8C969C"
    s = (f'<path d="M86,104 L84,96 L118,96 L116,104" stroke="{LINE}" stroke-width="4" fill="{BODY}"/>'
         f'<path fill="{BODY}" stroke="{LINE}" stroke-width="3" d="M70,196 L62,176 L64,134 Q70,112 110,108 '
         f'Q200,88 290,70 Q310,66 330,66 L418,66 Q434,68 446,78 L500,112 Q620,122 712,138 Q736,144 740,160 '
         f'L742,180 Q738,196 720,200 L84,206 Q72,204 70,196 Z"/>'
         + wells("mustang", 7, LINE) +
         f'<path fill="#1C2125" d="M302,80 L418,76 Q428,78 436,84 L480,112 L300,118 Z"/>'
         f'<path d="M292,84 L292,200 M498,114 L500,200" stroke="{LINE}" stroke-width="3" fill="none"/>'
         f'<path d="M66,130 L736,152" stroke="{LINE}" stroke-width="3" fill="none"/>'
         + "".join(f'<path d="M{x},92 L{x + 6},110" stroke="{LINE}" stroke-width="3"/>' for x in (256, 268, 280)) +
         f'<rect x="306" y="132" width="20" height="5" rx="2" fill="{LINE}"/>'
         f'<path d="M546,116 L590,114 L596,122 L548,124 Z" fill="#2A2F33" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="62" y="160" width="12" height="20" rx="3" fill="{RED_LIGHT}"/>'
         f'<circle cx="724" cy="158" r="8" fill="{AMBER}" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="686" y="182" width="62" height="10" rx="5" fill="{CHROME}"/>')
    return ref("mustang", s), ref("mustang", s, True)

# Wheel images, 64 by 64 like wheel.png. MainScene.brs shows each at the
# car's wheel size.
def spokes(n, r1, r2, color, width, start=0):
    import math
    out = ""
    for i in range(n):
        a = math.radians(start + i * 360 / n)
        out += (f'<line x1="{32 + r1 * math.cos(a):.2f}" y1="{32 + r1 * math.sin(a):.2f}" '
                f'x2="{32 + r2 * math.cos(a):.2f}" y2="{32 + r2 * math.sin(a):.2f}" stroke="{color}" stroke-width="{width}"/>')
    return out

def dots(n, r, size, color, start=0):
    import math
    return "".join(f'<circle cx="{32 + r * math.cos(math.radians(start + i * 360 / n)):.2f}" '
                   f'cy="{32 + r * math.sin(math.radians(start + i * 360 / n)):.2f}" r="{size}" fill="{color}"/>' for i in range(n))

TIRE = f'<circle cx="32" cy="32" r="32" fill="{DARK}"/>'
WHEELS = {
    # Wire wheels with a center spinner
    "aston": TIRE + '<circle cx="32" cy="32" r="21" fill="#7D878F"/>' + spokes(18, 5, 21, "#E3E7EA", 1.6)
             + '<circle cx="32" cy="32" r="21" fill="none" stroke="#C9D2DA" stroke-width="3"/>'
             + '<circle cx="32" cy="32" r="6" fill="#E3E7EA"/>' + spokes(3, 0, 9, "#C9D2DA", 3),
    # Large smooth hubcaps, with dots so the turning shows
    "herbie": TIRE + '<circle cx="32" cy="32" r="21" fill="#D9DEE2"/><circle cx="32" cy="32" r="14" fill="#EEF1F3"/>'
              + dots(4, 17.5, 1.8, "#8E969C") + '<circle cx="32" cy="32" r="4" fill="#B5BDC3"/>',
    # Silver turbine wheels
    "kitt": TIRE + '<circle cx="32" cy="32" r="21" fill="#C9D2DA"/>' + spokes(10, 9, 19, "#5B646C", 3, 10)
            + '<circle cx="32" cy="32" r="7" fill="#E3E7EA"/>',
    # Red rims with chrome hubcaps
    "ecto1": TIRE + '<circle cx="32" cy="32" r="22" fill="#F4F4F1"/><circle cx="32" cy="32" r="18" fill="#8C1C2E"/>'
             + '<circle cx="32" cy="32" r="11" fill="#E3E7EA"/>' + dots(4, 14.5, 1.8, "#3E4449"),
    # Silver multi-spoke wheels
    "delorean": TIRE + '<circle cx="32" cy="32" r="21" fill="#AEB6BC"/>' + spokes(12, 8, 19, "#5B646C", 2.5)
                + '<circle cx="32" cy="32" r="7" fill="#D3D8DC"/>',
    # Red rims with five holes
    "mcqueen": TIRE + '<circle cx="32" cy="32" r="20" fill="#D7261E"/>' + dots(5, 12, 4, "#5A0E0E", -90)
               + '<circle cx="32" cy="32" r="5" fill="#F7C514"/>',
    # Silver five-spoke wheels
    "mustang": TIRE + '<circle cx="32" cy="32" r="21" fill="#D3D8DC"/>' + dots(5, 13, 6, "#3E4449", -54)
               + '<circle cx="32" cy="32" r="5" fill="#8C969C"/>',
}

def draw(save):
    """Saves every special car facing right and facing left, and its wheel
    image. save is save(content, viewbox, w, h, file name) from sprites.py."""
    images = {"aston": aston(), "herbie": (herbie(False), herbie(True)), "kitt": kitt(),
              "ecto1": (ecto1(False), ecto1(True)), "delorean": delorean(),
              "mcqueen": (mcqueen(False), mcqueen(True)), "mustang": mustang()}
    for name, (right, left) in images.items():
        w, h = SPECS[name]["w"], SPECS[name]["h"]
        save(right, f"0 0 {w} {h}", w, h, f"car_{name}.png")
        save(left, f"0 0 {w} {h}", w, h, f"car_{name}_left.png")
        save(WHEELS[name], "0 0 64 64", 64, 64, f"wheel_{name}.png")
