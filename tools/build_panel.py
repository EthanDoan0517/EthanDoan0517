"""Original profile: one EKG moves left; fixed status dots breathe gently.

Run with Python 3 + Pillow + NumPy. Text/layout/colors are editable below.
Exported SVGs keep foreground text and waveform paths editable. No network use.
"""
from pathlib import Path
from html import escape
from base64 import b64encode
import io, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets'
SOURCE = ROOT/'source'
QA = ROOT/'preview'
for directory in (OUT, SOURCE, QA): directory.mkdir(exist_ok=True)
BG = (11, 15, 19)
TEXT = '#e6edf0'
MUTED = '#a6b3b9'
GREEN = '#6edb96'
BORDER = '#2b373d'
# Display magnification is uniform: one logical millimeter is a 16px square.
GRID_CELL = 16
GRID_ROWS = 16
RR_SECONDS = .8
PX_PER_SECOND = GRID_CELL / .04
PX_PER_MV = GRID_CELL / .1
BEAT = 20 * GRID_CELL
PATTERN_COUNT = 1
# Quarter-speed presentation: keep ECG-paper geometry independent of playback.
FRAMES, MS, PERIOD = 160, 20, BEAT
PLAYBACK_PX_PER_SECOND = PERIOD / (FRAMES * MS / 1000)
PLAYBACK_SPEED = PLAYBACK_PX_PER_SECOND / PX_PER_SECOND
NAME_SPACE_REDUCTION = 4
FONT_ROOT = Path(os.environ.get('PROFILE_FONT_DIR', 'C:/Windows/Fonts'))
FONT_FILES = {'sans':'consola.ttf', 'bold':'consolab.ttf', 'mono':'consola.ttf'}


