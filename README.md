# Reel Pipeline

Turns a topic (like "Bigfoot") into a finished, posted YouTube Short —
script, voiceover, real photos or folklore art, background video clips,
background music, and captions, all generated and uploaded automatically.
Runs twice a day on its own, in the cloud, with a phone-tap approval step
before anything goes public.

---

## What this actually does, end to end

1. **Twice a day**, GitHub's servers (not your computer) automatically:
   - Pick the next topic off `topics.txt`
   - Write a script (auto-checks past scripts on this topic to avoid repeats)
   - Pick a narration voice that fits the topic's tone
   - Generate the voiceover
   - Find real documentation photos (or folklore art if none exist) plus
     background video clips
   - Pick and download background music (only safely-licensed tracks)
   - Assemble the final vertical video with captions
   - Upload it to YouTube as **private**
   - Send you a phone notification with a real **"Approve & Publish"** button
2. **You tap the button** on your phone whenever you get a chance
3. That tap triggers a second cloud job that switches the video to **public**

Your computer doesn't need to be on for any of this. Everything runs on
GitHub's free infrastructure.

---

## Project structure

| File | What it does |
|---|---|
| `make_reel.py` | Connects every step into one pipeline; also runnable manually |
| `scheduled_run.py` | Picks the next topic off the list and calls make_reel.py |
| `script_writer.py` | Writes the script; auto-suggests voice/visuals/music mood |
| `script_history.py` | Tracks past scripts per topic, to avoid repeating content |
| `voice_generator.py` | Free text-to-speech voiceover |
| `clip_finder.py` | Pexels background video clips |
| `real_image_finder.py` | Openverse real photos / folklore art |
| `music_finder.py` | Jamendo background music, license-filtered for safe use |
| `video_assembler.py` | Stitches everything into the final .mp4 |
| `youtube_uploader.py` | Uploads to YouTube (private by default) |
| `notifier.py` | Sends the phone notification with the approve button |
| `approve.py` | Switches a video from private to public |
| `topics.txt` | The list of topics the scheduler works through |
| `.github/workflows/generate.yml` | Runs the full pipeline on a schedule |
| `.github/workflows/approve.yml` | Runs when you tap "Approve" on your phone |

---

## Running it manually (for testing, or one-off videos)