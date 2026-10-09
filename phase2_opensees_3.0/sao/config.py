"""
SHARED BY BOTH MODELS - parameters of the State Audit Office (SAO) building, Phase 2 models,
and the definition of the deficiency variants (D1-D4, individually and in combination).

Units: kN, m, s, tonne (t).  Stresses in kPa (1 MPa = 1000 kPa).

Every number here is either taken from the proposal (Section 3.2 tables, Figs 1.2/3.1/3.2),
from public reporting of the official investigation, or is an explicitly stated modelling
assumption.  Assumptions are marked "ASSUMED".
"""
from dataclasses import dataclass, field, replace, asdict
import itertools
import math

G = 9.81  # m/s2
MPA = 1000.0  # kPa per MPa

# ----------------------------------------------------------------------------------------
# Geometry (proposal Sec. 3.2 and Fig. 1.2)
# ----------------------------------------------------------------------------------------
N_STORY = 33                     # 33 stories
H_GROUND = 6.0                   # 6 m ground storey
H_TOTAL = 137.0                  # 137 m total height
H_TYP = (H_TOTAL - H_GROUND) / (N_STORY - 1)   # ~4.09 m ("~4 m for the rest")


def level_z(i):
    """Elevation of floor level i (0 = base)."""
    if i <= 0:
        return 0.0
    return H_GROUND + (i - 1) * H_TYP


def story_h(s):
    """Height of story s (1..N_STORY), between level s-1 and s."""
    return H_GROUND if s == 1 else H_TYP


PLAN = 39.0                      # 39 m x 39 m building grid (Google Earth, 1,525 m2)
# Column lines.  Exterior columns sit on the slab edge; interior lines ASSUMED (Fig. 1.2 N.T.S.)
GRID = [0.0, 5.5, 14.75, 24.25, 33.5, 39.0]

# Core: 17 m x 17 m, centred in x on the rear (y = 39) edge.  Two cells (lift/stair shafts)
# split by a middle wall; 4 openings (2 per side wall) bridged by coupling (link) beams.
CORE = dict(
    x0=11.0, x1=28.0,          # side walls (centrelines)
    y0=22.0, y1=39.0,          # front wall / rear wall
    ymid=30.5,                 # middle (cross) wall
    open_front=(25.5, 27.0),   # opening in side walls, front cell (1.5 m clear, ASSUMED)
    open_rear=(34.0, 35.5),    # opening in side walls, rear cell
)
CB_DEPTH = 0.50                  # coupling (link) beam depth 500 mm (proposal table)

# ----------------------------------------------------------------------------------------
# Column layout: 26 columns per floor (Fig. 1.2 / Fig. 3.2 caption)
# ----------------------------------------------------------------------------------------

def _in_core(x, y):
    c = CORE
    return (c["x0"] - 1e-6 <= x <= c["x1"] + 1e-6) and (c["y0"] - 1e-6 <= y <= c["y1"] + 1e-6)


def column_points():
    """Return list of dicts {x, y, pos} for the 26 columns.  pos = 'interior'|'edge'."""
    pts = []
    for x in GRID:
        for y in GRID:
            corner = (x in (0.0, PLAN)) and (y in (0.0, PLAN))
            if corner:
                continue                 # building corners are cantilevered slab (Fig. 1.2)
            if _in_core(x, y):
                continue                 # absorbed by the core
            edge = x in (0.0, PLAN) or y in (0.0, PLAN)
            pts.append(dict(x=x, y=y, pos="edge" if edge else "interior"))
    assert len(pts) == 26, len(pts)
    return pts


# Column size schedule (proposal: 1400x1400 first three stories, 800 mm circular floor 29-roof;
# intermediate steps ASSUMED).
def column_section(story):
    if story <= 3:
        return ("rect", 1.40)
    if story <= 12:
        return ("rect", 1.20)
    if story <= 20:
        return ("rect", 1.00)
    if story <= 28:
        return ("rect", 0.90)
    return ("circ", 0.80)


def column_fc(story):
    """Column concrete (MPa): 8000 psi low, 5000 psi top (proposal 5000-8000 psi)."""
    if story <= 11:
        return 55.0
    if story <= 22:
        return 45.0
    return 35.0


def column_rho(story):
    """Longitudinal reinforcement ratio of columns (ASSUMED, gravity design)."""
    if story <= 6:
        return 0.020
    if story <= 15:
        return 0.015
    return 0.010


# ----------------------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------------------
FY_NOM = 490.0          # MPa, SD50 main bars (Thai TIS 24)
FY_EXP = 1.10 * FY_NOM  # expected yield used in nonlinear models
FYT_EXP = 1.10 * 390.0  # SD40 ties / horizontal wall bars, expected
ES = 200000.0           # MPa
FC_SLAB = 35.0          # MPa (5000 psi) slab / beams
WALL_FC_SPEC_LOW = 49.0     # MPa, 500 ksc required (official finding), stories 1-16
WALL_FC_SPEC_HIGH = 40.0    # MPa, upper stories (ASSUMED)
WALL_SPLIT_STORY = 16


def wall_fc_spec(story):
    return WALL_FC_SPEC_LOW if story <= WALL_SPLIT_STORY else WALL_FC_SPEC_HIGH


def Ec(fc_mpa):
    return 4700.0 * math.sqrt(fc_mpa)  # MPa