def layout(mobile=False):
    """Text x values are visible ink edges, not font advance-box origins."""
    if not mobile:
        w,h=1200,610
        text=[
            (60,38,'Ethan Doan',44,'bold',TEXT),
            (60,94,'Pre-med @ William & Mary · Chemistry',18,'mono',MUTED),
            (60,166,'interests',18,'mono',MUTED),
            (204,167,'Medicine · Molecular & cell biology',16,'mono',TEXT),
            (60,204,'research',18,'mono',MUTED),
            (204,205,'Transcriptomics · RNA-seq',16,'mono',TEXT),
            (60,242,'tools',18,'mono',MUTED),
            (204,243,'R · Python · Git',16,'mono',TEXT),
            (60,303,'PROJECTS',15,'mono',GREEN),
            (88,438,'Skindex',27,'bold',TEXT),
            (88,492,'An educational skin-image library',17,'mono',TEXT),
            (88,522,'with photo interpretation tools.',17,'mono',TEXT),
            (88,558,'Not for medical diagnosis.',16,'mono',MUTED),
            (118,608,'in development',16,'mono',MUTED),
            (644,438,'Protist Atlas',27,'bold',TEXT),
            (644,492,'An interactive atlas of protist life.',17,'mono',TEXT),
            (644,522,'Browse lineages, traits & habitats.',17,'mono',TEXT),
            (644,558,'Source-linked profiles & images.',16,'mono',MUTED),
            (674,608,'planned',16,'mono',MUTED),
        ]
        cards=[(60,406,584,636),(616,406,1140,636)]
        dividers=[(60,146,1140,146),(60,282,1140,282)]
        icons=[(508,432,'skindex'),(1064,432,'protist')]
        dots=[(92,615),(648,615)]
        card_rules=[(88,589,556,589),(644,589,1112,589)]
    else:
        w,h=720,1970
        text=[
            (48,52,'Ethan Doan',76,'bold',TEXT),
            (48,164,'Pre-med @ William & Mary',34,'mono',MUTED),
            (48,210,'Chemistry undergraduate',34,'mono',MUTED),
            (48,552,'interests',34,'mono',GREEN),
            (48,600,'Medicine · Molecular &',32,'mono',TEXT),
            (48,640,'cell biology',32,'mono',TEXT),
            (48,714,'research',34,'mono',GREEN),
            (48,762,'Transcriptomics · RNA-seq',32,'mono',TEXT),
            (48,836,'tools',34,'mono',GREEN),
            (48,884,'R · Python · Git',32,'mono',TEXT),
            (48,986,'PROJECTS',32,'mono',GREEN),
            (78,1340,'Skindex',48,'bold',TEXT),
            (78,1426,'An educational skin-image',33,'mono',TEXT),
            (78,1470,'library with photo',33,'mono',TEXT),
            (78,1514,'interpretation tools.',33,'mono',TEXT),
            (78,1573,'Not for medical diagnosis.',33,'mono',MUTED),
            (110,1658,'in development',34,'mono',MUTED),
            (78,1790,'Protist Atlas',46,'bold',TEXT),
            (78,1876,'An interactive atlas of',33,'mono',TEXT),
            (78,1920,'protist life. Browse lineages,',33,'mono',TEXT),
            (78,1964,'traits & habitats.',33,'mono',TEXT),
            (78,2023,'Source-linked profiles & images.',32,'mono',MUTED),
            (110,2108,'planned',34,'mono',MUTED),
        ]
        # Balanced cards share the same height and text rhythm.
        cards=[(48,1288,672,1710),(48,1738,672,2160)]
        icons=[(566,1320,'skindex'),(566,1770,'protist')]
        dots=[(84,1675),(84,2125)]
        card_rules=[(78,1632,642,1632),(78,2082,642,2082)]
        dividers=[(48,392,672,392),(48,520,672,520),(48,944,672,944)]
    # Move the project section as a unit; its internal artwork is unchanged.
    card_top=cards[0][1]
    lift=232 if mobile else 52
    text=[(x,y-lift if y>=card_top else y,words,size,kind,color)
          for x,y,words,size,kind,color in text]
    cards=[(x1,y1-lift,x2,y2-lift) for x1,y1,x2,y2 in cards]
    icons=[(x,y-lift,kind) for x,y,kind in icons]
    dots=[(x,y-lift) for x,y in dots]
    card_rules=[(x1,y1-lift,x2,y2-lift) for x1,y1,x2,y2 in card_rules]
    baselines=[448 if mobile else 218]
    return dict(width=w,height=h,text=text,cards=cards,dividers=dividers,
                baselines=baselines,mobile=mobile,icons=icons,dots=dots,
                card_rules=card_rules,amplitude=1,
                grid_top=dividers[0][1]-GRID_ROWS*GRID_CELL/2,
                grid_middle=dividers[0][1],entry_x=w-72)


def text_runs(words,size,kind,color,scale=1):
    """Tiny optical word-space adjustment and one restrained header accent."""
    ft=font(size,kind,scale)
    if words=='Ethan Doan':
        return [(0,'Ethan',color),(ft.getlength('Ethan ')-NAME_SPACE_REDUCTION*scale,'Doan',color)]
    if words.startswith('Pre-med'):
        return [(0,'Pre-med',GREEN),(ft.getlength('Pre-med'),words[7:],color)]
    return [(0,words,color)]


def font(size,kind,scale=1):
    return ImageFont.truetype(str(FONT_ROOT/FONT_FILES[kind]),round(size*scale))


def ink_offset(words,size,kind,scale=1):
    """Optically align the first visible ink pixel, including the large E."""
    ft=font(size,kind,scale)
    tmp=Image.new('L',(int(ft.getlength(words))+size*scale+8,size*scale*2))
    ImageDraw.Draw(tmp).text((0,0),words,font=ft,anchor='lt',fill=255)
    return tmp.getbbox()[0]


def icon_shapes(kind):
    """Original 64px vector drawings, shared by raster and editable SVG exports."""
    if kind=='skindex':
        return [('rect',(9,5,57,49),10),('rect',(4,12,52,57),10),
                ('ellipse',(17,25,39,45),0),('ellipse',(22,29,26,33),0),
                ('ellipse',(30,35,34,39),0)]
    return [('ellipse',(4,11,43,55),0),('ellipse',(17,25,29,39),0),
            ('line',(43,33,54,33,54,12,63,12),0),
            ('line',(54,33,54,53,63,53),0),
            ('ellipse',(59,8,64,15),0),('ellipse',(59,49,64,56),0)]


