# Predictions — written 14 October 2026, before any bridge recording

Rydvan, 14 Oct 2026, about 10:45 Bangkok time. Fixed before the first bridge recording on the same day. Not to be changed after data exist; any later thoughts go in a new, dated file.

## Bridges
- Charoen Nakhon Road: four 6-lane, single-span reinforced-concrete footbridges. Span taken as **25 m** for all four (A measured 24.3 m, C 25.4 m; the other two assumed the same because they are on the same road over the same number of lanes).
- Ratchadaphisek Road: two 8-lane footbridges with a middle column. Span taken as **17 m** (end column to middle column; D measured 17 m on both sides, the other assumed the same).
- Every span is measured again on the day before recording. The analysis uses measured spans; these predictions use the values above.

## Method (worked by hand on a calculator)
- Simply supported concrete beam: f = (π / 2L²) × √(EI/m).
- Solid rectangular concrete section, depth h = L / 20, E = 30 GPa, density 2400 kg/m³: √(E / (12 × 2400)) = 1020.6, × π/2 = 1603 ≈ 1600, so **f ≈ 1600 × h / L²**, period T = 1 / f.
- Range: f × 0.8 to f × 1.25 (a factor of 1.25 either way). Lower: railings, roof and finishes add mass but little stiffness. Higher: real beams may be T-shaped or hollow, stiffer for their weight.

| Group | L (m) | h (m) | f (Hz) | Range (Hz) |
|---|---|---|---|---|
| Charoen Nakhon | 25 | 1.25 | 3.2 | 2.56 – 4.0 |
| Ratchadaphisek | 17 | 0.85 | 4.71 | 3.76 – 5.875 |

## Hypotheses
- **H1:** Yes, all calculations say they are between 2 and 6 Hz. (Periods about 0.17–0.5 s, far from Bangkok's site periods of 1–6 s.) Wrong if any bridge is outside 2–6 Hz.
- **H2:** For the 25 m ones, the low end of the range approaches the walking band (up to 2.4 Hz). Both groups can fall under 5 Hz (where a comfort check is needed), but the 17 m ones can also go higher. This is all without accounting for the extra things like railings. Wrong if all six are above 5 Hz, or if any is inside 1.6–2.4 Hz.
- **H3:** The ratio f(17 m) / f(25 m) is 1.46, call it about 1.5. It could be smaller because of mass and other things such as railings and stairs. (If both had the same beam depth the ratio would be (25/17)² ≈ 2.2.) Wrong if the 17 m spans are not faster.

## Ground rule
A spectral peak counts as the bridge's own only if its power on the bridge is **at least 10×** its power on the pavement at the same frequency. Peaks below 10× are reported as unconfirmed, never removed.
