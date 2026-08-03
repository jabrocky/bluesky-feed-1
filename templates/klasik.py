#!/usr/bin/env python3
"""Zápasové grafiky mládeže — Baseball Klasik Frýdek-Místek.

Barvy vychází přímo z klubového loga (bizon s pálkou):
vínová, klubová červená, písková a krémová.

Varianty:
  • klasik_gameday(...)  — pozvánka na zápas
  • klasik_vysledek(...) — výsledek po zápase
  • klasik_rozpis(...)   — rozpis více zápasů

Každá umí format="story" (1080×1920) nebo "post" (1080×1350).

Příklad:
    from klasik import klasik_gameday
    klasik_gameday("U13", "Arrows Ostrava", "sobota 12. 7.", "10:00",
                   "Frýdek-Místek", "gameday.png", home=True)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO = os.path.join(ASSETS, "logo_klasik.png")

# ── paleta z loga ─────────────────────────────────────────────
MAROON_DK = (34, 16, 16)      # pozadí nahoře
MAROON = (87, 45, 45)         # pozadí dole / obrysy
RED = (196, 52, 52)           # klubová červená
RED_DK = (150, 36, 40)
SAND = (249, 202, 125)        # písková (akcenty, popisky)
CREAM = (247, 237, 209)       # hlavní světlý text
WHITE = (255, 255, 255)
MUTED = (168, 138, 128)

F_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BI = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"

CLUB = "KLASIK FRÝDEK-MÍSTEK"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, path, size, max_w, min_size=24):
    """Zmenší písmo, dokud se text nevejde do max_w."""
    f = font(path, size)
    while d.textlength(text, font=f) > max_w and size > min_size:
        size -= 2
        f = font(path, size)
    return f


def _stripes(img, W, H):
    """Jemné diagonální pruhy v klubové červené."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    step, w = 86, 26
    for i in range(-H, W + H, step):
        od.line([(i, H), (i + H, 0)], fill=RED + (26,), width=w)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))


