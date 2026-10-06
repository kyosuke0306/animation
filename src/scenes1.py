import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
PRE = ("Use the reference image as the model sheet. Keep the identical art style, the same three equal panels separated by thick black vertical divider lines, "
"the same floor line, and the same three character designs: Character 1 (left panel, round head, headband), Character 2 (middle panel, pointy nose, slicked black hair, sits on a wooden stool), "
"Character 3 (right panel, bald round blank face, droopy heavy eyelids, flat mouth, sits on the floor). Necks are normal and short unless stated. ")
PEEK = "his neck is stretched only slightly (about one and a half times normal) and his head leans sideways so that it pokes ACROSS the thick black divider line into the neighboring panel"
S = {
"F1a": "LEFT: Character 1 eagerly strums an acoustic guitar with an excited open-mouth expression, facing right, focused only on the guitar. MIDDLE: Character 2 still sits on his stool, "+PEEK+" on the left, nosily staring at Character 1 with a sly grin. RIGHT: Character 3 still sits on the floor, "+PEEK+" on the left into the middle panel, staring blankly toward Character 1.",
"L1": "LEFT: Character 1 has his back turned to the other panels, sitting and seriously reading a thick book, normal neck, NOT looking at anyone. Small bandage on his head. MIDDLE: Character 2 laughs loudly with a huge open mouth, leaning back on his stool, pointing his finger at Character 1, motion lines. Normal neck. RIGHT: Character 3, "+PEEK+" on the left into the middle panel, staring blankly at Character 2.",
"D1": "LEFT: Character 1 has his back turned to the other panels, juggling three balls with a determined look, normal neck, NOT looking at anyone. MIDDLE: Character 2 sits on his stool, "+PEEK+" on the right into the right panel, staring curiously at Character 3. RIGHT: Character 3 sits on the floor doing absolutely nothing, blank face, a small fly buzzing near his head.",
"G1": "LEFT: Character 1 happily plays the guitar well, eyes closed in joy, music notes floating, a small trophy at his feet, and three simple cartoon friends (round heads, dot eyes) cheering and clapping around him. MIDDLE: Character 2, "+PEEK+" on the left, staring at Character 1 with a jealous surprised face. RIGHT: Character 3, "+PEEK+" on the left into the middle panel, staring blankly toward Character 1.",
"H1": "LEFT: Character 1 laughs happily with his three friends, arms around each other, facing left, normal neck, NOT looking at anyone else. MIDDLE: Character 2 stands up in panic, big sweat drops flying, trembling, looking toward the left panel; around him three simple cartoon people (round heads, dot eyes) with angry frowns point at him and shout 'boo', thumbs down, steam puffs over their heads. RIGHT: Character 3, "+PEEK+" on the left into the middle panel, staring blankly at Character 2.",
"V1": "LEFT: Character 1 and his three friends happily chat together, all facing left, their backs toward the right side, nobody looks right. MIDDLE: Character 2 sits slumped alone on his stool, head down, facing left, sulking, not looking right. RIGHT: Character 3 sits completely alone in a vast empty panel, small in the frame, totally hollow expressionless face, empty eyes, no tears, no sadness, just emptiness. Nobody in the image looks at Character 3.",
}
def run(k):
    spec = {"name": k, "refs": ["images/N0.png"], "prompt": PRE + S[k]}
    return subprocess.run([sys.executable, "src/gen.py", json.dumps(spec)], capture_output=True, text=True).stdout
with ThreadPoolExecutor(6) as ex:
    for out in ex.map(run, S): print(out.strip())
