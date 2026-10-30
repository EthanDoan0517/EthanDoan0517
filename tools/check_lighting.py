"""Verify bounded lighting response, shared phase and unchanged geometry."""
import json,hashlib,xml.etree.ElementTree as E
import numpy as np
from build_vector import b, lighting, response
ns={'s':'http://www.w3.org/2000/svg'}
report={}
def prior(name):
    path=b.ROOT/'archive/before-lighting-refinement/assets'/name
    if path.exists(): return path.read_bytes()
    import urllib.request
    return urllib.request.urlopen('https://raw.githubusercontent.com/EthanDoan0517/EthanDoan0517/867cc02141c476a503658ec77cfdecf7c110482e/assets/'+name).read()
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
    # Every color animation uses the same envelope as the grid's response.
    timing=root.find('.//s:g[@id="grid-response"]/s:animate',ns).attrib
    for a in grad.findall('.//s:animate',ns):
        for k in ('keyTimes','keySplines','dur','calcMode'):
            assert a.attrib[k]==timing[k]
        assert 'additive' not in a.attrib and 'accumulate' not in a.attrib
    t=light['peak']; peak_x=(.252*b.PX_PER_SECOND-t*100)%320
    assert abs((light['cx']-peak_x)%320)<1e-5
    phases=np.linspace(0,48,120001); gains=np.array([response(x,light) for x in phases])
    assert gains.min()>=0 and gains.max()<=1
    assert response(0,light)==response(3.2,light)==response(48,light)
    assert response(t,light)==1 and response(t-.16,light)<1e-10 and response(t+.64,light)<1e-10
    star=root.find('.//s:g[@id="entry-star"]',ns)
    core=star.find('s:circle[@id="entry-core"]',ns)
    assert core is not None and len(core)==0 and 'opacity' not in core.attrib
    pulses=star.findall('.//s:animate',ns); assert len(pulses)==2
    assert all(a.attrib['dur']=='3s' for a in pulses)
    assert min(float(v) for a in pulses for v in a.attrib['values'].split(';'))==.68
    # The independent star/ECG/status cycles all align again every 48 seconds.
    for period in (3,3.2,4):assert abs(48/period-round(48/period))<1e-10
    report[name]=dict(**light,ambient_gain_range=[1,1.1],grid_opacity_range=[.93,1],star_halo_opacity_range=[.68,1],star_period=3,ecg_period=3.2,combined_period=48,wave_and_movement_unchanged=True)
for path in b.OUT.glob('card-*.svg'):
    assert path.read_bytes()==prior(path.name)
(b.QA/'lighting-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
