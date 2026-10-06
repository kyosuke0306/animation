"""Compose panels, animate camera/eyes, burn subtitles, mix audio -> out/video.mp4"""
import math, wave, subprocess, pathlib, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG, AUD, OUT = ROOT / "images", ROOT / "audio", ROOT / "out"
OUT.mkdir(exist_ok=True)
W, H, FPS = 1920, 1080, 24
SW, SH = 2752, 1536
PANELS = [(0, 921), (921, 1832), (1832, SW)]
DIVIDERS = [(911, 931), (1822, 1842)]
P3_HEAD = (2316, 666, 200)  # center x, y, interior radius of character 3's head (N2-based panels)
JP = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@functools.lru_cache(None)
def src(name):
    return Image.open(IMG / f"{name}.png").convert("L")

@functools.lru_cache(None)
def panel(spec, idx):
    """spec: image name, optionally with modifiers: 'N2|flip', 'N2|eyes:-45', 'N2|eyes:0:blink', 'F1b|clean'."""
    name, *mods = spec.split("|")
    x0, x1 = PANELS[idx]
    im = src(name).crop((x0, 0, x1, SH))
    for m in mods:
        if m == "flip":
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif m == "clean":  # remove character 2's old stretched head poking into panel 1
            ImageDraw.Draw(im).rectangle((810, 170, x1 - x0, 660), fill=255)
        elif m.startswith("eyes"):
            _, dx, *blink = m.split(":")
            im = slide_face(im, int(dx), bool(blink), x0)
    return im

def slide_face(im, dx, blink, x0):
    """Slide character 3's facial features sideways inside his round head (pupils looking aside)."""
    cx, cy, r = P3_HEAD
    cx -= x0
    a = np.array(im)
    yy, xx = np.mgrid[: a.shape[0], : a.shape[1]]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 < r ** 2
    feat = np.where(inside, a, 255)
    if blink:  # replace eyes with closed-eye lines
        feat[cy - 60: cy + 60, cx - 140: cx + 70] = 255
        for ex in (cx - 109, cx + 31):
            feat[cy - 6: cy + 8, ex - 30: ex + 30] = 0
    def shift(arr, d):
        o = np.full_like(arr, 255)
        if d < 0: o[:, :d] = arr[:, -d:]
        elif d > 0: o[:, d:] = arr[:, :-d]
        else: o = arr
        return o
    band = np.zeros_like(inside); band[cy - 75: cy + 75] = True
    shifted = np.where(band, shift(feat, dx), shift(feat, int(dx * 0.4)))
    out = np.where(inside, np.minimum(255, shifted), a)
    return Image.fromarray(out.astype(np.uint8))

@functools.lru_cache(maxsize=64)
def compose(l, m, r):
    base = Image.new("L", (SW, SH), 255)
    for i, s in enumerate((l, m, r)):
        base.paste(panel(s, i), (PANELS[i][0], 0))
    d = ImageDraw.Draw(base)
    for a, b in DIVIDERS:
        d.rectangle((a, 0, b, SH), fill=0)
    d.rectangle((0, 0, SW - 1, SH - 1), outline=0, width=14)
    return base

# ---------------- camera presets (center x, center y, zoom) ----------------
WIDE = (SW / 2, SH / 2, 1.0)
L_MED, L_CLOSE = (900, 790, 1.55), (470, 700, 2.0)
M_MED, M_CLOSE = (1376, 790, 1.55), (1376, 680, 2.0)
R_MED, R_CLOSE = (1852, 790, 1.55), (2290, 720, 2.0)

def ease(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))

# ---------------- shot list ----------------
# each shot: (start, end, panels_fn(t_local)->(l,m,r), cam_from, cam_to, move_dur, shake_times, subtitle, card)
def const(l, m, r):
    return lambda t: (l, m, r)

def eye_dart(l, m, before, after, at, steps=4, step_dt=0.04):
    def f(t):
        if t < at:
            return (l, m, before)
        k = min(steps, int((t - at) / step_dt) + 1)
        return (l, m, after.replace("{dx}", str(round(-62 * k / steps))))
    return f

SHOTS = []
def shot(start, end, fn, c0, c1, move=0.6, shakes=(), sub=None, card=None):
    SHOTS.append(dict(start=start, end=end, fn=fn, c0=c0, c1=c1, move=move, shakes=shakes, sub=sub, card=card))

E = "N2|eyes:{dx}"          # character 3, round 1 (normal), with eye offset template
P3L = "N2|eyes:-62"         # character 3 looking left
# ---- round 1
shot(0.0, 0.8, const("N2", "N2", "N2"), WIDE, WIDE)
shot(0.8, 1.6, eye_dart("F1a_v2|clean", "N2", "N2", E, at=0.15), WIDE, L_MED, move=0.3)
shot(1.6, 2.6, lambda t: ("F1a_v2|clean" if t < 0.2 else "F1b|clean", "N2", P3L), L_MED, L_CLOSE, move=0.2, shakes=(1.8,))
shot(2.6, 3.6, const("F2|clean", "N2", P3L), L_CLOSE, L_MED, move=0.15, shakes=(2.65,))
shot(3.6, 4.6, const("F3|clean", "N2", P3L), L_MED, L_CLOSE, move=0.15, shakes=(3.65,))
shot(4.6, 6.6, lambda t: ("L1", "L1n" if int(t / 0.18) % 2 == 0 else "L2n", P3L), L_CLOSE, M_MED, move=0.25)
shot(6.6, 8.2, lambda t: ("D1", "N2" if t < 0.2 else "N2|flip",
                         "N2|eyes:0:blink" if 0.9 < t < 1.02 else "N2|eyes:0"), M_MED, R_MED, move=0.3)
