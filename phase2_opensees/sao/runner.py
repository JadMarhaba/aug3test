"""
SHARED - runs ONE analysis job in its own process and saves the result.

A job is a JSON dict, e.g.
    {"kind": "pushover", "variant": "A-D1D2D3D4", "dir": 2}
    {"kind": "nlth",     "variant": "B-REF", "gm": "GM1", "sf": 1.0}
    {"kind": "removal",  "variant": "A-D1D2D3D4", "scenario": "S4_core_1-4"}
Variant names: A-... = Phase 2A as-built flat slab, B-... = Phase 2B proposed beam-slab;
the letters after the dash list the documented deficiencies switched on (REF = none).

Usage:  python3 -m sao.runner '<job json>'
"""
import json
import os
import sys
import time
import traceback
import numpy as np

from . import config as C
from .design import load_design
from .analysis import Analyzer
from .capacities import PIERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

# Alternate-load-path scenarios: which core piers are removed suddenly under gravity
REMOVAL_SCENARIOS = {
    "S1_F_story1": [("pier", (1, "F"))],                                   # front pier, ground storey
    "S2_F_1-4": [("pier", (s, "F")) for s in range(1, 5)],                  # front pier, storeys 1-4
    "S3_FM_1-4": [("pier", (s, p)) for s in range(1, 5) for p in ("F", "M")],
    "S4_core_1-4": [("pier", (s, p)) for s in range(1, 5) for p in PIERS],  # whole core, storeys 1-4
    "S5_core_story1": [("pier", (1, p)) for p in PIERS],                   # whole core, ground storey
}
# Pushdown scenarios: one pier lost at a time (ground storey), and the front pier over storeys 1-4
PUSHDOWN_SCENARIOS = {
    "P1_F_story1": [("pier", (1, "F"))],
    "P2_M_story1": [("pier", (1, "M"))],
    "P3_R_story1": [("pier", (1, "R"))],
    "P4_F_1-4": [("pier", (s, "F")) for s in range(1, 5)],
}


def variant_from_name(name):
    cfg, defs = name.split("-", 1)
    sev = {}
    if "_" in defs:
        defs, extra = defs.split("_", 1)
        for tok in extra.split("_"):
            if tok.startswith("fc"):
                sev["fc_ratio"] = float(tok[2:])
            if tok.startswith("le"):
                sev["embed_ratio"] = float(tok[2:])
    flags = {d: (d in defs) for d in ("D1", "D2", "D3", "D4")}
    return C.Variant(config=cfg, **flags, **sev)


def job_id(job):
    k = job["kind"]
    if k == "pushover":
        return f"pushover/{job['variant']}_dir{job['dir']}"
    if k == "nlth":
        dt = job.get("dt", 0.025)
        suf = "" if abs(dt - 0.025) < 1e-9 else f"_dt{dt:g}"
        return f"nlth/{job['variant']}_{job['gm']}_sf{job['sf']:.2f}{suf}"
    if k == "removal":
        return f"removal/{job['variant']}_{job['scenario']}"
    if k == "pushdown":
        return f"pushdown/{job['variant']}_{job['scenario']}"
    if k == "modal":
        return f"modal/{job['variant']}"
    raise ValueError(k)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def run(job):
    jid = job_id(job)
    out_path = os.path.join(RES, jid + ".json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    v = variant_from_name(job["variant"])
    design = load_design(os.path.join(RES, "design.json"))
    logf = open(os.path.join(RES, jid + ".log"), "w")
    log = lambda *a: (logf.write(" ".join(str(x) for x in a) + "\n"), logf.flush())
    t0 = time.time()
    a = Analyzer(v, design, log=log)
    ok = a.gravity()
    res = dict(job=job, variant=v.to_dict(), model=a.b.MODEL_NAME, gravity_ok=ok == 0,
               weight_kN=a.b.total_weight)
    core0, cols0 = a.gravity_paths()
    res["gravity_core"], res["gravity_cols"] = core0.tolist(), cols0.tolist()
    res["pier_axial_ratio"] = {f"{k[0]}-{k[1]}": a.b.pier_info[k]["axial_ratio"] for k in a.b.pier_ele}
    if a.b.conn:
        res["vg_vc"] = {f"{k[0]}-{k[1][0]}{k[1][1]}": a.Vg0[k] / c["Vc"] for k, c in a.b.conn.items()}
    if job["kind"] == "modal":
        res["T"] = a.modal(12)
    elif job["kind"] == "pushover":
        r = a.pushover(direction=job["dir"], roof_drift=job.get("roof_drift", 0.025),
                       n_steps=job.get("n_steps", 250))
        res.update(r)
    elif job["kind"] == "nlth":
        gm = np.load(os.path.join(ROOT, "motions", job["gm"] + ".npz"))
        ax_, ay_ = gm["ax"], gm["ay"]
        if job.get("swap"):
            ax_, ay_ = ay_, ax_
        r = a.nlth(ax_, ay_, float(gm["dt"]), job["sf"], t_extra=job.get("t_extra", 5.0),
                   dt=job.get("dt", 0.025), max_wall=job.get("max_wall"))
        res.update(r)
        core1, cols1 = a.gravity_paths()
        res["final_core"], res["final_cols"] = core1.tolist(), cols1.tolist()
        res["pier_dcr"] = {f"{k[0]}-{k[1]}": v_ for k, v_ in a.pier_dcr.items()}
        res["cb_state"] = {f"{k[0]}-{k[1]}": v_ for k, v_ in a.cb_state.items()}
        res["conn_maxdrift"] = {f"{k[0]}-{k[1][0]}{k[1][1]}": v_ for k, v_ in a.conn_maxdrift.items()}
    elif job["kind"] == "pushdown":
        r = a.pushdown(PUSHDOWN_SCENARIOS[job["scenario"]])
        res.update(r)
    elif job["kind"] == "removal":
        r = a.sudden_removal(REMOVAL_SCENARIOS[job["scenario"]], t_total=job.get("t_total", 6.0),
                             dt=job.get("dt", 0.005))
        res.update(r)
        res["pier_state"] = {f"{k[0]}-{k[1]}": v_ for k, v_ in a.pier_state.items()}
    res["wall_clock_s"] = time.time() - t0
    with open(out_path, "w") as f:
        json.dump(_clean(res), f)
    logf.close()
    return res


if __name__ == "__main__":
    job = json.loads(sys.argv[1])
    try:
        r = run(job)
        print("DONE", job_id(job), r.get("status"), round(r["wall_clock_s"], 1))
    except Exception:
        traceback.print_exc()
        print("FAILED", job_id(job))
        sys.exit(1)
