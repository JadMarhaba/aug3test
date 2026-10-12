"""
ETABS RESPONSE-SPECTRUM INPUTS FROM FIGURE 12 OF ORNTHAMMARATH ET AL. (2025)
===========================================================================
"Far-field ground motion characteristics of the Bangkok Basin, Thailand, in the 2025 Mw 7.7
Mandalay earthquake: initial insights", Bulletin of Earthquake Engineering,
doi 10.1007/s10518-025-02295-7, Fig. 12: elastic response spectra (5 % damping) of the
recorded stations together with the DPT 1301/1302 (2018) Bangkok DBE and MCE spectra.

The curves are digitised from the figure image (source/fig12_ornthammarath_2025.png) by
colour:
  * each panel is calibrated on its gridlines (T = 0..10 s, Sa = 0..0.3 g);
  * every pixel column is searched for the curve's colour;
  * the centre of the line is converted to (T, Sa).
Resolution: 1 px = 0.03 s and 0.0011 g, so values are good to about +/- 0.002-0.003 g.

Outputs (this folder):
  fig12_digitized_spectra.csv           all curves on one period grid
  etabs_functions/RS-2025-<STATION>.txt ETABS user-defined spectrum files (Period, Sa in g)
  etabs_functions/RS-DPT61-Z5-DBE.txt   DPT design spectrum as plotted in Fig. 12 (corner points)
  etabs_functions/RS-DPT61-Z5-MCE.txt
  fig_check_overlay.png                 digitised points drawn over the source figure
  fig_spectra.png                       the digitised spectra, one panel per station

Run:  python3 digitize_fig12.py
"""
import csv
import os

import numpy as np
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "fig12_ornthammarath_2025.png")
OUT_FN = os.path.join(HERE, "etabs_functions")

# panel calibration from the gridlines: (x at T = 0, x at T = 10 s, y at Sa = 0, y at Sa = 0.3 g)
CAL = {"TL": (106.5, 445.0, 380.5, 112.0), "TR": (530.0, 865.0, 379.5, 112.0),
       "BL": (114.5, 445.0, 710.5, 448.0), "BR": (524.0, 854.0, 710.5, 447.5)}

# name: (panel, line colour, highest Sa searched, last period of the curve)
CURVES = {
    "PWSA": ("TL", "red", 0.15, 10.0), "BKSI": ("TL", "green", 0.15, 10.0),
    "KMUA": ("TR", "blue", 0.15, 10.0), "KCBA": ("TR", "purple", 0.05, 10.0),
    "NGPA": ("TR", "magenta", 0.05, 10.0), "PTNA": ("BL", "blue", 0.15, 10.0),
    "BKKA": ("BR", "orange", 0.15, 10.0),
    "DBE": ("TL", "gray", 0.29, 6.0), "MCE": ("TL", "black", 0.299, 6.0),
}
BASIN = ["PWSA", "BKSI", "KMUA", "PTNA", "BKKA"]       # the five Bangkok-basin stations
OUTSIDE = ["KCBA", "NGPA"]                              # the two stations outside the basin
STATION_NOTE = {
    "PWSA": "Central Bangkok, deepest basin (700-900 m to bedrock); largest amplification, clear 3 s peak",
    "BKSI": "Central Bangkok, 7 km from PWSA, borehole station at 30 m depth; clear 3 s peak",
    "KMUA": "Southern Bangkok (530-560 m to bedrock); peak near 1.8 s and clear 3 s peak",
    "PTNA": "Northern Bangkok, basin edge (~600 m); nearest to Chatuchak; peak at 2 s, no 3 s peak",
    "BKKA": "Southeastern Bangkok (530-560 m); no 2 s amplification",
}

# ETABS period grid: dense where the stations have their peaks
GRID = np.round(np.concatenate([[0.0, 0.05], np.arange(0.1, 4.0001, 0.1), np.arange(4.2, 6.0001, 0.2),
                                np.arange(6.5, 10.0001, 0.5)]), 3)
DPT_CORNERS = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
DPT_EXT = [7.0, 8.0, 10.0]          # beyond 6 s (end of the plotted code curve): Sa ~ 1/T, ASSUMED


def masks(im):
    R, G, B = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    return {
        "red": (R > 190) & (G < 100) & (B < 100) & (R - G > 120),
        "green": (G > 160) & (R < 190) & (B < 130) & (G - B > 70) & (G - R > 20),
        "blue": (B > 140) & (R < 110) & (B - R > 70) & (G < 175),
        "purple": (R > 90) & (R < 175) & (G < 90) & (B > 110) & (B < 190) & (B - G > 50),
        "magenta": (R > 190) & (G < 110) & (B > 100) & (R - G > 110),
        "orange": (R > 200) & (G > 80) & (G < 175) & (B < 130) & (R - B > 110) & (G - B > 25),
        "gray": (abs(R - G) < 12) & (abs(G - B) < 12) & (R > 100) & (R < 185),
        "black": (R < 80) & (G < 80) & (B < 80),
    }