shot(8.2, 10.2, const("D1", "N2|flip", "N2|eyes:0"), R_MED, WIDE, move=0.25, card="Which one are you?")
# ---- round 2
shot(10.2, 11.8, const("G1", "W3", "W3"), WIDE, L_MED, move=0.3)
shot(11.8, 13.2, const("H1", "W3", "W3"), L_MED, L_CLOSE, move=0.3)
shot(13.2, 14.8, const("H1", "H1n", "W3"), L_CLOSE, M_MED, move=0.25, shakes=(13.45, 14.15))
shot(14.8, 16.0, const("H1", "V2n", "W3"), M_MED, M_CLOSE, move=0.3)
shot(16.0, 18.0, const("V1", "V2n", "V1"), M_CLOSE, R_CLOSE, move=0.5)
shot(18.0, 20.0, const("V1", "V2n", "V1"), R_CLOSE, WIDE, move=0.25, card="Which one would you choose?")
DURATION = SHOTS[-1]["end"]

# ---------------- text ----------------
def draw_sub(frame, text):
    d = ImageDraw.Draw(frame)
    f = ImageFont.truetype(JP, 62)
    tw = d.textlength(text, font=f)
    x, y = (W - tw) / 2, H - 150
    d.rounded_rectangle((x - 36, y - 22, x + tw + 36, y + 84), radius=26, fill=255, outline=0, width=7)
    d.text((x, y), text, font=f, fill=0, stroke_width=2, stroke_fill=0)

def draw_card(frame, text, u):
    d = ImageDraw.Draw(frame)
    size = int(96 * (0.6 + 0.4 * ease(u * 3)))
    f = ImageFont.truetype(EN, size)
    tw = d.textlength(text, font=f)
    x, y = (W - tw) / 2, 70
    d.rounded_rectangle((x - 50, y - 30, x + tw + 50, y + size + 40), radius=30, fill=255, outline=0, width=10)
    d.text((x, y), text, font=f, fill=0)

def render_frame(t):
    s = next(s for s in SHOTS if s["start"] <= t < s["end"]) if t < DURATION else SHOTS[-1]
    lt = t - s["start"]
    frozen = s["card"] is not None
    l, m, r = s["fn"](0 if frozen else lt)
    img = compose(l, m, r)
    cx, cy, z = lerp(s["c0"], s["c1"], ease(lt / s["move"]))
    if not frozen:  # gentle "alive" drift + line boil while on screen
        if int(t * 12) % 2:
            cx += 2; cy += 1
    for st in s["shakes"]:
        if 0 <= t - st < 0.35:
            k = 1 - (t - st) / 0.35
            cx += 28 * k * math.sin((t - st) * 90)
            cy += 18 * k * math.cos((t - st) * 70)
    ch = SH / z; cw = ch * W / H
    cx = min(max(cx, cw / 2), SW - cw / 2) if cw < SW else SW / 2
    cy = min(max(cy, ch / 2), SH - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    frame = img.resize((W, H), Image.LANCZOS, box=box)
    if s["sub"]:
        draw_sub(frame, s["sub"])
    if frozen and lt > 0.2:
        draw_card(frame, s["card"], lt - 0.2)
    return frame

# ---------------- audio ----------------
SR = 44100
def load(name):
    w = wave.open(str(AUD / f"{name}.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getframerate() != SR:
        n = int(len(x) * SR / w.getframerate())
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    return x

def mix(cues):
    out = np.zeros(int(SR * (DURATION + 0.5)), np.float32)
    for name, at, vol, clip_from, clip_len in cues:
        x = load(name)
        if not name.startswith("sfx_"):  # voice: drop the click in the last 0.25s, normalize
            x = x[: -int(0.25 * SR)]
        x = x[int(clip_from * SR):]
        if clip_len:
            x = x[: int(clip_len * SR)]
            fade = min(len(x), int(0.08 * SR))
            x[-fade:] *= np.linspace(1, 0, fade)
        if not name.startswith("sfx_"):
            x = x / (np.abs(x).max() + 1e-9) * 0.9
        i = int(at * SR)
        x = x[: len(out) - i]
        out[i: i + len(x)] += x * vol
    out /= max(1.0, np.abs(out).max() / 0.95)
    path = OUT / "audio.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    return path

from cues import CUES  # (clip, at_sec, volume, clip_from_sec, clip_len_sec or None)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:  # preview stills: python render.py 2.0 7.5 ...
        for t in sys.argv[1:]:
            render_frame(float(t)).save(OUT / f"still_{t}.png")
        sys.exit()
    apath = mix(CUES)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(apath), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                           "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest", str(OUT / "video.mp4")],
                          stdin=subprocess.PIPE)
    for i in range(int(DURATION * FPS)):
        ff.stdin.write(render_frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("done", OUT / "video.mp4")
