"""
VERIFICATION (shared) - is the beam-slab's earlier collapse real or numerical?

Re-runs the beam-slab collapse cases with a finer time step and solver-fallback logging, and runs
the matching as-built case at the same intensity, then resumes the main Phase 2 batch.
"""
import subprocess, sys
from sao.jobqueue import run_jobs

JOBS = [
    {"kind": "nlth", "variant": "B-D1D2D3D4_fc0.50_le0.30", "gm": "GM1", "sf": 2.5, "dt": 0.01},   # finer dt
    {"kind": "nlth", "variant": "B-D1D2D3D4_fc0.50_le0.30", "gm": "GM1", "sf": 2.5, "dt": 0.02},   # logged repeat
    {"kind": "nlth", "variant": "A-D1D2D3D4_fc0.50_le0.30", "gm": "GM1", "sf": 2.5, "dt": 0.025},  # matching as-built
    {"kind": "nlth", "variant": "B-D1D2D3D4", "gm": "GM1", "sf": 3.75, "dt": 0.01},                # documented, finer dt
]

if __name__ == "__main__":
    run_jobs(JOBS, workers=4)
    subprocess.Popen([sys.executable, "run_02_all_phase2.py", "4"], stdout=open("results/batch.log", "a"),
                     stderr=subprocess.STDOUT)
