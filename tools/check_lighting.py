"""Verify steady ambient lighting and preserved endpoint/card animations."""
import json,hashlib,xml.etree.ElementTree as E
import numpy as np
from build_vector import b, lighting, Drawing
ns={'s':'http://www.w3.org/2000/svg'}
report={}
def prior(name):
    path=b.ROOT/'archive/before-steady-glow/assets'/name
    if path.exists(): return path.read_bytes()
    import urllib.request
    return urllib.request.urlopen('https://raw.githubusercontent.com/EthanDoan0517/EthanDoan0517/8b66fc700e7b9ce4b28f97679dc768d88e062675/assets/'+name).read()
for mobile in (False,True):
    name='mobile' if mobile else 'desktop'; cfg=b.layout(mobile); light=lighting(cfg)
    root=E.parse(b.OUT/f'hero-{name}.svg').getroot()
    old=E.fromstring(prior(f'hero-{name}.svg'))
    assert root.find('.//s:path[@id="wave"]',ns).attrib==old.find('.//s:path[@id="wave"]',ns).attrib
    old_transform=[E.tostring(x) for x in old.findall('.//s:animateTransform',ns)]
    new_transform=[E.tostring(x) for x in root.findall('.//s:animateTransform',ns)]
    assert old_transform==new_transform
    assert len(root.findall('.//s:rect[@id="ambient-field"]',ns))==1
    field=root.find('.//s:rect[@id="ambient-field"]',ns)
    assert 'mask' not in field.attrib and 'opacity' not in field.attrib
    grad=root.find('.//s:radialGradient[@id="ambient-color"]',ns)
    assert all('stop-opacity' not in s.attrib for s in grad)
    assert not grad.findall('.//s:animate',ns)
    grid=root.find('.//s:g[@id="grid-response"]',ns)
    assert grid.attrib['opacity']=='.93' and not grid.findall('s:animate',ns)
    # Exact prior resting gradient, same center and falloff; no brightness change.
    old_grad=old.find('.//s:radialGradient[@id="ambient-color"]',ns)
    assert grad.attrib==old_grad.attrib
    assert [x.attrib for x in grad]==[x.attrib for x in old_grad]
    for phase in (0,.608,2.018,3.199,3.2,3.201,47.999,48):
        frame=E.fromstring(Drawing(cfg,False,phase).render())
        assert E.tostring(frame.find('.//s:radialGradient[@id="ambient-color"]',ns))==E.tostring(grad)
    star=root.find('.//s:g[@id="entry-star"]',ns)
    assert E.tostring(star)==E.tostring(old.find('.//s:g[@id="entry-star"]',ns))
    core=star.find('s:circle[@id="entry-core"]',ns)
    assert core is not None and len(core)==0 and 'opacity' not in core.attrib
    pulses=star.findall('.//s:animate',ns); assert len(pulses)==2
    assert all(a.attrib['dur']=='3s' for a in pulses)
    assert min(float(v) for a in pulses for v in a.attrib['values'].split(';'))==.68
    # The independent star/ECG/status cycles all align again every 48 seconds.
    for period in (3,3.2,4):assert abs(48/period-round(48/period))<1e-10
    report[name]=dict(**light,ambient_gain_range=[1,1],grid_opacity_range=[.93,.93],star_halo_opacity_range=[.68,1],star_period=3,ecg_period=3.2,combined_period=48,wave_and_movement_unchanged=True)
for path in b.OUT.glob('card-*.svg'):
    assert path.read_bytes()==prior(path.name)
(b.QA/'steady-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
