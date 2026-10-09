"""
Builds etabs_comparison/ETABS_input_guide_ModelA_ModelB.pdf - the step-by-step ETABS input
guide for Model A (as-built flat slab) and Model B (proposed beam-slab), matching the OpenSees
version 2.0 models exactly, and the procedure to bring the ETABS results back into the
OpenSees comparison (compare_with_etabs.py).
Run from phase2_opensees_2.0:  python3 etabs_comparison/make_guide_pdf.py
"""
import json
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
                                KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from sao import config as C                      # noqa: E402
from sao.spectra import _DPT_T, _DPT_SA          # noqa: E402

OUT = os.path.join(HERE, "ETABS_input_guide_ModelA_ModelB.pdf")
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#1d3557"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11.5, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#1d3557"))
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9, leading=12)
SM = ParagraphStyle("SM", parent=B, fontSize=7.8, leading=10)
NOTE = ParagraphStyle("NOTE", parent=B, backColor=colors.HexColor("#fff4d6"), borderPadding=5, spaceBefore=4, spaceAfter=6)
TC = ParagraphStyle("TC", parent=B, fontSize=7.8, leading=9.6)
TH = ParagraphStyle("TH", parent=TC, textColor=colors.white, fontName="Helvetica-Bold")


def P(t, st=B):
    return Paragraph(t, st)


