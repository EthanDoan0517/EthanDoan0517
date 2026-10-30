"""Resolution-independent README assets. No scripts, external fonts or bitmaps.

Consolas glyph outlines preserve the existing artwork across platforms. SVG
SMIL animates shared geometry continuously; all lighting stays in screen space.
"""
import json, math, re
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import numpy as np
import build_panel as b


def fmt(v): return f'{float(v):.6f}'.rstrip('0').rstrip('.') or '0'


class Drawing:
    def __init__(self, cfg, animated=True, phase=0):
        self.cfg=cfg; self.animated=animated; self.phase=phase
        self.defs=[]; self.glyphs={}; self.fonts={}

    def text(self, rows):
        result=[]
        for x,y,words,size,kind,color in rows:
            key=b.FONT_FILES[kind]
            if key not in self.fonts: self.fonts[key]=TTFont(b.FONT_ROOT/key)
            font=self.fonts[key]; gs=font.getGlyphSet(); cmap=font.getBestCmap()
            scale=size/font['head'].unitsPerEm
            bounds=[]
            for c in words:
                pen=BoundsPen(gs); gs[cmap[ord(c)]].draw(pen)
                bounds.append(pen.bounds)
            top=max(box[3] for box in bounds if box)
            left=next(box[0] for box in bounds if box)
            baseline=y+top*scale
            for offset,part,run_color in b.text_runs(words,size,kind,color):
                advance=0
                for c in part:
                    name=cmap[ord(c)]; gid=(key,name)
                    if gid not in self.glyphs:
                        ident=f'g{len(self.glyphs)}'; self.glyphs[gid]=ident
                        pen=SVGPathPen(gs); gs[name].draw(pen)
                        self.defs.append(f'<path id="{ident}" d="{pen.getCommands()}"/>')
                    result.append(f'<use href="#{self.glyphs[gid]}" fill="{run_color}" transform="translate({fmt(x-left*scale+offset+advance*scale)} {fmt(baseline)}) scale({str(scale)} -{str(scale)})"/>')
                    advance+=font['hmtx'][name][0]
        return ''.join(result)

    def shift(self):
        if not self.animated: return ''
        return '<animateTransform attributeName="transform" type="translate" from="0 0" to="-320 0" dur="3.2s" repeatCount="indefinite"/>'

    def smooth_gradient(self, ident, x1, x2, inverse=False, diagonal=False):
        stops=''.join(f'<stop offset="{i/16}" stop-color="white" stop-opacity="{fmt(1-(i/16)**2*(3-2*i/16) if inverse else (i/16)**2*(3-2*i/16))}"/>' for i in range(17))
        self.defs.append(f'<linearGradient id="{ident}" gradientUnits="userSpaceOnUse" x1="{x1}" x2="{x2}" y1="0" y2="0"'+(' gradientTransform="matrix(1 0 .04 1 0 0)"' if diagonal else '')+f'>{stops}</linearGradient>')

    def signal(self):
        c=self.cfg; w=c['width']; h=c['height']; mid=c['grid_middle']; top=c['grid_top']; bottom=top+256; ex=c['entry_x']; base=c['baselines'][0]
        mobile=c['mobile']; shift=self.phase*100
        # Only the trace's left fade moves toward the words. Grid/blue field stay put.
        self.smooth_gradient('wave-left',24 if mobile else 548,72 if mobile else 628,diagonal=not mobile)
        self.smooth_gradient('field-left',24 if mobile else 610,72 if mobile else 702,diagonal=not mobile)
        self.smooth_gradient('right',w-72 if mobile else w-70,w-24 if mobile else w,inverse=True)
        vstops=[]
        for i in range(17):
            t=i/16; alpha=t*t*(3-2*t)
            vstops.append(f'<stop offset="{fmt(20*t/256)}" stop-color="white" stop-opacity="{fmt(alpha)}"/>')
        for i in range(17):
            t=i/16; alpha=1-t*t*(3-2*t)
            vstops.append(f'<stop offset="{fmt((236+20*t)/256)}" stop-color="white" stop-opacity="{fmt(alpha)}"/>')
        self.defs.append(f'<linearGradient id="vertical" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{top}" y2="{bottom}">{"".join(vstops)}</linearGradient>')
        for ident,fill in [('vl','vertical'),('wr','right'),('wl','wave-left'),('fl','field-left')]:
            self.defs.append(f'<mask id="{ident}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#{fill})"/></mask>')
        cx,cy,rx,ry=(470,390,235,145) if mobile else (932,158,245,185)
        stops=''.join(f'<stop offset="{i/24}" stop-color="#0c1322" stop-opacity="{fmt(math.exp(-2*(i/24*2.5)**2))}"/>' for i in range(25))
        self.defs.append(f'<radialGradient id="blue" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" gradientTransform="translate({cx} {cy}) scale({rx*2.5} {ry*2.5})">{stops}</radialGradient>')
        light=''.join(f'<stop offset="{i/24}" stop-color="white" stop-opacity="{fmt((.35+2.65*math.exp(-2*(i/24*2.5)**2))/3)}"/>' for i in range(25))
        self.defs.append(f'<radialGradient id="grid-light" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" gradientTransform="translate({cx} {cy}) scale({rx*2.5} {ry*2.5})">{light}</radialGradient><mask id="gl"><rect width="{w}" height="{h}" fill="url(#grid-light)"/></mask>')
        # Sparse moving grid paths, at exactly the same speed and phase as the ECG.
        grid=[]
        for major in (False,True):
            pitch=80 if major else 16
            coords=[f'M {x} {top} V {bottom}' for x in range(-320,w+641,pitch)]
            coords += [f'M -320 {y} H {w+640}' for y in np.arange(mid-128,mid+129,16) if not major or round(y-mid)%80==0]
            grid.append(f'<path d="{" ".join(coords)}" stroke="#526b9b" stroke-opacity="{.077 if major else .102}" stroke-width="1"/>')
        xs=b.sample_x(-320,w+640,.7); ys=base+b.wave(xs)
        path='M '+' L '.join(f'{fmt(x)} {fmt(y)}' for x,y in zip(xs,ys))
        self.defs.append(f'<path id="wave" d="{path}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        self.defs.append(f'<clipPath id="entry"><rect x="-10" y="0" width="{ex+10}" height="{h}"/></clipPath>')
        self.defs.append(f'<linearGradient id="mint" gradientUnits="userSpaceOnUse" x1="{ex-48}" x2="{ex}" y1="0" y2="0" gradientTransform="translate({fmt(shift)} 0)">{chr(60)+'animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="320 0" dur="3.2s" repeatCount="indefinite"/'+chr(62) if self.animated else ""}<stop stop-color="#46ed79"/><stop offset=".5" stop-color="#7af6a3"/><stop offset="1" stop-color="#aeffcd"/></linearGradient>')
        for ident,std in [('soft',2),('wide',6)]:
            self.defs.append(f'<filter id="{ident}" x="-20%" y="-100%" width="140%" height="300%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{std}"/></filter>')
        moving=f'<g class="moving-trace" transform="translate({fmt(-shift)} 0)">{self.shift()}<use href="#wave" stroke="url(#mint)" stroke-width="1.5"/></g>'
        # Inverse gradient translation cancels the path translation, keeping mint
        # fixed at the right edge without rasterizing an animated luminance mask.
        trace=f'<g clip-path="url(#entry)">{moving}</g>'
        layers=f'<g opacity=".11" filter="url(#wide)">{trace}</g><g opacity=".23" filter="url(#soft)">{trace}</g><g opacity=".74">{trace}</g>'
        # Matching breakpoints ensure the star follows the very same polyline.
        sx=b.sample_x(ex,ex+320,.7); sx=np.unique(np.round(np.r_[ex,sx[(sx>ex)&(sx<ex+320)],ex+320],6)); sy=base+b.wave(sx)
        motion=''
        if self.animated:
            vals=';'.join(f'{ex} {fmt(y)}' for y in sy)
            times=';'.join(fmt((x-ex)/320) for x in sx)
            motion=f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{times}" dur="3.2s" calcMode="linear" repeatCount="indefinite"/>'
        self.defs.append('<radialGradient id="star-halo"><stop stop-color="#41e178" stop-opacity=".3"/><stop offset="1" stop-color="#41e178" stop-opacity="0"/></radialGradient><radialGradient id="ray"><stop stop-color="#d4ffe4" stop-opacity=".85"/><stop offset="1" stop-color="#b9ffd8" stop-opacity="0"/></radialGradient>')
        star=f'<g transform="translate({ex} {fmt(base+b.wave(ex+shift))})">{motion}<circle r="11" fill="url(#star-halo)"/><ellipse rx="7" ry=".8" fill="url(#ray)"/><ellipse rx=".8" ry="8" fill="url(#ray)"/><circle r="1.05" fill="#d4ffe4"/></g>'
        return f'<g mask="url(#fl)"><rect width="{w}" height="{h}" fill="url(#blue)" style="mix-blend-mode:screen"/></g><g mask="url(#vl)"><g mask="url(#wr)"><g mask="url(#fl)"><g mask="url(#gl)"><g transform="translate({fmt(-shift)} 0)" fill="none">{self.shift()}{"".join(grid)}</g></g></g><g mask="url(#wl)">{layers}{star}</g></g></g>'

    def icon(self,x,y,kind):
        result=[]; scale=1 if self.cfg['mobile'] else .75
        for shape,co,r in b.icon_shapes(kind):
            if shape=='rect':
                x1,y1,x2,y2=co; s=f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="{r}"/>'
            elif shape=='ellipse':
                x1,y1,x2,y2=co; s=f'<ellipse cx="{(x1+x2)/2}" cy="{(y1+y2)/2}" rx="{(x2-x1)/2}" ry="{(y2-y1)/2}"/>'
            else: s=f'<polyline points="{" ".join(str(v) for v in co)}"/>'
            result.append(s)
        return f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{b.GREEN}" stroke-width="{2/scale}" stroke-linejoin="round">{"".join(result)}</g>'

    def cards(self,index=None):
        self.defs.append('<linearGradient id="glass" x2="0" y2="1"><stop stop-color="#0f1619"/><stop offset=".45" stop-color="#0d1216"/><stop offset="1" stop-color="#0d1216"/></linearGradient><linearGradient id="rim" x2="1" y2="1"><stop stop-color="#2a3b34"/><stop offset="1" stop-color="#202c28"/></linearGradient><radialGradient id="status"><stop stop-color="#46ed79" stop-opacity=".25"/><stop offset="1" stop-color="#46ed79" stop-opacity="0"/></radialGradient>')
        result=[]
        for i,(x1,y1,x2,y2) in enumerate(self.cfg['cards']):
            if index is not None and i!=index: continue
            result.append(f'<rect x="{x1+1}" y="{y1+1}" width="{x2-x1-2}" height="{y2-y1-2}" rx="24" fill="url(#glass)" stroke="url(#rim)"/>')
            result.append(self.text([r for r in self.cfg['text'] if x1<=r[0]<x2 and y1<=r[1]<y2]))
            result.append(self.icon(*self.cfg['icons'][i]))
            a,by,c,d=self.cfg['card_rules'][i]
            result.append(f'<path d="M {a} {by} H {c}" stroke="#242f34"/>')
            dx,dy=self.cfg['dots'][i];radius=5 if self.cfg['mobile'] else 3
            pulse='<animate attributeName="opacity" values=".48;1;.48" dur="4s" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1" repeatCount="indefinite"/>' if self.animated else ''
            result.append(f'<circle cx="{dx}" cy="{dy}" r="12" fill="url(#status)" opacity=".48">{pulse}</circle><circle cx="{dx}" cy="{dy}" r="{radius}" fill="{b.GREEN}"/>')
        return ''.join(result)

    def render(self,kind='hero',index=None):
        c=self.cfg;w=c['width'];h=c['height'];x=0;y=0
        if kind=='card':
            x,y,x2,y2=c['cards'][index];w=x2-x;h=y2-y;body=self.cards(index)
        else:
            if kind=='hero': h=c['cards'][0][1]-16
            body=f'<rect width="{w}" height="{h}" rx="20" fill="#0b0f13"/>'+self.signal()
            for i,(x1,y1,x2,y2) in enumerate(c['dividers']):
                body+=f'<path d="M {x1} {y1} H {x2}" stroke="{"#314a3b" if i==0 else b.BORDER}"/>'
                if i==0: body+=f'<path d="M {x1} {y1} h 84" stroke="{b.GREEN}" stroke-width="2"/>'
            body+=self.text([r for r in c['text'] if r[1]<c['cards'][0][1]])
            if kind=='profile':body+=self.cards()
            self.defs.append(f'<clipPath id="outer"><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="20"/></clipPath>')
            body=f'<g clip-path="url(#outer)">{body}</g><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20" fill="none" stroke="#303c43"/>'
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}"><title>Ethan Doan — {kind}</title><desc>Synthetic lead-II ECG illustration: represented 75 bpm, quarter-speed playback. Accessible text is in the README.</desc><defs>{"".join(self.defs)}</defs>{body}</svg>'


def build():
    for mobile in (False,True):
        variant='mobile' if mobile else 'desktop'; cfg=b.layout(mobile)
        for animated in (True,False):
            suffix='' if animated else '-still'
            outputs=[(f'hero-{variant}{suffix}','hero',None)]
            outputs += [(f'card-{name}-{variant}{suffix}','card',i) for i,name in enumerate(('skindex','protist'))]
            if not animated: outputs.append((f'profile-{variant}-still','profile',None))
            for name,kind,index in outputs:
                path=b.OUT/(name+'.svg');path.write_text(Drawing(cfg,animated).render(kind,index),encoding='utf-8')
                print(name,path.stat().st_size)
        for phase in (0,.32,.64,.96,1.28,1.6,1.92,2.24,2.56,2.88,3.199,3.2):
            (b.QA/f'sharp-{variant}-{phase}.svg').write_text(Drawing(cfg,False,phase%3.2).render(),encoding='utf-8')


if __name__=='__main__': build()
