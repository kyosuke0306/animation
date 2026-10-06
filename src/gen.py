"""Gemini image generation helper with running cost log."""
import json, sys, pathlib, fcntl
from google import genai
from google.genai import types
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "images" / "cost_log.json"
PRICE_OUT = 60 / 1e6   # $ per image output token (gemini-3.1-flash-image)
PRICE_IN = 0.5 / 1e6   # $ per input token (upper bound)
BUDGET = 5.0
SPENT_BEFORE = 0.35    # style tests

STYLE = """Black-and-white cartoon in the style of 1930s American rubber-hose cartoons. Pure black ink on pure white, no gray, no color, no shading. Very thick bold clean outlines, simple shapes, minimal detail.
EYES: every eye is a single small solid black filled oval dot. No white of the eye, no pupils, no eyebrows (except Character 2's), no eyelashes.
No text, no letters, no speech bubbles."""

def spent():
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    return SPENT_BEFORE + sum(e["cost"] for e in log), log

def gen(name, prompt, refs=()):
    total, log = spent()
    if total > BUDGET - 0.15:
        sys.exit(f"budget stop: ${total:.2f}")
    c = genai.Client()
    contents = [Image.open(ROOT / r) for r in refs] + [STYLE + "\n\n" + prompt]
    r = c.models.generate_content(
        model="gemini-3.1-flash-image", contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K")))
    u = r.usage_metadata
    cost = (u.candidates_token_count or 0) * PRICE_OUT + (u.prompt_token_count or 0) * PRICE_IN
    with open(LOG.with_suffix(".lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        total, log = spent()
        log.append({"name": name, "cost": round(cost, 4)})
        LOG.write_text(json.dumps(log, indent=1))
    for p in r.candidates[0].content.parts:
        if p.inline_data:
            out = ROOT / "images" / f"{name}.png"
            out.write_bytes(p.inline_data.data)
            print(f"saved {out.name}  cost ${cost:.3f}  total ${total + cost:.2f}")
            return
    print("no image returned", r.candidates[0].content.parts)

if __name__ == "__main__":
    spec = json.loads(sys.argv[1])
    gen(spec["name"], spec["prompt"], spec.get("refs", []))
