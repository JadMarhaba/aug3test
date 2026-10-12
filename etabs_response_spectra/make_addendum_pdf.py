"""
Addendum to the ETABS Elastic Modeling Input Sheet (Rev 3), Section 6: the actual response-
spectrum inputs read from Ornthammarath et al. (2025) Fig. 12.

Run digitize_fig12.py first, then:  python3 make_addendum_pdf.py
Output: ETABS_Section6_spectrum_inputs.pdf
"""
import csv
import os

import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ETABS_Section6_spectrum_inputs.pdf")

ss = getSampleStyleSheet()
INK, ACC, RULE, HEAD = "#333333", "#c75b2b", "#c9c4bb", "#efebe4"
TITLE = ParagraphStyle("T", parent=ss["Title"], fontSize=16, alignment=0, textColor=colors.HexColor(INK))
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=14, textColor=colors.HexColor(INK), spaceBefore=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11.5, textColor=colors.HexColor(ACC), spaceBefore=8)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9, leading=12.5, textColor=colors.HexColor(INK))
SM = ParagraphStyle("SM", parent=B, fontSize=8, leading=10.5, textColor=colors.HexColor("#666666"))
TC = ParagraphStyle("TC", parent=B, fontSize=8, leading=10)
TH = ParagraphStyle("TH", parent=TC, fontName="Helvetica-Bold")


def P(t, st=B):
    return Paragraph(t, st)


def table(rows, widths, bold_rows=()):
    data = [[P(str(c), TH if i == 0 else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    sty = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(RULE)),
           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(HEAD)),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    for r in bold_rows:
        sty.append(("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"))
    t.setStyle(TableStyle(sty))
    return t


def pairs_table(T, S, ncol=3):
    """T / Sa pairs in ncol column pairs, like the input sheet's Function 1 table."""
    n = int(np.ceil(len(T) / ncol))
    rows = [["T (s)", "Sa (g)"] * ncol]
    for i in range(n):
        r = []
        for c in range(ncol):
            k = c * n + i
            r += [f"{T[k]:.3f}", f"{S[k]:.4f}"] if k < len(T) else ["", ""]
        rows.append(r)
    return table(rows, [21, 21] * ncol)


def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "fig12_digitized_spectra.csv"))))
    T = np.array([float(r["T_s"]) for r in rows])
    st = {k[:-2]: np.array([float(r[k]) for r in rows]) for k in rows[0] if k != "T_s"}
    fn = {}
    for name in ("RS-DPT61-Z5-DBE", "RS-DPT61-Z5-MCE"):
        a = np.loadtxt(os.path.join(HERE, "etabs_functions", name + ".txt"))
        fn[name] = (a[:, 0], a[:, 1])
    return T, st, fn


