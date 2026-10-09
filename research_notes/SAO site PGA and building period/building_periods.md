# Fundamental vibration period of tall RC buildings in Bangkok, applied to the SAO building (33 storeys, ~137 m, PT flat slab + eccentric RC core)

Research note on method: WebFetch failed for every domain tried (DNS "ENOTFOUND" for tandfonline, sciencedirect, iitk/nicee, springer, zenodo, bknix). Every finding below therefore comes from search-engine extracts of the cited pages (abstracts, snippets and secondary summaries), not from reading the full text. Exact regression coefficients behind paywalls (JEE 2026, J. Building Eng. 2025) or in PDFs (WCEE 2004) could NOT be read. Where a number is a secondary report, these notes say so.

Target building parameters used throughout: H = 137 m, N = 33 storeys.

## Q1. Measured fundamental periods of Bangkok RC high-rises (30–40 storeys / 100–150 m) and measured period–height relations for Bangkok/Thailand

### Takeaway
Two large ambient-vibration databases exist for Bangkok: about 50 buildings, 20–210 m tall (Poovarodom/Warnitchai/Petcharoen, 13WCEE 2004), and 98 buildings, 7–142 m tall (Ornthammarath et al., J. Building Eng. 2025). The 2025 study says measured Bangkok periods "correlate well" with the DPT 1302-09 code estimate, which secondary sources give as T = 0.02H. That works out to about 2.7 s at H = 137 m. Warnitchai's post-2025 talks use roughly T ≈ N/10 (24 storeys → 2.4 s, 60 storeys → ~6 s), which gives 3.3 s for N = 33. I could not access the exact fitted coefficients of either database.

