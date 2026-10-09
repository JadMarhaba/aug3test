"""
SHARED - adaptive collapse-intensity search (a "hunt-and-fill" incremental dynamic analysis).

For one variant and one record, the scale factor SF on the 2025-event record is raised
0.5 -> 1.0 -> 1.5 -> 2.0 -> 3.0 -> 4.5 -> 6.0 -> 8.0 (v3.0) until the model collapses, then the bracket between
the highest SF it survived and the lowest SF at which it collapsed is bisected until it is
within 20 %.  The result is the collapse intensity of that variant (SF_collapse), i.e. how
many times the reconstructed 2025 Bangkok shaking the building could take.

Many searches run at once (one OpenSees process per analysis); static jobs (pushovers,
core-removal cases) fill idle workers.
"""
import json
import os
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait

from .runner import job_id, RES, ROOT

LADDER = [0.5, 1.0, 1.5, 2.0, 3.0, 4.5, 6.0, 8.0]   # v3.0: starts below the 2025 level
REL_TOL = 0.20
COLLAPSED = ("collapse", "nonconverged")   # non-convergence = dynamic instability
SEVERE = ("wall_axial_failure", "wall_shear_failure", "wall_shear_strength_loss", "punching",
          "column_axial_failure")


def classify(r):
    """Status used by the collapse search.  A run that stopped converging while nothing had
    failed (no wall, column or punching failure) and the drift was still below 3 % is a
    numerical stop, not dynamic instability: it is treated as 'numerical' and repeated at
    dt = 0.01 s, like any other numerical stop."""
    st = r.get("status")
    if st == "nonconverged" and "env" in r:
        severe = any(e.get("kind") in SEVERE for e in r.get("events", []))
        if not severe and max(r["env"]["drift_corner"]) < 0.03:
            return "numerical"
    return st


def result(job):
    p = os.path.join(RES, job_id(job) + ".json")
    if not os.path.exists(p):
        lg = os.path.join(RES, job_id(job) + ".log")
        if os.path.exists(lg) and time.time() - os.path.getmtime(lg) < 300:
            return "running"          # being run by another process (e.g. before a restart)
        return None
    with open(p) as f:
        r = json.load(f)
    return r.get("status")


class Hunt:
    def __init__(self, variant, gm, dt=0.025):
        self.variant, self.gm, self.dt = variant, gm, dt
        self.busy = False

    def job(self, sf, dt=None):
        return {"kind": "nlth", "variant": self.variant, "gm": self.gm, "sf": round(sf, 2),
                "dt": dt or self.dt}

    def _results(self):
        """sf -> {dt: status} for every finished analysis of this variant / record."""
        import re
        out = {}
        d = os.path.join(RES, "nlth")
        if not os.path.isdir(d):
            return out
        pat = re.compile(rf"^{re.escape(self.variant)}_{self.gm}_sf([0-9.]+?)(?:_dt([0-9.]+))?\.json$")
        for f in os.listdir(d):
            m = pat.match(f)
            if not m:
                continue
            sf = float(m.group(1))
            dt = float(m.group(2)) if m.group(2) else 0.025
            out.setdefault(sf, {})[dt] = classify(json.load(open(os.path.join(d, f))))
        return out

    def known(self):
        """SF -> collapsed?  A run that stopped for numerical reasons is repeated with
        dt = 0.01 s; if the repeat also fails to finish, it counts as collapse."""
        out = {}
        for sf, runs in self._results().items():
            st = runs.get(0.01, runs.get(0.025))
            if st in ("numerical", "crashed") and 0.01 not in runs:
                continue                     # pending re-run
            out[sf] = st in COLLAPSED or st in ("numerical", "crashed")
        return out

    def next_job(self):
        for sf, runs in self._results().items():
            if runs.get(0.025) in ("numerical", "crashed") and 0.01 not in runs:
                return self.job(sf, dt=0.01)
        sf = self.next_sf()
        return None if sf is None else self.job(sf)

    def next_sf(self):
        k = self.known()
        coll = [s for s, c in k.items() if c]
        surv = [s for s, c in k.items() if not c]
        if not k:
            return LADDER[0]
        if not coll:
            hi = max(surv)
            nxt = [s for s in LADDER if s > hi + 1e-9]
            return nxt[0] if nxt else None                  # survived the top of the ladder
        c = min(coll)
        s = max([x for x in surv if x < c], default=None)
        if s is None:
            return round(c / 2, 2) if c > 0.3 else None      # collapsed already at the lowest
        if (c - s) / c <= REL_TOL:
            return None
        return round(round((c + s) / 2 / 0.05) * 0.05, 2)

    def summary(self):
        k = self.known()
        coll = [s for s, c in k.items() if c]
        surv = [s for s, c in k.items() if not c]
        return dict(variant=self.variant, gm=self.gm, runs=sorted(k.items()),
                    sf_collapse=min(coll) if coll else None, sf_survived=max(surv) if surv else None)


