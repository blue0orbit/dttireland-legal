# dttireland.com

The website of DTT Ireland, the Irish driver theory test app by blue0orbit: English at the root and eight more
languages (`ga/`, `pl/`, `pt/`, `ro/`, `uk/`, `zh/`, `ur/`, `ar/`, made with the `_i18n/` tools).

This note sits in `.github/` on purpose: GitHub shows it as the repository's README, and GitHub Pages (Jekyll) never
publishes dot-folders, so it does not become a page on the site.

## How this site is published

dttireland.com is **GitHub Pages behind Cloudflare**:

- GitHub Pages serves this repository (`blue0orbit/dttireland-legal`, public, branch `main`, root folder, `CNAME`
  dttireland.com). The repository stays public because GitHub Pages needs that on the free plan.
- Cloudflare sits in front (proxied DNS). The zone adds HSTS, the site's Content-Security-Policy (a Transform Rule) and
  the AI-crawler blocks.
- **A push to `main` is the publish.** It goes live in about a minute; nothing else is needed. Pull first
  (`git pull --rebase`), because other sessions push here too. Undo: `git revert` the commit and push.
- `npm run publish-sites` (in the platform repository) is **not** used for this site: it only publishes the
  learnertest.com country sites.
- Not in this repository: the web study app at `dttireland.com/app/` and the question service at `dttireland.com/v1/`.
  The LearnerTest platform's Workers serve those paths on this host.

## Checks before a push

- Translated pages: `python _i18n/check.py <lang>` for each language you changed (it prints OK).
- `robots.txt` follows the owner's choice of 10 October 2026: search engines, AI assistants, AI search and Google's ad
  crawlers are welcome; AI-training crawlers are refused (`Content-Signal: search=yes, ai-input=yes, ai-train=no`), and
  Cloudflare blocks the same training crawlers at the edge. Keep it that way when you edit it.
