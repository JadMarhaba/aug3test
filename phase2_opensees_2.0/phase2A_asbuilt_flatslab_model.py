"""
PHASE 2A - AS-BUILT MODEL  (post-tensioned flat slab + eccentric core, NO beams)
================================================================================

What this file is
-----------------
The OpenSees (OpenSeesPy) nonlinear model of the State Audit Office building as it was built:
a core-tube / flat-slab system.  The floors are 300 mm post-tensioned flat slabs sitting
directly on 26 columns and on the 17 m x 17 m core, which sits on the rear edge of the plan.
There are no beams, so the core is the only real lateral load path.

Proposal Sec. 3.2 "As-Built Model" table, as used here
------------------------------------------------------
    building height 137 m, 33 storeys (6 m ground storey, ~4.09 m above)
    concrete 5000 - 8000 psi (35 - 55 MPa); core walls specified 500 ksc (49 MPa)
    building grid 39 m x 39 m; core 17 m x 17 m centred on the rear edge
    core wall thickness 250 mm (as-built); coupling (link) beams 250 x 500 mm
    slab 300 mm, post-tensioned; columns 1400 x 1400 mm -> 800 mm circular (storeys 29-33)

What this file adds to the shared building (sao/building_common.py)
-------------------------------------------------------------------
1. Slab strips.  Each span along a column line is an "effective beam width" slab strip
   (Hwang & Moehle 2000: width = 2 c1 + l1/3, cracking factor 0.5 for PT slabs) with plastic
   hinges at its ends whose strength is the column-strip moment capacity of the PT slab.
2. Slab-column and slab-wall connections.  The slab node and the column (or wall) node are
   separate nodes joined by two zero-length elements:
     a. a "punching" element (vertical shear + moment transfer) - REMOVED by the analysis
        when the connection punches: drift-based ACI 318-19 18.14.5.1 criterion for PT slabs,
        evaluated with the *current* gravity shear ratio Vg/Vc (so redistribution after a
        neighbouring failure lowers the remaining drift capacity), or Vg >= Vc;
     b. a "post-punching" vertical spring that stays (integrity bars / tendons over the column:
        40 % of Vc at columns, 30 % at walls).
   This is how the model can show punching cascades and loss of support after core damage.

Deficiency variants (proposal Part 4: "Documented deficiencies will be evaluated
individually, followed by combinations that can represent plausible as-built conditions")
----------------------------------------------------------------------------------------
    D1  core-wall concrete below the specified 500 ksc        (f'c = 0.70 x specified)
    D2  link (coupling) beam bars embedded less than required  (le/ld = 0.50, anchorage pull-out)
    D3  core wall thickness reduced 300 -> 250 mm             (steel per metre kept)
    D4  design not compliant with the regulation              (wall shear steel without the
                                                               required amplification, no
                                                               confined boundary zones)
Variant names are "A-" + the deficiencies that are switched on, e.g.
    A-REF          no deficiencies (300 mm walls, specified concrete, proper anchorage, compliant)
    A-D1           only D1 ... A-D4 only D4            (individual deficiencies)
    A-D1D2 ...     pairs, triples                      (combinations)
    A-D1D2D3D4     all four = THE AS-BUILT CONDITION
The 16 variants are listed in VARIANTS below; run this file to print them and check the model.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openseespy.opensees as ops                                      # noqa: E402
from sao import config as C                                             # noqa: E402
from sao.building_common import SAOBuildingBase, K_STIFF                # noqa: E402
from sao.capacities import (CONN_POINTS, slab_strip, punching_capacity,  # noqa: E402
                            wall_slab_connection_capacity)

MODEL_LABEL = "Phase 2A - As-built post-tensioned flat slab + eccentric core"


class AsBuiltFlatSlabModel(SAOBuildingBase):
    CONFIG = "A"
    MODEL_NAME = MODEL_LABEL
    SLAB_T = C.SLAB_T_FLAT          # 250 mm PT flat slab (version 2.0; 300 mm in phase2_opensees)
    BEAM_STEM_W = 0.0               # no beams

    # -- extra nodes: a slab node at every column and at every core-wall connection ----------
    def _floor_nodes(self, i):
        for c, col in enumerate(self.cols):
            n = 200000 + i * 1000 + c
            ops.node(n, col["x"], col["y"], C.level_z(i))
            self.Ns[(i, c)] = n
        for k, name in enumerate(CONN_POINTS):
            x, y, p = self.cpts[name]
            n = 500000 + i * 1000 + k
            ops.node(n, x, y, C.level_z(i))
            self.Nsc[(i, name)] = n

    def _end_node(self, i, end):
        """Slab strips connect to the SLAB nodes (not directly to columns / walls)."""
        kind, key = end
        return self.Ns[(i, key)] if kind == "col" else self.Nsc[(i, key)]

    def _diaphragm_extra_slaves(self, i):
        return [self.Ns[(i, c)] for c in range(self.ncol)] + [self.Nsc[(i, n)] for n in CONN_POINTS]

    # -- slab strips --------------------------------------------------------------------------
    def _floor_system(self):
        segs = self._build_segments()
        for i in range(1, C.N_STORY + 1):
            shape, D = C.column_section(min(i + 1, C.N_STORY))
            for sg in segs:
                ni, nj = self._end_node(i, sg["a"]), self._end_node(i, sg["b"])
                c1 = D if "col" in (sg["a"][0], sg["b"][0]) else 0.5
                pr = slab_strip(sg["L"], sg["l2"], c1, pos="edge" if sg["perim"] else "interior")
                tag = self.ele()
                # hinge: plastic rotation 0.03 before strength loss (flexure is not what fails a
                # flat slab - punching is, and that is handled by the connection elements)
                self.hinged_member(tag, ni, nj, pr["E"], pr["A"], pr["Iy"], pr["Iz"], pr["J"], pr["lp"],
                                   pr["My_pos"], pr["My_neg"], pr["My_pos"], pr["My_neg"],
                                   0.03, 0.05, 0.3, (0.5, 0.25))
                self.floor_ele[(i, sg["id"])] = tag
                self.floor_info[(i, sg["id"])] = dict(My_neg=pr["My_neg"], My_pos=pr["My_pos"], L=sg["L"],
                                                      beff=pr["beff"])
            self._connections(i)

    # -- slab-column and slab-wall connections (punching) ---------------------------------------
    def _connections(self, i):
        shape, D = C.column_section(i)       # the column below the slab sets the punching perimeter
        for c, col in enumerate(self.cols):
            Vc = punching_capacity(D, pos=col["pos"], circ=(shape == "circ"))   # ACI 318-19 22.6.5.5
            self._connection(i, ("col", c), self.Nc[(i, c)], self.Ns[(i, c)], Vc, col["x"], col["y"], "column")
        for name in CONN_POINTS:
            x, y, p = self.cpts[name]
            Vc = wall_slab_connection_capacity(4.0)   # one-way shear over ~4 m of wall
            self._connection(i, ("core", name), self.W[(i, name)], self.Nsc[(i, name)], Vc, x, y, "wall")

    def _connection(self, i, key, n_sup, n_slab, Vc, x, y, kind):
        punch = self.ele()
        mz = self._elastic_mat(K_STIFF * 0.1)          # vertical shear transfer (stiff)
        mr = self._elastic_mat(K_STIFF)                # moment transfer about X and Y (stiff)
        # zeroLength element: DOF 3 = vertical, 4/5 = rotations about X/Y
        ops.element("zeroLength", punch, n_sup, n_slab, "-mat", mz, mr, mr, "-dir", 3, 4, 5)
        pp, Vres = None, 0.0
        if self.nl:
            pp = self.ele()
            Vres = (0.4 if kind == "column" else 0.3) * Vc
            kpp = Vres / 0.02                          # residual capacity mobilised over 20 mm
            mpp = self.mat()
            ops.uniaxialMaterial("ElasticPP", mpp, kpp, Vres / kpp, -Vres / kpp)
            ops.element("zeroLength", pp, n_sup, n_slab, "-mat", mpp, "-dir", 3)
            self.zl_ele += [punch, pp]
        else:
            self.zl_ele.append(punch)
        self.conn[(i, key)] = dict(punch=punch, pp=pp, Vc=Vc, Vres=Vres, x=x, y=y, kind=kind, level=i,
                                   failed=False)


# ----------------------------------------------------------------------------------------------
# Deficiency variants for the as-built model (individual + every combination = 16 models)
# ----------------------------------------------------------------------------------------------
VARIANTS = {v.name: v for v in C.all_deficiency_variants("A")}
AS_BUILT = VARIANTS["A-D1D2D3D4"]          # all documented deficiencies present
REFERENCE = VARIANTS["A-REF"]              # same framing, no deficiencies


def build(variant="A-D1D2D3D4", design=None, mode="nonlinear"):
    """Build one as-built variant in the OpenSees domain and return the model object."""
    from sao.design import load_design
    v = VARIANTS[variant] if isinstance(variant, str) else variant
    return AsBuiltFlatSlabModel(v, design or load_design(), mode).build()


if __name__ == "__main__":
    print(MODEL_LABEL)
    print(f"{'variant':14s} {'group':12s} description")
    for name, v in VARIANTS.items():
        print(f"{name:14s} {v.group:12s} {v.description}")
    m = build("A-D1D2D3D4")
    print(m.summary())
