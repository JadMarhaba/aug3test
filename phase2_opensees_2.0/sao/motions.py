"""
SHARED BY BOTH MODELS - ground motions (identical loading for Phase 2A and Phase 2B).

No Bangkok strong-motion records of the 28 March 2025 event are publicly downloadable, so
bidirectional records are synthesised and spectrally matched to the reconstructed event
spectrum (spectra.event_2025: PGA ~0.02 g, PGV ~10 cm/s, amplification at 1-3 s and 5-7 s):

  1. random white noise x a long-duration envelope (10 s build-up, 50 s strong shaking,
     40 s decay - long-period far-field surface waves in the soft-clay basin);
  2. iterative frequency-domain spectral matching to the target (20 iterations);
  3. high-pass taper 0.07-0.10 Hz (removes T > 10-14 s, beyond the target) and polynomial
     baseline correction so that velocity / displacement do not drift.

Three independent pairs (GM1-GM3) give record-to-record variability.  Scale factor SF = 1.0 is
the estimated 2025 event level in Bangkok; larger SF are used for incremental dynamic analysis.
"""
import numpy as np
from .spectra import event_2025, sdof_spectrum_fast

DT = 0.01
DURATION = 100.0


def envelope(t, t_rise=10.0, t_strong=60.0, t_end=DURATION):
    e = np.ones_like(t)
    r = t < t_rise
    e[r] = (t[r] / t_rise) ** 2
    d = t > t_strong
    e[d] = np.exp(-3.0 * (t[d] - t_strong) / (t_end - t_strong))
    return e


def _highpass(x, dt, f1=0.07, f2=0.10):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), dt)
    w = np.ones_like(f)
    w[f <= f1] = 0.0
    m = (f > f1) & (f < f2)
    w[m] = 0.5 * (1 - np.cos(np.pi * (f[m] - f1) / (f2 - f1)))
    return np.fft.irfft(X * w, len(x))


def synthesize(seed, target=event_2025, dt=DT, duration=DURATION, n_iter=20):
    rng = np.random.default_rng(seed)
    n = int(round(duration / dt))
    t = np.arange(n) * dt
    env = envelope(t, t_end=duration)
    x = rng.standard_normal(n) * env
    x = _highpass(x, dt)
    periods = np.logspace(np.log10(0.05), np.log10(10.0), 60)
    tgt = target(periods)
    f = np.fft.rfftfreq(n, dt)
    for _ in range(n_iter):
        sa = sdof_spectrum_fast(x, dt, periods)
        ratio = tgt / np.maximum(sa, 1e-12)
        fr, rr = 1.0 / periods[::-1], ratio[::-1]
        rf = np.interp(f, fr, rr, left=rr[0], right=rr[-1])
        x = np.fft.irfft(np.fft.rfft(x) * rf, n)
        x = _highpass(x * np.where(env > 0.02, 1.0, env / 0.02), dt)
    x = baseline_correct(x, dt)
    sa = sdof_spectrum_fast(x, dt, periods)
    return t, x, periods, sa


def baseline_correct(acc_g, dt, order=3):
    """Remove the polynomial trend of the velocity (and then of the displacement) so the
    record starts and ends at rest - standard strong-motion baseline correction."""
    a = np.asarray(acc_g, dtype=float).copy()
    n = len(a)
    t = np.arange(n) * dt
    tn = t / t[-1]
    for _ in range(2):
        v = np.cumsum(a) * dt
        c = np.polyfit(tn, v, order)
        a -= np.polyval(np.polyder(c), tn) / t[-1]
        d = np.cumsum(np.cumsum(a) * dt) * dt
        c = np.polyfit(tn, d, order + 2)
        a -= np.polyval(np.polyder(c, 2), tn) / t[-1] ** 2
    # remove a constant velocity offset (linear displacement drift) with a smooth pulse spread
    # over the 10 s build-up, which leaves the spectrum above ~1 s unchanged
    v = np.cumsum(a) * dt
    m0 = int(10.0 / dt)
    w = np.hanning(m0)
    w /= w.sum() * dt
    a[:m0] -= np.mean(v) * w
    taper = np.ones(n)
    m = int(2.0 / dt)
    taper[-m:] = 0.5 * (1 + np.cos(np.pi * np.arange(m) / m))
    return a * taper


def stats(acc_g, dt):
    a = np.asarray(acc_g) * 9.81
    v = np.cumsum(a) * dt
    d = np.cumsum(v) * dt
    ia = np.pi / (2 * 9.81) * np.cumsum(a ** 2) * dt
    t5 = np.searchsorted(ia, 0.05 * ia[-1]) * dt
    t95 = np.searchsorted(ia, 0.95 * ia[-1]) * dt
    return dict(PGA_g=float(np.max(np.abs(acc_g))), PGV_cms=float(np.max(np.abs(v)) * 100),
                PGD_cm=float(np.max(np.abs(d)) * 100), D5_95_s=float(t95 - t5), Arias_ms=float(ia[-1]))
