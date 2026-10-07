"""
SHARED BY BOTH MODELS - design basis (reinforcement) for the nonlinear models.

The nonlinear models need reinforcement quantities that are not publicly available.  They are
generated here from an elastic (cracked) model and a response-spectrum analysis (RSA) to the
reconstructed DPT 1301/1302-61 Bangkok design spectrum:

* compliant design   : ACI 318-19 / DPT special-wall rules - wall shear amplified by
                       Omega_v * omega_v (= 1.5 x 1.8 = 2.7, ACI 18.10.3.1; equivalent in intent
                       to the DPT modified RSA for higher modes) and confined boundary zones.
* non-compliant (D4) : same RSA but shear designed for the unamplified RSA demand and no
                       boundary-zone confinement ("resisting less than legally required").

Walls are designed for the original 300 mm thickness; when D3 applies, the same steel area per
metre is kept in the 250 mm wall (the designer's "added reinforcement").

This is a design pass only (needed to define the Phase 2 models), not a Phase 1 deliverable.
"""
import json
import math
import os
import numpy as np
import openseespy.opensees as ops

from . import config as C
from .capacities import PIERS, pier_props, COUPLING_BEAMS
from .spectra import dpt_dbe

R_FACTOR = 5.0          # building-frame / dual system with RC shear walls (DPT, ASCE 7 basis)
IMPORTANCE = 1.25       # government office building
PHI_V = 0.75
OMEGA_V_OMEGA_V = 2.7   # ACI 318-19 18.10.3.1 (1.5 x 1.8)
WALL_ZONES = ("Z1", "Z2", "Z3", "Z4")


def wall_zone(story):
    if story <= 8:
        return "Z1"
    if story <= 16:
        return "Z2"
    if story <= 24:
        return "Z3"
    return "Z4"


beam_zone = wall_zone


def placeholder_design():
    walls = {k: {p: {z: dict(rho_v=0.0025, rho_h=0.0025) for z in WALL_ZONES} for p in PIERS}
             for k in ("compliant", "noncompliant")}
    return dict(walls=walls, wall_zone=wall_zone, beam_zone=beam_zone,
                cb_As={z: 1257.0 for z in WALL_ZONES},
                beam_As={z: {"perim": (4000.0, 2500.0), "int": (4000.0, 2500.0)} for z in WALL_ZONES})


def load_design(path=None):
    path = path or os.path.join(os.path.dirname(__file__), "..", "results", "design.json")
    with open(path) as f:
        d = json.load(f)
    d["wall_zone"] = wall_zone
    d["beam_zone"] = beam_zone
    d["cb_As"] = {k: float(v) for k, v in d["cb_As"].items()}
    d["beam_As"] = {z: {k: tuple(v) for k, v in d["beam_As"][z].items()} for z in d["beam_As"]}
    return d


# ----------------------------------------------------------------------------------------
def cqc(modal, omegas, zeta=0.05):
    """modal: array (nmodes, ...) ; returns CQC combination (abs)."""
    modal = np.asarray(modal)
    n = modal.shape[0]
    rho = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            r = omegas[j] / omegas[i]
            rho[i, j] = 8 * zeta ** 2 * (1 + r) * r ** 1.5 / ((1 - r * r) ** 2 + 4 * zeta ** 2 * r * (1 + r) ** 2)
    flat = modal.reshape(n, -1)
    out = np.sqrt(np.abs(np.einsum("ik,ij,jk->k", flat, rho, flat)))
    return out.reshape(modal.shape[1:])


def _setup_static():
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-8, 20)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")


