"""
PHASE 2B - PROPOSED MODEL  (column-beam-slab moment frame + the SAME eccentric core)
===================================================================================

What this file is
-----------------
The OpenSees (OpenSeesPy) nonlinear model of the proposed alternative: the same building with
500 x 800 mm beams on every column line, so that beams and columns form a moment frame (a
second lateral load path and an alternative gravity load path), and a 250 mm slab spanning
between the beams.  Everything else - geometry, columns, the eccentric core in the same place,
its walls and link beams, materials, loads - is identical to the as-built model (proposal
Part 4: "isolate framing configuration as the principal experimental variable").

Proposal Sec. 3.2 "Proposed Model" table, as used here
------------------------------------------------------
    building height 137 m, 33 storeys (6 m ground storey, ~4.09 m above)
    concrete 5000 - 8000 psi; core 17 m x 17 m centred on the rear edge, 250 mm walls
    coupling (link) beams 250 x 500 mm; slab 250 mm
    columns 1400 x 1400 mm -> 800 mm circular; BEAMS 500 (width) x 800 (depth) mm

What this file adds to the shared building (sao/building_common.py)
-------------------------------------------------------------------
Beams.  Each span along a column line is a 500 x 800 T-beam (slab flange, ACI cracked
stiffness 0.35 EIg) with plastic hinges at both ends (ASCE 41-17 Table 10-7: plastic rotation
0.025 before strength loss, 20 % residual).  Top / bottom steel comes from the design pass.
Beams frame directly into the column nodes (moment connections, no punching).  Where a beam
meets the 250 mm core wall at right angles it can transfer only 25 % of its moment capacity
(out-of-plane wall bending), but its full shear - this is the path along which load can be
redistributed between the core and the columns.

Deficiency variants - identical to the as-built model so both see the same conditions
------------------------------------------------------------------------------------
    D1  core-wall concrete below the specified 500 ksc        (f'c = 0.70 x specified)
    D2  link (coupling) beam bars embedded less than required  (le/ld = 0.50, anchorage pull-out)
    D3  core wall thickness reduced 300 -> 250 mm
    D4  design not compliant with the regulation (under-designed walls)
Variant names are "B-" + the deficiencies that are switched on:
    B-REF          no deficiencies
    B-D1 ... B-D4  individual deficiencies
    B-D1D2 ...     combinations
    B-D1D2D3D4     all four (the as-built deficiencies applied to the proposed framing)
Run this file to print the 16 variants and check the model.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sao import config as C                                   # noqa: E402
from sao.building_common import SAOBuildingBase               # noqa: E402
from sao.capacities import beam_section                       # noqa: E402

MODEL_LABEL = "Phase 2B - Proposed column-beam-slab frame + eccentric core"


class ProposedBeamSlabModel(SAOBuildingBase):
    CONFIG = "B"
    MODEL_NAME = MODEL_LABEL
    SLAB_T = C.SLAB_T_BEAM                                                   # 250 mm slab
    BEAM_STEM_W = C.BEAM_B * (C.BEAM_H - C.SLAB_T_BEAM) * C.GAMMA_RC         # 6.6 kN/m

    def _end_node(self, i, end):
        """Beams connect directly to the column nodes and to the core-wall attachment nodes."""
        kind, key = end
        return self.Nc[(i, key)] if kind == "col" else self.W[(i, key)]

    def _floor_system(self):
        segs = self._build_segments()
        for i in range(1, C.N_STORY + 1):
            zone = self.design["beam_zone"](i)
            for sg in segs:
                ni, nj = self._end_node(i, sg["a"]), self._end_node(i, sg["b"])
                As_top, As_bot = self.design["beam_As"][zone]["perim" if sg["perim"] else "int"]
                pr = beam_section(As_top, As_bot)
                Mp_i = Mp_j = pr["My_pos"]
                Mn_i = Mn_j = pr["My_neg"]
                if sg["a"][0] == "core":            # beam end at a thin core wall
                    Mp_i, Mn_i = 0.25 * Mp_i, 0.25 * Mn_i
                if sg["b"][0] == "core":
                    Mp_j, Mn_j = 0.25 * Mp_j, 0.25 * Mn_j
                tag = self.ele()
                self.hinged_member(tag, ni, nj, pr["E"], pr["A"], pr["Iy"], pr["Iz"], pr["J"], pr["lp"],
                                   Mp_i, Mn_i, Mp_j, Mn_j, pr["th_p"], pr["th_pc"], pr["res"], (0.8, 0.3))
                self.floor_ele[(i, sg["id"])] = tag
                self.floor_info[(i, sg["id"])] = dict(My_neg=pr["My_neg"], My_pos=pr["My_pos"], L=sg["L"],
                                                      Vn=pr["Vn"], As_top=As_top, As_bot=As_bot)


# ----------------------------------------------------------------------------------------------
# Deficiency variants for the proposed model (individual + every combination = 16 models)
# ----------------------------------------------------------------------------------------------
VARIANTS = {v.name: v for v in C.all_deficiency_variants("B")}
WITH_AS_BUILT_DEFICIENCIES = VARIANTS["B-D1D2D3D4"]
REFERENCE = VARIANTS["B-REF"]


def build(variant="B-D1D2D3D4", design=None, mode="nonlinear"):
    """Build one proposed-model variant in the OpenSees domain and return the model object."""
    from sao.design import load_design
    v = VARIANTS[variant] if isinstance(variant, str) else variant
    return ProposedBeamSlabModel(v, design or load_design(), mode).build()


if __name__ == "__main__":
    print(MODEL_LABEL)
    print(f"{'variant':14s} {'group':12s} description")
    for name, v in VARIANTS.items():
        print(f"{name:14s} {v.group:12s} {v.description}")
    m = build("B-D1D2D3D4")
    print(m.summary())
