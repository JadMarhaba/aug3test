"""
ETABS vs OPENSEES COMPARISON (both models)
==========================================
Step 1 (done once, already done):  python3 compare_with_etabs.py --make-templates
        writes the fill-in templates into etabs_comparison/templates/ :
          ETABS_summary_<A|B>_<REF|D1D2D3D4>.csv  - weight, periods, mass ratios, base shears,
                                                    roof displacements, storey-1 pier forces
          ETABS_storeys_<A|B>_<REF|D1D2D3D4>.csv  - storey shear and storey drift, X and Y
          ETABS_pushover_<A|B>_<X|Y>.csv           - pushover curve (optional)
        Each template already shows the OpenSees value next to the empty ETABS column.
Step 2 (you):  copy the ETABS results into the ETABS_value / ETABS columns (see the PDF guide)
        and save the files into etabs_comparison/filled/ with the same names.
Step 3:  python3 compare_with_etabs.py
        writes etabs_comparison/output/ETABS_vs_OpenSees_<cond>.csv (difference in % with a
        PASS / CHECK flag) and figures fig_etabs_vs_opensees_<cond>.png and
        fig_pushover_etabs_vs_opensees.png.

Run from the phase2_opensees_2.0 folder:  python3 etabs_comparison/compare_with_etabs.py
"""
import csv
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from sao import config as C          # noqa: E402

TPL, FILLED, OUTD = (os.path.join(HERE, d) for d in ("templates", "filled", "output"))
NAME = {"A": "As-built flat slab (Model A)", "B": "Proposed beam-slab (Model B)"}
COND = {"REF": "original design, no deficiencies", "D1D2D3D4": "documented as-built condition (D1-D4)"}
# tolerance on |ETABS - OpenSees| / OpenSees for a PASS
TOL = {"W": 0.05, "T": 0.10, "M": 0.10, "V": 0.15, "R": 0.20, "P": 0.10, "S": 0.15, "D": 0.25}


def opensees(cond):
    sfx = "" if cond == "REF" else f"_{cond}"
    return json.load(open(os.path.join(ROOT, "results/summary", f"E0_opensees_elastic{sfx}.json")))


def summary_rows(o):
    """(key, description, unit, OpenSees value, tolerance group)"""
    rows = [("W", "Total seismic weight = mass source x g", "kN", o["W_kN"], "W")]
    for k in range(6):
        rows.append((f"T{k + 1}", f"Mode {k + 1} period", "s", o["T"][k], "T"))
    for k in range(6):
        for comp, lab in (("mx", "UX"), ("my", "UY"), ("mrz", "RZ")):
            rows.append((f"{lab}{k + 1}", f"Mode {k + 1} participating mass ratio {lab}", "%", o[comp][k], "M"))
    for comp, lab in (("mx", "UX"), ("my", "UY"), ("mrz", "RZ")):
        rows.append((f"Sum{lab}", f"Cumulative mass ratio {lab}, 12 modes", "%", sum(o[comp][:12]), "M"))
    for dn in "XY":
        r = o["rsa"][dn]
        rows += [(f"V_RSA_{dn}", f"RSA base shear {dn} (unscaled, CQC)", "kN", r["V_kN"], "V"),
                 (f"Vcore_RSA_{dn}", f"RSA base shear {dn} carried by core walls (sum of pier shears, storey 1)",
                  "kN", r["V_core_kN"], "V"),
                 (f"roof_RSA_{dn}", f"RSA roof displacement {dn} at the plan centre", "mm", r["roof_m"] * 1000, "R")]
    for p, lab in (("R", "rear"), ("M", "middle"), ("F", "front")):
        rows.append((f"P1_{p}", f"Storey-1 axial force, pier {p} ({lab}), gravity D+SDL+LL", "kN",
                     o["P_core_kN"][p], "P"))
    rows.append(("P1_cols", "Storey-1 axial force, sum of the 26 columns, gravity D+SDL+LL", "kN", o["P_cols_kN"], "P"))
    return rows


