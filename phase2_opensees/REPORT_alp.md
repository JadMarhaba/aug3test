### Load redistribution after local core failure (alternate load paths)

These analyses ask what happens to the gravity load when part of the lower core fails. Two methods were used:

* **Pushdown (quasi-static).** One pier-storey is replaced by the forces it carried, and that support is withdrawn gradually. λmax is the share of the lost pier's load the rest of the building can carry. λps is the energy-based ("pseudo-static") capacity: λps ≥ 1 means the building should survive a *sudden* loss of that pier.
* **Sudden removal (dynamic).** The pier-storeys are deleted instantly under gravity, then the analysis follows the dynamic response for 6 s.

**Pushdown capacity (λmax / λps):**

| Pier lost (storey 1) | Gravity load lost | Flat slab, no def. | Beam-slab, no def. | Flat slab, all 4 def. | Beam-slab, all 4 def. |
|---|---|---|---|---|---|
| Front pier F | 53–60 MN | 0.91 / 0.77 | **1.13** / 0.89 | 0.66 / 0.46 | 0.90 / 0.63 |
| Middle pier M | 53–60 MN | 1.20 / 0.85 | 1.21 / **1.16** | 0.99 / 0.71 | **1.14** / 0.96 |
| Rear pier R | 35–42 MN | 1.11 / 0.79 | **1.33 / 1.08** | 0.79 / 0.57 | **1.15** / 0.88 |
| Front pier F, storeys 1–4 | 53–60 MN | 0.93 / 0.65 | ≥0.79 | 0.69 / 0.46 | ≥0.85 |

**Sudden removal under gravity:**

| Pier(s) removed | Flat slab, no def. | Beam-slab, no def. | Flat slab, all 4 | Beam-slab, all 4 |
|---|---|---|---|---|
| Middle pier M, storey 1 | stable (20 mm) | stable (17 mm) | **collapse** (0.58 s) | stable (27 mm) |
| Rear pier R, storey 1 | **collapse** (0.78 s) | stable (26 mm) | **collapse** (0.47 s) | stable (40 mm) |
| Front pier F, storey 1 | collapse (0.63 s) | collapse (0.89 s) | collapse (0.52 s) | collapse (0.62 s) |
| Front pier F, storeys 1–4 | collapse (0.63 s) | collapse (0.88 s) | collapse (0.52 s) | collapse (0.63 s) |
| Front + middle piers, storeys 1–4 | collapse (0.47 s) | collapse (0.53 s) | collapse (0.38 s) | collapse (0.51 s) |
| Whole core, storey 1 or storeys 1–4 | collapse (0.40 s) | collapse (0.45 s) | collapse (0.41 s) | collapse (0.47 s) |

"Collapse" here means the core above the gap drops 0.6 m; the time is how long that took. Free fall would cover 0.6 m in 0.35 s.

**Where the redistributed load goes** (pushdown, at peak):

* The load leaves the failed pier by two routes:
  * **through the link beams to the other two core piers.** This route is the same in both framings because it belongs to the core. It is worth about 31 MN for the front pier and up to 64 MN for the middle pier, which sits between two link beams per side.
  * **through the floor framing to the columns.** This is where the framings differ.
* For the front pier F without deficiencies, the floor route carries 22.8 MN through the flat slab and 36.9 MN through the beams, **1.6×** as much. For the rear pier it is 5.4 MN against 19.4 MN (**3.6×**).
* With all four deficiencies, D2's weak link beams roughly halve the core route, from 31.6 to 17.7 MN for pier F. The floor route then matters more: 17.3 MN through the flat slab against 29.9 MN through the beams (**1.7×**).
* After a sudden rear-pier loss the beam-slab model *with all four deficiencies* settles at 40 mm. The storey-1 columns pick up 25 MN, 69 % of the 36 MN lost; the rest is shared between the remaining piers through the link beams. Without deficiencies, the flat slab arrests only the middle pier, settling at 20 mm with 17 % of the load to the columns.
