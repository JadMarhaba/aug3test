### Load redistribution after local core failure (alternate load paths)

*Results from the corrected code (damping, hinge sign, wall-rotation and solver-sanity fixes). The pre-fix results are archived in `results/old/prefix_v8/`.*

These analyses ask what happens to the gravity load when part of the lower core fails. Two methods were used:

* **Pushdown (quasi-static).** One pier-storey is replaced by the forces it carried, and that support is withdrawn gradually. λmax is the share of the lost pier's load the rest of the building can carry. λps is the energy-based ("pseudo-static") capacity: λps ≥ 1 means the building should survive a *sudden* loss of that pier.
* **Sudden removal (dynamic).** The pier-storeys are deleted instantly under gravity, then the analysis follows the dynamic response for 6 s.

**Pushdown capacity (λmax / λps):**

| Pier lost (storey 1) | Gravity load lost | Flat slab, no def. | Beam-slab, no def. | Flat slab, all 4 def. | Beam-slab, all 4 def. |
|---|---|---|---|---|---|
| Front pier F | 53–63 MN | 0.96 / 0.80 | **1.11 / 1.01** | 0.69 / 0.47 | **1.05** / 0.91 |
| Middle pier M | 53–62 MN | 1.20 / 0.68 | 1.21 / **1.09** | 1.01 / 0.72 | **1.13** / 0.95 |
| Rear pier R | 35–42 MN | 1.14 / 0.80 | **1.33 / 1.13** | 0.81 / 0.58 | **1.14** / 0.84 |
| Front pier F, storeys 1–4 | 53–63 MN | 0.81 / 0.45 | 0.82 / 0.45 | 0.71 / 0.47 | 0.91 / 0.69 |

In every case the beam-slab carries as much of the lost load as the flat slab or more. With all four deficiencies it carries 12–52 % more.

**Sudden removal under gravity:**

| Pier(s) removed | Flat slab, no def. | Beam-slab, no def. | Flat slab, all 4 | Beam-slab, all 4 |
|---|---|---|---|---|
| Middle pier M, storey 1 | stable (20 mm) | stable (18 mm) | **collapse** (0.60 s) | stable (31 mm) |
| Rear pier R, storey 1 | **collapse** (1.16 s) | stable (25 mm) | **collapse** (0.47 s) | stable (42 mm) |
| Front pier F, storey 1 | **collapse** (0.68 s) | stable (133 mm) | collapse (0.55 s) | collapse (0.82 s) |
| Front pier F, storeys 1–4 | **collapse** (0.68 s) | stable (132 mm) | collapse (0.55 s) | collapse (0.85 s) |
| Front + middle piers, storeys 1–4 | collapse (0.49 s) | collapse (0.60 s) | collapse (0.47 s) | collapse (0.57 s) |
| Whole core, storey 1 or storeys 1–4 | collapse (0.41 s) | collapse (0.48 s) | collapse (0.42 s) | collapse (0.51 s) |

"Collapse" here means the core above the gap drops 0.6 m; the time is how long that took. Free fall would cover 0.6 m in 0.35 s. The figure in brackets for a stable case is the final settlement of the core above the gap.

* **Of the 8 single-pier sudden-loss cases (4 scenarios × 2 deficiency sets), the beam-slab survived 6 and the flat slab 1.**
* Without deficiencies, the beam-slab even stands after losing the front pier, the heaviest one (63 MN). It settles 133 mm and hands 97 % of the lost load to the storey-1 columns through the beams.
* No floor system can bridge the loss of two piers or of the whole core. Both framings collapse in under 0.6 s, which is close to free fall.

**Where the redistributed load goes** (pushdown, at peak):

* The load leaves the failed pier by two routes:
  * **through the link beams to the other two core piers.** This route belongs to the core, so it is the same in both framings. It carries about 29–31 MN for the front pier and up to 64 MN for the middle pier, which sits between two link beams per side.
  * **through the floor framing to the columns.** This is where the framings differ.
* With all four deficiencies, D2's weak link beams roughly halve the core route (front pier: 31 → 17 MN). The floor route then matters more.
  * Flat slab: the floor route peaks at 20 MN and the building fails at a 34 mm drop (λmax 0.69).
  * Beam-slab: the beams keep picking up load, after the link beams have failed, to 60 MN at a 160 mm drop (λmax 1.05).
* Rear pier: the floor route carries 6 MN in the flat slab and 19 MN in the beam-slab (**3×**). Middle pier: 7–9 MN against 14–15 MN.
* After a sudden rear-pier loss, the beam-slab with all four deficiencies settles at 42 mm, and the storey-1 columns pick up 24 MN (66 % of the 36 MN lost). After a sudden middle-pier loss, the flat slab without deficiencies settles at 20 mm, with only 18 % of the load going to the columns.
* No slab–column connection punched in any pushdown. The flat slab's weakness is the limited stiffness and strength of the slab strips spanning to the columns, not punching.
