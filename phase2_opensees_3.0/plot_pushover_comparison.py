"""
BOTH MODELS - pushover comparison of the ORIGINAL (no-deficiency) as-built flat slab and
proposed beam-slab, version 1 (../phase2_opensees, 300 mm flat slab) and version 2.0 (this
folder), X and Y, with the first occurrence of each kind of damage marked on the curves.
Output: figures/fig13_pushover_original_models.png and results/summary/E3_pushover_original_models.csv
"""
import csv
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sao import plotting as P
from run_03_postprocess import po_curve, first_event

RUNS = {"v2.0": "results/pushover", "v1": "../phase2_opensees/results/pushover"}
COL = {"A": P.FLAT, "B": P.BEAM}
NAME = {"A": "As-built flat slab", "B": "Proposed beam-slab"}
MARK = [("cb_yield", "o", "first link-beam yield"), ("cb_failure", "s", "first link-beam failure"),
        ("punching", "X", "first punching (flat slab)"),
        ("wall_shear_strength_loss", "D", "first wall shear strength loss"),
        ("wall_axial_failure", "*", "first core-pier axial failure"),
        ("column_axial_failure", "P", "first column failure")]


def main():
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.4), sharey=True)
    rows = []
    for k, (d, dn) in enumerate(((1, "X"), (2, "Y"))):
        ax = axs[k]
        for ver, path in RUNS.items():
            for cfg in "AB":
                f = os.path.join(path, f"{cfg}-REF_dir{d}.json")
                if not os.path.exists(f):
                    continue
                r = json.load(open(f))
                c, cut = po_curve(r)
                cf = np.array(r["curve"])
                W = r["weight_kN"]
                x, y = c[:, 0] * 100, (c[:, 1] + c[:, 2]) / W * 100
                ls, lw = ("-", 2.2) if ver == "v2.0" else ((0, (4, 2)), 1.4)
                ax.plot(x, y, color=COL[cfg], ls=ls, lw=lw, label=f"{NAME[cfg]} ({ver})")
                ev = r.get("events", [])
                marks = {}
                for kind, m, lab in MARK:
                    e = first_event(ev, (kind,))
                    if e:
                        i = min(int(e["t"]) - 1, len(cf) - 1)
                        marks[kind] = cf[i, 0] * 100
                        if i < len(c):
                            ax.plot(cf[i, 0] * 100, (cf[i, 1] + cf[i, 2]) / W * 100, m, color=COL[cfg],
                                    ms=8 if m == "*" else 6, mec="white", mew=0.7, zorder=5)
                i0 = max(1, int(0.1 * np.argmax(y > 0.5 * y.max()))) if y.max() > 0 else 1
                K0 = (y[i0] - y[0]) / max(x[i0] - x[0], 1e-9)
                ip = int(np.argmax(y))
                rows.append([ver, cfg, dn, f"{W / 1e3:.0f}", f"{y.max():.2f}", f"{(c[ip, 1] + c[ip, 2]) / 1e3:.1f}",
                             f"{x[ip]:.2f}", f"{c[ip, 1] / (c[ip, 1] + c[ip, 2]) * 100:.0f}", f"{K0:.1f}",
                             f"{x[-1]:.2f}", "core pier axial failure" if cut else r["status"]]
                            + [f"{marks[k]:.2f}" if k in marks else "" for k, _, _ in MARK])
        ax.set_title(f"Pushover in {dn} - original models (no deficiencies)", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Roof drift (%)")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("Base shear / building weight (%)")
    h, l = axs[0].get_legend_handles_labels()
    h += [plt.Line2D([], [], color=P.INK, marker=m, ls="", ms=7, label=lab) for _, m, lab in MARK]
    fig.legend(handles=h, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig("figures/fig13_pushover_original_models.png", dpi=140)
    with open("results/summary/E3_pushover_original_models.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["version", "framing", "direction", "weight_MN", "Vmax_over_W_pct", "Vmax_MN",
                    "roof_drift_at_Vmax_pct", "core_share_at_Vmax_pct", "initial_slope_pctW_per_pct_drift",
                    "end_roof_drift_pct", "end"] + [f"roof_drift_{k}_pct" for k, _, _ in MARK])
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
