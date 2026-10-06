"""Gemini TTS for laughs / crowd reactions (no narration)."""
import wave, json, pathlib, fcntl, sys
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types
ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "gemini-3.8-flash-lite-tts"
# Text only: this TTS model reads any style instruction aloud, so the wording itself carries the emotion.
CLIPS = {
 "p1_ow":   ("Puck",   "いてっ！うわぁ〜ん！"),
 "p1_crash":("Puck",   "うわっ、うわっ、うわぁぁぁっ！"),
 "p2_laugh":("Fenrir", "ハッハッハッハ！ザマアミロ！アハハハハ！"),
 "crowd_boo":("Charon","ブーーー！ブーーー！サイテー！"),
 "friends_cheer":("Kore","イェーイ！あはははは！"),
 "p2_gasp": ("Fenrir", "えっ…！？なんで…！？"),
}
def run(k):
    voice, text = CLIPS[k]
    c = genai.Client()
    r = c.models.generate_content(model=MODEL, contents=text, config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)))))
    pcm = r.candidates[0].content.parts[0].inline_data.data
    with wave.open(str(ROOT / "audio" / f"{k}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    u = r.usage_metadata
    return k, len(pcm) / 48000, u.prompt_token_count, u.candidates_token_count
with ThreadPoolExecutor(7) as ex:
    rows = list(ex.map(run, sys.argv[1:] or CLIPS))
cost = sum(p * 0.5e-6 + o * 6e-6 for _, _, p, o in rows)
for r in rows: print(r)
print(f"tts cost ${cost:.4f}")
log = ROOT / "images" / "cost_log.json"
d = json.loads(log.read_text()); d.append({"name": "tts", "cost": round(cost, 4)}); log.write_text(json.dumps(d, indent=1))
