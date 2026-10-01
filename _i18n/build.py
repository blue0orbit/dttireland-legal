"""Language versions of dttireland.com.

    python _i18n/build.py prepare        # English pages: switcher + hreflang; language skeletons
    python _i18n/build.py sitemap        # sitemap.xml with every language version

The English page stays the source. `prepare` writes, for each language, a skeleton of each translated
page into _i18n/skeleton/<lang>/ (paths, canonical, hreflang, lang/dir and structured data already
localised, words still English) and copies it to <lang>/<page> only when that file does not exist yet,
so translations are never overwritten. Translators then change words only; check.py proves it.

Folders starting with "_" are not published by GitHub Pages (Jekyll), so this tool stays private.
"""
import json
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dttireland.com/"
PAGES = ["index.html", "features.html", "motorcycle.html", "faq.html", "download.html"]
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


def relocate(value):
    """A relative link from a page moved one folder down: translated pages stay beside it."""
    if not value or value.startswith(("http:", "https:", "mailto:", "tel:", "#", "/", "data:", "javascript:")):
        return value
    path = value.split("#")[0].split("?")[0]
    return value if path in PAGES else "../" + value


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
        # Site-wide entities (the app, the organisation, the website) are described once, on the
        # English pages; a translated page refers to them by @id instead of repeating them.
    if not kept:
        return None
    out = {"@context": data.get("@context", "https://schema.org"), "@graph": kept} if "@graph" in data else kept[0]
    return json.dumps(out, ensure_ascii=False, indent=2)


def localise(html, page, lang):
    html_lang, _, _, rtl = LANGS[lang]
    html = re.sub(r'<html lang="en"', f'<html lang="{html_lang}"' + (' dir="rtl"' if rtl else ""), html, count=1)
    html = ATTR_URL.sub(lambda m: f'{m.group(1)}="{relocate(m.group(2))}"', html)
    html = re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        " ".join([relocate(part.split()[0])] + part.split()[1:]) for part in m.group(1).split(",")) + '"', html)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url(page, lang)}">', html)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url(page, lang)}">', html)

    def ld(m):
        block = localise_ld(m.group(1), page, lang)
        return "" if block is None else f'<script type="application/ld+json">\n{block}\n</script>'
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, html, flags=re.S)
    return with_i18n(html, page, lang)


def prepare():
    english = [f for f in os.listdir(SITE) if f.endswith(".html")]
    english += ["blog/" + f for f in os.listdir(os.path.join(SITE, "blog")) if f.endswith(".html")]
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
            os.makedirs(os.path.join(SITE, "_i18n", "skeleton", lang), exist_ok=True)
            open(os.path.join(SITE, "_i18n", "skeleton", lang, page), "w", encoding="utf8", newline="").write(skeleton)
            target = os.path.join(SITE, lang, page)
            if not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf8", newline="").write(skeleton)
                created += 1
    print(f"English pages updated: {len(english)}; language pages created: {created}")


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
            entries.append(f"\n  <url>\n    <loc>{url(page, lang)}</loc>\n    <lastmod>2026-10-01</lastmod>{links}\n  </url>")
    xml = xml.replace("</urlset>", "  " + START + "".join(entries) + "\n  " + END + "\n</urlset>")
    open(path, "w", encoding="utf8", newline="").write(xml)
    print("sitemap: added", len(entries), "language URLs")


if __name__ == "__main__":
    {"prepare": prepare, "sitemap": sitemap}[sys.argv[1]]()
