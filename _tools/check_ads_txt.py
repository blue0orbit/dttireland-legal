"""Keep dttireland.com's ads.txt and app-ads.txt intact.

    python _tools/check_ads_txt.py          # check the files in this checkout
    python _tools/check_ads_txt.py --live   # also check what https://dttireland.com serves

Run it before every push. It prints OK, or what is wrong and exits with 1.

- ads.txt is for the website (Google AdSense). It must hold exactly one record, the line AdSense gives for this
  account. Comment lines (#) and blank lines are allowed.
- app-ads.txt is for the Android app (AdMob, Unity and its resellers). It is pinned by its SHA-256, so no tool or edit
  can drop a line by accident (on 10 Oct 2026 an Australian site build overwrote that site's app-ads.txt). If you
  change app-ads.txt on purpose, put the new file's SHA-256 in APP_ADS_SHA256 below in the same commit.
- Both files: plain ASCII, no byte-order mark, LF line endings, at the site root.

The publisher ID is public: it is printed in every ad request and in Google's sellers.json.
"""
import hashlib
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent

ADSENSE_LINE = 'google.com, pub-1798960414758701, DIRECT, f08c47fec0942fa0'
ADMOB_LINE = 'google.com, pub-1798960414758701, DIRECT, f08c47fec0942fa0'
UNITY_LINE = 'unity.com, 3234135, DIRECT, 96cabb5fbdde37a7'
APP_ADS_SHA256 = 'a3ee7504f227e94199b40578bf6b8413843a7e968b18076e102235c81389ea45'
APP_ADS_MIN_LINES = 161

errors = []


def records(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]


def check_bytes(name, data):
    if data.startswith(b'\xef\xbb\xbf'):
        errors.append(f'{name}: starts with a byte-order mark')
    if b'\r' in data:
        errors.append(f'{name}: has CR characters (use LF line endings)')
    try:
        data.decode('ascii')
    except UnicodeDecodeError:
        errors.append(f'{name}: is not plain ASCII')
    if data and not data.endswith(b'\n'):
        errors.append(f'{name}: does not end with a newline')


def check_ads(data, where):
    check_bytes(f'{where} ads.txt', data)
    found = records(data.decode('ascii', 'replace'))
    if found != [ADSENSE_LINE]:
        errors.append(f'{where} ads.txt: must hold exactly the one AdSense record {ADSENSE_LINE!r}; found {found!r}')


def check_app_ads(data, where):
    check_bytes(f'{where} app-ads.txt', data)
    text = data.decode('ascii', 'replace')
    found = records(text)
    for line in (ADMOB_LINE, UNITY_LINE):
        if line not in found:
            errors.append(f'{where} app-ads.txt: the line {line!r} is missing')
    if len(text.splitlines()) < APP_ADS_MIN_LINES:
        errors.append(f'{where} app-ads.txt: has {len(text.splitlines())} lines, expected at least {APP_ADS_MIN_LINES}')
    digest = hashlib.sha256(data).hexdigest()
    if digest != APP_ADS_SHA256:
        errors.append(f'{where} app-ads.txt: SHA-256 is {digest}, expected {APP_ADS_SHA256}. If you changed it on '
                      'purpose, update APP_ADS_SHA256 (and APP_ADS_MIN_LINES) in _tools/check_ads_txt.py.')


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'dttireland-ads-txt-check'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.geturl() != url:
            errors.append(f'{url}: redirected to {response.geturl()} (Google needs a direct 200)')
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('text/plain'):
            errors.append(f'{url}: Content-Type is {content_type!r}, expected text/plain')
        return response.status, response.read()


def main():
    # A Windows console may not print every character of a broken file; never crash on that.
    sys.stdout.reconfigure(errors='backslashreplace')
    local = {}
    for name in ('ads.txt', 'app-ads.txt'):
        path = ROOT / name
        if not path.is_file():
            errors.append(f'{name}: missing at the site root')
        else:
            local[name] = path.read_bytes()
    if 'ads.txt' in local:
        check_ads(local['ads.txt'], 'repo')
    if 'app-ads.txt' in local:
        check_app_ads(local['app-ads.txt'], 'repo')

    if '--live' in sys.argv[1:]:
        for name in ('ads.txt', 'app-ads.txt'):
            url = f'https://dttireland.com/{name}'
            try:
                status, data = fetch(url)
            except urllib.error.HTTPError as error:
                errors.append(f'{url}: HTTP {error.code}')
                continue
            except OSError as error:
                errors.append(f'{url}: {error}')
                continue
            if status != 200:
                errors.append(f'{url}: HTTP {status}')
            (check_ads if name == 'ads.txt' else check_app_ads)(data, 'live')
            if name in local and data != local[name]:
                errors.append(f'{url}: differs from the repo file (GitHub Pages may still be publishing; retry in '
                              'a minute)')

    if errors:
        print('FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print('OK' + (' (repo and live)' if '--live' in sys.argv[1:] else ' (repo)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
