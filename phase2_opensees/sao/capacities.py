"""
SHARED BY BOTH MODELS - section geometry and member capacities (ACI 318-19 / ASCE 41-17 based) for the SAO models.

Units: kN, m, kPa unless noted (MPa inputs are converted where stated).
"""
import math
from .config import (CORE, CB_DEPTH, GRID, PLAN, FY_EXP, FYT_EXP, ES, FC_SLAB, PT_PRECOMP,
                     SLAB_T_FLAT, SLAB_T_BEAM, BEAM_B, BEAM_H, MPA, Ec)

PIERS = ("R", "M", "F")   # rear "C", middle "I", front "C"


# ----------------------------------------------------------------------------------------
# Core pier geometry (wide-column / multi-pier idealisation)
# ----------------------------------------------------------------------------------------

def pier_segments(p, t):
    """Wall segments (centreline end points, global x,y) making up pier p.

    Flanges are trimmed by t/2 where they meet a web so corner areas are not double counted.
    Returns list of dicts {a:(x,y), b:(x,y), dir:'x'|'y', role:'web'|'flange'}.
    """
    c = CORE
    x0, x1, y0, y1, ym = c["x0"], c["x1"], c["y0"], c["y1"], c["ymid"]
    fo0, fo1 = c["open_front"]
    ro0, ro1 = c["open_rear"]
    h = t / 2.0
    segs = []
    if p == "R":
        segs.append(dict(a=(x0, y1), b=(x1, y1), dir="x", role="web"))
        for x in (x0, x1):
            segs.append(dict(a=(x, ro1), b=(x, y1 - h), dir="y", role="flange"))
    elif p == "M":
        segs.append(dict(a=(x0, ym), b=(x1, ym), dir="x", role="web"))
        for x in (x0, x1):
            segs.append(dict(a=(x, fo1), b=(x, ym - h), dir="y", role="flange"))
            segs.append(dict(a=(x, ym + h), b=(x, ro0), dir="y", role="flange"))
    elif p == "F":
        segs.append(dict(a=(x0, y0), b=(x1, y0), dir="x", role="web"))
        for x in (x0, x1):
            segs.append(dict(a=(x, y0 + h), b=(x, fo0), dir="y", role="flange"))
    else:
        raise ValueError(p)
    for s in segs:
        s["L"] = math.hypot(s["b"][0] - s["a"][0], s["b"][1] - s["a"][1])
    return segs


def pier_props(p, t):
    segs = pier_segments(p, t)
    A = sum(s["L"] * t for s in segs)
    xc = sum(s["L"] * t * 0.5 * (s["a"][0] + s["b"][0]) for s in segs) / A
    yc = sum(s["L"] * t * 0.5 * (s["a"][1] + s["b"][1]) for s in segs) / A
    Ixx = Iyy = 0.0   # Ixx about global x axis through centroid (bending from y-direction load)
    for s in segs:
        L = s["L"]
        mx = 0.5 * (s["a"][0] + s["b"][0]) - xc
        my = 0.5 * (s["a"][1] + s["b"][1]) - yc
        if s["dir"] == "x":
            Iyy += t * L ** 3 / 12 + L * t * mx ** 2      # about y-axis (x-direction bending)
            Ixx += L * t ** 3 / 12 + L * t * my ** 2
        else:
            Ixx += t * L ** 3 / 12 + L * t * my ** 2
            Iyy += L * t ** 3 / 12 + L * t * mx ** 2
    Acv_x = sum(s["L"] * t for s in segs if s["dir"] == "x")
    Acv_y = sum(s["L"] * t for s in segs if s["dir"] == "y")
    J_open = sum(s["L"] * t ** 3 / 3.0 for s in segs)      # open thin-walled St Venant
    return dict(A=A, xc=xc, yc=yc, Ixx=Ixx, Iyy=Iyy, Acv_x=Acv_x, Acv_y=Acv_y, J=J_open, segs=segs)


def core_points():
    """Points on the core walls where slab strips / beams frame in, plus CB ends.

    Returns dict name -> (x, y, pier).
    """
    c = CORE
    x0, x1, y0, y1 = c["x0"], c["x1"], c["y0"], c["y1"]
    fo0, fo1 = c["open_front"]
    ro0, ro1 = c["open_rear"]
    g = GRID
    pts = {
        # slab / beam connection points (where grid lines meet the core)
        "cL24": (x0, g[3], "F"), "cR24": (x1, g[3], "F"),
        "cL33": (x0, g[4], "M"), "cR33": (x1, g[4], "M"),
        "cF14": (g[2], y0, "F"), "cF24": (g[3], y0, "F"),
        "cBL": (x0, y1, "R"), "cBR": (x1, y1, "R"),
        # coupling-beam ends
        "bL_R": (x0, ro1, "R"), "bL_Mr": (x0, ro0, "M"), "bL_Mf": (x0, fo1, "M"), "bL_F": (x0, fo0, "F"),
        "bR_R": (x1, ro1, "R"), "bR_Mr": (x1, ro0, "M"), "bR_Mf": (x1, fo1, "M"), "bR_F": (x1, fo0, "F"),
    }
    return pts


