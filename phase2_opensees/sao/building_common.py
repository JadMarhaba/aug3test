"""
SHARED BY BOTH MODELS  (Phase 2A as-built flat slab  AND  Phase 2B proposed beam-slab)
======================================================================================

This module builds every part of the OpenSees model that is IDENTICAL in the two framing
configurations, so that the framing system is the only experimental variable (proposal Part 4):

    * 33 storeys, 6 m ground storey + ~4.09 m typical storeys, 137 m total
    * 26 columns per floor, 1400x1400 mm (storeys 1-3) stepping down to 800 mm circular (29-33)
    * the eccentric 17 m x 17 m core (250 mm walls as-built; 300 mm if deficiency D3 is "off"),
      its 250 x 500 mm coupling (link) beams, and its connection points
    * rigid floor diaphragms, gravity loads and seismic mass

The two model files add only the floor framing:

    phase2A_asbuilt_flatslab_model.py   -> 300 mm post-tensioned flat slab (no beams),
                                           slab-column punching connections
    phase2B_proposed_beamslab_model.py  -> 500 x 800 mm beams on every column line,
                                           250 mm slab (no punching: beams frame into columns)

How the core is modelled ("multi-pier wide-column" idealisation)
----------------------------------------------------------------
The 17 x 17 m core is split by its 4 door openings into 3 wall piers:
    R = rear "C"   (rear wall + side-wall returns behind the rear openings)
    M = middle "I" (middle cross wall + side-wall segments between the openings)
    F = front "C"  (front wall + side-wall returns in front of the front openings)
Each pier is one vertical fibre beam-column element per storey placed at the pier centroid.
Its section is the real C / I shape made of concrete and steel fibres, so it captures axial
force - biaxial bending interaction, concrete crushing and bar yielding/buckling.  A nonlinear
shear spring (one per horizontal direction) is aggregated to the section so that diagonal-shear
failure of the walls (the documented failure mode) can occur.  Stiff "rigid arm" elements tie
each pier centroid to the points on its walls where coupling beams and the floor framing attach.

Node-numbering scheme (level i = 0..33, 0 = base)
-------------------------------------------------
    100000 + 1000 i + c   column node of column c         (both models)
    200000 + 1000 i + c   slab node at column c           (flat slab only)
    300000 + 1000 i + k   core pier centroid, k = 0 R, 1 M, 2 F   (both)
    400000 + 1000 i + k   point on a core wall (rigid-arm end)    (both)
    500000 + 1000 i + k   slab node at a core-wall connection     (flat slab only)
    900000 + i            diaphragm master node of floor i        (both)

Units: kN, m, s, tonne.
"""
import math
import numpy as np
import openseespy.opensees as ops

from . import config as C
from .capacities import (PIERS, pier_props, core_points, COUPLING_BEAMS, CONN_POINTS,
                         wall_shear_strength, wall_shear_backbone, coupling_beam, pier_extents)

E_RIGID = 1.0e9     # kPa  - modulus of the rigid arms (stiff but numerically well-conditioned)
K_STIFF = 1.0e8     # kN/m - "rigid" zero-length springs


class TagGen:
    """Simple counter that hands out unique OpenSees tags (element, material, section ...)."""

    def __init__(self, start=1):
        self.n = start - 1

    def __call__(self):
        self.n += 1
        return self.n