def table(rows, widths, head=True):
    data = [[Paragraph(str(c), TH if (head and i == 0) else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    sty = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c2cc")),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if head:
        sty.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d3557")))
    t.setStyle(TableStyle(sty))
    return t


def bullets(items):
    return [P("&bull; " + x) for x in items]


def img(path, w_mm):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    return Image(path, width=w_mm * mm, height=w_mm * mm * ih / iw)


def build():
    S = []
    d = json.load(open(os.path.join(ROOT, "results/design.json")))
    os_ref = json.load(open(os.path.join(ROOT, "results/summary/E0_opensees_elastic.json")))

    # ---------------------------------------------------------------------------- title
    S += [P("ETABS input guide - Model A (as-built flat slab) and Model B (proposed beam-slab)", ss["Title"]),
          P("State Audit Office building, Phase 2 comparison with the OpenSees models (version 2.0). "
            "Follow this guide to build the two ETABS models so that they describe exactly the same "
            "structure as the OpenSees models, run the same analyses, and paste the results into the "
            "comparison templates.", B), Spacer(1, 4)]
    S.append(P("<b>Workflow</b>", H2))
    S.append(table([["Step", "Where", "What"],
                    ["1", "ETABS", "Build Model A and Model B with the inputs in Sections 1-8 (same grid, columns, core; only the floor framing differs)."],
                    ["2", "ETABS", "Run the gravity, modal and response-spectrum cases (Section 9). Optional: the pushover (Section 11)."],
                    ["3", "ETABS -> Excel", "Export the tables listed in Section 10 and copy the values into the CSV templates in "
                     "<font face='Courier'>phase2_opensees_2.0/etabs_comparison/templates/</font>; save them in "
                     "<font face='Courier'>etabs_comparison/filled/</font> with the same file names."],
                    ["4", "OpenSees folder", "Run <font face='Courier'>python3 etabs_comparison/compare_with_etabs.py</font>. It writes "
                     "a table of ETABS vs OpenSees with the difference in % and PASS / CHECK flags, plus overlay figures, into "
                     "<font face='Courier'>etabs_comparison/output/</font>."]],
                   [14, 28, 128]))
    S.append(P("<b>What the comparison checks.</b> It is an <b>elastic</b> comparison (the standard ETABS "
               "Phase 1 analyses): seismic weight, periods and mass participation, response-spectrum base "
               "shear and its split between core and columns, storey shears, storey drifts, roof "
               "displacement and gravity axial forces. A pushover comparison is optional (Section 11) "
               "because ETABS hinges cannot reproduce punching or the wall failure rules used in OpenSees.", NOTE))
    S.append(P("Two conditions are compared: <b>REF</b> = the original design (no deficiencies) and "
               "<b>D1D2D3D4</b> = the documented as-built condition. Start with REF.", B))

    # ---------------------------------------------------------------------------- 1 general
    S.append(P("1. Units, code and general settings", H1))
    S.append(table([["Item", "Setting"],
                    ["Units", "kN, m, C (consistent: stresses in kN/m<super>2</super>; enter MPa x 1000)"],
                    ["Concrete code", "ACI 318-19 (for section properties only; no design check needed)"],
                    ["P-Delta", "<b>Off</b> for the elastic comparison (the OpenSees modal / RSA model has no initial P-Delta). "
                     "On (non-iterative, based on gravity) only for the optional pushover."],
                    ["Diaphragms", "One <b>rigid</b> diaphragm per floor (D1 ... D33) assigned to all slab/joint objects of the floor"],
                    ["Base", "Fixed supports (all 6 DOF) at the base of every column and wall at level 0 (no soil springs)"],
                    ["Auto mesh", "Walls: 1.0 m max; slabs: 1.0 m max (rectangular mesh); add walls/columns as mesh points"]],
                   [40, 130]))

    # ---------------------------------------------------------------------------- 2 grid
    S.append(P("2. Grid and storeys (both models)", H1))
    S.append(table([["Grid", "Lines (m)"],
                    ["X lines A-F", ", ".join(f"{g:g}" for g in C.GRID)],
                    ["Y lines 1-6", ", ".join(f"{g:g}" for g in C.GRID)],
                    ["Plan", "39 m x 39 m; the core is at the rear (y = 39 m) edge, centred in x"]],
                   [40, 130]))
    S.append(Spacer(1, 4))
    S.append(table([["Storey", "Height (m)", "Elevation of floor (m)"],
                    ["Base", "-", "0.0"],
                    ["Story 1 (ground)", f"{C.H_GROUND:.3f}", f"{C.H_GROUND:.3f}"],
                    ["Story 2 ... Story 33 (32 typical)", f"{C.H_TYP:.5f}", f"{C.level_z(2):.3f} ... {C.level_z(33):.3f}"]],
                   [60, 40, 70]))
    S.append(P("Total height 137.0 m. Use 'Similar to' so all 33 floors share one plan.", SM))

    # ---------------------------------------------------------------------------- 3 materials
    S.append(P("3. Materials", H1))
    S.append(P("Isotropic concrete, Poisson 0.2, unit weight 24 kN/m<super>3</super>, E = 4700 sqrt(f'c) MPa. "
               "Rebar SD50 fy = 490 MPa, SD40 fy = 390 MPa, Es = 200,000 MPa (rebar only matters for the pushover).", B))
    mats = [["Material name", "f'c (MPa)", "E (MPa)", "Used for"],
            ["C49-WALL", "49.0", f"{C.Ec(49):,.0f}", "Core walls + link beams, storeys 1-16 (REF)"],
            ["C40-WALL", "40.0", f"{C.Ec(40):,.0f}", "Core walls + link beams, storeys 17-33 (REF)"],
            ["C34-WALL-D1", f"{49 * 0.7:.1f}", f"{C.Ec(49 * 0.7):,.0f}", "Walls storeys 1-16, as-built condition (D1 = 0.70 f'c)"],
            ["C28-WALL-D1", f"{40 * 0.7:.1f}", f"{C.Ec(40 * 0.7):,.0f}", "Walls storeys 17-33, as-built condition (D1)"],
            ["C55-COL", "55.0", f"{C.Ec(55):,.0f}", "Columns storeys 1-11"],
            ["C45-COL", "45.0", f"{C.Ec(45):,.0f}", "Columns storeys 12-22"],
            ["C35", "35.0", f"{C.Ec(35):,.0f}", "Columns storeys 23-33, all slabs, beams (Model B)"]]
    S.append(table(mats, [32, 20, 22, 96]))

    # ---------------------------------------------------------------------------- 4 columns
    S.append(P("4. Columns (both models)", H1))
    S.append(P("26 columns per floor - <b>no columns at the four plan corners</b> and none inside the core.", B))
    pts = C.column_points()
    rows = [["#", "x (m)", "y (m)", "#", "x (m)", "y (m)", "#", "x (m)", "y (m)"]]
    for i in range(0, 26, 3):
        r = []
        for j in range(3):
            if i + j < 26:
                c = pts[i + j]
                r += [str(i + j + 1), f"{c['x']:g}", f"{c['y']:g}"]
            else:
                r += ["", "", ""]
        rows.append(r)
    S.append(table(rows, [9, 18, 18] * 3))
    S.append(Spacer(1, 4))
    S.append(table([["Storeys", "Section", "Concrete", "Long. steel ratio (pushover only)", "Stiffness modifiers"],
                    ["1-3", "1400 x 1400 rectangular", "C55-COL", "2.0 %", "I22 = I33 = 0.70; J = 0.20"],
                    ["4-12", "1200 x 1200 rectangular", "C55-COL (1-11), C45-COL (12)", "2.0 % (<=6), 1.5 %", "same"],
                    ["13-20", "1000 x 1000 rectangular", "C45-COL", "1.5 % (<=15), 1.0 %", "same"],
                    ["21-28", "900 x 900 rectangular", "C45-COL (<=22), C35", "1.0 %", "same"],
                    ["29-33", "800 diameter circular", "C35", "1.0 %", "same"]],
                   [16, 38, 44, 42, 30]))

    # ---------------------------------------------------------------------------- 5 core
    S.append(P("5. Core walls and link beams (both models)", H1))
    S.append(P("The core is a 17 x 17 m box (wall centrelines x = 11 to 28 m, y = 22 to 39 m) with a cross wall at "
               "y = 30.5 m. Each side wall (x = 11 and x = 28) has <b>two 1.5 m openings</b>, at y = 25.5-27.0 and "
               "y = 34.0-35.5 m, full storey height minus the link beam. The openings split the core into three "
               "<b>piers</b>, which must be given ETABS <b>pier labels R, M, F</b> (the OpenSees results are reported "
               "per pier):", B))
    S.append(table([["Pier label", "Wall pieces (centreline coordinates)", "Shape"],
                    ["F (front)", "Front wall y = 22.0, x 11->28; side walls x = 11 and x = 28 from y = 22.0 to 25.5", "C"],
                    ["M (middle)", "Cross wall y = 30.5, x 11->28; side walls x = 11 and x = 28 from y = 27.0 to 34.0", "I"],
                    ["R (rear)", "Rear wall y = 39.0, x 11->28 (building rear face); side walls x = 11 and 28 from y = 35.5 to 39.0", "C"]],
                   [24, 128, 18]))
    S.append(Spacer(1, 4))
    S.append(table([["Item", "Model input"],
                    ["Wall element", "Shell-thin wall, thickness 300 mm (REF); <b>250 mm</b> for the as-built condition (D3)"],
                    ["Wall concrete", "C49-WALL storeys 1-16, C40-WALL storeys 17-33 (REF); C34 / C28 for D1"],
                    ["Wall stiffness modifiers", "f11 = f22 = f12 = <b>0.50</b> (0.5 EI and 0.5 GA in OpenSees); m11 = m22 = m12 = 0.25; weight 1.0"],
                    ["Link beams (4 per floor)", "Across each 1.5 m opening at every floor level: 300 wide (= wall t; 250 for D3) x <b>500 deep</b>. "
                     "Model as frame elements (or spandrels) joined to the wall edges; label them as spandrels S1-S4."],
                    ["Link beam modifiers", "I33 = <b>0.20</b>, I22 = 0.20, J = 0.20 (ACI/TBI effective stiffness); shear area 1.0"],
                    ["Link beam reinforcement (pushover)", f"{d['cb_As']['Z1']:.0f} mm<super>2</super> top and bottom, SD50; D2: embedment = 0.5 of the development length"]],
                   [44, 126]))
    S.append(Spacer(1, 4))
    S.append(img(os.path.join(ROOT, "figures/fig00_floor_plans.png"), 170))
    S.append(P("Figure 1. Typical floor plans exactly as modelled in OpenSees v2.0 (Model A left, Model B right). "
               "Columns black, core piers R / M / F coloured, link beams yellow, corner cantilevers magenta.", SM))

    # ---------------------------------------------------------------------------- 6 floors
    S.append(PageBreak())
    S.append(P("6. Floor framing - the only difference between the models", H1))
    S.append(P("6A. Model A - as-built post-tensioned flat slab", H2))
    S.append(table([["Item", "Model input"],
                    ["Slab", "<b>250 mm</b> shell-thin slab, C35, covering the whole 39 x 39 m floor <b>to the corners</b> (the "
                     "corners cantilever 5.5 m from the edge columns). No beams, no drop panels."],
                    ["Inside the core", "No structural slab (shafts). Draw a 'None' (null) area over the core interior to carry the landing load "
                     "(Section 7)."],
                    ["Slab stiffness modifiers", "Bending m11 = m22 = m12 = <b>0.25</b> (cracked PT flat plate); membrane 1.0 (rigid diaphragm anyway)."],
                    ["Post-tensioning", "Do <b>not</b> model tendons for the elastic comparison (they do not change elastic stiffness). "
                     "OpenSees uses 1.5 MPa average precompression only in the punching strength."],
                    ["Alternative (exact match)", "OpenSees represents the slab as effective-width strips along the column lines: width "
                     "2c<sub>1</sub> + l<sub>1</sub>/3 (interior) or c<sub>1</sub> + l<sub>1</sub>/6 (edge), 250 mm deep, 0.5 EI. Shell slabs with "
                     "m = 0.25 are the normal ETABS practice and should give periods within about 10 %."]],
                   [40, 130]))
    S.append(P("6B. Model B - proposed beam-slab", H2))
    S.append(table([["Item", "Model input"],
                    ["Slab", "250 mm shell-thin slab, C35, whole floor to the corners (except inside the core); bending m = 0.25"],
                    ["Beams", "<b>500 x 800</b> rectangular frame sections, C35, on every column line between supports "
                     "(column-column and column-core wall) - 45 per floor - plus <b>8 corner cantilevers</b> (5.5 m from the "
                     "nearest edge column to each corner, along both edges): <b>53 beams per floor</b>"],
                    ["Beam insertion point", "Top centre (8) so the slab sits on top of the beams"],
                    ["Beam stiffness modifiers", "I33 = <b>0.74</b> if the beam is a plain 500 x 800 rectangle (= 0.35 x I<sub>g</sub> of the "
                     "T-section with 6t flanges / I<sub>g</sub> of the rectangle; OpenSees uses 0.35 I<sub>g,T</sub>). Use 0.35 if you "
                     "define a T-section. I22 = 0.35, J = 0.20."],
                    ["Beam end connections", "<b>No releases</b> - all beams, including the 8 framing into the core walls, are fully "
                     "moment connected. At wall ends add a short rigid link or mesh the wall so the beam frames into wall nodes."],
                    ["Beam reinforcement (pushover)", "Top / bottom As (mm<super>2</super>), perimeter | interior beams: "
                     + "; ".join(f"{z}: {d['beam_As'][z]['perim'][0]:.0f}/{d['beam_As'][z]['perim'][1]:.0f} | "
                                 f"{d['beam_As'][z]['int'][0]:.0f}/{d['beam_As'][z]['int'][1]:.0f}" for z in ("Z1", "Z2", "Z3", "Z4"))
                     + " (zones Z1 storeys 1-8, Z2 9-16, Z3 17-24, Z4 25-33)"]],
                   [40, 130]))

    # ---------------------------------------------------------------------------- 7 loads
    S.append(P("7. Load patterns and mass source", H1))
    q = 0.25 * 24
    S.append(table([["Load pattern", "Type", "Design values (elastic comparison)", "Event values (pushover gravity)"],
                    ["DEAD", "Dead", "Self-weight multiplier 1.0 (slab 0.25 x 24 = 6.0 kPa; beams, walls, columns automatic)", "same"],
                    ["SDL", "Super dead", "1.50 kPa on all slab areas", "0.75 kPa"],
                    ["LIVE", "Live", "2.50 kPa on all slab areas", "0.50 kPa"],
                    ["FACADE", "Super dead", "Line load on the full perimeter (156 m) = 1.50 kPa x storey height: "
                     f"{1.5 * C.H_GROUND:.2f} kN/m storey 1, {1.5 * C.H_TYP:.2f} kN/m typical (half each side)", "0.75 kPa x storey height"],
                    ["CORE (null area)", "Super dead", f"0.30 x (6.0 + 1.5 + 2.5) = {0.3 * (q + 1.5 + 2.5):.2f} kPa over the core interior (landings, stairs)",
                     f"0.30 x (6.0 + 0.75 + 0.5) = {0.3 * (q + 0.75 + 0.5):.2f} kPa"]],
                   [28, 20, 70, 52]))
    S.append(P("<b>Mass source:</b> 'From loads' - DEAD 1.0 + SDL 1.0 + FACADE 1.0 + CORE 1.0 + <b>LIVE 1.0</b> "
               "(OpenSees takes the full gravity load as mass; if you prefer 0.25 x LIVE note that the weight will be about "
               "6-7 % lower and adjust). Lumped at stories, include lateral mass only, no vertical mass. "
               f"Target seismic weight (REF, design loads): Model A {os_ref['A']['W_kN'] / 1e3:.0f} MN, "
               f"Model B {os_ref['B']['W_kN'] / 1e3:.0f} MN.", NOTE))

    # ---------------------------------------------------------------------------- 8 spectrum
    S.append(P("8. Response spectrum function (DPT 1301/1302-61, design level)", H1))
    rows = [["T (s)"] + [f"{t:g}" for t in _DPT_T[:7]], ["Sa (g)"] + [f"{2 / 3 * s:.4f}" for s in _DPT_SA[:7]],
            ["T (s)"] + [f"{t:g}" for t in _DPT_T[7:]], ["Sa (g)"] + [f"{2 / 3 * s:.4f}" for s in _DPT_SA[7:]]]
    S.append(table(rows, [20] + [21] * 7, head=False))
    S.append(P("Define as a 'From file / user' function with damping 5 %. These are the design (2/3 x MCE) spectral "
               "accelerations in g, before dividing by R / I.", SM))

    # ---------------------------------------------------------------------------- 9 cases
    S.append(P("9. Load cases to run", H1))
    S.append(table([["Case", "Type", "Settings"],
                    ["GRAV", "Linear static", "DEAD 1.0 + SDL 1.0 + LIVE 1.0 + FACADE 1.0 + CORE 1.0 (design values) - gives the pier and column axial forces"],
                    ["MODAL", "Eigen", "12 modes, no P-Delta, mass from the mass source"],
                    ["RSX", "Response spectrum", "U1, function DPT, <b>scale factor = 9.81 x I / R = 9.81 x 1.25 / 5 = 2.4525</b>; "
                     "modal combination <b>CQC</b>, damping 5 %; directional combination: single direction; "
                     "<b>no accidental eccentricity</b>; do not scale to ELF"],
                    ["RSY", "Response spectrum", "Same in U2"]],
                   [18, 28, 124]))
    S.append(P("Do <b>not</b> scale the response-spectrum results up to 85 % of ELF: the comparison uses the unscaled "
               "values (OpenSees RSA / ELF = 0.34-0.44). The ELF base shear (Cs = 0.0335, T capped at 1.4 Ta = 2.74 s) is "
               "reported separately.", SM))

    # ---------------------------------------------------------------------------- 10 export
    S.append(P("10. What to export from ETABS and where it goes", H1))
    S.append(P("Templates (one set per model and condition): <font face='Courier'>ETABS_summary_&lt;A|B&gt;_&lt;REF|D1D2D3D4&gt;.csv</font> "
               "and <font face='Courier'>ETABS_storeys_&lt;A|B&gt;_&lt;REF|D1D2D3D4&gt;.csv</font>. Each row already shows the "
               "OpenSees value; type the ETABS value in the empty column. Leave a cell empty if you do not have the value.", B))
    S.append(table([["Template key(s)", "ETABS table (Display > Show Tables)", "What to copy"],
                    ["W", "Mass Summary by Story (or Base Reactions of GRAV)", "Total mass x 9.81, or total vertical reaction of GRAV (kN)"],
                    ["T1 ... T6", "Modal Periods and Frequencies", "Period of modes 1-6 (s)"],
                    ["UX1 ... RZ6, SumUX/UY/RZ", "Modal Participating Mass Ratios", "UX, UY, RZ of modes 1-6 and the cumulative sums at mode 12, in % (ETABS gives fractions: multiply by 100)"],
                    ["V_RSA_X, V_RSA_Y", "Base Reactions", "FX of RSX and FY of RSY (kN)"],
                    ["Vcore_RSA_X / _Y", "Pier Forces, Story1, Bottom", "Sum of V2 (in-plane) of piers R, M, F for RSX / RSY - or the X / Y components if you report in global axes"],
                    ["roof_RSA_X / _Y", "Joint Displacements, a joint at the plan centre (19.5, 19.5) of the roof", "UX for RSX, UY for RSY, in mm"],
                    ["P1_R, P1_M, P1_F, P1_cols", "Pier Forces, Story1, Bottom, case GRAV; Column Forces Story1", "Axial P of each pier; sum of P of the 26 columns (kN, compression positive)"],
                    ["Storeys sheet: shear X / Y", "Story Forces, Location = Bottom, RSX / RSY", "VX for RSX and VY for RSY (kN), storey 1-33"],
                    ["Storeys sheet: drift centre", "Joint Drifts of the plan-centre joint (19.5, 19.5) of each floor", "Drift X for RSX, drift Y for RSY, in % (= ratio x 100)"],
                    ["Storeys sheet: drift max", "Story Drifts (max over the floor)", "Drift X for RSX, drift Y for RSY, in %"]],
                   [38, 56, 76]))
    S.append(P("Then save the filled templates into <font face='Courier'>etabs_comparison/filled/</font> and run "
               "<font face='Courier'>python3 etabs_comparison/compare_with_etabs.py</font> from the "
               "<font face='Courier'>phase2_opensees_2.0</font> folder. Acceptance used: weight +/-5 %, periods and mass ratios "
               "+/-10 %, base shears +/-15 %, roof displacement +/-20 %, gravity forces +/-10 %. Typical reasons for a CHECK: "
               "a different slab stiffness modifier, a missed link beam or opening, beams released at the core, LIVE taken "
               "as 0.25 in the mass source, or P-Delta switched on.", NOTE))

    # ---------------------------------------------------------------------------- 11 pushover
    S.append(P("11. Optional - pushover in ETABS", H1))
    S.append(table([["Item", "Setting (to match the OpenSees pushover)"],
                    ["Gravity first", "Nonlinear static case PGRAV: DEAD 1.0 + SDL 1.0 + LIVE 1.0 + FACADE 1.0 + CORE 1.0 with the <b>event</b> values of Section 7; P-Delta on"],
                    ["Lateral load", "User load pattern: at the plan centre of each floor a force F<sub>i</sub> proportional to W<sub>i</sub> z<sub>i</sub><super>2</super> "
                     "(W<sub>i</sub> floor weight, z<sub>i</sub> floor elevation), in X (PUSHX) or Y (PUSHY)"],
                    ["Case", "Nonlinear static, start from PGRAV, displacement control at the roof plan-centre joint, up to 3 % of 137 m = 4.11 m, "
                     "save multiple states"],
                    ["Hinges - columns", "Auto P-M2-M3, ASCE 41-13 Table 10-8, at both ends (relative distance 0.05 / 0.95)"],
                    ["Hinges - walls", "Fibre P-M3 hinges at every storey of piers R, M, F (or at least storeys 1-4), confined ends only for REF (D4: unconfined)"],
                    ["Hinges - link beams", "Auto V2 / M3, ASCE 41-13 Table 10-19, conventional (non-diagonal) reinforcement; for D2 cap the moment at 0.5 x the full value"],
                    ["Hinges - beams (B)", "Auto M3, ASCE 41-13 Table 10-7, at both ends including at the core walls"],
                    ["Not reproducible in ETABS", "Flat-slab punching (ends the OpenSees Model A curve at about 1 % roof drift in X) and the wall axial-failure removal; expect ETABS curves to continue further"],
                    ["Export", "Pushover Curve (base shear vs monitored displacement) -> templates ETABS_pushover_&lt;A|B&gt;_&lt;X|Y&gt;.csv (roof_displacement_m, base_shear_kN)"]],
                   [40, 130]))
    S.append(Spacer(1, 4))
    S.append(img(os.path.join(ROOT, "figures/fig13_pushover_original_models.png"), 165))
    S.append(P("Figure 2. OpenSees pushover curves of the original models (base shear / weight vs roof drift); the "
               "comparison script plots your ETABS curves on top (in MN vs m).", SM))

    # ---------------------------------------------------------------------------- 12 deficiencies
    S.append(P("12. As-built condition (D1-D4) - what to change in ETABS", H1))
    S.append(table([["Deficiency", "Change in ETABS", "Effect on the elastic comparison"],
                    ["D1 low wall concrete (finding 2)", "Walls and link beams use C34-WALL-D1 / C28-WALL-D1 (0.70 f'c)", "Lower wall stiffness: longer periods"],
                    ["D2 short link-beam embedment (finding 4)", "No change for elastic analysis; pushover link-beam hinge capped at 0.5 x moment", "None (elastic)"],
                    ["D3 walls 300 -> 250 mm (noted reduction)", "Wall and link-beam thickness 250 mm", "Lower stiffness and weight"],
                    ["D4 non-compliant design (finding 3)", "No change for elastic analysis (reinforcement only); pushover: unconfined wall hinges, wall horizontal steel "
                     + ", ".join(f"{p} {d['walls']['noncompliant'][p]['Z1']['rho_h'] * 100:.2f} %" for p in "RMF") + " at storeys 1-8", "None (elastic)"]],
                   [44, 76, 50]))
    S.append(P("Compare the ETABS as-built condition against the OpenSees file E0_opensees_elastic_D1D2D3D4.json "
               "(templates *_D1D2D3D4.csv).", SM))

    # ---------------------------------------------------------------------------- 13 targets
    S.append(P("13. OpenSees target values (REF, design loads) - quick check while building", H1))
    a, b = os_ref["A"], os_ref["B"]
    S.append(table([["Quantity", "Model A", "Model B"],
                    ["Seismic weight", f"{a['W_kN'] / 1e3:.0f} MN", f"{b['W_kN'] / 1e3:.0f} MN"],
                    ["T1 / T2 / T3", " / ".join(f"{t:.2f}" for t in a["T"][:3]) + " s", " / ".join(f"{t:.2f}" for t in b["T"][:3]) + " s"],
                    ["Mode 1 UX / RZ", f"{a['mx'][0]:.0f} / {a['mrz'][0]:.0f} %", f"{b['mx'][0]:.0f} / {b['mrz'][0]:.0f} %"],
                    ["Mode 2 UY", f"{a['my'][1]:.0f} %", f"{b['my'][1]:.0f} %"],
                    ["RSA base shear X / Y", f"{a['rsa']['X']['V_kN'] / 1e3:.1f} / {a['rsa']['Y']['V_kN'] / 1e3:.1f} MN",
                     f"{b['rsa']['X']['V_kN'] / 1e3:.1f} / {b['rsa']['Y']['V_kN'] / 1e3:.1f} MN"],
                    ["Roof displacement X / Y", f"{a['rsa']['X']['roof_m'] * 1000:.0f} / {a['rsa']['Y']['roof_m'] * 1000:.0f} mm",
                     f"{b['rsa']['X']['roof_m'] * 1000:.0f} / {b['rsa']['Y']['roof_m'] * 1000:.0f} mm"],
                    ["Storey-1 pier axial R / M / F", " / ".join(f"{a['P_core_kN'][p] / 1e3:.1f}" for p in "RMF") + " MN",
                     " / ".join(f"{b['P_core_kN'][p] / 1e3:.1f}" for p in "RMF") + " MN"]],
                   [60, 55, 55]))
    S.append(P("If ETABS mode 1 is a pure X translation instead of coupled X + torsion (about 30 % UX + 40 % RZ), the core "
               "position or the diaphragm assignment differs between the models - check those first.", NOTE))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawString(15 * mm, 10 * mm, "SAO building - ETABS input guide for comparison with OpenSees v2.0")
        canvas.drawRightString(195 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
                            title="ETABS input guide - Model A and Model B", author="Phase 2 OpenSees study")
    doc.build(S, onFirstPage=footer, onLaterPages=footer)
    print("written", OUT)


if __name__ == "__main__":
    build()
