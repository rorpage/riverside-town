"""Places the buildings along the street in 1920 pixel town sections."""
from . import buildings
from .config import ConfigError

SECTION = 1920
MARGIN = 16        # Space at each end of a section, so no building crosses a section edge
GAP = 12           # Smallest space between two buildings
MAX_SPREAD = 60    # Most extra space added to each gap when a section is not full
MAX_TREES = 3      # Most trees added at the end of a section
TREE = 80          # Width of a tree (buildings.tree_width)
MAX_SECTIONS = 5   # Each section uses about 4 MB of texture memory on the Roku

def split(items):
    """Splits the buildings into sections, in order. A building that does not
    fit in the current section starts the next one."""
    sections, current, used = [], [], 0
    for b in items:
        if b["type"] == "section_break":
            if current:
                sections.append(current)
            current, used = [], 0
            continue
        w = buildings.width(b)
        if w > SECTION - 2 * MARGIN:
            raise ConfigError(f"{b.get('name', b['type'])} is {w} pixels wide, which is wider than a town section.")
        need = w if not current else used + GAP + w
        if need > SECTION - 2 * MARGIN:
            sections.append(current)
            current, used = [b], w
        else:
            current.append(b)
            used = need
    if current:
        sections.append(current)
    return sections

def place(section):
    """Returns (spec, x) for each building in one section. Extra space is
    spread between the buildings, and up to MAX_TREES trees, in different
    sizes, stand in the space left at the end."""
    widths = [buildings.width(b) for b in section]
    room = SECTION - 2 * MARGIN - sum(widths) - GAP * (len(section) - 1)
    spread = min(MAX_SPREAD, room // (len(section) + 1))
    x = MARGIN + spread
    out = []
    for b, w in zip(section, widths):
        out.append((b, x))
        x += w + GAP + spread
    # Trees in the space that is left at the end
    end = SECTION - MARGIN
    x -= spread
    n = min(MAX_TREES, max(0, (end - x) // (TREE + GAP)))
    space = (end - x - n * TREE) / (n + 1)
    for k in range(n):
        out.append(({"type": "tree", "size": k}, round(x + space * (k + 1) + TREE * k)))
    return out

def layout(town):
    sections = split(town["buildings"])
    if len(sections) > MAX_SECTIONS:
        extra = sum(len(s) for s in sections[MAX_SECTIONS:])
        raise ConfigError(f"The buildings need {len(sections)} town sections, and the most is {MAX_SECTIONS}. "
                          f"Remove about {extra} buildings, or make some narrower.")
    placed = [place(s) for s in sections]
    gas = [(i, x) for i, s in enumerate(placed) for b, x in s if b["type"] == "gas_station"]
    # The parked car goes at the first gas station, in strip coordinates
    town["parked_car_x"] = gas[0][0] * SECTION + buildings.gas_parking(gas[0][1]) if gas else -1
    # The tall tower behind each radio station, at the center of the station
    town["towers"] = [i * SECTION + x + 240 for i, s in enumerate(placed) for b, x in s
                      if b["type"] == "radio_station" and b.get("tower", True)]
    town["sections"] = placed
    return placed
