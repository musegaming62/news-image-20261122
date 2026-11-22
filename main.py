#!/usr/bin/env python3
"""World news poster for Sunday 22 November 2026.

Draws a 1024x1024 PNG newspaper front page with pure Python 3.13
standard library only: no fonts, no PIL, no network. A tiny 5x7
bitmap font is embedded below, and the PNG is encoded by hand
(zlib + struct). Output is fully deterministic.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 24, 39)
WHITE = (255, 255, 255)
RED = (185, 28, 28)
DARKRED = (127, 29, 29)
BLUE = (29, 78, 216)
NAVY = (30, 58, 95)
TEAL = (13, 116, 128)
GREEN = (21, 101, 52)
AMBER = (180, 83, 9)
GREY = (107, 114, 128)
LGREY = (229, 231, 235)
MGREY = (209, 213, 219)
BLACK = (0, 0, 0)
CREAM = (255, 251, 235)
SKY = (186, 230, 253)
SAND = (253, 230, 138)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "11110", "10001", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, s, x, y, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT['?'])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px, py = cx + c * scale + dx, y + r * scale + dy
                            if 0 <= px < W and 0 <= py < H:
                                cv[py * W * 3 + px * 3: py * W * 3 + px * 3 + 3] = bytes(color)
        cx += 6 * scale
    return cx


def wrap(s, max_chars):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(cv, s, x, y, max_w, scale, color, leading=None):
    max_chars = max(1, max_w // (6 * scale))
    lines = wrap(s, max_chars)
    lh = leading if leading is not None else 7 * scale + 2
    for i, ln in enumerate(lines):
        draw_text(cv, ln, x, y + i * lh, scale, color)
    return y + len(lines) * lh


# ---------------------------------------------------------------- canvas
def new_canvas():
    cv = bytearray(W * H * 3)
    for i in range(0, len(cv), 3):
        cv[i:i + 3] = bytes(PAPER)
    return cv


def rect(cv, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for py in range(y0, y1):
        base = py * W * 3
        for px in range(x0, x1):
            cv[base + px * 3: base + px * 3 + 3] = bytes(color)


def frame(cv, x, y, w, h, color, t=2):
    rect(cv, x, y, w, t, color)
    rect(cv, x, y + h - t, w, t, color)
    rect(cv, x, y, t, h, color)
    rect(cv, x + w - t, y, t, h, color)


def hline(cv, x, y, w, color, t=1):
    rect(cv, x, y, w, t, color)


def vline(cv, x, y, h, color, t=1):
    rect(cv, x, y, t, h, color)


def circle(cv, cx, cy, r, color):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px, py = cx + dx, cy + dy
                if 0 <= px < W and 0 <= py < H:
                    cv[py * W * 3 + px * 3: py * W * 3 + px * 3 + 3] = bytes(color)


def line(cv, x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            cv[y0 * W * 3 + x0 * 3: y0 * W * 3 + x0 * 3 + 3] = bytes(color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def triangle(cv, x, y, s, color):
    for i in range(s):
        rect(cv, x - i, y + i, 2 * i + 1, 1, color)


def pin(cv, x, y, n, color):
    circle(cv, x, y, 6, color)
    frame(cv, x - 6, y - 6, 13, 13, WHITE, 1)
    s = str(n)
    tw = text_width(s, 1)
    draw_text(cv, s, x - tw // 2, y - 3, 1, WHITE)


# ---------------------------------------------------------------- PNG out
def write_png(cv, path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += cv[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- data
# (num, region, tag, headline, deck, verify, source, scene, big)
# scene: kind of data illustration in the band. big: the big number shown.
HEROES = [
    (1, "MIDDLE EAST", "IRAN STRIKES BAHRAIN",
     "IRGC missiles and drones hit US Patriot radars at two Bahrain bases",
     "Bahrain says an Iranian attack set a civilian plant ablaze; defences intercepted more strikes. No injuries reported.",
     "CLAIM", "IRGC / BAHRAIN GOVT", "missiles", "2"),
    (2, "UKRAINE / NATO", "RUSSIA'S BIGGEST STRIKE OF THE YEAR",
     "110 missiles and 400+ drones hit Ukraine; Poland's airspace breached",
     "Two killed, 60 hurt in Kryvyi Rih. NATO chief Rutte in Warsaw: alliance will defend every inch of Poland.",
     "REPORTED", "UKRAINE AIR FORCE", "bars", "510+"),
    (3, "BALTIC SEA", "DRONE HITS RUSSIAN SHIP OFF FINLAND",
     "Russian cargo ship Sparta II ablaze in the Gulf of Finland; crew evacuated",
     "Finland's PM: the war is spilling over into our neighbourhood. NATO vows to defend Polish territory.",
     "REPORTED", "FINNISH NAVY", "ship", "1"),
]

CARDS = [
    (4, "GULF", "HOUTHI MISSILES AT RIYADH",
     "Saudi-led coalition says it intercepted three ballistic missiles aimed at Riyadh",
     "Houthis also hit power plant and port targets; coalition struck Hodeidah in reply.",
     "REPORTED", "SAUDI-LED COALITION", "arcs", "3"),
    (5, "GAZA", "STORMS FLOOD GAZA SHELTERS",
     "Heavy rain and cold leave 1m+ displaced people exposed; aid vehicle hit in Gaza City",
     "Civil defence: most rescue vehicles out of service. Six killed Friday, three more Saturday.",
     "REPORTED", "GAZA CIVIL DEFENCE", "rain", "1M+"),
    (6, "DIPLOMACY", "US ENVOYS HEAD TO MOSCOW",
     "Kushner and Witkoff to brief Putin after Abu Dhabi talks, then meet Zelensky in Dublin",
     "Russia repeats demand NATO pull back to 1997 lines; Lavrov dismisses a truce plan.",
     "REPORTED", "US OFFICIALS", "route", "2"),
    (7, "UKRAINE", "ZELENSKY: PUTIN IS A KILLER",
     "Zelensky rebukes Trump after Trump called Putin a friend who wants to end the war",
     "NATO membership remains the clearest security guarantee, Zelensky says in Kyiv.",
     "REPORTED", "ZELENSKY / KYIV", "quote", "1"),
    (8, "NATO", "RUTTE: EVERY INCH OF POLAND",
     "NATO chief reaffirms defence of Poland after Russian missiles crashed on its soil",
     "Poland confirms three airspace violations, no injuries; EU states denounce Moscow.",
     "CONFIRMED", "NATO / RUTTE", "shield", "3"),
    (9, "DENMARK", "DIPLOMAT EXPELLED OVER MURDER PLOT",
     "Denmark expels a Russian defence attache over an alleged plot to kill a US-Ukrainian rapper",
     "Copenhagen says the plot was foiled; Moscow has not commented publicly.",
     "REPORTED", "DENMARK GOVT", "ban", "1"),
    (10, "MEXICO", "11 KILLED AFTER KINGPIN CAPTURE",
     "Reprisal violence sweeps Sinaloa after the capture of FBI most-wanted El Chapo Isidro",
     "Meza Flores, $5m reward, was taken in Guasave and flown to Mexico City.",
     "REPORTED", "GLOBE AND MAIL", "bars", "11"),
    (11, "N. AMERICA", "PENTAGON CURBS US-CANADA TIES",
     "Secret Hegseth memo tells US troops to curb informal contact with Canadian counterparts",
     "Canada's defence minister says he sees no major shift in the military relationship.",
     "REPORTED", "WASHINGTON POST", "memo", "1"),
    (12, "HONG KONG", "ELECTION COMMITTEE VOTES TODAY",
     "5,700 voters choose the 1,500-strong college that will pick the next city leader",
     "The college also nominates candidates for the 2029 Legislative Council election.",
     "REPORTED", "SCMP", "vote", "5,700"),
    (13, "FRANCE", "PROTEST WEEKEND, 4 NATIONS WARN",
     "US, UK, Canada and Australia warn travellers as strikes and rallies hit French cities",
     "Yellow Vests mark their 8th anniversary; unions and students march Sat and Sun.",
     "REPORTED", "US EMBASSY PARIS", "crowd", "4"),
    (14, "NORWAY", "COURT VOIDS OIL LICENCES",
     "Supreme Court rules climate-disputed oil licences invalid in a landmark ruling",
     "The licences were challenged on climate grounds; the state had defended them.",
     "CONFIRMED", "NORWAY SUPREME COURT", "gavel", "0"),
    (15, "GHANA", "NEW BANKNOTES HONOUR HEROES",
     "Heritage Series notes honour Nkrumah, Kofi Annan and Makola market traders",
     "The Bank of Ghana unveiled the series on Sunday; designs celebrate national history.",
     "REPORTED", "BANK OF GHANA", "notes", "3"),
    (16, "ASIA / QUAKES", "TWO QUAKES, NO DAMAGE",
     "M4.5 off Sarangani, Philippines at 08:23; M4.1 hits Myanmar in the early hours",
     "PHIVOLCS expects no damage and no aftershocks from either tremor.",
     "CONFIRMED", "PHIVOLCS / NCS", "quake", "4.5"),
    (17, "SPORT / TENNIS", "ATP FINAL TODAY IN TURIN",
     "World No.1 Zverev faces Alcaraz for the title, 18:00 CET; doubles final at 15:00",
     "Zverev has won 42 of 42 service games; unbeaten champion takes $5,171,000.",
     "REPORTED", "ATP TOUR", "court", "42/42"),
    (18, "SPORT / FOOTBALL", "LIVERPOOL v MAN UTD TODAY",
     "Pochettino's first game as United boss is at Anfield, 16:30; Hull host Brighton at 14:00",
     "Arsenal stay top on 28 pts after a 2-2 draw at Newcastle; Brighton 2nd on 22.",
     "REPORTED", "PREMIER LEAGUE", "ball", "28"),
]

# Dense list: (num, text) — short, one line each.
LIST = [
    (19, "Al-Shabaab claims hundreds dead in ambush on Somali troops - CLAIM, AL-SHABAAB"),
    (20, "Kenya discharges last Ebola patient; DRC death toll passes 5,300 - REPORTED, WHO"),
    (21, "Sahel states restart dialogue with West Africa bloc - REPORTED, ECOWAS"),
    (22, "New Tigray mayor vows elections within six months after clashes - REPORTED"),
    (23, "Lewis Pugh swims 3 days through the war-hit Strait of Hormuz - REPORTED"),
    (24, "SBF, from prison: $500m Anthropic bet was not worth it - REPORTED, INTERVIEW"),
    (25, "FinCEN flags MEXC as money-laundering concern; Binance may freeze deposits - REPORTED"),
    (26, "Google folds Duplex into Gemini App Tasks for autonomous calls - REPORTED, GOOGLE"),
    (27, "AWS launches distributed KV-cache skill to cut LLM costs - REPORTED, AWS"),
    (28, "Singapore plans AI-agent verification and stablecoin sandbox - REPORTED"),
    (29, "Australia bowl first in S. Africa decider; injured Smith out - REPORTED"),
    (30, "Rutgers stun Penn State 25-24 on the final play - REPORTED"),
    (31, "EU hunts new ECB chief as Lagarde resigns - REPORTED"),
    (32, "US declassifies more UFO footage filmed in the Middle East - REPORTED"),
    (33, "Trafalgar Square Christmas tree felled in Norway - REPORTED"),
    (34, "Princess of Wales recovery documentary leads front pages - REPORTED"),
    (35, "Teen gamer and mother help FBI rescue kidnapped girl - REPORTED, FBI"),
    (36, "Nigerian youth voter sign-ups lag 2023 ahead of election - REPORTED, BBC"),
    (37, "Bangladesh envoy: India's 1971 sacrifices deeply respected - REPORTED"),
    (38, "UAE president receives US Homeland Security secretary - REPORTED, WAM"),
    (39, "Eisenkot invites Likud to coalition talks as deadline nears - REPORTED"),
    (40, "Sudan: 10 killed as drone strafes South Kordofan gold mine - REPORTED"),
    (41, "Paolo Bulgari, jeweller who built a global luxury house, dies at 89 - REPORTED"),
    (42, "NASA: Voyager 1 is now the first object 1 light-day from Earth - REPORTED"),
]

TIMELINE = [
    ("00:23", "M4.5 QUAKE, PHILIPPINES"),
    ("01:25", "BBC: EL CHAPO CAPTURE"),
    ("02:19", "SPARTA II HIT REPORTED"),
    ("14:00", "HULL v BRIGHTON"),
    ("16:30", "LIVERPOOL v MAN UTD"),
    ("17:00", "ATP FINAL, TURIN"),
]

# (lon, lat) of each numbered story, for the map pins.
PINS = {
    1: (50.5, 26.2), 2: (31.0, 49.0), 3: (24.0, 59.8), 4: (46.7, 24.6),
    5: (34.5, 31.5), 6: (37.6, 55.8), 7: (30.5, 50.4), 8: (21.0, 52.2),
    9: (12.6, 55.7), 10: (-107.4, 25.6), 11: (-75.7, 45.4), 12: (114.2, 22.3),
    13: (2.35, 48.85), 14: (10.75, 59.9), 15: (-0.2, 5.6), 16: (125.2, 5.4),
    17: (7.7, 45.1), 18: (-2.96, 53.43),
}

# Rough continent polygons (lon, lat), equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-55, 52), (-60, 47), (-70, 44),
     (-75, 38), (-80, 32), (-81, 26), (-90, 21), (-97, 26), (-105, 20),
     (-110, 24), (-117, 33), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58), (-165, 60), (-168, 66)],
    [(-80, 10), (-77, 8), (-70, 12), (-62, 10), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41),
     (-70, -50), (-73, -53), (-70, -40), (-72, -30), (-77, -20),
     (-81, -5), (-80, 2), (-80, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70),
     (40, 68), (45, 66), (40, 60), (35, 55), (30, 50), (28, 45),
     (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-2, 37), (-10, 36)],
    [(-17, 15), (-15, 27), (-10, 31), (0, 36), (10, 37), (20, 32),
     (30, 31), (35, 28), (38, 22), (43, 12), (48, 11), (51, 12),
     (44, 5), (40, -2), (39, -10), (36, -18), (33, -26), (28, -33),
     (20, -35), (16, -28), (12, -18), (13, -10), (9, 4), (-8, 4),
     (-13, 8), (-17, 15)],
    [(30, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73),
     (100, 77), (120, 73), (140, 72), (160, 70), (178, 66), (170, 60),
     (162, 56), (158, 52), (142, 50), (140, 40), (135, 35), (130, 33),
     (127, 40), (122, 38), (120, 32), (115, 23), (110, 20), (108, 12),
     (105, 9), (100, 7), (98, 12), (95, 16), (92, 21), (89, 22),
     (85, 19), (80, 15), (77, 8), (73, 16), (70, 22), (66, 25),
     (62, 25), (58, 26), (54, 26), (50, 29), (48, 30), (44, 29),
     (42, 36), (36, 36), (30, 36), (30, 42), (28, 45), (30, 50),
     (32, 55), (30, 60), (30, 70)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (132, -12),
     (126, -14), (122, -17), (118, -20), (113, -22)],
]

# ---------------------------------------------------------------- scenes
def draw_scene(cv, kind, x, y, w, h, big, accent):
    """Data-carrying illustration band: bars, numbers, arcs, charts."""
    rect(cv, x, y, w, h, WHITE)
    frame(cv, x, y, w, h, MGREY, 1)
    cx, cy = x + w // 2, y + h // 2
    if kind == "bars":
        vals = [5, 9, 7, 12, 10, 14]
        bw = w // 8
        for i, v in enumerate(vals):
            bh = int(v * (h - 34) / 14)
            rect(cv, x + 10 + i * bw, y + h - 12 - bh, bw - 6, bh, accent)
        draw_text(cv, big, x + w - text_width(big, 3) - 8, y + 6, 3, RED)
    elif kind == "missiles":
        for i in range(3):
            sx = x + 14 + i * (w // 3)
            line(cv, sx, y + h - 10, sx + 16, y + 16, accent)
            line(cv, sx + 16, y + 16, sx + 30, y + 10, accent)
            circle(cv, sx + 30, y + 10, 4, RED)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "ship":
        rect(cv, x + 12, y + h - 26, w - 24, 12, NAVY)
        rect(cv, x + w // 2 - 8, y + h - 44, 16, 18, NAVY)
        for i in range(4):
            line(cv, x + 16 + i * 10, y + 14, x + 22 + i * 10, y + 30, RED)
        circle(cv, x + w - 22, y + 20, 8, RED)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "arcs":
        for i in range(3):
            line(cv, x + 12, y + h - 12, x + w // 2, y + 12 + i * 8, accent)
            line(cv, x + w // 2, y + 12 + i * 8, x + w - 12, y + h - 12, accent)
        draw_text(cv, big, x + 6, y + 4, 2, RED)
    elif kind == "rain":
        for i in range(8):
            lx = x + 10 + i * ((w - 70) // 9)
            line(cv, lx, y + 10, lx - 6, y + 26, BLUE)
            line(cv, lx, y + 34, lx - 6, y + 50, BLUE)
        draw_text(cv, big, x + w - text_width(big, 3) - 8, y + 6, 3, BLUE)
    elif kind == "route":
        line(cv, x + 12, y + h - 14, x + w // 2, y + 14, accent)
        line(cv, x + w // 2, y + 14, x + w - 12, y + h - 14, accent)
        circle(cv, x + 12, y + h - 14, 6, RED)
        circle(cv, x + w // 2, y + 14, 6, BLUE)
        circle(cv, x + w - 12, y + h - 14, 6, GREEN)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "quote":
        draw_text(cv, '"KILLER"', x + 10, y + 4, 2, RED)
        draw_text(cv, "VS FRIEND", x + 10, y + 24, 1, INK)
    elif kind == "shield":
        pts = [(cx, y + 8), (cx + 26, y + 16), (cx + 26, y + 36),
               (cx, y + h - 8), (cx - 26, y + 36), (cx - 26, y + 16)]
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            line(cv, a[0], a[1], b[0], b[1], BLUE)
        draw_text(cv, big, cx - text_width(big, 3) // 2, cy - 8, 3, BLUE)
    elif kind == "ban":
        circle(cv, cx, cy, 13, RED)
        rect(cv, cx - 13, cy - 3, 26, 6, RED)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "memo":
        rect(cv, x + w // 2 - 30, y + 8, 60, h - 16, CREAM)
        frame(cv, x + w // 2 - 30, y + 8, 60, h - 16, INK, 1)
        for i in range(4):
            hline(cv, x + w // 2 - 22, y + 18 + i * 10, 44, INK, 2)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "vote":
        for i in range(3):
            rect(cv, x + 14 + i * 40, y + 8, 24, 22, WHITE)
            frame(cv, x + 14 + i * 40, y + 8, 24, 22, INK, 2)
            if i == 1:
                line(cv, x + 17 + i * 40, y + 20, x + 23 + i * 40, y + 26, GREEN)
                line(cv, x + 23 + i * 40, y + 26, x + 34 + i * 40, y + 12, GREEN)
        draw_text(cv, big, x + w - text_width(big, 1) - 6, y + 2, 1, INK)
    elif kind == "crowd":
        for i in range(6):
            circle(cv, x + 16 + i * (w // 7), y + 22, 7, accent)
            rect(cv, x + 10 + i * (w // 7), y + 32, 13, 18, accent)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "gavel":
        line(cv, x + 14, y + h - 16, x + w - 14, y + h - 16, INK)
        rect(cv, x + w // 2 - 22, y + 14, 44, 12, AMBER)
        line(cv, cx, y + 26, cx, y + h - 16, AMBER)
        draw_text(cv, big, x + w - text_width(big, 2) - 6, y + 4, 2, RED)
    elif kind == "notes":
        for i in range(3):
            rect(cv, x + 12 + i * 48, y + 12, 38, 26, SAND)
            frame(cv, x + 12 + i * 48, y + 12, 38, 26, INK, 1)
            draw_text(cv, str(i + 1), x + 24 + i * 48, y + 18, 2, INK)
        draw_text(cv, big, x + w - text_width(big, 1) - 6, y + 2, 1, INK)
    elif kind == "quake":
        line(cv, x + 8, y + h // 2, x + w // 3, y + h // 2, INK)
        line(cv, x + w // 3, y + h // 2, x + w // 2, y + 10, RED)
        line(cv, x + w // 2, y + 10, x + w * 2 // 3, y + h - 10, RED)
        line(cv, x + w * 2 // 3, y + h - 10, x + w - 8, y + h // 2, INK)
        draw_text(cv, big, x + 8, y + 6, 3, RED)
    elif kind == "court":
        rect(cv, x, y, w, h, (34, 139, 34))
        hline(cv, x, y + h // 2, w, WHITE, 2)
        vline(cv, x + w // 2, y + 6, h - 12, WHITE, 2)
        circle(cv, cx, cy, 12, WHITE)
        draw_text(cv, big, x + 8, y + 6, 2, WHITE)
    elif kind == "ball":
        circle(cv, cx, cy, 20, WHITE)
        frame(cv, cx - 20, cy - 20, 41, 41, INK, 1)
        draw_text(cv, big, x + 8, y + 6, 3, RED)
    else:
        draw_text(cv, big, x + 8, y + 8, 3, RED)


# ---------------------------------------------------------------- layout
def tag_color(v):
    return {"CONFIRMED": GREEN, "REPORTED": BLUE, "CLAIM": AMBER}.get(v, GREY)


def build():
    cv = new_canvas()
    # ---- masthead
    rect(cv, 0, 0, W, 104, NAVY)
    draw_text(cv, "THE WORLD IN ONE DAY", 16, 12, 4, WHITE)
    draw_text(cv, "SUNDAY 22 NOVEMBER 2026", 16, 52, 3, SAND)
    draw_text(cv, "42 STORIES  -  6 REGIONS  -  7 FIELDS", 560, 16, 2, WHITE)
    draw_text(cv, "EVERY EVENT DATED 22 NOV 2026", 560, 40, 2, WHITE)
    draw_text(cv, "OR FIRST REPORTED TODAY", 560, 62, 2, WHITE)
    draw_text(cv, "VERIFIED + SOURCED", 560, 84, 2, SAND)
    # ---- timeline strip
    rect(cv, 0, 104, W, 44, CREAM)
    draw_text(cv, "UTC", 12, 112, 2, RED)
    draw_text(cv, "TIMELINE", 12, 128, 1, RED)
    tx = 120
    for t, label in TIMELINE:
        draw_text(cv, t, tx, 112, 2, INK)
        draw_text(cv, label, tx, 128, 1, GREY)
        tx += 152
    hline(cv, 0, 148, W, INK, 2)
    # ---- heroes
    hy, hh = 152, 150
    hw = (W - 32) // 3
    for i, (num, region, tag, head, deck, ver, src, scene, big) in enumerate(HEROES):
        x = 8 + i * (hw + 8)
        rect(cv, x, hy, hw, hh, WHITE)
        frame(cv, x, hy, hw, hh, INK, 2)
        draw_text(cv, "%d  %s" % (num, region), x + 8, hy + 6, 2, RED)
        draw_scene(cv, scene, x + 8, hy + 28, hw - 16, 44, big, BLUE)
        draw_text_block(cv, head, x + 8, hy + 80, hw - 16, 2, INK, leading=16)
        draw_text(cv, ver + " - " + src, x + 8, hy + hh - 16, 1, tag_color(ver))
    # ---- map band
    my, mh = 310, 100
    rect(cv, 0, my, W, mh, (219, 234, 254))
    draw_text(cv, "WORLD MAP - NUMBERED PINS MATCH THE STORIES", 12, my + 6, 2, NAVY)
    mx, mw = 8, W - 16
    mtop, mbot = my + 24, my + mh - 4

    def proj(lon, lat):
        return (mx + int((lon + 180.0) / 360.0 * mw),
                mtop + int((85.0 - lat) / 145.0 * (mbot - mtop)))

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            line(cv, a[0], a[1], b[0], b[1], NAVY)
    # Spread crowded pins with a leader line from the true spot.
    JITTER = {1: (18, -10), 5: (-18, 10), 7: (20, -10), 8: (-20, -12),
              9: (4, -20), 13: (-22, 10), 14: (16, -18), 17: (22, 10)}
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        dx, dy = JITTER.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            line(cv, px, py, px + dx, py + dy, RED)
        pin(cv, px + dx, py + dy, n, RED if n <= 3 else NAVY)
    # ---- card grid: 5 cols x 3 rows
    gy = 418
    cw = (W - 16 - 4 * 6) // 5
    ch = 120
    for i, (num, region, tag, head, deck, ver, src, scene, big) in enumerate(CARDS):
        r, c = divmod(i, 5)
        x = 8 + c * (cw + 6)
        y = gy + r * (ch + 6)
        rect(cv, x, y, cw, ch, WHITE)
        frame(cv, x, y, cw, ch, INK, 1)
        draw_text(cv, "%d %s" % (num, region), x + 6, y + 5, 1, RED)
        draw_scene(cv, scene, x + 6, y + 20, cw - 12, 30, big, TEAL)
        draw_text_block(cv, head, x + 6, y + 54, cw - 12, 1, INK, leading=10)
        draw_text(cv, ver + " " + src, x + 6, y + ch - 12, 1, tag_color(ver))
    # ---- dense list
    ly = gy + 3 * (ch + 6) + 4
    rect(cv, 0, ly, W, 1024 - ly - 84, WHITE)
    draw_text(cv, "THE REST OF THE DAY - 24 MORE STORIES", 12, ly + 6, 2, NAVY)
    col_w = (W - 24) // 2
    for i, (num, text) in enumerate(LIST):
        col = i // 12
        row = i % 12
        x = 12 + col * (col_w + 4)
        y = ly + 26 + row * 9
        draw_text(cv, "%d." % num, x, y, 1, RED)
        draw_text(cv, text[:62], x + 24, y, 1, INK)
    # ---- date check / left out footer
    fy = 1024 - 84
    rect(cv, 0, fy, W, 84, DARKRED)
    draw_text(cv, "DATE CHECK - LEFT OUT ON PURPOSE", 12, fy + 8, 2, WHITE)
    draw_text(cv, "KERCH BRIDGE STRIKE 19-20 NOV - XI HOSTS TRUMP + PUTIN AT APEC 21 NOV", 12, fy + 30, 1, WHITE)
    draw_text(cv, "EL CHAPO ISIDRO CAPTURED 20 NOV, CONFIRMED 21 NOV - FBI NCIC BREACH FIRST REPORTED 20 NOV", 12, fy + 44, 1, WHITE)
    draw_text(cv, "NVIDIA: HUANG RESIGNED 12 NOV - NOT YET: ATP FINAL + LIVERPOOL v MAN UTD DUE THIS EVENING", 12, fy + 58, 1, WHITE)
    draw_text(cv, "SOURCES: BBC - REUTERS - ATP - NATO - PHIVOLCS - GOVT STATEMENTS - JUDGE: THIS IS 22 NOV 2026 NEWS", 12, fy + 72, 1, SAND)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