# ----------------------------------------------------------------------------------------
# Slabs and beams
# ----------------------------------------------------------------------------------------
SLAB_T_FLAT = 0.25       # VERSION 2.0: as-built flat slab thinned to 250 mm (same as the beam-slab model)
SLAB_T_BEAM = 0.25       # proposed beam-slab model (proposal)
BEAM_B, BEAM_H = 0.50, 0.80   # proposed beams 500 x 800 (proposal)
PT_PRECOMP = 1.5         # MPa average precompression in PT slab (ASSUMED, typical 1-2.5 MPa)
# VERSION 3.0 - effective stiffness for the low-intensity (2025-level) shaking, same rule in both
# models: link (coupling) beams 0.5 EI (v2.0: 0.20); the post-tensioned flat slab (as-built only)
# stays uncracked under the PT precompression -> effective-width factor beta = 1.0 (v2.0: 0.5);
# the beam-slab's beams are ordinary (non-PT) RC, cracked by gravity -> unchanged 0.35 EI.
CB_EI_FACTOR = 0.50
PT_SLAB_BETA = 1.00

# ----------------------------------------------------------------------------------------
# Loads (kPa).  Two states:
#   'event'  : expected loads on 28 Mar 2025 (structure topped out, MEP/facade in progress)
#   'design' : code design loads (used only by the design pass)
# ----------------------------------------------------------------------------------------
GAMMA_RC = 24.0          # kN/m3
LOADS = {
    "event": dict(sdl=0.75, live=0.50, facade=0.75),    # ASSUMED construction-stage loads
    "design": dict(sdl=1.50, live=2.50, facade=1.50),   # office LL 250 kg/m2 (Thai MR)
}

# ----------------------------------------------------------------------------------------
# Deficiencies (proposal Sec. 1.3, official findings of 30 June 2025)
# ----------------------------------------------------------------------------------------
DEFICIENCY_INFO = {
    "D1": "D1 core-wall concrete below the specified 500 ksc (f'c x 0.70)",
    "D2": "D2 link-beam bar embedment shorter than required (le/ld = 0.5)",
    "D3": "D3 core walls 250 mm instead of 300 mm",
    "D4": "D4 non-compliant design (unamplified wall shear design, unconfined boundaries)",
}


@dataclass(frozen=True)
class Variant:
    """One model variant = framing configuration x set of documented deficiencies.

    config : 'A' = Phase 2A as-built flat slab   (phase2A_asbuilt_flatslab_model.py)
             'B' = Phase 2B proposed beam-slab    (phase2B_proposed_beamslab_model.py)
    D1..D4 : True = that documented deficiency is present (see DEFICIENCY_INFO)

    Naming: "<config>-<deficiencies on>", e.g.
        A-REF       as-built framing, no deficiencies (code-compliant reference)
        A-D2        as-built framing, only the short link-beam embedment
        A-D1D3      as-built framing, low wall concrete + thin walls
        A-D1D2D3D4  as-built framing with all four = the as-built condition
        B-...       the same for the proposed beam-slab framing
    """
    config: str = "A"
    D1: bool = False
    D2: bool = False
    D3: bool = False
    D4: bool = False
    fc_ratio: float = 0.70            # D1 severity: in-situ / specified wall f'c (ASSUMED 350/500 ksc)
    embed_ratio: float = 0.50         # D2 severity: provided / required development length (ASSUMED)
    gamma_axial: float = 0.0          # 0 -> axial-load-dependent default (see capacities.py)
    load_state: str = "event"
    damping: float = 0.025

    @property
    def deficiencies(self):
        return [d for d in ("D1", "D2", "D3", "D4") if getattr(self, d)]

    @property
    def code(self):
        return "".join("1" if getattr(self, d) else "0" for d in ("D1", "D2", "D3", "D4"))

    @property
    def name(self):
        n = f"{self.config}-{''.join(self.deficiencies) or 'REF'}"
        if self.D1 and abs(self.fc_ratio - 0.70) > 1e-9:
            n += f"_fc{self.fc_ratio:.2f}"
        if self.D2 and abs(self.embed_ratio - 0.50) > 1e-9:
            n += f"_le{self.embed_ratio:.2f}"
        return n

    @property
    def group(self):
        k = len(self.deficiencies)
        return ["reference", "individual", "pair", "triple", "all four"][k]

    @property
    def description(self):
        frame = "As-built flat slab" if self.config == "A" else "Proposed beam-slab"
        if not self.deficiencies:
            return f"{frame}: no deficiencies (300 mm walls, specified concrete, full embedment, compliant design)"
        txt = []
        for d in self.deficiencies:
            t = DEFICIENCY_INFO[d]
            if d == "D1":
                t = t.replace("(f'c x 0.70)", f"(f'c x {self.fc_ratio:.2f})")
            if d == "D2":
                t = t.replace("(le/ld = 0.5)", f"(le/ld = {self.embed_ratio:.2f})")
            txt.append(t)
        return f"{frame}: " + "; ".join(txt)

    @property
    def label(self):
        frame = "Flat-slab" if self.config == "A" else "Beam-slab"
        return f"{frame} [{'+'.join(self.deficiencies) if self.deficiencies else 'no deficiency'}]"

    @property
    def wall_t(self):
        return 0.25 if self.D3 else 0.30

    def wall_fc(self, story):
        f = wall_fc_spec(story)
        return f * self.fc_ratio if self.D1 else f

    def to_dict(self):
        d = asdict(self)
        d.update(name=self.name, label=self.label, group=self.group, description=self.description)
        return d


def all_deficiency_variants(config):
    """The 16 variants of one framing configuration: reference, the 4 deficiencies
    individually, the 6 pairs, the 4 triples and all four together (proposal Part 4)."""
    out = []
    for k in range(5):
        for combo in itertools.combinations(("D1", "D2", "D3", "D4"), k):
            out.append(Variant(config=config, **{d: True for d in combo}))
    return out


