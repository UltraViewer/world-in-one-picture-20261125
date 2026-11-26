#!/usr/bin/env python3
"""Compose the front page for 25 November 2026.

Builds a 1024x1024 newspaper front page, "The World in One Picture",
from three editorial photographs and the verified headlines of the day.
Every figure on the page comes from the research brief; nothing is
invented, and no number is rendered in a background panel.

Run:  python3 compose.py            (writes entry.png next to this file)
      python3 compose.py --out DIR  (writes entry.png into DIR instead)

The output is deterministic: same inputs, same bytes, every run.
"""

import argparse
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 36
GUTTER = 20

PAPER = (247, 242, 231)      # warm newsprint cream
INK = (17, 17, 17)           # near-black
RED = (176, 30, 30)          # kicker red
GOLD = (232, 185, 60)        # markets label
STRIP = (13, 13, 13)         # black footer band
CAPTION_GREY = (90, 84, 72)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "panels")
HERO_PHOTO = os.path.join(
    PANELS, "media-generation-hero-wallstreet-0-501f8b8f-1e58-4e6f-b206-07ad6886e572.webp")
HORMUZ_PHOTO = os.path.join(
    PANELS, "media-generation-panel-hormuz-0-28457acc-41d5-4cdc-a266-12bebc6ec509.webp")
TIANGONG_PHOTO = os.path.join(
    PANELS, "media-generation-panel-tiangong-0-df287b4a-c511-4d0d-954d-6b7ac9618bfb.webp")


def load_font(path, size):
    return ImageFont.truetype(path, size)


def text_width(draw, text, font):
    return draw.textlength(text, font=font)


def shrink_to_fit(draw, text, font_path, start_size, max_width, min_size=10):
    """Largest font size at which `text` fits inside max_width."""
    size = start_size
    while size > min_size:
        font = load_font(font_path, size)
        if text_width(draw, text, font) <= max_width:
            return font
        size -= 1
    return load_font(font_path, min_size)


def wrap_words(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if text_width(draw, trial, font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, y, text, font, fill, width=PAGE_W):
    w = text_width(draw, text, font)
    draw.text(((width - w) / 2, y), text, font=font, fill=fill)
    return y + font.size


def draw_rule(draw, y, weight, x0=MARGIN, x1=PAGE_W - MARGIN):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=INK)


def cover_crop(photo, target_w, target_h):
    """Resize + centre-crop a photo so it exactly covers target_w x target_h."""
    img = Image.open(photo).convert("RGB")
    scale = max(target_w / img.width, target_h / img.height)
    new_w = max(target_w, int(img.width * scale + 0.5))
    new_h = max(target_h, int(img.height * scale + 0.5))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def draw_column(draw, page, x, width, y, kicker, headline, photo,
                body, img_h):
    """One story column: red kicker, bold headline, photo, serif body."""
    draw.text((x, y), kicker, font=load_font(SANS_BOLD, 17), fill=RED)
    y += 26
    head_font = shrink_to_fit(
        draw, headline, SANS_BOLD, 31, width)
    # Headline may need two lines: split on the natural break.
    lines = wrap_words(draw, headline, head_font, width)
    for line in lines:
        draw.text((x, y), line, font=head_font, fill=INK)
        y += 35
    y += 4
    page.paste(cover_crop(photo, width, img_h), (x, y))
    y += img_h + 10
    body_font = load_font(SERIF, 19)
    for line in wrap_words(draw, body, body_font, width):
        draw.text((x, y), line, font=body_font, fill=INK)
        y += 24
    return y