### Cited Findings
- 13th WCEE (2004), Paper 1264, by Poovarodom, Warnitchai, Petcharoen et al.: ambient-vibration measurements on 50 RC buildings in Bangkok, 20–210 m tall and 5–54 storeys. It builds an empirical period formula from the data and defines the fundamental period as the first-mode period of a fixed-base model. — [13WCEE Paper 1264](https://www.iitk.ac.in/nicee/wcee/article/13_1264.pdf) (also at [nicee.org mirror](https://wcee.nicee.org/wcee/article/13_1264.pdf))
- The same study found that buildings of 15–25 storeys have fundamental periods "in the vicinity of" Bangkok's soft-soil predominant period of about 1 s. — [13WCEE Paper 1264](https://www.iitk.ac.in/nicee/wcee/article/13_1264.pdf)
- A Thai NCCE-28 conference paper tabulates a Poovarodom & Warnitchai relation for Thailand as T = 0.02H. The snippet did not show the units of H; metres is presumed. — [NCCE 28 paper](https://conference.thaince.org/index.php/ncce28/article/download/2168/1141/33067)
- A conference paper on a damaged Bangkok condominium cites a Warnitchai (2004) height-based formula of the form T = H/constant. It applies it to an 80 m, 32-storey building and gets T1 = 1.48 s, which is about 0.0185H. The equation text in the extracted PDF was garbled. — [ResearchGate: Seismic Damage of high-rise buildings in Bangkok ... Mw 6.4 Laos Earthquake](https://www.researchgate.net/publication/392283078_Seismic_Damage_of_high-rise_buildings_in_Bangkok_caused_by_soft_soil_amplification_from_Mw_64_Laos_Earthquake)
- Warnitchai's earlier AIT study surveyed about 50 buildings 20–210 m tall by ambient vibration and derived "relationships between building natural periods and building height". — [13WCEE Paper 744 / AIT Warnitchai](https://www.iitk.ac.in/nicee/wcee/article/13_744.pdf); [AIT news 2014](https://ait.ac.th/2014/05/new-study-led-by-aits-dr-pennung-warnitchai-indicates-threat-to-bangkoks-tall-buildings-from-distant-large-earthquakes/)
- Ornthammarath, Toe, Rupakhety, Málaga-Chuquitaype, Ranaweera and Pradittan, J. Building Engineering vol. 100 (2025):
  - ambient vibration on 98 RC buildings, 7–142 m tall (2–35 storeys), including hospitals, condominiums and offices;
  - buildings built both before and after the 2009 code;
  - periods identified with HVSR, FFT and half-power bandwidth;
  - regression formulas given for translational periods and for soil types D and E.
  — [ScienceDirect S2352710224032595](https://www.sciencedirect.com/science/article/pii/S2352710224032595)
- The same paper's other findings:
  - For Bangkok, measured periods "seem to correlate well with those estimates from the current seismic design code (DPT1302-09)".
  - Soil–structure interaction in Bangkok makes periods longer than those reported elsewhere in the literature for the same RC structures.
  - Formula-predicted periods for two instrumented hospitals in Chiang Mai and Chiang Rai were within 12% of earthquake-identified values.
  — [ScienceDirect S2352710224032595](https://www.sciencedirect.com/science/article/pii/S2352710224032595)
- News coverage of Warnitchai's 2025–2026 talks (EARTH survey) reported two groups:
  - about 1,000 mid-rise buildings of about 24 storeys with a sway period of about 2.4 s, about 10% damaged;
  - 6 very tall buildings of about 60 storeys with periods of about 6 s, 3 damaged (about 50%).
  — [Asia News Network / The Nation](https://asianews.network/bangkoks-soft-soil-basin-could-amplify-earthquake-shaking-by-3-6-times/); [Nation Thailand](https://www.nationthailand.com/thailand/bangkok/40064540); [Chiang Rai Times](https://www.chiangraitimes.com/news/bangkok/bangkok-earthquake-threat/)
- Caveat on those figures: in Warnitchai's BKNIX slides (22 May 2025), 2.4 s appears as a resonance illustration ("T = 5 s, T = 2.4 s, T = 1.1 s"), not as a labelled survey statistic. The slides also show building height back-calculated as H = T/0.02 and H = T/(1.3×0.02). — [Warnitchai, "The Bangkok Earthquake and what we learned from it", BKNIX Peering Forum slides](https://peeringforum.bknix.co.th/wp-content/uploads/2025/05/1.0-Bangkok-EQ-BKNIK-PF-22May2025.pdf)
- A 2025 Bangkok ground-motion study describes the fundamental period of 20–50-storey Bangkok buildings as lying between 1 and 3 s. — [Bull. Earthquake Eng. 2025, Far-field ground motion characteristics of the Bangkok Basin](https://link.springer.com/article/10.1007/s10518-025-02295-7)
- A dataset of top-floor accelerations exists for a 37-storey RC building in Bangkok during the 28 March 2025 event. It was recorded with a low-cost TUSHM sensor from Thammasat University and is intended for modal identification. The record description does not state the identified frequency. — [Zenodo 19379317](https://zenodo.org/records/19379317); [TUSHM](https://tu-shm.com/)

### Inferences
- Applying the measured Bangkok relations at H = 137 m, N = 33:
  - T = 0.02H gives 2.74 s.
  - T ≈ 0.0185H (implied by the 80 m / 1.48 s example) gives about 2.5 s.
  - T = 0.015H gives 2.06 s. I found no source stating 0.015H for Bangkok; it is listed only as a lower bound.
  - T = N/10 (Warnitchai's 24-storey/2.4 s and 60-storey/6 s pairs) gives 3.3 s.
- The 2004 statement that 15–25-storey buildings are about 1 s implies roughly 0.015–0.02H at 50–80 m, assuming about 3.2 m storeys. That fits the 0.02H family better than N/10. The N/10 values may reflect larger-amplitude or post-damage response, or simply be illustrative round numbers.
- The 98-building database goes up to 142 m and 35 storeys, so the SAO building (137 m, 33 storeys) lies at the top edge of the measured Bangkok range. Comparable buildings are therefore in the sample, but few are as tall.
- Bangkok periods measured by ambient vibration include soil–structure interaction; the 2025 paper says they are longer than literature values. They are "apparent" periods, which is appropriate for comparing with site response.

### Gaps
- I could not read the exact regression coefficients, scatter or R² from Poovarodom et al. (2004) or Ornthammarath et al. (2025), including whether the fit is T = aH or T = aH^b, because of paywall and fetch failure.
- I found no individually tabulated measured period for a specific Bangkok building of 30–40 storeys or 100–150 m.
- I did not find Lukkunaprasit- or Chandler-authored Bangkok measured-period data in this search round.

## Q2. Periods observed in instrumented Bangkok tall buildings during the 28 March 2025 Mw 7.7 earthquake, and period lengthening

### Takeaway
The 2026 Journal of Earthquake Engineering paper (Thammasat University group) analysed ambient and strong-motion data from several Bangkok RC high-rises before, during and after the event. Several buildings had permanent period elongation of up to 40%, and transient elongation during shaking was implied. The abstract extracts did not give per-building periods in seconds.

### Cited Findings
- "Dynamic Characteristics of Tall Buildings in Bangkok Associated with the 28 March 2025 Mw 7.7 Teleseismic Earthquake", Journal of Earthquake Engineering, DOI 10.1080/13632469.2026.2676969 (Thammasat University affiliation), reports:
  - ambient and strong-motion measurements from multiple RC high-rises, analysed for natural periods and damping before, during and after the event;
  - PGA of only about 0.02 g, with long-period spectral amplitudes amplified more than ten times;
  - "several structures exhibited permanent period elongation of up to 40%".
  — [Taylor & Francis abstract](https://www.tandfonline.com/doi/abs/10.1080/13632469.2026.2676969)
- Bangkok ground motion during the event had amplified spectral peaks near 1.6, 2.8 and 6.3 s, close to the natural periods of many high-rises. — [Nation Thailand](https://www.nationthailand.com/thailand/bangkok/40064540); [Asia News Network](https://asianews.network/bangkoks-soft-soil-basin-could-amplify-earthquake-shaking-by-3-6-times/)
- Warnitchai's AOGS 2025 abstract says many long-period high-rises were "strongly shaken by the resonance effect" and gives the damage counts:
  - several hundred buildings with non-structural damage;
  - about 10 with significant structural-wall damage (concrete crushing, bar buckling);
  - one 30-storey building (the SAO building) totally collapsed.
  — [AOGS2025 Warnitchai abstract](https://www.asiaoceania.org/aogs2025/public.asp?page=SS04_WARNITCHAI.asp)
- A TSER 2025 paper applying the JMA long-period intensity scale found Bangkok motions of Class 3, with dominant periods around 6 s. — [EARTH Digital Library item 32](https://earth.nrct.go.th/EarthLib/item.php?id=32)
- WTW's analysis puts the Bangkok motions in the 0.8–3.4 s range, which it maps to buildings of roughly 13–55 storeys. — [WTW, "Long waves and tall buildings"](https://www.wtwco.com/en-sg/insights/2025/08/long-waves-and-tall-buildings)
- Bangkok basin site periods range from about 1 s to over 6 s depending on location and depth to bedrock. — [Bull. Earthquake Eng. 2025](https://link.springer.com/article/10.1007/s10518-025-02295-7)

### Inferences
- Applying the 40% maximum permanent elongation to a 2.0–2.7 s pre-event (ambient) period gives about 2.8–3.8 s after the event. Transient periods during strong shaking are usually at least as long as the permanent post-event value.
- A first-mode period of about 2.7–3.3 s would sit close to the 2.8 s spectral peak that the Bangkok records reportedly showed. This is relevant to resonance arguments for the SAO building, but it is inference, not a published finding.

### Gaps
- I could not get the per-building periods in seconds, building heights, or during-shaking (transient) periods from the JEE 2026 full text.
- The identified frequency of the 37-storey Zenodo building is not stated in the record description. The raw data (BKK37FLbld_28Mar2025.zip) would need processing.

## Q3. Code formulas evaluated at H = 137 m, N = 33

### Takeaway
The code formulas give about 2.0 s at the low end and about 2.7–3.3 s once the empirical Bangkok coefficient or the upper-limit multipliers are applied:

| Formula | Result |
|---|---|
| Thai DPT 0.02H | 2.74 s |
| ASCE 7 "all other structures" Ta | 1.95 s |
| ASCE 7 Cu·Ta with Cu = 1.4 | 2.74 s |
| ASCE 7 Cu·Ta with Cu = 1.7 | 3.32 s |
| Eurocode 8, Ct = 0.05 (non-frame) | 2.00 s |
| Eurocode 8, Ct = 0.075 (RC frame) | 3.00 s |

### Cited Findings
- Thai standard (DPT 1301/1302-61): the fundamental period of RC buildings may be taken as T = 0.02H, or from eigenvalue analysis of a finite-element model. The period used must not exceed 1.5 × (0.02H). Source is secondary; I could not access the standard text. — [Engineering Journal (Thailand), "Verification of Design Forces Used in Seismic Design"](https://engj.org/index.php/ej/article/view/4685/1472)
- Background on DPT 1302-09: it was issued in 2009 by adopting ASCE 7-05 and was later superseded by DPT 1301/1302-61 (2018). — [ScienceDirect S2352710224032595](https://www.sciencedirect.com/science/article/pii/S2352710224032595); [Poovarodom, "A New Earthquake Resistant Design Standard for Buildings in Thailand"](https://dspace.spu.ac.th/bitstream/123456789/5894/1/ACEE0232_Poovarodom_A%20New%20Earthquake%20Resistant%20Design%20Standard%20for%20Buildings%20in%20Thailand.pdf)
- Measured Bangkok periods correlate well with the DPT 1302-09 estimate. — [ScienceDirect S2352710224032595](https://www.sciencedirect.com/science/article/pii/S2352710224032595)
- Calculated values. These are my own arithmetic, using the standard code forms ASCE 7 Ta = Ct·h^x and EC8 T1 = Ct·H^0.75. The coefficients are standard code values from general knowledge, not from a fetched source in this round. H^0.75 = 137^0.75 = 40.04.

| Formula | Value at H = 137 m, N = 33 |
|---|---|
| DPT 1301/1302-61: T = 0.02H | 2.74 s |
| DPT upper limit 1.5 × 0.02H | 4.11 s |
| ASCE 7 "all other systems" (incl. shear walls), Ct = 0.0488 (m), x = 0.75 | Ta = 1.95 s |
| ASCE 7 Cu·Ta, Cu = 1.4 (SD1 ≥ 0.4 g) | 2.74 s |
| ASCE 7 Cu·Ta, Cu = 1.7 (SD1 ≤ 0.1 g) | 3.32 s |
| ASCE 7 RC moment frame, Ct = 0.0466, x = 0.9 (not applicable, shown for reference) | 3.90 s |
| Eurocode 8, Ct = 0.05 ("all other structures", incl. RC walls) | 2.00 s |
| Eurocode 8, Ct = 0.075 (RC moment frames) | 3.00 s |
| Rule of thumb T = 0.1N = N/10 | 3.30 s |
| T = 0.015H | 2.06 s |

### Inferences
- The SAO building's lateral system is an RC core/shear walls with a PT flat slab. ASCE 7's "all other" category (1.95 s) and EC8's Ct = 0.05 (2.00 s) are the nominal code-applicable values. They are deliberately short (conservative for force), and ASCE notes they underestimate measured periods of tall buildings.
- EC8's formula is formally limited to H ≤ 40 m, so applying it at 137 m is an extrapolation.
- The Thai 0.02H (2.74 s) equals ASCE Cu·Ta at Cu = 1.4. It is the formula that Bangkok measurements reportedly validate.

### Gaps
- I did not obtain the DPT 1301/1302-61 clause text, so the 0.02H coefficient, whether it differs for wall versus frame systems, and the 1.5 multiplier are confirmed only through one secondary paper.

## Q4. Published estimates of the SAO building's own period

### Takeaway
I found no published fundamental period, from measurement, an ETABS/FE model or an investigation report, for the SAO building. The government investigation used simulations but released only qualitative conclusions.

### Cited Findings
- The PM-announced investigation (June 2025) used simulations to recreate the building's seismic response. It attributed the collapse to design and construction flaws, especially the shear walls around the lift and stair cores, with failure initiating at floors 1–4. No modal properties were published. — [Nation Thailand](https://www.nationthailand.com/news/general/40051947); [ThaiPublica](https://thaipublica.org/2025/06/prime-minister-reveals-audit-office-collapse-report/)
- The March 2026 SAO report lists four causes:
  - lower-floor walls failing under seismic shear;
  - shear-wall concrete cores below specified strength;
  - short rebar embedment at link-beam-to-wall joints;
  - drawings not compliant with law.
  It gives no period. — [The Star, 20 Mar 2026](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/03/20/thai-audit-office-releases-report-on-building-collapse-cites-four-main-causes)
- Investigators flagged the core-wall thickness being reduced from 30 cm to 25 cm, and a government panel noted the building's asymmetry (eccentric core). — [Thailand Construction](https://thailand-construction.com/reduced-thickness-of-elevator-shaft-walls-now-in-focus-on-bangkoks-collapsed-state-audit-office-building/); [BKK Tribune](https://bkktribune.com/govt-appointed-panel-focuses-its-probe-on-design-of-collapsed-sao-building/)
- The "8 seconds" often quoted is the collapse duration. One account splits it into about 3 s for lower-storey failure and about 5 s for the fall, with a 4.9 s free-fall check. It is not a vibration period. — [Bangkok Post opinion](https://www.bangkokpost.com/opinion/opinion/3225058/state-audit-office-collapse-still-demands-answers); [BKK Tribune](https://bkktribune.com/8-critical-seconds-how-the-30-storey-building-collapsed-into-a-layer-cake/)
- Sources disagree on the storey count, citing both 30 and 33 storeys. — [Wikipedia](https://en.wikipedia.org/wiki/Collapse_of_Thailand_State_Audit_Office_building)

### Inferences — best-supported estimate for SAO
- **Central estimate, small-amplitude (as-built, no SSI-induced damage): about 2.5–2.8 s, best value about 2.7 s.** This rests on the Bangkok-validated T = 0.02H (2.74 s), which coincides with ASCE Cu·Ta at Cu = 1.4 (2.74 s), and on the 98-building database reaching 142 m.
- **Plausible range: 2.0–3.3 s.**
  - The lower bound is the code Ta for wall systems (ASCE 1.95 s, EC8 2.00 s) and 0.015H (2.06 s).
  - The upper bound is N/10 (3.3 s) and ASCE Cu·Ta at Cu = 1.7 (3.32 s).
- **During strong shaking, an effective period of about 3–3.8 s is plausible** (2.7 s × 1.1–1.4), given the reported up-to-40% elongation in Bangkok high-rises. This is an extrapolation.
- Building-specific considerations:
  - Under construction, the building had no façade or partitions. That lowers mass and removes non-structural stiffness, but non-structural stiffness matters most for small-amplitude periods, so the net effect is uncertain.
  - The PT flat-slab plus core system has little frame action, which tends to lengthen the period relative to frame-wall buildings.
  - The eccentric core causes lateral-torsional coupling, so the first mode may be coupled and the torsional period may sit close to the translational periods.
  - The reported thinning of the core walls (30 to 25 cm) would also lengthen the period.
  - None of these effects is quantified in published sources.

### Gaps
- There is no measured or modelled period for the SAO building in public sources. The investigating institutions' internal simulation reports (Chulalongkorn, Kasetsart, DPT and others) may contain modal results but were not found publicly.