def make_templates():
    os.makedirs(TPL, exist_ok=True)
    os.makedirs(FILLED, exist_ok=True)
    for cond in COND:
        o = opensees(cond)
        for cfg in "AB":
            with open(os.path.join(TPL, f"ETABS_summary_{cfg}_{cond}.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["key", "description", "unit", "OpenSees_value", "ETABS_value"])
                for key, desc, unit, val, _ in summary_rows(o[cfg]):
                    w.writerow([key, desc, unit, f"{val:.6g}", ""])
            with open(os.path.join(TPL, f"ETABS_storeys_{cfg}_{cond}.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["storey", "OpenSees_shear_X_kN", "ETABS_shear_X_kN", "OpenSees_shear_Y_kN",
                            "ETABS_shear_Y_kN", "OpenSees_drift_centre_X_pct", "ETABS_drift_centre_X_pct",
                            "OpenSees_drift_max_X_pct", "ETABS_drift_max_X_pct", "OpenSees_drift_centre_Y_pct",
                            "ETABS_drift_centre_Y_pct", "OpenSees_drift_max_Y_pct", "ETABS_drift_max_Y_pct"])
                rx, ry = o[cfg]["rsa"]["X"], o[cfg]["rsa"]["Y"]
                for s in range(C.N_STORY):
                    w.writerow([s + 1, f"{rx['shear_kN'][s]:.0f}", "", f"{ry['shear_kN'][s]:.0f}", "",
                                f"{rx['drift_centre'][s] * 100:.4f}", "", f"{rx['drift_corner'][s] * 100:.4f}", "",
                                f"{ry['drift_centre'][s] * 100:.4f}", "", f"{ry['drift_corner'][s] * 100:.4f}", ""])
    for cfg in "AB":
        for dn in "XY":
            with open(os.path.join(TPL, f"ETABS_pushover_{cfg}_{dn}.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["roof_displacement_m", "base_shear_kN"])
                w.writerow(["", ""])
    print("templates written to", TPL)


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def compare():
    os.makedirs(OUTD, exist_ok=True)
    any_done = False
    for cond in COND:
        o = opensees(cond)
        rows, store = [], {}
        for cfg in "AB":
            fs = os.path.join(FILLED, f"ETABS_summary_{cfg}_{cond}.csv")
            if os.path.exists(fs):
                et = {r["key"]: _num(r["ETABS_value"]) for r in csv.DictReader(open(fs))}
                for key, desc, unit, val, grp in summary_rows(o[cfg]):
                    e = et.get(key)
                    if e is None:
                        continue
                    diff = (e - val) / val if val else float("nan")
                    rows.append([cfg, key, desc, unit, f"{val:.4g}", f"{e:.4g}", f"{diff * 100:+.1f}",
                                 "PASS" if abs(diff) <= TOL[grp] else "CHECK", f"+/-{TOL[grp] * 100:.0f}%"])
            fst = os.path.join(FILLED, f"ETABS_storeys_{cfg}_{cond}.csv")
            if os.path.exists(fst):
                store[cfg] = list(csv.DictReader(open(fst)))
        if not rows and not store:
            continue
        any_done = True
        with open(os.path.join(OUTD, f"ETABS_vs_OpenSees_{cond}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["model", "key", "quantity", "unit", "OpenSees", "ETABS", "difference_%", "result", "tolerance"])
            w.writerows(rows)
        if store:
            fig, axs = plt.subplots(1, 4, figsize=(15, 5.4), sharey=True)
            col = {"A": "#2f6db5", "B": "#e07b39"}
            for cfg, tab in store.items():
                st = [int(r["storey"]) for r in tab]
                for k, (cn, lab) in enumerate((("shear_X_kN", "Storey shear X (MN)"), ("shear_Y_kN", "Storey shear Y (MN)"),
                                               ("drift_max_X_pct", "Max storey drift X (%)"), ("drift_max_Y_pct", "Max storey drift Y (%)"))):
                    sc = 1e-3 if "shear" in cn else 1.0
                    os_ = [(_num(r[f"OpenSees_{cn}"]) or np.nan) * sc for r in tab]
                    et_ = [(_num(r[f"ETABS_{cn}"]) if _num(r[f"ETABS_{cn}"]) is not None else np.nan) * sc for r in tab]
                    axs[k].plot(os_, st, color=col[cfg], lw=2, label=f"{NAME[cfg]} - OpenSees")
                    axs[k].plot(et_, st, color=col[cfg], lw=0, marker="o", ms=4, label=f"{NAME[cfg]} - ETABS")
                    axs[k].set_xlabel(lab)
            axs[0].set_ylabel("Storey")
            axs[0].legend(fontsize=7)
            fig.suptitle(f"ETABS vs OpenSees, elastic response spectrum - {COND[cond]}", fontweight="bold")
            fig.tight_layout(rect=(0, 0, 1, 0.94))
            fig.savefig(os.path.join(OUTD, f"fig_etabs_vs_opensees_{cond}.png"), dpi=140)
            plt.close(fig)
        npass = sum(1 for r in rows if r[7] == "PASS")
        print(f"{cond}: {npass}/{len(rows)} quantities within tolerance -> output/ETABS_vs_OpenSees_{cond}.csv")
        for r in rows:
            if r[7] == "CHECK":
                print("   CHECK", r[0], r[1], r[2], "OpenSees", r[4], "ETABS", r[5], r[6], "%")
    # ---- pushover ---------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    have = False
    for k, dn in enumerate("XY"):
        for cfg, colr in (("A", "#2f6db5"), ("B", "#e07b39")):
            r = json.load(open(os.path.join(ROOT, "results/pushover", f"{cfg}-REF_dir{k + 1}.json")))
            from run_03_postprocess import po_curve
            c, _ = po_curve(r)
            axs[k].plot(c[:, 0] * C.H_TOTAL, (c[:, 1] + c[:, 2]) / 1e3, color=colr, lw=2, label=f"{NAME[cfg]} - OpenSees")
            fe = os.path.join(FILLED, f"ETABS_pushover_{cfg}_{dn}.csv")
            if os.path.exists(fe):
                d = [(_num(a["roof_displacement_m"]), _num(a["base_shear_kN"])) for a in csv.DictReader(open(fe))]
                d = [(a, b) for a, b in d if a is not None and b is not None]
                if d:
                    have = True
                    d = np.array(d)
                    axs[k].plot(np.abs(d[:, 0]), np.abs(d[:, 1]) / 1e3, color=colr, ls="--", marker="o", ms=3,
                                label=f"{NAME[cfg]} - ETABS")
        axs[k].set_xlabel(f"Roof displacement {dn} at plan centre (m)")
        axs[k].set_title(f"Pushover {dn}, original models")
        axs[k].grid(alpha=0.3)
    axs[0].set_ylabel("Base shear (MN)")
    axs[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTD, "fig_pushover_etabs_vs_opensees.png"), dpi=140)
    plt.close(fig)
    if not any_done and not have:
        print("No filled ETABS files found in", FILLED, "- copy the templates there and fill the ETABS columns.")


if __name__ == "__main__":
    if "--make-templates" in sys.argv:
        make_templates()
    else:
        compare()
