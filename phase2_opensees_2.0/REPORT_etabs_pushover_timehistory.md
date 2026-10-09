# Original models: ETABS comparison, pushover comparison and time-history explanation

"Original models" are the no-deficiency (REF) as-built flat slab (2A) and proposed beam-slab (2B). **v2.0** is this folder: 250 mm slab in both models, corner cantilevers, all beams moment-connected. **v1** is `../phase2_opensees`: 300 mm flat slab and the earlier framing.

---

## 1. Section for comparison with ETABS (elastic analysis)

**Script.** `run_04_etabs_comparison.py` writes `results/summary/E1_etabs_comparison.csv`, `E2_storey_profiles.csv` and `figures/fig12_etabs_comparison_profiles.png`.

**Analysis set-up – mirror these settings in ETABS so the numbers can be compared directly.**

| Item | Setting used |
|---|---|
| Analysis | Linear elastic: gravity, then modal (12 modes), then response spectrum (CQC), X and Y separately |
| Loads / mass | Self-weight + SDL 1.5 kPa + LL 2.5 kPa + façade 1.5 kPa; seismic mass = the same gravity load / g |
| Spectrum | DPT 1301/1302-61 design spectrum × I / R, with I = 1.25, R = 5, 5 % damping |
| Cracked-section factors | Core walls 0.50 EI and 0.50 GA; link beams 0.20 EI; columns 0.70 EI; beams (2B) 0.35 EI; flat slab as effective-width strips (Hwang & Moehle, β = 0.5 for PT) |
| Diaphragms | Rigid at every floor |
| Base | Fixed at ground level (no soil springs) |
| Drifts | Elastic response-spectrum drifts (not multiplied by Cd), at the plan centre and at the plan corners |

**Results.**

| Quantity | 2A as-built **v2.0** (250 mm) | 2B beam-slab **v2.0** | 2A as-built v1 (300 mm) | 2B beam-slab v1 |
|---|---|---|---|---|
| Seismic weight W | 632 MN | 715 MN | 684 MN | 706 MN |
| Period T1 / T2 / T3 | 7.65 / 5.94 / 3.82 s | 4.96 / 4.80 / 2.72 s | 7.11 / 5.82 / 3.63 s | 4.99 / 4.79 / 2.70 s |
| Mode 1 mass ratio UX / UY / RZ | 30 / 0 / 40 % | 33 / 0 / 41 % | 30 / 0 / 41 % | 33 / 0 / 41 % |
| Mode 2 mass ratio UX / UY / RZ | 0 / 72 / 0 % | 0 / 74 / 0 % | 0 / 72 / 0 % | 0 / 74 / 0 % |
| Mode 3 mass ratio UX / UY / RZ | 35 / 0 / 30 % | 35 / 0 / 33 % | 36 / 0 / 29 % | 35 / 0 / 33 % |
| Cumulative mass, 12 modes, UX / UY / RZ | 87 / 93 / 90 % | 89 / 95 / 91 % | 88 / 95 / 90 % | 89 / 95 / 91 % |
| ELF base shear (Cs = 0.0335, T capped at 1.4 Ta = 2.74 s) | 21.2 MN | 24.0 MN | 22.9 MN | 23.7 MN |
| RSA base shear X / Y (unscaled) | 7.2 / 7.8 MN | 10.7 / 10.5 MN | 8.2 / 8.6 MN | 10.5 / 10.4 MN |
| RSA / ELF (X / Y) | 0.34 / 0.37 | 0.44 / 0.44 | 0.36 / 0.38 | 0.44 / 0.44 |
| Base shear taken by the core, X / Y | 77 / 58 % | 74 / 52 % | 77 / 57 % | 74 / 52 % |
| Roof displacement X / Y (elastic) | 123 / 180 mm | 84 / 141 mm | 116 / 175 mm | 84 / 141 mm |
| Max storey drift X, centre / corner | 0.116 / 0.211 % | 0.076 / 0.139 % | 0.108 / 0.201 % | 0.076 / 0.142 % |
| Max storey drift Y, centre / corner | 0.166 / 0.166 % | 0.133 / 0.133 % | 0.161 / 0.161 % | 0.133 / 0.133 % |
| Storey-1 gravity axial force, pier R / M / F | 41.7 / 63.6 / 62.8 MN | 47.4 / 72.5 / 73.7 MN | 44.4 / 69.2 / 69.4 MN | 46.8 / 72.4 / 73.6 MN |
| Storey-1 gravity axial force, whole core / all columns | 168 / 464 MN | 194 / 522 MN | 183 / 501 MN | 193 / 513 MN |

**How to read it against ETABS.**