COUPLING_BEAMS = [("bL_R", "bL_Mr"), ("bL_Mf", "bL_F"), ("bR_R", "bR_Mr"), ("bR_Mf", "bR_F")]
CONN_POINTS = ["cL24", "cR24", "cL33", "cR33", "cF14", "cF24", "cBL", "cBR"]


# ----------------------------------------------------------------------------------------
# Walls
# ----------------------------------------------------------------------------------------

def wall_shear_strength(Acv, fc_mpa, rho_h, fyt_mpa=FYT_EXP):
    """ACI 318-19 Eq. 18.10.4.1 (alpha_c = 0.17 for slender walls), with 0.66 sqrt(fc) cap.

    Returns kN.
    """
    vn = 0.17 * math.sqrt(fc_mpa) + rho_h * fyt_mpa
    vn = min(vn, 0.66 * math.sqrt(fc_mpa))
    return vn * Acv * MPA


def wall_shear_backbone(Vn, Acv, fc_mpa, axial_ratio):
    """Shear spring backbone (V vs shear strain) for a wall pier - 4 points:

    1. diagonal cracking at 0.6 Vn on the uncracked shear stiffness G Acv;
    2. shear strength Vn reached on the cracked stiffness 0.1 G Acv;
    3. strength held to 0.50 % shear drift (0.75 % if P <= 0.05 Ag f'c) - ASCE 41-17
       Table 10-20 'd' for shear-controlled walls;
    4. loss to 20 % residual strength 0.25 % later (ASCE 41 'c' and 'e').
    """
    G = 0.4 * Ec(fc_mpa) * MPA          # kPa
    k0 = G * Acv
    V1 = 0.6 * Vn
    g1 = V1 / k0
    g2 = g1 + 0.4 * Vn / (0.1 * k0)
    gd = 0.0050 if axial_ratio > 0.05 else 0.0075
    gd = max(gd, 1.5 * g2)
    return dict(V1=V1, g1=g1, V2=Vn, g2=g2, gd=gd, V3=0.20 * Vn, g3=gd + 0.0025)


def wall_axial_failure_drift(axial_ratio):
    """Shear-strain (drift) at loss of axial capacity of a shear-damaged wall pier.

    ASCE 41-17 'e' for shear-controlled walls (1.0 % for P>0.05Agf'c, 2.0 % otherwise),
    interpolated and reduced further for very high axial load (Wallace et al. 2012 tests).
    """
    if axial_ratio <= 0.05:
        return 0.020
    if axial_ratio <= 0.10:
        return 0.020 - (axial_ratio - 0.05) / 0.05 * 0.010
    if axial_ratio <= 0.20:
        return 0.010 - (axial_ratio - 0.10) / 0.10 * 0.002
    return 0.008


# ----------------------------------------------------------------------------------------
# Coupling (link) beams
# ----------------------------------------------------------------------------------------

def coupling_beam(t, fc_mpa, As_mm2, embed_ratio=1.0, deficient=False):
    """Conventionally reinforced coupling beam, b = wall thickness, h = 500 mm, ln = 1.5 m.

    deficient -> bar stress limited by bond over the short embedment (fs = fy * le/ld) and
    anchorage pull-out failure (brittle) after the peak.
    """
    h = CB_DEPTH
    ln = CORE["open_front"][1] - CORE["open_front"][0]
    d = h - 0.06
    jd = d - 0.06
    fs = FY_EXP * (embed_ratio if deficient else 1.0)
    My = As_mm2 * 1e-6 * fs * MPA * jd             # kN m
    Vp = 2 * My / ln
    Vc = 0.17 * math.sqrt(fc_mpa) * MPA * t * d
    Av, s = 2 * 113.1e-6, 0.10                       # DB12 2-legs @100 (ASSUMED)
    Vs = Av * FYT_EXP * MPA * d / s
    Vn = Vc + Vs
    E = Ec(fc_mpa) * MPA
    Ig = t * h ** 3 / 12
    EI = 0.20 * E * Ig                               # ACI/TBI effective stiffness for CBs
    shear_ctrl = Vp > Vn
    if deficient:
        # anchorage-controlled: peak at small rotation then rapid pull-out degradation
        th_p, th_pc, res = 0.004, 0.010, 0.10
    elif shear_ctrl:
        # ASCE 41-17 Table 10-19, conventional reinforcement, controlled by shear
        th_p, th_pc, res = 0.012, 0.012, 0.30
    else:
        # ASCE 41-17 Table 10-19, conventional longitudinal, conforming transverse
        th_p, th_pc, res = 0.020, 0.020, 0.50
    return dict(My=min(My, Vn * ln / 2), Vp=Vp, Vn=Vn, EI=EI, E=E, A=t * h, Iz=h * t ** 3 / 12,
                Iy=Ig * 0.2, ln=ln, shear_ctrl=shear_ctrl, th_p=th_p, th_pc=th_pc, res=res, lp=0.5 * h, b=t, h=h)


