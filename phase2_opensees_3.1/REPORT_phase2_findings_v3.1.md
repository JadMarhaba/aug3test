# Phase 2 – Version 3.1 findings (calibrated periods, 1.7 m coupling beams)

Version 3.1 is version 2.0 recalibrated to the researched Bangkok periods and shaking. The aim was to see how collapse develops at lower intensity. The full batch is complete:

* 42 collapse searches (288 response histories);
* 28 sudden core-pier removals and 8 pushdowns;
* 64 pushovers;
* the severity ladder at the 2025 level.

## What changed from version 2.0

Both models are changed in the same way. Geometry is identical outside the beams; the as-built slab is post-tensioned and the beam-slab slab is not.

| Item | v2.0 | v3.1 |
|---|---|---|
| Link (coupling) beams over the 4 core openings | 300 × 500 mm, 0.20 EI | **300 × 1700 mm** (storey height minus lift door), **0.50 EI** |
| As-built PT flat slab stiffness | cracked (β = 0.5) | **uncracked (β = 1.0)**: low-intensity shaking |
| Beam-slab RC beams | 0.35 EI | 0.35 EI (unchanged) |
| Slab | 250 mm in both | 250 mm in both |
| Ground motions (SF = 1 = the 2025 event) | 0.08 g peak at 1.3 s | **peaks at 1.6 s (0.085 g), 2.8 s (0.070 g), 6.3 s (0.052 g)**; PGA 0.027–0.032 g, PGV 13–17 cm/s, 120 s long, 80–90 s strong-shaking duration |
| Collapse-search ladder | from 1.0× | **from 0.5×** (0.5, 1, 1.5, 2, 3, 4.5, 6, 8), then bisection to 20 % |

**Periods (s)**

| Model | T1 | T2 | T3 | Weight |
|---|---|---|---|---|
| As-built, no deficiency | 3.24 | 3.05 | 1.88 | 496 MN |
| As-built, all 4 deficiencies | 3.65 | 3.56 | 2.13 | 484 MN |
| Beam-slab, no deficiency | 3.04 | 2.91 | 1.80 | 580 MN |
| Beam-slab, all 4 deficiencies | 3.33 | 3.26 | 1.98 | 568 MN |

The researched range for Bangkok towers of this height is about 2.7–3.3 s; the Thai code gives 0.02H = 2.74 s. Getting to about 2 s would need thicker core walls.

**Important.** An SF in v3.1 is a multiple of a different, longer, more long-period-rich record than in v2.0. So an SF of 3 in v3.1 is not the same shaking as an SF of 3 in v2.0.

---

## 1. The 2025-level shaking (SF = 1)

* **Nothing collapses** in any of the 32 combinations on GM1, for either framing.
* Peak storey drift at the corners is **0.30–0.35 %** everywhere.
* There are no link-beam failures, wall shear failures, wall axial failures, punching or column failures.
* The worst wall shear demand is 55–86 % of capacity.

**The severity ladder** keeps all four deficiencies at the 2025 level and makes D1 and D2 much worse than documented. Even then, nothing collapses:

| Severity (f′c ratio, le/ld) | As-built peak drift | Beam-slab peak drift | Link beams failed (of 132), A / B |
|---|---|---|---|
| 0.60 / 0.40 | 0.40 % | 0.31 % | – |
| 0.50 / 0.30 | 0.69 % | 0.35 % | – |
| 0.40 / 0.20 | 1.33 % | 0.50 % | 119 / 81 |
| 0.35 / 0.10 | 1.15 % | 0.82 % | 126 / 107 |

* With extreme D2, almost every link beam pulls out at the 2025 level. The core still stands, as three separate piers.
* At the 2025 level the beam-slab sways **about 1.3–2.7× less** than the as-built in every ladder case.

**So the models still do not collapse at the 2025 intensity.** On the reconstructed shaking, the documented deficiencies (or much worse ones) are not enough on their own. Something not in the models would be needed, for example:
* a much stronger local motion;
* construction-stage or other defects not documented;
* a lower-storey pier already damaged before the event;
* a failure mode the models do not represent.

---

## 2. Collapse intensity (how much stronger than 2025 the shaking must be)

### 2.1 GM1, all 16 deficiency combinations

The values are SF brackets: highest SF survived → lowest SF that collapsed.

