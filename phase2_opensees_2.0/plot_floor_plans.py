"""
VERSION 2.0 (corner cantilevers, all beams moment-connected, 250 mm slab in both models).
BOTH MODELS - typical floor plans drawn directly from the OpenSees model data
(column nodes, core wall segments, link beams, slab strips / beams), so the sketch shows
exactly what is analysed.  Output: figures/fig00_floor_plans.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

from sao import config as C
from sao import plotting as P
from sao.building_common import CORNERS
from sao.capacities import pier_segments, core_points, COUPLING_BEAMS, CONN_POINTS, PIERS
from sao.design import load_design
from sao.registry import model_class
from sao.runner import variant_from_name

PIER_COL = {"R": "#7a5cc4", "M": "#2a9d8f", "F": "#d1495b"}
PIER_NAME = {"R": "R  rear pier (C)", "M": "M  middle pier (I)", "F": "F  front pier (C)"}


def end_xy(b, end, cp):
    kind, ref = end
    if kind == "corner":
        return CORNERS[ref]
    if kind == "col":
        c = b.cols[ref]
        return c["x"], c["y"]
    return cp[ref][0], cp[ref][1]


def draw(ax, cfg):
    b = model_class(cfg)(variant_from_name(f"{cfg}-REF"), load_design(), mode="elastic").build()
    cp = core_points()
    L = C.PLAN
    # slab: covers the whole 39 x 39 m plate to the corners (both models), shafts excluded
    ax.add_patch(Rectangle((0, 0), L, L, color="#e9eef3", lw=0, zorder=0))
    cc = C.CORE
    ax.add_patch(Rectangle((cc["x0"], cc["y0"]), cc["x1"] - cc["x0"], cc["y1"] - cc["y0"], color="white", lw=0, zorder=0))
    ax.add_patch(Rectangle((0, 0), L, L, fill=False, lw=1.2, ec=P.INK))
    for g in C.GRID:                                            # grid lines
        ax.plot([g, g], [-1.5, L + 1.5], color=P.MUTED, lw=0.5, ls=(0, (6, 4)), zorder=0)
        ax.plot([-1.5, L + 1.5], [g, g], color=P.MUTED, lw=0.5, ls=(0, (6, 4)), zorder=0)
    for k, g in enumerate(C.GRID):
        ax.text(g, L + 2.3, "ABCDEF"[k], ha="center", va="center", fontsize=8, color=P.MUTED)
        ax.text(-2.4, g, str(k + 1), ha="center", va="center", fontsize=8, color=P.MUTED)
    # floor framing: slab strips (A) or beams (B)
    for sg in b.segments:
        (xa, ya), (xb, yb) = end_xy(b, sg["a"], cp), end_xy(b, sg["b"], cp)
        if cfg == "A":
            w = min(sg["l2"], 3.0)           # drawn band ~ effective strip (capped for legibility)
            if sg["dir"] == "x":
                ax.add_patch(Rectangle((min(xa, xb), ya - w / 4), abs(xb - xa), w / 2, color="#9ec5e8",
                                       alpha=0.45, lw=0, zorder=1))
            else:
                ax.add_patch(Rectangle((xa - w / 4, min(ya, yb)), w / 2, abs(yb - ya), color="#9ec5e8",
                                       alpha=0.45, lw=0, zorder=1))
            ax.plot([xa, xb], [ya, yb], color="#4a8ac9", lw=0.8, zorder=2)
        else:
            ax.plot([xa, xb], [ya, yb], color="#b5179e" if sg.get("cantilever") else "#e07b39", lw=3.2,
                    solid_capstyle="butt", zorder=2)
    for (cx, cy) in CORNERS:                                  # free corner nodes
        ax.plot(cx, cy, "o", color="#b5179e" if cfg == "B" else "#4a8ac9", ms=4, zorder=8)
    # core walls
    for p in PIERS:
        t = b.pier_info[(1, p)]["t"]
        for s in pier_segments(p, t):
            (x0, y0), (x1, y1) = s["a"], s["b"]
            if s["dir"] == "x":
                ax.add_patch(Rectangle((min(x0, x1), y0 - t / 2), abs(x1 - x0), t, color=PIER_COL[p], zorder=4))
            else:
                ax.add_patch(Rectangle((x0 - t / 2, min(y0, y1)), t, abs(y1 - y0), color=PIER_COL[p], zorder=4))
    for p, (x, y) in {"R": (19.5, 37.6), "M": (19.5, 29.1), "F": (19.5, 23.4)}.items():
        ax.text(x, y, p, color=PIER_COL[p], fontsize=11, fontweight="bold", ha="center", va="center", zorder=6)
    # link (coupling) beams across the wall openings
    for a, c in COUPLING_BEAMS:
        (xa, ya), (xc, yc) = cp[a][:2], cp[c][:2]
        ax.plot([xa, xc], [ya, yc], color=P.INK, lw=4.0, zorder=5, solid_capstyle="butt")
        ax.plot([xa, xc], [ya, yc], color="#f2c14e", lw=2.0, zorder=5, solid_capstyle="butt")
    # columns (storey-1 size)
    shape, D = C.column_section(1)
    for c in b.cols:
        ax.add_patch(Rectangle((c["x"] - D / 2, c["y"] - D / 2), D, D, color=P.INK, zorder=6))
    # punching connections (flat slab only)
    if cfg == "A":
        for c in b.cols:
            ax.add_patch(Circle((c["x"], c["y"]), 1.35, fill=False, ec="#d1495b", lw=1.0, ls=(0, (2, 1.5)), zorder=7))
        for n in CONN_POINTS:
            x, y = cp[n][:2]
            ax.add_patch(Circle((x, y), 0.9, fill=False, ec="#d1495b", lw=1.0, ls=(0, (2, 1.5)), zorder=7))
    ax.set_xlim(-4, L + 4)
    ax.set_ylim(-4, L + 4)
    ax.set_aspect("equal")
    ax.set_xticks([0, 10, 20, 30, 39])
    ax.set_yticks([0, 10, 20, 30, 39])
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    if cfg == "A":
        ax.set_title(f"2A  As-built: {C.SLAB_T_FLAT * 1000:.0f} mm PT flat slab, no beams\n"
                     f"{len(b.segments)} slab strips/floor (incl. 8 corner cantilevers), {len(b.cols)} columns, "
                     f"{len(b.cols) + len(CONN_POINTS)} punching connections\nslab cantilevers to the 4 corners (no corner columns)", fontsize=9.5)
    else:
        nc = sum(1 for sg in b.segments if "core" in (sg["a"][0], sg["b"][0]))
        nk = sum(1 for sg in b.segments if sg.get("cantilever"))
        ax.set_title(f"2B  Proposed: {C.BEAM_B * 1000:.0f}x{C.BEAM_H * 1000:.0f} beams + "
                     f"{C.SLAB_T_BEAM * 1000:.0f} mm slab\n{len(b.segments)} beams/floor"
                     f"\n({len(b.segments) - nc - nk} column-column, {nc} column-core, {nk} corner cantilevers), "
                     f"{len(b.cols)} columns", fontsize=9.5)
    return b


OUT = 'figures/fig00_floor_plans.png'


def main():
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.9))
    draw(axs[0], "A")
    draw(axs[1], "B")
    h = [plt.Line2D([], [], color=P.INK, marker="s", ls="", ms=7, label="column (1400 mm sq., storey 1)"),
         plt.Line2D([], [], color="#4a8ac9", lw=4, alpha=0.6, label="flat-slab strip (effective width)"),
         plt.Line2D([], [], color="#d1495b", ls=(0, (2, 1.5)), marker="o", mfc="none", ms=9, lw=0,
                    label="punching connection (flat slab only)"),
         plt.Line2D([], [], color="#e07b39", lw=3.2, label="beam 500x800 (column-column and column-core, moment connected)"),
         plt.Line2D([], [], color="#b5179e", lw=3.2, label="cantilever beam 500x800 to the corner (5.5 m)"),
         plt.Line2D([], [], color="#e9eef3", lw=8, label="slab (to the corners in both models)"),
         plt.Line2D([], [], color="#f2c14e", lw=3, label="link (coupling) beam 250x500, 4 per floor")]
    h += [plt.Line2D([], [], color=PIER_COL[p], lw=6, label=f"core wall - {PIER_NAME[p]}") for p in PIERS]
    fig.legend(handles=h, loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.suptitle("Version 2.0 - typical floor plan as modelled (same grid, columns and core in both; "
                 "only the floor framing differs)", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0.13, 1, 0.96))
    fig.savefig(OUT, dpi=150)


if __name__ == "__main__":
    main()
