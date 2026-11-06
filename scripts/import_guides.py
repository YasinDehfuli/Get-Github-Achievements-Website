#!/usr/bin/env python3
"""Import the translated step-by-step guides from the original repository.

Usage:
    git clone --depth 1 https://github.com/4xmen/Get-Github-Achievements.git /tmp/gga
    python3 scripts/import_guides.py /tmp/gga

Writes data/guides/<lang>.json for every translated language. English
(data/guides/en.json) is written by hand and is not touched.
"""
import glob
import html
import json
import os
import re
import sys

RAW = "https://raw.githubusercontent.com/4xmen/Get-Github-Achievements/main/assets/"

# source folder suffix -> site language code
LANGS = {
    "fa": "fa", "ar": "ar", "de": "de", "fr": "fr", "ru": "ru", "tr": "tr",
    "nl": "nl", "chs": "zh", "es": "es", "id": "id", "hin": "hi", "ja": "ja",
    "am": "hy", "sw": "sw", "pt": "pt", "bn": "bn", "vi": "vi", "pl": "pl",
}

# guide file stem -> achievement id used on the site
ACHIEVEMENTS = {
    "quickdraw": "quickdraw",
    "yolo": "yolo",
    "pull-shark": "pull-shark",
    "pair-extraordinaire": "pair-extraordinaire",
    "starstruck": "starstruck",
    "galaxy-brain": "galaxy-brain",
    "publicsponsor": "public-sponsor",
}


def inline_md(text):
    """Escape HTML, then turn the little markdown used in the guides into HTML."""
    text = html.escape(text.strip(), quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def parse_guide(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    steps = []
    started = False
    for line in lines:
        s = line.strip()
        if re.match(r"^##\s", s):          # "## How to get ..." title: steps follow
            started = True
            continue
        if not started:
            continue
        # A step is a "###" heading, or a deeper heading that starts with a number
        # (one translation uses "#### 5." for its last step).
        m = re.match(r"^###\s+(.*)$", s) or re.match(r"^#{4,}\s+(\d+\s*[.)、．].*)$", s)
        if m:
            text = re.sub(r"^\d+\s*[.\-)、．:]?\s*", "", m.group(1))
            steps.append({"html": "<p>" + inline_md(text) + "</p>", "img": None, "small": False})
            continue
        if not steps:
            continue
        for tag in re.findall(r"<img\b[^>]*>", s):
            src = re.search(r'src="([^"]+)"', tag)
            width = re.search(r'width="(\d+)"', tag)
            if not src or "/badges/" in src.group(1) or steps[-1]["img"]:
                continue
            steps[-1]["img"] = RAW + re.sub(r"^(\.\./)+", "", src.group(1))
            steps[-1]["small"] = bool(width) and int(width.group(1)) <= 300
        extra = re.match(r"^#{4,}\s*-?\s*(.+)$", s)
        if extra:
            steps[-1]["html"] += "<p>" + inline_md(extra.group(1)) + "</p>"
    return steps


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "guides")
    os.makedirs(out_dir, exist_ok=True)
    for suffix, code in LANGS.items():
        guides = {}
        for stem, ach in ACHIEVEMENTS.items():
            matches = [p for p in glob.glob(os.path.join(src, "assets", "steps-" + suffix, "*.md"))
                       if re.match(r"README\." + re.escape(stem) + r"[-.]", os.path.basename(p))]
            if len(matches) != 1:
                sys.exit(f"{code}/{stem}: expected 1 guide file, found {matches}")
            steps = parse_guide(matches[0])
            if not steps:
                sys.exit(f"{code}/{stem}: no steps parsed")
            guides[ach] = steps
        with open(os.path.join(out_dir, code + ".json"), "w", encoding="utf-8") as f:
            json.dump(guides, f, ensure_ascii=False, indent=1)
        print(code, " ".join(f"{k}:{len(v)}" for k, v in guides.items()))


if __name__ == "__main__":
    main()
