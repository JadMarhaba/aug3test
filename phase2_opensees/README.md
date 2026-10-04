# Phase 2 – OpenSees nonlinear models of the State Audit Office building

This folder holds the Phase 2 work from the dissertation proposal: nonlinear modelling in OpenSees (Python / OpenSeesPy).

* **Phase 2A** – the as-built post-tensioned flat slab with its eccentric core.
* **Phase 2B** – the proposed column-beam-slab frame with the same core.

Both models are run with the documented deficiencies, first one at a time and then in every combination (proposal Part 4). Phase 1 (ETABS elastic) and Phase 3 (recommendations and cost) are not part of this folder.

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
| `run_03_postprocess.py` | shared | Produces the tables and figures in `figures/` and the numbers quoted in `REPORT.md`. |
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