def _ball(d, cx, cy, r, col):
    """Obrys míčku se švy."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=5)
    d.arc([cx - r + r * 0.42, cy - r - r * 0.5, cx + r + r * 1.1, cy + r + r * 0.5],
          150, 210, fill=col, width=5)
    d.arc([cx - r - r * 1.1, cy - r - r * 0.5, cx + r - r * 0.42, cy + r + r * 0.5],
          330, 30, fill=col, width=5)


def _base(W, H):
    img = Image.new("RGB", (W, H), MAROON_DK)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = (y / H) ** 0.85
        c = tuple(int(MAROON_DK[i] + (MAROON[i] - MAROON_DK[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    _stripes(img, W, H)
    d = ImageDraw.Draw(img)
    _ball(d, W + 120, H - 150, 320, (255, 255, 255, 255) and (110, 62, 58))
    bar = 14 if H > 1500 else 12
    d.rectangle([0, 0, W, bar], fill=RED)
    d.rectangle([0, H - bar, W, H], fill=SAND)
    d.rectangle([0, H - bar - 6, W, H - bar], fill=RED)
    return img, d


def _logo(img, W, cy, h):
    lg = Image.open(LOGO).convert("RGBA")
    s = h / lg.size[1]
    lg = lg.resize((int(lg.size[0] * s), h), Image.LANCZOS)
    img.paste(lg, ((W - lg.size[0]) // 2, cy), lg)
    return lg.size[1]


def _chip(d, text, cx, cy, size, fill=RED, fg=CREAM):
    f = font(F_BOLD, size)
    w = d.textlength(text, font=f) + 66
    h = size * 2.1
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=h / 2, fill=fill)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")
    return w


def _footer(d, W, H, story, note=None):
    y = H - (86 if story else 62)
    d.text((W // 2, y), CLUB, font=font(F_BOLD, 28 if story else 24),
           fill=SAND, anchor="mm")
    if note:
        d.text((W // 2, y + (44 if story else 36)), note,
               font=font(F_REG, 24 if story else 21), fill=MUTED, anchor="mm")


def _teams(img, d, W, y, home_name, away_name, size=54, opponent_logo=None):
    """Dva týmy pod sebou s VS mezi nimi. Klasik je vždy zvýrazněný."""
    rows = [(home_name, home_name.upper().startswith("KLASIK")),
            (away_name, away_name.upper().startswith("KLASIK"))]
    for i, (name, is_club) in enumerate(rows):
        ry = y + i * (size + 78)
        f = fit(d, name, F_BOLD, size, W - 260)
        d.text((W // 2, ry), name, font=f,
               fill=CREAM if is_club else WHITE, anchor="mm")
        if is_club:
            tw = d.textlength(name, font=f)
            d.line([(W / 2 - tw / 2, ry + size * 0.62),
                    (W / 2 + tw / 2, ry + size * 0.62)], fill=SAND, width=5)
        if i == 0:
            my = ry + (size + 78) / 2
            d.line([(W / 2 - 190, my), (W / 2 - 46, my)], fill=(120, 70, 66), width=3)
            d.line([(W / 2 + 46, my), (W / 2 + 190, my)], fill=(120, 70, 66), width=3)
            d.text((W // 2, my), "VS", font=font(F_BOLD, 40), fill=RED, anchor="mm")
    return y + 2 * size + 78


def _info_row(d, W, y, items, story):
    """Popisek + hodnota ve sloupcích."""
    n = len(items)
    col = W / n
    lf = font(F_BOLD, 22 if story else 20)
    vf = font(F_BOLD, 40 if story else 34)
    for i, (label, value) in enumerate(items):
        cx = col * (i + 0.5)
        d.text((cx, y), label, font=lf, fill=SAND, anchor="mm")
        f = fit(d, value, F_BOLD, vf.size, col - 40, min_size=20)
        d.text((cx, y + (46 if story else 40)), value, font=f, fill=CREAM, anchor="mm")
        if i < n - 1:
            d.line([(col * (i + 1), y - 18), (col * (i + 1), y + (66 if story else 58))],
                   fill=(120, 70, 66), width=2)



def _distribute(top, bottom, heights):
    """Rozloží bloky mezi top a bottom se stejnými mezerami."""
    gap = (bottom - top - sum(heights)) / (len(heights) + 1)
    ys, y = [], top + gap
    for h in heights:
        ys.append(y)
        y += h + gap
    return ys


def _photo_panel(img, d, box, path):
    x1, y1, x2, y2 = [int(v) for v in box]
    bw, bh = x2 - x1, y2 - y1
    p = Image.open(path).convert("RGB")
    sc = max(bw / p.size[0], bh / p.size[1])
    nw, nh = int(p.size[0] * sc) + 1, int(p.size[1] * sc) + 1
    rs = p.resize((nw, nh), Image.LANCZOS)
    cx, cy = (nw - bw) // 2, int((nh - bh) * 0.35)
    crop = rs.crop((cx, cy, cx + bw, cy + bh))
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=22, fill=255)
    img.paste(crop, (x1, y1), mask)
    d.rounded_rectangle([x1, y1, x2, y2], radius=22, outline=RED, width=4)


def _cta_bar(d, W, y, h, text):
    d.rounded_rectangle([70, y, W - 70, y + h], radius=h / 2, fill=RED)
    f = font(F_BOLD, int(h * 0.42))
    d.text((W // 2, y + h / 2), text, font=f, fill=CREAM, anchor="mm")

# ───────────────────────────── GAMEDAY ─────────────────────────────
def klasik_gameday(kategorie, souper, datum, cas, misto, out,
                   format="story", home=True, note=None, photo=None,
                   cta="PŘIJĎ FANDIT!"):
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img, d = _base(W, H)

    lh = 290 if story else 200
    top_pad = 50 if story else 34
    _logo(img, W, top_pad, lh)
    d = ImageDraw.Draw(img)

    chip_h = 66 if story else 56
    title_size = 128 if story else 96
    title_h = title_size + 40
    name_size = 66 if story else 52
    teams_h = name_size * 2 + (86 if story else 68)
    info_h = 90 if story else 78
    cta_h = 96 if story else 80
    photo_h = (540 if story else 300) if photo else 0

    heights = [chip_h, title_h, teams_h]
    if photo:
        heights.append(photo_h)
    heights += [info_h]
    if cta:
        heights.append(cta_h)

    ys = _distribute(top_pad + lh + (16 if story else 8), H - (150 if story else 108),
                     heights)
    i = 0
    _chip(d, kategorie.upper(), W // 2, ys[i] + chip_h / 2, 30 if story else 26); i += 1

    ty = ys[i] + title_size / 2
    d.text((W // 2, ty), "GAMEDAY", font=font(F_BOLD, title_size), fill=CREAM, anchor="mm")
    d.line([(W / 2 - 200, ty + title_size * 0.66), (W / 2 + 200, ty + title_size * 0.66)],
           fill=RED, width=6)
    i += 1

    home_name = "KLASIK FM" if home else souper.upper()
    away_name = souper.upper() if home else "KLASIK FM"
    _teams(img, d, W, ys[i] + name_size / 2, home_name, away_name, name_size); i += 1

    if photo:
        _photo_panel(img, d, (70, ys[i], W - 70, ys[i] + photo_h), photo); i += 1

    _info_row(d, W, ys[i] + 20, [("DATUM", datum), ("ZAČÁTEK", cas), ("HŘIŠTĚ", misto)],
              story); i += 1

    if cta:
        _cta_bar(d, W, ys[i], cta_h, cta)

    _footer(d, W, H, story, note)
    img.save(out)
    return out


# ───────────────────────────── VÝSLEDEK ─────────────────────────────
def klasik_vysledek(kategorie, souper, skore_klasik, skore_souper, out,
                    format="story", home=True, datum=None, misto=None, note=None,
                    photo=None, sestava=None):
    """sestava: volitelný seznam řádků (např. nejlepší hráči zápasu)."""
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img, d = _base(W, H)

    lh = 260 if story else 185
    top_pad = 46 if story else 32
    _logo(img, W, top_pad, lh)
    d = ImageDraw.Draw(img)

    if skore_klasik > skore_souper:
        verdict, vcol = "VÝHRA", SAND
    elif skore_klasik == skore_souper:
        verdict, vcol = "REMÍZA", CREAM
    else:
        verdict, vcol = "PROHRA", MUTED

    chip_h = 66 if story else 56
    vsize = 96 if story else 74
    v_h = vsize + 16
    card_h = 260 if story else 205
    info_h = 90 if story else 78
    photo_h = (470 if story else 280) if photo else 0
    lines = list(sestava or [])
    list_h = (len(lines) * (54 if story else 46) + 40) if lines else 0

    heights = [chip_h, v_h, card_h]
    if photo:
        heights.append(photo_h)
    if lines:
        heights.append(list_h)
    if datum or misto:
        heights.append(info_h)

    ys = _distribute(top_pad + lh + (14 if story else 6), H - (150 if story else 108),
                     heights)
    i = 0
    _chip(d, kategorie.upper(), W // 2, ys[i] + chip_h / 2, 30 if story else 26); i += 1
    d.text((W // 2, ys[i] + vsize / 2), verdict, font=font(F_BOLD, vsize),
           fill=vcol, anchor="mm"); i += 1

    cy_top = ys[i]
    d.rounded_rectangle([70, cy_top, W - 70, cy_top + card_h], radius=26,
                        fill=(52, 24, 24), outline=RED, width=4)
    left_name = "KLASIK FM" if home else souper.upper()
    right_name = souper.upper() if home else "KLASIK FM"
    left_score = skore_klasik if home else skore_souper
    right_score = skore_souper if home else skore_klasik
    nsize = 32 if story else 27
    ssize = 112 if story else 90
    mid = cy_top + card_h / 2
    for cx, name, score, is_club in (
            (W * 0.28, left_name, left_score, left_name.startswith("KLASIK")),
            (W * 0.72, right_name, right_score, right_name.startswith("KLASIK"))):
        f = fit(d, name, F_BOLD, nsize, W * 0.40, min_size=18)
        d.text((cx, mid - (74 if story else 60)), name, font=f,
               fill=SAND if is_club else MUTED, anchor="mm")
        d.text((cx, mid + (26 if story else 20)), str(score), font=font(F_BOLD, ssize),
               fill=CREAM if is_club else WHITE, anchor="mm")
    d.text((W // 2, mid + (14 if story else 10)), ":", font=font(F_BOLD, ssize),
           fill=RED, anchor="mm")
    i += 1

    if photo:
        _photo_panel(img, d, (70, ys[i], W - 70, ys[i] + photo_h), photo); i += 1

    if lines:
        lh2 = 54 if story else 46
        d.rounded_rectangle([70, ys[i], W - 70, ys[i] + list_h], radius=20,
                            fill=(52, 24, 24), outline=(120, 70, 66), width=2)
        ly = ys[i] + 20 + lh2 / 2
        for ln in lines:
            d.text((W // 2, ly), ln, font=font(F_REG, 30 if story else 26),
                   fill=CREAM, anchor="mm")
            ly += lh2
        i += 1

    if datum or misto:
        info = [x for x in (("DATUM", datum) if datum else None,
                            ("HŘIŠTĚ", misto) if misto else None) if x]
        _info_row(d, W, ys[i] + 20, info, story)

    _footer(d, W, H, story, note or "Díky za podporu!")
    img.save(out)
    return out


# ───────────────────────────── ROZPIS ─────────────────────────────
def klasik_rozpis(nadpis, zapasy, out, format="story", note=None):
    """zapasy: list (datum, cas, popis) — např. ("12. 7.", "10:00", "Klasik – Arrows")"""
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img, d = _base(W, H)

    lh = 230 if story else 175
    _logo(img, W, 50 if story else 34, lh)
    d = ImageDraw.Draw(img)

    y = (50 if story else 34) + lh + (34 if story else 22)
    f = fit(d, nadpis.upper(), F_BOLD, 68 if story else 54, W - 160)
    d.text((W // 2, y), nadpis.upper(), font=f, fill=CREAM, anchor="mm")
    d.line([(W / 2 - 180, y + 56), (W / 2 + 180, y + 56)], fill=RED, width=5)

    y += (110 if story else 92)
    row_h = 128 if story else 100
    for datum, cas, popis in zapasy:
        d.rounded_rectangle([70, y, W - 70, y + row_h - 16], radius=18,
                            fill=(52, 24, 24), outline=(120, 70, 66), width=2)
        cy = y + (row_h - 16) / 2
        d.text((110, cy - 18), datum, font=font(F_BOLD, 34 if story else 29),
               fill=SAND, anchor="lm")
        d.text((110, cy + 22), cas, font=font(F_REG, 28 if story else 24),
               fill=MUTED, anchor="lm")
        pf = fit(d, popis, F_BOLD, 38 if story else 32, W - 480)
        d.text((330, cy), popis, font=pf, fill=CREAM, anchor="lm")
        y += row_h

    _footer(d, W, H, story, note)
    img.save(out)
    return out
