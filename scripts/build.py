#!/usr/bin/env python3
"""Build the site: index.html (English) and <lang>/index.html for every language.

Usage:
    python3 scripts/build.py

Text for the page comes from i18n/<lang>.json; step-by-step guides come from
data/guides/<lang>.json. Edit those files, then run this script again.
"""
import datetime
import json
import os
import re
from html import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://yasindehfuli.github.io/Get-Github-Achievements-Website/"
RAW = "https://raw.githubusercontent.com/4xmen/Get-Github-Achievements/main/assets/"
REPO = "https://github.com/4xmen/Get-Github-Achievements"

# Search engine ownership checks. Paste the "content" value of the
# <meta name="google-site-verification" ...> tag from Google Search Console
# (and optionally Bing Webmaster Tools' msvalidate.01), then rebuild.
GOOGLE_SITE_VERIFICATION = ""
BING_SITE_VERIFICATION = ""

# site code -> (html lang, direction, original README file)
LANGUAGES = {
    "en": ("en", "ltr", "README.md"),
    "fa": ("fa", "rtl", "README.fa.md"),
    "ar": ("ar", "rtl", "README.ar.md"),
    "de": ("de", "ltr", "README.de.md"),
    "fr": ("fr", "ltr", "README.fr.md"),
    "ru": ("ru", "ltr", "README.ru.md"),
    "tr": ("tr", "ltr", "README.tr.md"),
    "nl": ("nl", "ltr", "README.nl.md"),
    "zh": ("zh-Hans", "ltr", "README.chs.md"),
    "es": ("es", "ltr", "README.es.md"),
    "id": ("id", "ltr", "README.id.md"),
    "hi": ("hi", "ltr", "README.hin.md"),
    "ja": ("ja", "ltr", "README.ja.md"),
    "hy": ("hy", "ltr", "README.am.md"),
    "sw": ("sw", "ltr", "README.sw.md"),
    "pt": ("pt", "ltr", "README.pt.md"),
    "bn": ("bn", "ltr", "README.bn.md"),
    "vi": ("vi", "ltr", "README.vi.md"),
    "pl": ("pl", "ltr", "README.pl.md"),
}

# id, name, badge image, difficulty, chips, requirement key, tiers key, (step index, tip key)
ACHIEVEMENTS = [
    ("quickdraw", "Quickdraw", "Quickdraw.png", "easy", ["solo", "minute"], "req_quickdraw", None, None),
    ("yolo", "YOLO", "Yolo.png", "easy", ["second_account"], "req_yolo", None, None),
    ("pull-shark", "Pull Shark", "PullShark.png", "medium", ["merge"], "req_pull_shark", "tiers_pull_shark", None),
    ("pair-extraordinaire", "Pair Extraordinaire", "PairExtraordinaire.png", "medium", ["coauthor"], "req_pair", "tiers_pair", (3, "coauthor")),
    ("starstruck", "Starstruck", "Starstruck.png", "hard", ["people"], "req_starstruck", "tiers_starstruck", None),
    ("galaxy-brain", "Galaxy Brain", "GalaxyBrain.png", "hard", ["people"], "req_galaxy", "tiers_galaxy", (0, "galaxy")),
    ("public-sponsor", "Public Sponsor", "PublicSponsor.png", "easy", ["money"], "req_sponsor", None, None),
]

SHELF_NAMES = {"pair-extraordinaire": "Pair Extra&shy;ordinaire"}


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def page_url(code):
    return SITE if code == "en" else SITE + code + "/"


def rel_link(from_code, to_code):
    up = "" if from_code == "en" else "../"
    return (up or "./") if to_code == "en" else up + to_code + "/"


