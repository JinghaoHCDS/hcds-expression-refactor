#!/usr/bin/env python3
"""Build the approved README hero SVG and GIF from one deterministic animation source."""
import argparse
import base64
from functools import lru_cache
from pathlib import Path
import subprocess
import tempfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/readme'
W, H, FPS, DURATION = 1200, 620, 20, 9
PAPER, INK, BLUE, MIST, WHEAT = '#F7F7F4', '#343A46', '#0C91FA', '#BECBEB', '#EBCB75'
FONT = "'PingFang SC', 'Helvetica Neue', sans-serif"


def clamp(v):
    return min(1, max(0, v))


def ease(t, start, end):
    v = clamp((t-start)/(end-start))
    return v*v*(3-2*v)


def fade(t):
    return 1-ease(t, 7.7, 8.7)


def text(x, y, value, size=24, color=INK, weight=400, **attrs):
    attributes = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {attributes}>{escape(value)}</text>'


def path(d, color=INK, width=3, **attrs):
    attributes = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {attributes}/>'


def rect(x,y,w,h,fill,**attrs):
    attributes=' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {attributes}/>'


def svg(body, title, desc, bg=PAPER):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<rect width="{W}" height="{H}" fill="{bg}"/>
<g font-family="{FONT}">{body}</g></svg>'''


@lru_cache(maxsize=1)
def author_mark():
    avatar = base64.b64encode((OUT/'author-avatar.png').read_bytes()).decode('ascii')
    return f'''<defs>