# ----------------------------------------------------------------------------------------
# Flat slab (as-built) : effective-beam-width strips + punching
# ----------------------------------------------------------------------------------------

def slab_moment_capacity_per_m(t=SLAB_T_FLAT, fc=FC_SLAB, precomp=PT_PRECOMP):
    """Hogging / sagging nominal moment per metre width of the PT flat slab (kN m / m)."""
    d = t - 0.04
    P = precomp * MPA * t                 # kN/m effective prestress
    fse = 1100.0                          # MPa effective tendon stress
    Aps = P / (fse * MPA)                 # m2/m
    fps = fse + 70 + fc / (300 * Aps / (1.0 * d))   # ACI unbonded span/depth > 35 (MPa)
    fps = min(fps, fse + 200)
    As_top = 1005e-6                      # DB16@200 over columns (ASSUMED)
    As_bot = 565e-6                       # DB12@200 bottom (ASSUMED)
    T_neg = Aps * fps * MPA + As_top * FY_EXP * MPA
    a = T_neg / (0.85 * fc * MPA)
    m_neg = T_neg * (d - a / 2)
    T_pos = As_bot * FY_EXP * MPA + 0.3 * Aps * fps * MPA
    a = T_pos / (0.85 * fc * MPA)
    m_pos = T_pos * (d - a / 2)
    return m_neg, m_pos


def punching_capacity(c, t=SLAB_T_FLAT, fc=FC_SLAB, pos="interior", circ=False):
    """Two-way (punching) shear strength of a PT flat-slab connection, ACI 318-19 22.6.5.5.

    vc = 0.29 sqrt(fc) + 0.3 fpc (interior, PT); 0.33 sqrt(fc) for edge connections.
    Returns kN.
    """
    d = 0.8 * t
    if pos == "interior":
        b0 = (math.pi * (c + d)) if circ else 4 * (c + d)
        vc = 0.29 * math.sqrt(fc) + 0.3 * PT_PRECOMP
    else:
        b0 = (0.75 * math.pi * (c + d)) if circ else (2 * (c + d / 2) + (c + d))
        vc = 0.33 * math.sqrt(fc)
    return vc * MPA * b0 * d


def punching_drift_capacity(vg_ratio):
    """Drift ratio at punching for a PT slab-column connection (ACI 318-19 18.14.5.1 for
    unbonded PT slabs, extended to vg/vc -> 1 as in Hueste & Wight 1999)."""
    if vg_ratio >= 1.0:
        return 0.0
    if vg_ratio <= 0.6:
        return 0.040 - 0.05 * vg_ratio
    return 0.010 * (1.0 - vg_ratio) / 0.4


def wall_slab_connection_capacity(b_trib, t=SLAB_T_FLAT, fc=FC_SLAB):
    """One-way shear of the flat slab at the core wall over tributary length b_trib (kN)."""
    d = 0.8 * t
    vc = 0.17 * math.sqrt(fc) + 0.3 * PT_PRECOMP
    return vc * MPA * b_trib * d


def slab_strip(l1, l2_trib, c1, pos="interior", t=SLAB_T_FLAT):
    """Effective beam-width strip (Hwang & Moehle 2000, beta = 0.5 for PT slabs)."""
    alpha_l2 = (2 * c1 + l1 / 3.0) if pos == "interior" else (c1 + l1 / 6.0)
    alpha_l2 = min(alpha_l2, l2_trib)
    E = Ec(FC_SLAB) * MPA
    beta = 0.5
    Iy = beta * alpha_l2 * t ** 3 / 12
    m_neg, m_pos = slab_moment_capacity_per_m(t)
    bcap = 0.5 * l2_trib                  # column strip carries the connection moment
    return dict(E=E, A=alpha_l2 * t, Iy=Iy, Iz=alpha_l2 ** 3 * t / 12, J=0.2 * alpha_l2 * t ** 3 / 3,
                My_neg=m_neg * bcap, My_pos=m_pos * bcap, beff=alpha_l2, lp=t)


