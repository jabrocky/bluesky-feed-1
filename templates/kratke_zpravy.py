#!/usr/bin/env python3
"""Šablona KRÁTKÉ ZPRÁVY pro IG stories (1080×1920) — Milujeme Baseball.

Vintage „stamp" styl odvozený z razítkového loga projektu: krémový papírový
podklad, rezavá červená, baseballové švy v rozích, ZPRÁVY jako otisk razítka.

Použití:
    python3 kratke_zpravy.py --topic "MLB · APPLE TV" \
        --headline "Friday Night Baseball se vrací!" \
        --text "Do nabídky Apple TV se vrací…" \
        [--date "19. 7."] [--out story.png]
"""
import argparse
import math
import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

CREAM = (240, 235, 224)
CREAM_DK = (228, 221, 206)
RUST = (154, 51, 36)        # rezavá z razítka
RUST_DARK = (118, 38, 26)
INK = (40, 34, 30)
INK_SOFT = (110, 100, 92)
WHITE = (252, 250, 246)

F_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


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


def draw_seam(base, cx, cy, R, a0, a1, color, stitch=36, gap_deg=6.0, width=6):
    """Baseballové stehy podél oblouku, vyhlazené supersamplingem."""
    ss = 3
    big = Image.new("RGBA", (base.size[0] * ss, base.size[1] * ss), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    a = a0
    while a < a1:
        rad = math.radians(a)
        px, py = (cx + R * math.cos(rad)) * ss, (cy + R * math.sin(rad)) * ss
        tx, ty = -math.sin(rad), math.cos(rad)
        nx, ny = math.cos(rad), math.sin(rad)
        for s in (-1, 1):
            x1 = px + s * tx * stitch * ss * 0.6
            y1 = py + s * ty * stitch * ss * 0.6
            x2 = px + nx * stitch * ss * 0.75
            y2 = py + ny * stitch * ss * 0.75
            bd.line([(x1, y1), (x2, y2)], fill=color, width=width * ss)
        a += gap_deg
    big = big.resize(base.size, Image.LANCZOS)
    base.paste(big, (0, 0), big)


def rotated_text(img, text, fnt, fill, cx, cy, angle, pad=30, box=None):
    tmp = Image.new("RGBA", (1400, 400), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(text, font=fnt)
    th = fnt.size
    x0, y0 = (tmp.size[0] - tw) / 2, (tmp.size[1] - th) / 2
    if box:
        bfill, boutl, bw, br = box
        td.rounded_rectangle(
            [x0 - pad, y0 - pad * 0.6, x0 + tw + pad, y0 + th + pad * 0.75],
            radius=br, fill=bfill, outline=boutl, width=bw)
    td.text((tmp.size[0] / 2, tmp.size[1] / 2), text, font=fnt, fill=fill, anchor="mm")
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
    img.paste(tmp, (int(cx - tmp.size[0] / 2), int(cy - tmp.size[1] / 2)), tmp)


def kratke_zpravy(topic, headline, text, out, date_label=None):
    logo_p = Image.open(os.path.join(ASSETS, "logo_project.png")).convert("RGBA")
    logo_s = Image.open(os.path.join(ASSETS, "logo_sponsor_nobg.png")).convert("RGBA")

    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(CREAM[i] + (CREAM_DK[i] - CREAM[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    seam_col = (198, 128, 112, 255)
    draw_seam(img, W + 260, -240, 640, 100, 168, seam_col)
    draw_seam(img, -260, H + 240, 640, 282, 350, seam_col)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 14], fill=RUST)
    d.rectangle([0, H - 14, W, H], fill=RUST)

    lh = 185
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, ((W - lp.size[0]) // 2, 50), lp)
    d = ImageDraw.Draw(img)

    d.text((W // 2, 330), "KRÁTKÉ", font=font(F_BOLD, 118), fill=INK, anchor="mm")
    rotated_text(img, "ZPRÁVY", font(F_BOLD, 118), CREAM, W // 2, 455, -2.5,
                 pad=38, box=(RUST, RUST_DARK, 5, 14))
    d = ImageDraw.Draw(img)

    d.line([(W // 2 - 260, 565), (W // 2 - 40, 565)], fill=RUST, width=4)
    d.line([(W // 2 + 40, 565), (W // 2 + 260, 565)], fill=RUST, width=4)
    d.ellipse([W // 2 - 22, 543, W // 2 + 22, 587], fill=WHITE, outline=RUST, width=4)
    d.arc([W // 2 - 34, 549, W // 2 - 2, 581], 300, 60, fill=RUST, width=3)
    d.arc([W // 2 + 2, 549, W // 2 + 34, 581], 120, 240, fill=RUST, width=3)

    tf = font(F_BOLD, 30)
    chips = [topic] + ([date_label] if date_label else [])
    total = sum(d.textlength(c, font=tf) + 76 for c in chips) + 20 * (len(chips) - 1)
    x = (W - total) / 2
    for c in chips:
        cw = d.textlength(c, font=tf)
        d.rounded_rectangle([x, 630, x + cw + 76, 695], radius=32, fill=INK)
        d.text((x + 38 + cw / 2, 662), c, font=tf, fill=CREAM, anchor="mm")
        x += cw + 76 + 20

    hf = font(F_BOLD, 58)
    hy = 800
    for ln in wrap(d, headline, hf, W - 200):
        d.text((W // 2, hy), ln, font=hf, fill=RUST_DARK, anchor="mm")
        hy += 72

    bf = font(F_REG, 35)
    lines = wrap(d, text, bf, W - 260)
    line_h = 54
    card_top = hy + 40
    card_bot = card_top + len(lines) * line_h + 80
    d.rounded_rectangle([80, card_top, W - 80, card_bot], radius=22,
                        fill=WHITE, outline=(205, 195, 180), width=2)
    d.rounded_rectangle([80, card_top, 104, card_bot], radius=11, fill=RUST)
    ty = card_top + 50
    for ln in lines:
        d.text((130, ty), ln, font=bf, fill=INK, anchor="lm")
        ty += line_h

    d.text((W // 2, H - 235), "PARTNER", font=font(F_BOLD, 22), fill=INK_SOFT, anchor="mm")
    sh = 80
    ls = logo_s.copy()
    s = sh / ls.size[1]
    ls = ls.resize((int(ls.size[0] * s), sh), Image.LANCZOS)
    img.paste(ls, ((W - ls.size[0]) // 2, H - 210), ls)
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 70),
           "milujeme-baseball.cz  ·  #MilujemeBaseball  #BaseballCzechia",
           font=font(F_REG, 27), fill=INK_SOFT, anchor="mm")
    img.save(out)
    return out





def kratke_zpravy_fb(topic, headline, text, out, photo=None, photo_credit=None):
    """FB varianta 4:5 (1080×1350): kompaktní hlavička, foto slot, text karta."""
    logo_p = Image.open(os.path.join(ASSETS, "logo_project.png")).convert("RGBA")
    logo_s = Image.open(os.path.join(ASSETS, "logo_sponsor_nobg.png")).convert("RGBA")

    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(CREAM[i] + (CREAM_DK[i] - CREAM[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    seam_col = (198, 128, 112, 255)
    draw_seam(img, W + 260, -240, 600, 100, 168, seam_col)
    draw_seam(img, -260, H + 240, 600, 282, 350, seam_col)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 12], fill=RUST)
    d.rectangle([0, H - 12, W, H], fill=RUST)

    lh = 150
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, (90, 42), lp)
    d = ImageDraw.Draw(img)
    d.text((280, 85), "KRÁTKÉ", font=font(F_BOLD, 74), fill=INK, anchor="lm")
    rotated_text(img, "ZPRÁVY", font(F_BOLD, 74), CREAM, 505, 160, -2.0,
                 pad=26, box=(RUST, RUST_DARK, 4, 10))
    d = ImageDraw.Draw(img)

    tf = font(F_BOLD, 26)
    cw = d.textlength(topic, font=tf)
    d.rounded_rectangle([W - 90 - cw - 64, 70, W - 90, 126], radius=28, fill=INK)
    d.text((W - 90 - 32 - cw / 2, 98), topic, font=tf, fill=CREAM, anchor="mm")

    hf = font(F_BOLD, 50)
    hy = 280
    for ln in wrap(d, headline, hf, W - 180):
        d.text((W // 2, hy), ln, font=hf, fill=RUST_DARK, anchor="mm")
        hy += 62

    # výška fota se přizpůsobí délce textu, aby karta nekolidovala s patičkou
    bf = font(F_REG, 30)
    lines = wrap(d, text, bf, W - 250)
    line_h = 46
    card_h = len(lines) * line_h + 60
    footer_top = H - 150
    ph_top = hy + 25
    ph_bot = footer_top - card_h - 30
    if ph_bot - ph_top < 260:
        ph_bot = ph_top + 260  # minimální výška fota; delší text raději zkrátit

    if photo:
        pimg = Image.open(photo).convert("RGB")
        bw, bh = W - 160, ph_bot - ph_top
        pw, ph_ = pimg.size
        sc = max(bw / pw, bh / ph_)
        nw, nh = int(pw * sc) + 1, int(ph_ * sc) + 1
        rs = pimg.resize((nw, nh), Image.LANCZOS)
        x = (nw - bw) // 2
        y = int((nh - bh) * 0.3)
        crop = rs.crop((x, y, x + bw, y + bh))
        mask = Image.new("L", (bw, bh), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=20, fill=255)
        img.paste(crop, (80, ph_top), mask)
        d.rounded_rectangle([80, ph_top, W - 80, ph_bot], radius=20, outline=RUST, width=4)
        if photo_credit:
            d.text((W - 95, ph_bot - 24), photo_credit,
                   font=font(F_REG, 18), fill=(240, 240, 240), anchor="rm")
    else:
        d.rounded_rectangle([80, ph_top, W - 80, ph_bot], radius=20,
                            fill=(225, 218, 203), outline=(200, 190, 175), width=2)
        d.text((W // 2, (ph_top + ph_bot) // 2), "FOTO",
               font=font(F_BOLD, 44), fill=(180, 170, 155), anchor="mm")

    card_top = ph_bot + 30
    card_bot = card_top + card_h
    d.rounded_rectangle([80, card_top, W - 80, card_bot], radius=20,
                        fill=WHITE, outline=(205, 195, 180), width=2)
    d.rounded_rectangle([80, card_top, 102, card_bot], radius=10, fill=RUST)
    ty = card_top + 38
    for ln in lines:
        d.text((126, ty), ln, font=bf, fill=INK, anchor="lm")
        ty += line_h

    sh = 58
    ls = logo_s.copy()
    s = sh / ls.size[1]
    ls = ls.resize((int(ls.size[0] * s), sh), Image.LANCZOS)
    d.text((W // 2, H - 118), "PARTNER", font=font(F_BOLD, 19), fill=INK_SOFT, anchor="mm")
    img.paste(ls, ((W - ls.size[0]) // 2, H - 100), ls)
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 32),
           "milujeme-baseball.cz  ·  #MilujemeBaseball  #BaseballCzechia",
           font=font(F_REG, 23), fill=INK_SOFT, anchor="mm")
    img.save(out)
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True, help='např. "MLB · APPLE TV"')
    p.add_argument("--headline", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--date", default=None, help='volitelný druhý chip, např. "19. 7."')
    p.add_argument("--out", default="kratke_zpravy.png")
    p.add_argument("--fb", action="store_true", help="FB varianta 4:5 s foto slotem")
    p.add_argument("--photo", default=None, help="cesta k fotce (jen --fb)")
    p.add_argument("--photo-credit", default=None, help="credit fotky (jen --fb)")
    a = p.parse_args()
    if a.fb:
        print(kratke_zpravy_fb(a.topic, a.headline, a.text, a.out,
                               photo=a.photo, photo_credit=a.photo_credit))
    else:
        print(kratke_zpravy(a.topic, a.headline, a.text, a.out, a.date))


def aktualita(topic, headline, intro, sections, out, photo=None, photo_credit=None):
    """Varianta AKTUALITA (story 1080×1920): velká zpráva s fotkou a výsledky.

    sections: list [(label, [(soupeř, skóre), …]), …]; poslední řádek poslední
    sekce se zvýrazní rezavou (typicky finále).
    """
    logo_p = Image.open(os.path.join(ASSETS, "logo_project.png")).convert("RGBA")
    logo_s = Image.open(os.path.join(ASSETS, "logo_sponsor_nobg.png")).convert("RGBA")

    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(CREAM[i] + (CREAM_DK[i] - CREAM[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    seam_col = (198, 128, 112, 255)
    draw_seam(img, W + 260, -240, 640, 100, 168, seam_col)
    draw_seam(img, -260, H + 240, 640, 282, 350, seam_col)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=RUST)
    d.rectangle([0, H - 14, W, H], fill=RUST)

    lh = 150
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, ((W - lp.size[0]) // 2, 42), lp)
    d = ImageDraw.Draw(img)

    rotated_text(img, "AKTUALITA", font(F_BOLD, 96), CREAM, W // 2, 280, -2.0,
                 pad=34, box=(RUST, RUST_DARK, 5, 12))
    d = ImageDraw.Draw(img)

    tf = font(F_BOLD, 28)
    cw = d.textlength(topic, font=tf)
    d.rounded_rectangle([W / 2 - cw / 2 - 34, 375, W / 2 + cw / 2 + 34, 437],
                        radius=31, fill=INK)
    d.text((W // 2, 406), topic, font=tf, fill=CREAM, anchor="mm")

    hf = font(F_BOLD, 52)
    hy = 510
    for ln in wrap(d, headline, hf, W - 160):
        d.text((W // 2, hy), ln, font=hf, fill=RUST_DARK, anchor="mm")
        hy += 64

    # výška fotky se dopočítá tak, aby se vešel úvod, výsledky i patička
    bf = font(F_REG, 31)
    intro_lines = wrap(d, intro, bf, W - 250)
    line_h = 46
    intro_h = len(intro_lines) * line_h + 52
    results_h = 40
    for _label, _games in sections:
        results_h += 42 + len(_games) * 48
    footer_top = H - 215
    ph_top = hy + 25
    photo_h = footer_top - ph_top - 28 - intro_h - 26 - results_h
    photo_h = max(260, min(430, photo_h))
    ph_bot = ph_top + photo_h
    if photo:
        pimg = Image.open(photo).convert("RGB")
        bw, bh = W - 160, ph_bot - ph_top
        pw, ph_ = pimg.size
        sc = max(bw / pw, bh / ph_)
        nw, nh = int(pw * sc) + 1, int(ph_ * sc) + 1
        rs = pimg.resize((nw, nh), Image.LANCZOS)
        x = (nw - bw) // 2
        y = int((nh - bh) * 0.45)
        crop = rs.crop((x, y, x + bw, y + bh))
        mask = Image.new("L", (bw, bh), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=20, fill=255)
        img.paste(crop, (80, ph_top), mask)
        d.rounded_rectangle([80, ph_top, W - 80, ph_bot], radius=20, outline=RUST, width=4)
        if photo_credit:
            d.text((W - 95, ph_bot - 24), photo_credit,
                   font=font(F_REG, 18), fill=(240, 240, 240), anchor="rm")
        y_cursor = ph_bot
    else:
        y_cursor = hy - 10

    # úvodní text
    lines = intro_lines
    card_top = y_cursor + 28
    card_bot = card_top + len(lines) * line_h + 52
    d.rounded_rectangle([80, card_top, W - 80, card_bot], radius=20,
                        fill=WHITE, outline=(205, 195, 180), width=2)
    d.rounded_rectangle([80, card_top, 102, card_bot], radius=10, fill=RUST)
    ty = card_top + 34
    for ln in lines:
        d.text((126, ty), ln, font=bf, fill=INK, anchor="lm")
        ty += line_h

    # výsledky
    lbl_f = font(F_BOLD, 24)
    row_f = font(F_REG, 32)
    row_fb = font(F_BOLD, 34)
    res_top = card_bot + 26
    ry = res_top + 28
    res_bot = res_top + results_h
    d.rounded_rectangle([80, res_top, W - 80, res_bot], radius=20,
                        fill=WHITE, outline=(205, 195, 180), width=2)
    last_section = len(sections) - 1
    for si, (label, games) in enumerate(sections):
        d.text((130, ry), label, font=lbl_f, fill=RUST, anchor="lm")
        ry += 42
        for gi, (opp, score) in enumerate(games):
            highlight = (si == last_section and gi == len(games) - 1)
            if highlight:
                d.rounded_rectangle([110, ry - 22, W - 110, ry + 26],
                                    radius=12, fill=RUST)
                d.text((130, ry), f"Česko – {opp}", font=row_fb, fill=CREAM, anchor="lm")
                d.text((W - 135, ry), score, font=row_fb, fill=CREAM, anchor="rm")
            else:
                d.text((130, ry), f"Česko – {opp}", font=row_f, fill=INK, anchor="lm")
                d.text((W - 135, ry), score, font=row_fb, fill=RUST_DARK, anchor="rm")
            ry += 48

    # patička
    d.text((W // 2, H - 195), "PARTNER", font=font(F_BOLD, 20), fill=INK_SOFT, anchor="mm")
    sh = 66
    ls = logo_s.copy()
    s = sh / ls.size[1]
    ls = ls.resize((int(ls.size[0] * s), sh), Image.LANCZOS)
    img.paste(ls, ((W - ls.size[0]) // 2, H - 175), ls)
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 60),
           "milujeme-baseball.cz  ·  #MilujemeBaseball  #BaseballCzechia",
           font=font(F_REG, 26), fill=INK_SOFT, anchor="mm")
    img.save(out)
    return out
