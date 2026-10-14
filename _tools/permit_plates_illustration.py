"""Draws the pictures for two guides:

    python _tools/permit_plates_illustration.py        (needs Pillow with WebP)

assets/img/blog/first-learner-permit.webp (1200x800) and first-learner-permit-small.webp (600x400), for
blog/first-learner-permit-ireland-after-theory-test.html: a generic permit card with a face outline, a
checklist with three ticks, an eye (the eyesight report) and an L-plate.

assets/img/blog/l-n-plates.webp (1200x800) and l-n-plates-small.webp (600x400), for
blog/l-plates-n-plates-rules-ireland.html: an L-plate, an N-plate and a learner motorcyclist's tabard.

Same method as _tools/edt_illustration.py: everything is drawn here from plain shapes in the site's colours
(the letters are polygons, not a font). No photo, screenshot, traced or AI picture. The card is not an NDLS
permit and shows no words. Folders starting with "_" are not published by GitHub Pages.
"""
import os

from PIL import Image, ImageDraw

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets", "img", "blog")
W, H, S = 1200, 800, 2  # drawn at 2x, then reduced for smooth edges

BG, ROAD, SHADOW = "#e6ede3", "#d4e0d0", "#c5d2c1"
FOREST, SPINE, PAGE, LINE = "#123d2f", "#0b2a20", "#fffdf7", "#d5ddd2"
TICK, BOX, BOX_EDGE = "#087443", "#f6f8f2", "#b9c7b5"
RED, MINT, YELLOW, YELLOW_EDGE = "#d0312d", "#8fe3b0", "#e9e04a", "#c9be2a"


def s(*values):
    return [v * S for v in values]


def pasted_rotated(base, layer, angle, centre):
    """Rotate an RGBA layer about its middle and paste it so that its middle lands on `centre`."""
    turned = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = centre[0] * S - turned.width // 2, centre[1] * S - turned.height // 2
    base.alpha_composite(turned, (int(x), int(y)))


def background():
    img = Image.new("RGBA", s(W, H), BG)
    d = ImageDraw.Draw(img)
    # a quiet road curve behind everything, as on the EDT picture and the site's share card
    d.ellipse(s(560, 380, 1560, 1320), fill=ROAD)
    d.ellipse(s(650, 470, 1470, 1230), fill=BG)
    return img, d


def letter_l(d, x, y, size):
    """A red L in a box of `size` whose top-left corner is (x, y)."""
    stem = size * 0.27
    d.rectangle(s(x, y, x + stem, y + size), fill=RED)
    d.rectangle(s(x, y + size - stem, x + size * 0.72, y + size), fill=RED)


def letter_n(d, x, y, size):
    """A red N in a box of `size` whose top-left corner is (x, y)."""
    stem, width = size * 0.22, size * 0.8
    d.rectangle(s(x, y, x + stem, y + size), fill=RED)
    d.rectangle(s(x + width - stem, y, x + width, y + size), fill=RED)
    d.polygon(s(x, y, x + stem * 1.15, y, x + width, y + size, x + width - stem * 1.15, y + size), fill=RED)


