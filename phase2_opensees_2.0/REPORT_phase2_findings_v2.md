# Phase 2 – Version 2.0 findings (revised framing, 250 mm slab in both models)

## What changed from version 1

| | Version 1 (`../phase2_opensees`) | Version 2.0 (this folder) |
|---|---|---|
| As-built flat-slab thickness | 300 mm | **250 mm** (same as the beam-slab slab) |
| Plan corners (no columns) | floor not framed to the corners | **corner cantilevers**, 5.5 m, along both edges: slab strips in the as-built, 500 × 800 beams in the beam-slab |
| Beams framing into the core walls (beam-slab) | wall-end moment capped at 25 % | **fully moment-connected**, like every other beam |
| Slab extent | whole plate except the core shafts | same |
| Design, ground motions, deficiencies, analysis settings | – | unchanged |
| Collapse-search rule (applied to **both** versions) | any non-convergence = collapse | a non-convergence with **no element failure and drift < 3 %** is a numerical stop, repeated at dt = 0.01 s; a run that crashes OpenSees is treated the same way |

The rule change left version 1 unchanged: its one affected run (beam-slab with no deficiency, GM3, SF 8) collapses again at dt = 0.01 s. It corrected two false early collapses in version 2.0 (as-built D1+D2 and D2+D3).

**Models.**

| | Weight | T1 / T2 / T3 (s) | Storey-1 front pier P/(A·f′c), no def. → all four |
|---|---|---|---|
| As-built 250 mm | 496 MN | 6.11 / 4.98 / 2.51 | 0.15 → 0.23 |
| Beam-slab | 580 MN | 4.19 / 4.17 / 2.06 | 0.18 → 0.27 |

SF = 1 is the reconstructed 2025 Bangkok shaking. A collapse level such as "3.75–4.5" means the model stood at SF 3.75 and collapsed at SF 4.5.

---

## 1. The 2025-level shaking (SF = 1, GM1)

All 32 variants **survive** in both framings.

| | As-built 250 mm | Beam-slab |
|---|---|---|
| Peak corner drift | 0.38–0.56 % | 0.24–0.35 % |
| Roof twist | 0.011–0.013 rad | 0.006–0.007 rad |
| Highest wall shear demand / capacity | 0.34–0.62 | 0.48–0.74 |
| Wall, column or punching failures | none | none |

**Severity ladder at SF = 1.** All four deficiencies, with wall f′c down to 35 % and le/ld down to 0.10: **everything survives**. Peak drift is 0.58–0.73 % in the as-built and 0.35–0.39 % in the beam-slab.

---

## 2. Collapse intensity

### 2.1 Record GM1

| Deficiencies | As-built 250 mm | Beam-slab | Better | (version 1: as-built / beam-slab) |
|---|---|---|---|---|
| none | 6.0–7.0 | > 8 | **beam-slab** | 7–8 / > 8 |
| D1 | 6.0–7.0 | 5.25–6.0 | as-built | 6–7 / 7–8 |
| D2 | 4.5–5.25 | > 8 | **beam-slab** | 6–7 / > 8 |
| D3 | 6.0–7.0 | 7.0–8.0 | **beam-slab** | 7–8 / > 8 |
| D4 | 6.0–7.0 | 4.5–5.25 | as-built | 6–7 / 3.75–4.5 |
| D1+D2 | 4.5–5.25 | 7.0–8.0 | **beam-slab** | 6–7 / 7–8 |
| D1+D3 | 6.0–7.0 | 5.25–6.0 | as-built | 6–7 / 6–7 |
| D1+D4 | 4.5–5.25 | 3.75–4.5 | as-built | 4.5–5.25 / 3.75–4.5 |
| D2+D3 | 4.5–5.25 | > 8 | **beam-slab** | 6–7 / 7–8 |
| D2+D4 | 5.25–6.0 | 3.75–4.5 | as-built | 5.25–6 / 3–3.75 |
| D3+D4 | 6.0–7.0 | 4.5–5.25 | as-built | 5.25–6 / 3.75–4.5 |
| D1+D2+D3 | 4.5–5.25 | 6.0–7.0 | **beam-slab** | 6–7 / 6–7 |
| D1+D2+D4 | 3.75–4.5 | 3.75–4.5 | equal | 4.5–5.25 / 3–3.75 |
| D1+D3+D4 | 4.5–5.25 | 3.75–4.5 | as-built | 4.5–5.25 / 3.75–4.5 |
| D2+D3+D4 | 5.25–6.0 | 3.75–4.5 | as-built | 4.5–5.25 / 3.75–4.5 |
| **all four** | **3.75–4.5** | **3.75–4.5** | **equal** | 3.75–4.5 / 3–3.75 |

