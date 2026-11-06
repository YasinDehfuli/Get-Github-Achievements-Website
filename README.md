# Get GitHub Achievements — Website

**Live site:** https://yasindehfuli.github.io/Get-Github-Achievements-Website/

A simple, one-page website that teaches anyone how to earn GitHub achievement badges, step by step with screenshots. It's a friendly web version of the [4xmen/Get-Github-Achievements](https://github.com/4xmen/Get-Github-Achievements) guide.

## What's on the site

- **7 earnable achievements**: Quickdraw, YOLO, Pull Shark, Pair Extraordinaire, Starstruck, Galaxy Brain and Public Sponsor. Each has a difficulty tag, what you need, and a collapsible step-by-step guide with screenshots.
- **Progress tracker**: tick off the badges you've earned (saved in your browser).
- **More badges**: achievements still in testing, retired ones, and highlight badges.
- **Links to the guide in 19 languages.**

Direct links open a guide straight away, e.g. [`#yolo`](https://yasindehfuli.github.io/Get-Github-Achievements-Website/#yolo).

## Run it locally

It's plain HTML, CSS and JavaScript with no build step:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | All page content |
| `style.css` | Styles (light and dark mode follow your system setting) |
| `main.js` | "Mark as earned" tracker and opening guides from links |
| `favicon.svg` | Trophy icon |
| `.nojekyll` | Tells GitHub Pages to serve the files as-is |

Badge images and screenshots load directly from the [original repository](https://github.com/4xmen/Get-Github-Achievements/tree/main/assets), so updates there show up here automatically.

## Credits

Guide content and images: [4xmen/Get-Github-Achievements](https://github.com/4xmen/Get-Github-Achievements) (GPL-3.0). Not affiliated with GitHub.
