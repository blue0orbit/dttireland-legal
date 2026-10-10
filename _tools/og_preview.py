"""Draws assets/img/og-preview.png, the 1200x630 card shown when a dttireland.com page is shared.

    python _tools/og_preview.py        (needs Pillow, fontTools and brotli)

Everything in it is ours: the site's check-mark logo (favicon.svg), the site's colours and its own
self-hosted Inter (SIL OFL 1.1, assets/fonts/inter/OFL.txt). No photo, screenshot, app icon or
AI picture is used. Folders starting with "_" are not published by GitHub Pages.
"""
import io
import os

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets", "img", "og-preview.png")
W, H, S = 1200, 630, 2  # drawn at 2x, then reduced for smooth edges

FOREST, INK, MINT, MUTED, LOGO = "#123d2f", "#0e3125", "#8fe3b0", "#bdcfc2", "#087443"


def inter(size, weight):
    """Inter from the site's own latin woff2, at a weight of its variable axis."""
    font = TTFont(os.path.join(SITE, "assets", "fonts", "inter", "inter-latin.woff2"))
    font.flavor = None
    data = io.BytesIO()
    font.save(data)
    data.seek(0)
    face = ImageFont.truetype(data, size * S)
    face.set_variation_by_axes([weight])
    return face


def main():
    img = Image.new("RGB", (W * S, H * S), FOREST)
    d = ImageDraw.Draw(img)
    # a quiet road-like curve across the background
    d.ellipse((560 * S, 250 * S, 1700 * S, 1400 * S), fill=INK)
    d.ellipse((640 * S, 330 * S, 1620 * S, 1320 * S), fill=FOREST)

    # logo: the favicon's green disc and white tick
    x, y, r = 80 * S, 72 * S, 34 * S
    d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=LOGO)
    tick = [(x + 0.27 * 2 * r, y + 0.51 * 2 * r), (x + 0.43 * 2 * r, y + 0.67 * 2 * r), (x + 0.74 * 2 * r, y + 0.29 * 2 * r)]
    d.line(tick, fill="white", width=int(0.104 * 2 * r), joint="curve")
    for px, py in (tick[0], tick[2]):
        rr = 0.052 * 2 * r
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill="white")
    bold, light = inter(40, 850), inter(40, 500)
    d.text((x + 2 * r + 20 * S, y + r), "DTT", font=bold, fill="white", anchor="lm")
    dtt_w = d.textlength("DTT", font=bold)
    d.text((x + 2 * r + 20 * S + dtt_w + 9 * S, y + r), "Ireland", font=light, fill="white", anchor="lm")

    head = inter(76, 800)
    d.text((80 * S, 230 * S), "Driver theory test", font=head, fill="white", anchor="ls")
    d.text((80 * S, 318 * S), "practice for Ireland", font=head, fill=MINT, anchor="ls")
    d.text((80 * S, 392 * S), "Car and motorcycle  ·  Study in 9 languages", font=inter(32, 500), fill="white", anchor="ls")

    d.text((80 * S, 510 * S), "dttireland.com", font=inter(40, 750), fill=MINT, anchor="ls")
    d.text((80 * S, 560 * S), "Independent study app. Not affiliated with the RSA, NDLS or Prometric.",
           font=inter(22, 400), fill=MUTED, anchor="ls")

    img.resize((W, H), Image.LANCZOS).save(OUT, optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