def glass_card(size):
    """Stationary dark optical surface: translucent tint, edge light and reflection."""
    w,h=size
    yy,xx=np.mgrid[0:h,0:w]
    u=xx/w;v=yy/h
    sheen=np.exp(-v*7)
    arr=np.zeros((h,w,4),np.uint8)
    for c,base in enumerate((13,18,22)):
        arr[:,:,c]=np.uint8(base+sheen*(2,4,3)[c])
    arr[:,:,3]=250
    material=Image.fromarray(arr)
    mask=Image.new('L',size);d=ImageDraw.Draw(mask)
    d.rounded_rectangle((0,0,w-1,h-1),radius=23,fill=255)
    material.putalpha(Image.fromarray(np.minimum(np.asarray(material)[:,:,3],np.asarray(mask))))
    d=ImageDraw.Draw(material)
    d.rounded_rectangle((0,0,w-1,h-1),radius=23,outline=(94,129,113,110),width=1)
    d.rounded_rectangle((2,2,w-3,h-3),radius=21,outline=(117,164,142,25),width=1)
    # Delicate upper rim and inner lower rim, with deliberately different weights.
    for x in range(23,w-23):
        a=int(115*(1-x/w)**1.5)
        d.point((x,0),fill=(163,214,184,a))
        d.point((x,h-2),fill=(70,107,91,int(25*x/w)))
    return material


def millivolts(seconds):
    """Representative synthetic lead II, not a patient recording.

    P +.15mV / 100ms; PR 160ms; Q -.08, R +1.0, S -.20mV;
    QRS 80ms; isoelectric ST 40ms; asymmetric upright T +.30mV;
    QT 360ms (Bazett QTc 402ms). Identical sinus beats every 800ms.
    Sources and amplitude rationale: source/ECG-NOTES.md.
    """
    t=np.asarray(seconds) % RR_SECONDS
    def lobe(start,peak,end):
        phase=np.where(t<=peak,(t-start)/(peak-start),(t-peak)/(end-peak)+1)
        return np.where((t>start)&(t<end),(1-np.cos(np.pi*np.clip(phase,0,2)))/2,0)
    qrs=np.interp(t,[0,.220,.232,.252,.274,.300,.800],
                    [0,0,-.08,1.0,-.20,0,0])
    return qrs+.15*lobe(.060,.110,.160)+.30*lobe(.340,.470,.580)


def wave(x):
    return -PX_PER_MV*millivolts(np.asarray(x)/PX_PER_SECOND)


def sample_x(start,end,step):
    # Include every extremum exactly so raster sampling cannot shorten R peaks.
    knots=np.array([.060,.110,.160,.220,.232,.252,.274,.300,.340,.470,.580])*PX_PER_SECOND
    beats=np.arange(np.floor(start/BEAT),np.ceil(end/BEAT)+1)*BEAT
    return np.unique(np.r_[np.arange(start,end,step),(beats[:,None]+knots).ravel()])


def entry_point(cfg,frame):
    shift=(frame % FRAMES)*PERIOD/FRAMES
    return cfg['entry_x'],float(cfg['baselines'][0]+wave(cfg['entry_x']+shift))


def entry_glow(cfg,frame):
    """A fixed-x star follows the same sampled signal as the incoming trace."""
    ex,ey=entry_point(cfg,frame)
    yy,xx=np.ogrid[:cfg['height'],:cfg['width']]
    dx,dy=xx-ex,yy-ey
    radius=np.hypot(dx,dy)
    support=np.clip((15-radius)/5,0,1)
    halo=np.exp(-radius**2/35)*support*.19
    rays=(np.exp(-dx**2/20-dy**2/.42)+np.exp(-dy**2/32-dx**2/.42))*.48*support
    core=np.exp(-radius**2/1.7)
    return (halo[...,None]*np.array([65,225,120])+
            (rays+core)[...,None]*np.array([185,255,216]))


