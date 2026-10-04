"""
SHARED - runs many analysis jobs in parallel (one OpenSees process per job, N at a time) and
skips jobs whose result file already exists, so a long batch can be stopped and resumed.
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from .runner import job_id, RES, ROOT


def done(job):
    return os.path.exists(os.path.join(RES, job_id(job) + ".json"))


def run_jobs(jobs, workers=4, timeout=4 * 3600):
    todo = [j for j in jobs if not done(j)]
    print(f"{len(jobs)} jobs, {len(todo)} to run, {workers} workers", flush=True)

    def one(job):
        t0 = time.time()
        try:
            p = subprocess.run([sys.executable, "-m", "sao.runner", json.dumps(job)], cwd=ROOT,
                               capture_output=True, text=True, timeout=timeout)
            tail = (p.stdout.strip().splitlines() or ["?"])[-1]
            if p.returncode != 0:
                tail += " | " + " ".join(p.stderr.strip().splitlines()[-3:])
        except subprocess.TimeoutExpired:
            tail = "TIMEOUT " + job_id(job)
        print(f"[{time.strftime('%H:%M:%S')}] {tail}  ({time.time() - t0:.0f}s)", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, todo))
