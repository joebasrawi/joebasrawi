import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SRC, OUT = sys.argv[1], sys.argv[2]

def outline(text, wght, size, x0, baseline, tracking=0.0):
    f = instantiateVariableFont(TTFont(SRC), {"wght": wght})
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    scale = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    x = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + x, baseline)))
        x += hmtx[g][0] * scale + tracking * size
    return pen.getCommands(), x - tracking * size

W, H = 1200, 210
name, nw = outline("Joe Basrawi", 800, 92, 0, 0, -0.05)
tag, tw = outline("CO-FOUNDER  /  BUILDER  /  HOUSE MUSIC PRODUCER", 500, 15, 0, 0, 0.22)
nx = (W - nw) / 2; tx = (W - tw) / 2

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Joe Basrawi: co-founder, builder, house music producer">
<style>
.b{{transform-box:fill-box;transform-origin:center;mix-blend-mode:screen}}
.b1{{animation:d1 14s ease-in-out infinite alternate}}
.b2{{animation:d2 17s ease-in-out infinite alternate}}
.b3{{animation:d3 20s ease-in-out infinite alternate}}
@keyframes d1{{to{{transform:translate(260px,40px) scale(1.25)}}}}
@keyframes d2{{to{{transform:translate(-300px,-30px) scale(.85)}}}}
@keyframes d3{{to{{transform:translate(180px,-50px) scale(1.2)}}}}
.n{{animation:rise .9s cubic-bezier(.2,.9,.2,1.2) both}}
.t{{animation:fade 1.2s .5s both}}
@keyframes rise{{from{{opacity:0;transform:translateY(24px)}}}}
@keyframes fade{{from{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
<radialGradient id="g1"><stop offset="0" stop-color="#3d1cff"/><stop offset="1" stop-color="#3d1cff" stop-opacity="0"/></radialGradient>
<radialGradient id="g2"><stop offset="0" stop-color="#ff3df5"/><stop offset="1" stop-color="#ff3df5" stop-opacity="0"/></radialGradient>
<radialGradient id="g3"><stop offset="0" stop-color="#00c2a8"/><stop offset="1" stop-color="#00c2a8" stop-opacity="0"/></radialGradient>
<linearGradient id="ink" gradientUnits="userSpaceOnUse" spreadMethod="reflect" x1="0" x2="{nw:.0f}" y1="0" y2="0">
<stop offset="0" stop-color="#d4ff3a"/><stop offset=".5" stop-color="#3dfcff"/><stop offset="1" stop-color="#ff3df5"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{2*nw:.0f} 0" dur="9s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="#07040f"/>
<g opacity=".55">
<ellipse class="b b1" cx="180" cy="40" rx="360" ry="200" fill="url(#g1)"/>
<ellipse class="b b2" cx="1000" cy="120" rx="380" ry="210" fill="url(#g2)" opacity=".7"/>
<ellipse class="b b3" cx="560" cy="250" rx="340" ry="170" fill="url(#g3)" opacity=".6"/>
</g>
<g class="n"><path transform="translate({nx:.1f} 122)" fill="url(#ink)" d="{name}"/></g>
<g class="t"><path transform="translate({tx:.1f} 168)" fill="#9a90b8" d="{tag}"/></g>
</g>
</svg>
'''
open(OUT, "w").write(svg)
print(len(svg), "bytes")
