#!/usr/bin/env python3
"""Compose the 25 Nov 2026 front page: 'The World in One Picture'.

Draws the newspaper front page with PIL from three editorial panels in
./panels/ plus the verified headlines for Wednesday 25 November 2026.
Writes entry.png (1024x1024, <=1 MiB). No network, no randomness: the same
inputs always produce the same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (250, 246, 238)
INK = (17, 17, 17)
BODY = (34, 34, 34)
GREY = (84, 84, 84)
RED = (155, 28, 28)
GOLD = (255, 196, 66)
STRIP_BG = (16, 16, 16)
STRIP_FG = (232, 232, 232)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

HERO_PANEL = "media-generation-hero-wallstreet-0-501f8b8f-1e58-4e6f-b206-07ad6886e572.webp"
HORMUZ_PANEL = "media-generation-panel-hormuz-0-28457acc-41d5-4cdc-a266-12bebc6ec509.webp"
TIANGONG_PANEL = "media-generation-panel-tiangong-0-df287b4a-c511-4d0d-954d-6b7ac9618bfb.webp"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def width(draw, text, font):
    return draw.textlength(text, font=font)


def wrap_text(draw, text, font, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if width(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, path, start, floor, max_w):
    """Largest size in [floor, start] whose text fits max_w."""
    size = start
    while size > floor and width(draw, text, fnt(path, size)) > max_w:
        size -= 2
    return size


def crop_fill(im, tw, th, focus=0.5):
    """Scale and center-crop (vertical focus 0..1) to the target size."""
    iw, ih = im.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(round(iw * scale)), int(round(ih * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - tw) // 2
    y0 = int(round((nh - th) * focus))
    return im.crop((x0, y0, x0 + tw, y0 + th))


def rule(draw, y, x0, x1, thick, fill=INK):
    draw.rectangle([x0, y, x1, y + thick - 1], fill=fill)


def build():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    y = 22
    # --- masthead ---
    d.text((W // 2, y), "THE WORLD IN ONE PICTURE",
           font=fnt(SERIF_B, 56), fill=INK, anchor="mt")
    y += 62
    rule(d, y, MARGIN, W - MARGIN, 2)
    y += 8
    # --- dateline ---
    d.text((MARGIN, y), "WEDNESDAY, 25 NOVEMBER 2026",
           font=fnt(SANS_B, 20), fill=INK)
    d.text((W - MARGIN, y), "ONE DAY  \u00b7  ONE PICTURE  \u00b7  THE WORLD",
           font=fnt(SANS, 17), fill=GREY, anchor="ra")
    y += 27
    rule(d, y, MARGIN, W - MARGIN, 4)
    y += 12

    # --- hero headline ---
    hl1 = "TARIFFS RETURN"
    s1 = fit(d, hl1, SANS_B, 96, 72, CW)
    d.text((MARGIN, y), hl1, font=fnt(SANS_B, s1), fill=INK)
    y += s1 + 4
    hl2 = "NVIDIA \u22123.9% AS WALL STREET SLIDES"
    s2 = fit(d, hl2, SANS_B, 46, 34, CW)
    d.text((MARGIN, y), hl2, font=fnt(SANS_B, s2), fill=INK)
    y += s2 + 8
    # --- deck ---
    deck = ("Trump proposes tariffs of 20\u201340% on 14 trading partners, "
            "none in force before a 25 January hearing; Wall Street falls "
            "as October inflation runs at 3.8%.")
    f_deck = fnt(SERIF, 23)
    for line in wrap_text(d, deck, f_deck, CW):
        d.text((MARGIN, y), line, font=f_deck, fill=BODY)
        y += 29
    y += 8

    # --- hero photo + caption ---
    hero = Image.open(os.path.join(HERE, "panels", HERO_PANEL)).convert("RGB")
    page.paste(crop_fill(hero, CW, 202, focus=0.55), (MARGIN, y))
    y += 202 + 5
    d.text((MARGIN, y),
           "Illustration: the New York Stock Exchange floor as Wall Street "
           "slid on Wednesday.",
           font=fnt(SERIF_I, 16), fill=GREY)
    y += 24
    y += 6

    # --- two story columns ---
    col_w = (CW - 20) // 2  # 466
    stories = [
        ("STRAIT OF HORMUZ",
         "TANKERS HIT BY MINES AND CATCH FIRE",
         HORMUZ_PANEL,
         "Iran\u2019s Revolutionary Guard said tankers struck naval mines "
         "and caught fire in the Strait of Hormuz, claiming the vessels "
         "were on an unauthorised route."),
        ("TIANGONG",
         "CHINA FLIES ITS FIRST FOREIGN ASTRONAUT",
         TIANGONG_PANEL,
         "Shenzhou-24 docked at the Tiangong space station carrying "
         "Pakistan\u2019s Muhammad Zeeshan Ali \u2014 the first foreign "
         "astronaut aboard Tiangong."),
    ]
    col_top = y
    col_bottom = col_top
    for i, (kicker, headline, panel, body) in enumerate(stories):
        x = MARGIN + i * (col_w + 20)
        cy = col_top
        d.text((x, cy), kicker, font=fnt(SANS_B, 18), fill=RED)
        cy += 23
        for line in wrap_text(d, headline, fnt(SANS_B, 29), col_w):
            d.text((x, cy), line, font=fnt(SANS_B, 29), fill=INK)
            cy += 33
        cy += 4
        im = Image.open(os.path.join(HERE, "panels", panel)).convert("RGB")
        page.paste(crop_fill(im, col_w, 122, focus=0.5), (x, cy))
        cy += 122 + 6
        for line in wrap_text(d, body, fnt(SERIF, 18), col_w):
            d.text((x, cy), line, font=fnt(SERIF, 18), fill=BODY)
            cy += 21
        col_bottom = max(col_bottom, cy)
    y = col_bottom + 10

    # --- dark strip: markets + briefs ---
    strip_top = y
    strip_h = H - 24 - strip_top
    assert strip_h >= 110, f"strip too short: {strip_h}px"
    d.rectangle([0, strip_top, W, H - 24], fill=STRIP_BG)
    sy = strip_top + 13
    d.text((MARGIN, sy), "MARKETS", font=fnt(SANS_B, 23), fill=GOLD)
    mkt = ("S&P 500 7,183 \u22120.25%   \u00b7   Nasdaq 23,586 \u22120.62%   "
           "\u00b7   NVDA $149.30 \u22123.91%   \u00b7   PCE +3.8%")
    mkt_size = fit(d, mkt, SANS_B, 23, 16, CW - 132)
    d.text((MARGIN + 132, sy), mkt, font=fnt(SANS_B, mkt_size),
           fill=(255, 255, 255))
    sy += 34
    briefs = ("HUAWEI \u2014 Guilty on 10 of 12 counts, sentencing Sept 2027  "
              "\u00b7  HOUTHIS claim Ras Tanura refinery attack  \u00b7  "
              "CAIRO \u2014 Fuel fire kills at least 30  \u00b7  "
              "NETANYAHU \u2014 Judges urge dropping top corruption case  "
              "\u00b7  SOLOMON ISLANDS signs Australia security treaty  "
              "\u00b7  BANGLADESH garment wage up 36% to ~$139  \u00b7  "
              "SUDAN \u2014 RSF strikes kill 19 civilians")
    f_brief = fnt(SANS, 16)
    for line in wrap_text(d, briefs, f_brief, CW):
        d.text((MARGIN, sy), line, font=f_brief, fill=STRIP_FG)
        sy += 20
    assert sy <= H - 24, f"briefs overflow: ends at {sy}px"

    out = os.path.join(HERE, "entry.png")
    page.save(out, format="PNG")
    print(f"wrote {out}  strip_top={strip_top} strip_h={strip_h} "
          f"briefs_end={sy}")


if __name__ == "__main__":
    build()
