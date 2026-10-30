# README rendering investigation — 2026-10-30

## Confirmed causes

The prior delivery rasterized all text, icons, thin lines and surfaces. Text was
painted at 2x then downsampled by Lanczos to 1200px (hero) or 524px (desktop card).
The browser then resized those flattened pixels again. The hero exporter also
redrew its outer border and corner mask at 1x. Existing cards reused raster crops.

At normal browser zoom (visual viewport scale 1), the actual desktop screen had
DPR 1.5. The live hero occupied 831.333 CSS px: 1247 physical pixels versus 1200
source pixels. Each card occupied 374 CSS px: 561 physical pixels versus 524.
Thus even this display slightly upsampled the already rasterized artwork. At
DPR 2 the shortfall is larger. Mobile at 375 viewport width displays the 720px
hero at 278.667 CSS px, enough at DPR 2 but insufficient at DPR 3 (836 pixels).
This density comparison is arithmetic; DPR 2/3 physical devices were not tested.

All four sampled live hero/card files were byte-identical to local exports.
Heroes were 8-bit RGB APNG; cards were 8-bit RGBA APNG with smooth alpha corners.
There was no active GIF palette reduction, lossy animation compression, or
GitHub recompression in these requests. Legacy GIFs are not linked by the README.
PNG gradients were already full-color; faint quantization in dark 8-bit gradients
can remain visible on some displays. Screenshot JPEG compression is not a source
asset defect and must not be confused with the actual page's rendering.

## Implemented approach

The linked artwork is now all vector: original Consolas glyph outlines, original
icon geometry, smooth rounded borders, vector grid and trace, continuous gradient
fields. Font outlines avoid missing-font fallback and external font loads in SVG
image contexts. Accessible prose and descriptive image alt text remain in README.
No JavaScript, foreignObject, network fonts, or embedded raster images are used.

The ECG and grid translate together by 320px in 3.2 seconds. The endpoint uses the
same waveform function with explicit QRS breakpoints; its x position stays fixed.
Mint coloring stays in screen space. Blue lighting is stationary. Fade masks are
applied after glow blur, preserving the clear text margin. The normal motion is
continuous rather than capped at the previous APNG's 50 frames/second.

Both hero layout dimensions and card display widths are unchanged. Responsive
and reduced-motion picture sources are retained. Static SVG alternatives contain
no animation. Links and accessible editorial content are unchanged.

SVG was chosen over larger APNG exports because it removes the raster bottleneck
while reducing transfer size. A 2x raster would improve density only up to its
finite resolution and multiply animated pixel volume. Full-color APNG remains a
valid fallback, but its current encoding was not the source of palette damage.

## Verification and limits

Automated checks: all 14 linked SVGs parse, all resources are internal, no bitmaps
or scripts; static variants contain no animations; content and links match the
prior README; grid/divider share y=146 desktop and y=392 mobile; 20 small squares
per beat; 320px loop periodicity; fixed endpoint x and matching waveform heights.
Browser verification and measured timings are recorded in preview/sharp-*.

Small type remains small by design. Vector rendering removes pre-rasterization
but cannot remove display pixel limits or browser antialiasing. Actual dark
color smoothness depends on the display. Browser testing is Chrome on Windows,
with desktop/mobile viewport checks, not physical iOS/Safari testing.

References:
- MDN, SVG as an image (image restrictions): https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image
- MDN, animateTransform: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/animateTransform
GitHub compatibility is checked empirically on the live profile, not inferred
from the local preview alone.


Live verification: GitHub loaded all three desktop SVGs as images. Sampled live
SVG response bodies match the source exactly and use image/svg+xml. The tested
raw asset requests completed in 0.21–0.32 seconds on this connection; this is not
a whole-page benchmark. Desktop hero112091 bytes versus6369621 bytes previously
(98.2% smaller); mobile100149 versus7108308 bytes (98.6% smaller).

Browser geometry was sampled over12.33 seconds. Linear interpolation between
sampled positions gives peak intervals3.2000000,3.2000000,3.2000001 seconds and
median translation100px/s. Raw requestAnimationFrame callbacks were irregular;
these values verify motion timing, not achieved display frame rate. Canvas
sampling of an SVG image returned a static image and was rejected as a timing
measurement. SVG image motion was separately inspected on the actual profile.


## Subsequent lighting correction

The masked low-alpha SVG glow itself produced a narrow dark band. This was a
compositing issue in the vector implementation, separate from the earlier raster
softness. The ambient field is now opaque and the signal's final blend is outside
its masks. See LIGHTING-NOTES.md for reproduced pixel evidence, repositioning,
independent star pulse and synchronized R-wave response.


The subsequent steady-glow revision removes the R-triggered ambient and grid
illumination pulses. The corrected opaque field and independent star pulse remain.
