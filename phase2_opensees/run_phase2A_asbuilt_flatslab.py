"""
PHASE 2A - AS-BUILT FLAT-SLAB MODEL: run all nonlinear analyses
================================================================
Model file : phase2A_asbuilt_flatslab_model.py   (variants A-REF ... A-D1D2D3D4)

Analyses (proposal 4.3 "Proposed Experimentation"):
  1. Pushover in X and Y for all 16 deficiency variants
       -> initial yielding, failure sequence, lateral capacity, core vs column share
  2. Collapse-intensity search (record GM1) for all 16 variants: response histories at the
     2025-event level (SF = 1.0) and then at increasing SF until collapse (sao/ida.py)
       -> which deficiency (individually or in combination) produces global instability
  3. The same collapse search with records GM2 and GM3 for the no-deficiency reference and
     the all-four-deficiency variant (record-to-record variability)
  4. (step 2 doubles as the incremental dynamic analysis: SF vs peak drift up to collapse)
  4b. Severity calibration: the as-built condition (all four deficiencies) with weaker wall
     concrete (f'c x 0.60 / 0.50) and shorter link-beam embedment (le/ld = 0.30), searched for
     the intensity at which it collapses - same inputs for both framings
  5. Pushdown (quasi-static withdrawal) of one core pier at a time + sudden removal of lower
     core piers under gravity (scenarios S1-S5) for A-REF and
       A-D1D2D3D4 -> load redistribution to the column-slab system, punching cascade

Results are written to results/<analysis>/A-*.json; re-running skips finished jobs.
Usage:  python3 run_phase2A_asbuilt_flatslab.py [workers]
"""
import sys
from sao import config as C
from sao.ida import Hunt, run_all
from sao.jobqueue import run_jobs
from sao.runner import REMOVAL_SCENARIOS, PUSHDOWN_SCENARIOS

CONFIG = "A"


def removal_jobs(config=CONFIG):
    """Sudden removal of lower core piers under gravity (alternate load path)."""
    return [{"kind": "removal", "variant": f"{config}-{d}", "scenario": s}
            for d in ("D1D2D3D4", "REF") for s in REMOVAL_SCENARIOS]


def pushdown_jobs(config=CONFIG):
    """Quasi-static withdrawal of one core pier's support: how much of its load the rest of
    the structure can pick up, and through which members (link beams vs floor framing)."""
    return [{"kind": "pushdown", "variant": f"{config}-{d}", "scenario": s}
            for d in ("REF", "D1D2D3D4") for s in PUSHDOWN_SCENARIOS]


def pushover_jobs(config=CONFIG):
    return [{"kind": "pushover", "variant": v.name, "dir": d}
            for d in (2, 1) for v in C.all_deficiency_variants(config)]


# Severity calibration: the investigation confirmed D1 and D2 but did not publish how bad they
# were.  These variants keep all four deficiencies and vary the two unknown severities; the
# same values are applied to both framings.  Names: _fc = wall f'c / specified,
# _le = provided / required link-beam bar embedment.
CALIBRATION = [dict(fc_ratio=0.50, embed_ratio=0.30), dict(fc_ratio=0.50), dict(embed_ratio=0.30),
               dict(fc_ratio=0.60)]


def calibration_hunts(config=CONFIG):
    return [Hunt(C.Variant(config=config, D1=True, D2=True, D3=True, D4=True, **kw).name, "GM1")
            for kw in CALIBRATION]


def hunts(config=CONFIG):
    """Collapse searches, most important first: all four deficiencies, reference, singles,
    pairs, triples (record GM1); then GM2 / GM3 for all-four and reference."""
    order = sorted(C.all_deficiency_variants(config),
                   key=lambda v: (0 if len(v.deficiencies) == 4 else 1 if not v.deficiencies else 2,
                                  len(v.deficiencies)))
    H = [Hunt(v.name, "GM1") for v in order]
    H += [Hunt(f"{config}-{d}", g) for g in ("GM2", "GM3") for d in ("D1D2D3D4", "REF")]
    return H


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    run_jobs(removal_jobs() + pushdown_jobs(), workers=w)
    H = hunts()
    run_all(H[:2] + calibration_hunts() + H[2:], pushover_jobs(), workers=w)
