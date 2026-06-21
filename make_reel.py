"""
MAKE REEL - main entry point
------------------------------
What this file does, in plain English:
    This is the file you actually run. It connects script writer ->
    voice generator -> clip finder -> real image finder -> music
    finder -> video assembler -> YouTube uploader -> notifier into one
    simple command. Voice, visuals, and music are all auto-selected by
    Claude based on the topic unless you manually override them.

How to use it:
    python make_reel.py --topic "weird ocean facts"
    python make_reel.py --topic "bigfoot" --voice male_us_v2   (manual override)
    python make_reel.py --topic "bigfoot" --no-upload           (skip YouTube)

What happens when you run it:
    1. Writes a script, picks a voice, finds visuals and music - all
       automatically based on the topic
    2. Assembles the finished video
    3. Uploads it to YouTube as PRIVATE (not visible to anyone but you)
    4. Sends a push notification to your phone with a link to review it
    5. You watch it, and if you're happy, run:
           python approve.py <video_id>
       to make it public. Nothing goes live without that explicit step.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from script_writer import write_script, suggest_visual_search_term, suggest_music_mood, suggest_voice
from voice_generator import generate_voiceover
from clip_finder import find_clips
from real_image_finder import find_real_images, find_folklore_art
from music_finder import find_background_music
from video_assembler import assemble_video
from youtube_uploader import upload_short
from notifier import notify_video_ready


class _SuppressHandleErrors:
    def write(self, msg):
        if "WinError 6" not in msg and "handle is invalid" not in msg:
            sys.__stderr__.write(msg)

    def flush(self):
        sys.__stderr__.flush()


sys.stderr = _SuppressHandleErrors()


def make_reel(
    topic: str,
    voice: str = None,
    visual_search: str = None,
    upload: bool = True,
):
    print(f"\n=== Building a reel about: '{topic}' ===\n")

    print("[1/5] Writing script...")
    script = write_script(topic)
    print(f"      Script ready ({len(script.split())} words):\n")
    print(f"      \"{script}\"\n")

    if voice:
        chosen_voice = voice
    else:
        chosen_voice = suggest_voice(topic)
        print(f"      Auto-suggested voice: '{chosen_voice}'")

    print("[2/5] Generating voiceover...")
    voice_path = generate_voiceover(script, "temp/voice.mp3", voice=chosen_voice)
    print(f"      Saved voiceover to {voice_path}\n")

    print("[3/5] Finding visuals...")

    if visual_search:
        search_term = visual_search
    else:
        search_term = suggest_visual_search_term(topic)
        print(f"      Auto-suggested visual search term: '{search_term}'")

    real_images = find_real_images(topic, count=6)
    if real_images:
        print(f"      Found {len(real_images)} real documentation photos for '{topic}'")
    else:
        print(f"      No real photos found for '{topic}' - trying folklore/artistic depictions...")
        real_images = find_folklore_art(topic, count=6)
        if real_images:
            print(f"      Found {len(real_images)} folklore/artistic images")
        else:
            print(f"      No folklore art found either - using mood footage only")

    print(f"      Searching Pexels for: '{search_term}'")
    video_clips = find_clips(search_term, count=8)
    print(f"      Downloaded {len(video_clips)} video clips\n")

    print("Finding background music...")
    music_mood = suggest_music_mood(topic)
    print(f"      Auto-suggested music mood: '{music_mood}'")
    music_path = find_background_music(music_mood)
    if music_path:
        print(f"      Music ready\n")
    else:
        print(f"      No safely-licensed music found - video will have no background music\n")

    print("[4/5] Assembling final video (this is the slow step - be patient)...")
    safe_filename = topic.lower().replace(" ", "_")
    output_path = f"output/{safe_filename}.mp4"
    final_path = assemble_video(
        voice_path, video_clips, script, output_path,
        image_paths=real_images, music_path=music_path,
    )

    print(f"\n=== Video ready: {final_path} ===\n")

    if not upload:
        print("Skipping YouTube upload (--no-upload was set).")
        return final_path

    print("[5/5] Uploading to YouTube as private...")
    video_title = topic.title()
    video_url = upload_short(
        final_path,
        title=video_title,
        description=f"Generated automatically. Topic: {topic}",
        privacy="private",
    )
    video_id = video_url.rstrip("/").split("/")[-1]
    print(f"      Uploaded (private): {video_url}\n")

    notify_video_ready(video_title, video_url, video_id)

    print(f"\n=== Done! Review the video, then run: python approve.py {video_id} ===\n")
    return final_path


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate a faceless short-form video.")
    parser.add_argument("--topic", required=True, help="What the video should be about (drives the script)")
    parser.add_argument(
        "--visuals",
        default=None,
        help="Optional: a different search term for background clips. If omitted, auto-suggested.",
    )
    parser.add_argument(
        "--voice",
        default=None,
        choices=[
            "male_us", "female_us", "male_uk", "female_uk",
            "male_us_v2", "female_us_v2", "female_us_warm",
        ],
        help="Optional: which voice to use. If omitted, auto-suggested based on topic.",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading to YouTube - just generate the video file locally.",
    )
    args = parser.parse_args()

    make_reel(
        args.topic,
        voice=args.voice,
        visual_search=args.visuals,
        upload=not args.no_upload,
    )