"""
SHARED BY BOTH MODELS - nonlinear analyses and failure / collapse monitors (Phase 2A and 2B).

The same analyses are run on the as-built flat-slab model and on the proposed beam-slab model
so that the two are compared under identical loading (proposal Part 4):

    gravity()          gravity loads at the time of the event, records the initial load paths
    modal()            periods (for comparison with the Phase 1 ETABS models)
    pushover()         nonlinear static push in X or Y (capacity, failure sequence, core/frame share)
    nlth()             bidirectional nonlinear response-history analysis (ground motion records)
    sudden_removal()   alternate-load-path analysis: core piers removed instantly under gravity,
                       to measure how much load the rest of the structure can pick up

Failure modes simulated explicitly (element removal at the step the criterion is met):
  * punching of slab-column / slab-wall connections (flat slab only): drift-based criterion of
    ACI 318-19 18.14.5.1 (PT) using the *current* gravity shear ratio Vg/Vc (so load
    redistribution after earlier failures lowers the drift capacity of neighbours), or
    V >= Vc at any drift.  The connection keeps a post-punching (integrity / tendon) spring.
  * axial failure of core wall piers after shear failure (shear-strain limit that depends on
    axial-load ratio, ASCE 41-17 / Wallace et al.) or full-section crushing.
  * axial (crushing) failure of columns.
Coupling-beam anchorage failure, wall shear degradation, beam / slab hinging and concrete /
steel degradation are captured by the material models themselves.
"""
import math
import time
import json
import numpy as np
import openseespy.opensees as ops

from . import config as C
from .capacities import PIERS, punching_drift_capacity, wall_axial_failure_drift, wall_flexure_limits
from .registry import model_class

SIDESWAY_DRIFT = 0.10        # collapse if any storey drift > 10 %
VERT_COLLAPSE = 0.60         # m, additional vertical displacement of a floor = collapse