# ----------------------------------------------------------------------------------------
# Beams (proposed beam-slab system)
# ----------------------------------------------------------------------------------------

def beam_section(As_top_mm2, As_bot_mm2, b=BEAM_B, h=BEAM_H, fc=FC_SLAB, ts=SLAB_T_BEAM):
    d = h - 0.065
    E = Ec(fc) * MPA
    bf = b + 2 * 6 * ts                       # T-beam flange (ACI 6.3.2.1, interior)
    # gross T-section inertia
    Aw, Af = b * (h - ts), bf * ts
    yw, yf = (h - ts) / 2, h - ts / 2
    yb = (Aw * yw + Af * yf) / (Aw + Af)
    Ig = b * (h - ts) ** 3 / 12 + Aw * (yw - yb) ** 2 + bf * ts ** 3 / 12 + Af * (yf - yb) ** 2
    EI = 0.35 * E * Ig                        # ACI 318-19 Table 6.6.3.1.1(a) cracked beams
    a_neg = As_top_mm2 * 1e-6 * FY_EXP / (0.85 * fc * b)
    My_neg = As_top_mm2 * 1e-6 * FY_EXP * MPA * (d - a_neg / 2)
    a_pos = As_bot_mm2 * 1e-6 * FY_EXP / (0.85 * fc * bf)
    My_pos = As_bot_mm2 * 1e-6 * FY_EXP * MPA * (d - a_pos / 2)
    Vc = 0.17 * math.sqrt(fc) * MPA * b * d
    Vs = 4 * 113.1e-6 * FYT_EXP * MPA * d / 0.15      # 4-leg DB12 @150 (ASSUMED)
    return dict(E=E, A=b * h + (bf - b) * ts, Iy=EI / E, Iz=h * b ** 3 / 12 + ts * (bf - b) ** 3 / 12,
                J=0.2 * b ** 3 * h / 3, My_neg=My_neg, My_pos=My_pos, Vn=Vc + Vs, lp=0.5 * h,
                th_p=0.025, th_pc=0.025, res=0.2)


# ----------------------------------------------------------------------------------------
# Flexure-compression (axial) failure of wall piers: ASCE/SEI 41-13 Table 10-19
# ----------------------------------------------------------------------------------------
# (axial term, shear term, confined boundary) -> (a, b) plastic hinge rotations (rad)
#   axial term  = ((As - As') fy + P) / (tw lw f'c)       brackets <= 0.10 and >= 0.25
#   shear term  = V / (tw lw sqrt(f'c))  [psi]            brackets <= 4 and >= 6
#                 (= 0.332 and 0.498 sqrt(f'c) in MPa units)
#   a = plastic rotation at significant strength loss, b = plastic rotation at the ONSET OF
#   AXIAL FAILURE (loss of gravity-load capacity) - the criterion used to remove a pier.
_T1019 = {
    True: {(0, 0): (0.015, 0.020), (0, 1): (0.010, 0.015), (1, 0): (0.009, 0.012), (1, 1): (0.005, 0.010)},
    False: {(0, 0): (0.008, 0.015), (0, 1): (0.006, 0.010), (1, 0): (0.003, 0.005), (1, 1): (0.002, 0.004)},
}


def wall_flexure_limits(axial_term, shear_ratio_mpa, confined):
    """Bilinear interpolation of ASCE 41-13 Table 10-19 (walls controlled by flexure)."""
    fa = min(max((axial_term - 0.10) / 0.15, 0.0), 1.0)
    fv = min(max((shear_ratio_mpa - 0.332) / (0.498 - 0.332), 0.0), 1.0)
    t = _T1019[bool(confined)]
    out = []
    for k in (0, 1):
        v = ((1 - fa) * (1 - fv) * t[(0, 0)][k] + (1 - fa) * fv * t[(0, 1)][k]
             + fa * (1 - fv) * t[(1, 0)][k] + fa * fv * t[(1, 1)][k])
        out.append(v)
    return tuple(out)


def pier_extents(p, t):
    """Plan depth of pier p in X and in Y (m) - the 'lw' for bending in each direction."""
    segs = pier_segments(p, t)
    xs = [c for s in segs for c in (s["a"][0], s["b"][0])]
    ys = [c for s in segs for c in (s["a"][1], s["b"][1])]
    return max(xs) - min(xs) + t, max(ys) - min(ys) + t
