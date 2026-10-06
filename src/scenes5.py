import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
KEEP = ("Edit the reference image. Keep the image EXACTLY the same: same art style, same three panels and divider lines, the middle and right panels completely unchanged. "
        "Character 1 keeps his design (round head, headband, white gloves), stays fully inside the left panel, and does NOT look toward the other panels. Only change the LEFT panel: ")
S = {
"R2a": "Character 1, with a small bandage on his head, sings loudly and badly into a microphone with his eyes shut, jagged sour music notes around him. Two simple bald cartoon people (round heads, simple eyes, no hair) stand beside him covering their ears with annoyed, disgusted frowns.",
"R2b": "Character 1 has tripped over the microphone cord and fallen flat on his face. Two simple bald cartoon people (round heads, simple eyes, no hair) stand over him: one rolls his eyes and facepalms, the other shrugs with an exasperated sigh puff, both turning away from him in disgust.",
"R2c": "Character 1 is completely alone now, a little battered with bandages, but still determined: he practices strumming his guitar by himself, facing left with his back toward the right side of the image. Nobody else is in the left panel.",
}
def run(k):
    spec = {"name": k, "refs": ["images/N2.png"], "prompt": KEEP + S[k]}
    return subprocess.run([sys.executable, "src/gen.py", json.dumps(spec)], capture_output=True, text=True).stdout
with ThreadPoolExecutor(3) as ex:
    for out in ex.map(run, S): print(out.strip())
