"""Branded project cards for the GitHub profile, one SVG per project.
Text is outlined to paths (SVGs shown through <img> can't load fonts), logos are inlined."""
import base64, re, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SITE = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
FONTS = SITE / "public/fonts"
FONTFILE = {"Inter": "inter-bec94a4d.woff2", "Montserrat": "montserrat-83a31c81.woff2", "Source Sans 3": "source-sans-3-e6c9ca63.woff2",
            "Manrope": "manrope-f2edea8e.woff2", "DM Sans": "dm-sans-f71cbe2c.woff2", "Bricolage Grotesque": "bricolage-grotesque-2ec2ef37.woff2",
            "Nunito": "nunito-57f464a4.woff2", "Fraunces": "fraunces-9e509503.woff2", "Unbounded": "unbounded-10e743c6.woff2"}
_cache = {}
def font(family, wght):
    key = (family, wght)
    if key not in _cache:
        f = TTFont(FONTS / FONTFILE[family])
        if "fvar" in f:
            axes = {a.axisTag: a for a in f["fvar"].axes}
            loc = {"wght": max(axes["wght"].minValue, min(axes["wght"].maxValue, wght))}
            if "opsz" in axes: loc["opsz"] = axes["opsz"].maxValue
            for t, a in axes.items():
                if t not in loc: loc[t] = a.defaultValue
            f = instantiateVariableFont(f, loc)
        _cache[key] = f
    return _cache[key]

def width(text, family, wght, size, track=0):
    f = font(family, wght); cmap, hmtx = f.getBestCmap(), f["hmtx"]; s = size / f["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] * s + track * size for c in text) - track * size

def path(text, family, wght, size, x, y, track=0):
    f = font(family, wght); gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]; s = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip(".")); cx = x
    for c in text:
        g = cmap.get(ord(c), cmap[ord("?")])
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y))); cx += hmtx[g][0] * s + track * size
    return pen.getCommands()

def wrap(text, family, wght, size, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if width(t, family, wght, size) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def front(md):
    fm = md.split("---")[1]
    get = lambda k, src=fm: (re.search(rf'^\s*{k}:\s*"?(.*?)"?\s*$', src, re.M) or [None, ""])[1]
    theme = fm[fm.index("theme:"):]
    return get("name"), get("tagline"), get("role"), get("status"), {k: get(k, theme) for k in ("bg", "surface", "text", "muted", "line", "accent", "accent2", "accent3")}

STAGE = {"idea": "Just started", "building": "Building", "beta": "Beta", "shipped": "Live"}
# slug: (display family, display weight, body family, logo file or None, wide wordmark?)
P = {"flow": ("Inter", 700, "Inter", "flow.svg", False),
     "campaign-baby": ("Montserrat", 900, "Inter", "campaign-baby.svg", False),
     "opid": ("Source Sans 3", 800, "Source Sans 3", "opid-icon.png", False),
     "resonant": ("Manrope", 800, "DM Sans", None, False),
     "auditbaby": ("Bricolage Grotesque", 800, "Inter", "auditbaby.svg", False),
     "crosslist": ("Nunito", 900, "Nunito", "crosslist.svg", False),
     "big-spoon": ("Fraunces", 800, "DM Sans", "big-spoon.png", True)}

W, H, PAD = 600, 240, 32
for slug, (dfam, dw, bfam, logo, wide) in P.items():
    name, tagline, role, status, t = front((SITE / f"src/content/projects/{slug}.md").read_text())
    g = []
    # logo
    if logo:
        lp = OUT / "_src" / logo
        data = base64.b64encode(lp.read_bytes()).decode()
        mime = "image/svg+xml" if logo.endswith(".svg") else "image/png"
        if wide: g.append(f'<image href="data:{mime};base64,{data}" x="{PAD}" y="{PAD}" height="44" width="237"/>')
        else: g.append(f'<image href="data:{mime};base64,{data}" x="{PAD}" y="{PAD}" width="44" height="44"/>')
    else:
        g.append(f'<rect x="{PAD}" y="{PAD}" width="44" height="44" rx="12" fill="{t["accent"]}"/>')
        g.append(f'<path fill="{t["bg"]}" d="{path(name[0], dfam, 800, 26, 0, 0)}" transform="translate({PAD + 22 - width(name[0], dfam, 800, 26)/2:.1f} {PAD + 32})"/>')
    # name (wordmark logos already say the name)
    tx = PAD + 60
    if not wide:
        g.append(f'<path fill="{t["text"]}" d="{path(name, dfam, dw, 30, tx, PAD + 33, -0.02)}"/>')
    # status pill, top right
    st = STAGE.get(status, status); sw = width(st, bfam, 700, 13) + 24
    g.append(f'<rect x="{W - PAD - sw:.1f}" y="{PAD + 9}" width="{sw:.1f}" height="26" rx="13" fill="{t["accent"]}"/>')
    g.append(f'<path fill="{t["bg"]}" d="{path(st, bfam, 700, 13, W - PAD - sw + 12, PAD + 27)}"/>')
    # tagline
    y = PAD + 96
    for line in wrap(tagline, bfam, 400, 18, W - 2 * PAD)[:3]:
        g.append(f'<path fill="{t["text"]}" fill-opacity=".86" d="{path(line, bfam, 400, 18, PAD, y)}"/>'); y += 27
    # role
    g.append(f'<path fill="{t["muted"]}" d="{path(role.upper(), bfam, 600, 11.5, PAD, H - PAD + 4, 0.12)}"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{name}: {tagline}">
<defs><radialGradient id="glow"><stop offset="0" stop-color="{t["accent2"]}" stop-opacity=".45"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>
<circle cx="{W - 40}" cy="{H + 10}" r="190" fill="url(#glow)"/>
<rect x="0" y="0" width="6" height="{H}" fill="{t["accent"]}"/>
{chr(10).join(g)}
</g><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="21.5" fill="none" stroke="{t["text"]}" stroke-opacity=".12"/>
</svg>
'''
    (OUT / f"{slug}.svg").write_text(svg)
    print(slug, len(svg))
