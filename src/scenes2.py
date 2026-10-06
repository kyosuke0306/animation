import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
KEEP = "Edit the reference image. Keep everything exactly the same (style, panels, divider lines, all other characters and poses) except the following change: "
PEEK = "his neck is a normal simple straight tube stretched only slightly (about one and a half times normal length, no loops, no curls), and he leans so that his head pokes ACROSS the thick black divider line into the neighboring panel to the left"
S = {
"F1a": ("F1a", "Character 3 in the right panel: "+PEEK+". His head is now over the middle panel area, his face turned left toward Character 1, staring blankly with droopy eyelids. Remove the loop-shaped neck."),
"G1": ("G1", "Character 2 in the middle panel: "+PEEK+". His head is now over the left panel, staring at Character 1 with a jealous surprised face, sweat drop."),
"L2": ("L1", "Character 2 in the middle panel laughs even harder: he leans far back on his stool, holding his belly with both hands, eyes squeezed shut, tears of laughter flying, mouth wide open."),
"H2": ("H1", "In the middle panel, the three angry people have turned their backs on Character 2 and are walking away out of the panel, one looks back sticking out his tongue. Character 2 is left alone, sweating and stunned, reaching out a hand."),
}
def run(k):
    ref, p = S[k]
    spec = {"name": k + ("_v2" if k == ref else ""), "refs": [f"images/{ref}.png"], "prompt": KEEP + p}
    return subprocess.run([sys.executable, "src/gen.py", json.dumps(spec)], capture_output=True, text=True).stdout + subprocess.PIPE.__class__.__name__[:0]
with ThreadPoolExecutor(4) as ex:
    for out in ex.map(run, S): print(out.strip())