def illumination(cfg):
    """One stationary radial field, shared by the ambient tint and grid light.

    Desktop center maps the user's marker (1014,262) from the 1245x403 panel.
    """
    x=np.arange(cfg['width'])[None,:]
    y=np.arange(cfg['height'])[:,None]
    cx,cy,rx,ry=(470,390,235,145) if cfg['mobile'] else (932,158,245,185)
    return np.exp(-2*(((x-cx)/rx)**2+((y-cy)/ry)**2))


def prepare(cfg):
    w,h=cfg['width'],cfg['height']
    x,y=np.meshgrid(np.arange(w),np.arange(h))
    def smooth(t):
        t=np.clip(t,0,1)
        return t*t*(3-2*t)
    # A single analytic boundary, independent of text length or individual rows.
    # Desktop: diagonal transition into the upper-right signal area.
    # Mobile: one reserved signal band between identity and information rows.
    top=cfg['grid_top']; bottom=top+GRID_ROWS*GRID_CELL
    vertical=smooth((y-top)/20)*(1-smooth((y-bottom+20)/20))
    horizontal=smooth((x-24)/48)*(1-smooth((x-w+72)/48)) if cfg['mobile'] else smooth((x-610-.04*y)/92)*(1-smooth((x-w+70)/70))
    visibility=vertical*horizontal
    ambient=illumination(cfg)*horizontal
    bg=np.zeros((h,w,3),np.float32)+BG
    bg+=ambient[...,None]*np.array([12,19,34])

    # One horizontal tile contains all wave rows; tiled sampling translates
    # actual geometry left by PERIOD/FRAMES pixels at every frame.
    S=3
    tile=Image.new('L',(PERIOD*S,h*S))
    td=ImageDraw.Draw(tile)
    wave_paths=[]
    for row,b in enumerate(cfg['baselines']):
        xs=sample_x(-PERIOD,PERIOD*2,.35)
        ys=b+wave(xs+row*83)*cfg['amplitude']
        td.line([(round(xx*S),round(yy*S)) for xx,yy in zip(xs,ys)],
                fill=255,width=round(1.5*S),joint='curve')
        vx=sample_x(-PERIOD,w+PERIOD,1.2)
        vy=b+wave(vx+row*83)*cfg['amplitude']
        wave_paths.append('M '+' L '.join(f'{xx:.1f} {yy:.1f}' for xx,yy in zip(vx,vy)))
    tile=tile.resize((PERIOD,h),Image.Resampling.LANCZOS)
    signal=(np.asarray(tile,np.float32)/255*.69
            +np.asarray(tile.filter(ImageFilter.GaussianBlur(2)),np.float32)/255*.23
            +np.asarray(tile.filter(ImageFilter.GaussianBlur(6)),np.float32)/255*.11)

    # Foreground is built once. Text, dividers, card borders never translate.
    S=2
    foreground=Image.new('RGBA',(w*S,h*S))
    draw=ImageDraw.Draw(foreground)
    def box(v): return tuple(round(z*S) for z in v)
    for x1,y1,x2,y2 in cfg['cards']:
        material=glass_card((x2-x1,y2-y1)).resize(((x2-x1)*S,(y2-y1)*S),Image.Resampling.LANCZOS)
        foreground.alpha_composite(material,(x1*S,y1*S))
    draw=ImageDraw.Draw(foreground)
    for x,y,kind in cfg['icons']:
        icon_scale=1 if cfg['mobile'] else .75
        for shape,coords,radius in icon_shapes(kind):
            coords=tuple((z*icon_scale+(x if i%2==0 else y))*S for i,z in enumerate(coords))
            if shape=='rect': draw.rounded_rectangle(coords,radius=radius*S*icon_scale,outline=GREEN,width=2*S)
            elif shape=='ellipse': draw.ellipse(coords,outline=GREEN,width=2*S)
            else: draw.line(coords,fill=GREEN,width=2*S,joint='curve')
    for line in cfg['dividers']:
        draw.line(box(line),fill=(43,55,61,255),width=S)
    for line in cfg['card_rules']:
        draw.line(box(line),fill=(36,47,52,255),width=S)
    pulse=np.zeros((h,w),np.float32)
    pulse_y,pulse_x=np.indices((h,w))
    for dx,dy in cfg['dots']:
        radius=5 if cfg['mobile'] else 3
        draw.ellipse(box((dx-radius,dy-radius,dx+radius,dy+radius)),fill=GREEN)
        # Finite support keeps even the glow from touching the status label.
        distance=np.hypot(pulse_x-dx,pulse_y-dy)
        pulse+=np.exp(-distance**2/50)*np.clip((13-distance)/4,0,1)
    header=cfg['dividers'][0]
    draw.line(box(header),fill=(49,74,59,255),width=S)
    draw.line(box((header[0],header[1],header[0]+84,header[1])),fill=GREEN,width=2*S)
    for x,y,words,size,kind,color in cfg['text']:
        ft=font(size,kind,S)
        assert draw.textbbox((x*S,y*S),words,font=ft,anchor='lt')[2] < (w-28)*S, words
        text_top=ft.getbbox(words,anchor='la')[1]
        for offset,part,run_color in text_runs(words,size,kind,color,S):
            draw.text((x*S-ink_offset(words,size,kind,S)+offset,y*S-text_top),part,font=ft,fill=run_color,anchor='la')
    draw.rounded_rectangle((S,S,(w-1)*S,(h-1)*S),radius=20*S,
                           outline=(48,60,67,255),width=S)
    foreground=foreground.resize((w,h),Image.Resampling.LANCZOS)
    outer=Image.new('L',(w,h)); ImageDraw.Draw(outer).rounded_rectangle((0,0,w-1,h-1),radius=20,fill=255)
    return cfg,bg,visibility,signal,foreground,outer,wave_paths,pulse


