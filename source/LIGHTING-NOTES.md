# EKG lighting — 2026-10-30

## Current: steady ambient glow

The R-triggered ambient and grid-illumination pulses have been removed. The
corrected opaque gradient stays at its resting RGB(19,29,44) center color at all
times, including spikes and loop boundaries. Its shape and desktop/mobile centers
are unchanged. Grid illumination is fixed at opacity0.93 while the grid scrolls.
The endpoint star retains its3-second pulse and fixed pale core; project status
dots retain their4-second animations. Waveform geometry and3.2-second translation
are unchanged. The gradient has no animation elements. Checks compare its exact
stop colors and geometry with the previous resting field, the star element with
the previous export, and the complete card bytes with the previous assets.

The earlier investigation below documents the band correction and the now-removed
R-wave response. Current browser evidence uses preview/steady-* filenames.

## Earlier band correction and response

The supplied crop shows a real dark fade band, not just low image resolution.
Its pixels fall from the panel's RGB(11,15,19) to (9,13,17). A browser-rendered
isolation of the old ambient layer reproduced below-background pixels. The old
full desktop still contained41,185 below-background pixels in the tested interior.

## Correction

The old ambient layer used a low-alpha blue radial gradient and a translucent
left mask, with screen blending inside the mask's isolated group. Premultiplied
low-alpha compositing introduced dark rounding along the fade. The ambient field
is now one opaque radial color gradient, interpolated directly from the panel
background to its center color. It has no alpha ramp, mask, or blend operation.
No second glow, dark overlay, seam, or decorative texture was added.

The finished grid/trace group uses screen blending against the opaque background,
outside its masks. This also removes residual below-background pixels from faint
grid-mask edges. All original waveform stroke colors remain unchanged.

At11 static phases per layout, including spike rise/peak/decay, the3.2-second
waveform boundary and48-second combined boundary, there are no below-background
pixels in the ECG area. Eight desktop /28 mobile isolated single-channel edge
pixels remain in pre-existing green text antialiasing, outside the ECG region;
they are unrelated to the corrected band. The test did not modify typography.

## Composition and timing

Desktop text ends conservatively at x519, panel right border x1199. The ambient
center is their midpoint x859, shifted left from x932; y158 is retained. Mobile
has a separate signal band, with no adjacent text column. Its glow moves left
from x470 to x360, centered in that usable band; y390 is retained. One continuous
elliptical field provides the background and defines the grid's illumination.

Quiet center RGB(19,29,44), peak approximately RGB(20,30,47): only a10% lift in
the light's contribution above the background. The response rises smoothly for
160ms, peaks as R crosses the field center, then decays smoothly over640ms.
The grid's illumination moves from opacity0.93 to1 with the identical envelope.
Both return to the same baseline; neither uses additive or accumulating animation.

R maxima satisfy x=100.8+320k-100t. The first center crossings occur at2.018s
on desktop and0.608s on mobile, then every3.2s. Geometry and translation remain
byte-identical to the previous SVG paths and transform animations. This is still
a slowed synthetic illustration, not a patient recording or real-time rate display.

The endpoint star retains its fixed x and original waveform-following transform.
Its halo varies smoothly between0.68 and1 opacity, and rays between0.80 and1,
every3 seconds—slightly faster than the unchanged4-second project status dots.
The pale core has no opacity animation and remains visible. This regular pulse
is independent of the R-triggered ambient response. All cycles align every48s.

## Verification

- tools/check_vector.py: image structure, geometry, loop, links and content.
- tools/check_lighting.py: unchanged movement/paths/card bytes, center calculation,
  bounded response, matching grid timings, fixed star core,3/3.2/4-second cycles.
- preview/lighting-pixel-checks.json: browser-rendered phase images and dark-pixel locations.
- preview/lighting-browser-peak.json and lighting-browser-quiet.json: actual browser
  animated colors/opacity and endpoint position at exact signal phases.
- preview/lighting-motion-samples.json: multiple live animation cycles, when present.
- Live desktop/mobile screenshots and publication hash checks are in preview/lighting-*.

The SVG remains fully vector and self-contained, with no script or external font.
Nonanimated reduced-motion SVGs remain available. Content, card links, typography,
calibration, section dimensions and scrolling speed are preserved.
