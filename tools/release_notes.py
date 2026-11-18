#!/usr/bin/env python3
"""Generate the Brano release-notes pages from Brano's CHANGELOG.md.

Usage:
    python3 tools/release_notes.py /path/to/brano/CHANGELOG.md

Writes brano/releases/index.html (English) and brano/es/releases/index.html
(Spanish page chrome; the notes themselves are written in English). Run it
after each Brano release and commit the result. Standard library only.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE_HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?\s*$")
CODE_SPAN = re.compile(r"`([^`]+)`")

LANGUAGES = {
    "en": {
        "out": "brano/releases/index.html",
        "up": "../",
        "url": "https://onpu.dev/brano/releases/",
        "title": "Brano release notes",
        "description": "What changed in each Brano release: additions, changes and fixes, newest first.",
        "heading": "Release notes",
        "lede": 'What changed in each Brano release, newest first. Get the current release from the <a href="../download/">download page</a>.',
        "nav": [("../", "Brano"), ("../download/", "Download"), ("../help/", "Help")],
        "other": ("../es/releases/", "es", "Español"),
        "footer": [("../help/", "Help"), ("mailto:support@onpu.dev", "Support"),
                   ("https://onpu.dev/privacy.html", "Privacy policy"), ("https://onpu.dev/", "Onpu")],
        "copyright": "© 2026 Onpu. Brano is a trademark of its author.",
        "sections": {},
    },
    "es": {
        "out": "brano/es/releases/index.html",
        "up": "../../",
        "url": "https://onpu.dev/brano/es/releases/",
        "title": "Notas de versión de Brano",
        "description": "Qué cambió en cada versión de Brano: novedades, cambios y correcciones, de la más reciente a la más antigua.",
        "heading": "Notas de versión",
        "lede": 'Qué cambió en cada versión de Brano, de la más reciente a la más antigua. Las notas se publican en inglés. La versión actual está en la <a href="../download/">página de descargas</a>.',
        "nav": [("../", "Brano"), ("../download/", "Descargar"), ("../help/", "Ayuda")],
        "other": ("../../releases/", "en", "English"),
        "footer": [("../help/", "Ayuda"), ("mailto:support@onpu.dev", "Soporte"),
                   ("https://onpu.dev/privacy.html", "Política de privacidad"), ("https://onpu.dev/", "Onpu")],
        "copyright": "© 2026 Onpu. Brano es una marca de su autor.",
        "sections": {
            "Added": "Añadido",
            "Changed": "Cambiado",
            "Fixed": "Corregido",
            "Removed": "Eliminado",
            "Security": "Seguridad",
            "Documentation": "Documentación",
            "Known limitations": "Limitaciones conocidas",
        },
    },
}


def inline(text: str) -> str:
    """Escape text and turn Markdown code spans into <code>."""
    parts = []
    last = 0
    for match in CODE_SPAN.finditer(text):
        parts.append(html.escape(text[last:match.start()], quote=False))
        parts.append(f"<code>{html.escape(match.group(1), quote=False)}</code>")
        last = match.end()
    parts.append(html.escape(text[last:], quote=False))
    return "".join(parts)


def parse(changelog: str) -> list[dict]:
    """Return released versions as {version, date, blocks}; blocks are
    ("h", text), ("p", text) or ("ul", [items])."""
    releases: list[dict] = []
    current: dict | None = None
    kind = None  # "p" or "li" while a paragraph or list item is open
    buffer: list[str] = []

    def flush() -> None:
        nonlocal kind, buffer
        if current is not None and kind and buffer:
            text = " ".join(buffer)
            blocks = current["blocks"]
            if kind == "p":
                blocks.append(("p", text))
            elif blocks and blocks[-1][0] == "ul":
                blocks[-1][1].append(text)
            else:
                blocks.append(("ul", [text]))
        kind, buffer = None, []

    for raw in changelog.splitlines():
        line = raw.rstrip()
        heading = RELEASE_HEADING.match(line)
        if heading:
            flush()
            current = None
            if heading["date"]:  # skips [Unreleased]
                current = {"version": heading["version"], "date": heading["date"], "blocks": []}
                releases.append(current)
            continue
        if current is None:
            continue
        if line.startswith("### "):
            flush()
            current["blocks"].append(("h", line[4:].strip()))
        elif line.startswith("- "):
            flush()
            kind, buffer = "li", [line[2:].strip()]
        elif not line.strip():
            flush()
        elif kind:
            buffer.append(line.strip())
        else:
            kind, buffer = "p", [line.strip()]
    flush()
    return releases


def render_release(release: dict, sections: dict[str, str], latest: bool) -> str:
    version, date = release["version"], release["date"]
    out = [f'      <section class="release" id="v{html.escape(version)}">']
    badge = ' <span class="badge">Latest</span>' if latest and not sections else ""
    if latest and sections:
        badge = ' <span class="badge">Actual</span>'
    out.append(f'        <h2><a href="#v{html.escape(version)}">{html.escape(version)}</a>{badge} <time datetime="{date}">{date}</time></h2>')
    for block in release["blocks"]:
        if block[0] == "h":
            out.append(f"        <h3>{html.escape(sections.get(block[1], block[1]))}</h3>")
        elif block[0] == "p":
            out.append(f"        <p>{inline(block[1])}</p>")
        else:
            out.append("        <ul>")
            out.extend(f"          <li>{inline(item)}</li>" for item in block[1])
            out.append("        </ul>")
    out.append("      </section>")
    return "\n".join(out)


def links(items: list[tuple[str, str]], sep: str) -> str:
    return sep.join(f'<a href="{href}">{label}</a>' for href, label in items)


def render_page(lang: str, releases: list[dict]) -> str:
    cfg = LANGUAGES[lang]
    up = cfg["up"]
    other_href, other_lang, other_label = cfg["other"]
    nav = "\n".join(f'          <li><a href="{href}">{label}</a></li>' for href, label in cfg["nav"])
    body = "\n".join(render_release(r, cfg["sections"], i == 0) for i, r in enumerate(releases))
    title, description = html.escape(cfg["title"]), html.escape(cfg["description"])
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#111820">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="https://onpu.dev/brano/img/brano-hero.webp">
  <meta property="og:url" content="{cfg["url"]}">
  <link rel="alternate" hreflang="en" href="https://onpu.dev/brano/releases/">
  <link rel="alternate" hreflang="es" href="https://onpu.dev/brano/es/releases/">
  <link rel="icon" type="image/svg+xml" href="{up}img/brano-icon.svg">
  <link rel="stylesheet" href="{up}brano.css">
  <link rel="stylesheet" href="{up}releases/releases.css">
</head>
<body>
  <!-- Generated by tools/release_notes.py from Brano's CHANGELOG.md. Do not edit by hand. -->
  <header>
    <div class="wrap">
      <nav class="nav">
        <a href="../"><img src="{up}img/brano-lockup.svg" width="125" height="32" alt="Brano"></a>
        <ul>
{nav}
          <li><a href="{other_href}" hreflang="{other_lang}">{other_label}</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <main class="notes">
    <div class="wrap">
      <h1>{html.escape(cfg["heading"])}</h1>
      <p class="lede">{cfg["lede"]}</p>
{body}
    </div>
  </main>
  <footer>
    <div class="wrap">
      <span>{cfg["copyright"]}</span>
      <span>{links(cfg["footer"], " · ")}</span>
    </div>
  </footer>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    releases = parse(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not releases:
        print("no released versions found in the changelog", file=sys.stderr)
        return 1
    for lang, cfg in LANGUAGES.items():
        target = ROOT / cfg["out"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(lang, releases), encoding="utf-8")
        print(f"wrote {cfg['out']} ({len(releases)} releases, newest {releases[0]['version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