class SAOBuildingBase:
    """Common building model.  Not used directly - use AsBuiltFlatSlabModel (Phase 2A) or
    ProposedBeamSlabModel (Phase 2B), which add the floor framing.

    variant : config.Variant  - which deficiencies are switched on (D1..D4)
    design  : dict            - reinforcement from the design pass (results/design.json)
    mode    : 'nonlinear' (Phase 2 models) or 'elastic' (used only by the design pass)
    """
    CONFIG = None          # 'A' (as-built) or 'B' (proposed) - set by the subclass
    MODEL_NAME = None
    SLAB_T = None          # slab thickness (m)
    BEAM_STEM_W = 0.0      # self-weight of beam stems below the slab (kN/m), beam model only

    def __init__(self, variant, design, mode="nonlinear"):
        if variant.config != self.CONFIG:
            raise ValueError(f"{self.MODEL_NAME} needs a variant with config='{self.CONFIG}'")
        self.v = variant
        self.design = design
        self.mode = mode
        self.nl = mode == "nonlinear"
        self.mat, self.sec, self.ele, self.integ = TagGen(), TagGen(), TagGen(), TagGen()
        self._mat_cache, self._sec_cache = {}, {}
        self.cols = C.column_points()
        self.ncol = len(self.cols)
        # node dictionaries
        self.Nc, self.Ns, self.P, self.W, self.Nsc, self.master = {}, {}, {}, {}, {}, {}
        # element registries used by the analyses / failure monitors
        self.col_ele, self.pier_ele, self.pier_info = {}, {}, {}
        self.cb_ele, self.cb_info = {}, {}
        self.arm_ele = []
        self.floor_ele, self.floor_info = {}, {}
        self.conn = {}            # flat slab only: punching connections
        self.zl_ele = []
        self.node_mass, self.nodal_loads, self.ele_loads = {}, {}, {}
        self.segments = []

    # ====================================================================================
    # build sequence
    # ====================================================================================
    def build(self):
        ops.wipe()                                  # clear any previous model
        ops.model("basic", "-ndm", 3, "-ndf", 6)    # 3-D model, 6 DOF per node
        self._transforms()
        self._nodes()
        self._columns()
        self._core()
        self._floor_system()                        # <- defined by the two model files
        self._diaphragms()
        self._gravity_and_mass()
        return self

    # ------------------------------------------------------------------------------------
    def _transforms(self):
        """Geometric transformations = orientation of member local axes.

        Vertical members use P-Delta (second-order effects of gravity on the swaying building).
        For them local y = global X and local z = global Y, so fibre coordinates are simply
        (X - Xc, Y - Yc).  Horizontal members have local z = global Z, so gravity bending is
        about the local y axis ('My').
        """
        self.tr_col, self.tr_hor, self.tr_arm = 1, 2, 3
        ops.geomTransf("PDelta", self.tr_col, 0.0, 1.0, 0.0)
        ops.geomTransf("Linear", self.tr_hor, 0.0, 0.0, 1.0)
        ops.geomTransf("Linear", self.tr_arm, 0.0, 0.0, 1.0)

    def _nodes(self):
        t = self.v.wall_t
        self.pprops = {p: pier_props(p, t) for p in PIERS}     # area, centroid, I of each pier
        self.cpts = core_points()                               # attachment points on the walls
        for i in range(C.N_STORY + 1):
            z = C.level_z(i)
            for c, col in enumerate(self.cols):                 # column nodes
                n = 100000 + i * 1000 + c
                ops.node(n, col["x"], col["y"], z)
                self.Nc[(i, c)] = n
                if i == 0:
                    ops.fix(n, 1, 1, 1, 1, 1, 1)                # fixed base (pile cap)
            for k, p in enumerate(PIERS):                       # core pier centroid nodes
                n = 300000 + i * 1000 + k
                ops.node(n, self.pprops[p]["xc"], self.pprops[p]["yc"], z)
                self.P[(i, p)] = n
                if i == 0:
                    ops.fix(n, 1, 1, 1, 1, 1, 1)
            if i == 0:
                continue
            for k, (name, (x, y, p)) in enumerate(self.cpts.items()):   # wall attachment points
                n = 400000 + i * 1000 + k
                ops.node(n, x, y, z)
                self.W[(i, name)] = n
            self._floor_nodes(i)                                # extra nodes of the framing type
            m = 900000 + i                                      # diaphragm master node
            ops.node(m, C.PLAN / 2, C.PLAN / 2, z)
            ops.fix(m, 0, 0, 1, 1, 1, 0)                        # free: X, Y, rotation about Z
            self.master[i] = m

    # ====================================================================================
    # materials
    # ====================================================================================
    def _concrete(self, fc_mpa, kind):
        """Concrete02 = Kent-Park concrete with linear tension softening.

        kind: 'cover' / 'wall_unconf' unconfined (crushes at 0.2 %, 20 % residual at 0.6 %)
              'wall_conf' confined wall boundary zone (code-compliant walls only)
              'col_core'  confined column core
        """
        key = ("conc", round(fc_mpa, 3), kind)
        if key in self._mat_cache:
            return self._mat_cache[key]
        tag = self.mat()
        fc = fc_mpa * C.MPA
        ft = 0.33 * math.sqrt(fc_mpa) * C.MPA * 0.5
        if kind in ("cover", "wall_unconf"):
            ops.uniaxialMaterial("Concrete02", tag, -fc, -0.002, -0.2 * fc, -0.006, 0.1, ft, ft / 0.002)
        elif kind == "wall_conf":
            K = 1.3
            ops.uniaxialMaterial("Concrete02", tag, -K * fc, -0.002 * (1 + 5 * (K - 1)), -0.5 * K * fc,
                                 -0.015, 0.1, ft, ft / 0.002)
        elif kind == "col_core":
            K = 1.2
            ops.uniaxialMaterial("Concrete02", tag, -K * fc, -0.002 * (1 + 5 * (K - 1)), -0.4 * K * fc,
                                 -0.012, 0.1, ft, ft / 0.002)
        else:
            raise ValueError(kind)
        self._mat_cache[key] = tag
        return tag

    def _steel(self, emin):
        """Steel02 (Menegotto-Pinto) reinforcing bar, wrapped in MinMax so that the bar stops
        carrying stress once it buckles (strain < emin) or fractures (strain > 8 %)."""
        key = ("steel", emin)
        if key in self._mat_cache:
            return self._mat_cache[key]
        base = self.mat()
        ops.uniaxialMaterial("Steel02", base, C.FY_EXP * C.MPA, C.ES * C.MPA, 0.01, 18.0, 0.925, 0.15)
        tag = self.mat()
        ops.uniaxialMaterial("MinMax", tag, base, "-min", emin, "-max", 0.08)
        self._mat_cache[key] = tag
        return tag

    def _elastic_mat(self, k):
        key = ("el", float(k))
        if key in self._mat_cache:
            return self._mat_cache[key]
        tag = self.mat()
        ops.uniaxialMaterial("Elastic", tag, k)
        self._mat_cache[key] = tag
        return tag

    def _hinge_mat(self, EI, lp, My_pos, My_neg, th_p, th_pc, res, pinch=(0.6, 0.3)):
        """Plastic-hinge moment-curvature law (Hysteretic material).

        Elastic to My, 5 % hardening over the plastic rotation th_p, then strength loss over
        th_pc down to a residual fraction 'res' of My.  Curvature = rotation / hinge length lp.
        Used for coupling beams, slab strips and beams.
        """
        tag = self.mat()
        phy_p, phy_n = My_pos / EI, My_neg / EI
        ops.uniaxialMaterial("Hysteretic", tag,
                             My_pos, phy_p, 1.05 * My_pos, phy_p + th_p / lp, res * My_pos,
                             phy_p + (th_p + th_pc) / lp,
                             -My_neg, -phy_n, -1.05 * My_neg, -(phy_n + th_p / lp), -res * My_neg,
                             -(phy_n + (th_p + th_pc) / lp),
                             pinch[0], pinch[1], 0.0, 0.0, 0.0)
        return tag

    def hinged_member(self, tag, ni, nj, E, A, Iy, Iz, J, lp, Mp_i, Mn_i, Mp_j, Mn_j, th_p, th_pc, res,
                      pinch, transf=None):
        """Horizontal member with lumped plastic hinges at both ends (used by slab strips,
        beams and coupling beams).

        forceBeamColumn + 'HingeRadau' integration: the element is elastic in the middle and
        its two end regions of length lp follow the hinge moment-curvature law above.
        """
        transf = transf or self.tr_hor
        G = 0.4 * E
        if not self.nl:
            ops.element("elasticBeamColumn", tag, ni, nj, A, E, G, J, Iy, Iz, transf)
            return
        el = self.sec()
        ops.section("Elastic", el, E, A, Iz, Iy, G, J)
        mP, mZ, mT = self._elastic_mat(E * A), self._elastic_mat(E * Iz), self._elastic_mat(G * J)
        hi = self._hinge_mat(E * Iy, lp, Mp_i, Mn_i, th_p, th_pc, res, pinch)
        hj = self._hinge_mat(E * Iy, lp, Mp_j, Mn_j, th_p, th_pc, res, pinch)
        si, sj = self.sec(), self.sec()
        # 'Aggregator' combines independent axial (P), in-plane (Mz), gravity-plane (My) and
        # torsion (T) responses into one section; only 'My' is nonlinear.
        ops.section("Aggregator", si, mP, "P", mZ, "Mz", hi, "My", mT, "T")
        ops.section("Aggregator", sj, mP, "P", mZ, "Mz", hj, "My", mT, "T")
        it = self.integ()
        ops.beamIntegration("HingeRadau", it, si, lp, sj, lp, el)
        ops.element("forceBeamColumn", tag, ni, nj, transf, it, "-iter", 30, 1e-10)

    # ====================================================================================
    # columns (identical in both models)
    # ====================================================================================
    def _column_sections(self, story):
        """Fibre section of a column for storey 'story' (size / f'c / steel from config)."""
        shape, D = C.column_section(story)
        fc, rho = C.column_fc(story), C.column_rho(story)
        key = ("col", shape, D, fc, rho)
        if key in self._sec_cache:
            return self._sec_cache[key]
        E = C.Ec(fc) * C.MPA
        G = 0.4 * E
        if shape == "rect":
            A, I, J = D * D, D ** 4 / 12, 0.141 * D ** 4
        else:
            A, I = math.pi * D ** 2 / 4, math.pi * D ** 4 / 64
            J = 2 * I
        el = self.sec()
        ops.section("Elastic", el, E, A, 0.7 * I, 0.7 * I, G, 0.2 * J)   # cracked interior
        if not self.nl:
            self._sec_cache[key] = (el, el, A, I, E)
            return self._sec_cache[key]
        fib = self.sec()
        cov, core = self._concrete(fc, "cover"), self._concrete(fc, "col_core")
        st = self._steel(-0.03)
        cc = 0.05                                         # cover to bar centre (m)
        ops.section("Fiber", fib, "-GJ", G * 0.2 * J)
        As = rho * A
        if shape == "rect":
            h, hc = D / 2, D / 2 - cc
            ops.patch("rect", core, 5, 5, -hc, -hc, hc, hc)        # confined core
            ops.patch("rect", cov, 5, 1, -h, -h, h, -hc)           # 4 cover strips
            ops.patch("rect", cov, 5, 1, -h, hc, h, h)
            ops.patch("rect", cov, 1, 5, -h, -hc, -hc, hc)
            ops.patch("rect", cov, 1, 5, hc, -hc, h, hc)
            nb = 5
            ab = As / (4 * (nb - 1))                               # 16 perimeter bars
            sp = 2 * hc / (nb - 1)
            ops.layer("straight", st, nb, ab, -hc, -hc, hc, -hc)
            ops.layer("straight", st, nb, ab, -hc, hc, hc, hc)
            ops.layer("straight", st, nb - 2, ab, -hc, -hc + sp, -hc, hc - sp)
            ops.layer("straight", st, nb - 2, ab, hc, -hc + sp, hc, hc - sp)
        else:
            r, rc = D / 2, D / 2 - cc
            ops.patch("circ", core, 8, 3, 0.0, 0.0, 0.0, rc, 0.0, 360.0)
            ops.patch("circ", cov, 8, 1, 0.0, 0.0, rc, r, 0.0, 360.0)
            ops.layer("circ", st, 12, As / 12, 0.0, 0.0, rc)
        self._sec_cache[key] = (fib, el, A, I, E)
        return self._sec_cache[key]

    def _columns(self):
        """One forceBeamColumn per column per storey: fibre plastic hinges (length 0.5 D) at
        both ends, cracked elastic in between (HingeRadau)."""
        for s in range(1, C.N_STORY + 1):
            fib, el, A, I, E = self._column_sections(s)
            shape, D = C.column_section(s)
            lp = 0.5 * D
            for c in range(self.ncol):
                tag = self.ele()
                ni, nj = self.Nc[(s - 1, c)], self.Nc[(s, c)]
                if self.nl:
                    it = self.integ()
                    ops.beamIntegration("HingeRadau", it, fib, lp, fib, lp, el)
                    ops.element("forceBeamColumn", tag, ni, nj, self.tr_col, it, "-iter", 30, 1e-10)
                else:
                    J = 0.141 * D ** 4 if shape == "rect" else math.pi * D ** 4 / 32
                    ops.element("elasticBeamColumn", tag, ni, nj, A, E, 0.4 * E, 0.2 * J, 0.7 * I, 0.7 * I,
                                self.tr_col)
                self.col_ele[(s, c)] = tag
                w = A * C.story_h(s) * C.GAMMA_RC            # self-weight, half to each end
                self._add_load(ni, w / 2)
                self._add_load(nj, w / 2)

    # ====================================================================================
    # core walls + coupling (link) beams (identical in both models)
    # ====================================================================================
    def _pier_section(self, story, p):
        """Fibre section of core pier p at a storey; THIS IS WHERE D1, D3, D4 ACT:

        D1 (low concrete strength) -> wall f'c = fc_ratio x specified (variant.wall_fc)
        D3 (250 mm instead of 300) -> wall thickness t (variant.wall_t); the steel area per
                                      metre of the 300 mm design is kept ("added steel")
        D4 (non-compliant design)  -> 'noncompliant' reinforcement (shear steel designed without
                                      the dynamic amplification) and unconfined boundary zones
        """
        v = self.v
        t, fc = v.wall_t, v.wall_fc(story)
        zone = self.design["wall_zone"](story)
        rd = self.design["walls"]["noncompliant" if v.D4 else "compliant"][p][zone]
        scale = 0.30 / t
        rho_v, rho_h = rd["rho_v"] * scale, rd["rho_h"] * scale
        confined = not v.D4
        pp = self.pprops[p]
        key = ("pier", p, story if self.nl else zone, round(fc, 2), t, rho_v, rho_h, confined)
        if key in self._sec_cache:
            return self._sec_cache[key]
        E = C.Ec(fc) * C.MPA
        G = 0.4 * E
        info = dict(fc=fc, t=t, rho_v=rho_v, rho_h=rho_h, A=pp["A"], E=E, confined=confined,
                    Vn_x=wall_shear_strength(pp["Acv_x"], fc, rho_h),     # ACI 318-19 Eq. 18.10.4.1
                    Vn_y=wall_shear_strength(pp["Acv_y"], fc, rho_h))
        if not self.nl:
            self._sec_cache[key] = (None, info)
            return self._sec_cache[key]
        unc = self._concrete(fc, "wall_unconf")
        conf = self._concrete(fc, "wall_conf") if confined else unc
        st_unc = self._steel(-0.010)                   # bars buckle early in unconfined concrete
        st_conf = self._steel(-0.030) if confined else st_unc
        fib = self.sec()
        ops.section("Fiber", fib, "-GJ", G * pp["J"])  # open thin-walled St Venant torsion
        xc, yc = pp["xc"], pp["yc"]
        for sg in pp["segs"]:                          # each straight wall segment of the pier
            L = sg["L"]
            lbe = min(1.0 if sg["role"] == "web" else 0.6, L / 3)    # boundary-zone length
            (xa, ya), (xb, yb) = sg["a"], sg["b"]
            for s0, s1, cm, sm in ((0.0, lbe, conf, st_conf), (lbe, L - lbe, unc, st_unc),
                                   (L - lbe, L, conf, st_conf)):
                ln = s1 - s0
                if ln <= 1e-6:
                    continue
                nf = max(1, int(math.ceil(ln / 0.8)))   # concrete fibres ~0.8 m long
                nb = max(2, int(round(ln / 0.5)))        # one "bar" fibre per 0.5 m of wall
                ab = rho_v * t * ln / nb
                if sg["dir"] == "x":
                    x0, x1 = xa + s0, xa + s1
                    ops.patch("rect", cm, nf, 1, x0 - xc, ya - t / 2 - yc, x1 - xc, ya + t / 2 - yc)
                    dx = ln / nb
                    ops.layer("straight", sm, nb, ab, x0 + dx / 2 - xc, ya - yc, x1 - dx / 2 - xc, ya - yc)
                else:
                    y0, y1 = ya + s0, ya + s1
                    ops.patch("rect", cm, 1, nf, xa - t / 2 - xc, y0 - yc, xa + t / 2 - xc, y1 - yc)
                    dy = ln / nb
                    ops.layer("straight", sm, nb, ab, xa - xc, y0 + dy / 2 - yc, xa - xc, y1 - dy / 2 - yc)
        self._sec_cache[key] = (fib, info)
        return self._sec_cache[key]

    def _shear_mat(self, Vn, Acv, fc, axial_ratio):
        """Wall shear spring (HystereticSM, shear force vs shear strain): cracking at 0.6 Vn,
        strength Vn on the cracked stiffness 0.1 G A, plateau to 0.5 %, then loss to 20 %
        residual (ASCE 41-17 shear-controlled walls).  Pinched hysteresis."""
        b = wall_shear_backbone(Vn, Acv, fc, axial_ratio)
        tag = self.mat()
        # 1 % hardening on the "plateau" keeps the tangent non-zero (a zero tangent makes the
        # force-based element's section flexibility singular)
        env = [b["V1"], b["g1"], b["V2"], b["g2"], 1.01 * b["V2"], b["gd"], b["V3"], b["g3"]]
        ops.uniaxialMaterial("HystereticSM", tag, "-posEnv", *env, "-negEnv", *[-x for x in env],
                             "-pinch", 0.4, 0.2, "-damage", 0.0, 0.0, "-beta", 0.3)
        return tag, b

    def _core(self):
        self._core_axial_estimate()
        for s in range(1, C.N_STORY + 1):
            h = C.story_h(s)
            for p in PIERS:
                fib, info = self._pier_section(s, p)
                pp = self.pprops[p]
                tag = self.ele()
                ni, nj = self.P[(s - 1, p)], self.P[(s, p)]
                ar = self._axial_ratio_est[(s, p)] * C.wall_fc_spec(s) / info["fc"]
                if self.nl:
                    # shear springs: 'Vy' = global X shear (resisted by the walls running in X),
                    #                'Vz' = global Y shear (resisted by the side-wall segments)
                    mvx, bx = self._shear_mat(info["Vn_x"], pp["Acv_x"], info["fc"], ar)
                    mvy, by = self._shear_mat(info["Vn_y"], pp["Acv_y"], info["fc"], ar)
                    agg = self.sec()
                    ops.section("Aggregator", agg, mvx, "Vy", mvy, "Vz", "-section", fib)
                    it = self.integ()
                    ops.beamIntegration("Lobatto", it, agg, 3)       # 3 sections: base, mid, top
                    ops.element("forceBeamColumn", tag, ni, nj, self.tr_col, it, "-iter", 30, 1e-10)
                    info = dict(info, back_x=bx, back_y=by)
                else:
                    E = info["E"]
                    ops.element("ElasticTimoshenkoBeam", tag, ni, nj, E, 0.4 * E, pp["A"], pp["J"],
                                0.5 * pp["Ixx"], 0.5 * pp["Iyy"], pp["Acv_x"] * 0.5, pp["Acv_y"] * 0.5,
                                self.tr_col)
                self.pier_ele[(s, p)] = tag
                w = pp["A"] * h * C.GAMMA_RC
                lx, ly = pier_extents(p, self.v.wall_t)
                self.pier_info[(s, p)] = dict(info, axial_ratio_est=ar, h=h, Acv_x=pp["Acv_x"],
                                              Acv_y=pp["Acv_y"], w_self=w, nodes=(ni, nj), lw_x=lx, lw_y=ly)
                self._add_load(ni, w / 2)
                self._add_load(nj, w / 2)
        # rigid arms: pier centroid -> every attachment point on that pier's walls
        for i in range(1, C.N_STORY + 1):
            for name, (x, y, p) in self.cpts.items():
                tag = self.ele()
                ops.element("elasticBeamColumn", tag, self.P[(i, p)], self.W[(i, name)], 5.0, E_RIGID,
                            0.4 * E_RIGID, 5.0, 5.0, 5.0, self.tr_arm)
                self.arm_ele.append(tag)
        # coupling (link) beams 250 x 500 mm across the 4 door openings at every floor.
        # THIS IS WHERE D2 ACTS: short bar embedment limits the bar stress to fy x (le/ld) and
        # makes the beam fail by anchorage pull-out soon after its (reduced) peak.
        for i in range(1, C.N_STORY + 1):
            cb = coupling_beam(self.v.wall_t, self.v.wall_fc(i), self.design["cb_As"][self.design["wall_zone"](i)],
                               self.v.embed_ratio, deficient=self.v.D2)
            for k, (a, b) in enumerate(COUPLING_BEAMS):
                tag = self.ele()
                self.hinged_member(tag, self.W[(i, a)], self.W[(i, b)], cb["E"], cb["A"], cb["EI"] / cb["E"],
                                   cb["Iz"], 0.2 * cb["Iz"], cb["lp"], cb["My"], cb["My"], cb["My"], cb["My"],
                                   cb["th_p"], cb["th_pc"], cb["res"], (0.4, 0.2))
                self.cb_ele[(i, k)] = tag
                self.cb_info[(i, k)] = cb

    def _core_axial_estimate(self):
        """Approximate gravity axial-load ratio of each pier (used to pick shear-spring
        parameters before the gravity analysis; refined after gravity in analysis.py)."""
        lw = C.LOADS[self.v.load_state]
        q = (self.SLAB_T + (0.07 if self.CONFIG == "B" else 0.0)) * C.GAMMA_RC + lw["sdl"] + lw["live"]
        trib = {"R": 70.0, "M": 60.0, "F": 110.0}
        self._axial_ratio_est = {}
        for s in range(1, C.N_STORY + 1):
            nfl = C.N_STORY - s + 1
            for p in PIERS:
                pp = self.pprops[p]
                P = nfl * (q * trib[p] + pp["A"] * C.H_TYP * C.GAMMA_RC)
                self._axial_ratio_est[(s, p)] = P / (pp["A"] * C.wall_fc_spec(s) * C.MPA)

    # ====================================================================================
    # floor framing lines (the members are created by the two model files)
    # ====================================================================================
    def _support_points_on_line(self, direction, coord):
        pts = []
        for c, col in enumerate(self.cols):
            if direction == "x" and abs(col["y"] - coord) < 1e-6:
                pts.append((col["x"], ("col", c)))
            if direction == "y" and abs(col["x"] - coord) < 1e-6:
                pts.append((col["y"], ("col", c)))
        for name in CONN_POINTS:
            x, y, p = self.cpts[name]
            if direction == "x" and abs(y - coord) < 1e-6:
                pts.append((x, ("core", name)))
            if direction == "y" and abs(x - coord) < 1e-6:
                pts.append((y, ("core", name)))
        pts.sort(key=lambda a: a[0])
        return pts

    def _build_segments(self):
        """Spans along every column line between supports (columns or core walls).

        In the flat-slab model each span becomes an effective-width slab strip; in the
        beam-slab model each span becomes a 500 x 800 beam.  Same layout in both models.
        """
        segs = []
        g = C.GRID
        for direction in ("x", "y"):
            for li, coord in enumerate(g):
                pts = self._support_points_on_line(direction, coord)
                lo = coord - g[li - 1] if li > 0 else 0.0
                hi = g[li + 1] - coord if li < len(g) - 1 else 0.0
                for (s0, a), (s1, b) in zip(pts[:-1], pts[1:]):
                    if a[0] == "core" and b[0] == "core":
                        continue                       # span inside the core: no member
                    segs.append(dict(dir=direction, coord=coord, s0=s0, s1=s1, a=a, b=b, L=s1 - s0,
                                     l2=0.5 * (lo + hi), perim=li in (0, len(g) - 1)))
        for k, sgm in enumerate(segs):
            sgm["id"] = k
        self.segments = segs
        return segs

    # hooks implemented by the two model files ---------------------------------------------
    def _floor_nodes(self, i):
        pass

    def _end_node(self, i, end):
        raise NotImplementedError

    def _floor_system(self):
        raise NotImplementedError

    def _diaphragm_extra_slaves(self, i):
        return []

    # ====================================================================================
    def _diaphragms(self):
        """Rigid in-plane floor diaphragm per level: all floor nodes follow the master node
        in X, Y and rotation about Z (vertical motion and slab bending stay free)."""
        for i in range(1, C.N_STORY + 1):
            slaves = [self.Nc[(i, c)] for c in range(self.ncol)] + [self.P[(i, p)] for p in PIERS]
            slaves += self._diaphragm_extra_slaves(i)
            ops.rigidDiaphragm(3, self.master[i], *slaves)

    # ====================================================================================
    # gravity loads and mass
    # ====================================================================================
    def _add_load(self, node, w_down):
        self.nodal_loads[node] = self.nodal_loads.get(node, 0.0) + w_down

    def _mass_node(self, node):
        """Masses on wall attachment nodes are lumped at the pier centroid."""
        if 400000 <= node < 500000:
            i = (node - 400000) // 1000
            k = node - 400000 - i * 1000
            name = list(self.cpts.keys())[k]
            return self.P[(i, self.cpts[name][2])]
        return node

    def _floor_load_raster(self, q, q_core=0.3):
        """Two-way distribution of the floor pressure q (kPa) to the supporting lines.

        The floor is cut into 0.25 m cells; half of each cell's load goes to the nearest
        support line running in X and half to the nearest one running in Y.  Support lines are
        the framing spans and the core walls.  Inside the core (shafts) only 30 % of q is applied
        (landings / stairs).  Returns uniform load per span (kN/m) and load per core pier (kN).
        """
        cs = 0.25
        xs = np.arange(cs / 2, C.PLAN, cs)
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        X, Y = X.ravel(), Y.ravel()
        cc = C.CORE
        incore = (X > cc["x0"]) & (X < cc["x1"]) & (Y > cc["y0"]) & (Y < cc["y1"])
        load = np.where(incore, q * q_core, q) * cs * cs
        lines = {"x": [], "y": []}
        for sg in self.segments:
            lines[sg["dir"]].append((sg["coord"], sg["s0"], sg["s1"], ("seg", sg["id"])))
        fo = 0.5 * (cc["open_front"][0] + cc["open_front"][1])
        ro = 0.5 * (cc["open_rear"][0] + cc["open_rear"][1])
        lines["x"] += [(cc["y0"], cc["x0"], cc["x1"], ("pier", "F")), (cc["ymid"], cc["x0"], cc["x1"], ("pier", "M")),
                       (cc["y1"], cc["x0"], cc["x1"], ("pier", "R"))]
        for xw in (cc["x0"], cc["x1"]):
            lines["y"] += [(xw, cc["y0"], fo, ("pier", "F")), (xw, fo, ro, ("pier", "M")),
                           (xw, ro, cc["y1"], ("pier", "R"))]
        seg_w, pier_P = {}, {p: 0.0 for p in PIERS}
        for d in ("x", "y"):
            along, perp = (X, Y) if d == "x" else (Y, X)
            best = np.full(X.shape, np.inf)
            who = np.full(X.shape, -1)
            for k, (coord, s0, s1, tgt) in enumerate(lines[d]):
                inside = (along >= s0 - 1e-9) & (along <= s1 + 1e-9)
                dist = np.where(inside, np.abs(perp - coord), np.inf)
                upd = dist < best
                best[upd], who[upd] = dist[upd], k
            for k, (coord, s0, s1, tgt) in enumerate(lines[d]):
                tot = 0.5 * load[who == k].sum()
                if tgt[0] == "seg":
                    seg_w[tgt[1]] = seg_w.get(tgt[1], 0.0) + tot
                else:
                    pier_P[tgt[1]] += tot
        for sg in self.segments:
            seg_w[sg["id"]] = seg_w.get(sg["id"], 0.0) / sg["L"]
        return seg_w, pier_P

    def _gravity_and_mass(self):
        """Gravity loads (slab self-weight + superimposed dead + live + facade) and the seismic
        mass derived from them (translational mass in X, Y and Z at every floor node)."""
        lw = C.LOADS[self.v.load_state]
        q = self.SLAB_T * C.GAMMA_RC + lw["sdl"] + lw["live"]
        self.floor_q = q
        seg_w, pier_P = self._floor_load_raster(q)
        perim_cols = [c for c, col in enumerate(self.cols) if col["pos"] == "edge"]
        for i in range(1, C.N_STORY + 1):
            for sg in self.segments:
                tag = self.floor_ele[(i, sg["id"])]
                w = seg_w[sg["id"]] + self.BEAM_STEM_W
                self.ele_loads[tag] = w
                for end in (sg["a"], sg["b"]):
                    mn = self._mass_node(self._end_node(i, end))
                    self.node_mass[mn] = self.node_mass.get(mn, 0.0) + w * sg["L"] / 2 / C.G
            for p in PIERS:
                self._add_load(self.P[(i, p)], pier_P[p])
            h = 0.5 * (C.story_h(i) + (C.story_h(i + 1) if i < C.N_STORY else 0.0))
            fw = lw["facade"] * h
            core_len = C.CORE["x1"] - C.CORE["x0"]
            for c in perim_cols:
                self._add_load(self.Nc[(i, c)], fw * (4 * C.PLAN - core_len) / len(perim_cols))
            self._add_load(self.P[(i, "R")], fw * core_len)
        for n, w in self.nodal_loads.items():
            if 100000 <= n < 101000 or 300000 <= n < 301000:
                continue                                        # base nodes: no mass
            mn = self._mass_node(n)
            self.node_mass[mn] = self.node_mass.get(mn, 0.0) + w / C.G
        for n, m in self.node_mass.items():
            ops.mass(n, m, m, m, 0.0, 0.0, 0.0)
        Wl = {}
        for n, m in self.node_mass.items():
            z = round(ops.nodeCoord(n)[2], 3)
            Wl[z] = Wl.get(z, 0.0) + m * C.G
        self.weight_by_level = Wl
        self.total_weight = sum(Wl.values())

    def apply_gravity_pattern(self, ts_tag=1, pat_tag=1, factor=1.0):
        """Create the gravity load pattern (uniform loads on spans + nodal loads)."""
        ops.timeSeries("Linear", ts_tag)
        ops.pattern("Plain", pat_tag, ts_tag)
        for tag, w in self.ele_loads.items():
            ops.eleLoad("-ele", tag, "-type", "-beamUniform", 0.0, -w * factor, 0.0)
        for n, w in self.nodal_loads.items():
            ops.load(n, 0.0, 0.0, -w * factor, 0.0, 0.0, 0.0)

    def all_frame_elements(self):
        """Elements that receive stiffness-proportional (Rayleigh) damping."""
        return (list(self.col_ele.values()) + list(self.pier_ele.values()) + list(self.cb_ele.values())
                + list(self.floor_ele.values()))

    def summary(self):
        return dict(model=self.MODEL_NAME, variant=self.v.name, total_weight_kN=self.total_weight,
                    n_nodes=len(ops.getNodeTags()), n_ele=len(ops.getEleTags()), floor_q_kPa=self.floor_q)
