"""Build the self-hosted app in app/ from src/sheen.html.

src/sheen.html is written as a page body, the form the Claude artifact uses, and
loads highlight.js and fonts from CDNs. This wraps it in a full document, points
it at the bundled copies so it works with no internet access, and writes the
PWA manifest and service worker.

    python3 src/build.py
"""
import hashlib
import json
from pathlib import Path

VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"

HLJS_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>'
HLJS_LOCAL = '<script src="vendor/highlight.min.js"></script>'
FONTS_LOCAL = '<link rel="stylesheet" href="fonts/fonts.css">'

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#121317">
<meta name="description" content="Beautiful code images in the color themes that ship with Xcode.">
<meta name="apple-mobile-web-app-title" content="Sheen">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="manifest" href="manifest.webmanifest">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""

SW_REGISTER = """<script>
if ("serviceWorker" in navigator && window.isSecureContext) navigator.serviceWorker.register("sw.js").catch(() => {});
</script>"""


def replace_fonts(body: str) -> str:
    start = body.find('<link rel="preconnect" href="https://fonts.googleapis.com">')
    marker = 'display=swap">'
    end = body.find(marker, start)
    if start < 0 or end < 0:
        raise SystemExit("Google Fonts links not found in src/sheen.html")
    return body[:start] + FONTS_LOCAL + body[end + len(marker):]


def main() -> None:
    body = (ROOT / "src" / "sheen.html").read_text()
    if HLJS_CDN not in body:
        raise SystemExit("highlight.js script tag not found in src/sheen.html")
    body = replace_fonts(body.replace(HLJS_CDN, HLJS_LOCAL))
    html = HEAD + body + "\n" + SW_REGISTER + "\n</body>\n</html>\n"
    (APP / "index.html").write_text(html)

    manifest = {
        "name": "Sheen",
        "short_name": "Sheen",
        "description": "Beautiful code images in the color themes that ship with Xcode.",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#121317",
        "theme_color": "#121317",
        "icons": [
            {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"},
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (APP / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")

    # Cache every shipped file; the cache name changes whenever any of them does.
    assets = sorted(
        str(p.relative_to(APP)) for p in APP.rglob("*")
        if p.is_file() and p.name != "sw.js" and not p.name.startswith("LICENSE")
        and not any(part.startswith(".") for part in p.relative_to(APP).parts)
    )
    digest = hashlib.sha256(b"".join((APP / a).read_bytes() for a in assets)).hexdigest()[:10]
    sw = (ROOT / "src" / "sw.template.js").read_text()
    sw = sw.replace("__CACHE__", f"sheen-{VERSION}-{digest}").replace("__ASSETS__", json.dumps(["./"] + assets))
    (APP / "sw.js").write_text(sw)
    print(f"Built app/ for Sheen {VERSION} ({len(assets)} files, cache {digest})")


if __name__ == "__main__":
    main()
