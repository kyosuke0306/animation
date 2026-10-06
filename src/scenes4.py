import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
KEEP = ("Edit the reference image. Keep the image EXACTLY the same: same art style, same three panels and divider lines, same characters, same positions and body poses, "
        "all necks normal and short (NO neck stretching), every character stays fully inside his own panel. Only change the following: ")
S = {
"H1n": ("N2", "Character 2 (middle): stands up from his stool in panic, big sweat drops flying, trembling, pupils shifted to the left as he glances nervously toward the left panel. Around him inside the middle panel, three simple bald cartoon people (round heads, simple eyes) with angry frowns point at him, thumbs down, steam puffs over their heads, booing. Characters 1 and 3 unchanged."),
"V2n": ("N2", "Character 2 (middle): sits slumped alone on his stool, head hanging down, turned away facing left, sulking, NOT looking right. Characters 1 and 3 unchanged."),
"W1": ("N2", "Character 2 (middle): his pupils shift to the far left side of his eyes and his head turns slightly left, sneaking a nosy sly sideways glance toward the left panel, smirk. Character 3 (right): his pupils shift to the far left side of his eyes and his head turns slightly left, quietly watching toward the left. Character 1 unchanged."),
"W2": ("N2", "Character 2 (middle): his pupils shift to the far right side of his eyes and his head turns slightly right, curiously glancing sideways toward the right panel. Characters 1 and 3 unchanged."),
"W3": ("N2", "Character 2 (middle): worried jealous face, sweat drop, pupils shifted to the far left side of his eyes, glancing nervously toward the left panel. Character 3 (right): now a hollow empty person: heavy droopy half-closed eyelids, dull expressionless face, flat mouth, slightly slumped shoulders, pupils shifted to the far left, staring emptily toward the left. Character 1 unchanged."),
"L1n": ("N2", "Character 2 (middle): laughing loudly with a huge open mouth, eyes squeezed shut, leaning back on his stool, pointing his finger toward the left panel, motion lines. Character 3 (right): pupils shifted to the far left of his eyes, head turned slightly left, watching toward the middle panel. Character 1 unchanged."),
"L2n": ("N2", "Character 2 (middle): laughing even harder, leaning far back on his stool holding his belly with both hands, eyes squeezed shut, tears of laughter flying, mouth wide open. Character 3 (right): pupils shifted to the far left of his eyes, head turned slightly left, watching toward the middle panel. Character 1 unchanged."),
}
def run(k):
    ref, p = S[k]
    spec = {"name": k, "refs": [f"images/{ref}.png"], "prompt": KEEP + p}
    return subprocess.run([sys.executable, "src/gen.py", json.dumps(spec)], capture_output=True, text=True).stdout
with ThreadPoolExecutor(5) as ex:
    for out in ex.map(run, S): print(out.strip())