def plate(letter, width=230, height=230):
    """A white rectangular plate with a red letter, as an RGBA layer."""
    layer = Image.new("RGBA", s(width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(s(18, 22, width - 8, height - 4), radius=20 * S, fill=SHADOW)
    d.rounded_rectangle(s(10, 10, width - 16, height - 16), radius=20 * S, fill="white", outline="#d7dfd4",
                        width=3 * S)
    size = (height - 26) * 0.6
    left, top = 10 + (width - 26 - size * (0.72 if letter == "L" else 0.8)) / 2, 10 + (height - 26 - size) / 2
    (letter_l if letter == "L" else letter_n)(d, left, top, size)
    return layer


def first_permit():
    img, d = background()

    # a generic permit card: header band, a face outline, lines and a chip, no words
    d.rounded_rectangle(s(132, 214, 712, 594), radius=30 * S, fill=SHADOW)
    d.rounded_rectangle(s(120, 198, 700, 578), radius=30 * S, fill=PAGE, outline=BOX_EDGE, width=3 * S)
    d.rounded_rectangle(s(120, 198, 700, 270), radius=30 * S, fill=FOREST)
    d.rectangle(s(120, 240, 700, 270), fill=FOREST)
    d.rounded_rectangle(s(154, 300, 324, 520), radius=16 * S, fill="#e3ebe0")
    d.ellipse(s(201, 334, 277, 410), fill="#9fb3a6")
    d.chord(s(170, 420, 308, 560), start=180, end=360, fill="#9fb3a6")
    for i, width in enumerate((300, 250, 280, 200)):
        y = 318 + i * 44
        d.rounded_rectangle(s(360, y, 360 + width, y + 14), radius=7 * S, fill=LINE)
    d.rounded_rectangle(s(360, 496, 430, 540), radius=10 * S, fill=MINT)
    letter_l(d, 600, 480, 50)

    # a checklist with three ticked lines
    d.rounded_rectangle(s(772, 150, 1052, 470), radius=22 * S, fill=SHADOW)
    d.rounded_rectangle(s(760, 136, 1040, 456), radius=22 * S, fill="white", outline="#d7dfd4", width=3 * S)
    d.rounded_rectangle(s(850, 118, 950, 152), radius=12 * S, fill=FOREST)
    for i in range(3):
        y = 196 + i * 82
        d.rounded_rectangle(s(792, y, 846, y + 54), radius=10 * S, fill=BOX, outline=BOX_EDGE, width=3 * S)
        d.line(s(805, y + 28, 816, y + 40, 836, y + 14), fill=TICK, width=8 * S, joint="curve")
        d.rounded_rectangle(s(866, y + 20, 866 + (140, 120, 132)[i], y + 34), radius=7 * S, fill=LINE)

    # an eye, for the eyesight report
    d.ellipse(s(812, 540, 1092, 680), fill=SHADOW)
    d.ellipse(s(800, 524, 1080, 664), fill="white", outline=FOREST, width=6 * S)
    d.ellipse(s(894, 548, 986, 640), fill=TICK)
    d.ellipse(s(918, 572, 962, 616), fill=SPINE)
    d.ellipse(s(926, 576, 942, 592), fill="white")

    return img


def tabard():
    """A learner motorcyclist's yellow tabard with an L patch, as an RGBA layer."""
    layer = Image.new("RGBA", s(320, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # a sleeveless vest: shoulders, a V neck, armholes and a straight hem
    body = (86, 30, 128, 30, 160, 112, 192, 30, 234, 30, 246, 96, 284, 150, 284, 352,
            36, 352, 36, 150, 74, 96)
    d.polygon(s(*[v + (10 if i % 2 else 8) for i, v in enumerate(body)]), fill=SHADOW)
    d.polygon(s(*body), fill=YELLOW)
    d.line(s(*body, body[0], body[1]), fill=YELLOW_EDGE, width=4 * S, joint="curve")
    d.rounded_rectangle(s(98, 168, 222, 292), radius=12 * S, fill="white", outline="#d7dfd4", width=3 * S)
    letter_l(d, 126, 192, 76)
    return layer


def plates():
    img, _ = background()
    pasted_rotated(img, plate("L", 330, 330), -7, (290, 370))
    pasted_rotated(img, plate("N", 330, 330), 6, (640, 420))
    pasted_rotated(img, tabard(), -4, (975, 390))
    return img


def save(img, name):
    full = img.convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    full.save(os.path.join(OUT, f"{name}.webp"), "WEBP", quality=88, method=6)
    full.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(OUT, f"{name}-small.webp"), "WEBP",
                                                       quality=88, method=6)
    print(f"wrote {name}.webp and {name}-small.webp")


if __name__ == "__main__":
    save(first_permit(), "first-learner-permit")
    save(plates(), "l-n-plates")
