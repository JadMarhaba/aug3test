# Phase 2 – Nonlinear findings (2A as-built flat slab vs 2B proposed beam-slab)

All results below come from the corrected code: Rayleigh damping verified at 2.4–2.6 % against the 2.5 % target, beam-hinge hogging/sagging signs fixed, the ASCE 41 wall-rotation integration fixed, per-step solver-sanity checks, and the strengthened pushover solver. Earlier results are archived in `results/old/`.

Scale factor **SF = 1 is the reconstructed 28 March 2025 shaking in Bangkok**. On the same scale, the DPT design earthquake is about SF 2.7–3 and the MCE about SF 4. A collapse level given as "3.0–3.75" means the model stood at SF 3.0 and collapsed at SF 3.75.

**Analyses run.**

| Analysis | Runs |
|---|---|
| Response histories (earthquake time-history analyses) | 258 |
| Collapse-intensity searches | 42 |
| Severity-ladder runs (D1 / D2 intensified) at SF = 1 | 8 |
| Pushovers (both directions, all 32 variants) | 64 |
| Pushdowns | 16 |
| Sudden-removal analyses | 28 |

The 42 collapse searches cover:

* 16 deficiency variants × 2 framings, record GM1;
* records GM2 and GM3 for the reference and all-four variants of each framing;
* the all-four variant with intensified D1 / D2.

---

## 1. Response to the 2025-level shaking (SF = 1, GM1, all 32 variants)

| | As-built flat slab (16 variants) | Proposed beam-slab (16 variants) |
|---|---|---|
| Outcome | **all survive** | **all survive** |
| Peak storey drift (building corner) | 0.36–0.52 % | 0.25–0.33 % |
| Roof twist (torsion) | 0.010–0.013 rad | 0.006–0.007 rad |
| Highest wall shear demand / capacity | 0.38–0.67 | 0.42–0.64 |
| Wall shear or axial failures, punching, column failures | none | none |
| Link-beam failures | 0–12 (only in variants with D2) | none |

**Severity ladder at SF = 1.** All four deficiencies were applied, with D1 and D2 intensified step by step, using the same values in both framings:

* f′c / specified: 0.60 → 0.50 → 0.40 → 0.35;
* bar embedment le/ld: 0.40 → 0.30 → 0.20 → 0.10.

**Every step survives in both framings.** Peak drift reaches 0.48–0.59 % in the as-built and 0.34–0.39 % in the beam-slab.

---

## 2. Collapse intensity (SF at collapse)

### 2.1 All 16 deficiency combinations (record GM1)

| Deficiencies | As-built flat slab | Proposed beam-slab | Better framing |
|---|---|---|---|
| none (REF) | 7.0–8.0 | > 8.0 (stood at 8) | beam-slab |
| D1 | 6.0–7.0 | 7.0–8.0 | beam-slab |
| D2 | 6.0–7.0 | > 8.0 | beam-slab |
| D3 | 7.0–8.0 | > 8.0 | beam-slab |
| D4 | 6.0–7.0 | **3.75–4.5** | **as-built** |
| D1+D2 | 6.0–7.0 | 7.0–8.0 | beam-slab |
| D1+D3 | 6.0–7.0 | 6.0–7.0 | equal |
| D1+D4 | 4.5–5.25 | 3.75–4.5 | as-built |
| D2+D3 | 6.0–7.0 | 7.0–8.0 | beam-slab |
| D2+D4 | 5.25–6.0 | 3.0–3.75 | as-built |
| D3+D4 | 5.25–6.0 | 3.75–4.5 | as-built |
| D1+D2+D3 | 6.0–7.0 | 6.0–7.0 | equal |
| D1+D2+D4 | 4.5–5.25 | 3.0–3.75 | as-built |
| D1+D3+D4 | 4.5–5.25 | 3.75–4.5 | as-built |
| D2+D3+D4 | 4.5–5.25 | 3.75–4.5 | as-built |
| **all four** | **3.75–4.5** | **3.0–3.75** | as-built |