def _mark_crashed(job, why):
    """The OpenSees process died without saving a result (e.g. a memory error inside OpenSees
    after the solver failed).  Record it as 'crashed' so the job is not repeated forever; for
    the collapse search it is treated like 'numerical' (repeat at dt = 0.01, and a repeat
    that also cannot finish counts as collapse)."""
    path = os.path.join(RES, job_id(job) + ".json")
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"job": job, "status": "crashed", "note": why[-500:]}, f)


def _run(job, timeout=5 * 3600):
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-m", "sao.runner", json.dumps(job)], cwd=ROOT,
                           capture_output=True, text=True, timeout=timeout)
        tail = (p.stdout.strip().splitlines() or ["?"])[-1]
        if p.returncode != 0:
            tail += " | " + " ".join(p.stderr.strip().splitlines()[-3:])
            _mark_crashed(job, tail)
    except subprocess.TimeoutExpired:
        tail = "TIMEOUT " + job_id(job)
    print(f"[{time.strftime('%H:%M:%S')}] {tail}  ({time.time() - t0:.0f}s)", flush=True)


def run_all(hunts, static_jobs=(), workers=4, priority_jobs=(), static_slots=0):
    """priority_jobs run before any collapse-search step; static_jobs fill idle workers.
    static_slots workers are kept for static jobs while any are left, so they are not
    starved until every collapse search has finished."""
    prio = [j for j in priority_jobs if result(j) is None]
    static = [j for j in static_jobs if result(j) is None]
    print(f"{len(prio)} priority jobs, {len(hunts)} collapse searches, {len(static)} other jobs, "
          f"{workers} workers", flush=True)
    lock = threading.Lock()
    running = {}
    with ThreadPoolExecutor(workers) as ex:
        while True:
            with lock:
                while len(running) < workers and prio:
                    j = prio.pop(0)
                    if result(j) is None:
                        running[ex.submit(_run, j)] = None
                # fill free workers: searches next (in priority order), then static jobs
                n_hunt = sum(1 for v in running.values() if v is not None)
                cap = workers - (min(static_slots, workers - 1) if static else 0)
                for h in hunts:
                    if len(running) >= workers or n_hunt >= cap:
                        break
                    if h.busy:
                        continue
                    j = h.next_job()
                    if j is None:
                        continue
                    if result(j) is not None:
                        continue
                    h.busy = True
                    running[ex.submit(_run, j)] = h
                    n_hunt += 1
                while len(running) < workers and static:
                    j = static.pop(0)
                    running[ex.submit(_run, j)] = None
            if not running:
                external = any(result(h.next_job()) == "running" for h in hunts if h.next_job())
                if external:
                    time.sleep(30)                # wait for jobs started by an earlier scheduler
                    continue
                break
            done, _ = wait(list(running), return_when=FIRST_COMPLETED, timeout=60)
            if not done:
                continue
            with lock:
                for f in done:
                    h = running.pop(f)
                    if h is not None:
                        h.busy = False
    out = [h.summary() for h in hunts]
    with open(os.path.join(RES, "collapse_search_summary.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out
