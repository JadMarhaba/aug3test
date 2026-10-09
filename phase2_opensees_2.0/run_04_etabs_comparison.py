"""
STEP 4 (BOTH MODELS) - ELASTIC "ETABS-STYLE" COMPARISON of the original models
==============================================================================
The no-deficiency (REF) as-built flat slab and proposed beam-slab are built as LINEAR
ELASTIC models with cracked-section stiffness, loaded with the design loads, and analysed the
way an ETABS Phase 1 model normally is:

  1. gravity (dead + superimposed dead + live)      -> weight, axial forces in core / columns
  2. modal analysis (12 modes)                      -> periods, participating mass ratios (OpenSees returns them in %)
  3. response spectrum, DPT 1301/1302-61 design spectrum x I / R, CQC, X and Y separately
                                                    -> base shear, core vs column share,
                                                       storey shears, storey drifts

Cracked-section factors (stiffness modifiers) used - set the same values in ETABS:
  core walls 0.50 EI (flexure) and 0.50 GA (shear); link (coupling) beams 0.20 EI;
  columns 0.70 EI; beams (beam-slab) 0.35 EI; flat slab: effective-width strips
  (Hwang & Moehle, beta = 0.5 for PT, i.e. about 0.25-0.35 EI of the full bay width).
Response spectrum: DPT design spectrum, R = 5, I = 1.25, 5 % damping, CQC; drifts are the
ELASTIC response-spectrum drifts (multiply by Cd for the inelastic design drift).

Output: results/summary/E1_etabs_comparison.csv, E2_storey_profiles.csv,
        figures/fig12_etabs_comparison_profiles.png and REPORT_etabs_comparison.md
Usage:  python3 run_04_etabs_comparison.py            (original models, no deficiencies)
        python3 run_04_etabs_comparison.py D1D2D3D4   (documented as-built condition)
"""
import csv
import math
import os
import numpy as np
import openseespy.opensees as ops
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sao import config as C
from sao import plotting as P
from sao.capacities import PIERS
from sao.design import load_design, dpt_dbe, cqc, IMPORTANCE, R_FACTOR, _setup_static
from sao.registry import model_class

OUT = "results/summary"
FIG = "figures"
NMODES = 12
NAME = {"A": "As-built flat slab (2A)", "B": "Proposed beam-slab (2B)"}


def analyse(cfg, defs=""):
    v = C.Variant(config=cfg, load_state="design", **{d: (d in defs) for d in ("D1", "D2", "D3", "D4")})
    design = load_design()
    Model = model_class(cfg)
    # ---- 1. gravity -------------------------------------------------------------------------
    b = Model(v, design, mode="elastic").build()
    b.apply_gravity_pattern()
    _setup_static()
    ops.analyze(1)
    W = b.total_weight
    P_core = {p: ops.eleForce(b.pier_ele[(1, p)])[2] for p in PIERS}
    P_cols = sum(ops.eleForce(b.col_ele[(1, c)])[2] for c in range(b.ncol))
    # ---- 2. modal ---------------------------------------------------------------------------
    b = Model(v, design, mode="elastic").build()
    _setup_static()
    lam = np.array(ops.eigen(NMODES))
    om = np.sqrt(lam)
    T = 2 * np.pi / om
    mp = ops.modalProperties("-unorm", "-return")
    mx, my, mrz = (np.array(mp["partiMassRatiosMX"]), np.array(mp["partiMassRatiosMY"]),
                   np.array(mp["partiMassRatiosRMZ"]))
    # ---- 3. response spectrum (CQC) ---------------------------------------------------------
    Tn = np.concatenate([[0.0], np.logspace(-2, 1.3, 200)])
    Sa = dpt_dbe(Tn) * C.G * IMPORTANCE / R_FACTOR
    ops.timeSeries("Path", 50, "-time", *Tn, "-values", *Sa)
    hs = np.array([C.story_h(s) for s in range(1, C.N_STORY + 1)])
    xm = ym = C.PLAN / 2
    corners = [(0, 0), (C.PLAN, 0), (0, C.PLAN), (C.PLAN, C.PLAN)]
    rsa = {}
    for d in (1, 2):
        base_core, base_col, st_shear, drift_cm, drift_cor, roof = [], [], [], [], [], []
        for m in range(1, NMODES + 1):
            ops.responseSpectrumAnalysis(50, d, "-mode", m)
            vc = sum(ops.eleForce(b.pier_ele[(1, p)])[d - 1] for p in PIERS)
            vk = sum(ops.eleForce(b.col_ele[(1, c)])[d - 1] for c in range(b.ncol))
            base_core.append(vc)
            base_col.append(vk)
            sh = [sum(ops.eleForce(b.pier_ele[(s, p)])[d - 1] for p in PIERS)
                  + sum(ops.eleForce(b.col_ele[(s, c)])[d - 1] for c in range(b.ncol))
                  for s in range(1, C.N_STORY + 1)]
            st_shear.append(sh)
            # master node of each floor: u_x, u_y and rotation about z (rigid diaphragm)
            u = np.array([[0.0, 0.0, 0.0]] + [[ops.nodeDisp(b.master[i], 1), ops.nodeDisp(b.master[i], 2),
                                               ops.nodeDisp(b.master[i], 6)] for i in range(1, C.N_STORY + 1)])
            du = np.diff(u, axis=0)
            drift_cm.append(du[:, d - 1] / hs)
            dc = []
            for (cx, cy) in corners:     # rigid diaphragm: corner displacement from u, v, rotation
                ux = du[:, 0] - du[:, 2] * (cy - ym)
                uy = du[:, 1] + du[:, 2] * (cx - xm)
                dc.append((ux if d == 1 else uy) / hs)
            drift_cor.append(dc)
            roof.append(u[-1, d - 1])
        rsa[d] = dict(V=float(cqc(np.array(base_core) + np.array(base_col), om)),
                      V_core=float(cqc(base_core, om)), V_cols=float(cqc(base_col, om)),
                      shear=cqc(np.array(st_shear), om), drift_cm=cqc(np.array(drift_cm), om),
                      drift_cor=cqc(np.array(drift_cor), om).max(axis=0), roof=float(cqc(roof, om)))
    # equivalent lateral force (DPT / ASCE 7 form, Ta = 0.0488 H^0.75, Cu Ta cap 1.4)
    Ta = 0.0488 * C.H_TOTAL ** 0.75
    Tuse = min(T[0], 1.4 * Ta)
    Cs = max(float(dpt_dbe(np.array([Tuse]))[0]) * IMPORTANCE / R_FACTOR, 0.01)
    return dict(cfg=cfg, W=W, P_core=P_core, P_cols=P_cols, T=T, mx=mx, my=my, mrz=mrz, rsa=rsa,
                Ta=Ta, Tuse=Tuse, Cs=Cs, V_elf=Cs * W, b=b)


