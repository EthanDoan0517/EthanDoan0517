"""Check the delivered vector assets, preserved content and sampled geometry."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
import numpy as np
import build_panel as b

root=b.ROOT; ns={'s':'http://www.w3.org/2000/svg'}
readme=(root/'README.md').read_text(encoding='utf-8')
baseline=root/'archive/before-sharp-refinement/README.md'
if baseline.exists(): old=baseline.read_text(encoding='utf-8')
else:
    import urllib.request
    old=urllib.request.urlopen('https://raw.githubusercontent.com/EthanDoan0517/EthanDoan0517/f862e486b6835f53df401f21db8bbced2345bc55/README.md').read().decode('utf-8')
assert re.findall(r'href="([^"]+)"',readme)==re.findall(r'href="([^"]+)"',old)
assert readme[readme.index('# Ethan Doan'):]==old[old.index('# Ethan Doan'):]
assets=sorted(set(re.findall(r'assets/[\w-]+\.svg',readme)))
records=[]
for name in assets:
    raw=(root/name).read_bytes(); el=ET.fromstring(raw)
    assert not el.findall('.//s:image',ns), 'no raster layers'
    assert not el.findall('.//s:script',ns)
    assert not el.findall('.//s:foreignObject',ns)
    assert not el.findall('.//s:text',ns), 'glyph outlines must not depend on installed fonts'
    for use in el.findall('.//s:use',ns): assert use.attrib['href'].startswith('#')
    animated=not '-still' in name
    anims=el.findall('.//s:animateTransform',ns)+el.findall('.//s:animate',ns)
    assert bool(anims)==animated
    if 'hero-' in name and animated:
        transforms=el.findall('.//s:animateTransform',ns)
        assert len(transforms)==6
        assert all(a.attrib['dur']=='3.2s' for a in transforms)
        assert sum(a.attrib.get('to')=='-320 0' for a in anims)==4
        star=next(a for a in transforms if 'keyTimes' in a.attrib)
        times=np.array([float(x) for x in star.attrib['keyTimes'].split(';')])
        vals=np.array([[float(x) for x in p.split()] for p in star.attrib['values'].split(';')])
        assert np.all(np.diff(times)>0) and times[0]==0 and times[-1]==1
        cfg=b.layout('mobile' in name); ex=cfg['entry_x']; baseline=cfg['baselines'][0]
        expected=baseline+b.wave(ex+times*320)
        # keyTimes rounded to 4 decimals may shift a steep slope by <.07px.
        assert np.max(abs(expected-vals[:,1]))<.08
        assert np.all(vals[:,0]==ex) and np.max(abs(vals[0]-vals[-1]))<1e-6
    records.append(dict(path=name,bytes=len(raw),sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),dimensions=[float(el.attrib[x]) for x in ['width','height']],animated=animated))

geometry={}
for mobile in (False,True):
    cfg=b.layout(mobile); name='mobile' if mobile else 'desktop'
    assert cfg['grid_middle']==cfg['dividers'][0][1]
    x=np.linspace(0,320,20001)
    assert np.max(abs(b.wave(x+320)-b.wave(x)))<1e-10
    margin=None
    if not mobile:
        margins=[]
        for tx,ty,words,size,kind,col in cfg['text']:
            if ty<cfg['grid_top']+256 and tx==204:
                right=tx+b.font(size,kind).getlength(words)
                margins.append(548+.04*ty-right)
        margin=min(margins); assert margin>20
    geometry[name]=dict(beat_spacing=320,small_square=16,beat_small_squares=20,playback_beat_seconds=3.2,playback_px_per_second=100,divider_grid_y=cfg['grid_middle'],minimum_text_fade_clearance_source_px=margin,loop_max_wave_error=float(np.max(abs(b.wave(x+320)-b.wave(x)))))

report=dict(assets=records,geometry=geometry,links_unchanged=True,accessible_content_unchanged=True)
(root/'preview/sharp-vector-checks.json').write_text(json.dumps(report,indent=2))
publish=[dict(path='README.md')]+[dict(path=x['path']) for x in records]+[dict(path='source/ECG-NOTES.md'),dict(path='source/RENDERING-NOTES.md'),dict(path='tools/build_vector.py'),dict(path='tools/build_panel.py'),dict(path='tools/check_vector.py'),dict(path='tools/requirements.txt'),dict(path='MAINTENANCE.txt'),dict(path='source/LIGHTING-NOTES.md'),dict(path='tools/check_lighting.py')]
for entry in publish:
    path=root/entry['path']
    if path.exists():
        data=path.read_bytes();entry.update(bytes=len(data),sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
(root/'preview/publication-manifest.json').write_text(json.dumps(publish,indent=2))
print(json.dumps(dict(total_svg_bytes=sum(x['bytes'] for x in records),geometry=geometry,linked_assets=len(records),links_preserved=True),indent=2))