**The pattern splits on D4.**

* Without D4 (8 combinations): the beam-slab is better in 6 and equal in 2.
* With D4 (8 combinations): the as-built is better in all 8, by one to two SF steps.

### 2.2 Effect of each deficiency (factorial analysis of ln SF_collapse, GM1)

| Factor on collapse SF | D1 | D2 | D3 | D4 | Largest interaction |
|---|---|---|---|---|---|
| As-built | 0.88 | 0.91 | 0.94 | **0.76** | ±6 % |
| Beam-slab | 0.84 | 0.89 | 0.95 | **0.47** | +13 % (D1×D4) |

* D4 (non-compliant design: no dynamic shear amplification, no confined boundary zones) is by far the most damaging deficiency. It costs the beam-slab more than half of its collapse capacity.
* The interaction terms are small, so the deficiencies combine roughly multiplicatively. For the as-built: 0.88 × 0.91 × 0.94 × 0.76 = 0.57, and 7.5 × 0.57 ≈ 4.3, against 4.1 found.

### 2.3 Record-to-record check (GM2, GM3)

| | GM1 | GM2 | GM3 |
|---|---|---|---|
| As-built, no deficiency | 7.0–8.0 | 6.0–7.0 | 6.0–7.0 |
| Beam-slab, no deficiency | > 8.0 | > 8.0 | 7.0–8.0 |
| As-built, all four | 3.75–4.5 | 3.75–4.5 | 3.0–3.75 |
| Beam-slab, all four | 3.0–3.75 | 3.0–3.75 | 3.0–3.75 |

* Without deficiencies, the beam-slab is one step better on all three records.
* With all four deficiencies, the beam-slab is one step worse on GM1 and GM2 and equal on GM3. The difference is small: one bisection step of the search.

### 2.4 Intensified D1/D2 (f′c × 0.50, le/ld = 0.30, all four deficiencies)

| | As-built | Beam-slab |
|---|---|---|
| Collapse SF | **1.5–1.75** | **2.5–3.0** |

When the concrete and anchorage deficiencies are severe rather than D4-dominated, the ranking reverses: the beam-slab withstands about 1.7× the shaking that collapses the as-built.

---

## 3. How collapse starts and propagates (the collapse run of every search)

| Initiating failure | As-built (21 collapses) | Beam-slab (17 collapses) |
|---|---|---|
| Storey-1 front pier F crushes, then the core drops | 12 | 13 |
| Punching of slab–column connections (floors 29–32; floor 1 for D1+D3+D4), spreading until equilibrium is lost | 8 (REF on all three records, D2, D3, D4, D2+D3, D1+D3+D4) | – (no punching mode) |
| Other wall failure (storey-2 pier M crushing, top-storey or storey-1 shear failure) | 1 | 3 |
| Non-convergence without a recorded failure | – | 1 (REF, GM3, SF 8) |

* **Location.** The dominant mechanism is the same in both framings. The **storey-1 front wall pier (F)** carries the highest gravity axial load in the core (P/A·f′c = 0.17 reference, 0.26 with all four deficiencies). It crushes at about −0.6 % average axial strain, and the core above it drops vertically.
* **Speed.**
  * From pier crushing to a 0.6 m drop: median **0.48 s** in the as-built (range 0.45–0.57 s) and **0.65 s** in the beam-slab (0.54–1.92 s).
  * In the sudden-removal tests the same difference appears: 0.55 s against 0.82 s for the front pier with all four deficiencies.
  * The beam-slab slows the collapse but does not stop it once the front pier is lost during strong shaking with deficient walls.
* **Flat-slab-specific mechanism.** When the core is *not* the weak link (reference, D2, D3), the as-built instead fails by **punching of the upper-floor slab–column connections**. The punching then spreads to as many as about 130 connections. The beam-slab has no equivalent mechanism.

---

## 4. Lateral strength (pushover, first-mode-like load pattern)

