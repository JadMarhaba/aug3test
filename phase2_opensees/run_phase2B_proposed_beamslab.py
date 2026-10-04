"""
PHASE 2B - PROPOSED BEAM-SLAB MODEL: run all nonlinear analyses
==================================================================
Model file : phase2B_proposed_beamslab_model.py   (variants B-REF ... B-D1D2D3D4)

Analyses (proposal 4.4 - identical loading to Phase 2A):
  1. Pushover in X and Y for all 16 deficiency variants
       -> initial yielding, failure sequence, lateral capacity, core vs column share
  2. Collapse-intensity search (record GM1) for all 16 variants: response histories at the
     2025-event level (SF = 1.0) and then at increasing SF until collapse (sao/ida.py)
       -> does failure propagate differently from the flat slab under the same deficiencies?
  3. The same collapse search with records GM2 and GM3 for the no-deficiency reference and
     the all-four-deficiency variant (record-to-record variability)
  4. (step 2 doubles as the incremental dynamic analysis: SF vs peak drift up to collapse)
  5. Sudden removal of lower core piers under gravity (scenarios S1-S5) for B-REF and
       B-D1D2D3D4 -> how much load the beams / columns pick up; stable state or not

Results are written to results/<analysis>/B-*.json; re-running skips finished jobs.
Usage:  python3 run_phase2B_proposed_beamslab.py [workers]
"""
import sys
from sao import config as C
from sao.ida import Hunt, run_all
from sao.jobqueue import run_jobs
from sao.runner import REMOVAL_SCENARIOS

CONFIG = "B"


def removal_jobs(config=CONFIG):
    """Sudden removal of lower core piers under gravity (alternate load path)."""
    return [{"kind": "removal", "variant": f"{config}-{d}", "scenario": s}
            for d in ("D1D2D3D4", "REF") for s in REMOVAL_SCENARIOS]


def pushover_jobs(config=CONFIG):
    return [{"kind": "pushover", "variant": v.name, "dir": d}
            for d in (2, 1) for v in C.all_deficiency_variants(config)]


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
    run_jobs(removal_jobs(), workers=w)
    run_all(hunts(), pushover_jobs(), workers=w)
