"""
STEP 1 (SHARED BY BOTH MODELS) - generate the ground motions -> motions/GM*.npz + figure.

Three bidirectional synthetic records (GM1, GM2, GM3) matched to the reconstructed 2025-event
spectrum in Bangkok.  Both the as-built (2A) and the proposed (2B) model are run with exactly
these records so the comparison is under identical loading.
"""
import json
import numpy as np
from sao.motions import synthesize, stats, DT
from sao.spectra import event_2025, dpt_dbe, dpt_mce
from sao import plotting as P
import matplotlib.pyplot as plt

SEEDS = {"GM1": (11, 12), "GM2": (21, 22), "GM3": (31, 32)}

if __name__ == "__main__":
    info = {}
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    Tp = np.logspace(-1.3, 1, 120)
    for k, (gm, (sx, sy)) in enumerate(SEEDS.items()):
        t, ax_, per, sax = synthesize(sx)
        _, ay_, _, say = synthesize(sy)
        np.savez(f"motions/{gm}.npz", t=t, ax=ax_, ay=ay_, dt=DT)
        info[gm] = {"X": stats(ax_, DT), "Y": stats(ay_, DT)}
        gmean = np.sqrt(sax * say)
        axs[0].plot(per, gmean, color=P.SERIES[2 + k], lw=1.4, label=f"{gm} (geomean X,Y)")
        if k == 0:
            axs[1].plot(t, ax_, color=P.SERIES[0], lw=0.6, label="GM1-X")
        print(gm, info[gm])
    axs[0].plot(Tp, event_2025(Tp), color=P.INK, lw=2.2, label="Target: 2025 event (SF = 1)")
    axs[0].plot(Tp, dpt_dbe(Tp), color=P.MUTED, lw=1.6, ls="--", label="DPT 1301/1302-61 DBE")
    axs[0].plot(Tp, dpt_mce(Tp), color=P.MUTED, lw=1.2, ls=":", label="DPT 1301/1302-61 MCE")
    axs[0].set_xscale("log")
    axs[0].set_xlabel("Period T (s)")
    axs[0].set_ylabel("Sa (g), 5 % damping")
    axs[0].set_title("Spectra of the synthetic records vs target")
    axs[0].legend(fontsize=8)
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Ground acceleration (g)")
    axs[1].set_title("GM1, X component")
    fig.tight_layout()
    fig.savefig("figures/fig01_ground_motions.png")
    json.dump(info, open("motions/motion_stats.json", "w"), indent=1)
