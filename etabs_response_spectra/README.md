# ETABS response-spectrum inputs from Ornthammarath et al. (2025), Fig. 12

These are the Section 6 inputs for the *ETABS Elastic Modeling Input Sheet, Rev 3*:
* Function 1, the DPT design spectrum;
* Function 2, the 2025 recorded motion.

Both are read from Fig. 12 of Ornthammarath et al. (2025), *Far-field ground motion characteristics of the Bangkok Basin, Thailand, in the 2025 Mw 7.7 Mandalay earthquake: initial insights*, Bull. Earthquake Eng., doi 10.1007/s10518-025-02295-7. All spectra are at 5 % damping, in g.

**Start with `ETABS_Section6_spectrum_inputs.pdf`.** It holds the tables, the recommendation and the ETABS steps.

## Files

| File | What it is |
|---|---|
| `ETABS_Section6_spectrum_inputs.pdf` | Addendum to the input sheet: corrected Function 1, Function 2 tables, ETABS steps |
| `etabs_functions/RS-2025-PWSA.txt` | **Function 2 (recommended RS-2025-REC)**, ETABS "From File" format (Period, Sa in g) |
| `etabs_functions/RS-2025-PTNA.txt` | Function 2 sensitivity case: nearest station to the site, at the basin edge |
| `etabs_functions/RS-2025-BKSI.txt`, `-KMUA.txt`, `-BKKA.txt`, `-BASIN-MEAN.txt` | Other basin stations, and the mean of the five |
| `etabs_functions/RS-DPT61-Z5-DBE.txt` | **Function 1 corrected:** DPT DBE as plotted in Fig. 12, corner points 0–6 s, Sa ∝ 1/T beyond 6 s (assumed) |
| `etabs_functions/RS-DPT61-Z5-MCE.txt` | DPT MCE, same layout |
| `fig12_digitized_spectra.csv` | All seven stations, plus the basin mean, basin max, DBE and MCE, on one period grid |
| `fig_spectra.png` | The digitised spectra, one panel per station |
| `fig_check_overlay.png` | Digitised points drawn over the source figure (accuracy check) |
| `digitize_fig12.py`, `make_addendum_pdf.py` | Reproduce everything: `python3 digitize_fig12.py && python3 make_addendum_pdf.py` |
| `source/fig12_ornthammarath_2025.png` | The figure that was digitised |

## How the values were read

* Each panel is calibrated on its gridlines (0–10 s, 0–0.3 g).
* Every curve is then traced by its line colour, one pixel column at a time.
* Values are good to about **±0.03 s and ±0.002–0.003 g**, the width of the plotted lines.
* Check: the digitised DBE is two thirds of the digitised MCE at every corner, to within 0.001 g, as the code defines it.
* PWSA is drawn under BKSI in the figure. Past 8.9 s it is hidden completely, and BKSI's values are used there; the two curves coincide.

## Two findings for the input sheet

1. **Function 1 in the input sheet (Section 6.2) is 21–40 % below the DPT spectrum in Fig. 12, between 0 and 3.5 s.**
   * The sheet uses an ASCE-style shape with SDS = 0.15 g and SD1 = 0.20 g. That shape gives Sa(1.0 s) = 0.15 g, not the 0.20 g the sheet quotes.
   * The plotted code spectrum is a tabulated shape: 0.079 / 0.191 / 0.198 / 0.166 / 0.093 / 0.053 / 0.037 / 0.028 g at 0 / 0.5 / 1 / 2 / 3 / 4 / 5 / 6 s.
   * At the building's period (~2.9 s), recorded PWSA is 0.082 g. That is below the plotted DBE (0.100 g) but above the sheet's Function 1 (0.069 g). With the sheet's function, the Section 6.6 conclusion would reverse.
   * Use `RS-DPT61-Z5-DBE.txt`.
2. **The station choice matters at the building's period.**
   * At 2.9–3.0 s: PWSA 0.078–0.082 g, BKSI 0.056–0.067, KMUA 0.065–0.068, BKKA 0.050–0.052, PTNA only 0.030–0.031 g.
   * Recommended: RS-2025-REC = **PWSA** (deep basin, conservative), plus **PTNA** as a second function. PTNA is nearest to Chatuchak but at the basin edge.

## Not covered

* **2.5 % damping:** Fig. 13 of the paper gives PWSA at 2.5 % and needs its own digitising. For the DPT curve, the sheet's 0.25 g at 1.0 s corresponds to ×1.25. Uniform scaling by 1.25 is an approximation that is exact only at 1.0 s.
* **Zone:** the figure caption says *Bangkok DBE and MCE*. Zone 5 is taken from the input sheet, which cites the paper's 0.20 g at 1.0 s. Confirm the corners against the DPT 1301/1302-61 zone 5 table if it is available.
