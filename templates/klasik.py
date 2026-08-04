#!/usr/bin/env python3
"""Zápasové grafiky mládeže — Baseball Klasik Frýdek-Místek.

Navazuje na zavedený vizuál klubových příspěvků:
fotka na celou plochu, logo vlevo nahoře, krátký kicker, červená linka,
velký kondenzovaný titulek verzálkami a adresa webu dole.

Varianty:
  • klasik_gameday(...)  — pozvánka na zápas
  • klasik_vysledek(...) — výsledek po zápase
  • klasik_rozpis(...)   — rozpis více zápasů
  • klasik_info(...)     — obecný informační příspěvek

Formáty: format="post" (1080×1350) nebo "story" (1080×1920).
"""
import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO = os.path.join(ASSETS, "logo_klasik.png")

RED = (214, 32, 39)
WHITE = (255, 255, 255)
SAND = (249, 202, 125)
MAROON_DK = (32, 15, 15)
MAROON = (74, 34, 34)

F_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

WEB = "WWW.BK-KLASIK.CZ"
COND = 0.84          # míra stlačení písma (simulace condensed řezu)


def font(path, size):
    return ImageFont.truetype(path, size)


def _measure(d, text, size, cond=COND, path=F_BOLD):
    return d.textlength(text, font=font(path, size)) * cond


def _cond_text(img, text, cx, cy, size, fill, cond=COND, path=F_BOLD, track=0):
    """Vykreslí stlačený (condensed) text vystředěný na (cx, cy)."""
    f = font(path, size)
    tmp_d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    if track:
        text = (" " * 0).join(text)  # ponecháno kvůli čitelnosti volání
    w = int(tmp_d.textlength(text, font=f)) + size
    h = int(size * 1.8)
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((w / 2, h / 2), text, font=f, fill=fill, anchor="mm")
    nw = max(1, int(w * cond))
    tmp = tmp.resize((nw, h), Image.LANCZOS)
    img.paste(tmp, (int(cx - nw / 2), int(cy - h / 2)), tmp)


def _tracked_text(d, text, cx, cy, size, fill, spacing=6, path=F_BOLD):
    """Text s rozpalem (letter-spacing), vystředěný."""
    f = font(path, size)
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, cy), ch, font=f, fill=fill, anchor="lm")
        x += w + spacing


def _tracked_left(d, text, x, cy, size, fill, spacing=6, path=F_BOLD):
    """Text s rozpalem zarovnaný doleva od x."""
    f = font(path, size)
    for ch in text:
        d.text((x, cy), ch, font=f, fill=fill, anchor="lm")
        x += d.textlength(ch, font=f) + spacing


def _wrap_cond(d, text, size, max_w, cond=COND):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if _measure(d, t, size, cond) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_cond(d, text, size, max_w, cond=COND, min_size=28):
    while _measure(d, text, size, cond) > max_w and size > min_size:
        size -= 2
    return size


