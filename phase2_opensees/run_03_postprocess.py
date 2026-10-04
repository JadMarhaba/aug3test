"""
STEP 3 (SHARED - compares Phase 2A as-built vs Phase 2B proposed) - tables and figures.

Reads every result in results/ and writes
    results/summary/*.csv         tables quoted in REPORT.md
    figures/fig02 ... fig10.png   figures quoted in REPORT.md
Colour code in every figure: as-built flat slab (2A) = blue, proposed beam-slab (2B) = orange.
"""
import glob
import itertools
import json
import os
from collections import Counter, defaultdict

import numpy as np

from sao import config as C
from sao import plotting as P
from sao.runner import REMOVAL_SCENARIOS, PUSHDOWN_SCENARIOS
import matplotlib.pyplot as plt

RES = "results"
OUT = "results/summary"
FIG = "figures"
os.makedirs(OUT, exist_ok=True)
DEFS = ("D1", "D2", "D3", "D4")
FRAME = {"A": "As-built flat slab (2A)", "B": "Proposed beam-slab (2B)"}
COLOR = {"A": P.FLAT, "B": P.BEAM}
KEY = ["REF", "D1", "D2", "D3", "D4", "D1D2D3D4"]
SEVERE = ("wall_shear_strength_loss", "wall_shear_failure", "wall_axial_failure", "punching", "column_axial_failure")


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, pattern))):
        try:
            out[os.path.basename(f)[:-5]] = json.load(open(f))
        except Exception as e:
            print("skip", f, e)
    return out


def variants(config):
    return [v.name for v in C.all_deficiency_variants(config)]


def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")


def first_event(events, kinds):
    for e in events:
        if e["kind"] in kinds:
            return e
    return None


def story_of(where):
    try:
        return int(where.split("-")[0][1:])
    except Exception:
        return None


# =========================================================================================
def nlth_summary(r):
    ev = r.get("events", [])
    cnt = Counter(e["kind"] for e in ev)
    env = r.get("env", {})
    col = r.get("collapse") or {}
    fw = first_event(ev, ("wall_shear_failure",))
    fa = first_event(ev, ("wall_axial_failure",))
    fp = first_event(ev, ("punching",))
    fc = first_event(ev, ("cb_failure",))
    dcr = r.get("pier_dcr", {})
    worst = max(dcr.items(), key=lambda kv: max(kv[1][0], kv[1][1])) if dcr else ("-", [0, 0, 0])
    status = r.get("status")
    if status == "collapse":
        outcome = f"COLLAPSE ({col.get('mode')})"
    elif status == "nonconverged":
        outcome = "NON-CONVERGED (instability)"
    else:
        outcome = "survived"
    lost_core = None
    if r.get("final_core") and r.get("gravity_core"):
        lost_core = 1 - r["final_core"][0] / max(r["gravity_core"][0], 1)
    return dict(
        status=status, outcome=outcome, collapse_mode=col.get("mode", ""), t_collapse=col.get("t", ""),
        t_end=r.get("t_end"), max_drift_corner=max(env.get("drift_corner", [0])),
        max_drift_cm=max(env.get("drift_cm", [0])), roof_rot=(env.get("roof") or [0, 0, 0])[2],
        n_cb_fail=cnt.get("cb_failure", 0), n_wall_shear=cnt.get("wall_shear_failure", 0),
        n_wall_axial=cnt.get("wall_axial_failure", 0), n_punch=cnt.get("punching", 0),
        n_col=cnt.get("column_axial_failure", 0),
        t_first_cb=fc["t"] if fc else "", t_first_wall_shear=fw["t"] if fw else "",
        first_wall_shear=fw["where"] if fw else "", t_first_wall_axial=fa["t"] if fa else "",
        first_wall_axial=fa["where"] if fa else "", t_first_punch=fp["t"] if fp else "",
        worst_wall=worst[0], worst_dcr=max(worst[1][0], worst[1][1]), core_gravity_lost=lost_core)


