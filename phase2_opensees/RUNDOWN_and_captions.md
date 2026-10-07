# Phase 2 – Run-down of every model and calculation, with captions

All paths are relative to `phase2_opensees/`. The code is Python with OpenSeesPy 3.7.1.

---

## A. The models

| File | What it is | Caption |
|---|---|---|
| `phase2A_asbuilt_flatslab_model.py` | **Phase 2A model** – the as-built 33-storey, 137 m building with a 300 mm post-tensioned flat slab and no beams. The slab is modelled as effective-width strips (Hwang & Moehle, β = 0.5) with end hinges. Each slab–column and slab–wall joint has a removable punching element (ACI 318-19 §18.14.5.1 drift rule for PT slabs) plus a post-punching residual spring (40 % Vc at columns, 30 % at walls). | *3-D nonlinear OpenSees model of the as-built post-tensioned flat-slab configuration with an eccentric core (Phase 2A).* |
| `phase2B_proposed_beamslab_model.py` | **Phase 2B model** – the same building, geometry, core, columns and loads, but with 500 × 800 mm beams on every column line and a 250 mm slab acting as the T-beam flange. Beams have plastic hinges (HingeRadau) at both ends; at wall ends the moment is capped at 25 %. The beam–column joints are monolithic, so there is no punching mode. | *3-D nonlinear OpenSees model of the proposed column-beam-slab frame configuration with the same core (Phase 2B).* |
| `sao/building_common.py` | Parts shared by both models: nodes, the 26 columns per floor (1400 mm square stepping to 800 mm circular, fibre hinges), the core, the link beams, rigid diaphragms, gravity load and mass. | *Common structural components of both models; only the floor framing differs.* |
| — core (inside `building_common.py`) | 17 × 17 m eccentric core split into three wall piers – R (rear C), M (middle I), F (front C). Each pier-storey is a force-based fibre element with nonlinear shear springs in X and Y (elastic to 0.6 Vn, Vn on 0.1 GA, a plateau to 0.5 % drift, then 20 % residual). Four 250 × 500 link beams per floor connect the piers. | *Wide-column fibre model of the three-pier core with nonlinear shear springs and coupling (link) beams.* |
| `sao/config.py` | Geometry, loads (event stage: SDL 0.75, LL 0.5, façade 0.75 kPa) and the 16 deficiency variants per framing. | *Model parameters and deficiency variants.* |
| `sao/capacities.py` | Strength calculations: wall shear Vn and backbone, link-beam strength (with anchorage limit for D2), punching Vc and drift capacity, slab-strip and beam moment capacities, ASCE 41-13 Table 10-19 wall rotation limits. | *Member capacity and failure-criterion calculations.* |
| `sao/design.py` + `run_00_design_basis.py` → `results/design.json` | Design of walls and beams to the DPT 1301/1302-61 spectrum (R = 5, I = 1.25). Compliant walls get the dynamic shear amplification and confined boundary zones; D4 walls do not. | *Design basis used to size wall and beam reinforcement in both models.* |

### The deficiency variants (16 per framing, 32 in total)

| Code | Deficiency | How it is modelled |
|---|---|---|
| D1 | Wall concrete below 500 ksc | Wall f′c × 0.70 |
| D2 | Short link-beam bar embedment | Bar stress ≤ 0.5 fy, brittle pull-out after the peak |
| D3 | Walls reduced from 300 to 250 mm | t = 250 mm, same steel per metre |
| D4 | Non-compliant (under-designed) drawings | No dynamic shear amplification, no confined boundary zones |

The variants are REF (none), the four singles, 6 pairs, 4 triples and all four. They are named `A-…` for the as-built and `B-…` for the beam-slab, e.g. `A-D1D2D3D4`. Intensified versions add `_fc0.50_le0.30` (f′c × 0.50, le/ld = 0.30).

---

## B. The calculations / analyses run