def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)
    content_w = PAGE_W - 2 * MARGIN

    # --- Masthead -------------------------------------------------------
    y = 16
    mast_font = shrink_to_fit(
        draw, "THE WORLD IN ONE PICTURE", SERIF_BOLD, 66, content_w)
    y = draw_centered(draw, y, "THE WORLD IN ONE PICTURE", mast_font, INK)
    y += 8
    draw_rule(draw, y, 2)
    y += 8

    # --- Dateline bar ---------------------------------------------------
    date_font = load_font(SANS_BOLD, 20)
    tag_font = load_font(SANS, 16)
    draw.text((MARGIN, y), "WEDNESDAY, 25 NOVEMBER 2026",
              font=date_font, fill=INK)
    tag = "ONE DAY  ·  ONE PICTURE  ·  THE WORLD"
    draw.text((PAGE_W - MARGIN - text_width(draw, tag, tag_font), y),
              tag, font=tag_font, fill=INK)
    y += 30
    draw_rule(draw, y, 5)
    y += 12

    # --- Hero headline --------------------------------------------------
    # Bigger first line so the headline owns the full column width.
    hero1 = shrink_to_fit(draw, "TARIFFS RETURN", SANS_BOLD, 108, content_w)
    draw.text((MARGIN, y), "TARIFFS RETURN", font=hero1, fill=INK)
    y += 96
    hero2 = shrink_to_fit(
        draw, "NVIDIA −3.9% AS WALL STREET SLIDES", SANS_BOLD, 46, content_w)
    draw.text((MARGIN, y), "NVIDIA −3.9% AS WALL STREET SLIDES",
              font=hero2, fill=INK)
    y += 52

    # --- Hero deck ------------------------------------------------------
    deck = ("Trump proposes tariffs of 20–40% on 14 trading partners, none "
            "in force before a 25 January hearing; Wall Street falls as "
            "October inflation runs at 3.8%.")
    deck_font = load_font(SERIF, 24)
    for line in wrap_words(draw, deck, deck_font, content_w):
        draw.text((MARGIN, y), line, font=deck_font, fill=INK)
        y += 30
    y += 8

    # --- Hero photograph + caption --------------------------------------
    hero_h = 196
    page.paste(cover_crop(HERO_PHOTO, content_w, hero_h), (MARGIN, y))
    y += hero_h + 8
    cap_font = load_font(SERIF_ITALIC, 17)
    draw.text((MARGIN, y),
              "Illustration: the New York Stock Exchange floor as Wall "
              "Street slid on Wednesday.",
              font=cap_font, fill=CAPTION_GREY)
    y += 30

    # --- Two story columns ----------------------------------------------
    col_w = (content_w - GUTTER) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + GUTTER
    draw_column(
        draw, page, left_x, col_w, y,
        "STRAIT OF HORMUZ",
        "TANKERS HIT BY MINES AND CATCH FIRE",
        HORMUZ_PHOTO,
        "Iran\u2019s Revolutionary Guard said tankers struck naval mines "
        "and caught fire in the Strait of Hormuz, claiming the vessels "
        "were on an unauthorised route.",
        148)
    draw_column(
        draw, page, right_x, col_w, y,
        "TIANGONG",
        "CHINA FLIES ITS FIRST FOREIGN ASTRONAUT",
        TIANGONG_PHOTO,
        "Shenzhou-24 docked at the Tiangong space station carrying "
        "Pakistan\u2019s Muhammad Zeeshan Ali \u2014 the first foreign "
        "astronaut aboard Tiangong.",
        148)

    # --- Black footer band: markets + briefs ----------------------------
    strip_top = 892
    draw.rectangle([0, strip_top, PAGE_W, PAGE_H], fill=STRIP)
    sy = strip_top + 10
    markets_font = load_font(SANS_BOLD, 22)
    label = "MARKETS  "
    label_w = text_width(draw, label, markets_font)
    draw.text((MARGIN, sy), label, font=markets_font, fill=GOLD)
    tickers = ("S&P 500 7,183  −0.25%   ·   Nasdaq 23,586  −0.62%   ·   "
               "NVDA $149.30  −3.91%   ·   PCE +3.8%")
    tick_font = shrink_to_fit(
        draw, tickers, SANS_BOLD, 22, content_w - label_w)
    draw.text((MARGIN + label_w, sy), tickers, font=tick_font, fill=(255, 255, 255))
    sy += 34
    briefs = ("HUAWEI — Guilty on 10 of 12 counts, sentencing Sept 2027 · "
              "HOUTHIS claim Ras Tanura refinery attack · CAIRO — Fuel fire "
              "kills at least 30 · NETANYAHU — Judges urge dropping top "
              "corruption case · SOLOMON ISLANDS signs Australia security "
              "treaty · BANGLADESH garment wage up 36% to ~$139 · SUDAN — "
              "RSF strikes kill 19 civilians")
    brief_font = load_font(SANS, 16)
    for line in wrap_words(draw, briefs, brief_font, content_w):
        draw.text((MARGIN, sy), line, font=brief_font, fill=(255, 255, 255))
        sy += 20

    return page


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=HERE,
                        help="directory to write entry.png into")
    args = parser.parse_args(argv)

    page = build_page()
    out_path = os.path.join(args.out, "entry.png")
    page.save(out_path, format="PNG")
    digest = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    size = os.path.getsize(out_path)
    print(f"wrote {out_path}  {size} bytes  sha256 {digest}")
    if size > 1024 * 1024:
        print("ERROR: entry.png exceeds the 1 MiB cap", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
