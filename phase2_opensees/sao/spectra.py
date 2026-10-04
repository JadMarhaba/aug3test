"""
SHARED BY BOTH MODELS - response spectra (5 % damping, units of g).

DPT 1301/1302-61 Bangkok basin spectrum: reconstructed for the Chatuchak district from the
published description of the standard (Poovarodom et al. 2018: MCE Sa(1 s) = 0.30 g, DBE =
2/3 MCE = 0.20 g; plateau centred near 1 s with very little decay between 1 and 2 s).
The official zone table should be substituted when available.

2025 Mandalay event in Bangkok: reconstructed target from reported station data
(Ornthammarath et al. 2025): PGA ~ 0.02 g, PGV ~ 10 cm/s, amplification bands at 1-3 s and
5-7 s.  This is the "event-level" spectrum (scale factor SF = 1.0) for the nonlinear analyses.
"""
import numpy as np

_DPT_T = np.array([0.0, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0])
_DPT_SA = np.array([0.12, 0.20, 0.27, 0.30, 0.30, 0.29, 0.26, 0.22, 0.18, 0.13, 0.10, 0.085, 0.06, 0.045])

_EV_T = np.array([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0])
_EV_SA = np.array([0.020, 0.024, 0.030, 0.036, 0.048, 0.060, 0.075, 0.080, 0.075, 0.065, 0.050, 0.040,
                   0.028, 0.024, 0.022, 0.019, 0.014, 0.008])


def _interp(T, Tt, St):
    T = np.atleast_1d(np.asarray(T, dtype=float))
    out = np.interp(T, Tt, St)
    beyond = T > Tt[-1]
    out[beyond] = St[-1] * (Tt[-1] / T[beyond]) ** 2     # constant displacement beyond 10 s
    return out


def dpt_mce(T):
    return _interp(T, _DPT_T, _DPT_SA)


def dpt_dbe(T):
    return 2.0 / 3.0 * dpt_mce(T)


def event_2025(T):
    return _interp(T, _EV_T, _EV_SA)


def sdof_spectrum(acc_g, dt, periods, zeta=0.05):
    """Pseudo-acceleration spectrum (g) by Newmark average acceleration (exact for linear)."""
    periods = np.atleast_1d(periods)
    ag = np.asarray(acc_g) * 9.81
    out = np.zeros(len(periods))
    for k, T in enumerate(periods):
        if T <= 0:
            out[k] = np.max(np.abs(acc_g))
            continue
        w = 2 * np.pi / T
        m, c, kk = 1.0, 2 * zeta * w, w * w
        # Newmark beta=1/4 gamma=1/2
        a1 = m / (0.25 * dt * dt) + c * 0.5 / (0.25 * dt)
        a2 = m / (0.25 * dt) + c * (0.5 / 0.25 - 1)
        a3 = m * (1 / (2 * 0.25) - 1) + c * dt * (0.5 / (2 * 0.25) - 1)
        kh = kk + a1
        u = v = 0.0
        a = -ag[0]
        umax = 0.0
        for i in range(1, len(ag)):
            p = -m * ag[i] + a1 * u + a2 * v + a3 * a
            un = p / kh
            vn = 0.5 / (0.25 * dt) * (un - u) + (1 - 0.5 / 0.25) * v + dt * (1 - 0.5 / (2 * 0.25)) * a
            an = (un - u) / (0.25 * dt * dt) - v / (0.25 * dt) - (1 / (2 * 0.25) - 1) * a
            u, v, a = un, vn, an
            if abs(u) > umax:
                umax = abs(u)
        out[k] = umax * w * w / 9.81
    return out


def sdof_spectrum_fast(acc_g, dt, periods, zeta=0.05):
    """Vectorised over periods (same algorithm as sdof_spectrum)."""
    periods = np.atleast_1d(np.asarray(periods, dtype=float))
    ag = np.asarray(acc_g) * 9.81
    w = 2 * np.pi / periods
    c = 2 * zeta * w
    kk = w * w
    b, g = 0.25, 0.5
    a1 = 1 / (b * dt * dt) + c * g / (b * dt)
    a2 = 1 / (b * dt) + c * (g / b - 1)
    a3 = (1 / (2 * b) - 1) + c * dt * (g / (2 * b) - 1)
    kh = kk + a1
    u = np.zeros_like(w)
    v = np.zeros_like(w)
    a = np.full_like(w, -ag[0])
    umax = np.zeros_like(w)
    for i in range(1, len(ag)):
        p = -ag[i] + a1 * u + a2 * v + a3 * a
        un = p / kh
        vn = g / (b * dt) * (un - u) + (1 - g / b) * v + dt * (1 - g / (2 * b)) * a
        an = (un - u) / (b * dt * dt) - v / (b * dt) - (1 / (2 * b) - 1) * a
        u, v, a = un, vn, an
        np.maximum(umax, np.abs(u), out=umax)
    return umax * w * w / 9.81
