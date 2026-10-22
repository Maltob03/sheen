"""Print the color themes bundled with Xcode as the JSON array Sheen embeds.

Run on a Mac with Xcode installed, then paste the output over XCODE_THEMES in
src/sheen.html:

    python3 src/extract_themes.py > themes.json
"""
import glob
import json
import os
import plistlib

FRAMEWORKS = "/Applications/Xcode.app/Contents/SharedFrameworks/"
CLASSIC = FRAMEWORKS + "DVTUserInterfaceKit.framework/Versions/A/Resources/FontAndColorThemes/*.xccolortheme"
# Newer copies of the Default themes live in the source editor framework.
NEWER = FRAMEWORKS + "SourceEditor.framework/Versions/A/Resources/*.xccolortheme"

TOKENS = {
    "plain": "plain", "comment": "comment", "comment.doc": "doc", "comment.doc.keyword": "docKeyword",
    "mark": "mark", "string": "string", "character": "character", "number": "number", "keyword": "keyword",
    "preprocessor": "preprocessor", "url": "url", "attribute": "attribute", "regex": "regex",
    "declaration.type": "declType", "declaration.other": "declOther",
    "identifier.class": "projClass", "identifier.type": "projType", "identifier.function": "projFunc",
    "identifier.constant": "projConst", "identifier.variable": "projVar", "identifier.macro": "projMacro",
    "identifier.class.system": "sysClass", "identifier.type.system": "sysType",
    "identifier.function.system": "sysFunc", "identifier.constant.system": "sysConst",
    "identifier.variable.system": "sysVar", "identifier.macro.system": "sysMacro",
}


def hex_color(value: str) -> str:
    parts = [float(x) for x in value.split()]
    r, g, b = (round(max(0.0, min(1.0, v)) * 255) for v in parts[:3])
    alpha = parts[3] if len(parts) > 3 else 1.0
    out = f"#{r:02x}{g:02x}{b:02x}"
    return out + f"{round(alpha * 255):02x}" if alpha < 0.999 else out


def main() -> None:
    newer = {os.path.basename(p): p for p in glob.glob(NEWER)}
    themes = []
    for path in sorted(glob.glob(CLASSIC)):
        name = os.path.basename(path)
        with open(newer.get(name, path), "rb") as f:
            d = plistlib.load(f)
        colors, fonts = d["DVTSourceTextSyntaxColors"], d.get("DVTSourceTextSyntaxFonts", {})
        theme = {
            "name": name.removesuffix(".xccolortheme"),
            "bg": hex_color(d["DVTSourceTextBackground"]),
            "sel": hex_color(d.get("DVTSourceTextSelectionColor", "0.64 0.8 1 1")),
            "line": hex_color(d.get("DVTSourceTextCurrentLineHighlightColor", "0 0 0 0")),
            "cursor": hex_color(d.get("DVTSourceTextInsertionPointColor", "0 0 0 1")),
            "c": {}, "bold": [], "italic": [],
            "font": fonts.get("xcode.syntax.plain", "SFMono-Regular - 12.0"),
        }
        for key, value in colors.items():
            token = TOKENS.get(key.removeprefix("xcode.syntax."))
            if not token:
                continue
            theme["c"][token] = hex_color(value)
            font = fonts.get(key, "")
            if "Bold" in font or "Heavy" in font:
                theme["bold"].append(token)
            if "Italic" in font or "Oblique" in font:
                theme["italic"].append(token)
        themes.append(theme)
    print(json.dumps(themes, separators=(",", ":")))


if __name__ == "__main__":
    main()
