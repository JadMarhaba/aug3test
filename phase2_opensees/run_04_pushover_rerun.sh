#!/bin/sh
# Re-run all 64 pushovers with the strengthened pushover solver step (Analyzer._push_step),
# after the main batch (run_02_all_phase2.py) has finished.  The first pushover set, which
# stopped early on solver non-convergence in many cases, is kept in results/old/.
cd "$(dirname "$0")"
while pgrep -f run_02_all_phase2 > /dev/null; do sleep 60; done
[ -d results/pushover ] && mv results/pushover results/old/pushover_v1_weak_solver
python3 -u -c "
from sao.jobqueue import run_jobs
import run_phase2A_asbuilt_flatslab as A, run_phase2B_proposed_beamslab as B
from run_02_all_phase2 import zip_lists
run_jobs(zip_lists(A.pushover_jobs('A'), B.pushover_jobs('B')), workers=4)
"
