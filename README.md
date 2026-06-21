# Reel Pipeline

Turns a topic (like "weird ocean facts") into a finished, ready-to-post
vertical video — script, voiceover, background clips, and captions — all
generated automatically.

This is Phase 1: video generation. Phase 2 (auto-posting to TikTok/
Instagram/YouTube) comes later, once this part is working well.

---

## One-time setup

Do these steps once. After that, making a video is just one command.

### 1. Install Python
Download from [python.org](https://python.org) if you don't have it.
During install, check the box that says "Add Python to PATH."

### 2. Install FFmpeg
This is the free tool that actually encodes video behind the scenes.
- Download from [ffmpeg.org](https://ffmpeg.org/download.html) (Windows builds)
- Unzip it somewhere, e.g. `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to your system PATH (search "edit environment
  variables" in the Windows start menu, add it there)
- Test it worked: open a new terminal and type `ffmpeg -version` —
  you should see version info, not an error

### 3. Open this folder in VS Code
File → Open Folder → select this `reel-pipeline` folder.

### 4. Install the Python packages
Open the terminal inside VS Code (`Terminal` → `New Terminal`) and run:

```
pip install -r requirements.txt
```

This installs everything listed in `requirements.txt` — each line
explains what it's for.

### 5. Set up your API keys
- Copy `.env.example` and rename the copy to `.env`
- Get a free Anthropic API key: [console.anthropic.com](https://console.anthropic.com)
- Get a free Pexels API key: [pexels.com/api](https://pexels.com/api)
- Paste both into `.env`, replacing the placeholder text

That's it — setup is done.

---

## Testing it piece by piece (recommended before running the whole thing)

Rather than running the full pipeline first and guessing what broke,
test each piece on its own. Each file can be run by itself:

```
python script_writer.py
```
Should print a generated script to your terminal. If this fails, it's
your Anthropic API key.

```
python voice_generator.py
```
Should create `temp/test_voice.mp3`. Play it — should sound like a
real (if slightly robotic) voice. No API key needed for this one.

```
python clip_finder.py
```
Should download a few clips into `temp/clips/`. If this fails, it's
your Pexels API key.

Once all three work on their own, you're ready for the real thing.

---

## Making your first video

```
python make_reel.py --topic "weird ocean facts"
```

Watch the terminal — it prints what it's doing at each of the 4 steps.
The last step (assembling video) is the slowest; give it a minute or two.

When it's done, your video will be at:
```
output/weird_ocean_facts.mp4
```

Open it like any video file and see how it looks.

### Optional: pick a different voice
```
python make_reel.py --topic "weird ocean facts" --voice female_uk
```
Options: `male_us`, `female_us`, `male_uk`, `female_uk`

---

## If something goes wrong

- **"API key invalid"** → double check you copied the full key into
  `.env` with no extra spaces, and that you renamed the file to exactly
  `.env` (not `.env.example` or `.env.txt`)
- **"ffmpeg not found"** → FFmpeg isn't installed or isn't on your PATH
  (see step 2 above)
- **Captions look cut off or font looks wrong** → this is a minor
  cosmetic issue we can tune once you see your first real output
- **Video looks/sounds off in some other way** → that's expected on a
  first run. Tell me what looks wrong and we'll adjust that specific
  piece.

---

## What's next (Phase 2, not built yet)

Once you're happy with the videos this produces, the next phase adds:
- Scheduling (auto-generate a new video every day on a topic list)
- Auto-posting to TikTok / Instagram / YouTube Shorts
- A simple review step before anything goes live publicly