| Deficiencies | As-built | Beam-slab | Higher |
|---|---|---|---|
| none | 4.5 → 5.25 | 3.75 → 4.5 | As-built |
| D1 | 3.75 → 4.5 | 3.0 → 3.75 | As-built |
| D2 | 3.0 → 3.75 | 3.0 → 3.75 | equal |
| D3 | 4.5 → 5.25 | 3.75 → 4.5 | As-built |
| D4 | 2.5 → 3.0 | 3.0 → 3.75 | Beam-slab |
| D1+D2 | 3.0 → 3.75 | 2.5 → 3.0 | As-built |
| D1+D3 | 2.5 → 3.0 | 3.0 → 3.75 | Beam-slab |
| D1+D4 | 2.5 → 3.0 | 2.5 → 3.0 | equal |
| D2+D3 | 3.0 → 3.75 | 3.0 → 3.75 | equal |
| D2+D4 | 2.5 → 3.0 | 2.5 → 3.0 | equal |
| D3+D4 | 2.5 → 3.0 | 3.0 → 3.75 | Beam-slab |
| D1+D2+D3 | 3.0 → 3.75 | 2.5 → 3.0 | As-built |
| D1+D2+D4 | 3.0 → 3.75 | 2.0 → 2.5 | As-built |
| D1+D3+D4 | 2.0 → 2.5 | 2.5 → 3.0 | Beam-slab |
| D2+D3+D4 | 3.0 → 3.75 | 2.0 → 2.5 | As-built |
| all four | 3.0 → 3.75 | 2.0 → 2.5 | As-built |

### 2.2 GM1 / GM2 / GM3 for the two key cases

| Case | GM1 | GM2 | GM3 |
|---|---|---|---|
| As-built, no deficiency | 4.5 → 5.25 | 3.0 → 3.75 | 3.75 → 4.5 |
| Beam-slab, no deficiency | 3.75 → 4.5 | 4.5 → 5.25 | 3.75 → 4.5 |
| As-built, all four | 3.0 → 3.75 | 2.0 → 2.5 | 2.0 → 2.5 |
| Beam-slab, all four | 2.0 → 2.5 | 2.0 → 2.5 | 2.5 → 3.0 |

**Intensified D1/D2** (f′c × 0.50, le/ld = 0.30, all four, GM1): as-built **2.0 → 2.5**, beam-slab **1.5 → 1.75**.

### 2.3 Summary

Collapse-SF estimates are the geometric mean of each bracket.

| Group | As-built | Beam-slab |
|---|---|---|
| No deficiency (3 records) | 4.06 | 4.35 |
| Single deficiencies | 3.68 | 3.53 |
| Pairs | 2.93 | 3.03 |
| Triples | 3.03 | 2.48 |
| All four (3 records) | 2.56 | 2.40 |
| **All 20 searches** | **3.18** | **3.06** |

* Across the 20 matched searches: **as-built higher in 8, beam-slab higher in 6, equal in 6.**
* The differences are mostly one bracket step (about 20 %), which is the resolution of the search.
* **Under earthquake shaking alone, the two framings collapse at statistically the same intensity in v3.1.** There is a slight tilt toward the as-built in the multiply-deficient cases.
* In v2.0 the beam-slab was clearly stronger without deficiencies (7–8× against 5.6–6.5×). That advantage has gone.

### 2.4 Effect of each deficiency (factor on the collapse SF, GM1)

| Deficiency | As-built | Beam-slab |
|---|---|---|
| D1 weak wall concrete | 0.91 | 0.84 |
| D2 short link-beam embedment | 1.01 | 0.80 |
| D3 walls 300 → 250 mm | 0.95 | 0.97 |
| D4 non-compliant wall design | **0.78** | **0.80** |

* **D4 is the most damaging single deficiency in both models.** It means no dynamic shear amplification and unconfined boundaries.
* D2 matters for the beam-slab and not for the as-built. In the beam-slab, the collapse runs through the core piers, and the link beams tie them together.
* Interactions are small (factors 0.9–1.2) and inconsistent in sign. Deficiencies roughly multiply; they do not amplify each other strongly.

---

## 3. How collapse starts (the mechanism differs)

Each collapse case is classified by its first severe failure:

| Framing | First severe failure in the collapsing run |
|---|---|
| As-built (20 collapses) | **punching** of the flat slab in 13; wall axial failure in 3; none (non-convergence only) in 4 |
| Beam-slab (20 collapses) | **storey-1 core-pier axial failure** in 17 (mostly the front pier F); wall shear strength loss in 3 |

* **As-built.** Link beams fail early (12–16 s). The building then reaches about 2–3 % drift and the flat slab punches. Punching is mostly on the upper floors (L13–L14 at columns) or at the slab–core joints. The run loses stability within a fraction of a second.
  * The no-deficiency cases collapse 19–101 s into the record. The all-four case on GM1 collapses at 25 s: storey-2 middle pier and slab–core punching, 0.5 s apart.
  * Four as-built "collapses" have no recorded failure. They stopped on numerical grounds twice (also at dt = 0.01 s) and are counted as collapse by the conservative rule. In these four cases the as-built collapse SF may be underestimated.
