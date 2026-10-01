"""Proves a translated page changed words only:  python _i18n/check.py <lang>

Compares <lang>/<page> with _i18n/skeleton/<lang>/<page> (the same page before translation):
markup, classes, links, scripts and the language menu must be identical; the words, the title, the
meta descriptions, alt/aria/title attributes and the human-readable strings of the structured data
may change, and must. Prints OK or the problems.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import LANGS, PAGES, SITE, START, END  # noqa: E402

TEXT_ATTRS = {"alt", "title", "aria-label", "placeholder"}
TEXT_META = {"description", "keywords", "og:title", "og:description", "og:locale", "og:image:alt",
             "twitter:title", "twitter:description", "twitter:image:alt"}
FIXED_LD = {"@context", "@type", "@id", "url", "item", "inLanguage", "image", "logo", "screenshot",
            "sameAs", "downloadUrl", "installUrl", "urlTemplate", "price", "priceCurrency", "email",
            "telephone", "applicationCategory", "operatingSystem", "datePublished", "dateModified",
            "position", "cssSelector", "contentUrl", "thumbnailUrl", "uploadDate"}
BRANDS = re.compile(r"DTT Ireland|Google Play|AppGallery|APK|RSA|NDLS|Pro Car|Pro Motorcycle|Pro Both|"
                    r"Android|Huawei|Honor|Rules of the Road|blue0orbit|©", re.I)


class Shape(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events, self.texts, self.ld, self.scripts = [], [], [], []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        kept = []
        for k, v in sorted(attrs):
            if k in TEXT_ATTRS:
                continue
            if tag == "meta" and k == "content" and (a.get("name") in TEXT_META or a.get("property") in TEXT_META):
                continue
            kept.append((k, v))
        self.events.append(("start", tag, tuple(kept)))
        if tag in ("script", "style"):
            self._in = (tag, a.get("type"))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))
        if tag in ("script", "style"):
            self._in = None

    def handle_data(self, data):
        if self._in:
            (self.ld if self._in == ("script", "application/ld+json") else self.scripts).append(data.strip())
        elif data.strip():
            self.texts.append(" ".join(data.split()))


def shape(path):
    html = open(path, encoding="utf8").read()
    menu = re.findall(re.escape(START) + r".*?" + re.escape(END), html, flags=re.S)
    parser = Shape()
    parser.feed(re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S))
    return parser, menu, html


def ld_problems(en, loc, where):
    problems = []
    if type(en) is not type(loc):
        return [f"{where}: structure changed"]
    if isinstance(en, dict):
        if set(en) != set(loc):
            return [f"{where}: keys changed"]
        for k in en:
            if k in FIXED_LD and en[k] != loc[k]:
                problems.append(f"{where}.{k}: must not change")
            else:
                problems += ld_problems(en[k], loc[k], f"{where}.{k}")
    elif isinstance(en, list):
        if len(en) != len(loc):
            return [f"{where}: list length changed"]
        for i, (a, b) in enumerate(zip(en, loc)):
            problems += ld_problems(a, b, f"{where}[{i}]")
    elif isinstance(en, str):
        if en.startswith(("http", "#", "mailto:")) and en != loc:
            problems.append(f"{where}: link changed")
    elif en != loc:
        problems.append(f"{where}: value changed")
    return problems


def check(lang):
    problems = []
    for page in PAGES:
        sk_path = os.path.join(SITE, "_i18n", "skeleton", lang, page)
        tr_path = os.path.join(SITE, lang, page)
        sk, sk_menu, _ = shape(sk_path)
        tr, tr_menu, tr_html = shape(tr_path)
        where = f"{lang}/{page}"
        if sk_menu != tr_menu:
            problems.append(f"{where}: the language menu or hreflang block changed")
        if sk.events != tr.events:
            for i, (a, b) in enumerate(zip(sk.events, tr.events)):
                if a != b:
                    problems.append(f"{where}: markup differs at element {i}: {a} != {b}")
                    break
            else:
                problems.append(f"{where}: element count {len(sk.events)} != {len(tr.events)}")
        if sk.scripts != tr.scripts:
            problems.append(f"{where}: a script changed")
        if len(sk.ld) != len(tr.ld):
            problems.append(f"{where}: structured data blocks changed")
        for i, (a, b) in enumerate(zip(sk.ld, tr.ld)):
            try:
                problems += ld_problems(json.loads(a), json.loads(b), f"{where} ld#{i}")
            except json.JSONDecodeError as error:
                problems.append(f"{where} ld#{i}: invalid JSON ({error})")
        # Words left in English: long text runs identical to the skeleton, brand names aside.
        english = set(sk.texts)
        left = [t for t in tr.texts if t in english and len(BRANDS.sub("", t).strip(" ·—-|:,.()")) > 18]
        if left:
            problems.append(f"{where}: {len(left)} text runs still in English, e.g. {left[0][:70]!r}")
        title_en = re.search(r"<title>(.*?)</title>", open(sk_path, encoding="utf8").read(), re.S).group(1)
        title = re.search(r"<title>(.*?)</title>", tr_html, re.S).group(1)
        if title.strip() == title_en.strip():
            problems.append(f"{where}: the <title> is still English")
        for name in ("description", "og:description"):
            pattern = rf'<meta (?:name|property)="{re.escape(name)}" content="([^"]*)"'
            en_value, tr_value = re.search(pattern, open(sk_path, encoding="utf8").read()), re.search(pattern, tr_html)
            if en_value and tr_value and en_value.group(1) == tr_value.group(1):
                problems.append(f"{where}: meta {name} is still English")
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(f"OK {lang}: {len(PAGES)} pages")


if __name__ == "__main__":
    check(sys.argv[1])
