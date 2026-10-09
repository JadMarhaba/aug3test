# Phase 2 (version 3.1) – v3.0 with deeper coupling over the core openings

v3.1 is version 3.0 (`../phase2_opensees_3.0`) with one change: **the link (coupling) beams over the four core openings are 1.70 m deep instead of 0.50 m.** The depth is the storey height (4.09 m) minus a lift-door opening of about 2.4 m. Everything else is as in v3.0, and identical in both models apart from the beams:

* 250 mm slab, PT flat slab (as-built) and non-PT RC beam-slab;
* corner cantilevers; all beams moment-connected;
* link beams 0.5 EI; PT slab uncracked;
* revised 2025 records; collapse search from SF 0.5.

With 500 mm link beams the three core piers act almost independently, which gave the long v3.0 periods. With 1.7 m coupling the core acts close to one box. The periods then fall in the researched Bangkok range for a building of this height (about 2.7–3.3 s; Thai code 0.02H = 2.74 s). Making the coupling deeper still barely changes them (2.5 m: 3.18 s; 3.2 m: 3.17 s). About 2 s would need thicker core walls.

| Model (nonlinear, event loads) | T1 | T2 | T3 | (v3.0, 0.5 m link beams) |
|---|---|---|---|---|
| As-built, no deficiency | **3.24 s** | 3.05 s | 1.88 s | 4.74 s |
| As-built, all four deficiencies | **3.65 s** | 3.56 s | 2.13 s | 5.27 s |
| Beam-slab, no deficiency | **3.04 s** | 2.91 s | 1.80 s | 3.99 s |
| Beam-slab, all four deficiencies | **3.33 s** | 3.26 s | 1.98 s | 4.24 s |

The link beam reinforcement is unchanged (3300 mm<sup>2</sup> top and bottom, from the design basis). A 1.7 m deep link beam then has a flexural capacity My ≈ 1630 kNm and a shear capacity Vn ≈ 2180 kN, using reference wall concrete. D2 (short embedment) limits the bar stress exactly as before.

---

# Phase 2 (version 3.0) – calibrated stiffness and revised 2025 Bangkok ground motions

Version 3.0 starts from `../phase2_opensees_2.0`. The geometry and framing are unchanged:

* 250 mm slab in both models, corner cantilevers, all beams moment-connected.
* Identical geometry apart from the beams.
* The as-built flat slab is post-tensioned; the beam-slab is ordinary reinforced concrete, not post-tensioned.
* 500 mm link beams, as in the proposal.

It changes only the items below, which are based on the research report `../reports/SAO site PGA and building period.md`.

| Item | v2.0 | **v3.0** | Why |
|---|---|---|---|
| Link (coupling) beam stiffness | 0.20 EI | **0.50 EI** (both models) | The 2025 shaking was low intensity; the link beams were not yet heavily cracked |
| Flat-slab strip stiffness (as-built, PT) | beta = 0.5 | **beta = 1.0** | Post-tensioning precompression keeps the PT slab uncracked |
| Beam stiffness (beam-slab, RC, not PT) | 0.35 EI | 0.35 EI (unchanged) | Ordinary RC beams are already cracked by gravity |
| Target spectrum (2025 event, SF = 1) | peak 0.08 g at 1.3 s; 0.022 g at 6 s | **peaks near 1.6 s (0.085 g), 2.8 s (0.070 g) and 6.3 s (0.052 g)** | Recorded peaks at 1.6 / 2.8 / 6.3 s; JMA long-period class 3 at ~6 s |
| Record length / strong shaking | 100 s / D5-95 ≈ 57 s | **120 s / D5-95 ≈ 80–90 s** | TMD: "more than a minute"; Warnitchai: up to ~2 min |
| Collapse-search ladder | starts at SF 1 | **starts at SF 0.5** (0.5, 1, 1.5, 2, 3, 4.5, 6, 8) | To show collapse below the 2025 level, if it happens |

**Resulting records (GM1–GM3).**

* PGA 0.027–0.032 g. That is about 20–35 % above the recorded 0.024 g at station PWSA, because the long, strong 1–3 s content sets the peak.
* PGV 13–17 cm/s (PWSA recorded 13.9 cm/s).
* D5-95 = 80–90 s.

**Resulting periods (nonlinear models, event loads).**

| Model | T1 | T2 | T3 |
|---|---|---|---|
| As-built, no deficiency | 4.74 s | 3.86 s | 2.30 s |
| As-built, all four deficiencies | 5.27 s | 4.43 s | 2.57 s |
| Beam-slab, no deficiency | 3.99 s | 3.62 s | 2.04 s |
| Beam-slab, all four deficiencies | 4.24 s | 3.99 s | 2.20 s |

