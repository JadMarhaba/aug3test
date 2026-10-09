"""
SHARED - figure style for all Phase 2 plots (validated categorical palette, fixed order).

Colour follows the entity everywhere:
    as-built flat slab (2A) = blue, proposed beam-slab (2B) = orange,
    then aqua, yellow, magenta, green, violet, red for further series.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
FLAT, BEAM = SERIES[0], SERIES[1]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"


def style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.0,
        "font.size": 9.5, "axes.titlesize": 10.5, "axes.titleweight": "bold", "legend.frameon": False,
        "axes.prop_cycle": matplotlib.cycler(color=SERIES), "figure.dpi": 130,
    })


style()
