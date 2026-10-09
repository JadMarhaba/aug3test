"""
BOTH MODELS - explanation sheet: what the core "piers" R, M and F are, and what each
pier-loss (sudden removal) scenario S1-S7 takes away, with the version 2.0 outcome for each
framing.  Output: figures/fig00b_core_piers_and_removal_scenarios.png
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

from sao import config as C
from sao import plotting as P
from sao.capacities import pier_segments, core_points, COUPLING_BEAMS, PIERS
from plot_floor_plans import draw, PIER_COL

RES = "results/removal"
SCEN = [  # name, piers removed, storeys, plain-language label
    ("S1_F_story1", ["F"], "storey 1", "Front wall F lost\n(ground storey)"),
    ("S2_F_1-4", ["F"], "storeys 1-4", "Front wall F lost\n(storeys 1-4)"),
    ("S6_M_story1", ["M"], "storey 1", "Middle wall M lost\n(ground storey)"),
    ("S7_R_story1", ["R"], "storey 1", "Rear wall R lost\n(ground storey)"),
    ("S3_FM_1-4", ["F", "M"], "storeys 1-4", "Front F + middle M lost\n(storeys 1-4)"),
    ("S5_core_story1", ["R", "M", "F"], "storey 1", "Whole core lost\n(ground storey)"),
    ("S4_core_1-4", ["R", "M", "F"], "storeys 1-4", "Whole core lost\n(storeys 1-4)"),
]
T = 0.30


def core_walls(ax, removed=(), lw_scale=1.0, label=True):
    cc = C.CORE
    for p in PIERS:
        for s in pier_segments(p, T):
            (x0, y0), (x1, y1) = s["a"], s["b"]
            gone = p in removed
            kw = dict(color="#d9d9d9" if gone else PIER_COL[p], zorder=4)
            w = 0.55 * lw_scale
            if s["dir"] == "x":
                ax.add_patch(Rectangle((min(x0, x1), y0 - w / 2), abs(x1 - x0), w, **kw))
            else:
                ax.add_patch(Rectangle((x0 - w / 2, min(y0, y1)), w, abs(y1 - y0), **kw))
            if gone:
                ax.plot([x0, x1], [y0, y1], color="#d1495b", lw=1.6 * lw_scale, ls=(0, (2, 1.5)), zorder=5)
    cp = core_points()
    for a, c in COUPLING_BEAMS:
        (xa, ya), (xc, yc) = cp[a][:2], cp[c][:2]
        ax.plot([xa, xc], [ya, yc], color="#f2c14e", lw=3.5 * lw_scale, zorder=5, solid_capstyle="butt")
    if label:
        for p, (x, y) in {"R": (19.5, 37.0), "M": (19.5, 29.3), "F": (19.5, 23.5)}.items():
            ax.text(x, y, p, color="#9a9a9a" if p in removed else PIER_COL[p], fontsize=13 * lw_scale,
                    fontweight="bold", ha="center", va="center", zorder=6)


def outcome(variant, sc):
    f = os.path.join(RES, f"{variant}_{sc}.json")
    if not os.path.exists(f):
        return "?", P.MUTED
    r = json.load(open(f))
    if r["status"] == "stable":
        return f"stands ({r['final_vz'] * 1000:.0f} mm)", "#2a9d8f"
    return "COLLAPSES", "#d1495b"


def main():
    fig = plt.figure(figsize=(15, 14.5))
    gs = fig.add_gridspec(3, 7, height_ratios=[1.35, 0.85, 1.0], hspace=0.22, wspace=0.12)

    # ---- row 1: the two floor plans, full size -------------------------------------------
    for k, cfg in enumerate("AB"):
        ax = fig.add_subplot(gs[0, k * 3 + (0 if k == 0 else 1):k * 3 + 3 + (0 if k == 0 else 1)])
        draw(ax, cfg)
        ax.set_title(("2A  AS-BUILT: 250 mm flat slab, no beams" if cfg == "A"
                      else "2B  PROPOSED: 500x800 beams + 250 mm slab"), fontsize=10.5, fontweight="bold")
        ax.annotate("back face of building", xy=(19.5, 39.6), xytext=(19.5, 42.2), ha="center", fontsize=8,
                    color=P.MUTED, arrowprops=dict(arrowstyle="-", color=P.MUTED, lw=0.6))
        ax.set_ylim(-4, 44)

    # ---- row 2, left: zoomed core with explanation -------------------------------------------
    axz = fig.add_subplot(gs[1, 0:3])
    cc = C.CORE
    core_walls(axz, lw_scale=1.4)
    for (xa, ya, txt) in ((cc["x0"] - 0.3, 26.25, "opening 1.5 m\n+ link beam"), (cc["x0"] - 0.3, 34.75, "opening 1.5 m\n+ link beam")):
        axz.annotate(txt, xy=(xa, ya), xytext=(xa - 6.5, ya), fontsize=8, va="center", ha="center",
                     arrowprops=dict(arrowstyle="->", color=P.INK, lw=0.8))
    notes = {"R": "R = REAR wall: C-shape, forms the back\nface of the building. Carries 35-42 MN.",
             "M": "M = MIDDLE wall: I-shape, the cross wall\nthrough the core. Carries 53-62 MN.",
             "F": "F = FRONT wall: C-shape, faces into the\nfloor plate. Carries 53-63 MN (most loaded)."}
    for p, y in (("R", 37.5), ("M", 30.5), ("F", 23.0)):
        axz.text(cc["x1"] + 1.2, y, notes[p], fontsize=8.5, va="center", color=PIER_COL[p], fontweight="bold")
    axz.set_xlim(2, 46)
    axz.set_ylim(20.5, 40.5)
    axz.set_aspect("equal")
    axz.axis("off")
    axz.set_title("The core = 3 separate wall 'piers' joined by 4 link beams per floor", fontsize=10.5,
                  fontweight="bold")

    # ---- row 2, right: elevation (what 'storey 1' vs 'storeys 1-4' means) ---------------------
    axe = fig.add_subplot(gs[1, 4:7])
    H = [C.level_z(i) for i in range(0, 9)]
    for i in range(8):
        y0, y1 = H[i], H[i + 1]
        for x, p in ((0, "R"), (1.2, "M"), (2.4, "F")):
            gone1 = (i == 0 and p == "F")
            axe.add_patch(Rectangle((x, y0), 0.8, y1 - y0 - 0.15, color="#d9d9d9" if gone1 else PIER_COL[p],
                                    alpha=0.9, lw=0))
            if i == 0:
                axe.text(x + 0.4, -1.8, p, ha="center", fontsize=10, fontweight="bold", color=PIER_COL[p])
    axe.add_patch(Rectangle((2.4 - 0.08, H[0] - 0.08), 0.96, H[4] - H[0] + 0.0, fill=False, ec="#d1495b",
                            lw=1.3, ls=(0, (4, 2))))
    axe.text(3.45, (H[0] + H[1]) / 2, "'storey 1' scenario:\nthis one pier-storey removed",
             fontsize=8.5, va="center", color="#d1495b")
    axe.text(3.45, (H[2] + H[4]) / 2, "'storeys 1-4' scenario:\nthe pier removed over the\nbottom 4 storeys (dashed)",
             fontsize=8.5, va="center", color="#d1495b")
    axe.text(1.6, H[8] + 1.2, "... up to storey 33 (the rest of the core stays)", ha="center", fontsize=8,
             color=P.MUTED)
    axe.set_xlim(-0.6, 7.5)
    axe.set_ylim(-3, H[8] + 3)
    axe.axis("off")
    axe.set_title("Side view of the core (bottom 8 storeys)", fontsize=10.5, fontweight="bold")

    # ---- row 3: one mini-core per scenario with outcomes ---------------------------------------
    for j, (sc, rem, st, lab) in enumerate(SCEN):
        ax = fig.add_subplot(gs[2, j])
        core_walls(ax, removed=rem, lw_scale=0.6)
        ax.set_xlim(cc["x0"] - 1.5, cc["x1"] + 1.5)
        ax.set_ylim(cc["y0"] - 27.0, cc["y1"] + 1.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{sc.split('_')[0]}: {lab}", fontsize=8.2, fontweight="bold")
        y = cc["y0"] - 3.0
        for cfg, nm in (("A", "2A as-built"), ("B", "2B beam-slab")):
            for d, dl in (("REF", "no def."), ("D1D2D3D4", "all 4 def.")):
                txt, col = outcome(f"{cfg}-{d}", sc)
                ax.text(cc["x0"] - 1.3, y, f"{nm}, {dl}:", fontsize=7.0, va="center", color=P.INK)
                ax.text(cc["x0"] - 1.3, y - 2.2, txt, fontsize=7.6, va="center", color=col, fontweight="bold")
                y -= 6.0
    fig.text(0.5, 0.012, "Grey wall with red dashes = removed instantly under gravity, then the building is followed "
             "for 6 s.  'stands (x mm)' = settles x mm and stays up;  'COLLAPSES' = the core above the gap drops 0.6 m.",
             ha="center", fontsize=9, color=P.INK)
    fig.suptitle("Core wall piers and the pier-loss scenarios (version 2.0 results)", fontsize=13,
                 fontweight="bold", y=0.93)
    fig.savefig("figures/fig00b_core_piers_and_removal_scenarios.png", dpi=130, bbox_inches="tight")


if __name__ == "__main__":
    main()