| # | Analysis | Runs | What it answers | Caption |
|---|---|---|---|---|
| 1 | **Gravity + modal analysis** | every run | Self-weight state; periods (A: 5.85 / 4.98 / 2.49 s, B: 4.24 / 4.23 / 2.10 s, no deficiencies) | *Gravity equilibrium and natural periods of both models.* |
| 2 | **Damping verification** (`verify_damping.py`) | 2 | Measured damping 2.6 % (A) and 2.4 % (B) against the 2.5 % target | *Free-vibration check of the Rayleigh damping.* |
| 3 | **Ground-motion generation** (`run_01_ground_motions.py`) | 3 records | GM1–GM3: bidirectional synthetic records spectrally matched to the reconstructed 28 March 2025 Bangkok spectrum (PGA ≈ 0.024 g, D5-95 ≈ 57 s) | *Synthetic ground motions representing the 2025 shaking in Bangkok.* |
| 4 | **Event-level response histories** (SF = 1) | 32 | Do any deficiency combinations collapse under the real 2025 shaking? (None do.) | *Nonlinear response to the 2025-level shaking for every deficiency combination.* |
| 5 | **Severity ladder** (SF = 1) | 8 | All four deficiencies with D1/D2 made progressively worse (f′c 0.60 → 0.35, le/ld 0.40 → 0.10). All survive. | *Sensitivity of the 2025-level response to the unknown severity of D1 and D2.* |
| 6 | **Collapse-intensity searches** (incremental dynamic analysis, `sao/ida.py`) | 42 searches, 258 response histories in total | The scale factor on the 2025 shaking at which each variant collapses (ladder 1 → 2 → 3 → 4.5 → 6 → 8, then bisection to 20 %) | *Collapse intensity of every deficiency combination in both framings.* |
| 7 | **Record-to-record check** | 8 of the 42 searches | GM2 and GM3 for no deficiencies and all four, both framings | *Record-to-record variability of the collapse intensity.* |
| 8 | **Factorial (effects) analysis** | from 6 | How much each deficiency and each interaction changes ln(collapse SF) and ln(drift) | *Main and interaction effects of the four deficiencies.* |
| 9 | **Pushover** (X and Y, all 32 variants) | 64 | Lateral strength, core vs column share, first failure | *Static lateral capacity of both framings.* |
| 10 | **Pushdown** (quasi-static support withdrawal) | 16 | Share of a lost core pier's load the rest of the building can carry (λmax, λps), and through which route | *Alternate-load-path capacity after the loss of one core pier.* |
| 11 | **Sudden removal** (dynamic, under gravity) | 28 | Does the building arrest a sudden loss of core piers? | *Dynamic response to sudden loss of lower-core piers.* |

**Failure criteria monitored in every run:**

* punching (flat slab);
* wall shear strength loss / shear failure;
* wall axial failure (shear drift, crushing at −0.6 % average strain, or ASCE 41 limit b) → the pier is removed;
* link-beam yielding / failure;
* column crushing.

**Global collapse** is any of:

* storey drift > 10 %;
* vertical drop > 0.6 m;
* loss of equilibrium (non-convergence).

---

## C. Figures (`figures/`)

| File | Caption |
|---|---|
| `fig01_ground_motions.png` | **Figure 1.** Synthetic ground motions GM1–GM3. Left: 5 %-damped response spectra of the three records against the reconstructed 2025 Bangkok target spectrum and the DPT 1301/1302-61 design spectrum. Right: acceleration history of GM1 (X component). |
| `fig02_pushover_curves.png` | **Figure 2.** Pushover curves (base shear / building weight vs roof drift) in X and Y for the as-built flat slab (blue) and the proposed beam-slab (orange), with no deficiencies (dashed) and all four deficiencies (solid). × marks the axial failure of a core wall pier. |
| `fig03_deficiency_matrix_event_level.png` | **Figure 3.** Peak corner storey drift (log scale) of all 16 deficiency combinations in both framings under the 2025-level shaking (SF = 1, GM1). Every combination stands in both framings. |
| `fig04_failure_sequence_event_level.png` | **Figure 4.** Damage timeline at the 2025-event level (SF = 1, GM1), all four deficiencies: each damage event plotted by time and storey (link-beam yielding and failure, wall and slab events), as-built vs beam-slab. |
| `fig05_core_demand_profiles.png` | **Figure 5.** Height-wise profiles at SF = 1 (GM1) for both framings, with and without deficiencies. Left: peak wall shear demand / capacity per storey. Right: peak corner storey drift. |
| `fig06_incremental_dynamic_analysis.png` | **Figure 6.** Incremental dynamic analysis: peak storey drift vs scale factor on the 2025 shaking for the reference, single-deficiency and all-four variants of each framing (GM1). Curves end at collapse. |
| `fig07_core_removal_vertical_response.png` | **Figure 7.** Vertical displacement of the core after sudden removal of lower-core piers under gravity (scenarios S1–S7), as-built vs beam-slab with all four deficiencies. |
| `fig08_pushdown_capacity.png` | **Figure 8.** Pushdown curves for the loss of each storey-1 core pier: fraction of the lost pier's load carried by the rest of the building (λ) vs drop of the core above it, both framings, with no deficiencies (left) and all four (right). |
| `fig09_load_redistribution_paths.png` | **Figure 9.** Where a lost core pier's load goes at peak pushdown capacity: through the link beams to the other core piers vs through the floor framing to the columns, for both framings. |
| `fig10_torsion.png` | **Figure 10.** Torsional response at SF = 1 with all four deficiencies. Left: roof twist history. Right: ratio of corner drift to centre drift by storey. |
| `fig11_collapse_intensity_all_combinations.png` | **Figure 11.** Collapse intensity of all 16 deficiency combinations in both framings (record GM1). The bar spans the bracket from the highest scale factor survived to the lowest at which the building collapsed; the dot is the geometric-mean estimate. |

