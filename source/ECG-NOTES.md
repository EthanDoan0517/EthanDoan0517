# Synthetic ECG illustration

This is an original, representative lead-II-style normal sinus rhythm illustration,
not a patient recording or diagnostic tracing. Identical upright P waves precede
each narrow QRS, with a fixed PR interval and represented regular 75 bpm rate.
Playback is deliberately slowed to one-quarter speed for comfortable profile
viewing; it does not demonstrate a real-time heart rate.

Calibration is expressed in logical ECG-paper units, uniformly magnified for the
screen: one 16 × 16 source-pixel square represents 1 mm, 0.04 s horizontally and
0.1 mV vertically. Five small squares form a large square (0.2 s / 0.5 mV).
Screen resizing preserves square cells; physical screen millimeters depend on the
display and zoom. R–R = 320 source pixels = 20 small squares = four large squares
= 0.8 s of represented ECG time. Both trace and grid translate 2 pixels every
20 ms (100 source pixels per playback second). The full-color APNG has 160
frames and loops every 3.2 seconds. The geometry still uses the 25 mm/s paper
standard; on-screen motion is slowed fourfold without stretching the waveform.

| Component | Chosen value | Rationale |
| --- | --- | --- |
| P | +0.15 mV, 100 ms | Small, rounded and upright; below 0.25 mV and 120 ms |
| PR | 160 ms | Constant, within the usual 120–200 ms range |
| Q | −0.08 mV | Small initial septal deflection, <25% of R; negative phase <40 ms |
| R | +1.00 mV | Dominant positive limb-lead deflection; 10 small squares |
| S | −0.20 mV | Modest terminal negative deflection; two small squares |
| QRS | 80 ms | Narrow normal complex; two small squares |
| ST | 40 ms at baseline | Isoelectric, without elevation or depression |
| T | +0.30 mV, 240 ms | Broad upright lobe with a slower rise and faster return |
| QT | 360 ms | Bazett QTc ≈402 ms at R–R 800 ms |

These amplitudes are illustrative choices within a plausible lead-II morphology,
not universal normal values; QRS voltage varies with the person and lead. There
are no decorative beat-to-beat changes, ectopic beats, baseline drift or U waves.

The grid center and green divider share y=146 on desktop and y=392 on mobile.
The desktop lower separator moves from y=334 to y=282; the mobile signal-band
lower separator moves from y=554 to y=520. The mobile trace and central divider
move up together by 8 pixels. Shorter information rows reduce hero height from
390 to 338 pixels on desktop and from 1272 to 1040 on mobile. The blue field
stays stationary; category-label sizes and project-card artwork are unchanged. The trace ends at x=1128 / x=648; its last 48 pixels blend into
mint with a smoothstep gradient. A pale core, thin rays and a 15-pixel-radius
finite halo follow the exact signal height at this fixed x, including at the loop.

## Clinical references (reviewed 2026-10-30)

- [University of Utah ECG Learning Center: Characteristics of the Normal ECG](https://ecg.utah.edu/lesson/3): normal P polarity, P/PR/QRS dimensions, small septal Q waves, voltage variability, and T-wave morphology.
- [Merck Manual Professional: Electrocardiography](https://www.merckmanuals.com/professional/cardiovascular-disorders/cardiovascular-tests-and-procedures/electrocardiography): normal QRS duration, isoelectric ST, rounded concordant T waves, and adult QTc ranges.
- [McGraw Hill, Clinician's Pocket Reference: Basic ECG Reading](https://accessmedicine.mhmedical.com/content.aspx?bookid=365&sectionid=43074928): 25 mm/s, 10 mm/mV, 40 ms small squares and 200 ms large squares.

The supplied rhythm image informed the overall P–QRS–T appearance; the supplied
blue glow image informed only the original green lighting treatment. Neither
image was copied into the artwork. The documented calibration governs geometry.
