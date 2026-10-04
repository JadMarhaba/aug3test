## 2. What was modelled

### 2.1 The two models

Both models are full 3-D OpenSees (OpenSeesPy 3.7.1) models of the 33-storey, 137 m building. They share every component except the floor framing, so framing is the only variable between them (proposal Part 4).

| | Phase 2A – as-built (`phase2A_asbuilt_flatslab_model.py`) | Phase 2B – proposed (`phase2B_proposed_beamslab_model.py`) |
|---|---|---|
| Floor framing | 300 mm PT flat slab with no beams. Modelled as effective-width slab strips with end hinges (Hwang & Moehle). | 500 × 800 mm beams on every column line, plus a 250 mm slab (as T-beam flange). |
| Slab–column joint | Separate slab node joined to the column by a removable **punching** element plus a post-punching spring. | Monolithic beam–column joint (no punching mechanism). |
| Core | Identical in both: 17 × 17 m, eccentric (rear edge), 3 wall piers R / M / F linked by 4 link beams per floor (250 × 500). | Identical. |
| Columns | Identical in both: 26 per floor, 1400 mm square stepping to 800 mm circular. Fibre hinges at both ends. | Identical. |
| Weight (event-stage loads) | 549 MN (reference), 536 MN (all four deficiencies). | 570 MN, 558 MN. |
| Periods T1/T2/T3 (s) | 5.85 / 4.98 / 2.49 (reference); 6.44 / 5.67 / 2.81 (all four). | 4.30 / 4.30 / 2.20; 4.65 / 4.47 / 2.31. |

**How the core is modelled.** Each core pier is a force-based fibre element per storey. Its section is the real C / I shape in fibres, with a nonlinear shear spring in each direction:

* elastic to 0.6 Vn;
* reaches Vn on the cracked stiffness 0.1 GA;
* holds Vn to 0.5 % shear drift;
* then drops to 20 % residual (ASCE 41-17, shear-controlled walls).

When a pier-storey reaches its axial-failure shear drift, or its whole section crushes, the analysis **removes** it and the gravity load it carried has to find another path. The axial-failure drift depends on axial load: 0.8–1.0 % for P/(A·f′c) above 0.10, and up to 2.0 % for low axial load.

**Coupling (link) beams** have lumped hinges. With proper anchorage they are shear-limited (ASCE 41 conforming / shear-controlled). With D2 the bar stress is capped by the short embedment (fs = fy·le/ld), and anchorage pull-out failure follows soon after the peak.

**Flat-slab punching** is checked continuously:

* drift-based capacity from ACI 318-19 §18.14.5.1 for PT slabs, using the *current* gravity shear ratio Vg/Vc, which rises as neighbouring supports fail;
* or punching whenever Vg ≥ Vc.

After punching, only the integrity / tendon capacity remains: 40 % of Vc at columns, 30 % at walls.

**Columns** are removed when their section crushes, defined as an average axial strain beyond 1 %.

### 2.2 The documented deficiencies (individually and in every combination)

| Code | Deficiency (official findings, 30 June 2025) | How it enters the model |
|---|---|---|
| D1 | Shear-wall concrete below the required 500 ksc | Wall f′c = 0.70 × specified (≈ 350 ksc) |
| D2 | Rebar embedment of link beams shorter than required | Link-beam bar stress limited to 0.5 fy; brittle anchorage pull-out after a 0.004 rad peak |
| D3 | Core walls reduced 300 → 250 mm | t = 250 mm, with the same steel per metre (the designer's "added reinforcement") |
| D4 | Drawings not compliant with the law (under-designed) | Wall shear steel designed without the required dynamic amplification (0.33–0.39 % instead of 0.8 %); no confined boundary zones |

Each framing has 16 variants:

* `REF` – none of the deficiencies;
* `D1`–`D4` – each one individually;
* 6 pairs and 4 triples;
* `D1D2D3D4` – all four, which is the as-built condition.

Together the four deficiencies cut the core's shear capacity roughly in half: 19 MN in Y and 36 MN in X, against 37 MN and 71 MN for the reference. They also raise the front pier's gravity axial-load ratio from 0.17 to 0.26.

### 2.3 Loading – identical for both models

* **Gravity** reflects the building at the time of the event, when it was structurally complete and being fitted out:
  * superimposed dead load 0.75 kPa;
  * live load 0.5 kPa;
  * façade 0.75 kPa.
* **Ground motion.** Three bidirectional records (GM1–GM3) were synthesised and spectrally matched (±5 %) to a reconstruction of the 28 March 2025 shaking in Bangkok:
  * PGA ≈ 0.024 g;
  * PGV ≈ 8–10 cm/s;
  * 5–95 % duration ≈ 57 s;
  * amplification at 1–3 s and 5–7 s (Ornthammarath et al. 2025).

  This event spectrum is about 35–40 % of the DPT 1301/1302-61 design-basis spectrum (Fig. 1). The scale factor **SF = 1 is the 2025 event**.

### 2.4 Analyses run on both models

| Analysis | What it answers |
|---|---|
| **Collapse-intensity search** (incremental dynamic analysis), for all 16 variants × 2 framings with GM1, and with GM2 / GM3 for the reference and all-four variants. SF = 1 (2025 event), then 2 → 3 → 4.5 → 6 → 8 until collapse, then bisection to within 20 %. | Does each deficiency set collapse at the 2025 level? How far is it from collapse? Where does failure start, and how does it spread? |
| **Pushover** in X and Y, all 32 variants | Lateral strength, initial yielding, failure sequence, core versus column share |
| **Pushdown**: one core pier's support withdrawn quasi-statically | How much of a lost pier's load the rest of the building can carry, and through which members |
| **Sudden removal** of lower core piers under gravity (5 scenarios) | Does the building arrest a sudden loss of core support? |

Collapse is defined as any of:

* storey drift above 10 % (sidesway);
* the core or a floor dropping 0.6 m (vertical);
* loss of dynamic equilibrium (non-convergence).

A run that stops because the solver landed in a corrupted state is labelled *numerical*, not collapse. It is repeated with a 0.01 s time step before it counts.
