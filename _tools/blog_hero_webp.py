"""Makes the WebP copies of the older guides' PNG hero pictures (assets/img/blog/*-hero.png).

    python _tools/blog_hero_webp.py        (needs Pillow with WebP)

Each PNG is only re-encoded, never redrawn, cropped or replaced: <name>-600.webp, <name>-1200.webp and
<name>-<full width>.webp (quality 80, the settings of the home page's WebP pictures of 26 Oct 2026).
The pages show them through <picture> with the PNG as the fallback, so the PNGs stay as they are.
Running it again rewrites the same files.
"""
import os

from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(SITE, "assets", "img", "blog")
HEROES = ["categories-hero", "comparison-hero", "failed-topics-hero", "how-to-pass-hero",
          "irish-language-hero", "spaced-rep-hero"]
WIDTHS = [600, 1200]  # plus the picture's own width


def main():
    for name in HEROES:
        source = Image.open(os.path.join(FOLDER, name + ".png"))
        # All six are opaque (the one RGBA file has alpha 255 everywhere), so RGB loses nothing.
        picture = source.convert("RGB")
        full_w, full_h = picture.size
        for width in WIDTHS + [full_w]:
            if width > full_w:
                continue
            height = round(full_h * width / full_w)
            out = picture if width == full_w else picture.resize((width, height), Image.LANCZOS)
            path = os.path.join(FOLDER, f"{name}-{width}.webp")
            out.save(path, "WEBP", quality=80, method=6)
            print(f"{os.path.relpath(path, SITE)}: {width}x{height}, {os.path.getsize(path):,} bytes")


if __name__ == "__main__":
    main()
