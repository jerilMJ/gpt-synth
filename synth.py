import json
import music21 as m21
import os
import openai
import sys


if len(sys.argv) < 3:
    print("Usage: synth.py <song-name> <duration>")
    exit(0)

openai.api_key = os.environ["OPENAI_API_KEY"]

song = sys.argv[1]
duration = sys.argv[2]
if os.path.isfile(f"cache/{song.lower()}.json"):
    print("Loading cached result...")
    with open(f"cache/{song.lower()}.json", "r") as f:
        res = json.loads(f.read())
else:
    print("Prompting gpt...")
    with open("context.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{$1}", song).replace("{$2}", duration)
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"${prompt}"}],
        temperature=0.5,
    )
    res = chat_completion.choices[0].message.content
    print(res)
    res = json.loads(res)
    with open(f"cache/{song.lower()}.json", "w") as f:
        f.write(json.dumps(res, indent=4))


if __name__ == "__main__":
    stream = m21.stream.Stream()
    for group in res["track"].split(","):
        note, dur = group.split("|")
        note = note.replace("_", "-")
        dur = float(dur)
        if note == "R":
            stream.append(m21.note.Rest(quarterLength=dur))
        else:
            stream.append(m21.note.Note(note, quarterLength=dur))
    score = m21.stream.Score()
    score.insert(0, stream)
    sp = m21.midi.realtime.StreamPlayer(score)
    sp.play()