| | As-built flat slab | Proposed beam-slab |
|---|---|---|
| Peak base shear, X | 19.9–22.5 MN (3.7–4.1 % W) | 36.2–40.9 MN (6.5–7.2 % W), **~1.8×** |
| Peak base shear, Y | 7.5–10.3 MN (1.4–1.9 % W) | 19.5–22.4 MN (3.5–3.9 % W), **~2.2×** |
| Core share of base shear at peak (X) | 60–66 % | 41–56 % |
| First serious failure (X) | punching at floors 13–15, roof drift 0.9–1.1 % | storey-1 pier axial failure at 0.6–1.7 % (variants with D1); no punching mode |

The beam-slab frame roughly doubles lateral strength and halves torsion. It also takes a larger share of the base shear away from the core. Even so, the beam-slab's core walls receive *higher* shear in the response histories: at SF 3 with all four deficiencies, 73 % vs 65 % of capacity in storey 1 and 86 % vs 76 % in storey 2. The stiffer frame restrains the core into a shear-type deformed shape, which raises shear at the base. With D4 walls that extra shear is what lowers the beam-slab's collapse intensity.

Pushover curves end at the first core-pier axial failure, or where the solution diverges (`run_03_postprocess.py`, `po_curve`).

---

## 5. Load redistribution after local core failure

Full details are in `REPORT_alp.md`.

| | As-built | Beam-slab |
|---|---|---|
| Survives a sudden single-pier loss (8 cases) | **1 of 8** | **6 of 8** |
| Front pier lost, no deficiency | collapses in 0.68 s | stands; settles 133 mm; 97 % of the 63 MN goes to the storey-1 columns |
| Pushdown capacity λmax with all four deficiencies | 0.69–1.01 | 0.91–1.14 (12–52 % higher) |
| Load carried by the floor system at peak, storey-1 front pier lost | 20–26 MN | 60–65 MN |
| Two piers or the whole core lost | collapses (0.41–0.49 s) | collapses (0.48–0.60 s) |

---

## 6. Answers to the research questions

### Phase 2A – as-built flat slab

**Q1. Can the as-built model reproduce the documented collapse?**
*Partly.*

* **Mechanism reproduced.** Failure starts in the lower core, at the storey-1 front pier. The core then drops and the instability becomes global within about half a second.
* **Intensity not reproduced.** At the reconstructed 2025 shaking (SF 1), every deficiency combination survives with drifts below 0.6 % and wall shear below 70 % of capacity. This holds even with wall concrete at 35 % of specification and link-beam anchorage at 10 %.
* **Shaking needed to collapse.** With the documented deficiencies at the assumed severity, collapse needs at least 3.0–3.75× the reconstructed shaking. With D1/D2 intensified it needs 1.5–1.75×.
* **What this implies.** The model does not explain the collapse as an outcome of the 2025 shaking acting on the completed building with these deficiencies alone. At least one of the following must also be involved:
  * the site motion was stronger than reconstructed;
  * the deficiencies were more severe than assumed;
  * construction-stage conditions;
  * a mechanism not represented in the model.

**Q2. Can individual deficiencies cause global instability, or is interaction required?**
*Hypothesis supported.*

* No single deficiency brings the as-built near collapse at the 2025 level. Single deficiencies reduce the collapse SF only from about 7.5 to, at worst, about 6.5.
* All four together reduce it to about 4.1. Severe D1/D2 on top reduce it to about 1.6.
* The deficiencies act cumulatively, roughly multiplicatively, rather than through strong synergy.
* The framing also interacts with D4 (see Q4).

**Q3. How does local core failure affect the column-slab system and the global load path?**
*Hypothesis supported.*

* When a lower-core pier fails, the flat slab transfers little of the lost load to the columns: 18 % for the middle pier, and 20–26 MN of the 53–60 MN for the front pier.
* It collapses in 7 of 8 single-pier-loss cases, typically within 0.5–0.7 s.
* The limited alternate load path accelerates the collapse.

### Phase 2B – proposed beam-slab

**Q4. Under identical loading, does failure propagate differently?**
*Yes, but not always in the hypothesised direction.*