def elastic_run(variant, design, n_modes=40):
    """Build the elastic model, run gravity and RSA; return demands."""
    from .registry import model_class
    SAOBuilding = model_class(variant.config)
    # ---- gravity -------------------------------------------------------------------------
    b = SAOBuilding(variant, design, mode="elastic").build()
    b.apply_gravity_pattern()
    _setup_static()
    ops.analyze(1)
    grav = {}
    for (s, p), tag in b.pier_ele.items():
        f = ops.eleForce(tag)
        grav[("pier", s, p)] = np.array(f[:6])
    for key, tag in b.floor_ele.items():
        grav[("floor",) + key] = np.array(ops.eleResponse(tag, "localForce"))
    W = b.total_weight
    # ---- modal + RSA ---------------------------------------------------------------------
    b = SAOBuilding(variant, design, mode="elastic").build()
    _setup_static()
    lam = np.array(ops.eigen(n_modes))
    omegas = np.sqrt(lam)
    T = 2 * np.pi / omegas
    ops.modalProperties("-unorm")
    Tn = np.concatenate([[0.0], np.logspace(-2, 1.3, 200)])
    Sa = dpt_dbe(Tn) * C.G * IMPORTANCE / R_FACTOR
    ops.timeSeries("Path", 50, "-time", *Tn, "-values", *Sa)
    res = {}
    for d in (1, 2):
        modal = {"pier": [], "cb": [], "floor": [], "base": [], "roof": []}
        for m in range(1, n_modes + 1):
            ops.responseSpectrumAnalysis(50, d, "-mode", m)
            modal["pier"].append([ops.eleForce(b.pier_ele[(s, p)])[:6] for s in range(1, C.N_STORY + 1)
                                  for p in PIERS])
            modal["cb"].append([ops.eleResponse(b.cb_ele[(i, k)], "localForce") for i in range(1, C.N_STORY + 1)
                                for k in range(len(COUPLING_BEAMS))])
            if variant.config == "B":
                modal["floor"].append([ops.eleResponse(b.floor_ele[key], "localForce") for key in sorted(b.floor_ele)])
            vb = 0.0
            for c in range(b.ncol):
                vb += ops.eleForce(b.col_ele[(1, c)])[d - 1]
            for p in PIERS:
                vb += ops.eleForce(b.pier_ele[(1, p)])[d - 1]
            modal["base"].append(vb)
            modal["roof"].append(ops.nodeDisp(b.master[C.N_STORY])[:3])
        res[d] = {k: cqc(np.array(v), omegas) for k, v in modal.items() if len(v)}
    keys_floor = sorted(b.floor_ele)
    return dict(b=b, T=T, W=W, grav=grav, rsa=res, keys_floor=keys_floor, omegas=omegas)


# ----------------------------------------------------------------------------------------
def pier_moment_capacity(p, t, fc, rho_v, P, axis, sign, fy=C.FY_NOM):
    """Nominal moment (kN m) of a thin-walled pier at axial load P (kN, compression +),
    rectangular stress block; axis 'x' = X-direction bending (moment about global Y)."""
    pp = pier_props(p, t)
    pts = []
    for s in pp["segs"]:
        n = max(4, int(s["L"] / 0.1))
        for k in range(n):
            f = (k + 0.5) / n
            x = s["a"][0] + f * (s["b"][0] - s["a"][0])
            y = s["a"][1] + f * (s["b"][1] - s["a"][1])
            pts.append((x - pp["xc"], y - pp["yc"], s["L"] * t / n))
    pts = np.array(pts)
    u = sign * (pts[:, 0] if axis == "x" else pts[:, 1])
    A = pts[:, 2]
    As = rho_v * A
    umax = u.max()
    beta1 = max(0.65, 0.85 - 0.05 * (fc - 28) / 7)
    fcK, fyK, Es = fc * C.MPA, fy * C.MPA, C.ES * C.MPA

    def forces(c):
        depth = umax - u
        a = beta1 * c
        cc = np.where(depth <= a, 0.85 * fcK * (A - As), 0.0)
        eps = 0.003 * (c - depth) / c
        fs = np.clip(Es * eps, -fyK, fyK)
        N = cc.sum() + (fs * As).sum()
        M = (cc * u).sum() + (fs * As * u).sum()
        et = -eps.min()
        return N, M, et

    lo, hi = 1e-3, 3 * (umax - u.min())
    for _ in range(80):
        c = 0.5 * (lo + hi)
        N, M, et = forces(c)
        if N > P:
            hi = c
        else:
            lo = c
    phi = 0.65 + 0.25 * np.clip((et - 0.00245) / (0.005 - 0.00245), 0, 1)
    return abs(M), phi