def render(data,frame,show_entry=True):
    cfg,bg,visibility,signal,fg,outer,_,pulse=data
    shift=(frame % FRAMES)*PERIOD/FRAMES
    positions=np.arange(cfg['width'])+shift
    low=positions.astype(int)%PERIOD
    frac=(positions%1)[None,:]
    moving=signal[:,low]*(1-frac)+signal[:,(low+1)%PERIOD]*frac
    screen_x=np.arange(cfg['width'])[None,:]
    mint=np.clip((screen_x-(cfg['entry_x']-48))/48,0,1)
    mint=mint*mint*(3-2*mint)
    color=np.array([70,237,121])+mint[...,None]*np.array([104,18,84])
    trace_visibility=visibility*(screen_x<=cfg['entry_x'])
    pixels=bg+moving[...,None]*trace_visibility[...,None]*color
    # Grid and trace share the same translation; the blue illumination stays fixed.
    xx=np.arange(cfg['width'])[None,:]+shift
    yy=np.arange(cfg['height'])[:,None]-cfg['grid_middle']
    def lines(z,period):
        distance=np.abs((z+period/2)%period-period/2)
        return np.clip(1-distance,0,1)
    grid=np.maximum(lines(xx,GRID_CELL),lines(yy,GRID_CELL))*4.0
    grid+=np.maximum(lines(xx,GRID_CELL*5),lines(yy,GRID_CELL*5))*3.0
    light=.35+2.65*illumination(cfg)
    pixels+=grid[...,None]*visibility[...,None]*light[...,None]*np.array([.7,.9,1.3])
    strength=.12+.14*(1-np.cos(16*np.pi*(frame%FRAMES)/FRAMES))/2
    # Added after the stationary translucent surface; the pulse is only a halo.
    image=Image.fromarray(np.uint8(np.clip(pixels,0,255))).convert('RGBA')
    image=Image.alpha_composite(image,fg)
    rgb=np.asarray(image).copy()
    rgb[:,:,:3]=np.uint8(np.clip(rgb[:,:,:3]+pulse[...,None]*strength*np.array([70,237,121])+(entry_glow(cfg,frame) if show_entry else 0),0,255))
    image=Image.fromarray(rgb)
    backing=Image.new('RGBA',image.size,(*BG,255))
    backing.paste(image,(0,0),outer)
    return backing.convert('RGB')


