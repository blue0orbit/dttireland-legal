"""Draws the picture for the EDT guide (blog/edt-essential-driver-training-ireland.html):

    python _tools/edt_illustration.py        (needs Pillow with WebP)

assets/img/blog/edt-logbook.webp (1200x800) and edt-logbook-small.webp (600x400): an open training logbook
with 12 session boxes (seven ticked, one stamped), a pen and an L-plate. Everything is drawn here from
plain shapes in the site's colours: no photo, no screenshot, no font, no traced or AI picture. It is not
the RSA's logbook and shows no words. Folders starting with "_" are not published by GitHub Pages.
"""
import os

from PIL import Image, ImageDraw

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets", "img", "blog")
W, H, S = 1200, 800, 2  # drawn at 2x, then reduced for smooth edges

BG, ROAD, SHADOW = "#e6ede3", "#d4e0d0", "#c5d2c1"
FOREST, SPINE, PAGE, LINE = "#123d2f", "#0b2a20", "#fffdf7", "#d5ddd2"
TICK, STAMP, BOX, BOX_EDGE = "#087443", "#cc7e3d", "#f6f8f2", "#b9c7b5"
RED, MINT, NIB = "#d0312d", "#8fe3b0", "#e6c79c"


def s(*values):
    return [v * S for v in values]


def pasted_rotated(base, layer, angle, centre):
    """Rotate an RGBA layer about its middle and paste it so that its middle lands on `centre`."""
    turned = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = centre[0] * S - turned.width // 2, centre[1] * S - turned.height // 2
    base.alpha_composite(turned, (int(x), int(y)))


def l_plate():
    layer = Image.new("RGBA", s(230, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(s(18, 22, 222, 226), radius=20 * S, fill=SHADOW)
    d.rounded_rectangle(s(10, 10, 214, 214), radius=20 * S, fill="white", outline="#d7dfd4", width=3 * S)
    d.rectangle(s(66, 46, 108, 170), fill=RED)
    d.rectangle(s(66, 128, 162, 170), fill=RED)
    return layer


def pen():
    layer = Image.new("RGBA", s(330, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(s(40, 8, 300, 32), radius=12 * S, fill=FOREST)
    d.rounded_rectangle(s(236, 6, 312, 34), radius=13 * S, fill=MINT)
    d.polygon(s(40, 8, 40, 32, 8, 20), fill=NIB)
    d.polygon(s(16, 16, 16, 24, 6, 20), fill=SPINE)
    return layer


def main():
    img = Image.new("RGBA", s(W, H), BG)
    d = ImageDraw.Draw(img)
    # a quiet road curve behind everything, as on the site's share card
    d.ellipse(s(560, 380, 1560, 1320), fill=ROAD)
    d.ellipse(s(650, 470, 1470, 1230), fill=BG)

    # the open logbook
    d.rounded_rectangle(s(162, 186, 882, 666), radius=26 * S, fill=SHADOW)
    d.rounded_rectangle(s(150, 170, 870, 650), radius=26 * S, fill=FOREST)
    d.rounded_rectangle(s(172, 188, 506, 632), radius=14 * S, fill=PAGE)
    d.rounded_rectangle(s(514, 188, 848, 632), radius=14 * S, fill=PAGE)
    d.rectangle(s(506, 188, 514, 632), fill=SPINE)

    # left page: a heading bar, lines of notes and a signature
    d.rounded_rectangle(s(204, 226, 404, 248), radius=8 * S, fill="#2d5a47")
    for i, width in enumerate((262, 236, 270, 214, 250, 228, 196)):
        y = 286 + i * 40
        d.rounded_rectangle(s(204, y, 204 + width, y + 12), radius=6 * S, fill=LINE)
    wave = [(214 + i * 12, 590 + (8 if i % 2 else -8)) for i in range(11)]
    d.line([(x * S, y * S) for x, y in wave], fill="#6b7f73", width=4 * S, joint="curve")

    # right page: 12 session boxes, seven ticked and one stamped
    for n in range(12):
        col, row = n % 3, n // 3
        x, y = 543 + col * 98, 228 + row * 92
        d.rounded_rectangle(s(x, y, x + 80, y + 72), radius=12 * S, fill=BOX, outline=BOX_EDGE, width=3 * S)
        if n < 7:
            d.line(s(x + 22, y + 38, x + 36, y + 52, x + 60, y + 22), fill=TICK, width=9 * S, joint="curve")
            for px, py in ((x + 22, y + 38), (x + 60, y + 22)):
                d.ellipse(s(px - 4.5, py - 4.5, px + 4.5, py + 4.5), fill=TICK)
        elif n == 7:
            cx, cy = x + 40, y + 36
            d.ellipse(s(cx - 27, cy - 27, cx + 27, cy + 27), outline=STAMP, width=5 * S)
            d.ellipse(s(cx - 15, cy - 15, cx + 15, cy + 15), outline=STAMP, width=3 * S)

    pasted_rotated(img, pen(), 24, (905, 620))
    pasted_rotated(img, l_plate(), -8, (1030, 330))

    full = img.convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    full.save(os.path.join(OUT, "edt-logbook.webp"), "WEBP", quality=88, method=6)
    full.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(OUT, "edt-logbook-small.webp"), "WEBP",
                                                       quality=88, method=6)
    print("wrote edt-logbook.webp and edt-logbook-small.webp")


if __name__ == "__main__":
    main()
