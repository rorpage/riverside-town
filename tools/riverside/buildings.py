"""Building types for town.json. Each type has a width and a draw function.

draw(spec, x, p, season) returns the SVG for one building whose left edge is
at x in its town section. spec is the building's entry from town.json, with
defaults filled in by config.py. Every building stands on the sidewalk at
y=900, and nothing may be drawn above y=550 (the top of the town images).

Some types are drawn at the position they had in the original town and moved
into place with shift(). Their ORIGIN value is the left edge of that drawing.
"""
import math
from .art import (ACCENT, ICON, WHITE, DARK, wall, text, text_width, fit_size, sign, shift, arch,
                  snow_flat, snow_ridge, pumpkins, flower_box, round_tree)

def colors(p):
    return p["houseA"], p["houseB"], p["wall2"], p["roof"], p["window"]

# ---------- house ----------
def house_width(s):
    return s["width"] + 16

def house_draw(s, x, p, season):
    """A house with a pointed roof, two windows on each floor, a door, and a
    number plaque above the door."""
    A, B, W2, R, Wn = colors(p)
    w = s["width"]
    hx = x + 8
    # One-story houses have their wall top at y=730 to 750, two-story houses at
    # y=680 to 700. The exact height comes from the house number, so houses next
    # to each other are not all the same height.
    step = sum(ord(c) for c in str(s["number"])) % 3 * 10
    y = (730 if s["stories"] == 1 else 680) + step
    peak = y - 64
    rows = [y + 18] + ([762] if s["stories"] == 2 else [])
    doorX = hx + w // 2 - 20
    wins = "".join(f'<rect x="{hx + 10}" y="{r}" width="40" height="38" fill="{Wn}"/><rect x="{hx + w - 50}" y="{r}" width="40" height="38" fill="{Wn}"/>'
                   + flower_box(season, p, hx + 10, r + 38, 40) + flower_box(season, p, hx + w - 50, r + 38, 40) for r in rows)
    return (f'<rect x="{hx}" y="{y}" width="{w}" height="{900 - y}" fill="{wall(s["color"], p)}"/>'
            f'<polygon points="{hx - 8},{y} {hx + w // 2},{peak} {hx + w + 8},{y}" fill="{R}"/>'
            + snow_ridge(season, p, (hx - 6, y - 3), (hx + w // 2, peak - 3), (hx + w + 6, y - 3)) + wins +
            f'<rect x="{doorX}" y="830" width="40" height="70" fill="{R}"/>'
            f'<rect x="{doorX - 2}" y="808" width="44" height="18" rx="3" fill="{R}"/>'
            + text(str(s["number"]), s["font"], s["weight"], fit_size(str(s["number"]), s["font"], s["weight"], 14, 38, 1),
                   doorX + 20, 822, WHITE, 1)
            + pumpkins(season, doorX + 50))

# ---------- shop ----------
def shop_width(s):
    return s["width"] + 8

def awning(season, p, x, w, style, color, stripes):
    """The awning over a shop window, from y=800 to y=828."""
    if style == "none":
        return ""
    if style == "striped":
        n = len(stripes) * 3
        out = ""
        for i in range(n):
            t0, t1 = x + 10 + (w - 20) * i / n, x + 10 + (w - 20) * (i + 1) / n
            b0, b1 = x + w * i / n, x + w * (i + 1) / n
            c = wall(stripes[i % len(stripes)], p) if stripes[i % len(stripes)].upper() in ("#F8FAFC", "#FFFFFF") else stripes[i % len(stripes)]
            out += f'<polygon points="{t0:.1f},800 {t1:.1f},800 {b1:.1f},828 {b0:.1f},828" fill="{c}"/>'
    else:
        out = f'<polygon points="{x + 10},800 {x + w - 10},800 {x + w},828 {x},828" fill="{color}"/>'
    return out + snow_flat(season, p, x + 8, 800, w - 16)

def window_books(wx, wy, ww, wh, p, s):
    R = p["roof"]
    colors_ = ["#B5523F", "#4A82A8", "#6B7B3A", "#F6C46A", "#34495E", "#C9D2DA"]
    out = ""
    for row, (top, base) in enumerate([(wy + 6, wy + 24), (wy + 28, wy + 46)]):
        bx = wx + 4 + row * 4
        i = row * 2
        while bx < wx + ww - 10:
            bw = [8, 10, 7, 9][i % 4]
            bh = base - top - [0, 3, 1, 4, 2][i % 5]
            out += f'<rect x="{bx}" y="{base - bh}" width="{bw}" height="{bh}" fill="{colors_[i % len(colors_)]}"/>'
            bx += bw + 2
            i += 1
        out += f'<rect x="{wx}" y="{base}" width="{ww}" height="4" fill="{R}"/>'
    return out

def window_computer(wx, wy, ww, wh, p, s):
    Wn = p["window"]
    cx = wx + ww / 2
    return (f'<rect x="{cx - 18}" y="{wy + 8}" width="36" height="25" rx="2" fill="{ICON}"/><rect x="{cx - 14}" y="{wy + 12}" width="28" height="17" fill="{Wn}"/>'
            f'<rect x="{cx - 3}" y="{wy + 33}" width="6" height="6" fill="{ICON}"/><rect x="{cx - 11}" y="{wy + 39}" width="22" height="3" rx="1" fill="{ICON}"/>'
            f'<rect x="{cx - 22}" y="{wy + 45}" width="44" height="6" rx="1.5" fill="{ICON}"/>')

def window_camera(wx, wy, ww, wh, p, s):
    Wn = p["window"]
    cx, cy = wx + ww // 2, wy + wh // 2 + 2
    return (f'<rect x="{cx - 20}" y="{cy - 10}" width="40" height="24" rx="4" fill="{ICON}"/><rect x="{cx - 15}" y="{cy - 15}" width="11" height="6" rx="1.5" fill="{ICON}"/>'
            f'<rect x="{cx + 8}" y="{cy - 7}" width="8" height="4" rx="1" fill="{Wn}"/>'
            f'<circle cx="{cx}" cy="{cy + 2}" r="8" fill="{Wn}"/><circle cx="{cx}" cy="{cy + 2}" r="5" fill="{ICON}"/>')

def window_palette(wx, wy, ww, wh, p, s):
    """A painter's palette and brush, drawn like an icon. The paint spots and
    thumb hole are cut out in the window color."""
    Wn = p["window"]
    px, py, k = wx + ww / 2 - 6, wy + wh / 2, 0.6
    def pt(dx, dy):
        return f"{px + dx * k:.1f},{py + dy * k:.1f}"
    out = (f'<path d="M{pt(-34, 0)} C{pt(-36, -22)} {pt(10, -26)} {pt(30, -14)} C{pt(42, -6)} {pt(30, 4)} {pt(20, 2)} '
           f'C{pt(8, 0)} {pt(8, 14)} {pt(16, 18)} C{pt(4, 26)} {pt(-30, 24)} {pt(-34, 0)} Z" fill="{ICON}"/>'
           f'<circle cx="{px + 14 * k:.1f}" cy="{py + 8 * k:.1f}" r="{5 * k:.1f}" fill="{Wn}"/>')
    for dx, dy in ((-24, -2), (-14, -14), (2, -16), (18, -10), (-20, 12)):
        out += f'<circle cx="{px + dx * k:.1f}" cy="{py + dy * k:.1f}" r="{4.5 * k:.1f}" fill="{Wn}"/>'
    return out + (f'<line x1="{px + 40 * k:.1f}" y1="{py + 22 * k:.1f}" x2="{px + 62 * k:.1f}" y2="{py - 20 * k:.1f}" stroke="{ICON}" stroke-width="3" stroke-linecap="round"/>'
                  f'<path d="M{pt(60, -16)} L{pt(68, -28)} L{pt(64, -15)} Z" fill="{ICON}"/>')

def window_ice_cream(wx, wy, ww, wh, p, s):
    out = ""
    for i, (c1, c2) in enumerate((("#F2B8C6", "#F6E7B0"), ("#B8E2C8", "#F2B8C6"), ("#F6E7B0", "#B8E2C8"))):
        cx = wx + ww * (i + 1) / 4
        out += (f'<polygon points="{cx - 8:.0f},{wy + 26} {cx + 8:.0f},{wy + 26} {cx:.0f},{wy + 50}" fill="#D9A55B"/>'
                f'<circle cx="{cx:.0f}" cy="{wy + 22}" r="9" fill="{c1}"/><circle cx="{cx:.0f}" cy="{wy + 12}" r="7" fill="{c2}"/>')
    return out

def window_pets(wx, wy, ww, wh, p, s):
    """A fish bowl, a puppy, and a kitten on a small table."""
    base = wy + wh - 12
    out = (f'<rect x="{wx + 4}" y="{base}" width="{ww - 8}" height="4" rx="1" fill="#8C5A3C"/>'
           f'<rect x="{wx + 10}" y="{base + 4}" width="4" height="{wy + wh - base - 4}" fill="#6B4A3A"/>'
           f'<rect x="{wx + ww - 14}" y="{base + 4}" width="4" height="{wy + wh - base - 4}" fill="#6B4A3A"/>')
    fx, fy = wx + 18, base - 14
    out += (f'<circle cx="{fx}" cy="{fy}" r="13" fill="#A9D4EC" fill-opacity="0.9"/><rect x="{fx - 8}" y="{fy - 15}" width="16" height="4" rx="2" fill="#A9D4EC"/>'
            f'<ellipse cx="{fx - 1}" cy="{fy + 1}" rx="5" ry="3" fill="#E8913A"/><polygon points="{fx + 3},{fy + 1} {fx + 8},{fy - 2} {fx + 8},{fy + 4}" fill="#E8913A"/>')
    dx = wx + ww * 0.47
    PUP, PUPD = "#B07A4A", "#7A4E2C"
    out += (f'<ellipse cx="{dx:.0f}" cy="{base - 9}" rx="10" ry="9" fill="{PUP}"/>'
            f'<path d="M{dx - 9:.0f},{base - 8} Q{dx - 17:.0f},{base - 14} {dx - 15:.0f},{base - 20}" stroke="{PUP}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{dx + 6:.0f}" cy="{base - 21}" r="8" fill="{PUP}"/><ellipse cx="{dx + 14:.0f}" cy="{base - 18}" rx="5" ry="3.5" fill="{PUP}"/>'
            f'<ellipse cx="{dx + 2:.0f}" cy="{base - 20}" rx="3" ry="6" fill="{PUPD}"/>'
            f'<circle cx="{dx + 9:.0f}" cy="{base - 23}" r="1.4" fill="#1F2A33"/><circle cx="{dx + 18:.0f}" cy="{base - 19}" r="1.6" fill="#1F2A33"/>'
            f'<rect x="{dx + 2:.0f}" y="{base - 6}" width="4" height="6" rx="1.5" fill="{PUP}"/><rect x="{dx + 7:.0f}" y="{base - 6}" width="4" height="6" rx="1.5" fill="{PUP}"/>')
    kx = wx + ww * 0.78
    KIT, KITD = "#E8913A", "#C8662E"
    out += (f'<path d="M{kx + 7:.0f},{base - 4} Q{kx + 18:.0f},{base - 6} {kx + 14:.0f},{base - 18}" stroke="{KIT}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="{kx:.0f}" cy="{base - 8}" rx="8" ry="8" fill="{KIT}"/>'
            f'<circle cx="{kx - 3:.0f}" cy="{base - 19}" r="6.5" fill="{KIT}"/>'
            f'<polygon points="{kx - 9:.0f},{base - 22} {kx - 8:.0f},{base - 30} {kx - 3:.0f},{base - 25}" fill="{KIT}"/>'
            f'<polygon points="{kx - 1:.0f},{base - 25} {kx + 3:.0f},{base - 30} {kx + 3:.0f},{base - 21}" fill="{KIT}"/>'
            f'<path d="M{kx - 4:.0f},{base - 12} L{kx + 4:.0f},{base - 12}" stroke="{KITD}" stroke-width="2"/><path d="M{kx - 5:.0f},{base - 7} L{kx + 5:.0f},{base - 7}" stroke="{KITD}" stroke-width="2"/>'
            f'<circle cx="{kx - 6:.0f}" cy="{base - 20}" r="1.2" fill="#1F2A33"/><circle cx="{kx - 1:.0f}" cy="{base - 20}" r="1.2" fill="#1F2A33"/>')
    return out

def window_table(wx, wy, ww, wh, p, s):
    """A table with a checkered tablecloth, a bottle, and a candle."""
    tx, ty = wx + (ww - 96) / 2, wy + 30
    out = ""
    for row in range(2):
        for col in range(8):
            c = "#C0392B" if (row + col) % 2 == 0 else "#F8FAFC"
            out += f'<rect x="{tx + col * 12:.0f}" y="{ty + row * 8}" width="12" height="8" fill="{c}"/>'
    return out + (f'<rect x="{tx + 6:.0f}" y="{ty + 16}" width="4" height="10" fill="#6B4A3A"/><rect x="{tx + 86:.0f}" y="{ty + 16}" width="4" height="10" fill="#6B4A3A"/>'
                  f'<rect x="{tx + 30:.0f}" y="{ty - 16}" width="7" height="16" rx="2" fill="#2F5D3A"/><rect x="{tx + 32:.0f}" y="{ty - 22}" width="3" height="7" fill="#2F5D3A"/>'
                  f'<rect x="{tx + 58:.0f}" y="{ty - 10}" width="4" height="10" fill="#F8FAFC"/><ellipse cx="{tx + 60:.0f}" cy="{ty - 13}" rx="2" ry="3" fill="#F6C46A"/>')

WINDOWS = {"books": window_books, "computer": window_computer, "camera": window_camera, "palette": window_palette,
           "ice_cream": window_ice_cream, "pets": window_pets, "table": window_table}

def window_lettering(lines, wx, wy, ww, wh):
    """Gray lettering on a shop window, in one or two lines."""
    lines = [l for l in lines if l][:2]
    if len(lines) == 1:
        size = fit_size(lines[0], "oswald", 600, 18, ww - 12, 2)
        return text(lines[0], "oswald", 600, size, wx + ww / 2, wy + wh / 2 + size * 0.36, ICON, 2)
    small = fit_size(lines[0], "oswald", 500, 11, ww - 12, 3)
    big = fit_size(lines[1], "oswald", 600, 16, ww - 12, 2)
    return (text(lines[0], "oswald", 500, small, wx + ww / 2, wy + 15, ICON, 3)
            + text(lines[1], "oswald", 600, big, wx + ww / 2, wy + 33, ICON, 2))

def paw(x, y, color):
    out = f'<ellipse cx="{x}" cy="{y + 4}" rx="6" ry="5" fill="{color}"/>'
    for dx, dy in ((-7, -4), (-2.5, -8), (2.5, -8), (7, -4)):
        out += f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="2.2" ry="3" fill="{color}"/>'
    return out

def shop_draw(s, x, p, season):
    """A shop: walls, a roof edge, upper windows for each extra story, a sign,
    an awning, a display window, and a door."""
    A, B, W2, R, Wn = colors(p)
    w = s["width"]
    x = x + 4
    top = {1: 712, 2: 652, 3: 600}[s["stories"]]
    out = ""
    if s.get("roof_icon") == "ice_cream":
        cx = x + w / 2
        out += (f'<polygon points="{cx - 8:.0f},{top - 4} {cx + 8:.0f},{top - 4} {cx:.0f},{top + 26}" fill="#D9A55B"/>'
                f'<circle cx="{cx - 6:.0f}" cy="{top - 12}" r="10" fill="#F2B8C6"/><circle cx="{cx + 6:.0f}" cy="{top - 12}" r="10" fill="#B8E2C8"/>'
                f'<circle cx="{cx:.0f}" cy="{top - 22}" r="10" fill="#F6E7B0"/>')
    out += f'<rect x="{x}" y="{top}" width="{w}" height="{900 - top}" fill="{wall(s["color"], p)}"/>'
    for r in {1: [], 2: [top + 20], 3: [top + 18, top + 70]}[s["stories"]]:
        out += (f'<rect x="{x + 24}" y="{r}" width="42" height="38" fill="{Wn}"/>'
                f'<rect x="{x + w - 66}" y="{r}" width="42" height="38" fill="{Wn}"/>')
    out += f'<rect x="{x - 4}" y="{top}" width="{w + 8}" height="14" fill="{R}"/>' + snow_flat(season, p, x - 4, top, w + 8)

    # Sign
    sx, sw = x + 18, w - 36
    sign_color = s.get("sign_color") or R
    tcolor = s.get("sign_text_color", WHITE)
    font, weight = s["font"], s["weight"]
    out += f'<rect x="{sx}" y="728" width="{sw}" height="48" rx="4" fill="{sign_color}"/>'
    room, cx = sw - 16, sx + sw / 2
    if s.get("sign_icon") == "paw":
        room -= 26
        cx -= 12
        out += paw(sx + sw - 20, 749, tcolor)
    if s.get("small_line"):
        small = fit_size(s["small_line"], font, weight, 13, room, 4)
        big = fit_size(s["name"], font, weight, 24, room, 3)
        out += text(s["small_line"], font, weight, small, cx, 746, tcolor, 4) + text(s["name"], font, weight, big, cx, 771, tcolor, 3)
    else:
        size = fit_size(s["name"], font, weight, s.get("sign_size", 28), room, s.get("letter_spacing", 1))
        out += text(s["name"], font, weight, size, cx, 752 + size * 0.34, tcolor, s.get("letter_spacing", 1))

    out += awning(season, p, x, w, s.get("awning", "plain"), s.get("awning_color", ACCENT), s.get("awning_colors", [ACCENT, "#F8FAFC"]))
    wx, wy, ww, wh = x + 12, 838, w - 78, 56
    out += f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="{Wn}"/><rect x="{x + w - 56}" y="834" width="42" height="66" fill="{R}"/>'
    if s.get("window") in WINDOWS:
        out += WINDOWS[s["window"]](wx, wy, ww, wh, p, s)
    if s.get("window_lettering"):
        lines = s["window_lettering"]
        out += window_lettering(lines if isinstance(lines, list) else str(lines).split("\n"), wx, wy, ww, wh)
    return out

# ---------- church ----------
def church_width(s):
    return 388 if s["style"] == "steeple" else 262

def church_draw(s, x, p, season):
    A, B, W2, R, Wn = colors(p)
    C = wall(s["color"], p)
    RED, GOLD, BLUE = "#B5523F", "#F6C46A", "#4A82A8"
    font, weight = s["font"], s["weight"]
    if s["style"] == "steeple":
        # A bell tower with a spire, and a nave with three stained glass windows
        ORIGIN = 56
        out = (f'<rect x="166" y="760" width="264" height="140" fill="{C}"/>'
               f'<polygon points="156,762 300,692 440,762" fill="{R}"/>'
               f'<rect x="70" y="690" width="100" height="210" fill="{C}"/>'
               + snow_ridge(season, p, (160, 759), (300, 689), (436, 759)) +
               f'<polygon points="62,692 120,590 178,692" fill="{R}"/>'
               + snow_ridge(season, p, (66, 689), (120, 594), (174, 689)))
        if s["cross"]:
            out += f'<rect x="116" y="556" width="8" height="38" fill="{R}"/><rect x="106" y="566" width="28" height="8" fill="{R}"/>'
        out += (arch(100, 708, 40, 56, R) +
                f'<g stroke="{C}" stroke-width="3"><line x1="104" y1="738" x2="136" y2="738"/><line x1="104" y1="750" x2="136" y2="750"/></g>'
                f'<circle cx="120" cy="790" r="13" fill="{GOLD}"/><circle cx="120" cy="790" r="6" fill="{RED}"/>'
                + arch(98, 826, 44, 74, R)
                + sign(196, 768, 204, 30, R, s["name"], font, weight, s.get("sign_size", 22), 790, 2))
        for wx in (196, 280, 364):
            out += (arch(wx, 806, 36, 66, BLUE) + f'<rect x="{wx+12}" y="826" width="12" height="46" fill="{RED}"/>'
                    f'<circle cx="{wx+18}" cy="822" r="7" fill="{GOLD}"/>'
                    f'<g stroke="{R}" stroke-width="2"><line x1="{wx}" y1="846" x2="{wx+36}" y2="846"/><line x1="{wx}" y1="860" x2="{wx+36}" y2="860"/></g>')
        out += f'<rect x="60" y="892" width="120" height="8" fill="{p["curb"]}"/>' + pumpkins(season, 160)
    else:
        # A stone church with a square bell tower and pointed windows
        ORIGIN = 502
        out = (f'<rect x="566" y="740" width="190" height="160" fill="{C}"/>'
               f'<polygon points="558,742 661,690 764,742" fill="{R}"/>' + snow_ridge(season, p, (562, 739), (661, 687), (760, 739)) +
               f'<rect x="508" y="640" width="64" height="260" fill="{C}"/>'
               f'<polygon points="502,642 540,596 578,642" fill="{R}"/>' + snow_ridge(season, p, (506, 639), (540, 599), (574, 639)))
        if s["cross"]:
            out += f'<rect x="537" y="570" width="6" height="30" fill="{R}"/><rect x="530" y="578" width="20" height="6" fill="{R}"/>'
        out += (f'<path d="M526,700 L526,676 L540,660 L554,676 L554,700 Z" fill="{R}"/>'
                f'<path d="M524,900 L524,846 L540,826 L556,846 L556,900 Z" fill="{R}"/>'
                + sign(600, 752, 122, 34, R, s["name"], font, weight, s.get("sign_size", 24), 778, 6))
        for wx in (590, 646, 702):
            out += (f'<path d="M{wx},874 L{wx},816 L{wx + 13},798 L{wx + 26},816 L{wx + 26},874 Z" fill="{BLUE}"/>'
                    f'<rect x="{wx + 11}" y="812" width="4" height="62" fill="{GOLD}"/><rect x="{wx}" y="842" width="26" height="3" fill="{R}"/>')
    return shift(out, x - ORIGIN)

# ---------- school ----------
def school_width(s):
    return s["width"] + 12

def school_draw(s, x, p, season):
    """A two-story school with a center entrance, the name over the door, and
    an optional cross or bell tower on top."""
    A, B, W2, R, Wn = colors(p)
    w = s["width"]
    x = x + 6
    color = wall(s["color"], p)
    white = wall("#F8FAFC", p)
    cx = x + w // 2
    ex0, ex1 = cx - 70, cx + 70
    gable_top = 636 if s["cross"] else 646
    out = (f'<rect x="{x}" y="700" width="{w}" height="200" fill="{color}"/>'
           f'<rect x="{x - 4}" y="700" width="{w + 8}" height="12" fill="{R}"/>' + snow_flat(season, p, x - 4, 700, w + 8))
    left = [x + 12 + i * 32 for i in range(max(1, (ex0 - x - 12) // 32))]
    right = [ex1 + 8 + i * 32 for i in range(max(1, (x + w - ex1 - 12) // 32))]
    for wx in left + right:
        for wy in (726, 784):
            out += f'<rect x="{wx}" y="{wy}" width="24" height="36" fill="{Wn}"/><rect x="{wx}" y="{wy + 17}" width="24" height="2" fill="{color}"/>'
    out += (f'<rect x="{ex0}" y="672" width="140" height="228" fill="{white}"/>'
            f'<polygon points="{ex0 - 6},672 {cx},{gable_top} {ex1 + 6},672" fill="{R}"/>'
            + snow_ridge(season, p, (ex0 - 4, 669), (cx, gable_top - 3), (ex1 + 4, 669))
            + sign(ex0 + 8, 690, 124, 30, R, s["name"], s["font"], s["weight"], s.get("sign_size", 15), 711, 1) +
            f'<rect x="{ex0 + 26}" y="734" width="36" height="40" fill="{Wn}"/><rect x="{ex1 - 62}" y="734" width="36" height="40" fill="{Wn}"/>'
            + arch(cx - 28, 820, 56, 80, R) + f'<rect x="{cx - 1}" y="836" width="2" height="64" fill="{color}"/>'
            f'<rect x="{ex0 - 6}" y="892" width="152" height="8" fill="{p["curb"]}"/>')
    if s["cross"]:
        out += f'<rect x="{cx - 3}" y="602" width="6" height="36" fill="{R}"/><rect x="{cx - 11}" y="612" width="22" height="6" fill="{R}"/>'
    if s["bell_tower"]:
        out += (f'<rect x="{cx - 14}" y="620" width="28" height="30" fill="{white}"/>'
                f'<path d="M{cx - 8},650 L{cx - 8},634 A8,8 0 0 1 {cx + 8},634 L{cx + 8},650 Z" fill="{R}"/>'
                f'<polygon points="{cx - 18},622 {cx},600 {cx + 18},622" fill="{R}"/>' + snow_ridge(season, p, (cx - 16, 620), (cx, 603), (cx + 16, 620)))
    return out

# ---------- columned hall ----------
def hall_width(s):
    return 500 if s["clock"] else 410

def clock_face(cx, cy, cr, p, R, time):
    hh, mm = (int(v) for v in time.split(":"))
    out = f'<circle cx="{cx}" cy="{cy}" r="{cr}" fill="{p["clockFace"]}" stroke="{R}" stroke-width="3"/>'
    for i in range(12):
        a = math.radians(i * 30)
        r1 = cr - (7 if i % 3 == 0 else 5)
        out += (f'<line x1="{cx + r1 * math.sin(a):.1f}" y1="{cy - r1 * math.cos(a):.1f}" '
                f'x2="{cx + (cr - 3) * math.sin(a):.1f}" y2="{cy - (cr - 3) * math.cos(a):.1f}" stroke="{R}" stroke-width="2"/>')
    for deg, length, width in ((((hh % 12) + mm / 60) * 30, 14, 4), (mm * 6, 21, 3)):
        a = math.radians(deg)
        out += (f'<line x1="{cx}" y1="{cy}" x2="{cx + length * math.sin(a):.1f}" y2="{cy - length * math.cos(a):.1f}" '
                f'stroke="{R}" stroke-width="{width}" stroke-linecap="round"/>')
    return out + f'<circle cx="{cx}" cy="{cy}" r="3" fill="{R}"/>'

def hall_draw(s, x, p, season):
    """A stone building with columns, steps, and the name across the top, like a
    library or a courthouse. With clock on, it has a clock tower."""
    A, B, W2, R, Wn = colors(p)
    font, weight = s["font"], s["weight"]
    fill = s.get("letter_color") or R
    outline = s.get("letter_outline")
    if s["clock"]:
        ORIGIN = 1250
        out = (f'<rect x="1456" y="600" width="88" height="112" fill="{A}"/>'
               f'<rect x="1448" y="592" width="104" height="10" fill="{W2}"/>'
               f'<rect x="1470" y="574" width="60" height="18" fill="{A}"/>'
               + arch(1478, 578, 12, 14, R) + arch(1494, 578, 12, 14, R) + arch(1510, 578, 12, 14, R) +
               f'<polygon points="1462,575 1500,552 1538,575" fill="{R}"/>'
               + snow_ridge(season, p, (1466, 572), (1500, 555), (1534, 572)) + snow_flat(season, p, 1448, 592, 104)
               + clock_face(1500, 636, 28, p, R, s["clock_time"]) +
               f'<rect x="1250" y="888" width="500" height="12" fill="{p["curb"]}"/><rect x="1262" y="876" width="476" height="12" fill="{W2}"/>'
               f'<rect x="1280" y="730" width="440" height="146" fill="{A}"/>'
               f'<polygon points="1262,712 1500,672 1738,712" fill="{B}"/>'
               f'<polygon points="1300,706 1500,680 1700,706" fill="none" stroke="{W2}" stroke-width="4"/>'
               + snow_ridge(season, p, (1266, 709), (1456, 678)) + snow_ridge(season, p, (1544, 678), (1734, 709)) +
               f'<rect x="1270" y="708" width="460" height="24" fill="{W2}"/>')
        size = fit_size(s["name"], font, weight, s.get("sign_size", 18), 440, 2)
        out += text(s["name"], font, weight, size, 1500, 720 + size * 0.36, fill, 2, outline, 2 if outline else 0)
        for cx in (1320, 1392, 1464, 1536, 1608, 1680):
            out += (f'<rect x="{cx-11}" y="740" width="22" height="136" fill="{B}"/>'
                    f'<rect x="{cx-15}" y="732" width="30" height="8" fill="{W2}"/><rect x="{cx-15}" y="868" width="30" height="8" fill="{W2}"/>')
        for wx in (1356, 1428, 1572, 1644):
            out += arch(wx - 15, 760, 30, 80, Wn)
        out += arch(1478, 796, 44, 80, R) + pumpkins(season, 1540)
    else:
        ORIGIN = 1490
        out = (f'<rect x="1490" y="888" width="410" height="12" fill="{p["curb"]}"/><rect x="1500" y="876" width="390" height="12" fill="{W2}"/>'
               f'<rect x="1514" y="744" width="362" height="132" fill="{A}"/>'
               f'<polygon points="1498,728 1695,684 1892,728" fill="{B}"/>'
               f'<polygon points="1530,722 1695,692 1860,722" fill="none" stroke="{W2}" stroke-width="4"/>'
               + snow_ridge(season, p, (1502, 725), (1695, 687), (1888, 725)) +
               f'<rect x="1504" y="724" width="382" height="26" fill="{W2}"/>')
        size = fit_size(s["name"], font, weight, s.get("sign_size", 21), 360, 2)
        out += text(s["name"], font, weight, size, 1695, 737 + size * 0.36, fill, 2, outline, 2 if outline else 0)
        for cx in (1546, 1608, 1670, 1720, 1782, 1844):
            out += (f'<rect x="{cx - 10}" y="756" width="20" height="120" fill="{B}"/>'
                    f'<rect x="{cx - 14}" y="750" width="28" height="7" fill="{W2}"/><rect x="{cx - 14}" y="869" width="28" height="7" fill="{W2}"/>')
        for wx in (1577, 1639, 1751, 1813):
            out += arch(wx - 13, 776, 26, 74, Wn)
        out += arch(1676, 806, 38, 70, R) + pumpkins(season, 1630, 876)
    return shift(out, x - ORIGIN)

# ---------- gas station ----------
GAS_ORIGIN = 448
GAS_PARKING = 780   # Center of the parking space under the canopy, in the original drawing

def gas_width(s):
    return 736

def gas_parking(x):
    """The center x of the parking space for a gas station whose left edge is at x."""
    return x - GAS_ORIGIN + GAS_PARKING

def gas_draw(s, x, p, season):
    """A price sign, a canopy over one pump, and a small store. The parked car
    is added by MainScene.brs, at the position from gas_parking()."""
    A, B, W2, R, Wn = colors(p)
    price = "$" + s["price"]
    priceW = text_width(price, "oswald", 500, 22, 1)
    nineW = text_width("9", "oswald", 500, 11)
    priceX = 484 - (priceW + 2 + nineW) / 2
    out = (f'<rect x="480" y="746" width="8" height="154" fill="{W2}"/>'
           f'<rect x="448" y="690" width="72" height="62" rx="4" fill="{R}"/>'
           + text("GAS", "oswald", 700, 20, 484, 714, ACCENT, 2)
           + text(price, "oswald", 500, 22, priceX + priceW / 2, 742, WHITE, 1)
           + text("9", "oswald", 500, 11, priceX + priceW + 2 + nineW / 2, 731, WHITE) +
           f'<rect x="556" y="772" width="12" height="128" fill="{W2}"/><rect x="912" y="772" width="12" height="128" fill="{W2}"/>'
           f'<rect x="520" y="740" width="440" height="34" fill="{R}"/><rect x="520" y="766" width="440" height="8" fill="{ACCENT}"/>'
           + snow_flat(season, p, 520, 740, 440) + snow_flat(season, p, 448, 690, 72))
    size = fit_size(s["canopy_name"], "oswald", 600, 22, 400, 5)
    out += (text(s["canopy_name"], "oswald", 600, size, 740, 762, WHITE, 5) +
            f'<rect x="578" y="886" width="62" height="14" fill="{p["curb"]}"/>'
            f'<rect x="588" y="812" width="40" height="76" fill="{B}"/><rect x="588" y="812" width="40" height="10" fill="{ACCENT}"/>'
            f'<rect x="594" y="828" width="28" height="18" fill="{Wn}"/>'
            f'<path d="M628,836 Q646,840 642,870" stroke="{DARK}" stroke-width="4" fill="none"/>'
            f'<rect x="980" y="770" width="200" height="130" fill="{wall(s["color"], p)}"/><rect x="976" y="770" width="208" height="14" fill="{R}"/>'
            + snow_flat(season, p, 976, 770, 208)
            + sign(1006, 792, 148, 36, s.get("store_sign_color", ACCENT), s["store_name"], s["font"], s["weight"], 22, 818, 2) +
            f'<rect x="996" y="842" width="96" height="50" fill="{Wn}"/><rect x="1110" y="836" width="46" height="64" fill="{R}"/>')
    return shift(out, x - GAS_ORIGIN)

# ---------- drive-through restaurant ----------
def drive_width(s):
    return 322

def drive_draw(s, x, p, season):
    """A restaurant with a colored roof that has the name on it, big windows,
    and a drive-through window with a sign."""
    A, B, W2, R, Wn = colors(p)
    ORIGIN = 776
    RED = s.get("roof_color", "#D62E3C")
    CW = wall(s["color"], p)
    size = fit_size(s["name"], s["font"], s["weight"], s.get("sign_size", 34), 230)
    out = (f'<rect x="784" y="752" width="256" height="148" fill="{CW}"/>'
           f'<polygon points="776,754 1048,754 1032,708 792,708" fill="{RED}"/>' + snow_flat(season, p, 792, 708, 240)
           + text(s["name"], s["font"], s["weight"], size, 912, 731 + size * 0.38, s.get("sign_text_color", WHITE)) +
           f'<rect x="800" y="790" width="70" height="80" fill="{Wn}"/><rect x="882" y="790" width="70" height="80" fill="{Wn}"/>'
           f'<rect x="834" y="790" width="2" height="80" fill="{CW}"/><rect x="916" y="790" width="2" height="80" fill="{CW}"/>'
           f'<rect x="964" y="830" width="34" height="70" fill="{R}"/>'
           f'<rect x="1006" y="806" width="28" height="40" fill="{Wn}"/><rect x="1002" y="798" width="36" height="8" fill="{RED}"/>'
           + snow_flat(season, p, 1002, 798, 36) +
           f'<rect x="1054" y="770" width="4" height="130" fill="{R}"/><polygon points="1046,766 1094,766 1094,786 1046,786" fill="{RED}"/>'
           + text("DRIVE THRU", "oswald", 600, 9, 1070, 780, WHITE, 0.5))
    return shift(out, x - ORIGIN)

# ---------- tree ----------
def tree_width(s):
    return 80

def tree_draw(s, x, p, season):
    return round_tree(x + 40, 900, 56, 30, p, season)

TYPES = {
    "house": (house_width, house_draw),
    "shop": (shop_width, shop_draw),
    "church": (church_width, church_draw),
    "school": (school_width, school_draw),
    "columned_hall": (hall_width, hall_draw),
    "gas_station": (gas_width, gas_draw),
    "drive_through": (drive_width, drive_draw),
    "tree": (tree_width, tree_draw),
}

def width(spec):
    return TYPES[spec["type"]][0](spec)

def draw(spec, x, p, season):
    return TYPES[spec["type"]][1](spec, x, p, season)