def _canvas(W, H, photo):
    """Fotka na celou plochu (cover) nebo klubový gradient jako záloha."""
    img = Image.new("RGB", (W, H), MAROON_DK)
    if photo:
        p = Image.open(photo).convert("RGB")
        sc = max(W / p.size[0], H / p.size[1])
        nw, nh = int(p.size[0] * sc) + 1, int(p.size[1] * sc) + 1
        rs = p.resize((nw, nh), Image.LANCZOS)
        img.paste(rs, (-(nw - W) // 2, -int((nh - H) * 0.35)))
    else:
        d = ImageDraw.Draw(img)
        for y in range(H):
            t = (y / H) ** 0.9
            c = tuple(int(MAROON_DK[i] + (MAROON[i] - MAROON_DK[i]) * t)
                      for i in range(3))
            d.line([(0, y), (W, y)], fill=c)
    return img


def _scrim(img, W, H, start=0.40, strength=232, veil=0):
    """Tmavý přechod odspodu, aby text držel kontrast."""
    if veil:
        v = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * veil)))
        img.paste(Image.alpha_composite(img.convert("RGBA"), v).convert("RGB"), (0, 0))
    top = int(H * start)
    ov = Image.new("RGBA", (W, H - top), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    n = H - top
    for i in range(n):
        a = int(strength * (i / n) ** 1.5)
        od.line([(0, i), (W, i)], fill=(0, 0, 0, a))
    img.paste(Image.alpha_composite(
        img.crop((0, top, W, H)).convert("RGBA"), ov).convert("RGB"), (0, top))
    # jemné ztmavení nahoře pod logem
    ov2 = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(ov2)
    for i in range(260):
        od2.line([(0, i), (W, i)], fill=(0, 0, 0, int(120 * (1 - i / 260))))
    img.paste(Image.alpha_composite(
        img.crop((0, 0, W, 260)).convert("RGBA"), ov2).convert("RGB"), (0, 0))


def _logo_tl(img, width, x=40, y=28):
    lg = Image.open(LOGO).convert("RGBA")
    s = width / lg.size[0]
    lg = lg.resize((width, int(lg.size[1] * s)), Image.LANCZOS)
    img.paste(lg, (x, y), lg)


def _bottom_block(img, d, W, H, kicker, headline_lines, hsize,
                  extra=None, extra_size=0, score=None, score_size=0):
    """Skládá obsah odspodu: web → info → titulek → linka → kicker."""
    story = H > 1500
    web_y = H - (58 if story else 48)
    _tracked_text(d, WEB, W / 2, web_y, 21 if story else 19, WHITE, spacing=5)

    y = web_y - (56 if story else 46)

    if extra:
        _tracked_text(d, extra, W / 2, y - extra_size * 0.5, extra_size,
                      (232, 226, 218), spacing=3)
        y -= extra_size + (34 if story else 28)

    line_gap = int(hsize * 1.02)
    for ln in reversed(headline_lines):
        _cond_text(img, ln, W / 2, y - hsize * 0.5, hsize, WHITE)
        y -= line_gap

    if score:
        y -= (10 if story else 6)
        _cond_text(img, score, W / 2, y - score_size * 0.52, score_size, SAND, cond=0.80)
        y -= int(score_size * 1.02)

    y -= (26 if story else 20)
    d.rectangle([64, y - 2, W - 64, y + 2], fill=RED)

    y -= (34 if story else 28)
    ks = 30 if story else 26
    _tracked_text(d, kicker, W / 2, y - ks / 2, ks, WHITE, spacing=7)


# ───────────────────────────── GAMEDAY ─────────────────────────────
def klasik_gameday(kategorie, souper, datum, cas, misto, out,
                   format="post", home=True, photo=None, titulek=None):
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img = _canvas(W, H, photo)
    _scrim(img, W, H, 0.38 if story else 0.34)
    _logo_tl(img, 210 if story else 190)
    d = ImageDraw.Draw(img)

    home_name = "KLASIK" if home else souper.upper()
    away_name = souper.upper() if home else "KLASIK"
    head = titulek or f"{home_name} – {away_name}"

    hsize = 92 if story else 78
    lines = _wrap_cond(d, head.upper(), hsize, W - 120)
    if len(lines) > 2:
        hsize = _fit_cond(d, max(lines, key=len), hsize, W - 120)
        lines = _wrap_cond(d, head.upper(), hsize, W - 120)

    info = "  ·  ".join(x for x in (datum, cas, misto) if x).upper()
    _bottom_block(img, d, W, H, f"{kategorie.upper()}  ·  GAMEDAY", lines, hsize,
                  extra=info, extra_size=26 if story else 23)
    img.save(out)
    return out


# ───────────────────────────── VÝSLEDEK ─────────────────────────────
def klasik_vysledek(kategorie, souper, skore_klasik, skore_souper, out,
                    format="post", home=True, photo=None, datum=None, misto=None,
                    poznamka=None):
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img = _canvas(W, H, photo)
    _scrim(img, W, H, 0.34 if story else 0.30)
    _logo_tl(img, 210 if story else 190)
    d = ImageDraw.Draw(img)

    home_name = "KLASIK" if home else souper.upper()
    away_name = souper.upper() if home else "KLASIK"
    left = skore_klasik if home else skore_souper
    right = skore_souper if home else skore_klasik

    hsize = 72 if story else 62
    lines = _wrap_cond(d, f"{home_name} – {away_name}", hsize, W - 120)
    if len(lines) > 2:
        hsize = _fit_cond(d, max(lines, key=len), hsize, W - 120)
        lines = _wrap_cond(d, f"{home_name} – {away_name}", hsize, W - 120)

    if skore_klasik > skore_souper:
        verdict = "VÝHRA"
    elif skore_klasik == skore_souper:
        verdict = "REMÍZA"
    else:
        verdict = "PROHRA"

    info = poznamka or "  ·  ".join(x for x in (datum, misto) if x).upper()
    _bottom_block(img, d, W, H, f"{kategorie.upper()}  ·  {verdict}", lines, hsize,
                  extra=info or None, extra_size=26 if story else 23,
                  score=f"{left} : {right}", score_size=150 if story else 126)
    img.save(out)
    return out


# ───────────────────────────── INFO ─────────────────────────────
def klasik_info(kicker, titulek, out, format="post", photo=None, podtitulek=None):
    """Obecný informační příspěvek: kicker, linka, velký titulek, web."""
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img = _canvas(W, H, photo)
    _scrim(img, W, H, 0.36 if story else 0.32)
    _logo_tl(img, 210 if story else 190)
    d = ImageDraw.Draw(img)

    head = titulek.upper()
    hsize = 92 if story else 78
    lines = _wrap_cond(d, head, hsize, W - 120)
    if len(lines) > 3:
        hsize = _fit_cond(d, max(lines, key=len), hsize, W - 120, min_size=44)
        lines = _wrap_cond(d, head, hsize, W - 120)

    _bottom_block(img, d, W, H, kicker.upper(), lines, hsize,
                  extra=(podtitulek.upper() if podtitulek else None),
                  extra_size=26 if story else 23)
    img.save(out)
    return out


# ───────────────────────────── ROZPIS ─────────────────────────────
def klasik_rozpis(nadpis, zapasy, out, format="post", photo=None):
    """zapasy: list (datum_cas, popis) — např. ("SO 12. 7. · 10:00", "U11 Klasik – Hroši")"""
    story = format == "story"
    W, H = (1080, 1920) if story else (1080, 1350)
    img = _canvas(W, H, photo)
    _scrim(img, W, H, 0.30, strength=246, veil=0.55)
    _logo_tl(img, 210 if story else 190)
    d = ImageDraw.Draw(img)

    web_y = H - (58 if story else 48)
    _tracked_text(d, WEB, W / 2, web_y, 21 if story else 19, WHITE, spacing=5)

    ky = 300 if story else 252
    _tracked_text(d, "ROZPIS ZÁPASŮ", W / 2, ky, 30 if story else 26, WHITE, spacing=7)

    hsize = _fit_cond(d, nadpis.upper(), 84 if story else 70, W - 140)
    hcy = ky + (52 if story else 46) + hsize * 0.5
    _cond_text(img, nadpis.upper(), W / 2, hcy, hsize, WHITE)

    ly = hcy + hsize * 0.72 + (40 if story else 34)
    d.rectangle([64, ly - 2, W - 64, ly + 2], fill=RED)

    row_h = 136 if story else 112
    gap = 18
    block_h = len(zapasy) * row_h + (len(zapasy) - 1) * gap
    space_top = ly + (56 if story else 46)
    space_bot = web_y - (60 if story else 48)
    y = space_top + max(0, (space_bot - space_top - block_h) / 2)

    r = 16
    for when, what in zapasy:
        d.rounded_rectangle([64, y, W - 64, y + row_h], radius=r, fill=(20, 13, 13))
        d.rounded_rectangle([64, y, 64 + 2 * r + 12, y + row_h], radius=r, fill=RED)
        d.rectangle([64 + 14, y, W - 64, y + row_h], fill=(20, 13, 13))
        cy = y + row_h / 2
        _tracked_left(d, when.upper(), 108, cy - (24 if story else 20),
                      24 if story else 21, SAND, spacing=3)
        ws = _fit_cond(d, what.upper(), 42 if story else 36, W - 300)
        _cond_text(img, what.upper(), 120 + (W - 184 - 56) / 2 - 20,
                   cy + (22 if story else 19), ws, WHITE)
        y += row_h + gap

    img.save(out)
    return out