* **Without D4:** the beam-slab is better in 6 of 8 combinations. In the 2 where it is worse (D1, D1+D3) the gap is one step. Every combination where D2 (weak link-beam anchorage) is present without D4 favours the beam-slab, often by 2–3 steps. Its beams take over the coupling that the failing link beams lose.
* **With D4:** the as-built is better in 6 of 8 combinations and equal in 2 (D1+D2+D4, all four).

### 2.2 Effect of each deficiency (factor on the collapse SF, GM1)

| | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| As-built 250 mm | 0.86 | **0.80** | ≈ 1 | 0.92 |
| Beam-slab | 0.79 | ≈ 1 | ≈ 1 | **0.56** |

* For the flat slab, the most damaging deficiency is **D2**, the link-beam anchorage. The core loses its coupling and the slab cannot replace it.
* For the beam-slab, it is **D4**, the under-designed and unconfined walls. The stiff frame drives more shear into those walls.

### 2.3 Records GM1 / GM2 / GM3

| | GM1 | GM2 | GM3 |
|---|---|---|---|
| As-built, no deficiency | 6.0–7.0 | 6.0–7.0 | 5.25–6.0 |
| Beam-slab, no deficiency | > 8 | 7.0–8.0 | > 8 |
| As-built, all four | 3.75–4.5 | 3.75–4.5 | 3.0–3.75 |
| Beam-slab, all four | 3.75–4.5 | 2.5–3.0 | 3.0–3.75 |

* **No deficiency:** the beam-slab is better on every record, by 1–3 steps.
* **All four:** the two are equal on GM1 and GM3; the beam-slab is one step worse on GM2.

### 2.4 Intensified D1 / D2 (f′c × 0.50, le/ld = 0.30, all four deficiencies)

| | Version 1 | Version 2.0 |
|---|---|---|
| As-built | 1.5–1.75 | **3.75–4.5** |
| Beam-slab | 2.5–3.0 | 3.0–3.75 |

The 53 MN lighter 250 mm flat slab lowers the axial load on the weakened front pier. That removes the as-built's early collapse in this case.

---

## 3. How collapse starts and propagates

| First failure in the collapse run | As-built 250 mm (21 searches) | Beam-slab (17 searches with collapse) |
|---|---|---|
| Storey-1 front pier F crushes | 10 | 15 |
| Punching on the upper floors (29–33) | 9 | – (no punching mode) |
| Other wall failure | – | 1 |
| Solver stop or crash with no element failure (counted as collapse under the rule) | 2 | 1 |

**Time from front-pier crushing to a 0.6 m drop.**

* As-built: median **0.45 s** (range 0.42–0.50 s).
* Beam-slab: median **6.1 s** (range 0.6–12 s).

With fully moment-connected beams into the core, the beam-slab **holds the core up for seconds after the pier crushes**. The core above is carried through the beams to the columns, and it comes down only under further shaking. In version 1 this took 0.65 s.

---

## 4. Lateral strength (pushover)

| | As-built 250 mm | Beam-slab | Ratio |
|---|---|---|---|
| Peak base shear, X | 16.1–18.3 MN (3.3–3.7 % W) | 43.0–48.8 MN (7.6–8.4 % W) | **≈ 2.6×** |
| Peak base shear, Y | 5.6–8.8 MN (1.1–1.8 % W) | 22.1–26.9 MN (3.9–4.7 % W) | **≈ 3×** |

The thinner slab lowers the as-built's strength by about 15–20 % compared with version 1. The corner cantilevers and full beam–core connections raise the beam-slab's by about 10–20 %.

---

## 5. Loss of core piers (alternate load paths)

**Sudden removal under gravity.**