def table_matrix(nl):
    rows = []
    hdr = ["variant", "framing", "group", "D1", "D2", "D3", "D4", "outcome", "t_collapse_s", "max_drift_corner",
           "max_drift_cm", "roof_rotation_rad", "link_beams_failed", "wall_shear_failures", "wall_axial_failures",
           "punching_failures", "column_failures", "t_first_link_beam_fail", "t_first_wall_shear", "first_wall_shear",
           "t_first_wall_axial", "first_wall_axial", "t_first_punch", "worst_wall_pier", "worst_wall_shear_DCR"]
    summ = {}
    for cfg in "AB":
        for name in variants(cfg):
            r = nl.get(f"{name}_GM1_sf1.00")
            if not r:
                continue
            s = nlth_summary(r)
            summ[name] = s
            v = r["variant"]
            rows.append([name, FRAME[cfg], v["group"]] + [int(v[d]) for d in DEFS] +
                        [s["outcome"], s["t_collapse"], f"{s['max_drift_corner']:.4f}", f"{s['max_drift_cm']:.4f}",
                         f"{s['roof_rot']:.5f}", s["n_cb_fail"], s["n_wall_shear"], s["n_wall_axial"], s["n_punch"],
                         s["n_col"], s["t_first_cb"], s["t_first_wall_shear"], s["first_wall_shear"],
                         s["t_first_wall_axial"], s["first_wall_axial"], s["t_first_punch"], s["worst_wall"],
                         f"{s['worst_dcr']:.2f}"])
    write_csv("T1_deficiency_matrix_event_level_GM1.csv", hdr, rows)
    return summ


def factorial(summ, metric, cfg):
    """2^4 factorial effects on a response metric (log of peak drift, or collapse 0/1)."""
    data = {}
    for name, s in summ.items():
        if not name.startswith(cfg + "-"):
            continue
        defs = name.split("-")[1]
        key = tuple(int(d in defs) for d in DEFS)
        data[key] = metric(s)
    if len(data) < 16:
        return None
    eff = {}
    for k in range(1, 5):
        for combo in itertools.combinations(range(4), k):
            tot = 0.0
            for key, y in data.items():
                sign = np.prod([1 if key[i] else -1 for i in combo])
                tot += sign * y
            eff["x".join(DEFS[i] for i in combo)] = tot / 8.0
    return eff