* **Beam-slab.** Link beams also fail early, but the building then rocks for a long time. A **storey-1 core pier crushes** (the front pier in all but one case) 57–83 s into the record, and the core drops about 1–18 s later. This is the mechanism investigators reported for SAO: lower core, front pier first.
* **Why the beam-slab core fails first:**
  * The beam-slab is **17 % heavier** (580 vs 496 MN): beam stems on every line.
  * Its beams frame into the core with full moment, so the core carries **15 % more gravity load** (169 vs 147 MN at storey 1).
  * The front pier's gravity axial ratio is 0.18 against 0.15 with no deficiency, and 0.26 against 0.23 with all four.
  * More mass means more inertia. More axial load means less pier ductility. Both reduce the shaking the core can take.
  * The frame adds strength (see §4), but the 1.7 m coupled core still dominates the lateral response. So the frame's extra strength does not convert into a higher collapse intensity.
* **1.7 m coupling.** Coupling this deep pulls the front pier toward net tension under sway; in the pushovers its compression drops from 41 to 9 MN at storey 14. Under reversing load the same action crushes the pier at the bottom. This is the same in both models.

---

## 4. Lateral strength (pushover)

| | As-built | Beam-slab | Ratio |
|---|---|---|---|
| Peak base shear, X | 24.6 MN (4.95 % W) | 50.2 MN (8.66 % W) | **≈ 2.0×** |
| Peak base shear, Y | 22.5 MN (4.53 % W) | 33.0 MN (5.70 % W) | **≈ 1.5×** |

* The beam-slab is still clearly **stronger** statically. It is 1.5–2× in absolute force and 1.3–1.75× relative to its larger weight.
* The Y pushovers end at only 0.36–0.45 % roof drift. This is the front-pier net-tension event under 1.7 m coupling; finer steps reach the same point (`results/diagnostics/README.md`). So the curves show strength up to that event, not the full post-peak branch.
* The time histories go well beyond this (2–3 % drift before collapse). So the pushover is not the governing collapse measure here.

---

## 5. Loss of core piers (alternate load paths)

**Sudden removal under gravity**

| Scenario | As-built, no def. | As-built, all 4 | Beam-slab, no def. | Beam-slab, all 4 |
|---|---|---|---|---|
| S1 front pier F, storey 1 | stands (20 mm) | stands (24 mm) | stands (14 mm) | stands (16 mm) |
| S2 F, storeys 1–4 | stands (21 mm) | stands (23 mm) | stands (15 mm) | stands (17 mm) |
| S6 middle pier M, storey 1 | stands (4 mm) | stands (6 mm) | stands (5 mm) | stands (6 mm) |
| S7 rear pier R, storey 1 | stands (13 mm) | stands (15 mm) | stands (10 mm) | stands (12 mm) |
| **S3 F + M, storeys 1–4** | **fails** (unstable at 274 mm) | **collapse** | **stands (45 mm)** | **stands (40 mm)** |
| S5 whole core, storey 1 | collapse | collapse | collapse | stands (158 mm)* |
| S4 whole core, storeys 1–4 | collapse | collapse | collapse | stands (158 mm)* |

* **Single-pier loss:** both framings now stand in 8 of 8. In v2.0 the as-built stood in only 1 of 8.
  * The 1.7 m link beams hang the lost pier from its neighbours: 34–79 MN goes through the link beams in the pushdowns.
  * The uncracked PT slab also helps.
  * With deep coupling, the core repairs itself for one lost pier, whatever the floor framing.
* **Two-pier loss (the reported SAO scenario: lower core, front and middle):** the as-built fails; the beam-slab stands with 40–45 mm sag.
  * The beam-slab storey-1 columns pick up **72–75 %** of the lost 108–127 MN.
  * The flat slab passes only **16–45 %**.
* \*Whole-core loss is borderline, as in v2.0. The beam-slab stands only with the lighter D3 walls.