def design_walls(run):
    t = 0.30
    out = {"compliant": {}, "noncompliant": {}}
    rsa = run["rsa"]
    nP = len(PIERS)
    detail = []
    for k in ("compliant", "noncompliant"):
        out[k] = {p: {z: dict(rho_v=0.0025, rho_h=0.0025) for z in WALL_ZONES} for p in PIERS}
    for s in range(1, C.N_STORY + 1):
        z = wall_zone(s)
        fc = C.wall_fc_spec(s)
        for kp, p in enumerate(PIERS):
            idx = (s - 1) * nP + kp
            ex, ey = rsa[1]["pier"][idx], rsa[2]["pier"][idx]
            E = np.maximum(ex + 0.3 * ey, 0.3 * ex + ey)
            # global components at node i: Fx Fy Fz Mx My Mz
            Vx, Vy, Pe, Mx, My = E[0], E[1], E[2], E[3], E[4]
            Pg = -run["grav"][("pier", s, p)][2]      # eleForce at node i is force on element
            Pg = abs(Pg)
            pp = pier_props(p, t)
            fyt = 390.0
            for k, amp in (("compliant", OMEGA_V_OMEGA_V), ("noncompliant", 1.0)):
                rh = 0.0025
                for V, Acv in ((Vx, pp["Acv_x"]), (Vy, pp["Acv_y"])):
                    vu = amp * V / (PHI_V * Acv) / C.MPA
                    rh = max(rh, (vu - 0.17 * math.sqrt(fc)) / fyt)
                # ACI 318-19 18.10.4.4: Vn <= 0.66 sqrt(fc) Acv -> steel beyond this is useless
                rh_max = (0.66 - 0.17) * math.sqrt(fc) / (fyt * 1.10)
                cur = out[k][p][z]
                if rh > rh_max:
                    cur["shear_cap_exceeded"] = True
                rh = min(rh, rh_max)
                cur["rho_h"] = max(cur["rho_h"], rh)
                # flexure: check 1.1(D+L)+E and 0.8(D+L)-E in both directions/signs
                rv = cur["rho_v"]
                for Pu, Mu, ax in ((1.1 * Pg + Pe, My, "x"), (0.8 * Pg - Pe, My, "x"),
                                   (1.1 * Pg + Pe, Mx, "y"), (0.8 * Pg - Pe, Mx, "y")):
                    for sign in (1, -1):
                        while rv < 0.04:
                            Mn, phi = pier_moment_capacity(p, t, fc, rv, Pu, ax, sign)
                            if phi * Mn >= Mu:
                                break
                            rv += 0.0005
                cur["rho_v"] = max(cur["rho_v"], rv)
            detail.append(dict(story=s, pier=p, Vx=Vx, Vy=Vy, Mx=Mx, My=My, Pe=Pe, Pg=Pg))
    return out, detail


def design_coupling_beams(run):
    rsa = run["rsa"]
    ln = C.CORE["open_front"][1] - C.CORE["open_front"][0]
    jd = C.CB_DEPTH - 0.12
    out = {z: 0.0 for z in WALL_ZONES}
    nk = len(COUPLING_BEAMS)
    vmax = {z: 0.0 for z in WALL_ZONES}
    for i in range(1, C.N_STORY + 1):
        z = wall_zone(i)
        for k in range(nk):
            idx = (i - 1) * nk + k
            ex, ey = rsa[1]["cb"][idx], rsa[2]["cb"][idx]
            E = np.maximum(ex + 0.3 * ey, 0.3 * ex + ey)
            Vu = max(abs(E[2]), abs(E[8]))           # local Vz at ends
            Mu = max(abs(E[4]), abs(E[10]), Vu * ln / 2)
            As = Mu / (0.9 * C.FY_NOM * C.MPA * jd) * 1e6
            As = max(As, 1.4 / C.FY_NOM * 0.3 * (C.CB_DEPTH - 0.06) * 1e6)
            # practical limit for a 300 x 500 conventionally reinforced link beam (2.5 % b d)
            As = min(As, 0.025 * 0.30 * (C.CB_DEPTH - 0.06) * 1e6)
            out[z] = max(out[z], As)
            vmax[z] = max(vmax[z], Vu)
    return out, vmax