def render_steps(t, ach_id, name, steps, tip):
    items = []
    for i, step in enumerate(steps):
        last = i == len(steps) - 1
        body = step["html"]
        if tip and tip[0] == i:
            if tip[1] == "coauthor":
                body += f'<div class="tip">{t["tip_coauthor"]}<code>{escape(t["tip_coauthor_code"])}</code></div>'
            else:
                body += f'<div class="tip">{t["tip_galaxy"]}</div>'
        if step["img"]:
            alt = escape(t["step_alt"].format(name=name, n=i + 1))
            cls = "shot small" if step["small"] else "shot"
            body += (f'\n              <a class="{cls}" href="{step["img"]}"><img loading="lazy" '
                     f'src="{step["img"]}" alt="{alt}"></a>')
        li_attr = ' class="done"' if last else ""
        items.append(f"            <li{li_attr}>{body}</li>")
    return "\n".join(items)


def render_card(t, guides, ach):
    ach_id, name, badge, diff, chips, req, tiers, tip = ach
    steps = guides[ach_id]
    chip_html = f'<span class="chip {diff}">{t["diff_" + diff]}</span>' + "".join(
        f'<span class="chip{" money" if c == "money" else ""}">{t["chip_" + c]}</span>' for c in chips)
    tiers_html = f'\n            <p class="tiers">{t[tiers]}</p>' if tiers else ""
    return f'''
      <article class="card" id="{ach_id}" data-id="{ach_id}">
        <div class="card-top">
          <img class="badge" src="{RAW}badges/{badge}" alt="{escape(t["badge_alt"].format(name=name))}" width="112" height="112">
          <div class="card-body">
            <div class="chips">{chip_html}</div>
            <h3>{name}</h3>
            <p class="req">{t[req]}</p>{tiers_html}
          </div>
          <button class="earn" type="button" aria-pressed="false"><span class="tick" aria-hidden="true"></span><span class="earn-label">{t["mark"]}</span></button>
        </div>
        <details>
          <summary>{t["show_steps"].format(n=len(steps))}</summary>
          <ol class="steps">
{render_steps(t, ach_id, name, steps, tip)}
          </ol>
        </details>
      </article>'''