# =========================================================================================
def fig_pushover(po):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    rows = []
    for d, ax in zip((1, 2), axs):
        for cfg in "AB":
            for name, ls, lw in ((f"{cfg}-REF", "--", 1.6), (f"{cfg}-D1D2D3D4", "-", 2.2)):
                r = po.get(f"{name}_dir{d}")
                if not r or not r.get("curve"):
                    continue
                c = np.array(r["curve"])
                W = r["weight_kN"]
                ax.plot(c[:, 0] * 100, (c[:, 1] + c[:, 2]) / W * 100, color=COLOR[cfg], ls=ls, lw=lw,
                        label=f"{FRAME[cfg].split(' (')[0]} - {'no deficiency' if 'REF' in name else 'all 4 deficiencies'}")
        ax.set_title(f"Pushover in {'X' if d == 1 else 'Y'} (first-mode-like load pattern)")
        ax.set_xlabel("Roof drift (%)")
        ax.axhline(0, color=P.MUTED, lw=0.8)
    axs[0].set_ylabel("Base shear / building weight (%)")
    axs[1].legend(fontsize=7.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig02_pushover_curves.png"))
    plt.close(fig)
    for key, r in po.items():
        c = np.array(r.get("curve") or [])
        if not len(c):
            continue
        W = r["weight_kN"]
        V = c[:, 1] + c[:, 2]
        i = int(np.argmax(V))
        ev = r.get("events", [])
        fcb = first_event(ev, ("cb_failure",))
        fws = first_event(ev, ("wall_shear_failure",))
        fpu = first_event(ev, ("punching",))
        fax = first_event(ev, ("wall_axial_failure",))
        drift_at = lambda e: f"{c[min(int(e['t']) - 1, len(c) - 1), 0] * 100:.2f}" if e else ""
        rows.append([key, r["variant"]["config"], f"{V[i] / 1e3:.1f}", f"{V[i] / W * 100:.2f}",
                     f"{c[i, 0] * 100:.2f}", f"{c[i, 1] / V[i] * 100:.0f}", drift_at(fcb), drift_at(fws),
                     drift_at(fax), drift_at(fpu), r["status"], f"{c[-1, 0] * 100:.2f}"])
    write_csv("T2_pushover_capacity.csv",
              ["run", "framing", "Vmax_MN", "Vmax_over_W_pct", "roof_drift_at_Vmax_pct", "core_share_at_Vmax_pct",
               "roof_drift_first_link_beam_failure_pct", "roof_drift_first_wall_shear_failure_pct",
               "roof_drift_first_wall_axial_failure_pct", "roof_drift_first_punching_pct", "status",
               "final_roof_drift_pct"], rows)


def fig_matrix(summ):
    names = [v.name.split("-")[1] for v in C.all_deficiency_variants("A")]
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    for j, cfg in enumerate("AB"):
        for i, n in enumerate(names):
            s = summ.get(f"{cfg}-{n}")
            if not s:
                continue
            d = s["max_drift_corner"] * 100
            col = "#e34948" if s["status"] in ("collapse", "nonconverged") else COLOR[cfg]
            mk = "X" if s["status"] in ("collapse", "nonconverged") else "o"
            ax.scatter(min(d, 10), i + (j - 0.5) * 0.3, s=60, color=col, marker=mk, edgecolor=P.SURFACE, lw=1.5,
                       zorder=3)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(["no deficiency" if n == "REF" else n.replace("D", " D").strip().replace(" ", "+")
                        for n in names])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("Peak storey drift at building corners (%) - log scale, capped at 10 %")
    ax.set_title("2025-event level (SF = 1, GM1): every deficiency combination")
    h = [plt.Line2D([], [], color=P.FLAT, marker="o", ls="", label="As-built flat slab (2A) - stood"),
         plt.Line2D([], [], color=P.BEAM, marker="o", ls="", label="Proposed beam-slab (2B) - stood"),
         plt.Line2D([], [], color="#e34948", marker="X", ls="", label="Collapse / instability (either framing)")]
    ax.legend(handles=h, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig03_deficiency_matrix_event_level.png"))
    plt.close(fig)


def fig_sequence(nl, keys, fname, title):
    kinds = {"cb_failure": ("Link-beam failure", P.SERIES[3], "s"),
             "wall_shear_failure": ("Wall shear failure", P.SERIES[4], "D"),
             "wall_axial_failure": ("Wall axial failure (removed)", "#e34948", "X"),
             "punching": ("Slab punching", P.SERIES[6], "v"),
             "column_axial_failure": ("Column crushing", P.SERIES[5], "P")}
    fig, axs = plt.subplots(1, len(keys), figsize=(5.2 * len(keys), 4.2), sharey=True, squeeze=False)
    for ax, key in zip(axs[0], keys):
        r = nl.get(key)
        if not r:
            continue
        for k, (lab, col, mk) in kinds.items():
            pts = [(e["t"], story_of(e["where"]) or 0) for e in r["events"] if e["kind"] == k]
            if pts:
                t, s = zip(*pts)
                ax.scatter(t, s, s=26, color=col, marker=mk, label=lab, edgecolor=P.SURFACE, lw=0.6, zorder=3)
        if r.get("collapse"):
            ax.axvline(r["collapse"]["t"], color=P.INK, lw=1.2, ls="--")
            ax.text(r["collapse"]["t"], 34, " collapse", fontsize=8, color=P.INK, va="bottom")
        cfg = r["variant"]["config"]
        ax.set_title(f"{FRAME[cfg]}\n{r['variant']['label']}, SF = {r['job']['sf']}", fontsize=9.5)
        ax.set_xlabel("Time (s)")
        ax.set_ylim(0, 36)
    axs[0][0].set_ylabel("Storey / floor level")
    hs, ls_ = [], []
    for ax in axs[0]:
        h, l = ax.get_legend_handles_labels()
        for hh, ll in zip(h, l):
            if ll not in ls_:
                hs.append(hh)
                ls_.append(ll)
    fig.legend(hs, ls_, loc="lower center", ncol=5, fontsize=8)
    fig.suptitle(title, fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(os.path.join(FIG, fname))
    plt.close(fig)


def fig_demand_profiles(nl, names, fname):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
    st = np.arange(1, C.N_STORY + 1)
    for k, name in enumerate(names):
        r = nl.get(f"{name}_GM1_sf1.00")
        if not r:
            continue
        cfg = r["variant"]["config"]
        dcr = r.get("pier_dcr", {})
        prof = np.zeros(C.N_STORY)
        for key, v in dcr.items():
            s = int(key.split("-")[0])
            prof[s - 1] = max(prof[s - 1], v[0], v[1])
        ls = "-" if "D1D2D3D4" in name else "--"
        axs[0].plot(prof, st, color=COLOR[cfg], ls=ls, label=r["variant"]["label"])
        dr = np.array(r["env"]["drift_corner"]) * 100
        axs[1].plot(dr, st, color=COLOR[cfg], ls=ls, label=r["variant"]["label"])
    axs[0].axvline(1.0, color=P.INK, lw=1, ls=":")
    axs[0].set_xlabel("Peak wall shear demand / capacity (max over piers)")
    axs[0].set_ylabel("Storey")
    axs[0].set_title("Where the core is loaded hardest")
    axs[1].set_xlabel("Peak storey drift at the corners (%)")
    axs[1].set_title("Drift profile")
    axs[1].legend(fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname))
    plt.close(fig)


def ida(nl):
    rows = []
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    out = {}
    for j, cfg in enumerate("AB"):
        ax = axs[j]
        for k, d in enumerate(KEY):
            name = f"{cfg}-{d}"
            pts = []
            for key, r in nl.items():
                if key.startswith(name + "_GM1_sf"):
                    sf = r["job"]["sf"]
                    s = nlth_summary(r)
                    coll = s["status"] in ("collapse", "nonconverged")
                    pts.append((sf, s["max_drift_corner"], coll))
            if not pts:
                continue
            pts.sort()
            sfs = [p[0] for p in pts]
            col_sf = min([p[0] for p in pts if p[2]], default=None)
            surv = max([p[0] for p in pts if not p[2]], default=None)
            out[name] = dict(collapse_sf=col_sf, max_survived_sf=surv)
            rows.append([name, " ".join(f"{p[0]}:{'C' if p[2] else round(p[1] * 100, 2)}" for p in pts),
                         col_sf if col_sf else f">{max(sfs)}", surv if surv else "-"])
            xs = [min(p[1] * 100, 10) for p in pts]
            ax.plot(xs, sfs, color=P.SERIES[k], lw=1.6, marker="o", ms=4,
                    label="no deficiency" if d == "REF" else ("all 4" if d == "D1D2D3D4" else d))
            for p in pts:
                if p[2]:
                    ax.scatter(10, p[0], marker="X", s=60, color=P.SERIES[k], zorder=4)
        ax.axhline(1.0, color=P.INK, lw=1, ls=":")
        ax.text(0.12, 1.02, "2025 event (SF = 1)", fontsize=8)
        ax.set_xscale("log")
        ax.set_xlim(0.1, 12)
        ax.set_xlabel("Peak storey drift (%)  [X at 10 % = collapse]")
        ax.set_title(FRAME[cfg])
        ax.legend(fontsize=7.5, title="deficiencies", title_fontsize=8)
    axs[0].set_ylabel("Scale factor on the 2025-event record (GM1)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig06_incremental_dynamic_analysis.png"))
    plt.close(fig)
    write_csv("T4_ida_collapse_intensity.csv", ["variant", "SF:peak_drift_% (C = collapse)", "collapse_SF",
                                                 "max_SF_survived"], rows)
    return out


def removal(rm):
    rows = []
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    scen = list(REMOVAL_SCENARIOS)
    redistribution = {}
    for j, cfg in enumerate("AB"):
        for name in (f"{cfg}-REF", f"{cfg}-D1D2D3D4"):
            for k, sc in enumerate(scen):
                r = rm.get(f"{name}_{sc}")
                if not r:
                    continue
                h = np.array(r.get("hist") or [[0, 0, 0, 0, 0]])
                removed = r["removed_load"]
                dcols = r["after_cols"][0] - r["before_cols"][0]
                dcore = r["after_core"][0] - (r["before_core"][0] - removed)
                ev = Counter(e["kind"] for e in r["events"])
                st = r["status"]
                redistribution[(name, sc)] = dict(status=st, removed=removed, to_cols=dcols, to_core=dcore,
                                                  vz=r["final_vz"])
                rows.append([name, sc, st, f"{removed / 1e3:.1f}", f"{dcols / 1e3:.1f}", f"{dcore / 1e3:.1f}",
                             f"{dcols / removed * 100:.0f}" if removed else "", f"{r['final_vz'] * 1000:.0f}",
                             r["final_where"], ev.get("punching", 0), ev.get("wall_axial_failure", 0),
                             ev.get("column_axial_failure", 0), ev.get("cb_failure", 0),
                             (r.get("collapse") or {}).get("t", "")])
                if "D1D2D3D4" in name:
                    axs[j].plot(h[:, 0], h[:, 1] * 1000, color=P.SERIES[k], lw=1.8, label=sc.replace("_", " "))
        axs[j].set_title(f"{FRAME[cfg]} - all 4 deficiencies")
        axs[j].set_xlabel("Time after sudden removal (s)")
        axs[j].axhline(600, color=P.INK, lw=1, ls=":")
        axs[j].text(0.05, 615, "collapse criterion (0.6 m)", fontsize=8)
    axs[0].set_ylabel("Extra vertical displacement of the core / floors (mm)")
    axs[1].legend(fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig07_core_removal_vertical_response.png"))
    plt.close(fig)
    write_csv("T3_core_removal_redistribution.csv",
              ["variant", "scenario", "outcome", "gravity_load_removed_MN", "extra_load_on_storey1_columns_MN",
               "extra_load_on_remaining_core_MN", "pct_of_removed_load_to_columns", "final_or_collapse_drop_mm",
               "where", "punching_failures", "wall_axial_failures", "column_failures", "link_beam_failures",
               "t_collapse_s"], rows)
    return redistribution


def pushdown(pdn):
    """Quasi-static withdrawal of one core pier: capacity and load paths."""
    rows = []
    scen = list(PUSHDOWN_SCENARIOS)
    labels = {"P1_F_story1": "front pier F, storey 1", "P2_M_story1": "middle pier M, storey 1",
              "P3_R_story1": "rear pier R, storey 1", "P4_F_1-4": "front pier F, storeys 1-4"}
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for j, d in enumerate(("REF", "D1D2D3D4")):
        ax = axs[j]
        for cfg in "AB":
            for k, sc in enumerate(scen):
                r = pdn.get(f"{cfg}-{d}_{sc}")
                if not r or not r.get("hist"):
                    continue
                h = np.array(r["hist"])
                if k in (0, 3):
                    ax.plot(h[:, 0] * 1000, h[:, 1], color=COLOR[cfg], lw=2.0 if k == 0 else 1.3,
                            ls="-" if k == 0 else "--",
                            label=f"{FRAME[cfg].split(' (')[0]}: {labels[sc]}")
        ax.axhline(1.0, color=P.INK, lw=1, ls=":")
        ax.text(2, 1.02, "lost pier's full gravity load", fontsize=8)
        ax.set_title("No deficiencies" if d == "REF" else "All four deficiencies")
        ax.set_xlabel("Drop of the core above the lost pier (mm)")
        ax.legend(fontsize=7)
    axs[0].set_ylabel("Fraction of the lost pier's load carried by the rest (lambda)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig08_pushdown_capacity.png"))
    plt.close(fig)
    # where does the load go?  stacked horizontal bars at the peak
    bars, ypos, y = [], [], 0.0
    for d in ("REF", "D1D2D3D4"):
        for sc in scen:
            for cfg in "AB":
                r = pdn.get(f"{cfg}-{d}_{sc}")
                if not r or not r.get("at_peak"):
                    continue
                pk, P0 = r["at_peak"], r["P_removed"]
                bars.append((f"{'2A flat slab' if cfg == 'A' else '2B beam-slab'} | {labels[sc]} | "
                             f"{'no deficiency' if d == 'REF' else 'all 4 deficiencies'}",
                             pk["via_link_beams"] / P0, pk["via_floor"] / P0, r["lambda_max"], cfg))
                ypos.append(y)
                y += 1.0
            y += 0.5
    fig, ax = plt.subplots(figsize=(9.5, 0.32 * len(bars) + 1.6))
    for (lab, a, b_, lam, cfg), yy in zip(bars, ypos):
        ax.barh(yy, a, color=P.SERIES[2], height=0.75, edgecolor=P.SURFACE, lw=2)
        ax.barh(yy, b_, left=a, color=COLOR[cfg], height=0.75, edgecolor=P.SURFACE, lw=2)
        ax.text(max(a + b_, a, 0) + 0.02, yy, f"{lam:.2f}", va="center", fontsize=8, color=P.INK2)
    ax.set_yticks(ypos)
    ax.set_yticklabels([b[0] for b in bars], fontsize=7.5)
    ax.invert_yaxis()
    ax.axvline(1.0, color=P.INK, lw=1, ls=":")
    ax.set_xlabel("Share of the lost pier's gravity load picked up at peak (number = lambda_max)")
    h = [plt.Rectangle((0, 0), 1, 1, color=P.SERIES[2]), plt.Rectangle((0, 0), 1, 1, color=P.FLAT),
         plt.Rectangle((0, 0), 1, 1, color=P.BEAM)]
    ax.legend(h, ["through link beams to the other core piers", "through the flat slab to the columns",
                  "through the beams to the columns"], fontsize=8, loc="lower right")
    ax.set_title("Load redistribution after losing one core pier (quasi-static pushdown)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig09_load_redistribution_paths.png"))
    plt.close(fig)
    for key, r in sorted(pdn.items()):
        pk, fu = r.get("at_peak") or {}, r.get("at_full") or {}
        ev = Counter(e["kind"] for e in r.get("events", []))
        P0 = r["P_removed"]
        rows.append([key, r["status"], f"{P0 / 1e3:.1f}", f"{r['lambda_max']:.3f}", f"{r['lambda_ps_max']:.3f}",
                     "yes" if r["lambda_max"] >= 1 else "no", "yes" if r["lambda_ps_max"] >= 1 else "no",
                     f"{pk.get('drop', 0) * 1000:.0f}", f"{pk.get('d_cols', 0) / 1e3:.1f}",
                     f"{pk.get('d_core_other', 0) / 1e3:.1f}", f"{pk.get('via_link_beams', 0) / 1e3:.1f}",
                     f"{pk.get('via_floor', 0) / 1e3:.1f}", f"{fu.get('drop', 0) * 1000:.0f}" if fu else "",
                     ev.get("punching", 0), ev.get("cb_failure", 0), ev.get("wall_axial_failure", 0),
                     ev.get("column_axial_failure", 0)])
    write_csv("T6_pushdown_redistribution.csv",
              ["run", "status", "lost_pier_load_MN", "lambda_max_static", "lambda_pseudostatic_dynamic",
               "carries_full_load_statically", "survives_sudden_loss", "drop_at_peak_mm",
               "extra_on_storey1_columns_MN", "extra_on_other_core_piers_MN", "via_link_beams_MN",
               "via_floor_framing_MN", "drop_when_full_load_carried_mm", "punching", "link_beam_failures",
               "wall_axial_failures", "column_failures"], rows)