* **Mode 1 is coupled translation-torsion in X** (about 30 % UX + 40 % RZ in both framings), because the core sits at the rear edge. Mode 2 is pure Y translation. ETABS should show the same pattern. If ETABS gives a pure X first mode, the core position or the diaphragm differs between the two models.
* **The beam-slab is about 1.5× stiffer in X** (T1 4.96 s against 7.65 s). The beams form frames with the columns. Because it is stiffer, it attracts more base shear (10.7 MN against 7.2 MN), even though it is only about 13 % heavier.
* **The RSA base shear is only 34–44 % of the ELF value.** The code requires the RSA results to be scaled up to 85 % of ELF: factors of about 2.5 (2A) and 1.9 (2B). Compare against **unscaled** ETABS RSA results, or apply the same factors to both.
* **Expected agreement.** Periods within about 10 %, base shears within about 15 % and gravity forces within about 5 % would indicate that the two programs model the same building. The largest differences usually come from:
  * the cracked-section factors;
  * how the flat slab is meshed (ETABS shell elements against effective-width strips here);
  * whether the wall openings (link beams) are modelled.

---

## 2. Pushover comparison of the original models

**Script.** `plot_pushover_comparison.py` writes `figures/fig13_pushover_original_models.png` and `results/summary/E3_pushover_original_models.csv`.

**What a pushover is.** The building is pushed sideways with a slowly increasing load, distributed up the height roughly like the first mode, until it loses strength or the analysis stops. The curve plots the base shear (as % of building weight) against the roof drift (roof displacement / building height). It shows:

* **stiffness** – the initial slope;
* **strength** – the peak;
* **ductility** – how far the curve continues after the peak;
* **what fails first** – the markers on the curve.

| | 2A as-built **v2.0** | 2B beam-slab **v2.0** | 2A as-built v1 | 2B beam-slab v1 |
|---|---|---|---|---|
| **X: peak strength** | 3.65 % W (18.1 MN) | **8.42 % W (48.8 MN)** | 4.10 % W (22.5 MN) | 7.15 % W (40.8 MN) |
| X: roof drift at peak | 0.61 % | 0.89 % | 0.62 % | 0.91 % |
| X: initial stiffness (% W per % drift) | 12.1 | **24.6** | 13.3 | 23.3 |
| X: core share of base shear at peak | 65 % | 50 % | 64 % | 49 % |
| X: first link-beam yield / failure (roof drift) | 0.21 % / 0.67 % | 0.28 % / 0.85 % | 0.21 % / 0.67 % | 0.30 % / 1.07 % |
| X: what ends the curve | **punching at 1.04 %** | strength falls gradually; stops at 1.47 % | punching at 1.08 % | gradual; 2.05 % |
| **Y: peak strength** | 1.72 % W (8.5 MN) | **4.25 % W (24.6 MN)** | 1.83 % W (10.0 MN) | 3.85 % W (22.0 MN) |
| Y: roof drift at peak | 0.27 % | 1.12 % | 0.74 % | 0.95 % |
| Y: core share at peak | 63 % | 22 % | 57 % | 28 % |
| Y: what ends the curve | **punching at 1.91 %** | reaches the 2.5 % target | punching at 1.85 % | reaches 2.5 % |

**Interpretation.**

1. **Strength: the beam-slab is about 2.3× stronger in X and 2.5× stronger in Y** (v2.0). In the flat slab the core does almost all the work, because the slab–column "frame" is weak and flexible. In the beam-slab, the 500 × 800 beams and the columns form moment frames that take about half the base shear in X and about three quarters in Y.
2. **Stiffness: the beam-slab is about twice as stiff.** Its initial slope is twice as steep, which matches its shorter period (4.96 s against 7.65 s).
3. **Sequence of damage.**
   * The link beams yield first in both models, at about 0.2–0.3 % roof drift. They are the "fuse" of the core.
   * They then fail at about 0.7–0.9 %.
   * In the flat slab, the **slab punches at the columns at about 1.0 % (X) and 1.9 % (Y)**. That is a brittle failure, and the analysis cannot continue past it.
   * The beam-slab has no punching mode. It loses strength slowly as hinges form in the beams and the core.
4. **Ductility.**
   * The flat slab reaches its peak early and its curve ends at the first punching.
   * The beam-slab keeps more than 85 % of its peak strength up to about 1.5 % drift in X and holds it to 2.5 % in Y.
5. **v1 against v2.0.**
   * The thinner 250 mm flat slab is about 10–20 % weaker and slightly softer.
   * Corner cantilevers and full beam–core connections make the beam-slab about 10–20 % stronger.
   * The ranking does not change.

**One-sentence version.** The proposed beam-slab is about twice as stiff and 2.3–2.5 times as strong as the as-built flat slab, and it fails gradually instead of by sudden punching. Its weakness is not the framing but the core walls it loads harder.

---

## 3. What was done with the time-history (earthquake) analyses

**Records.**