**Pushdown (gradual withdrawal of a pier's support)**

* Front pier storey 1, with all four deficiencies: the floor framing carries **28.8 MN** in the beam-slab against **20.3 MN** in the flat slab. The columns take 32.8 MN against 22.1 MN.
* Front pier over storeys 1–4: the beam-slab carries the full load statically (λmax 1.23–1.26). The as-built cannot (λmax 0.88–0.98).
  * Sudden-loss capacity λps: beam-slab 1.04 (no deficiency) and 0.98 (all four); as-built 0.55 and 0.48.
  * So for a sudden multi-storey front-pier loss, the beam-slab is at the threshold and the as-built is well below it.

---

## 6. Answers to the questions (version 3.1)

* **2A-Q1 – Does the model reproduce the collapse?**
  * **Mechanism: partly.** The beam-slab model fails exactly as reported: storey-1 front core pier crushing, then core drop. The as-built model, with the same core, fails first by punching of the flat slab at about 2–3 % drift, before the core crushes.
  * **Intensity: no.** Nothing collapses at the 2025 level, even with f′c × 0.35 and le/ld = 0.10. With the documented deficiencies, collapse needs about **2–3.75×** the reconstructed shaking, compared with 3–4.5× in v2.0.
* **2A-Q2 – Single deficiencies vs interaction.** Single deficiencies cost 0–22 % of the collapse intensity each, with D4 the largest. All four together cost about 35–45 %. Interaction effects are small. The collapse needs the combination plus something not modelled.
* **2A-Q3 – Local core failure and the column–slab system.**
  * With 1.7 m coupling, the flat slab survives any single-pier loss.
  * It does not survive the loss of the front and middle piers over storeys 1–4, which is the reported SAO scenario. It passes only 16–45 % of that load to the columns.
* **2B-Q4 – Does failure propagate differently?** Yes, in both kinds of analysis.
  * Under shaking, the beam-slab has no punching cascade. It collapses only when the core itself crushes, and later in the record.
  * After pier loss, it stands where the flat slab collapses (two-pier loss) and sags much less.
* **2B-Q5 – How much load is redistributed?**
  * After the two-pier loss, the beam-slab columns take 82–92 MN, 72–75 % of the lost load.
  * In the flat slab it is 15–50 MN, and the building then becomes unstable.
  * The link-beam route through the core carries 34–79 MN for single-pier loss in both framings.

---

## 7. Overall conclusion

1. **At the 2025 intensity neither framing collapses.** Drifts are 0.3–0.35 % and nothing fails. The recalibration lowered the collapse intensity (about 2–5× instead of 3–8×), but not to 1×.
2. **Under earthquake shaking alone, the two framings are equivalent.** The collapse SF averages 3.18 (as-built) and 3.06 (beam-slab). The heavier beam-slab, with its beams loading the core, sends its collapse through the same lower core pier that failed at SAO. Its frame strength (1.5–2× in the pushover) does not raise the shaking it survives.
3. **The beam-slab's advantage is robustness after core damage.** It survives losing the front and middle core piers over four storeys, which is the reported SAO failure, with 40–45 mm sag. The flat slab does not. In v2.0, with shallow link beams, this advantage also covered every single-pier loss. With 1.7 m coupling the core itself handles a single-pier loss.
4. **For the hypothesis:**
   * "Beam-slab is more robust against progressive collapse once the core is damaged": **supported.**
   * "Beam-slab survives stronger shaking": **not supported in v3.1.** It was supported in v2.0 without deficiencies.

---

## Limitations

* The ground motions are synthetic, spectrally matched to a reconstructed spectrum; there is no Bangkok recording at the SAO site. The 13 single, pair and triple combinations use GM1 only.
* Collapse brackets are ±20 % (bisection tolerance). Differences of one bracket step are within resolution.
* A run that stops for numerical reasons twice (dt 0.025 and 0.01 s) counts as collapse. This affects 4 as-built cases with no recorded failure, so the as-built collapse SF may be slightly underestimated there.
* Link-beam reinforcement (3,300 mm²) was kept from the 500 mm design, not redesigned for 1.7 m. The beams are shear-controlled either way, so their strength would not change. Conventional bars are modelled, with no diagonal reinforcement.
* Y pushovers end at front-pier net tension (≈ 0.4 % roof drift).
* There is no joint-panel flexibility in either model. The beam-to-core connections are full moment connections, as specified.

## Files

* Tables:
  * `results/summary/T7_collapse_intensity_all_variants.csv` (collapse brackets)
  * `T4` (IDA, GM1)
  * `T1` (2025-level matrix)
  * `T3` (sudden removal)
  * `T6` (pushdown)
  * `T2` (pushover)
  * `T8` (deficiency factors)
* Figures:
  * `figures/fig11_collapse_intensity_all_combinations.png`
  * `fig06_incremental_dynamic_analysis.png`
  * `fig03_deficiency_matrix_event_level.png`
  * `fig07`–`fig09` (core removal and redistribution)
  * `fig02` (pushover)