def torsion(nl):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    for cfg in "AB":
        r = nl.get(f"{cfg}-D1D2D3D4_GM1_sf1.00")
        if not r or not r.get("hist"):
            continue
        h = np.array(r["hist"])
        axs[0].plot(h[:, 0], h[:, 3] * 1000, color=COLOR[cfg], lw=1.2, label=FRAME[cfg])
        e = r["env"]
        ratio = np.array(e["drift_corner"]) / np.maximum(np.array(e["drift_cm"]), 1e-9)
        axs[1].plot(ratio, np.arange(1, C.N_STORY + 1), color=COLOR[cfg], label=FRAME[cfg])
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Roof twist (mrad)")
    axs[0].set_title("Torsional response, all four deficiencies, SF = 1")
    axs[0].legend(fontsize=8)
    axs[1].set_xlabel("Peak corner drift / peak drift at the centre")
    axs[1].set_ylabel("Storey")
    axs[1].set_title("Torsional amplification of drift")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig10_torsion.png"))
    plt.close(fig)


def main():
    nl = load("nlth/*.json")
    po = load("pushover/*.json")
    rm = load("removal/*.json")
    print(f"{len(nl)} response histories, {len(po)} pushovers, {len(rm)} removal analyses")
    summ = table_matrix(nl)
    fig_matrix(summ)
    for cfg in "AB":
        for nm, met in (("log_drift", lambda s: np.log(min(max(s["max_drift_corner"], 1e-4), 0.1))),
                        ("collapse", lambda s: float(s["status"] in ("collapse", "nonconverged")))):
            eff = factorial(summ, met, cfg)
            if eff:
                write_csv(f"T5_factorial_effects_{cfg}_{nm}.csv", ["effect", "value"],
                          sorted(eff.items(), key=lambda kv: -abs(kv[1])))
    fig_pushover(po)
    fig_sequence(nl, ["A-D1D2D3D4_GM1_sf1.00", "B-D1D2D3D4_GM1_sf1.00"], "fig04_failure_sequence_event_level.png",
                 "Failure sequence at the 2025-event level, all four deficiencies")
    fig_demand_profiles(nl, ["A-REF", "A-D1D2D3D4", "B-REF", "B-D1D2D3D4"], "fig05_core_demand_profiles.png")
    ida(nl)
    removal(rm)
    pushdown(load("pushdown/*.json"))
    torsion(nl)


if __name__ == "__main__":
    main()
