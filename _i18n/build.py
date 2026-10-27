"""Language versions of dttireland.com.

    python _i18n/build.py prepare        # English pages: switcher + hreflang; language skeletons
    python _i18n/build.py sitemap        # sitemap.xml with every language version
    python _i18n/build.py applinks       # translated pages: links to the web app carry ?lang=<code>,
                                         # and the Google Play badge is the one in their language

The translated pages are PAGES: the home, features, motorcycle, FAQ and download pages, and the guides listed
there (blog/<guide> becomes <lang>/blog/<guide>; the other guides and the guide index stay English-only).

The English page stays the source. `prepare` writes, for each language, a skeleton of each translated
page into _i18n/skeleton/<lang>/ (paths, canonical, hreflang, lang/dir and structured data already
localised, words still English) and copies it to <lang>/<page> only when that file does not exist yet,
so translations are never overwritten. Translators then change words only; check.py proves it.

Links to the web study app on a translated page open it in that page's language: /app/ becomes
/app/?lang=<code> (the app takes the hint, remembers it and removes it from the address). The skeleton
carries it, and `prepare` (or `applinks`) puts it into the existing translated pages too. The codes are
the folder names, which are the app's own (pt = the Brazilian Portuguese of these pages).

Folders starting with "_" are not published by GitHub Pages (Jekyll), so this tool stays private.
"""
import json
import os
import posixpath
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dttireland.com/"
# Translated pages. A guide in blog/ is translated to <lang>/blog/<page>; its links to other translated
# pages go to that language's version, everything else to the English page (relocate).
PAGES = ["index.html", "features.html", "motorcycle.html", "faq.html", "download.html",
         "blog/edt-essential-driver-training-ireland.html", "blog/first-learner-permit-ireland-after-theory-test.html"]
# <lastmod> of a page's language URLs in the sitemap (the date the translations were published).
LASTMOD = {"blog/edt-essential-driver-training-ireland.html": "2026-10-13",
           "blog/first-learner-permit-ireland-after-theory-test.html": "2026-10-14"}
# code: (html lang, hreflang, native name, right-to-left)
LANGS = {
    "ga": ("ga", "ga", "Gaeilge", False),
    "pl": ("pl", "pl", "Polski", False),
    "pt": ("pt-BR", "pt", "Português", False),
    "ro": ("ro", "ro", "Română", False),
    "uk": ("uk", "uk", "Українська", False),
    "zh": ("zh-Hans", "zh-Hans", "简体中文", False),
    "ar": ("ar", "ar", "العربية", True),
    "ur": ("ur", "ur", "اردو", True),
}
# A link to the web study app (/app/, optionally absolute, with a language hint already or a #route).
APP_LINK = re.compile(r'\bhref="((?:https://dttireland\.com)?/app/)(?:\?lang=[^"#&]*)?(#[^"]*)?"')
# Google's official "Get it on Google Play" badge in the page's language (assets/img/badges/SOURCES.txt).
# ga, ar and ur keep the English badge: no Irish badge exists, and Google's public Arabic and Urdu
# files still carry the old logo.
PLAY_BADGE = {"pl": "pl", "pt": "pt-br", "ro": "ro", "uk": "uk", "zh": "zh-cn"}
BADGE_SRC = re.compile(r'(assets/img/badges/google-play-)[a-z-]+(\.png)')
CSS_LINK = '<link rel="stylesheet" href="/assets/css/i18n.css?v=20261001-2">'
START, END = "<!-- i18n:start -->", "<!-- i18n:end -->"


def url(page, lang=None):
    path = "" if page == "index.html" else page
    return BASE + (f"{lang}/" if lang else "") + path


def href(page, lang=None):
    return "/" + (f"{lang}/" if lang else "") + ("" if page == "index.html" else page)


def head_block(page, lang):
    """Stylesheet, plus hreflang alternates for a translated page."""
    lines = [CSS_LINK]
    if page in PAGES:
        lines.append(f'<link rel="alternate" hreflang="en" href="{url(page)}">')
        lines += [f'<link rel="alternate" hreflang="{v[1]}" href="{url(page, k)}">' for k, v in LANGS.items()]
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{url(page)}">')
    return START + "".join(lines) + END


