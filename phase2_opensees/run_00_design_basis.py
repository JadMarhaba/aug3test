"""
STEP 0 (SHARED BY BOTH MODELS) - design pass -> results/design.json

The proposal does not give reinforcement, so wall / link-beam / beam steel is sized here from an
elastic response-spectrum analysis of each model (DPT 1301/1302-61 Bangkok spectrum, R = 5,
I = 1.25).  Compliant walls get the ACI 318-19 amplified shear design; the D4 (non-compliant)
walls get the unamplified design.  Output is read by both model files.
"""
import json, sys, time
from sao.design import run_design

if __name__ == "__main__":
    t0 = time.time()
    out = run_design("results/design.json")
    print("periods A", [round(x, 2) for x in out["periods_A"][:6]])
    print("periods B", [round(x, 2) for x in out["periods_B"][:6]])
    print("ELF A", {k: round(v, 3) for k, v in out["elf_A"].items()}, "scale", round(out["rsa_scale_A"], 2))
    print("ELF B", {k: round(v, 3) for k, v in out["elf_B"].items()}, "scale", round(out["rsa_scale_B"], 2))
    for k in ("compliant", "noncompliant"):
        for p in "RMF":
            print(k, p, {z: (round(d["rho_v"] * 100, 2), round(d["rho_h"] * 100, 2)) for z, d in out["walls"][k][p].items()})
    print("CB As mm2", {z: round(v) for z, v in out["cb_As"].items()}, "Vu", {z: round(v) for z, v in out["cb_Vu"].items()})
    print("beam As", out["beam_As"])
    print("time", round(time.time() - t0, 1))