| Scenario | As-built 250 mm, no def. | As-built, all 4 | Beam-slab, no def. | Beam-slab, all 4 |
|---|---|---|---|---|
| S1 front pier F, storey 1 | collapse | collapse | **stands** (37 mm) | **stands** (64 mm) |
| S2 F, storeys 1–4 | collapse | collapse | **stands** (38 mm) | **stands** (63 mm) |
| S6 middle pier M | stands (18 mm) | collapse | stands (16 mm) | **stands** (22 mm) |
| S7 rear pier R | collapse | collapse | **stands** (20 mm) | **stands** (22 mm) |
| S3 F + M, storeys 1–4 | collapse | collapse | **stands** (119 mm) | **stands** (122 mm) |
| S5 whole core, storey 1 | collapse | collapse | collapse | stands (159 mm)* |
| S4 whole core, storeys 1–4 | collapse | collapse | collapse | stands (159 mm)* |

* **Single-pier losses:** the beam-slab stands in **8 of 8**; the as-built in **1 of 8**.
* **Two-pier loss:** the beam-slab stands; the as-built collapses.
* After losing the front pier, the beam-slab's storey-1 columns pick up **79–106 %** of the lost load (55–65 MN). After losing the middle pier, the flat slab passes only 11 % to the columns.
* \*The whole-core cases are borderline. The beam-slab stands with all four deficiencies, because the thinner D3 walls weigh less, but collapses without them. Both results rely on the beams developing their full moment at the core walls.

**Pushdown (gradual withdrawal of one pier's support).**

* Floor route when the front pier is lost: **43–69 MN** in the beam-slab against **12–18 MN** in the flat slab (**about 3–4×**).
* Pseudo-static capacity λps ≥ 1, meaning the building should survive a sudden loss:
  * beam-slab: 7 of 8 cases (all but the front pier at storey 1 with all four deficiencies, 0.70);
  * flat slab: 0 of 8.

---

## 6. Answers to the questions (version 2.0)

* **2A-Q1 – Does the model reproduce the collapse?**
  * **Mechanism: yes.** Failure starts at the storey-1 front core pier and the core drops; the flat slab also fails by punching on the upper floors.
  * **Intensity: no.** Nothing collapses at the 2025 level. With all four deficiencies, collapse needs 3–4.5× the reconstructed shaking.
* **2A-Q2 – Single deficiencies vs interaction:** supported.
  * No single deficiency collapses the as-built near the 2025 level; single ones give 4.5–7×.
  * All four together give 3–4.5×.
* **2A-Q3 – Local core failure and the column-slab system:** supported.
  * The 250 mm flat slab collapses in 7 of 8 single-pier losses, in 0.4–0.6 s.
  * It carries only 12–18 MN through the floor to the columns.
* **2B-Q4 – Does failure propagate differently?** Yes.
  * In the beam-slab it is slower: seconds rather than about 0.5 s after the front pier crushes.
  * It is more localised: the building stands after any single-pier loss and after the loss of two piers.
  * There is no punching cascade.
* **2B-Q5 – How much load is redistributed?**
  * After a front-pier loss, the beams carry 43–69 MN, and the columns pick up 79–106 % of the lost load.
  * The link-beam route through the core carries 0–29 MN.
* **2B-Q6 – Stable state after localised damage?** **Yes.**
  * Every single-pier and two-pier loss ends in a stable state, settling 16–122 mm.
  * In the flat slab only 1 of these 10 cases does.

## 7. Overall conclusion

* **Robustness after local core failure:** the beam-slab is decisively better, more so than in version 1. With full beam–core moment connections and corner cantilevers, it bridges the loss of one or two core piers that the flat slab cannot survive.
* **Seismic collapse:**
  * The beam-slab is better when the core walls meet the code (no D4). This holds on all three records without deficiencies, and especially when the link beams are deficient (D2).
  * With the documented under-designed walls (D4), the lighter, more flexible flat slab delays collapse by about one step. With all four deficiencies the two are equal or within one step.
* **At the 2025 shaking level:** neither framing collapses with any combination of deficiencies.

**The proposition holds for failure propagation and stability after damage.** For the initiation of collapse under shaking, the documented wall deficiencies (D4), together with the link-beam anchorage (D2) in the flat slab, matter more than the framing.

## Limitations

The limitations listed in version 1 still apply:

* three spectrally matched synthetic records;
* assumed D1 / D2 severities;
* lumped-plasticity idealisations;
* no construction-stage effects.

In addition, version 2.0:

* assumes full moment transfer between the beams and the 250–300 mm core walls;
* uses an unchanged design basis (no re-design for the 250 mm flat slab or for the corner cantilevers);
* has one collapse level that rests on a run that crashed OpenSees (as-built, no deficiency, GM1, SF 7).
