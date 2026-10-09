# ETABS vs OpenSees comparison kit (version 2.0 models)

1. Read **`ETABS_input_guide_ModelA_ModelB.pdf`** and build Model A (as-built flat slab) and
   Model B (proposed beam-slab) in ETABS with exactly those inputs.
2. Run the cases in Section 9 of the guide (and optionally the pushover in Section 11).
3. Copy the files from `templates/` to `filled/` and type the ETABS results into the empty
   ETABS columns. Each row already shows the OpenSees value.
4. From the `phase2_opensees_2.0` folder, run `python3 etabs_comparison/compare_with_etabs.py`.
   The results are written to `output/`:
   * `ETABS_vs_OpenSees_<REF|D1D2D3D4>.csv` – difference in % for each quantity, with a PASS / CHECK flag;
   * `fig_etabs_vs_opensees_*.png` – storey shear and drift overlays;
   * `fig_pushover_etabs_vs_opensees.png` – pushover overlay.

The OpenSees side comes from `run_04_etabs_comparison.py` (elastic, design loads), run once
for the original models and once with `D1D2D3D4`, and from the REF pushovers in
`results/pushover/`. To regenerate the guide: `python3 etabs_comparison/make_guide_pdf.py`
(needs reportlab).