With the 500 mm link beams from the proposal, the as-built cannot reach the ~2.7–3.3 s typical of Bangkok towers of this height: even fully uncracked link beams and slab give 4.3 s. A quick test with ~1.7 m deep coupling over the lift doors gave 3.6 s. This core is therefore more flexible than typical Bangkok buildings. It sits in the amplified 5–7 s band, where the 2025 shaking was strongest at long periods.

---

# Phase 2 (version 2.0) – revised floor framing, 250 mm slab in both models

Version 2.0 differs from `../phase2_opensees` (version 1) in three ways, agreed against the floor plan in `figures/fig00_floor_plans.png`:

1. **250 mm slab in both models.** The as-built PT flat slab is thinned from 300 mm to 250 mm (`sao/config.py`: `SLAB_T_FLAT = 0.25`). The beam-slab slab was already 250 mm.
2. **Corner cantilevers.** There are no columns at the four plan corners. In both models the floor cantilevers 5.5 m from the nearest edge column to each corner, along both edges: 8 cantilevers per floor. They are slab strips in the as-built and 500 × 800 beams in the beam-slab (`sao/building_common.py`, `_build_segments`, `CORNERS`).
3. **All beams fully moment-connected.** In the beam-slab, the 8 beams per floor that frame into the core walls now keep their full hinge capacity at the wall end. In version 1 that end was capped at 25 %.

The slab covers the whole 39 × 39 m plate to the corners, except inside the core. The link (coupling) beams join only the core piers to one another: 4 per floor, across 1.5 m openings (assumed).

Unchanged from version 1: the design basis (`results/design.json`, copied as is, with no re-design or code check), the ground motions, the deficiencies D1–D4, and all analysis settings.

| Model (version 2.0) | Weight | T1 / T2 / T3 (s) | Corner tip sag under gravity | Cantilever moment / capacity |
|---|---|---|---|---|
| As-built 250 mm, no deficiency | 496 MN | 6.11 / 4.98 / 2.51 | 25–40 mm | 0.50–0.52 |
| As-built 250 mm, all four | 484 MN | 6.87 / 5.76 / 2.86 | 25–40 mm | 0.50–0.52 |
| Beam-slab, no deficiency | 580 MN | 4.19 / 4.17 / 2.06 | 8–24 mm | 0.11–0.16 |
| Beam-slab, all four | 568 MN | 4.51 / 4.39 / 2.22 | 8–24 mm | 0.12–0.16 |

**Results: `REPORT_phase2_findings_v2.md`** (with a comparison to version 1). Floor plan: `figures/fig00_floor_plans.png`; core piers and pier-loss scenarios: `figures/fig00b_core_piers_and_removal_scenarios.png`.

All analyses of version 1 are re-run here for both models. Results from an earlier 2.0 attempt with the version-1 floor layout are kept in `results/old/v2_before_corner_cantilevers/`.

---

# Phase 2 – OpenSees nonlinear models of the State Audit Office building

This folder holds the Phase 2 work from the dissertation proposal: nonlinear modelling in OpenSees (Python / OpenSeesPy).

* **Phase 2A** – the as-built post-tensioned flat slab with its eccentric core.
* **Phase 2B** – the proposed column-beam-slab frame with the same core.

Both models are run with the documented deficiencies, first one at a time and then in every combination (proposal Part 4). Phase 1 (ETABS elastic) and Phase 3 (recommendations and cost) are not part of this folder.

**Results:** start with `REPORT_phase2_findings.md`. It answers each Phase 2A / 2B question and hypothesis from the proposal. Load redistribution is detailed in `REPORT_alp.md`, and the modelling and the corrections applied in `REPORT_methods.md`.

## Which file is which

