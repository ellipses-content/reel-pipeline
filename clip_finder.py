"""
CLIP FINDER
-----------
What this file does, in plain English:
    Searches Pexels (a free stock video site) for short background video
    clips that match the topic, and downloads a handful of them.

How it fits in the pipeline:
    This is STEP 3. It runs independently of the script/voice steps
    (it just needs the topic, not the script text), and its output -
    a folder of downloaded clips - gets handed to video_assembler.py.

What you need for this to work:
    A free Pexels API key. Sign up at pexels.com/api - it's instant and
    free, no credit card needed. Save the key in the .env file.

Important note on legality:
    These clips are explicitly licensed by Pexels for free reuse, including
    commercial use, with no attribution required. This is NOT the same as
    downloading random videos off the internet - Pexels exists specifically
    to license footage this way.
"""

import os
import requests
from dotenv import load_dotenv

# Load API keys from the .env file - needed when this file is run on its
# own (python clip_finder.py) to test it in isolation.
load_dotenv()


def find_clips(topic: str, count: int = 4, save_folder: str = "temp/clips") -> list:
    """
    Searches Pexels for short vertical video clips matching the topic,
    and downloads them to a local folder.

    Inputs:
        topic        - search term, e.g. "ocean" (keep it simple - one or
                        two words tends to find better matches than a full
                        sentence)
        count        - how many clips to download
        save_folder  - where to save the downloaded clips

    Output:
        A list of file paths to the downloaded clips, e.g.
        ["temp/clips/clip_0.mp4", "temp/clips/clip_1.mp4", ...]
    """
    os.makedirs(save_folder, exist_ok=True)

    api_key = os.environ.get("PEXELS_API_KEY")
    headers = {"Authorization": api_key}

    # Ask Pexels for vertical (portrait) videos, since that's what
    # TikTok/Reels/Shorts all need - this saves us a cropping step later.
    search_url = "https://api.pexels.com/videos/search"
    params = {
        "query": topic,
        "orientation": "portrait",
        "per_page": count,
    }

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()  # stops here with a clear error if the key is wrong
    results = response.json()

    downloaded_paths = []

    for i, video in enumerate(results.get("videos", [])):
        # Each Pexels video comes in multiple resolutions ("video_files").
        # We grab a mid-size file - large enough to look good, small enough
        # to download quickly. Sorting by width picks a reasonable middle one.
        video_files = sorted(video["video_files"], key=lambda v: v.get("width", 0))
        chosen = video_files[len(video_files) // 2]

        video_url = chosen["link"]
        file_path = os.path.join(save_folder, f"clip_{i}.mp4")

        video_data = requests.get(video_url)
        with open(file_path, "wb") as f:
            f.write(video_data.content)

        downloaded_paths.append(file_path)

    return downloaded_paths


# Test block - only runs if you execute this file directly.
if __name__ == "__main__":
    print("Searching for clips about: ocean")
    clips = find_clips("ocean", count=3)
    print(f"Downloaded {len(clips)} clips:")
    for c in clips:
        print(f"  - {c}")