---

## D. Tables (`results/summary/`)

| File | Caption |
|---|---|
| `T1_deficiency_matrix_event_level_GM1.csv` | **Table 1.** Response of all 32 variants to the 2025-level shaking (SF = 1, GM1): outcome, peak drift, roof twist, counts of failed link beams, walls, slab connections and columns, and the worst wall shear demand/capacity. |
| `T2_pushover_capacity.csv` | **Table 2.** Pushover capacity of all 32 variants in X and Y: peak base shear (MN and % of weight), roof drift at peak, core share, and roof drift at the first link-beam, wall and punching failures. |
| `T3_core_removal_redistribution.csv` | **Table 3.** Sudden removal of lower-core piers: outcome, removed load, load picked up by the columns and the core, final settlement and failures. |
| `T4_ida_collapse_intensity.csv` | **Table 4.** Incremental dynamic analysis: peak drift at each scale factor, collapse SF and highest SF survived (key variants, GM1). |
| `T5_factorial_effects_{A,B}_log_drift.csv` | **Table 5.** Factorial effects of the deficiencies on ln(peak drift) at SF = 1. The `_collapse` versions are all zero, because nothing collapses at SF = 1. |
| `T6_pushdown_redistribution.csv` | **Table 6.** Pushdown results: λmax, pseudo-static capacity λps, and the load carried through the link beams vs the floor framing. |
| `T7_collapse_intensity_all_variants.csv` | **Table 7.** Collapse intensity of all 42 collapse searches: highest SF survived, lowest SF collapsed, geometric-mean estimate, and every run. |
| `T8_factorial_effects_logSFcollapse_{A,B}.csv` | **Table 8.** Factorial effects of each deficiency and interaction on ln(collapse SF), and the equivalent factor on the collapse SF. |

---

## E. Run scripts

| File | What it does |
|---|---|
| `run_00_design_basis.py` | Designs walls and beams → `results/design.json` |
| `run_01_ground_motions.py` | Generates GM1–GM3 → `motions/` and Figure 1 |
| `run_02_all_phase2.py` | Runs every analysis for both models (resumable) |
| `run_phase2A_asbuilt_flatslab.py` | Runs the as-built analyses only |
| `run_phase2B_proposed_beamslab.py` | Runs the beam-slab analyses only |
| `run_03_postprocess.py` | Builds Tables 1–8 and Figures 2–11 |
| `verify_damping.py` | Damping check (calculation 2) |
| `verify_beamslab_collapse.py` | Diagnostic runs used to check why the beam-slab collapses first |

## F. Reports

| File | Contents |
|---|---|
| `REPORT_phase2_findings.md` | Final results and answers to each Phase 2A / 2B question and hypothesis |
| `REPORT_alp.md` | Load redistribution / alternate load paths |
| `REPORT_methods.md` | Modelling assumptions, deficiencies, loading, and the corrections and verification |
| `README.md` | Folder guide |