def switcher(page, lang):
    """A no-JavaScript language menu. Pages that are not translated offer each language's home."""
    target = page if page in PAGES else "index.html"
    current = "English" if lang is None else LANGS[lang][2]
    items = [f'<li><a href="{href(page if page in PAGES else page)}" hreflang="en" lang="en"'
             f'{" aria-current=\"true\"" if lang is None else ""}>English</a></li>']
    for k, (html_lang, _, name, _) in LANGS.items():
        cur = ' aria-current="true"' if k == lang else ""
        items.append(f'<li><a href="{href(target, k)}" hreflang="{LANGS[k][1]}" lang="{html_lang}"{cur}>{name}</a></li>')
    return (f'{START}<details class="site-lang"><summary><span aria-hidden="true">🌐</span> '
            f'<span class="site-lang-current">{current}</span></summary><ul>{"".join(items)}</ul></details>{END}')


def app_links(html, lang):
    """Every link to the web app on a page in `lang` opens the app in that language."""
    return APP_LINK.sub(lambda m: f'href="{m.group(1)}?lang={lang}{m.group(2) or ""}"', html)


def store_badges(html, lang):
    """The Google Play badge on a page in `lang` is Google's badge for that language, else English."""
    return BADGE_SRC.sub(lambda m: m.group(1) + PLAY_BADGE.get(lang, "en") + m.group(2), html)


def strip_blocks(html):
    return re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)


def with_i18n(html, page, lang):
    html = strip_blocks(html)
    html = re.sub(r'(<link rel="stylesheet" href="[^"]*editorial\.css[^"]*">)',
                  lambda m: m.group(1) + head_block(page, lang), html, count=1)
    assert START in html, f"no editorial.css link in {page}"
    html, n = re.subn(r'(<a class="site-download")', lambda m: switcher(page, lang) + m.group(1), html, count=1)
    assert n == 1, f"no header download button in {page}"
    return html


# ── Localised skeleton ──────────────────────────────────────────────────────────────────────

ATTR_URL = re.compile(r'\b(href|src|poster)="([^"]*)"')


def relocate(value, page="index.html", lang=None):
    """A relative link from a page moved one folder down: translated pages stay beside it.
    For a page in a subfolder (blog/), the link is resolved from the English page's folder and pointed
    from <lang>/<folder>/ at the language version of a translated page, else at the English page.
    The site's home link "/" (logo, breadcrumb "Home") becomes that language's home, "/<lang>/"."""
    if value == "/" and lang:
        return href("index.html", lang)
    if not value or value.startswith(("http:", "https:", "mailto:", "tel:", "#", "/", "data:", "javascript:")):
        return value
    path = value.split("#")[0].split("?")[0]
    folder = posixpath.dirname(page)
    if not folder:
        return value if path in PAGES else "../" + value
    target = posixpath.normpath(posixpath.join(folder, path))
    dest = f"{lang}/{target}" if target in PAGES else target
    moved = posixpath.relpath(dest, f"{lang}/{folder}") + ("/" if path.endswith("/") else "")
    return moved + value[len(path):]


def localise_ld(block, page, lang):
    data = json.loads(block)
    mapping = {url(p): url(p, lang) for p in PAGES}

    def local(value):
        for en, loc in mapping.items():
            if value == en:
                return loc
            if value.startswith(en + "#") and en != BASE:
                return loc + value[len(en):]
        if value in (BASE + "#webpage", BASE + "#page", BASE + "#breadcrumbs") and page == "index.html":
            return url("index.html", lang) + value[len(BASE):]
        return value

    nodes = data.get("@graph", [data])
    kept = []
    for node in nodes:
        kind = node.get("@type")
        if kind in ("WebPage", "FAQPage", "ItemList", "BreadcrumbList", "HowTo", "CollectionPage", "AboutPage"):
            for key in ("@id", "url"):
                if isinstance(node.get(key), str):
                    node[key] = local(node[key])
            if "inLanguage" in node:
                node["inLanguage"] = LANGS[lang][1]
            for item in node.get("itemListElement", []):
                if isinstance(item, dict) and isinstance(item.get("item"), str):
                    item["item"] = local(item["item"])
            kept.append(node)
        elif kind == "BlogPosting":
            # A translated guide is its own article in its language.
            if isinstance(node.get("mainEntityOfPage"), str):
                node["mainEntityOfPage"] = local(node["mainEntityOfPage"])
            if "inLanguage" in node:
                node["inLanguage"] = LANGS[lang][1]
            kept.append(node)
        # Site-wide entities (the app, the organisation, the website) are described once, on the
        # English pages; a translated page refers to them by @id instead of repeating them.
    if not kept:
        return None
    out = {"@context": data.get("@context", "https://schema.org"), "@graph": kept} if "@graph" in data else kept[0]
    return json.dumps(out, ensure_ascii=False, indent=2)