* **Where the hypothesis holds.**
  * Propagation is slower: 0.65 s against 0.48 s from initiation to a 0.6 m drop.
  * Failure is more localised after a pier loss: the beam-slab stands in 6 of 8 cases.
  * The as-built's upper-floor punching cascades disappear.
* **Where it does not.** Under seismic shaking with D4 walls, the beam-slab's stiffer frame drives *more* shear into the base of the core. Failure then starts at a *lower* intensity: 3.0–3.75 against 3.75–4.5 with all four deficiencies.

**Q5. How much load is redistributed into beams, columns, slabs and core?**

* **Core route (link beams to the other piers).** 29–64 MN in both framings; D2 roughly halves it.
* **Floor route (to the columns).**
  * Beam-slab: 60–65 MN when the storey-1 front pier is lost, against 20–26 MN through the flat slab (2.5–3×).
  * Rear pier: 19 MN against 6 MN.
  * After a sudden front-pier loss without deficiencies, the beam-slab's storey-1 columns pick up 97 % of the lost 63 MN.

**Q6. Does the beam-slab retain a stable load-carrying state after localised damage?**

* **After the loss of a single lower-core pier under gravity: yes, in most cases.** The beam-slab survives 6 of 8 cases against 1 of 8 for the flat slab, and it is the only framing that survives losing the heaviest (front) pier.
* **After the loss of two piers, the whole core, or the front pier during strong shaking with deficient walls: no.** Neither framing survives these.

### Overall proposition

Two findings hold together:

* **Framing strongly controls the post-failure redistribution.** The beam-slab arrests single-pier losses that collapse the flat slab, carries 2–3× more load through the floor, roughly doubles lateral strength and halves torsion.
* **The documented deficiencies, above all D4 (under-designed, unconfined core walls), control the seismic collapse intensity.** With D4 present, the beam-slab is **not** safer under earthquake shaking: it collapses at about the same intensity or one step lower. Without D4, or with severe D1/D2, it is safer.

In the proposal's terms: the beam-slab supports the proposition for alternate load paths and stability after localised damage. For the seismic initiation of collapse in this building, the documented deficiencies are more influential than the framing configuration. The beam-slab helps only if the core walls are designed to the code, including the dynamic shear amplification.

---

## 7. Limitations

* **Ground motions.** Three synthetic records, spectrally matched to a *reconstructed* 2025 spectrum, scaled uniformly. Collapse levels are resolved only to one bisection step (≤ 20 %).
* **Deficiency severities.** D1 and D2 severities are assumptions; the official findings confirm the deficiencies but not their magnitude. D3 and D4 follow the design basis in `results/design.json`.
* **Model idealisations.**
  * The flat slab uses effective-width strips.
  * Hinges are lumped.
  * Wall piers are removed at −0.6 % average strain or at the ASCE 41 limit b.
  * Punching follows the ACI 318-19 drift rule for post-tensioned slabs.
  * Construction-stage loads, partial completion, soil–structure interaction and any lift-core details beyond the three piers are not modelled.
* **Non-convergence.** Under the collapse protocol non-convergence counts as collapse. One beam-slab run (REF, GM3, SF 8) stopped without any recorded element failure. Several pushovers end on non-convergence after their peak.

---

## Files

All paths are under `phase2_opensees/`.

* Tables: `results/summary/`
  * T1 – SF 1 deficiency matrix
  * T2 – pushover capacity
  * T3 – sudden removal
  * T4 / T7 – collapse intensity
  * T5 / T8 – factorial effects
  * T6 – pushdown
* Figures: `figures/fig01`–`fig11`
* Load-redistribution write-up: `REPORT_alp.md`
* Methods: `REPORT_methods.md`
* Raw results: `results/nlth/`, `results/pushover/`, `results/pushdown/`, `results/removal/`
* Models:
  * `phase2A_asbuilt_flatslab_model.py`
  * `phase2B_proposed_beamslab_model.py`
  * shared parts in `sao/`