| File | Model | What it does |
|---|---|---|
| `phase2A_asbuilt_flatslab_model.py` | **AS-BUILT (2A)** | Flat-slab model: 300 mm PT slab strips and slab–column / slab–wall punching connections. Defines the 16 as-built variants `A-…`. Run it to list the variants and build one. |
| `phase2B_proposed_beamslab_model.py` | **PROPOSED (2B)** | Beam-slab model: 500×800 beams on every column line and a 250 mm slab. Defines the 16 proposed variants `B-…`. |
| `run_phase2A_asbuilt_flatslab.py` | **AS-BUILT (2A)** | Runs every 2A analysis: pushovers, response histories, IDA and core-removal cases. |
| `run_phase2B_proposed_beamslab.py` | **PROPOSED (2B)** | Runs the same analyses on the 2B model under identical loading. |
| `run_00_design_basis.py` | shared | Sizes the reinforcement the proposal does not give, writing `results/design.json`. |
| `run_01_ground_motions.py` | shared | Builds the 3 bidirectional records matched to the 2025-event spectrum in Bangkok. |
| `run_02_all_phase2.py` | shared | Runs the 2A and 2B job lists together on all CPU cores. |
| `run_03_postprocess.py` | shared | Produces the tables and figures in `figures/` and the numbers quoted in `REPORT_phase2_findings.md`, `REPORT_alp.md` and `REPORT_methods.md`. |
| `sao/config.py` | shared | All geometry, material and load values (proposal Sec. 3.2), the deficiency definitions D1–D4, and the `Variant` naming. |
| `sao/building_common.py` | shared | Everything identical in both models: columns, the 3-pier core, link beams, diaphragms, loads and mass. |
| `sao/capacities.py` | shared | Strength formulas: wall shear, link beams, punching, slab strips, beams. |
| `sao/analysis.py` | shared | Gravity, modal, pushover, response-history and sudden-removal analyses, plus the failure monitors. |
| `sao/motions.py`, `sao/spectra.py` | shared | Ground-motion synthesis and the target / DPT spectra. |
| `sao/design.py` | shared | The design pass used by `run_00`. |
| `sao/runner.py`, `sao/jobqueue.py` | shared | Run one analysis per process and save it to `results/…json`; run many in parallel. |
| `sao/registry.py` | shared | Picks the 2A or 2B model file for a variant. |

## What the variant codes mean

Each variant name is the framing letter followed by the deficiencies that are switched on.

| Code | Meaning |
|---|---|
| `A-` | Phase 2A as-built flat-slab framing |
| `B-` | Phase 2B proposed beam-slab framing (same core, same loads) |
| `REF` | No deficiencies: 300 mm walls, specified concrete, full bar embedment, compliant design |
| `D1` | Core-wall concrete below the specified 500 ksc (f′c × 0.70, i.e. about 350 ksc) |
| `D2` | Link (coupling) beam bars embedded less than required (le/ld = 0.5), giving anchorage pull-out |
| `D3` | Core walls 250 mm instead of 300 mm (steel per metre kept, as the designer did) |
| `D4` | Design not compliant with the regulation: wall shear steel without the required amplification, and no confined boundary zones |

Examples:

* `A-D1D2D3D4` is the **as-built condition**: all four deficiencies in the flat-slab building.
* `B-D1D2D3D4` puts the same four deficiencies into the beam-slab building.
* `A-D2` is the flat slab with only the short link-beam embedment.

Each framing has 16 variants: the reference, the 4 deficiencies individually, 6 pairs, 4 triples, and all four.

## Modelling assumptions

From the proposal's Sec. 3.2 tables:

* 33 storeys and 137 m total: a 6 m ground storey, then about 4.09 m per storey.
* 39 × 39 m grid with 26 columns per floor.
* 17 × 17 m core centred on the rear edge, with 250 mm walls (300 mm when D3 is off).
* 250 × 500 mm link beams.
* 300 mm PT flat slab in 2A; 250 mm slab and 500 × 800 beams in 2B.
* Columns 1400 × 1400 mm, stepping down to 800 mm circular for storeys 29–33.
* Concrete 5000–8000 psi; wall concrete specified at 500 ksc.

Added assumptions (the proposal does not give these values):

* **Interior column grid and core layout.** Three wall piers are created by 4 door openings 1.5 m wide.
* **Reinforcement.** Sized by the design pass from the reconstructed DPT 1301/1302-61 Bangkok spectrum, with R = 5 and I = 1.25.
* **Event-time loads.** The building was under construction, so the loads are superimposed dead load 0.75 kPa, live load 0.5 kPa and façade 0.75 kPa.
* **Damping.** 2.5 % Rayleigh.
* **Base.** Fixed (no soil–structure interaction).
* **Ground motions.** These are synthetic. Each bidirectional record is matched to a spectrum reconstructed from the reported Bangkok values: PGA about 0.02 g, PGV about 10 cm/s, and amplification at 1–3 s and 5–7 s. Scale factor SF = 1 is the estimated 2025 event.

## How to run

```bash
pip install openseespy numpy scipy matplotlib
python3 run_00_design_basis.py             # reinforcement -> results/design.json
python3 run_01_ground_motions.py           # records -> motions/GM1..GM3.npz
python3 run_phase2A_asbuilt_flatslab.py 4  # all as-built analyses (4 parallel processes)
python3 run_phase2B_proposed_beamslab.py 4 # all proposed analyses
python3 run_03_postprocess.py              # tables + figures
python3 phase2A_asbuilt_flatslab_model.py  # print the 2A variants and build the as-built model
```

The run scripts skip any job that already has a result, so a long batch can be stopped and resumed.
