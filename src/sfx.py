"""Locally synthesized cartoon sound effects (no API)."""
import numpy as np, wave, pathlib
SR = 44100
OUT = pathlib.Path(__file__).resolve().parent.parent / "audio"
rng = np.random.default_rng(1)
t = lambda d: np.arange(int(SR * d)) / SR

def save(name, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    with wave.open(str(OUT / f"sfx_{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def sweep(f0, f1, d, shape=np.sin):
    tt = t(d); f = np.geomspace(f0, f1, len(tt))
    return shape(2 * np.pi * np.cumsum(f) / SR)

def lowpass(x, a):  # one-pole
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y

# guitar string snap: bright pluck + falling twang
tt = t(0.9)
twang = sweep(330, 140, 0.9) * np.exp(-tt * 4) * (1 + 0.5 * np.sin(2 * np.pi * 9 * tt))
snap = np.r_[rng.normal(size=int(SR * .02)) * np.linspace(1, 0, int(SR * .02)), np.zeros(len(tt) - int(SR * .02))]
save("snap", twang + snap * 1.5)
# crash: noise burst + metal clank
tt = t(1.0)
crash = lowpass(rng.normal(size=len(tt)), 0.3) * np.exp(-tt * 6)
clank = sum(np.sin(2 * np.pi * f * tt) for f in (523, 789, 1240)) * np.exp(-tt * 9) * 0.3
save("crash", crash + clank)
# splat: low thud + wet noise
tt = t(0.6)
save("splat", np.sin(2 * np.pi * 80 * tt) * np.exp(-tt * 12) + lowpass(rng.normal(size=len(tt)), 0.08) * np.exp(-tt * 8) * 2)
# eye dart "zip"
save("zip", sweep(600, 2400, 0.12) * np.hanning(int(SR * .12)) * 0.6)
# blink "plink"
tt = t(0.25); save("plink", np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 25))
# success ding (two notes)
tt = t(0.9)
ding = lambda f: sum(np.sin(2 * np.pi * f * k * tt) / k for k in (1, 2, 3)) * np.exp(-tt * 4)
save("ding", np.r_[ding(784)[: int(SR * .15)], ding(1047)])
# slide whistle down (failure)
save("whistle_down", sweep(1400, 300, 0.8) * np.r_[np.linspace(0, 1, 2000), np.ones(int(SR * .8) - 2000)])
# hollow wind
tt = t(6.0)
wind = lowpass(rng.normal(size=len(tt)), 0.02) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * tt))
save("wind", wind * np.minimum(1, tt / 1.5) * np.minimum(1, (6 - tt) / 1.5))
# freeze-frame "record stop"
save("stop", sweep(500, 60, 0.5, lambda p: np.sign(np.sin(p))) * np.linspace(1, 0, int(SR * .5)) * 0.4)
# bouncy ragtime-ish bass/piano loop for round 1 and 2 (simple, quiet)
def loop(notes, bpm, bars, wave_=np.sin):
    beat = 60 / bpm; out = []
    for _ in range(bars):
        for f in notes:
            tt = t(beat); out.append(wave_(2 * np.pi * f * tt) * np.exp(-tt * 5))
    return np.concatenate(out)
save("music1", loop([131, 196, 165, 196, 147, 220, 175, 220], 200, 6) * 0.5)
save("music2", loop([131, 165, 196, 262, 147, 175, 220, 294], 200, 6) * 0.5)
print("ok")
