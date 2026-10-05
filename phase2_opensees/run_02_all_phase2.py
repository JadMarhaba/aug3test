"""
STEP 2 - run the Phase 2A (as-built) and Phase 2B (proposed) analyses together, interleaved,
so all CPU cores stay busy.  Same work as running the two phase scripts one after the other:
  1. alternate-load-path cases for both models: sudden core removal + pushdown
  2. collapse-intensity searches for all 32 variants (+ GM2/GM3 for key variants, + severity
     a D1 / D2 severity ladder at the real 2025 shaking for both framings, run first),
     with the pushovers filling idle workers
"""
import sys
import itertools
from sao.jobqueue import run_jobs
from sao.ida import run_all
import run_phase2A_asbuilt_flatslab as A
import run_phase2B_proposed_beamslab as B


def zip_lists(a, b):
    return [x for pair in itertools.zip_longest(a, b) for x in pair if x is not None]


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    run_jobs(zip_lists(A.removal_jobs("A") + A.pushdown_jobs("A"), B.removal_jobs("B") + B.pushdown_jobs("B")),
             workers=w)
    ha, hb = A.hunts("A"), B.hunts("B")
    order = zip_lists(ha, hb)
    # severity ladder at the real 2025 shaking runs first (same severities in both framings)
    sev = zip_lists(A.severity_jobs("A"), B.severity_jobs("B"))
    run_all(order, zip_lists(A.pushover_jobs("A"), B.pushover_jobs("B")), workers=w, priority_jobs=sev)
