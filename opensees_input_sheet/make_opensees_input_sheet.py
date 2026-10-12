"""
OpenSees NONLINEAR modelling input sheet, built to parallel the ETABS Elastic Modeling Input Sheet
(Rev 3) and the PhD modelling outline: same geometry, same 27-combination matrix, same two
framings; what changes is everything that makes the model nonlinear.

Run:  python3 make_opensees_input_sheet.py   ->  OpenSees_Nonlinear_Input_Sheet.pdf
"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "OpenSees_Nonlinear_Input_Sheet.pdf")

ss = getSampleStyleSheet()
INK, ACC, RULE, HEAD = "#333333", "#c75b2b", "#c9c4bb", "#efebe4"
TITLE = ParagraphStyle("T", parent=ss["Title"], fontSize=17, alignment=0, textColor=colors.HexColor(INK))
SUB = ParagraphStyle("S", parent=ss["Heading2"], fontSize=12, textColor=colors.HexColor(ACC), spaceBefore=0)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=14, textColor=colors.HexColor(INK), spaceBefore=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11, textColor=colors.HexColor(INK), spaceBefore=7)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9, leading=12.3, textColor=colors.HexColor(INK))
SM = ParagraphStyle("SM", parent=B, fontSize=8, leading=10.4, textColor=colors.HexColor("#666666"))
TC = ParagraphStyle("TC", parent=B, fontSize=7.9, leading=9.8)
TH = ParagraphStyle("TH", parent=TC, fontName="Helvetica-Bold")


def P(t, st=B):
    return Paragraph(t, st)


def table(rows, widths):
    data = [[P(str(c), TH if i == 0 else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(RULE)),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(HEAD)),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return t


W3 = [38, 62, 74]
W4 = [32, 48, 50, 44]


def build():
    s = []
    s += [P("OpenSees Nonlinear Modeling Input Sheet", TITLE),
          P("Models A and B, Bangkok State Audit Office Study", SUB),
          P("This is Phase 2, the nonlinear analysis in OpenSees (OpenSeesPy). It uses the <b>same building, the same 27 "
            "parameter combinations and the same two framings</b> as the ETABS Elastic Modeling Input Sheet. Model A "
            "is the as-built flat slab on the eccentric core; Model B is the proposed column-beam-slab frame. "
            "Geometry, materials, supports and seismic input are identical in both; the gravity framing system is "
            "the only variable."),
          P("The elastic sheet answers <i>how large are the demands</i>. This sheet answers <i>what yields, what "
            "fails, in what order, how the load redistributes, and at what shaking the building collapses</i>. "
            "Section 0 lists what changes; the rest gives the inputs."),
          P("0. What changes from the elastic sheet", H1),
          table([["Item", "ETABS elastic (Phase 1)", "OpenSees nonlinear (Phase 2)"],
                 ["Geometry, grid, 27-run matrix, supports", "As defined", "<b>Unchanged.</b> Same values, Sections 1-2 below."],
                 ["Materials", "E and Poisson's ratio only", "Full stress-strain curves: concrete crushing and cracking "
                  "(confined / unconfined), rebar yield, buckling and fracture. Section 3."],
                 ["Reinforcement", "Not needed", "<b>Required.</b> Every wall, column, beam and link beam needs bar "
                  "areas, because strength comes from them. Section 4."],
                 ["Stiffness modifiers (0.25, 0.35, 0.15 ...)", "Assigned by hand (ACI 6.6.3.1.1)", "<b>Removed</b> where "
                  "cracking is modelled by the fibres. Kept only for the elastic middle parts of members. Section 5."],
                 ["Elements", "Shells and frames", "Fibre wall piers with shear springs, plastic-hinge columns and "
                  "beams, link beams with an anchorage (bond) failure, slab strips with punching springs. Section 5."],
                 ["Seismic input", "Response spectrum (RS-DPT61-Z5, RS-2025-REC) with CQC and SRSS",
                  "<b>Ground-motion time histories</b>: acceleration records applied step by step, X and Y together. "
                  "The response spectrum is no longer the load. Section 7."],
                 ["Response spectrum", "Is the load case", "<b>Still used, but in the background:</b> (1) target "
                  "the records are selected or matched to; (2) design spectrum for sizing the reinforcement; "
                  "(3) the DBE / MCE levels the records are scaled to."],
                 ["R factor and I/R x g scale factor", "1.635 (R = 6), 1.226 (R = 8), 9.81 (recorded)", "<b>Removed.</b> "
                  "Ductility is modelled directly, so the records are applied unreduced. Intensity is set by a "
                  "scale factor on the record (SF), where SF = 1 is the 2025 event."],
                 ["Gravity", "Mass source only (DEAD); P-Delta from mass", "<b>Gravity is applied first</b> as a real "
                  "load (D, plus SDL and 0.25 L if adopted). Wall axial load and slab shear at each column control "
                  "failure."],
                 ["Damping", "5 % modal, built into the spectrum", "<b>2.5 % Rayleigh</b> (tall building), explicit "
                  "in the analysis. Section 8."],
                 ["Analyses", "Modal + response spectrum", "Modal (check against ETABS), gravity, pushover, nonlinear "
                  "time history and incremental dynamic analysis (IDA), sudden core-pier removal, pushdown. Section 9."],
                 ["Results", "Forces, drifts, demand/capacity", "Damage sequence, residual drift, load redistribution "
                  "paths, collapse yes/no, <b>collapse intensity</b>. Section 10."],
                 ["Deficiencies", "f'c only (as a matrix level)", "f'c levels <b>plus</b> link-beam embedment (bar "
                  "slip), which ETABS cannot model, and the non-compliant design option. Section 6."]],
                [44, 50, 80])]

    # 1 geometry -----------------------------------------------------------------------------------
    s += [PageBreak(), P("1. Fixed Geometry (unchanged from ETABS sheet Section 1)", H1),
          table([["Parameter", "Value", "Note for OpenSees"],
                 ["Building height", "137.0 m, 33 storeys", "One floor node set per storey"],
                 ["Ground floor / typical storey", "6.000 m / 4.094 m", "Storey elevations as ETABS sheet 1.1"],
                 ["Building grid", "39.0 x 39.0 m", ""],
                 ["Column grid", "7 lines each way at 6.50 m (0 ... 39.0)", "As adopted in ETABS sheet 2.3"],
                 ["Core", "17.0 x 17.0 m; X 11.0-28.0 m, Y 22.0-39.0 m; on the rear edge", "Eccentric: torsion is "
                  "captured through the rigid-diaphragm master node"],
                 ["Core wall thickness", "250 mm", ""],
                 ["Coupling (link) beam", "250 x 800 mm, clear span 2.4 m (ln/h = 3.0)", "Opening width as ETABS "
                  "sheet Section 9"],
                 ["Beams (Model B only)", "500 x 800 mm on every column line", "T-beam with slab flange"],
                 ["Columns", "1400 sq (F1-10), 1300 sq (F11-20), 1200 sq (F21-28), 800 dia (F29-33)", ""]],
                [40, 70, 64]),
          P("2. Iteration Matrix (unchanged) and run count", H1),
          P("The same three parameters at three levels each (27 combinations), for Model A and Model B (54 models). "
            "Run identifiers as in the ETABS sheet: <font face='Courier'>1A-ABC</font> is Model A, solid core, 4,000 psi, "
            "250 mm slab."),
          table([["Parameter", "Level A", "Level B", "Level C"],
                 ["Core configuration", "Solid, no openings", "2 openings (front face)", "4 openings (front + sides)"],
                 ["Core concrete f'c", "3,000 psi (21 MPa)", "4,000 psi (28 MPa)", "5,000 psi (35 MPa)"],
                 ["Slab thickness", "150 mm", "200 mm", "250 mm"]], [38, 44, 44, 48]),
          Spacer(1, 4),
          P("<b>What is new: each model is run many times, not once.</b> An ETABS response-spectrum case is one run "
            "per model. A nonlinear time history is one run per record per intensity. Recommended staging:"),
          table([["Stage", "Runs", "What it answers", "Compute (4 cores)"],
                 ["1. All 54 models", "Modal, gravity, pushover X and Y, 3 records at SF = 1 (2025 event)",
                  "Did any configuration fail in the actual event? Strength and ductility of every combination",
                  "about 1.5-2 days"],
                 ["2. All 54 models", "3 records scaled to DPT DBE and MCE at T1",
                  "Code-level performance (replaces the RS-DPT load cases)", "about 3 days"],
                 ["3. Selected models", "IDA: SF 0.5 to 8, bisection to 20 %",
                  "Collapse intensity: how much stronger than 2025 the shaking must be", "about 0.5 day per model"],
                 ["4. Selected models", "Sudden core-pier removal and pushdown",
                  "Alternate load paths and progressive collapse", "minutes per run"]], [30, 50, 64, 30]),
          P("Records of about 150 s take 30 to 60 minutes each in a 33-storey 3-D model. Run Stage 1 first; choose "
            "Stage 3 and 4 models from its results (for example the extremes and the mid-level 1A/1B-BBB).", SM)]

    # 3 materials ----------------------------------------------------------------------------------
    s += [PageBreak(), P("3. Materials (nonlinear stress-strain)", H1),
          P("Keep the ETABS names and switch the assignment between runs, never edit a material in place. In OpenSees "
            "each name becomes a set of uniaxial materials used in the fibre sections."),
          table([["Name", "OpenSees material", "Parameters", "Use"],
                 ["C-CORE-3000 / 4000 / 5000 unconfined", "Concrete02 (Kent-Park, linear tension softening)",
                  "f'c = 21 / 28 / 35 MPa; peak at 0.002; 20 % f'c residual at 0.006; ft = 0.17 sqrt(f'c); "
                  "tension softening to zero at ft/Ets = 0.002", "Wall cover and wall web; whole wall if "
                  "unconfined (non-compliant design option)"],
                 ["C-CORE-* confined", "Concrete02", "f'cc = 1.3 f'c; peak at 0.005; 50 % f'cc residual at 0.015",
                  "Wall boundary zones (0.6 m flanges, 1.0 m webs), code-compliant design"],
                 ["C-COL-5000 / 4000", "Concrete02", "Cover as unconfined; core f'cc = 1.2 f'c, peak at 0.004, "
                  "40 % residual at 0.012", "Column fibre hinges"],
                 ["C-SLAB-4000", "Concrete02 (beams); elastic (slab strips)", "28 MPa", "Model B beams; slab strips"],
                 ["SD40 bars", "Steel02 (Menegotto-Pinto) inside MinMax", "fy,exp = 1.1 x 400 = 440 MPa, E = 200 GPa, "
                  "b = 0.01, R0 = 18, cR1 = 0.925, cR2 = 0.15; bar drops out at -1 % (unconfined, buckling) or -3 % "
                  "(confined), and at +8 % (fracture)", "All longitudinal bars"]],
                [34, 38, 66, 36]),
          P("<b>Expected vs specified strength.</b> Nonlinear analysis uses expected strengths (steel 1.1 fy). "
            "Concrete uses the matrix level directly, because f'c is the deficiency variable: 3,000 psi stands for "
            "the low strength measured on site.", SM),
          P("4. Reinforcement (new: not needed in ETABS)", H1),
          P("Strength, yielding and failure all come from the bars, so every member needs reinforcement. The "
            "drawings are not public. The quantities are produced by a <b>design pass</b>: an elastic "
            "response-spectrum analysis to the DPT zone 5 spectrum (Fig. 12 values), with members sized to "
            "ACI 318-19 / DPT 1301/1302. The design pass is the same for Models A and B, and for every matrix "
            "level that changes the demand."),
          table([["Member", "Reinforcement", "Source"],
                 ["Core walls, vertical", "rho_v from flexure and axial demand, minimum 0.25 %", "Design pass"],
                 ["Core walls, horizontal (shear)", "rho_h for 2.7 x the RSA shear (ACI 18.10.3.1: 1.5 x 1.8), max "
                  "0.66 sqrt(f'c) on the section", "Design pass, code-compliant"],
                 ["Wall boundary zones", "Confined over 0.6-1.0 m (ties at about 100 mm)", "Code-compliant"],
                 ["Link beams 250 x 800", "Top and bottom bars from the RSA demand; 2-leg DB12 at 100 mm stirrups; "
                  "required embedment ld per ACI 25.4", "Design pass"],
                 ["Columns", "2.5 % (F1-10), 2.0 % above", "ETABS sheet Section 9"],
                 ["Beams 500 x 800 (Model B)", "Top and bottom from the RSA plus gravity demand", "Design pass"],
                 ["Slab (Model A)", "Column-strip top steel; integrity bars through the column", "Design pass, "
                  "ACI 8.7.4.2"]], [38, 92, 44])]

    # 5 elements -----------------------------------------------------------------------------------
    s += [PageBreak(), P("5. Elements (replaces ETABS shells and frames)", H1),
          table([["Component", "OpenSees element", "Key inputs", "Failure modelled"],
                 ["Core wall piers (between openings)", "forceBeamColumn per storey, fibre section of the whole pier "
                  "(webs and flanges), aggregated with a shear spring; rigid arms to the floor nodes",
                  "Fibres per Section 3; shear spring HystereticSM: crack at 0.6 Vn, Vn (ACI Eq. 18.10.4.1) on 0.1 "
                  "G Acv, held to 0.5 % shear drift, 20 % residual 0.25 % later (ASCE 41-17 Table 10-20)",
                  "Flexural crushing; shear failure; axial failure of a shear-damaged pier at 1-2 % drift (ASCE 41 'e')"],
                 ["Solid core (level A)", "One closed-section pier per storey", "St Venant torsion of the closed "
                  "tube", "As above; no link beams"],
                 ["Link beams 250 x 800", "Elastic element with end plastic hinges (rotational springs)", "My from bars; "
                  "effective EI 0.15 EIg (ATC 72, as ETABS); ASCE 41-17 Table 10-19: theta_p 0.02 (flexure) or "
                  "0.012 (shear-controlled), residual 50 % / 30 %", "Yield, shear failure; <b>anchorage pull-out</b> "
                  "when embedment is short (bar stress capped at fy x le/ld, pull-out at 0.004 rad, 10 % residual)"],
                 ["Columns", "forceBeamColumn, HingeRadau (hinge 0.5 D at each end), elastic middle",
                  "Fibre core and cover; -iter 30 1e-10", "Flexural hinging; axial crushing"],
                 ["Beams (Model B)", "Elastic T-beam with end hinges", "0.35 EIg middle; ASCE 41-17 Table 10-7: "
                  "theta_p 0.025, 20 % residual", "Hinging; full moment connection to columns and core walls"],
                 ["Slab (Model A)", "Effective-beam-width strips on every column line (Hwang & Moehle 2000)",
                  "Width 2c1 + l1/3 interior, c1 + l1/6 edge; cracked factor 0.5; hinges at the column-strip "
                  "moment capacity", "Flexural yielding (rarely governs)"],
                 ["Slab-column connection (Model A)", "Two zeroLength elements between the slab node and the column "
                  "node", "(1) Stiff in shear and moment, <b>removed when it punches</b>: ACI 318-19 18.14.5.1 drift "
                  "limit with the current Vg/Vc, or Vg >= Vc (Vc per ACI 22.6.5.2). (2) Post-punching vertical "
                  "spring at 40 % Vc (columns), 30 % (walls)", "<b>Punching</b> and punching cascade"],
                 ["Slab (Model B)", "Not a separate element: the T-beam flange plus the diaphragm", "", "None (no "
                  "punching)"],
                 ["Floors", "Rigid diaphragm (rigidDiaphragm) with a master node per floor carrying mass and rotary "
                  "inertia", "Semi-rigid in ETABS: compare mode shapes", "-"],
                 ["P-Delta", "PDelta geometric transformation on columns and wall piers", "Not optional at 137 m", "-"]],
                [27, 45, 58, 44]),
          P("<b>What happens to the stiffness modifiers.</b> Fibre members crack and yield on their own, so 0.35 / 0.70 "
            "factors are not applied to them. Factors stay only where a member's middle part is modelled "
            "elastically: link beams 0.15, beams 0.35, slab strips 0.5. Check the cracked periods against ETABS; they "
            "should agree within about 10 %.", SM)]

    # 6 supports + deficiencies -------------------------------------------------------------------
    s += [P("6. Supports, Connections and Deficiencies", H1),
          table([["Item", "Setting", "Note"],
                 ["Base", "Fixed, all 6 DOF, at column bases and the wall pier bases", "As ETABS 5.1; no soil springs "
                  "(soft clay is in the input motion)"],
                 ["Column to slab (A)", "Moment connection through the punching element", "It transfers moment "
                  "until it punches, then becomes a hinge with residual shear"],
                 ["Beam to column (B)", "Fully fixed, no releases", "As ETABS"],
                 ["Slab or beam to core wall", "Continuous / fixed", "As ETABS"],
                 ["f'c deficiency", "Matrix levels A / B / C", "3,000 psi = about 0.60 of the specified 5,000"],
                 ["Link-beam embedment (4th official finding)", "Optional switch: le/ld = 1.0 (compliant) or 0.5",
                  "<b>Only possible in Phase 2</b>: bar stress capped at fy x le/ld, then pull-out"],
                 ["Non-compliant design (3rd official finding)", "Optional switch: wall shear steel for the "
                  "unamplified demand and unconfined boundaries", "Alternative reinforcement set from the design pass"]],
                [42, 62, 70])]

    # 7 seismic demand -----------------------------------------------------------------------------
    s += [PageBreak(), P("7. Seismic Demand: time histories instead of a response spectrum", H1),
          P("<b>The response spectrum is not applied to the model.</b> The model is shaken by acceleration records, two "
            "horizontal components at once (X and Y), integrated step by step. The soft clay is still represented "
            "only through the input motion, which is a free-field surface record from the basin."),
          table([["Input", "Value", "Source / note"],
                 ["Preferred records", "Actual 28 March 2025 records: PWSA (deep basin, conservative) and PTNA "
                  "(nearest to Chatuchak). Two horizontal components each", "Available from the corresponding author "
                  "(Ornthammarath, Mahidol University) on request, as stated in the paper"],
                 ["Fallback records", "3 synthetic 2-component records, spectrally matched (5 %) to the Fig. 12 PWSA "
                  "spectrum from 0.2 to 10 s; repeat for PTNA", "Digitised spectra: etabs_response_spectra/ (same "
                  "values as ETABS Function 2)"],
                 ["Duration", "Significant duration D5-95 of about 133-156 s", "Paper Table 2. Long-duration, "
                  "long-period shaking must be preserved: it drives damage accumulation"],
                 ["Intensity SF = 1", "The 2025 event as recorded (PGA about 0.02 g)", "No scaling, no R"],
                 ["Code level", "Records scaled so their 5 % spectrum matches DPT zone 5 DBE, then MCE, at T1 "
                  "(0.2T1-1.5T1 average)", "Replaces RS-DPT-U1/U2. DBE / MCE from Fig. 12 (corrected Function 1)"],
                 ["Collapse search (IDA)", "SF ladder 0.5, 1, 1.5, 2, 3, 4.5, 6, 8, then bisection to 20 %",
                  "Collapse intensity = SF at collapse"],
                 ["Directions", "Both components together; repeat with components swapped for selected runs",
                  "Replaces the SRSS directional combination"],
                 ["Accidental torsion", "Not added", "The core eccentricity is modelled explicitly; ETABS uses 0.05"]],
                [32, 78, 64]),
          P("<b>Where the response spectrum still appears.</b> (1) As the target the records are matched or scaled to. "
            "(2) In the design pass that sizes the reinforcement (Section 4). (3) In the modal and elastic check against "
            "ETABS. It is no longer how the earthquake load is applied.", B)]

    # 8 loads / damping ----------------------------------------------------------------------------
    s += [P("8. Gravity, Mass and Damping", H1),
          table([["Item", "Setting", "Why"],
                 ["Gravity load", "Self-weight (DEAD), plus SDL and 0.25 LL if adopted, applied in 10 load-control "
                  "steps, then held constant (loadConst) before the earthquake", "Wall axial load and slab shear at "
                  "each column govern crushing and punching. Use the same gravity as the ETABS mass source so the "
                  "two phases match"],
                 ["Mass", "From the same loads; lumped at the floor master node (X, Y, rotation)", "Matches ETABS "
                  "MASS-SELFWEIGHT"],
                 ["Damping", "<b>2.5 %</b> Rayleigh, anchored at T1 and max(T1/8, 0.35 s); not applied to the rigid "
                  "zeroLength springs", "Tall-building damping (DPT for H > 60 m; PEER TBI). Yielding adds hysteretic "
                  "energy loss on top"],
                 ["Damping, sensitivity", "5 % for selected runs", "Shows how much the result depends on it"]],
                [32, 82, 60]),
          P("9. Analyses", H1),
          table([["Analysis", "Settings", "Purpose"],
                 ["Modal", "Eigen, 12+ modes, after gravity", "Periods and mass participation; check against ETABS"],
                 ["Gravity", "Load control, 10 steps", "Starting state for every other analysis"],
                 ["Pushover", "Displacement control at the roof master node to 2.5 % drift; first-mode-like "
                  "load pattern (h^2), X and Y, both signs", "Strength, stiffness, sequence of yielding, ductility"],
                 ["Nonlinear time history", "Newmark average acceleration; dt = 0.02 s (repeat at 0.01 s if a step "
                  "fails numerically); KrylovNewton, fallbacks to Newton, NewtonLineSearch and ModifiedNewton, then "
                  "sub-steps; NormDispIncr 1e-5", "Response to the 2025 event and to the code levels"],
                 ["IDA", "Section 7 ladder", "Collapse intensity"],
                 ["Sudden core-pier removal", "Remove pier elements under gravity in one step; 5 % damping; 6 s",
                  "Alternate load path: does the floor system hold?"],
                 ["Pushdown", "Withdraw the removed pier's force gradually", "Static capacity of the alternate path, "
                  "and the force carried by each path"]], [32, 88, 54])]

    # 10 outputs + resolve ------------------------------------------------------------------------
    s += [P("10. Collapse Criteria and Outputs", H1),
          table([["Item", "Definition"],
                 ["Collapse", "Any one of: storey drift at a corner > 10 %; floor vertical drop > 0.6 m; or loss of "
                  "convergence after a wall, column or punching failure. Numerical stops are repeated at dt = 0.01 s; "
                  "a second stop counts as collapse"],
                 ["Damage events (time-stamped)", "Link-beam yield and failure, wall shear strength loss, wall axial "
                  "failure, column failure, punching, with location"],
                 ["Outputs per run", "Peak and residual drift per storey; base shear (core vs columns); torsion; "
                  "pier demand/capacity; gravity-load path before and after damage; event sequence"]], [40, 134]),
          P("11. To Resolve Before Building", H1),
          table([["Item", "Issue", "Suggested resolution"],
                 ["Reinforcement", "Not public; nonlinear results depend on it", "Design pass to the Fig. 12 DPT "
                  "spectrum, same rules for A and B; state it in the methodology"],
                 ["Records", "Actual 2025 records not yet obtained", "Request them. Until then use synthetic records "
                  "matched to the Fig. 12 PWSA spectrum, with the recorded duration"],
                 ["Slab type, Model A", "The outline gives a 4,000 psi slab; the investigation describes a "
                  "post-tensioned flat slab", "Decide PT or RC: it changes punching strength (PT: 0.29 sqrt(f'c) + "
                  "0.3 fpc) and the drift limit"],
                 ["Link-beam depth", "800 mm here. The current Phase 2 runs use 1.7 m (door spandrel), which gave "
                  "periods of 3.0-3.2 s", "Use 800 mm to match ETABS, and keep 1.7 m as a sensitivity"],
                 ["Grid", "7 lines at 6.5 m here. The current Phase 2 runs use 6 lines", "Rebuild the Phase 2 model "
                  "on the 7-line grid so both phases share it"],
                 ["Diaphragm", "Semi-rigid in ETABS, rigid in OpenSees", "Acceptable: compare modes; the vertical "
                  "redistribution after pier loss is carried by the slab strips and beams, not the diaphragm"],
                 ["Run count", "54 models x records x intensities", "Stage the runs as in Section 2"]],
                [28, 70, 76])]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, str(doc.page))
        canvas.restoreState()

    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                      bottomMargin=16 * mm, title="OpenSees Nonlinear Modeling Input Sheet").build(
        s, onFirstPage=footer, onLaterPages=footer)
    print("written", OUT)


if __name__ == "__main__":
    build()