def main(defs=""):
    tag = defs or "REF"
    sfx = "" if tag == "REF" else f"_{tag}"
    res = {cfg: analyse(cfg, defs) for cfg in "AB"}
    # machine-readable copy for compare_with_etabs.py
    dump = {}
    for cfg, r in res.items():
        dump[cfg] = dict(variant=f"{cfg}-{tag}", W_kN=r["W"], T=r["T"].tolist(), mx=r["mx"].tolist(),
                         my=r["my"].tolist(), mrz=r["mrz"].tolist(), V_elf_kN=r["V_elf"],
                         P_core_kN={p: r["P_core"][p] for p in PIERS}, P_cols_kN=r["P_cols"],
                         rsa={dn: dict(V_kN=r["rsa"][d]["V"], V_core_kN=r["rsa"][d]["V_core"],
                                       V_cols_kN=r["rsa"][d]["V_cols"], roof_m=r["rsa"][d]["roof"],
                                       shear_kN=r["rsa"][d]["shear"].tolist(),
                                       drift_centre=r["rsa"][d]["drift_cm"].tolist(),
                                       drift_corner=r["rsa"][d]["drift_cor"].tolist())
                              for d, dn in ((1, "X"), (2, "Y"))})
    import json
    json.dump(dump, open(os.path.join(OUT, f"E0_opensees_elastic{sfx}.json"), "w"), indent=1)
    os.makedirs(OUT, exist_ok=True)
    # ---------------- table E1 ---------------------------------------------------------------
    rows = []
    def add(q, unit, fa, fb):
        rows.append([q, unit, fa(res["A"]), fb(res["B"]) if fb else fa(res["B"])])
    f1 = lambda x: f"{x:.1f}"
    add("Seismic weight W (design loads)", "MN", lambda r: f1(r["W"] / 1e3), None)
    for k in range(6):
        add(f"Mode {k + 1}: period", "s", lambda r, k=k: f"{r['T'][k]:.2f}", None)
        add(f"Mode {k + 1}: mass ratio UX / UY / RZ", "%",
            lambda r, k=k: f"{r['mx'][k]:.0f} / {r['my'][k]:.0f} / {r['mrz'][k]:.0f}", None)
    add("Cumulative mass ratio, 12 modes, UX / UY / RZ", "%",
        lambda r: f"{r['mx'].sum():.0f} / {r['my'].sum():.0f} / {r['mrz'].sum():.0f}", None)
    add("ELF: Ta = 0.0488 H^0.75 / period used / Cs", "s / s / -",
        lambda r: f"{r['Ta']:.2f} / {r['Tuse']:.2f} / {r['Cs']:.4f}", None)
    add("ELF base shear V = Cs W", "MN", lambda r: f1(r["V_elf"] / 1e3), None)
    for d, dn in ((1, "X"), (2, "Y")):
        add(f"RSA base shear {dn} (unscaled)", "MN", lambda r, d=d: f1(r["rsa"][d]["V"] / 1e3), None)
        add(f"RSA base shear {dn} / ELF", "-", lambda r, d=d: f"{r['rsa'][d]['V'] / r['V_elf']:.2f}", None)
        add(f"RSA {dn}: share to core / columns", "%",
            lambda r, d=d: f"{r['rsa'][d]['V_core'] / (r['rsa'][d]['V_core'] + r['rsa'][d]['V_cols']) * 100:.0f} / "
                           f"{r['rsa'][d]['V_cols'] / (r['rsa'][d]['V_core'] + r['rsa'][d]['V_cols']) * 100:.0f}", None)
        add(f"RSA {dn}: roof displacement (elastic)", "mm", lambda r, d=d: f"{r['rsa'][d]['roof'] * 1000:.0f}", None)
        add(f"RSA {dn}: max storey drift at centre (elastic)", "%",
            lambda r, d=d: f"{r['rsa'][d]['drift_cm'].max() * 100:.3f}", None)
        add(f"RSA {dn}: max storey drift at corners (elastic)", "%",
            lambda r, d=d: f"{r['rsa'][d]['drift_cor'].max() * 100:.3f}", None)
    add("Gravity: storey-1 axial, pier R / M / F", "MN",
        lambda r: " / ".join(f1(r["P_core"][p] / 1e3) for p in PIERS), None)
    add("Gravity: storey-1 axial, all core / all columns", "MN",
        lambda r: f"{sum(r['P_core'].values()) / 1e3:.1f} / {r['P_cols'] / 1e3:.1f}", None)
    with open(os.path.join(OUT, f"E1_etabs_comparison{sfx}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "unit", NAME["A"], NAME["B"]])
        w.writerows(rows)
    # ---------------- table E2 (storey profiles) ----------------------------------------------
    with open(os.path.join(OUT, f"E2_storey_profiles{sfx}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        hdr = ["storey"]
        for cfg in "AB":
            for dn in "XY":
                hdr += [f"{cfg}_shear_{dn}_MN", f"{cfg}_drift_centre_{dn}_pct", f"{cfg}_drift_corner_{dn}_pct"]
        w.writerow(hdr)
        for s in range(C.N_STORY):
            row = [s + 1]
            for cfg in "AB":
                for d in (1, 2):
                    r = res[cfg]["rsa"][d]
                    row += [f"{r['shear'][s] / 1e3:.2f}", f"{r['drift_cm'][s] * 100:.4f}", f"{r['drift_cor'][s] * 100:.4f}"]
            w.writerow(row)
    # ---------------- figure -------------------------------------------------------------------
    fig, axs = plt.subplots(1, 4, figsize=(14, 5.2), sharey=True)
    st = np.arange(1, C.N_STORY + 1)
    col = {"A": P.FLAT, "B": P.BEAM}
    for k, (d, dn) in enumerate(((1, "X"), (2, "Y"))):
        for cfg in "AB":
            r = res[cfg]["rsa"][d]
            axs[k].plot(r["shear"] / 1e3, st, color=col[cfg], lw=2, label=NAME[cfg])
            axs[2 + k].plot(r["drift_cm"] * 100, st, color=col[cfg], lw=2, label=f"{NAME[cfg]} - centre")
            axs[2 + k].plot(r["drift_cor"] * 100, st, color=col[cfg], lw=1.2, ls="--", label=f"{NAME[cfg]} - corner")
        axs[k].set_xlabel(f"Storey shear {dn} (MN)")
        axs[k].set_title(f"RSA storey shear, {dn}")
        axs[2 + k].set_xlabel(f"Storey drift {dn} (%)")
        axs[2 + k].set_title(f"RSA storey drift (elastic), {dn}")
    axs[0].set_ylabel("Storey")
    axs[0].legend(fontsize=7.5)
    axs[3].legend(fontsize=6.8)
    fig.suptitle("Elastic response-spectrum results of the original models (DPT spectrum, R = 5, I = 1.25, CQC) "
                 "- for comparison with ETABS", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(FIG, f"fig12_etabs_comparison_profiles{sfx}.png"), dpi=140)
    plt.close(fig)
    for r in rows:
        print(" | ".join(str(x) for x in r))


if __name__ == "__main__":
    import sys
    # no argument: original models (no deficiencies); "D1D2D3D4": documented as-built condition
    # (elastically only D1 = lower wall E and D3 = 250 mm walls change the stiffness)
    main(sys.argv[1] if len(sys.argv) > 1 else "")
