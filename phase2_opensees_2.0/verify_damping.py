"""VERIFICATION (both models) - free-vibration check of the Rayleigh damping.
Push the building statically into its mode-1 shape (small, elastic), release, and measure the
logarithmic decrement of the mode-1 modal coordinate (relative to the gravity state).
Usage: python3 verify_damping.py A-REF   (or B-REF)
Result (fixed code): A-REF 2.6 %, B-REF 2.4 % over full cycles; target 2.5 %."""
import sys, math, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import openseespy.opensees as ops
from sao.design import load_design
from sao.analysis import Analyzer
from sao.runner import variant_from_name

name = sys.argv[1]
an = Analyzer(variant_from_name(name), load_design())
an.gravity()
T = an.modal(6)
print(name, "periods", [round(t, 2) for t in T], flush=True)
nodes = [n for n in an.b.node_mass]
ug = {n: (ops.nodeDisp(n, 1), ops.nodeDisp(n, 2)) for n in nodes}
m = np.array([an.b.node_mass[n] for n in nodes])
phi = np.array([[ops.nodeEigenvector(n, 1, d) for d in (1, 2)] for n in nodes])
# static push in the mode-1 shape: F = M*phi, scaled to ~20 mm max displacement
w1 = 2 * math.pi / T[0]
scale = 0.02 / np.abs(phi).max()
ops.timeSeries("Constant", 77)
ops.pattern("Plain", 77, 77)
for n, mi, ph in zip(nodes, m, phi):
    ops.load(n, mi * w1**2 * ph[0] * scale, mi * w1**2 * ph[1] * scale, 0, 0, 0, 0)
an._setup()
ops.integrator("LoadControl", 0.1)
ops.analysis("Static")
print("static ok", ops.analyze(10), flush=True)
ops.remove("loadPattern", 77)
ops.setTime(0.0)
an._setup(tol=1e-4, it=30)
an.set_damping(T[0], max(T[0] / 8.0, 0.35))
print("a0, a1 =", an.damp, flush=True)
ops.integrator("Newmark", 0.5, 0.25)
ops.analysis("Transient")
den = np.sum(m * (phi**2).sum(1))
phi2 = np.array([[ops.nodeEigenvector(n, 2, d) for d in (1, 2)] for n in nodes])
den2 = np.sum(m * (phi2**2).sum(1))
q2s = []
def q():
    u = np.array([[ops.nodeDisp(n, d) - ug[n][d - 1] for d in (1, 2)] for n in nodes])
    q2s.append(np.sum(m * (u * phi2).sum(1)) / den2)
    return np.sum(m * (u * phi).sum(1)) / den
qs, ts = [q()], [0.0]
dt = 0.025
for k in range(int(3.2 * T[0] / dt)):
    if ops.analyze(1, dt) != 0:
        print("fail", k); break
    qs.append(q()); ts.append(ops.getTime())
qs = np.array(qs)
np.savez(f"results/damping_check_{name}.npz", t=ts, q=qs, q2=np.array(q2s))
print("q range", qs.min(), qs.max(), " q2 range", min(q2s), max(q2s))
pk = [i for i in range(1, len(qs) - 1) if abs(qs[i]) >= abs(qs[i-1]) and abs(qs[i]) >= abs(qs[i+1])]
amps = np.abs(qs[[0] + pk])
print("peak |q|:", np.round(amps, 5))
# half-cycle log decrement
d = [math.log(amps[i] / amps[i+1]) for i in range(len(amps) - 1)]
zeta = [x / math.pi for x in d]   # per half cycle: delta_half = pi*zeta
print("zeta per half-cycle:", np.round(zeta, 4), " mean", round(float(np.mean(zeta)), 4))
w2 = 2 * math.pi / max(T[0] / 8.0, 0.35)
a0, a1 = an.damp
print("theoretical zeta at T1 = a0/(2w1)+a1*w1/2 =", round(a0 / (2 * w1) + a1 * w1 / 2, 4))