<clipPath id="author-circle"><circle cx="1097" cy="174" r="39"/></clipPath>
<filter id="author-shadow" x="-40%" y="-40%" width="180%" height="190%">
<feGaussianBlur in="SourceAlpha" stdDeviation="3"/><feOffset dy="4"/>
<feComponentTransfer><feFuncA type="linear" slope=".18"/></feComponentTransfer>
<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter></defs>
<circle cx="1097" cy="174" r="41" fill="{PAPER}" filter="url(#author-shadow)"/>
<image x="1058" y="135" width="78" height="78" href="data:image/png;base64,{avatar}" clip-path="url(#author-circle)"/>
''' + text(1038,169,'HCDS',22,INK,700,text_anchor='end') + text(1038,196,'作者 · 制作',15,INK,500,text_anchor='end')


def typeset(t):
    b=text(54,48,'HCDS  /  EXPRESSION REFACTOR',19,INK,700,letter_spacing=1.2)
    # Explicit weight plus a fine matching stroke keeps the headings visibly bold
    # even on systems whose Chinese font family has no 800-weight face.
    b+=text(54,128,'想到哪，说到哪。',59,INK,800,stroke=INK,stroke_width=.65,paint_order='stroke')
    b+=text(54,198,'最后，讲得明明白白。',59,INK,800,stroke=INK,stroke_width=.65,paint_order='stroke')
    b+=text(969,73,'排句',51,BLUE,800,stroke=BLUE,stroke_width=.5,paint_order='stroke')
    b+=text(971,105,'去噪 · 梳理 · 成稿',18,INK,600)
    b+=author_mark()
    b+=text(59,271,'散落的口述',22,INK,600)
    b+=text(712,271,'可以直接念的稿',22,INK,600)
    b+=text(586,271,'去噪',20,INK,600)
    # A real visual barrier: filler text is clipped to its left and never passes.
    b+='<defs><clipPath id="filler-side"><rect x="0" y="290" width="615" height="268"/></clipPath></defs>'
    b+=rect(618,296,6,254,INK,rx=3)
    for yy in range(309,546,18):
        b+=path(f'M610 {yy} H619',INK,2,opacity=.6)
    b+=path('M628 296 H638 M628 550 H638',PAPER,2)
    fragments=[
        ('我真的有点烦。',86,418,-5,712,340),
        ('录了五遍，',83,331,4,712,419),
        ('每次都卡在开头。',274,377,-3,847,419),
        ('后来挑了一遍能讲清楚的，',66,473,2,712,500),
        ('就发了。',369,531,-5,712,535),
    ]
    reset=ease(t,7.7,8.7)
    # Group labels explain the chosen order, rather than just decorating the draft.
    for label,why,y,start in [
        ('感受','先让人共情',306,3.7),
        ('痛点','交代卡在哪里',385,3.1),
        ('办法','给出具体动作',466,3.5),
    ]:
        show=ease(t,start,start+.65)*fade(t)
        b+=text(712,y,label,20,INK,650,opacity=f'{show:.3f}')
        b+=text(778,y,why,17,INK,400,opacity=f'{show*.72:.3f}')
    b+=path('M712 361 H1138 M712 445 H1138',PAPER,1.5,opacity=.75)
    for i,(value,x0,y0,rot,x1,y1) in enumerate(fragments):
        # Clear the two pain-point phrases first, then move the feeling into
        # the opening slot. Separate lanes keep moving text readable.
        start,end=[(2.7,4.1),(.75,1.65),(1.65,2.65),(2.1,3.7),(3.3,4.4)][i]
        a=ease(t,start,end)
        x=x0+(x1-x0)*a; y=y0+(y1-y0)*a
        if i==2:
            x=x0+(x1-x0)*ease(t,1.65,2.25)
            y=y0+(y1-y0)*ease(t,2.25,2.65)
        angle=rot*(1-a)
        b+=text(x0,y0,value,27,INK,400,transform=f'rotate({rot} {x0} {y0})',opacity=f'{a*.30*(1-reset):.3f}')
        if i==0:
            b+=rect(f'{x-5:.2f}',f'{y-28:.2f}',210,35,WHEAT,opacity=f'{1-reset:.3f}',transform=f'rotate({angle:.2f} {x:.2f} {y:.2f})')
        b+=text(f'{x:.2f}',f'{y:.2f}',value,27,INK,500,transform=f'rotate({angle:.2f} {x:.2f} {y:.2f})',opacity=f'{1-reset:.3f}')
        if reset>0:
            if i==0:b+=rect(x0-5,y0-28,210,35,WHEAT,opacity=f'{reset:.3f}',transform=f'rotate({rot} {x0} {y0})')
            b+=text(x0,y0,value,27,INK,500,transform=f'rotate({rot} {x0} {y0})',opacity=f'{reset:.3f}')
    # Only three contextual filler examples: no mechanical forbidden-word list.
    # They approach, stop with an 18px gap at the barrier, then dissolve in place.
    b+='<g clip-path="url(#filler-side)">'
    for word,x0,y0,yy,start in [
        ('嗯嗯',444,324,318,.65),
        ('那个',131,375,395,1.05),
        ('这个',96,529,514,1.55),
    ]:
        a=ease(t,start,start+.9)
        x=x0+(556-x0)*a; y=y0+(yy-y0)*a
        alpha=.55*(1-ease(t,start+1.1,start+1.65))*(1-reset)
        b+=text(f'{x:.2f}',f'{y:.2f}',word,21,INK,400,opacity=f'{alpha:.3f}')
        contact=ease(t,start+.8,start+1.02)*(1-ease(t,start+1.22,start+1.65))*(1-reset)
        b+=path(f'M601 {yy-16} V{yy+3}',WHEAT,4,opacity=f'{contact:.3f}')
        if reset>0:b+=text(x0,y0,word,21,INK,400,opacity=f'{reset*.55:.3f}')
    b+='</g>'
    b+=text(55,589,'删掉口水话，留下你的话。',27,INK,500)
    b+=text(971,589,'口述改写演示',18)
    return svg(b,'想到哪说到哪，最后讲得明明白白','三个无意义口头填充示例“嗯嗯、那个、这个”被中间挡板截住并淡出；有效内容通过后，按感受、痛点、办法归位，并解释每段的作用。',MIST)

def run(module):
    name = "hero"
    draw = typeset
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/f'{name}.svg').write_text(draw(5.6),encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix=f'hcds-{name}-') as tmp:
        work=Path(tmp);svgs=work/'svg';pngs=work/'png';svgs.mkdir()
        for i in range(FPS*DURATION):
            (svgs/f'frame-{i:04d}.svg').write_text(draw(i/FPS),encoding='utf-8')
        subprocess.run(['node',str(ROOT/'scripts/readme/render_svg_frames.cjs'),module,str(svgs),str(pngs)],check=True)
        # Global palette, no dithering; stable flat areas compress cleanly.
        common=['ffmpeg','-v','error','-y','-framerate',str(FPS),'-i',str(pngs/'frame-%04d.png')]
        subprocess.run(common+['-vf','palettegen=max_colors=256:stats_mode=full','-frames:v','1',str(work/'palette.png')],check=True)
        subprocess.run(common+['-i',str(work/'palette.png'),'-lavfi','paletteuse=dither=none:diff_mode=rectangle','-loop','0',str(OUT/f'{name}.gif')],check=True)
    print(f'{name}: {(OUT/f"{name}.gif").stat().st_size/1024:.0f} KB',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer-module',required=True,help='Absolute path to installed @resvg/resvg-js module')
    args=parser.parse_args()
    run(args.renderer_module)