def trace(m, panel, sa_max, t_max):
    """(T, Sa) of the line centre in every pixel column; where a column holds several runs of
    the colour, the run nearest the previous point is kept (curves are continuous)."""
    x0, x10, y0, y3 = CAL[panel]
    ytop = int(np.ceil(y0 - (y0 - y3) * sa_max / 0.3))
    out = []
    for x in range(int(np.ceil(x0)) + 1, int(np.floor(x10))):
        T = (x - x0) / (x10 - x0) * 10.0
        if T > t_max:
            break
        ys = np.nonzero(m[ytop:int(y0), x])[0]
        if len(ys) == 0:
            continue                      # hidden under another curve: filled by interpolation
        groups = np.split(ys, np.nonzero(np.diff(ys) > 2)[0] + 1)
        cands = [ytop + g.mean() for g in groups]
        if out:
            prev_y = y0 - out[-1][1] / 0.3 * (y0 - y3)
            yc = min(cands, key=lambda c: abs(c - prev_y))
        else:
            yc = max(cands)
        out.append((T, (y0 - yc) / (y0 - y3) * 0.3))
    return np.array(out)


def resample(tr, grid, half=0.045):
    """Median of the traced points within +/- half (about 3 pixel columns) of each grid
    period; linear interpolation across gaps; the first traced value is held to T = 0."""
    vals = []
    for T in grid:
        w = tr[np.abs(tr[:, 0] - T) <= half, 1]
        if len(w):
            vals.append(float(np.median(w)))
        elif T < tr[0, 0]:
            vals.append(float(np.median(tr[:2, 1])))
        else:
            vals.append(float(np.interp(T, tr[:, 0], tr[:, 1])))
    return np.array(vals)


def first_segment(m, panel, lo, hi):
    """Sa at T = 0 of the code curves.  The 0 - 0.5 s segment is so steep that one pixel column
    spans 6-11 px of line, so the line centre is taken in the first four columns beside the
    axis (rows between Sa = lo and hi only), fitted with a straight line and evaluated on the
    axis (T = 0)."""
    x0, x10, y0, y3 = CAL[panel]
    r0, r1 = int(y0 - hi / 0.3 * (y0 - y3)), int(y0 - lo / 0.3 * (y0 - y3))
    X, Y = [], []
    for x in range(int(np.ceil(x0)), int(np.ceil(x0)) + 4):
        ys = np.nonzero(m[r0:r1, x])[0]
        if len(ys):
            # the anti-aliased edge of the MCE line reads as grey too: keep the lowest run
            g = np.split(ys, np.nonzero(np.diff(ys) > 2)[0] + 1)[-1]
            X.append(x)
            Y.append(r0 + g.mean())
    k, c = np.polyfit(X, Y, 1)
    return float((y0 - (k * x0 + c)) / (y0 - y3) * 0.3)


def dpt_corners(tr, sa0):
    """Corner values of the code spectrum (straight segments between 0, 0.5, 1, 2 ... 6 s)."""
    vals = {0.0: sa0}
    for T in DPT_CORNERS[1:]:
        w = tr[np.abs(tr[:, 0] - T) <= 0.06, 1]
        vals[T] = float(np.median(w))
    T = np.array(DPT_CORNERS + DPT_EXT)
    sa = np.array([vals[t] for t in DPT_CORNERS] + [vals[6.0] * 6.0 / t for t in DPT_EXT])
    return T, sa


def write_etabs(name, T, sa):
    with open(os.path.join(OUT_FN, name + ".txt"), "w") as f:
        for t, s in zip(T, sa):
            f.write(f"{t:.3f}\t{s:.4f}\n")


