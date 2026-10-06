import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
KEEP = ("Edit the reference image. Keep the image EXACTLY the same: same art style, same three panels and divider lines, same characters with the same designs and positions. "
        "Only change the following: ")
S = {
"H2": ("H1", "Remove the three angry people from the middle panel completely, leaving empty white space where they were (a few small dust puffs where they walked off). Character 2 stays exactly as he is, alone, sweating and stunned. Left and right panels unchanged."),
"F1b": ("F1a_v2", "LEFT panel only: a guitar string has snapped and whipped Character 1 in the face; he recoils backwards, eyes replaced by X shapes, a red-mark welt drawn as black lines on his cheek, the broken string curling in the air, little stars around his head. Middle and right panels unchanged."),
"F2": ("F1a_v2", "LEFT panel only: Character 1 has crashed off a unicycle, lying flat on his back on the floor, the unicycle on top of him, dazed with X eyes, stars circling, dust puff. Middle and right panels unchanged."),
"F3": ("F1a_v2", "LEFT panel only: Character 1 tried to paint and tripped; a paint bucket landed upside down on his head, black paint splattered all over him and a canvas, drips running down. Middle and right panels unchanged."),
}
def run(k):
    ref, p = S[k]
    spec = {"name": k, "refs": [f"images/{ref}.png"], "prompt": KEEP + p}
    return subprocess.run([sys.executable, "src/gen.py", json.dumps(spec)], capture_output=True, text=True).stdout
with ThreadPoolExecutor(4) as ex:
    for out in ex.map(run, S): print(out.strip())