* Three synthetic ground motions, GM1–GM3, each with two horizontal components.
* Matched to the reconstructed spectrum of the 28 March 2025 shaking in Bangkok (soft-clay site): PGA ≈ 0.024 g, PGV 8–10 cm/s, strong-shaking duration (D5-95) ≈ 56–58 s, record length 100 s.
* Each analysis runs the 100 s record plus 5 s of free vibration, at a time step of 0.025 s (4,200 steps). Runs that stop for numerical reasons are repeated at 0.01 s.

**What happens in one run.**

1. The building is loaded with gravity, using the loads at the time of the event.
2. The record, multiplied by a **scale factor SF**, is applied at the base in X and Y at the same time (SF = 1 is the real 2025 shaking).
3. At every step the model checks every wall pier, link beam, column and slab–column joint against its failure criteria. Anything that fails is removed, and its load has to find another path.
4. The run stops when the building **collapses**:
   * a storey drifts more than 10 %; or
   * the core or a floor drops 0.6 m; or
   * the building can no longer find equilibrium.
5. Otherwise it stops at the end of the record ("survived").

**The collapse search.** For each model and deficiency set:

* SF is raised 1 → 2 → 3 → 4.5 → 6 → 8 until the building collapses;
* the gap between the last SF survived and the first SF that collapsed is then halved until it is within 20 %.

That bracket is the **collapse intensity**.

**When each original and as-built model collapsed (v2.0).** "Time" is seconds into the record.

| Model | Record | Collapse SF | First link beam fails | First wall / slab failure | Building collapses | Initiation → collapse |
|---|---|---|---|---|---|---|
| 2A as-built, no deficiencies | GM1 | 7.0 | – | – | OpenSees aborted at 47.6 s (counted as collapse) | – |
| | GM2 | 7.0 | 7.8 s | punching, 24.5 s | 61.0 s | 36.5 s (progressive punching) |
| | GM3 | 6.0 | 6.8 s | punching, 19.6 s | 47.3 s | 27.7 s (progressive punching) |
| 2B beam-slab, no deficiencies | GM1 | **survives SF 8** | – | – | – | – |
| | GM2 | 8.0 | 7.7 s | none recorded | 60.5 s (numerical stop, counted as collapse) | – |
| | GM3 | **survives SF 8** | – | – | – | – |
| 2A as-built, all four deficiencies | GM1 | 4.5 | 8.3 s | none recorded | 43.2 s (numerical stop, counted as collapse) | – |
| | GM2 | 4.5 | 7.8 s | front pier F crushes, 63.6 s | 64.1 s | **0.45 s** |
| | GM3 | 3.75 | 6.4 s | front pier F crushes, 38.7 s | 39.2 s | **0.45 s** |
| 2B beam-slab, all four deficiencies | GM1 | 4.5 | 10.9 s | front pier F crushes, 20.1 s | 25.0 s | **4.9 s** |
| | GM2 | 3.0 | 12.1 s | front pier F crushes, 43.5 s | 51.1 s | **7.6 s** |
| | GM3 | 3.75 | 10.8 s | front pier F crushes, 15.1 s | 27.2 s | **12.1 s** |

**Over all collapse searches (v2.0).**

| | As-built flat slab | Beam-slab |
|---|---|---|
| Collapse, seconds into the record (median, range) | 44.9 s (20.5–64.1 s) | 27.2 s (15.9–60.5 s) |
| From the first core-wall crushing to the 0.6 m drop (median) | **0.45 s** (almost free fall) | **6.1 s** |
| Typical first event | link beams fail at 6–8 s, then the front pier crushes or the upper floors punch | link beams fail at 8–12 s, then the front pier crushes |

**What the timing means.**

* **The link beams always go first**, a few seconds into the strong shaking, in both framings.
* **Flat slab: once the front pier crushes, the core falls within about half a second.** Nothing in the floor can hold it up. When the core is strong enough (no deficiencies), the flat slab instead fails by punching that spreads over 25–35 s on the upper floors.
* **Beam-slab: after the same pier crushes, the beams hang the core from the columns for 5–12 s.** The building comes down only after continued shaking. This is the "slower, more localised failure propagation" the proposal hypothesised.
* **No run collapses at SF = 1** (the actual 2025 shaking), in either framing or with any deficiency combination. The peak drift at SF = 1 is 0.4–0.6 % in the as-built and 0.25–0.35 % in the beam-slab.
* **Version 1 comparison.** Same pattern, but the beam-slab with the 25 %-capped beam–core connections held the core for only about 0.6 s. The full beam–core moment connection in v2.0 is what buys the extra seconds.
* **Caveat.** Three of the v2.0 collapse levels in the table rest on runs that stopped without any recorded element failure (a numerical stop or an OpenSees abort). Under the protocol these count as collapse, so those brackets are conservative (lower bounds).
