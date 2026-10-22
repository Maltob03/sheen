"""Build the self-hosted page from src/codeshot.html.

src/codeshot.html is written as a page body (the form the Claude artifact uses).
This wraps it in a full document and points highlight.js at the vendored copy,
so the app works on a home server with no internet access.

    python3 src/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>'
LOCAL = '<script src="vendor/highlight.min.js"></script>'

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""

body = (ROOT / "src" / "codeshot.html").read_text()
if CDN not in body:
    raise SystemExit("highlight.js script tag not found in src/codeshot.html")
out = ROOT / "app" / "index.html"
out.write_text(HEAD + body.replace(CDN, LOCAL) + "\n</body>\n</html>\n")
print(f"wrote {out.relative_to(ROOT)}")