def localise(html, page, lang):
    html_lang, _, _, rtl = LANGS[lang]
    html = re.sub(r'<html lang="en"', f'<html lang="{html_lang}"' + (' dir="rtl"' if rtl else ""), html, count=1)
    html = ATTR_URL.sub(lambda m: f'{m.group(1)}="{relocate(m.group(2), page, lang)}"', html)
    html = re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        " ".join([relocate(part.split()[0], page, lang)] + part.split()[1:]) for part in m.group(1).split(",")) + '"',
        html)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url(page, lang)}">', html)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url(page, lang)}">', html)

    def ld(m):
        block = localise_ld(m.group(1), page, lang)
        return "" if block is None else f'<script type="application/ld+json">\n{block}\n</script>'
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, html, flags=re.S)
    return store_badges(app_links(with_i18n(html, page, lang), lang), lang)


def prepare():
    english = [f for f in os.listdir(SITE) if f.endswith(".html")]
    # blog/index.html only forwards dttireland.com/blog/ to the guide index (blog.html): not a page to localise.
    english += ["blog/" + f for f in os.listdir(os.path.join(SITE, "blog")) if f.endswith(".html") and f != "index.html"]
    for page in english:
        path = os.path.join(SITE, page)
        source = open(path, encoding="utf8").read()
        updated = with_i18n(source, page if page in PAGES else page, None)
        if updated != source:
            open(path, "w", encoding="utf8", newline="").write(updated)
    created = 0
    for lang in LANGS:
        for page in PAGES:
            source = open(os.path.join(SITE, page), encoding="utf8").read()
            skeleton = localise(source, page, lang)
            skeleton_path = os.path.join(SITE, "_i18n", "skeleton", lang, page)
            os.makedirs(os.path.dirname(skeleton_path), exist_ok=True)
            open(skeleton_path, "w", encoding="utf8", newline="").write(skeleton)
            target = os.path.join(SITE, lang, page)
            if not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf8", newline="").write(skeleton)
                created += 1
    print(f"English pages updated: {len(english)}; language pages created: {created}")
    applinks()


def applinks():
    """The existing translated pages get the same ?lang= on their links to the web app, and the same
    store badge, as their skeleton."""
    changed = 0
    for lang in LANGS:
        for page in PAGES:
            target = os.path.join(SITE, lang, page)
            if not os.path.exists(target):
                continue
            html = open(target, encoding="utf8").read()
            updated = store_badges(app_links(html, lang), lang)
            if updated != html:
                open(target, "w", encoding="utf8", newline="").write(updated)
                changed += 1
    print(f"translated pages with web app links updated: {changed}")


def sitemap():
    path = os.path.join(SITE, "sitemap.xml")
    xml = open(path, encoding="utf8").read()
    xml = re.sub(r"\s*<!-- i18n:start -->.*?<!-- i18n:end -->", "", xml, flags=re.S)
    if 'xmlns:xhtml=' not in xml:
        xml = xml.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
                          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"', 1)
    entries = []
    for page in PAGES:
        alternates = [("en", url(page))] + [(v[1], url(page, k)) for k, v in LANGS.items()] + [("x-default", url(page))]
        links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in alternates)
        for lang in LANGS:
            entries.append(f"\n  <url>\n    <loc>{url(page, lang)}</loc>\n    <lastmod>{LASTMOD.get(page, '2026-10-01')}</lastmod>{links}\n  </url>")
    xml = xml.replace("</urlset>", "  " + START + "".join(entries) + "\n  " + END + "\n</urlset>")
    open(path, "w", encoding="utf8", newline="").write(xml)
    print("sitemap: added", len(entries), "language URLs")


if __name__ == "__main__":
    {"prepare": prepare, "sitemap": sitemap, "applinks": applinks}[sys.argv[1]]()