class Analyzer:
    def __init__(self, variant, design, log=None):
        self.v = variant
        # builds phase2A_asbuilt_flatslab_model (config 'A') or phase2B_proposed_beamslab_model ('B')
        self.b = model_class(variant.config)(variant, design, mode="nonlinear").build()
        self.log = log or (lambda *a: None)
        self.events = []
        self.removed = set()
        self.t = 0.0
        self.collapse = None
        self.n_fail = {"punch": 0, "wall_axial": 0, "column": 0}
        b = self.b
        self.h = {s: C.story_h(s) for s in range(1, C.N_STORY + 1)}
        self.xm, self.ym = C.PLAN / 2, C.PLAN / 2
        self.conn_maxdrift = {k: 0.0 for k in b.conn}
        self.cb_state = {k: 0 for k in b.cb_ele}
        self.pier_state = {k: 0 for k in b.pier_ele}
        self.pier_dcr = {}          # (storey, pier) -> [max Vx/Vn_x, max Vy/Vn_y, max P/(A fc)]
        self.pier_rot = {}          # (storey, pier) -> [max plastic rotation, limit a, limit b]
        self.uz0 = {}

    # ------------------------------------------------------------------------------------
    def _setup(self, static=True, tol=1e-5, it=40):
        ops.wipeAnalysis()
        ops.constraints("Transformation")        # enforces the rigid floor diaphragms
        ops.numberer("RCM")
        ops.system("Mumps")                       # sparse direct solver (fastest here)
        ops.test("NormDispIncr", tol, it, 0)
        ops.algorithm("KrylovNewton")

    def gravity(self, nsteps=10):
        b = self.b
        b.apply_gravity_pattern()
        self._setup()
        ops.integrator("LoadControl", 1.0 / nsteps)
        ops.analysis("Static")
        ok = ops.analyze(nsteps)
        if ok != 0:
            ops.algorithm("KrylovNewton")
            ok = ops.analyze(nsteps)
        ops.loadConst("-time", 0.0)
        self.grav_ok = ok == 0
        self.record_gravity_state()
        return ok

    def record_gravity_state(self):
        b = self.b
        self.P_col0 = {k: -ops.eleForce(t)[2] * -1 for k, t in b.col_ele.items()}   # compression +
        self.P_col0 = {k: ops.eleForce(t)[2] for k, t in b.col_ele.items()}
        self.P_pier0 = {k: ops.eleForce(t)[2] for k, t in b.pier_ele.items()}
        self.Vg0 = {}
        for k, c in b.conn.items():
            self.Vg0[k] = abs(ops.eleResponse(c["punch"], "basicForce")[0])
        self.Vg = dict(self.Vg0)
        for k, tg in b.pier_ele.items():
            info = b.pier_info[k]
            P = self.P_pier0[k]
            ar = max(P, 0.0) / (info["A"] * info["fc"] * C.MPA)
            info["axial_ratio"] = ar
            info["gamma_ax"] = self.v.gamma_axial or wall_axial_failure_drift(ar)
        self.uz0 = {n: ops.nodeDisp(n, 3) for n in list(b.P.values()) + list(b.Nc.values())}
        for n in b.Ns.values():
            self.uz0[n] = ops.nodeDisp(n, 3)

    def modal(self, n=6):
        self._setup()
        ops.integrator("LoadControl", 0.0)
        ops.analysis("Static")
        lam = ops.eigen(n)
        T = [2 * math.pi / math.sqrt(l) for l in lam]
        return T

    # ------------------------------------------------------------------------------------
    # kinematics helpers
    def floor_disp(self):
        """u, v, theta of every master (level 1..N)."""
        out = np.zeros((C.N_STORY + 1, 3))
        for i in range(1, C.N_STORY + 1):
            d = ops.nodeDisp(self.b.master[i])
            out[i] = (d[0], d[1], d[5])
        return out

    def drift_at(self, fd, x, y):
        """Storey drift ratios (vector norm) at plan location (x,y) for all storeys."""
        u = fd[:, 0] - fd[:, 2] * (y - self.ym)
        v = fd[:, 1] + fd[:, 2] * (x - self.xm)
        du = np.diff(u)
        dv = np.diff(v)
        h = np.array([self.h[s] for s in range(1, C.N_STORY + 1)])
        return np.sqrt(du ** 2 + dv ** 2) / h

    def corner_drifts(self, fd):
        best = np.zeros(C.N_STORY)
        for x, y in ((0, 0), (C.PLAN, 0), (0, C.PLAN), (C.PLAN, C.PLAN)):
            best = np.maximum(best, self.drift_at(fd, x, y))
        return best

    # ------------------------------------------------------------------------------------
    def _event(self, kind, where, **kw):
        e = dict(t=round(self.t, 4), kind=kind, where=where, **kw)
        self.events.append(e)
        self.log(f"  t={self.t:7.2f}  {kind:18s} {where} {kw if kw else ''}")

    def _remove(self, tag):
        """Remove a failed element from the model (it carries no more force from now on)."""
        if tag in self.removed:
            return
        ops.remove("element", tag)
        self.removed.add(tag)

    def _remove_pier(self, key):
        """Remove a failed wall pier-storey AND its own self-weight / mass (the wall debris no
        longer loads the floor-level core node it hung from)."""
        b = self.b
        tag = b.pier_ele[key]
        if tag in self.removed:
            return
        self._remove(tag)
        info = b.pier_info[key]
        self._cancel_pat = getattr(self, "_cancel_pat", 400) + 1
        ops.timeSeries("Constant", self._cancel_pat)
        ops.pattern("Plain", self._cancel_pat, self._cancel_pat)
        for n in info["nodes"]:
            if n in self.b.node_mass:
                ops.load(n, 0.0, 0.0, info["w_self"] / 2, 0.0, 0.0, 0.0)
                m = max(self.b.node_mass[n] - info["w_self"] / 2 / C.G, 1e-3)
                self.b.node_mass[n] = m
                ops.mass(n, m, m, m, 0.0, 0.0, 0.0)

    def _insane(self):
        """True if any column or wall section holds a physically impossible state (|axial strain|
        > 5 % or shear strain > 20 %).  Such states appear when an iteration that failed is
        followed by a 'converged' retry from the corrupted trial state; the step is then
        rejected instead of being treated as structural failure."""
        b = self.b
        for tag in b.col_ele.values():
            if tag in self.removed:
                continue
            for ip in (1, 6):
                if abs(ops.eleResponse(tag, "section", ip, "deformation")[0]) > 0.05:
                    return True
        for tag in b.pier_ele.values():
            if tag in self.removed:
                continue
            for ip in (1, 2, 3):
                d = ops.eleResponse(tag, "section", ip, "deformation")
                if abs(d[0]) > 0.05 or abs(d[4]) > 0.2 or abs(d[5]) > 0.2:
                    return True
        return False

    def _orphan(self, i, p):
        """True if the floor-level core node of pier p at level i has lost the wall both below
        and above it (a loose wall fragment, not a supported part of the core)."""
        b = self.b
        below = b.pier_ele.get((i, p))
        above = b.pier_ele.get((i + 1, p))
        return (below is None or below in self.removed) and (above is None or above in self.removed)

    def check(self, fd=None, full=True):
        """Evaluate failure criteria; remove failed elements.  Returns number of removals."""
        b = self.b
        nrem = 0
        if fd is None:
            fd = self.floor_disp()
        # --- punching (flat slab) --------------------------------------------------------
        if b.conn:
            cache = {}
            for k, c in b.conn.items():
                if c["failed"]:
                    continue
                i = c["level"]
                key = (c["x"], c["y"])
                if key not in cache:
                    cache[key] = self.drift_at(fd, c["x"], c["y"])
                dr = cache[key]
                d_here = max(dr[i - 1], dr[i] if i < C.N_STORY else 0.0)
                if d_here > self.conn_maxdrift[k]:
                    self.conn_maxdrift[k] = d_here
                if full:
                    self.Vg[k] = abs(ops.eleResponse(c["punch"], "basicForce")[0])
                ratio = self.Vg[k] / c["Vc"]
                cap = punching_drift_capacity(ratio)
                if self.conn_maxdrift[k] >= cap:
                    c["failed"] = True
                    self._remove(c["punch"])
                    self.n_fail["punch"] += 1
                    nrem += 1
                    self._event("punching", f"L{i}-{k[1][0]}{k[1][1]}", drift=round(self.conn_maxdrift[k], 4),
                                vg_vc=round(ratio, 3), conn=c["kind"])
        # --- wall piers ------------------------------------------------------------------
        for k, tag in b.pier_ele.items():
            if tag in self.removed:
                continue
            info = b.pier_info[k]
            emin = 0.0
            gam = 0.0
            for ip in (1, 2, 3):
                d = ops.eleResponse(tag, "section", ip, "deformation")
                emin = min(emin, d[0])
                gam = max(gam, abs(d[4]), abs(d[5]))
            # --- flexure-compression: plastic hinge rotation vs ASCE 41-13 Table 10-19 -------
            # curvature about local z = bending in X (depth lw_x), about local y = bending in Y
            if full:
                ey = C.FY_EXP / C.ES
                kp_x = kp_y = 0.0
                for ip in (1, 3):
                    d = ops.eleResponse(tag, "section", ip, "deformation")
                    kp_x = max(kp_x, abs(d[1]) - 2.0 * ey / info["lw_x"])
                    kp_y = max(kp_y, abs(d[2]) - 2.0 * ey / info["lw_y"])
                h = info["h"]
                th = max(kp_x * min(0.5 * info["lw_x"], h), kp_y * min(0.5 * info["lw_y"], h), 0.0)
                dcr = self.pier_dcr.get(k, [0.0, 0.0, 0.0])
                v_ratio = max(dcr[0] * info["Vn_x"] / info["Acv_x"], dcr[1] * info["Vn_y"] / info["Acv_y"]) \
                    / C.MPA / math.sqrt(info["fc"])
                rho_term = info["rho_v"] * C.FY_EXP / info["fc"]
                a_lim, b_lim = wall_flexure_limits(info["axial_ratio"] + rho_term, v_ratio, info["confined"])
                cur = self.pier_rot.setdefault(k, [0.0, a_lim, b_lim])
                cur[0], cur[1], cur[2] = max(cur[0], th), a_lim, b_lim
                if cur[0] >= a_lim and not info.get("flex_a"):
                    info["flex_a"] = True
                    self._event("wall_flexure_strength_loss", f"S{k[0]}-{k[1]}", rot=round(cur[0], 5),
                                a=round(a_lim, 4))
                if cur[0] >= b_lim:
                    self._remove_pier(k)
                    self.n_fail["wall_axial"] += 1
                    nrem += 1
                    self._event("wall_axial_failure", f"S{k[0]}-{k[1]}", rot=round(cur[0], 5), b=round(b_lim, 4),
                                cause="flexure-compression (ASCE 41 b)")
                    continue
            st = self.pier_state[k]
            gp = min(info["back_x"]["gd"], info["back_y"]["gd"])     # end of strength plateau
            g3 = min(info["back_x"]["g3"], info["back_y"]["g3"])     # residual reached
            if st < 1 and gam >= gp:
                self.pier_state[k] = 1
                self._event("wall_shear_strength_loss", f"S{k[0]}-{k[1]}", gamma=round(gam, 5))
            if st < 2 and gam >= g3:
                self.pier_state[k] = 2
                self._event("wall_shear_failure", f"S{k[0]}-{k[1]}", gamma=round(gam, 5))
            if gam >= info["gamma_ax"] or emin <= -0.006:
                self._remove_pier(k)
                self.n_fail["wall_axial"] += 1
                nrem += 1
                self._event("wall_axial_failure", f"S{k[0]}-{k[1]}", gamma=round(gam, 5), eps=round(emin, 5),
                            cause="shear" if gam >= info["gamma_ax"] else "crushing")
        # --- peak wall shear demand / capacity per pier-storey (for the demand profiles) ---
        if full:
            for k, tag in b.pier_ele.items():
                if tag in self.removed:
                    continue
                f = ops.eleResponse(tag, "section", 1, "force")     # [P, Mz, My, T, Vx, Vy]
                info = b.pier_info[k]
                cur = self.pier_dcr.setdefault(k, [0.0, 0.0, 0.0])
                cur[0] = max(cur[0], abs(f[4]) / info["Vn_x"])
                cur[1] = max(cur[1], abs(f[5]) / info["Vn_y"])
                cur[2] = max(cur[2], -f[0] / (info["A"] * info["fc"] * C.MPA))   # axial ratio
        # --- coupling beams (state only) -------------------------------------------------
        if full:
            for k, tag in b.cb_ele.items():
                if self.cb_state[k] >= 2:
                    continue
                cb = b.cb_info[k]
                rot = 0.0
                for ip in (1, 4):
                    try:
                        d = ops.eleResponse(tag, "section", ip, "deformation")
                        rot = max(rot, abs(d[2]) * cb["lp"])
                    except Exception:
                        pass
                th_y = cb["My"] / cb["EI"] * cb["lp"]
                if self.cb_state[k] < 1 and rot >= th_y:
                    self.cb_state[k] = 1
                    self._event("cb_yield", f"L{k[0]}-CB{k[1]}", rot=round(rot, 5))
                if rot >= th_y + cb["th_p"] + cb["th_pc"]:
                    self.cb_state[k] = 2
                    self._event("cb_failure", f"L{k[0]}-CB{k[1]}", rot=round(rot, 5))
        # --- columns ---------------------------------------------------------------------
        if full:
            for k, tag in b.col_ele.items():
                if tag in self.removed:
                    continue
                emin = 0.0
                for ip in (1, 6):
                    d = ops.eleResponse(tag, "section", ip, "deformation")
                    emin = min(emin, d[0])
                if emin <= -0.010:
                    self._remove(tag)
                    self.n_fail["column"] += 1
                    nrem += 1
                    self._event("column_axial_failure", f"S{k[0]}-C{k[1]}", eps=round(emin, 5))
        return nrem

    def vertical_state(self):
        """Max additional downward displacement of core piers / columns (m)."""
        b = self.b
        worst = 0.0
        where = None
        for (i, p), n in b.P.items():
            if i == 0 or self._orphan(i, p):
                continue
            dz = self.uz0.get(n, 0.0) - ops.nodeDisp(n, 3)
            if dz > worst:
                worst, where = dz, f"core-{p}-L{i}"
        for (i, c), n in b.Nc.items():
            if i == 0 or i % 4:
                continue
            dz = self.uz0.get(n, 0.0) - ops.nodeDisp(n, 3)
            if dz > worst:
                worst, where = dz, f"col{c}-L{i}"
        if b.Ns:
            for (i, c), n in b.Ns.items():
                if i % 4:
                    continue
                dz = self.uz0.get(n, 0.0) - ops.nodeDisp(n, 3)
                if dz > worst:
                    worst, where = dz, f"slab{c}-L{i}"
        return worst, where

    def collapse_check(self, fd):
        cd = self.corner_drifts(fd)
        if cd.max() > SIDESWAY_DRIFT:
            self.collapse = dict(t=self.t, mode="sidesway", story=int(np.argmax(cd)) + 1, drift=float(cd.max()))
            return True
        vz, where = self.vertical_state()
        if vz > VERT_COLLAPSE:
            self.collapse = dict(t=self.t, mode="vertical", where=where, dz=float(vz))
            return True
        return False

    # ------------------------------------------------------------------------------------
    def base_shears(self):
        b = self.b
        core = np.zeros(2)
        cols = np.zeros(2)
        for p in PIERS:
            tag = b.pier_ele[(1, p)]
            if tag in self.removed:
                continue
            f = ops.eleForce(tag)
            core += (f[0], f[1])
        for c in range(b.ncol):
            tag = b.col_ele[(1, c)]
            if tag in self.removed:
                continue
            f = ops.eleForce(tag)
            cols += (f[0], f[1])
        return -core, -cols

    def story_shears(self):
        """Core and column shear (global X,Y) per storey."""
        b = self.b
        out = np.zeros((C.N_STORY, 4))
        for s in range(1, C.N_STORY + 1):
            for p in PIERS:
                tag = b.pier_ele[(s, p)]
                if tag in self.removed:
                    continue
                f = ops.eleForce(tag)
                out[s - 1, 0] -= f[0]
                out[s - 1, 1] -= f[1]
            for c in range(b.ncol):
                tag = b.col_ele[(s, c)]
                if tag in self.removed:
                    continue
                f = ops.eleForce(tag)
                out[s - 1, 2] -= f[0]
                out[s - 1, 3] -= f[1]
        return out

    def gravity_paths(self):
        """Axial load carried by core piers and columns per storey (kN, compression +)."""
        b = self.b
        core = np.zeros(C.N_STORY)
        cols = np.zeros(C.N_STORY)
        for s in range(1, C.N_STORY + 1):
            for p in PIERS:
                tag = b.pier_ele[(s, p)]
                if tag not in self.removed:
                    core[s - 1] += ops.eleForce(tag)[2]
            for c in range(b.ncol):
                tag = b.col_ele[(s, c)]
                if tag not in self.removed:
                    cols[s - 1] += ops.eleForce(tag)[2]
        return core, cols

    def column_axial(self, stories=range(1, 6)):
        b = self.b
        out = {}
        for s in stories:
            for c in range(b.ncol):
                tag = b.col_ele[(s, c)]
                out[(s, c)] = 0.0 if tag in self.removed else ops.eleForce(tag)[2]
        return out

    # ------------------------------------------------------------------------------------
    def set_damping(self, T1, T2, zeta=None):
        zeta = zeta if zeta is not None else self.v.damping
        w1, w2 = 2 * math.pi / T1, 2 * math.pi / T2
        a0 = zeta * 2 * w1 * w2 / (w1 + w2)
        a1 = zeta * 2 / (w1 + w2)
        ops.rayleigh(a0, 0.0, 0.0, 0.0)
        eles = [e for e in self.b.all_frame_elements() if e not in self.removed]
        ops.region(1, "-ele", *eles, "-rayleigh", 0.0, 0.0, 0.0, a1)
        self.damp = (a0, a1)

    # ------------------------------------------------------------------------------------
    def _try_step(self, dt, mode="transient"):
        """Advance one time step.  Returns 0 on success, -1 if every fallback failed, -2 if a
        fallback 'converged' to a numerically corrupted state (see _insane)."""
        if ops.analyze(1, dt) == 0:
            return 0
        # if a step fails to converge: try other solution algorithms, then sub-step
        algos = [("Newton",), ("NewtonLineSearch", "-type", "Bisection"), ("ModifiedNewton", "-initial")]
        t0 = ops.getTime()
        for a in algos:
            ops.algorithm(*a)
            ok = ops.analyze(1, dt)
            ops.algorithm("KrylovNewton")
            if ok == 0:
                self.log(f"  t={t0:7.3f}  solver fallback: {a[0]}")
                return -2 if self._insane() else 0
        for nsub in (4, 16):
            okall = True
            for _ in range(nsub):
                ok = ops.analyze(1, dt / nsub)
                if ok != 0:
                    for a in algos:
                        ops.algorithm(*a)
                        ok = ops.analyze(1, dt / nsub)
                        ops.algorithm("KrylovNewton")
                        if ok == 0:
                            break
                if ok != 0:
                    okall = False
                    break
            if okall:
                self.log(f"  t={t0:7.3f}  solver fallback: {nsub} sub-steps")
                return -2 if self._insane() else 0
        return -1

    def nlth(self, acc_x, acc_y, dt_gm, sf, t_extra=5.0, dt=0.02, check_every=1, full_every=5,
             rec_every=0.2, max_wall=None):
        """Bidirectional nonlinear response-history analysis.  acc in g."""
        b = self.b
        T = self.modal(6)
        self.T = T
        self._setup(tol=1e-4, it=30)
        self.set_damping(T[0], max(T[0] / 8.0, 0.35))
        n = len(acc_x)
        ops.timeSeries("Path", 101, "-dt", dt_gm, "-values", *(np.asarray(acc_x) * sf * C.G))
        ops.timeSeries("Path", 102, "-dt", dt_gm, "-values", *(np.asarray(acc_y) * sf * C.G))
        ops.pattern("UniformExcitation", 101, 1, "-accel", 101)
        ops.pattern("UniformExcitation", 102, 2, "-accel", 102)
        ops.integrator("Newmark", 0.5, 0.25)
        ops.analysis("Transient")
        t_end = n * dt_gm + t_extra
        hist = []
        nstep = 0
        last_rec = -1e9
        env = dict(drift_cm=np.zeros(C.N_STORY), drift_corner=np.zeros(C.N_STORY),
                   roof=np.zeros(3), core_share_min=1.0)
        status = "completed"
        wall0 = time.time()
        self.t = 0.0
        while self.t < t_end - 1e-9:
            ok = self._try_step(dt)
            if ok != 0:
                status = "numerical" if ok == -2 else "nonconverged"
                break
            self.t = ops.getTime()
            nstep += 1
            fd = self.floor_disp()
            if nstep % check_every == 0:
                nrem = self.check(fd, full=(nstep % full_every == 0))
                if nrem:
                    self.set_damping(T[0], max(T[0] / 8.0, 0.35))
            cd = self.corner_drifts(fd)
            cm = self.drift_at(fd, self.xm, self.ym)
            env["drift_cm"] = np.maximum(env["drift_cm"], cm)
            env["drift_corner"] = np.maximum(env["drift_corner"], cd)
            env["roof"] = np.maximum(env["roof"], np.abs(fd[-1]))
            if self.t - last_rec >= rec_every - 1e-9:
                last_rec = self.t
                core, cols = self.base_shears()
                vz, _ = self.vertical_state()
                hist.append([self.t, fd[-1][0], fd[-1][1], fd[-1][2], core[0], core[1], cols[0], cols[1],
                             cd.max(), vz, self.n_fail["punch"], self.n_fail["wall_axial"], self.n_fail["column"],
                             sum(1 for s in self.cb_state.values() if s >= 2)])
            if int(self.t / 10.0) != int((self.t - dt) / 10.0):          # progress every 10 s
                self.log(f"  progress t={self.t:6.1f}s  max corner drift so far={env['drift_corner'].max():.4f}"
                         f"  wall clock={time.time() - wall0:.0f}s")
            if self.collapse_check(fd):
                status = "collapse"
                break
            if max_wall and time.time() - wall0 > max_wall:
                status = "timeout"
                break
        return dict(status=status, t_end=self.t, collapse=self.collapse, events=self.events,
                    n_fail=self.n_fail, T=T, hist=np.array(hist), env={k: (v.tolist() if hasattr(v, "tolist")
                                                                           else v) for k, v in env.items()},
                    wall_time=time.time() - wall0, nstep=nstep)

    # ------------------------------------------------------------------------------------
    def pushover(self, direction=1, roof_drift=0.03, n_steps=300, k_exp=2.0, sign=1.0):
        b = self.b
        H = C.H_TOTAL
        ops.timeSeries("Linear", 201)
        ops.pattern("Plain", 201, 201)
        Wl = {}
        for i in range(1, C.N_STORY + 1):
            z = C.level_z(i)
            Wl[i] = b.weight_by_level.get(round(z, 3), 0.0)
        den = sum(Wl[i] * C.level_z(i) ** k_exp for i in Wl)
        for i in range(1, C.N_STORY + 1):
            f = Wl[i] * C.level_z(i) ** k_exp / den
            load = [0.0] * 6
            load[direction - 1] = sign * f
            ops.load(b.master[i], *load)
        self._setup(tol=1e-5, it=50)
        dU = sign * roof_drift * H / n_steps
        ops.integrator("DisplacementControl", b.master[C.N_STORY], direction, dU)
        ops.analysis("Static")
        curve = []
        status = "completed"
        for k in range(n_steps):
            ok = ops.analyze(1)
            if ok != 0:
                for a in (("KrylovNewton",), ("NewtonLineSearch",), ("ModifiedNewton", "-initial")):
                    ops.algorithm(*a)
                    ok = ops.analyze(1)
                    if ok == 0:
                        ops.algorithm("KrylovNewton")
                        break
            if ok != 0:
                ops.integrator("DisplacementControl", b.master[C.N_STORY], direction, dU / 10)
                for _ in range(10):
                    ok = ops.analyze(1)
                    if ok != 0:
                        break
                ops.integrator("DisplacementControl", b.master[C.N_STORY], direction, dU)
                if ok == 0 and self._insane():
                    ok = -2
            if ok != 0:
                status = "numerical" if ok == -2 else "nonconverged"
                break
            self.t = k + 1
            fd = self.floor_disp()
            self.check(fd, full=True)
            core, cols = self.base_shears()
            cd = self.corner_drifts(fd)
            vz, _ = self.vertical_state()
            roof = fd[-1][direction - 1]
            curve.append([roof / H, core[direction - 1], cols[direction - 1], fd[-1][2], cd.max(), vz,
                          self.n_fail["punch"], self.n_fail["wall_axial"], self.n_fail["column"],
                          sum(1 for s in self.cb_state.values() if s >= 2)])
            if self.collapse_check(fd):
                status = "collapse"
                break
        return dict(status=status, curve=np.array(curve), events=self.events, collapse=self.collapse)

    # ------------------------------------------------------------------------------------
    def sudden_removal(self, targets, t_total=6.0, dt=0.005, zeta=0.05):
        """Alternate-load-path analysis: remove core piers / columns instantaneously under
        gravity and follow the dynamic response (no ground motion)."""
        b = self.b
        T = self.modal(6)
        self._setup(tol=1e-5, it=40)
        before_core, before_cols = self.gravity_paths()
        colP0 = self.column_axial(range(1, C.N_STORY + 1))
        # gravity load carried by the removed members (lowest removed storey of each pier)
        lowest = {}
        for kind, key in targets:
            if kind == "pier":
                s, p = key
                if p not in lowest or s < lowest[p]:
                    lowest[p] = s
        removed_load = sum(ops.eleForce(b.pier_ele[(s, p)])[2] for p, s in lowest.items())
        for kind, key in targets:
            if kind == "pier":
                self._remove_pier(key)
            else:
                self._remove(b.col_ele[key])
            self._event("removed", f"{kind}-{key}")
        self.set_damping(T[0], 0.3, zeta)
        ops.integrator("Newmark", 0.5, 0.25)
        ops.analysis("Transient")
        hist = []
        status = "stable"
        self.t = 0.0
        nstep = 0
        while self.t < t_total - 1e-9:
            ok = self._try_step(dt)
            if ok != 0:
                status = "numerical" if ok == -2 else "nonconverged"
                break
            nstep += 1
            self.t = ops.getTime()
            fd = self.floor_disp()
            self.check(fd, full=(nstep % 4 == 0))
            if nstep % 10 == 0:
                vz, where = self.vertical_state()
                hist.append([self.t, vz, self.n_fail["punch"], self.n_fail["wall_axial"], self.n_fail["column"]])
            if self.collapse_check(fd):
                status = "collapse"
                break
        after_core, after_cols = self.gravity_paths()
        colP1 = self.column_axial(range(1, C.N_STORY + 1))
        vz, where = self.vertical_state()
        return dict(status=status, collapse=self.collapse, events=self.events, hist=np.array(hist),
                    removed_load=removed_load, before_core=before_core.tolist(), before_cols=before_cols.tolist(),
                    after_core=after_core.tolist(), after_cols=after_cols.tolist(),
                    colP0={f"{k[0]}-{k[1]}": v for k, v in colP0.items()},
                    colP1={f"{k[0]}-{k[1]}": v for k, v in colP1.items()},
                    final_vz=vz, final_where=where, n_fail=self.n_fail, t_end=self.t)

    # ------------------------------------------------------------------------------------
    def _support_forces(self, pier):
        """Vertical force (kN, + = upward on the pier) delivered to a core pier by the members
        attached to its wall points, per floor: link beams vs floor framing (beams in the
        beam-slab model, slab connections in the flat-slab model)."""
        b = self.b
        names = [n for n, (x, y, p) in b.cpts.items() if p == pier]
        cb_tot = np.zeros(C.N_STORY + 1)
        fl_tot = np.zeros(C.N_STORY + 1)
        from .capacities import COUPLING_BEAMS
        for i in range(1, C.N_STORY + 1):
            wn = {b.W[(i, n)] for n in names}
            for k, (a, c) in enumerate(COUPLING_BEAMS):
                tag = b.cb_ele[(i, k)]
                f = ops.eleForce(tag)
                if b.W[(i, a)] in wn:
                    cb_tot[i] -= f[2]
                if b.W[(i, c)] in wn:
                    cb_tot[i] -= f[8]
            if b.conn:
                for n in names:
                    key = (i, ("core", n))
                    if key in b.conn:
                        c = b.conn[key]
                        for t in (c["punch"], c["pp"]):
                            if t is not None and t not in self.removed:
                                # zeroLength i = wall node, j = slab node: + force (tension)
                                # pulls the wall node up, i.e. the slab supports the pier
                                fl_tot[i] += ops.eleResponse(t, "basicForce")[0]
            else:
                for (lev, sid), tag in b.floor_ele.items():
                    if lev != i:
                        continue
                    sg = b.segments[sid]
                    for end, off in ((sg["a"], 2), (sg["b"], 8)):
                        if end[0] == "core" and end[1] in names:
                            fl_tot[i] -= ops.eleForce(tag)[off]
        return cb_tot, fl_tot

    def pushdown(self, targets, max_drop=0.40, step=-0.001):
        """Quasi-static alternate-load-path ("pushdown") analysis.

        The target pier-storeys are replaced by the forces they carried; those forces are then
        withdrawn gradually (load factor lambda 0 -> 1) under displacement control of the
        pier node above the gap.  lambda at the peak = fraction of the lost member's load that
        the rest of the structure can redistribute.  Returns lambda history, lambda_max and the
        redistribution of the withdrawn load into columns / remaining core / link beams / floor
        framing at the peak.
        """
        b = self.b
        piers = sorted({key[1] for kind, key in targets})
        top_story = {p: max(k[0] for kind, k in targets if k[1] == p) for p in piers}
        R = {}
        for kind, key in targets:
            tag = b.pier_ele[key]
            f = np.array(ops.eleForce(tag))
            ni, nj = b.pier_info[key]["nodes"]
            R[ni] = R.get(ni, np.zeros(6)) + f[:6]
            R[nj] = R.get(nj, np.zeros(6)) + f[6:]
        P_removed = sum(-ops.eleForce(b.pier_ele[(min(k[0] for kind, k in targets if k[1] == p), p)])[8]
                        for p in piers)
        core0, cols0 = self.gravity_paths()
        sup0 = {p: self._support_forces(p) for p in piers}
        colP0 = self.column_axial(range(1, 2))
        for kind, key in targets:
            self._remove(b.pier_ele[key])
            self._event("removed", f"pier-{key}")
        fixed = {n for (i, p), n in b.P.items() if i == 0}
        # eleForce = element resisting force (R); the support the element gave its nodes is -R.
        # Pattern 501 (constant) puts that support back as external load, pattern 502 (linear,
        # factor lambda) withdraws it: net support = (1 - lambda) x original.
        ops.timeSeries("Linear", 501)
        ops.pattern("Plain", 501, 501)
        for n, f in R.items():
            if n not in fixed:
                ops.load(n, *(-f).tolist())
        self._setup(tol=1e-5, it=50)
        ops.integrator("LoadControl", 1.0)
        ops.analysis("Static")
        ops.analyze(1)                       # replacement forces in place: same state as before
        ops.loadConst("-time", 0.0)          # freeze them (and gravity) as constant loads
        ops.timeSeries("Linear", 502)
        ops.pattern("Plain", 502, 502)
        for n, f in R.items():
            if n not in fixed:
                ops.load(n, *f.tolist())
        # control node: a wall attachment point of the lost pier (rigidly tied to the pier, and
        # not a diaphragm slave - displacement control on a constrained slave node is unreliable)
        wname = [n for n, (x, y, p) in b.cpts.items() if p == piers[0]][0]
        ctrl = b.W[(top_story[piers[0]], wname)]
        self._setup(tol=1e-5, it=50)
        ops.integrator("DisplacementControl", ctrl, 3, step)
        ops.analysis("Static")
        hist = []
        status = "completed"
        best = (-1.0, None)
        at_full = None
        uz_ref = ops.nodeDisp(ctrl, 3)
        k = 0
        def robust_step():
            """One displacement increment; on failure try other algorithms, then split the
            increment into 4 and 16 sub-steps with a relaxed tolerance."""
            if ops.analyze(1) == 0:
                return 0
            for a in (("Newton",), ("NewtonLineSearch",), ("ModifiedNewton", "-initial")):
                ops.algorithm(*a)
                if ops.analyze(1) == 0:
                    ops.algorithm("KrylovNewton")
                    return -1 if self._insane() else 0
            ops.algorithm("KrylovNewton")
            for nsub, tol in ((4, 1e-5), (16, 1e-4)):
                ops.test("NormDispIncr", tol, 100, 0)
                ops.integrator("DisplacementControl", ctrl, 3, step / nsub)
                good = True
                for _ in range(nsub):
                    ok_ = ops.analyze(1)
                    if ok_ != 0:
                        for a in (("Newton",), ("NewtonLineSearch",), ("ModifiedNewton", "-initial")):
                            ops.algorithm(*a)
                            ok_ = ops.analyze(1)
                            if ok_ == 0:
                                break
                        ops.algorithm("KrylovNewton")
                    if ok_ != 0:
                        good = False
                        break
                ops.integrator("DisplacementControl", ctrl, 3, step)
                ops.test("NormDispIncr", 1e-5, 50, 0)
                if good:
                    return -1 if self._insane() else 0
            return -1

        while True:
            ok = robust_step()
            if ok != 0:
                status = "nonconverged"
                break
            k += 1
            self.t = k
            lam = ops.getLoadFactor(502)
            drop = uz_ref - ops.nodeDisp(ctrl, 3)
            nrem = self.check(self.floor_disp(), full=True)
            hist.append([drop, lam, self.n_fail["punch"], self.n_fail["wall_axial"], self.n_fail["column"],
                         sum(1 for s_ in self.cb_state.values() if s_ >= 2)])
            def snapshot():
                core1, cols1 = self.gravity_paths()
                sup1 = {p: self._support_forces(p) for p in piers}
                colP1 = self.column_axial(range(1, 2))
                return dict(lam=lam, drop=drop, d_cols=float(cols1[0] - cols0[0]),
                            d_core_other=float(core1[0] - (core0[0] - P_removed)),
                            via_link_beams=float(sum((sup1[p][0] - sup0[p][0]).sum() for p in piers)),
                            via_floor=float(sum((sup1[p][1] - sup0[p][1]).sum() for p in piers)),
                            d_colP={f"{kk[0]}-{kk[1]}": colP1[kk] - colP0[kk] for kk in colP1},
                            events_so_far=len(self.events))
            if lam > best[0]:
                best = (lam, snapshot())
            if at_full is None and lam >= 1.0:
                at_full = snapshot()          # the lost load fully carried by the rest
            if drop >= max_drop:
                status = "max_drop"
                break
            if len(hist) > 30 and lam < 0.5 * best[0]:
                status = "unloading"
                break
        hist = np.array(hist)
        # energy-based pseudo-static capacity (Izzuddin et al. 2008): the structure survives the
        # SUDDEN loss of the member if the pseudo-static curve reaches lambda = 1
        lam_ps = np.zeros(len(hist))
        if len(hist) > 1:
            u = hist[:, 0]
            area = np.concatenate([[0.0], np.cumsum(0.5 * (hist[1:, 1] + hist[:-1, 1]) * np.diff(u))])
            area += 0.5 * hist[0, 1] * u[0]
            lam_ps = area / np.maximum(u, 1e-9)
        return dict(status=status, lambda_max=best[0], at_peak=best[1], at_full=at_full, P_removed=P_removed,
                    lambda_ps_max=float(lam_ps.max()) if len(lam_ps) else 0.0, lambda_ps=lam_ps,
                    hist=hist, events=self.events, n_fail=self.n_fail)
