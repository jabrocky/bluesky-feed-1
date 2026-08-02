#!/usr/bin/env python3
"""Sada grafik k ROZHOVORU — Milujeme Baseball.

Stejný vintage „stamp" styl jako Krátké zprávy / Aktuality:
krémový papír, rezavá červená, baseballové švy, nakloněné razítko.

Vyrábí:
  • cover story 9:16      (rozhovor_cover_story)
  • Q&A story 9:16        (rozhovor_qa_story)
  • carousel slide 4:5    (rozhovor_cover_post, rozhovor_qa_post, rozhovor_cta_post)
"""
import os

from PIL import Image, ImageDraw, ImageFont

from kratke_zpravy import (ASSETS, CREAM, CREAM_DK, RUST, RUST_DARK, INK,
                           INK_SOFT, WHITE, F_BOLD, F_REG, font, wrap,
                           draw_seam, rotated_text)

F_BI = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
SEAM = (198, 128, 112, 255)


def _base(W, H):
    logo_p = Image.open(os.path.join(ASSETS, "logo_project.png")).convert("RGBA")
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(CREAM[i] + (CREAM_DK[i] - CREAM[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    story = H > 1500
    draw_seam(img, W + 260, -240, 640 if story else 600, 100, 168, SEAM)
    draw_seam(img, -260, H + 240, 640 if story else 600, 282, 350, SEAM)
    d = ImageDraw.Draw(img)
    bar = 14 if story else 12
    d.rectangle([0, 0, W, bar], fill=RUST)
    d.rectangle([0, H - bar, W, H], fill=RUST)
    return img, d, logo_p


def _footer(img, d, W, H, story, partner=True):
    logo_s = Image.open(os.path.join(ASSETS, "logo_sponsor_nobg.png")).convert("RGBA")
    if partner:
        d.text((W // 2, H - (195 if story else 118)), "PARTNER",
               font=font(F_BOLD, 20 if story else 19), fill=INK_SOFT, anchor="mm")
        sh = 66 if story else 56
        ls = logo_s.copy()
        s = sh / ls.size[1]
        ls = ls.resize((int(ls.size[0] * s), sh), Image.LANCZOS)
        img.paste(ls, ((W - ls.size[0]) // 2, H - (175 if story else 100)), ls)
        d = ImageDraw.Draw(img)
    d.text((W // 2, H - (60 if story else 32)),
           "milujeme-baseball.cz  ·  #MilujemeBaseball  #BaseballCzechia",
           font=font(F_REG, 26 if story else 23), fill=INK_SOFT, anchor="mm")


def _chips(d, W, items, cy, size, right_x=None):
    """Vrátí celkovou šířku. right_x = zarovnat doprava k této hraně."""
    if not items:
        return 0
    f = font(F_BOLD, size)
    ws = [d.textlength(t, font=f) + 64 for t in items]
    gap, h = 16, size * 2.1
    total = sum(ws) + gap * (len(ws) - 1)
    x = (right_x - total) if right_x else (W - total) / 2
    for t, w in zip(items, ws):
        d.rounded_rectangle([x, cy - h / 2, x + w, cy + h / 2], radius=h / 2, fill=INK)
        d.text((x + w / 2, cy), t, font=f, fill=CREAM, anchor="mm")
        x += w + gap
    return total


def _photo(img, d, box, path, credit=None):
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    if path:
        p = Image.open(path).convert("RGB")
        sc = max(bw / p.size[0], bh / p.size[1])
        nw, nh = int(p.size[0] * sc) + 1, int(p.size[1] * sc) + 1
        rs = p.resize((nw, nh), Image.LANCZOS)
        cx = (nw - bw) // 2
        cy = int((nh - bh) * 0.35)
        crop = rs.crop((cx, cy, cx + bw, cy + bh))
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=20, fill=255)
        img.paste(crop, (x1, y1), mask)
    else:
        d.rounded_rectangle(box, radius=20, fill=(225, 218, 203),
                            outline=(200, 190, 175), width=2)
        d.text(((x1 + x2) // 2, (y1 + y2) // 2), "FOTO",
               font=font(F_BOLD, 46), fill=(180, 170, 155), anchor="mm")
    d.rounded_rectangle(box, radius=20, outline=RUST, width=4)
    if credit and path:
        d.text((x2 - 16, y2 - 24), credit, font=font(F_REG, 18),
               fill=(245, 245, 245), anchor="rm")


def _quote_card(d, W, top, lines, fnt, line_h):
    h = len(lines) * line_h + 50
    d.rounded_rectangle([80, top, W - 80, top + h], radius=20,
                        fill=WHITE, outline=(205, 195, 180), width=2)
    d.rounded_rectangle([80, top, 102, top + h], radius=10, fill=RUST)
    y = top + 34
    for ln in lines:
        d.text((126, y), ln, font=fnt, fill=INK, anchor="lm")
        y += line_h
    return h


# ───────────────────────── STORY ─────────────────────────
def rozhovor_cover_story(chips, headline, name, role, quote, out,
                         photo=None, credit=None):
    W, H = 1080, 1920
    img, d, logo_p = _base(W, H)
    lh = 150
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, ((W - lp.size[0]) // 2, 42), lp)
    d = ImageDraw.Draw(img)

    rotated_text(img, "ROZHOVOR", font(F_BOLD, 96), CREAM, W // 2, 280, -2.0,
                 pad=34, box=(RUST, RUST_DARK, 5, 12))
    d = ImageDraw.Draw(img)
    _chips(d, W, chips, 406, 28)

    hf = font(F_BOLD, 52)
    hy = 500
    for ln in wrap(d, headline, hf, W - 170):
        d.text((W // 2, hy), ln, font=hf, fill=RUST_DARK, anchor="mm")
        hy += 64

    qf = font(F_BI, 38)
    qlines = wrap(d, quote, qf, W - 250)
    quote_h = len(qlines) * 52 + 50
    name_block = 120
    ph_top = hy + 20
    ph_bot = (H - 240) - quote_h - name_block - 40
    ph_bot = max(ph_top + 300, min(ph_top + 700, ph_bot))
    _photo(img, d, (80, ph_top, W - 80, ph_bot), photo, credit)

    d.text((W // 2, ph_bot + 52), name, font=font(F_BOLD, 54), fill=RUST_DARK, anchor="mm")
    d.text((W // 2, ph_bot + 100), role, font=font(F_REG, 30), fill=INK_SOFT, anchor="mm")

    _quote_card(d, W, ph_bot + name_block + 20, qlines, qf, 52)
    _footer(img, d, W, H, True)
    img.save(out)
    return out


def rozhovor_qa_story(name, question, quote, idx, total, out):
    W, H = 1080, 1920
    img, d, logo_p = _base(W, H)
    lh = 150
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, ((W - lp.size[0]) // 2, 42), lp)
    d = ImageDraw.Draw(img)

    rotated_text(img, "ROZHOVOR", font(F_BOLD, 90), CREAM, W // 2, 275, -2.0,
                 pad=32, box=(RUST, RUST_DARK, 5, 12))
    d = ImageDraw.Draw(img)
    _chips(d, W, [name.upper()], 398, 26)

    # postup
    sp, r = 40, 9
    x0 = W / 2 - (total - 1) * sp / 2
    for i in range(total):
        col = RUST if i == idx else (206, 196, 182)
        d.ellipse([x0 + i * sp - r, 470 - r, x0 + i * sp + r, 470 + r], fill=col)

    qf = font(F_BOLD, 38)
    qlines = wrap(d, question, qf, W - 200)
    bf = font(F_BI, 54)
    blines = wrap(d, quote, bf, W - 210)

    block = len(qlines) * 50 + 70 + 100 + len(blines) * 74 + 90
    y = 560 + ((H - 300) - 560 - block) // 2

    for ln in qlines:
        d.text((W // 2, y), ln, font=qf, fill=RUST, anchor="mm")
        y += 50
    y += 24
    d.line([(W / 2 - 80, y), (W / 2 + 80, y)], fill=RUST, width=4)
    y += 70
    d.text((W // 2, y), "„", font=font(F_BOLD, 140), fill=RUST, anchor="mm")
    y += 100
    for ln in blines:
        d.text((W // 2, y), ln, font=bf, fill=INK, anchor="mm")
        y += 74
    y += 60
    d.text((W // 2, y), f"— {name}", font=font(F_REG, 32), fill=INK_SOFT, anchor="mm")

    _footer(img, d, W, H, True)
    img.save(out)
    return out


# ───────────────────────── CAROUSEL 4:5 ─────────────────────────
def _post_header(img, d, stamp_text, chips, slide_no, total):
    W = 1080
    logo_p = Image.open(os.path.join(ASSETS, "logo_project.png")).convert("RGBA")
    lh = 130
    lp = logo_p.copy()
    s = lh / lp.size[1]
    lp = lp.resize((int(lp.size[0] * s), lh), Image.LANCZOS)
    img.paste(lp, (85, 38), lp)
    d = ImageDraw.Draw(img)
    rotated_text(img, stamp_text, font(F_BOLD, 58), CREAM, 520, 100, -2.0,
                 pad=22, box=(RUST, RUST_DARK, 4, 10))
    d = ImageDraw.Draw(img)
    d.text((W - 85, 100), f"{slide_no}/{total}", font=font(F_BOLD, 30),
           fill=INK_SOFT, anchor="rm")
    if chips:
        _chips(d, W, chips, 190, 24, right_x=W - 85)
    return d


def rozhovor_cover_post(chips, headline, name, role, quote, out, total,
                        photo=None, credit=None):
    W, H = 1080, 1350
    img, d, _ = _base(W, H)
    d = _post_header(img, d, "ROZHOVOR", chips, 1, total)

    hf = font(F_BOLD, 46)
    hy = 275
    for ln in wrap(d, headline, hf, W - 170):
        d.text((85, hy), ln, font=hf, fill=RUST_DARK, anchor="lm")
        hy += 56

    qf = font(F_BI, 34)
    qlines = wrap(d, quote, qf, W - 250)
    quote_h = len(qlines) * 46 + 50
    ph_top = hy + 15
    ph_bot = (H - 150) - quote_h - 110
    ph_bot = max(ph_top + 260, min(ph_top + 460, ph_bot))
    _photo(img, d, (80, ph_top, W - 80, ph_bot), photo, credit)

    d.text((85, ph_bot + 46), name, font=font(F_BOLD, 44), fill=RUST_DARK, anchor="lm")
    d.text((85, ph_bot + 88), role, font=font(F_REG, 26), fill=INK_SOFT, anchor="lm")
    _quote_card(d, W, ph_bot + 116, qlines, qf, 46)
    _footer(img, d, W, H, False)
    img.save(out)
    return out


def rozhovor_qa_post(name, question, quote, slide_no, total, out):
    W, H = 1080, 1350
    img, d, _ = _base(W, H)
    d = _post_header(img, d, "ROZHOVOR", [name.upper()], slide_no, total)

    qf = font(F_BOLD, 36)
    qlines = wrap(d, question, qf, W - 180)
    bf = font(F_BI, 48)
    blines = wrap(d, quote, bf, W - 190)

    block = len(qlines) * 48 + 62 + 90 + len(blines) * 64 + 80
    y = 300 + ((H - 200) - 300 - block) // 2

    for ln in qlines:
        d.text((W // 2, y), ln, font=qf, fill=RUST, anchor="mm")
        y += 48
    y += 20
    d.line([(W / 2 - 80, y), (W / 2 + 80, y)], fill=RUST, width=4)
    y += 62
    d.text((W // 2, y), "„", font=font(F_BOLD, 120), fill=RUST, anchor="mm")
    y += 90
    for ln in blines:
        d.text((W // 2, y), ln, font=bf, fill=INK, anchor="mm")
        y += 64
    y += 52
    d.text((W // 2, y), f"— {name}", font=font(F_REG, 30), fill=INK_SOFT, anchor="mm")

    _footer(img, d, W, H, False)
    img.save(out)
    return out


def rozhovor_cta_post(bullets, out, total, photo=None, credit=None):
    W, H = 1080, 1350
    img, d, _ = _base(W, H)
    d = _post_header(img, d, "ROZHOVOR", [], total, total)

    ph_top, ph_bot = 210, 610
    _photo(img, d, (80, ph_top, W - 80, ph_bot), photo, credit)

    d.text((W // 2, 690), "CELÝ ROZHOVOR", font=font(F_BOLD, 68), fill=RUST_DARK, anchor="mm")
    d.text((W // 2, 752), "najdeš na", font=font(F_REG, 34), fill=INK_SOFT, anchor="mm")

    wf = font(F_BOLD, 50)
    wt = "milujeme-baseball.cz"
    ww = d.textlength(wt, font=wf)
    d.rounded_rectangle([W / 2 - ww / 2 - 44, 800, W / 2 + ww / 2 + 44, 892],
                        radius=46, fill=RUST)
    d.text((W // 2, 846), wt, font=wf, fill=CREAM, anchor="mm")

    y = 960
    for b in bullets:
        d.text((W // 2, y), b, font=font(F_REG, 29), fill=INK, anchor="mm")
        y += 46

    _footer(img, d, W, H, False)
    img.save(out)
    return out