def render_page(code, t, guides, names):
    html_lang, direction, readme = LANGUAGES[code]
    up = "" if code == "en" else "../"
    h1 = t["h1"].replace("<hl>", '<span class="hl">').replace("</hl>", "</span>")

    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{LANGUAGES[c][0]}" href="{page_url(c)}">' for c in LANGUAGES
    ) + f'\n  <link rel="alternate" hreflang="x-default" href="{SITE}">'

    def lang_links(indent):
        rows = []
        for c in LANGUAGES:
            current = ' aria-current="page"' if c == code else ""
            hl = LANGUAGES[c][0]
            rows.append(f'{indent}<li><a href="{rel_link(code, c)}" lang="{hl}" hreflang="{hl}"{current}>{names[c]}</a></li>')
        return "\n".join(rows)
    menu = lang_links("          ")
    lang_chips = lang_links("        ")

    shelf = "\n".join(
        f'        <li><a href="#{a[0]}"><img src="{RAW}badges/{a[2]}" alt="{a[1]}" width="84" height="84">'
        f'<span>{SHELF_NAMES.get(a[0], a[1])}</span></a></li>' for a in ACHIEVEMENTS)
    cards = "\n".join(render_card(t, guides, a) for a in ACHIEVEMENTS)

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": t["og_title"],
        "description": t["meta_description"],
        "url": page_url(code),
        "inLanguage": html_lang,
        "isPartOf": {"@type": "WebSite", "name": "Get GitHub Achievements", "url": SITE},
        "about": [{"@type": "Thing", "name": a[1] + " (GitHub achievement)"} for a in ACHIEVEMENTS],
        "isBasedOn": REPO,
    }, ensure_ascii=False).replace("</", "<\\/")

    verification = ""
    if GOOGLE_SITE_VERIFICATION:
        verification += f'\n  <meta name="google-site-verification" content="{escape(GOOGLE_SITE_VERIFICATION)}">'
    if BING_SITE_VERIFICATION:
        verification += f'\n  <meta name="msvalidate.01" content="{escape(BING_SITE_VERIFICATION)}">'

    rtl_font = ""
    if direction == "rtl":
        rtl_font = ('\n  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800&display=swap" '
                    'rel="stylesheet">')

    page = f'''<!doctype html>
<html lang="{html_lang}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(t["title"])}</title>
  <meta name="description" content="{escape(t["meta_description"])}">
  <meta name="theme-color" content="#0c0e13" media="(prefers-color-scheme: dark)">
  <meta name="theme-color" content="#f7f5ef" media="(prefers-color-scheme: light)">
  <link rel="canonical" href="{page_url(code)}">{verification}
{alternates}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(t["og_title"])}">
  <meta property="og:description" content="{escape(t["og_description"])}">
  <meta property="og:url" content="{page_url(code)}">
  <meta property="og:image" content="{RAW}badges/PullShark.png">
  <link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&display=swap" rel="stylesheet">{rtl_font}
  <link rel="stylesheet" href="{up}style.css">
  <script type="application/ld+json">{json_ld}</script>
</head>
<body data-mark="{escape(t["mark"])}" data-earned="{escape(t["earned"])}">
<!-- Generated by scripts/build.py from i18n/{code}.json and data/guides/{code}.json. Edit those, not this file. -->

<a class="skip" href="#achievements">{t["skip"]}</a>

<header class="nav">
  <div class="wrap nav-inner">
    <a class="brand" href="#top" aria-label="{escape(t["title"])}">
      <img src="{up}favicon.svg" alt="" width="26" height="26">
      <span>{t["title"]}</span>
    </a>
    <nav class="nav-links" aria-label="Sections">
      <a class="hide-sm" href="#achievements">{t["nav_guides"]}</a>
      <a class="hide-sm" href="#more">{t["nav_more"]}</a>
      <details class="lang-menu">
        <summary aria-label="{escape(t["lang_menu"])}"><span aria-hidden="true">🌐</span> <span class="lang-current">{names[code]}</span></summary>
        <ul>
{menu}
        </ul>
      </details>
      <a class="gh hide-xs" href="{REPO}">{t["nav_source"]}&nbsp;↗</a>
    </nav>
  </div>
</header>

<main id="top">

  <section class="hero">
    <div class="wrap">
      <p class="eyebrow">{t["eyebrow"]}</p>
      <h1>{h1}</h1>
      <p class="lede">{t["lede"]}</p>

      <ul class="shelf" aria-label="{escape(t["shelf_label"])}">
{shelf}
      </ul>

      <div class="progress" aria-live="polite">
        <div class="progress-text"><strong><bdi><span data-earned-count>0</span> / 7</bdi></strong> {t["progress_earned"]} <span class="muted">· {t["progress_hint"]}</span></div>
        <div class="bar" role="progressbar" aria-label="{escape(t["progress_earned"])}" aria-valuemin="0" aria-valuemax="7" aria-valuenow="0"><span data-earned-bar></span></div>
      </div>

      <div class="cta">
        <a class="btn primary" href="#quickdraw">{t["cta_start"]}</a>
        <a class="btn" href="{REPO}/blob/main/{readme}">{t["cta_original"]} ↗</a>
      </div>
    </div>
  </section>

  <section id="achievements" class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>{t["ach_title"]}</h2>
        <p>{t["ach_intro"]}</p>
      </div>
{cards}
    </div>
  </section>

  <section id="more" class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>{t["more_title"]}</h2>
        <p>{t["more_intro"]}</p>
      </div>

      <h3 class="sub">{t["testing_title"]}</h3>
      <div class="mini-grid">
        <div class="mini">
          <img src="{RAW}badges/HeartOnYourSleeve.png" alt="{escape(t["badge_alt"].format(name="Heart On Your Sleeve"))}" width="72" height="72" loading="lazy">
          <div><h4>Heart On Your Sleeve</h4><p>{t["testing_text"]}</p></div>
        </div>
        <div class="mini">
          <img src="{RAW}badges/OpenSourcerer.png" alt="{escape(t["badge_alt"].format(name="Open Sourcerer"))}" width="72" height="72" loading="lazy">
          <div><h4>Open Sourcerer</h4><p>{t["testing_text"]}</p></div>
        </div>
      </div>

      <h3 class="sub">{t["retired_title"]}</h3>
      <div class="mini-grid">
        <div class="mini retired">
          <img src="{RAW}badges/Mars-2020-Contributor.png" alt="{escape(t["badge_alt"].format(name="Mars 2020 Contributor"))}" width="72" height="72" loading="lazy">
          <div><h4>Mars 2020 Contributor</h4><p>{t["mars_text"]}</p></div>
        </div>
        <div class="mini retired">
          <img src="{RAW}badges/Arctic-Code-Vault-Contributor.png" alt="{escape(t["badge_alt"].format(name="Arctic Code Vault Contributor"))}" width="72" height="72" loading="lazy">
          <div><h4>Arctic Code Vault Contributor</h4><p>{t["arctic_text"]}</p></div>
        </div>
      </div>

      <h3 class="sub">{t["highlights_title"]}</h3>
      <ul class="highlights">
        <li><b>Pro</b><span>{t["hl_pro"]}</span></li>
        <li><b>Developer Program Member</b><span>{t["hl_devprogram"]}</span></li>
        <li><b>Security Bug Bounty Hunter</b><span>{t["hl_bounty"]}</span></li>
        <li><b>GitHub Campus Expert</b><span>{t["hl_campus"]}</span></li>
        <li><b>Security Advisory Credit</b><span>{t["hl_advisory"]}</span></li>
      </ul>

      <div class="two-col">
        <div class="note">
          <h3>{t["skin_title"]}</h3>
          <p>{t["skin_text"]}</p>
          <img src="{RAW}badges/quickdraw-skin.png" alt="{escape(t["skin_alt"])}" loading="lazy">
        </div>
        <div class="note">
          <h3>{t["hide_title"]}</h3>
          <p>{t["hide_text"]}</p>
          <p>{t["docs_text"]}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="fair">
        <h2>{t["fair_title"]}</h2>
        <p>{t["fair_text"]}</p>
      </div>
    </div>
  </section>

  <section id="languages" class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>{t["langs_title"]}</h2>
        <p>{t["langs_intro"]}</p>
      </div>
      <ul class="langs">
{lang_chips}
      </ul>
    </div>
  </section>

</main>

<footer class="footer">
  <div class="wrap footer-inner">
    <p>{t["footer_credit"]}</p>
    <p class="muted">{t["footer_by"]} <a href="https://github.com/YasinDehfuli">YasinDehfuli</a> · <a href="https://github.com/YasinDehfuli/Get-Github-Achievements-Website">{t["footer_source"]}</a> · {t["footer_unaffiliated"]}</p>
  </div>
</footer>

<script src="{up}main.js" defer></script>
</body>
</html>
'''
    # Open every external link in a new tab.
    page = re.sub(r'<a (class="[^"]*" )?href="(https?://[^"]+)"(?![^>]*target=)',
                  lambda m: f'<a {m.group(1) or ""}href="{m.group(2)}" target="_blank" rel="noopener"', page)
    return page


def write_seo_files():
    today = datetime.date.today().isoformat()
    alternates = "".join(
        f'\n    <xhtml:link rel="alternate" hreflang="{LANGUAGES[c][0]}" href="{page_url(c)}"/>' for c in LANGUAGES
    ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
    urls = "".join(
        f"\n  <url>\n    <loc>{page_url(c)}</loc>\n    <lastmod>{today}</lastmod>{alternates}\n  </url>" for c in LANGUAGES)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    print("wrote sitemap.xml, robots.txt")


def main():
    en = load("i18n/en.json")
    texts, names = {}, {}
    for code in LANGUAGES:
        t = load(f"i18n/{code}.json")
        missing = set(en) - set(t)
        if missing:
            raise SystemExit(f"i18n/{code}.json is missing keys: {sorted(missing)}")
        texts[code] = t
        names[code] = t["lang_name"]
    for code in LANGUAGES:
        guides = load(f"data/guides/{code}.json")
        out = os.path.join(ROOT, "index.html" if code == "en" else os.path.join(code, "index.html"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(render_page(code, texts[code], guides, names))
        print("wrote", os.path.relpath(out, ROOT))
    write_seo_files()


if __name__ == "__main__":
    main()