def design_beams(run_b):
    b = run_b["b"]
    rsa = run_b["rsa"]
    keys = run_b["keys_floor"]
    grav = run_b["grav"]
    segs = {sg["id"]: sg for sg in b.segments}
    out = {z: {"perim": [0.0, 0.0], "int": [0.0, 0.0]} for z in WALL_ZONES}
    d = C.BEAM_H - 0.065
    for n, key in enumerate(keys):
        i, sid = key
        z = beam_zone(i)
        sg = segs[sid]
        g = grav[("floor",) + key]
        ex, ey = rsa[1]["floor"][n], rsa[2]["floor"][n]
        E = np.maximum(ex + 0.3 * ey, 0.3 * ex + ey)
        # design loads factor ~1.3 on (D+L) service gravity for 1.2D+1.6L
        Mg = max(abs(g[4]), abs(g[10]))
        Me = max(abs(E[4]), abs(E[10]))
        M_neg = max(1.3 * Mg, 1.0 * Mg + Me)
        M_pos = max(Me - 0.8 * Mg, 0.6 * Mg)
        As_t = M_neg / (0.9 * C.FY_NOM * C.MPA * 0.9 * d) * 1e6
        As_b = M_pos / (0.9 * C.FY_NOM * C.MPA * 0.9 * d) * 1e6
        As_min = 1.4 / C.FY_NOM * C.BEAM_B * d * 1e6
        As_t = max(As_t, As_min)
        As_b = max(As_b, 0.5 * As_t, As_min)
        grp = "perim" if sg["perim"] else "int"
        out[z][grp][0] = max(out[z][grp][0], As_t)
        out[z][grp][1] = max(out[z][grp][1], As_b)
    return out


def run_design(out_path):
    design0 = placeholder_design()
    vA = C.Variant(config="A", load_state="design")
    runA = elastic_run(vA, design0)
    walls, detail = design_walls(runA)
    cb_As, cb_V = design_coupling_beams(runA)
    vB = C.Variant(config="B", load_state="design")
    runB = elastic_run(vB, design0)
    beam_As = design_beams(runB)

    def elf(run):
        T1 = run["T"][0]
        Ta = 0.0488 * C.H_TOTAL ** 0.75
        Tuse = min(T1, 1.4 * Ta)
        Cs = max(float(dpt_dbe(Tuse)[0]) * IMPORTANCE / R_FACTOR, 0.01)
        return dict(T1=T1, Tuse=Tuse, Cs=Cs, V=Cs * run["W"], W=run["W"],
                    V_rsa_x=float(run["rsa"][1]["base"]), V_rsa_y=float(run["rsa"][2]["base"]))

    # RSA results are scaled up to 85 % of ELF where needed -> scale design demands
    eA = elf(runA)
    sc = max(1.0, 0.85 * eA["V"] / min(eA["V_rsa_x"], eA["V_rsa_y"]))
    if sc > 1.0:
        for k in runA["rsa"]:
            for kk in runA["rsa"][k]:
                runA["rsa"][k][kk] = runA["rsa"][k][kk] * sc
        walls, detail = design_walls(runA)
        cb_As, cb_V = design_coupling_beams(runA)
    eB = elf(runB)
    scB = max(1.0, 0.85 * eB["V"] / min(eB["V_rsa_x"], eB["V_rsa_y"]))
    if scB > 1.0:
        for k in runB["rsa"]:
            for kk in runB["rsa"][k]:
                runB["rsa"][k][kk] = runB["rsa"][k][kk] * scB
        beam_As = design_beams(runB)
    out = dict(walls=walls, cb_As=cb_As, cb_Vu=cb_V, beam_As=beam_As,
               elf_A=eA, elf_B=eB, rsa_scale_A=sc, rsa_scale_B=scB,
               periods_A=runA["T"][:12].tolist(), periods_B=runB["T"][:12].tolist(),
               wall_detail=detail)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out