def build():
    T, st, fn = load()
    Td, dbe = fn["RS-DPT61-Z5-DBE"]
    _, mce = fn["RS-DPT61-Z5-MCE"]
    sheet_T = [0, .05, .1, .15, .2, .267, .4, .6, .8, 1, 1.2, 1.333, 1.6, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10]
    sheet_S = [.06, .0769, .0938, .1106, .1275, .15, .15, .15, .15, .15, .15, .15, .125, .1, .08, .0667,
               .0571, .05, .04, .0333, .0286, .025, .016]
    s = []
    s += [P("ETABS Input Sheet, Section 6: spectrum inputs from Fig. 12", TITLE),
          P("Addendum to the ETABS Elastic Modeling Input Sheet, Rev 3, Models A and B, Bangkok State Audit "
            "Office Study", ParagraphStyle("st", parent=H2, spaceBefore=0)),
          P("Values are read from <b>Fig. 12 of Ornthammarath et al. (2025)</b>, <i>Far-field ground motion "
            "characteristics of the Bangkok Basin, Thailand, in the 2025 Mw 7.7 Mandalay earthquake: initial "
            "insights</i>, Bull. Earthquake Eng., doi 10.1007/s10518-025-02295-7. The figure shows elastic response "
            "spectra at 5 percent damping for the five basin stations and two stations outside the basin, with the "
            "DPT 1301/1302 (2018) Bangkok DBE and MCE spectra on the same axes."),
          P("<b>How the values were obtained.</b> Each panel was calibrated on its gridlines (0 to 10 s, 0 to "
            "0.3 g). Every curve was then traced by its line colour, pixel column by pixel column. The digitised "
            "points were drawn back over the source figure to check them (fig_check_overlay.png). "
            "<b>Accuracy:</b> about 0.03 s in period and 0.002 to 0.003 g in Sa, which is the line width of "
            "the published figure. The code curves pass a check: the digitised DBE is two thirds of the "
            "digitised MCE at every corner, to within 0.001 g."),
          Spacer(1, 4)]

    # ---- Function 1 ---------------------------------------------------------------------------
    s += [P("6.2 Function 1: DPT design spectrum, corrected to Fig. 12", H1),
          P("<b>The Function 1 table in the input sheet does not match the code spectrum plotted in Fig. 12.</b> "
            "The sheet builds an ASCE-style curve from SDS = 0.15 g and SD1 = 0.20 g. That shape is not "
            "self-consistent: with Ts = 1.333 s it gives Sa(1.0 s) = 0.15 g, not the 0.20 g the sheet itself "
            "quotes as the zone 5 DBE at 1.0 s. The Bangkok basin spectrum in DPT 1301/1302 is a tabulated shape. "
            "In Fig. 12 it is a set of straight segments with corners at 0, 0.5, 1, 2, 3, 4, 5 and 6 s. Between 0 "
            "and 3.5 s the sheet's values are <b>21 to 40 percent below</b> the plotted DBE."),
          Spacer(1, 3)]
    rows = [["T (s)", "Fig. 12 DBE (g)", "Fig. 12 MCE (g)", "Input sheet Function 1 (g)", "Sheet / Fig. 12"]]
    for t in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6):
        d, m_, sh = np.interp(t, Td, dbe), np.interp(t, Td, mce), np.interp(t, sheet_T, sheet_S)
        rows.append([f"{t:g}", f"{d:.3f}", f"{m_:.3f}", f"{sh:.3f}", f"{sh / d:.2f}"])
    s += [table(rows, [18, 30, 30, 42, 26]), Spacer(1, 4),
          P("<b>Why it matters.</b> At the building's expected cracked period of about 2.9 s, the recorded PWSA "
            "ordinate is 0.082 g. The plotted DBE is 0.100 g, so the code demand exceeds the recorded demand, "
            "which is the finding in Section 6.6. Against the sheet's Function 1 value of 0.069 g, the recorded "
            "motion would <i>exceed</i> the design spectrum at the building's period. That would reverse the "
            "Section 6.6 conclusion."),
          PageBreak(),
          P("<b>Enter this instead.</b> Name it RS-DPT61-Z5, function type User Defined, damping ratio 0.05. "
            "These are the corner points; ETABS interpolates linearly between them, exactly as the code curve is "
            "drawn. The plotted curve stops at 6 s. Beyond 6 s, Sa = Sa(6 s) x 6 / T is <b>assumed</b> (constant "
            "velocity), so the function reaches 10 s as the sheet requires."), Spacer(1, 3)]
    rows = [["T (s)", "DBE, Sa (g)  [RS-DPT61-Z5]", "MCE, Sa (g)", "Source"]]
    for t, d, m_ in zip(Td, dbe, mce):
        rows.append([f"{t:.3f}", f"{d:.4f}", f"{m_:.4f}", "Fig. 12 corner" if t <= 6 else "assumed, Sa ~ 1/T"])
    s += [table(rows, [20, 50, 30, 45]), Spacer(1, 3),
          P("<b>Zone check.</b> The figure caption says only <i>Bangkok DBE and MCE</i>. The sheet identifies the "
            "curve as zone 5 because the paper quotes 0.20 g DBE at 1.0 s for zone 5, and the plotted DBE is "
            "0.198 g at 1.0 s. If the DPT zone 5 table is available, confirm these corners against it.", SM),
          P("<b>2.5 percent damping (Section 6.3).</b> If the 2.5 percent spectrum governs, the sheet gives 0.25 g "
            "DBE at 1.0 s, which is 1.25 times the 5 percent value. Uniform scaling of the table above by 1.25 is an "
            "approximation that is exact only at 1.0 s. File: RS-DPT61-Z5-DBE.txt x 1.25.", SM),
          Spacer(1, 6), P("Digitised spectra", H2),
          Image(os.path.join(HERE, "fig_spectra.png"), width=174 * mm, height=174 * mm * 960 / 2000),
          P("Bottom right: the input sheet's Function 1 (orange) against the DBE plotted in Fig. 12 (blue).", SM)]

    # ---- Function 2 ---------------------------------------------------------------------------
    s += [PageBreak(), P("6.4 Function 2: 2025 recorded motion", H1),
          P("Section 6.5 leaves the station choice open. The decision matters: at the building's period, the "
            "stations differ by a factor of about 2.5."), Spacer(1, 3)]
    rows = [["T (s)", "DBE", "PWSA", "BKSI", "KMUA", "BKKA", "PTNA", "Basin mean"]]
    for t in (2.5, 2.9, 3.0, 3.2, 3.5):
        rows.append([f"{t:g}", f"{np.interp(t, Td, dbe):.3f}"] +
                    [f"{np.interp(t, T, st[k]):.3f}" for k in ("PWSA", "BKSI", "KMUA", "BKKA", "PTNA", "basin_mean")])
    s += [table(rows, [16, 18, 18, 18, 18, 18, 18, 24]), Spacer(1, 3),
          P("<b>Recommendation: RS-2025-REC = PWSA</b>, with <b>PTNA as a second function</b> for sensitivity.", B),
          P("PWSA is in the deepest basin and has the largest ordinates in the building's 2.9 to 3.5 s range, "
            "so it is the conservative choice. It is also the station used for the PGA and for the Phase 2 "
            "nonlinear target. PTNA is nearest to Chatuchak but sits at the basin edge, with no 3 s peak and only "
            "0.03 g at 3 s. Running both brackets the answer for the actual site. Both use the 5 percent spectra; "
            "for 2.5 percent, PWSA is in Fig. 13 of the paper, which is not digitised here.", B), Spacer(1, 3),
          KeepTogether([P("RS-2025-REC (PWSA), damping 0.05, Sa in g", H2), pairs_table(T, st["PWSA"])])]
    s += [PageBreak(),
          KeepTogether([P("RS-2025-PTNA (sensitivity), damping 0.05, Sa in g", H2), pairs_table(T, st["PTNA"])]),
          Spacer(1, 4),
          P("BKSI, KMUA and BKKA, and the mean of the five basin stations, are in etabs_functions/ and "
            "fig12_digitized_spectra.csv on the same period grid. That grid is 0.1 s to 4 s, where the "
            "peaks are, 0.2 s to 6 s, then 0.5 s to 10 s. Below 0.3 s the spectra are flat at the PGA read from "
            "the figure: 0.016 to 0.021 g.", SM)]

    # ---- ETABS steps --------------------------------------------------------------------------
    s += [P("Entering the functions in ETABS", H1),
          table([["Step", "Action"],
                 ["1", "Define, Functions, Response Spectrum. Choose <b>From File</b>, then Add New Function."],
                 ["2", "Browse to etabs_functions/RS-2025-PWSA.txt (or type the table). Header lines to skip: 0. "
                       "Values are: <b>Period vs Value</b>. Function damping ratio: <b>0.05</b>."],
                 ["3", "Name it RS-2025-REC. Click <b>Convert to User Defined</b>, so the model no longer depends "
                       "on the text file."],
                 ["4", "Repeat for RS-2025-PTNA and RS-DPT61-Z5 (DBE file), or type the tables above."],
                 ["5", "Load cases as Section 7.3: RS-REC-U1 / U2 with RS-2025-REC, scale factor 9.81, no R. "
                       "Add RS-PTNA-U1 / U2 the same way for the sensitivity case."],
                 ["6", "Check: plot each function in ETABS and compare with fig_spectra.png. The PWSA peak should "
                       "be 0.082 g at 2.9 s, and the DBE 0.198 g at 1.0 s."]], [12, 150]),
          ]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, str(doc.page))
        canvas.restoreState()

    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                      bottomMargin=16 * mm, title="ETABS Section 6 spectrum inputs").build(
        s, onFirstPage=footer, onLaterPages=footer)
    print("written", OUT)


if __name__ == "__main__":
    build()