def main():
    os.makedirs(OUT_FN, exist_ok=True)
    im = np.array(Image.open(SRC).convert("RGB")).astype(int)
    mk = masks(im)
    tr = {k: trace(mk[c], p, smax, tmax) for k, (p, c, smax, tmax) in CURVES.items()}
    # PWSA is drawn under BKSI; past 8.9 s it is hidden completely and the two coincide
    hid = tr["BKSI"][tr["BKSI"][:, 0] > tr["PWSA"][-1, 0] + 0.03]
    tr["PWSA"] = np.vstack([tr["PWSA"], hid])

    st = {k: resample(tr[k], GRID) for k in BASIN + OUTSIDE}
    st["BASIN_MEAN"] = np.mean([st[k] for k in BASIN], axis=0)
    st["BASIN_MAX"] = np.max([st[k] for k in BASIN], axis=0)
    Td, dbe = dpt_corners(tr["DBE"], first_segment(mk["gray"], "TL", 0.05, 0.13))
    _, mce = dpt_corners(tr["MCE"], first_segment(mk["black"], "TL", 0.09, 0.20))
    dbe_g, mce_g = np.interp(GRID, Td, dbe), np.interp(GRID, Td, mce)

    with open(os.path.join(HERE, "fig12_digitized_spectra.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["T_s"] + [f"{k}_g" for k in BASIN + OUTSIDE] + ["basin_mean_g", "basin_max_g",
                                                                  "DPT_DBE_g", "DPT_MCE_g"])
        for i, T in enumerate(GRID):
            w.writerow([f"{T:.2f}"] + [f"{st[k][i]:.4f}" for k in BASIN + OUTSIDE + ["BASIN_MEAN", "BASIN_MAX"]]
                       + [f"{dbe_g[i]:.4f}", f"{mce_g[i]:.4f}"])
    for k in BASIN:
        write_etabs(f"RS-2025-{k}", GRID, st[k])
    write_etabs("RS-2025-BASIN-MEAN", GRID, st["BASIN_MEAN"])
    write_etabs("RS-DPT61-Z5-DBE", Td, dbe)
    write_etabs("RS-DPT61-Z5-MCE", Td, mce)

    # ---- check: digitised points drawn over the source figure --------------------------------
    pan = {k: v[0] for k, v in CURVES.items()}
    img = Image.open(SRC).convert("RGB")
    d = ImageDraw.Draw(img)
    for k in CURVES:
        x0, x10, y0, y3 = CAL[pan[k]]
        pts = [(T, s) for T, s in zip(GRID, st[k])] if k in st else list(zip(Td[:8], (dbe if k == "DBE" else mce)[:8]))
        for T, s in pts:
            x, y = x0 + T / 10 * (x10 - x0), y0 - s / 0.3 * (y0 - y3)
            d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(0, 0, 0))
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img.save(os.path.join(HERE, "fig_check_overlay.png"))

    # ---- digitised spectra, one panel per station -------------------------------------------
    INK, INK2, GRIDC, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    S1, S2 = "#2a78d6", "#eb6834"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURF,
                         "axes.facecolor": SURF})
    fig, axs = plt.subplots(2, 4, figsize=(15, 7.2), sharex=True, sharey=True)
    panels = [(k, [k]) for k in BASIN] + [("Outside the basin", OUTSIDE), ("Basin mean and max", None),
                                           ("DPT zone 5 DBE: Fig. 12 vs input sheet", "DPT")]
    sheet_T = [0, .05, .1, .15, .2, .267, .4, .6, .8, 1, 1.2, 1.333, 1.6, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10]
    sheet_S = [.06, .0769, .0938, .1106, .1275, .15, .15, .15, .15, .15, .15, .15, .125, .1, .08, .0667,
               .0571, .05, .04, .0333, .0286, .025, .016]
    for ax, (title, keys) in zip(axs.flat, panels):
        ax.grid(color=GRIDC, lw=0.6)
        ax.plot(Td[:8], dbe[:8], color="#9a9893", lw=1.6, label="DPT DBE (Fig. 12)")
        ax.plot(Td[:8], mce[:8], color=INK2, lw=1.2, ls=(0, (4, 2)), label="DPT MCE (Fig. 12)")
        if keys == "DPT":
            ax.plot(sheet_T, sheet_S, color=S2, lw=2, label="Function 1, input sheet")
            ax.plot(Td, dbe, color=S1, lw=2, label="DBE digitised (Fig. 12)")
        elif keys is None:
            ax.fill_between(GRID, np.min([st[k] for k in BASIN], axis=0), st["BASIN_MAX"], color=S1, alpha=0.15,
                            lw=0, label="range of 5 basin stations")
            ax.plot(GRID, st["BASIN_MEAN"], color=S1, lw=2, label="mean of 5 basin stations")
        else:
            for k, c in zip(keys, (S1, S2)):
                ax.plot(GRID, st[k], color=c, lw=2, label=k)
        ax.set_title(title, fontsize=10, color=INK, loc="left", fontweight="bold")
        h, l = ax.get_legend_handles_labels()
        if ax is not axs.flat[0]:               # the DPT lines are named once, in the first panel
            h, l = h[2:], l[2:]
        if len(h) > 1 or ax is axs.flat[0]:
            ax.legend(h, l, fontsize=7, frameon=False, loc="upper right")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 0.31)
    for ax in axs[1]:
        ax.set_xlabel("Period T (s)")
    for ax in axs[:, 0]:
        ax.set_ylabel("Sa (g), 5 % damping")
    fig.suptitle("Bangkok basin, 28 March 2025: spectra digitised from Ornthammarath et al. (2025) Fig. 12",
                 color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(HERE, "fig_spectra.png"), dpi=150)
    plt.close(fig)

    # ---- console summary -----------------------------------------------------------------------
    print("DPT corners  T:", Td.tolist())
    print("  DBE:", np.round(dbe, 4).tolist())
    print("  MCE:", np.round(mce, 4).tolist())
    for k in BASIN + OUTSIDE:
        i = int(np.argmax(st[k]))
        print(f"{k}: Sa(0) {st[k][0]:.3f} g, peak {st[k][i]:.3f} g at {GRID[i]:.2f} s")


if __name__ == "__main__":
    main()
