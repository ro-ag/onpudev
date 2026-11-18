# onpu.dev

Static site for Onpu, the publisher of [Brano](https://github.com/ro-ag/brano).
Served by GitHub Pages from the `main` branch at https://onpu.dev.

- `index.html` landing page
- `brano/` Brano product page (`index.html` English, `es/index.html` Spanish, `brano.css`, `img/` screenshots captured from the Windows build)
- `brano/help/` Brano help (`index.html` English, `help.css`, `media/` screen recordings as MP4 with WebP posters); Spanish at `brano/es/help/index.html`, sharing the same CSS and media
- `brano/download/` list of current Brano packages (`index.html` English, `download.css`, `download.js`); Spanish at `brano/es/download/index.html`. The files live in the Cloudflare R2 bucket behind https://downloads.onpu.dev, filled by Brano's release workflow; `download.js` reads `brano/latest/latest.json` there for version, size and SHA-256
- `brano/releases/` Brano release notes (`index.html` English, `releases.css`); Spanish page chrome at `brano/es/releases/index.html`. Both are generated from Brano's `CHANGELOG.md` by `tools/release_notes.py`; do not edit them by hand
- `privacy.html` privacy policy referenced from the Microsoft Store listing
- `CNAME` custom domain for GitHub Pages

No build step. Edit the HTML, commit, push. The one generated part is the
release notes; after each Brano release run:

```sh
python3 tools/release_notes.py /path/to/brano/CHANGELOG.md
```