def svg_source(data,name):
    cfg,_,vis,_,_,_,paths,_=data
    w,h=cfg['width'],cfg['height']
    buf=io.BytesIO(); Image.fromarray(np.uint8(vis*255)).save(buf,format='PNG')
    maskdata=b64encode(buf.getvalue()).decode()
    background_data=list(data)
    background_data[3]=np.zeros_like(data[3])
    background_data[4]=Image.new('RGBA',(w,h))
    background_data[7]=np.zeros_like(data[7])
    platebuf=io.BytesIO();render(tuple(background_data),0,show_entry=False).save(platebuf,format='PNG')
    background_png=b64encode(platebuf.getvalue()).decode()
    items=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>Ethan Doan — undergraduate profile</title>
<desc>Synthetic lead-II geometry represents 75 bpm, shown at quarter speed for calm viewing, not real-time heart-rate playback. Trace and grid move together; illumination and entry x remain fixed.</desc>
<defs><clipPath id="panel"><rect width="{w}" height="{h}" rx="20"/></clipPath>
<mask id="soft-content-fade"><image width="{w}" height="{h}" href="data:image/png;base64,{maskdata}"/></mask>

<clipPath id="entry-clip"><rect width="{cfg['entry_x']}" height="{h}"/></clipPath>
<linearGradient id="mint" gradientUnits="userSpaceOnUse" x1="{cfg['entry_x']-48}" x2="{cfg['entry_x']}" y1="0" y2="0"><stop stop-color="#46ed79"/><stop offset=".5" stop-color="#7af6a3"/><stop offset="1" stop-color="#aeffcd"/></linearGradient>
<filter id="glow"><feGaussianBlur stdDeviation="3"/></filter></defs>
<g clip-path="url(#panel)"><rect width="{w}" height="{h}" fill="#0b0f13"/>
<image id="stationary-blue-and-grid-at-phase-zero" width="{w}" height="{h}" href="data:image/png;base64,{background_png}"/>
<g id="background" mask="url(#soft-content-fade)">
<g id="waveforms" clip-path="url(#entry-clip)" fill="none" stroke="url(#mint)" stroke-width="1.5">''']
    for p in paths:
        items += [f'<path d="{p}" opacity=".25" filter="url(#glow)"/>',f'<path d="{p}" opacity=".72"/>']
    ex,ey=entry_point(cfg,0)
    items += [f'</g></g><g id="entry-star" transform="translate({ex} {ey})"><circle r="5" fill="#46ed79" opacity=".5" filter="url(#glow)"/><path d="M-7 0Q0 -1 0 -9Q1 0 7 0Q0 1 0 9Q-1 0 -7 0" fill="#caffdf"/><circle r="1.1" fill="#eafff0"/></g><g id="stationary-foreground">']
    for n,(x1,y1,x2,y2) in enumerate(cfg['cards']):
        buf=io.BytesIO();glass_card((x2-x1,y2-y1)).save(buf,format='PNG')
        plate=b64encode(buf.getvalue()).decode()
        items += [f'<image id="glass-material-{n}" x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" href="data:image/png;base64,{plate}"/>']
    for x,y,kind in cfg['icons']:
        parts=[]
        for shape,coords,radius in icon_shapes(kind):
            if shape=='rect':
                a,b,c,d=coords
                parts.append(f'<rect x="{a}" y="{b}" width="{c-a}" height="{d-b}" rx="{radius}"/>')
            elif shape=='ellipse':
                a,b,c,d=coords
                parts.append(f'<ellipse cx="{(a+c)/2}" cy="{(b+d)/2}" rx="{(c-a)/2}" ry="{(d-b)/2}"/>')
            else:
                points=' '.join(f'{coords[i]},{coords[i+1]}' for i in range(0,len(coords),2))
                parts.append(f'<polyline points="{points}"/>')
        shapes=''.join(parts)
        icon_scale=1 if cfg['mobile'] else .75
        items.append(f'<g id="icon-{kind}" transform="translate({x} {y}) scale({icon_scale})" fill="none" stroke="{GREEN}" stroke-width="{2/icon_scale}">{shapes}</g>')
        (SOURCE/f'icon-{kind}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="68" height="68" viewBox="-2 -2 68 68"><title>{kind} concept icon</title><g fill="none" stroke="{GREEN}" stroke-width="2">{shapes}</g></svg>',encoding='utf-8')
    for x1,y1,x2,y2 in cfg['dividers']+cfg['card_rules']:
        items += [f'<path d="M{x1} {y1}H{x2}" stroke="{BORDER}"/>']
    x1,y1,x2,_=cfg['dividers'][0]
    items += [f'<path d="M{x1} {y1}H{x2}" stroke="#314a3b"/>',f'<path d="M{x1} {y1}h84" stroke="{GREEN}" stroke-width="2"/>']
    for x,y in cfg['dots']:
        items.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{GREEN}" opacity=".15" filter="url(#glow)"/><circle cx="{x}" cy="{y}" r="{5 if cfg["mobile"] else 3}" fill="{GREEN}"/>')
    for x,y,words,size,kind,color in cfg['text']:
        family='Consolas, monospace'
        spans=''.join(f'<tspan x="{x-ink_offset(words,size,kind)+offset}" fill="{run_color}">{escape(part)}</tspan>' for offset,part,run_color in text_runs(words,size,kind,color))
        items += [f'<text y="{y}" dominant-baseline="text-before-edge" font-family="{family}" font-size="{size}" font-weight="{700 if kind=="bold" else 400}">{spans}</text>']
    items += [f'</g><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20" fill="none" stroke="#303c43"/></g></svg>']
    (SOURCE/f'{name}.svg').write_text('\n'.join(items),encoding='utf-8')


def build(mobile=False):
    name='profile-mobile' if mobile else 'profile-desktop'
    data=prepare(layout(mobile))
    static=render(data,0)
    static.save(OUT/f'{name}-still.png',optimize=True)
    gifsize=static.size
    palette=static.resize(gifsize,Image.Resampling.LANCZOS).quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    # Freeze foreground glyph pixels after quantization. Moving near-black
    # background must not make antialiased letters shimmer between palette bins.
    foreground=np.asarray(data[4].resize(gifsize,Image.Resampling.LANCZOS))
    locked=Image.fromarray(np.uint8((foreground[:,:,3]>0)&(foreground[:,:,:3].mean(axis=2)>70))*255)
    frames=[]
    for i in range(FRAMES):
        rgb=render(data,i)
        if i in (0,30,60,90,119): rgb.save(QA/f'{name}-frame-{i:03}.png',optimize=True)
        frame=rgb.resize(gifsize,Image.Resampling.LANCZOS).quantize(palette=palette,dither=Image.Dither.NONE)
        frame.paste(palette,(0,0),locked)
        frames.append(frame)
    frames[0].save(OUT/f'{name}.gif',save_all=True,append_images=frames[1:],
                   duration=MS,loop=0,disposal=1,optimize=True)
    svg_source(data,name)
    print(name, (OUT/f'{name}.gif').stat().st_size,'bytes',flush=True)
    return data


if __name__=='__main__':
    for mobile in (False,True): build(mobile)
    (SOURCE/'panel-layout.json').write_text(json.dumps({
        'desktop':layout(), 'mobile':layout(True),
        'frames':FRAMES,'frame_ms':MS,'period_px':PERIOD,
        'patterns':PATTERN_COUNT,'beat_pitch_px':BEAT,'name_space_reduction_px':NAME_SPACE_REDUCTION,
        'direction':'right to left','pixels_per_second':PERIOD/(FRAMES*MS/1000)
    },indent=2),encoding='utf-8')

