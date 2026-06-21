"""
MUSIC FINDER (Jamendo)
------------------------
What this file does, in plain English:
    Searches Jamendo for a background track matching a mood/genre,
    and downloads it.

Why licensing filtering matters here:
    Only CC0 and CC-BY are unambiguously safe for monetized YouTube
    content. This file ONLY accepts those two license types.

What you need for this to work:
    A free Jamendo developer account and client_id, saved in .env as
    JAMENDO_CLIENT_ID.
"""

import os
import requests

JAMENDO_BASE = "https://api.jamendo.com/v3.0"


def find_background_music(mood: str, save_path: str = "temp/music.mp3") -> str:
    """
    Searches Jamendo for a track matching the given mood/genre, downloads
    the first safely-licensed match, and returns the local file path.

    If the requested mood returns no results, falls back to "ambient" -
    a reliably well-stocked tag - rather than leaving the video with
    no music at all.
    """
    result = _search_and_download(mood, save_path)
    if result:
        return result

    if mood != "ambient":
        print(f"      [debug] Falling back to 'ambient' mood...")
        result = _search_and_download("ambient", save_path)
        if result:
            return result

    return None


def _search_and_download(mood: str, save_path: str) -> str:
    client_id = os.environ.get("JAMENDO_CLIENT_ID")

    response = requests.get(
        f"{JAMENDO_BASE}/tracks/",
        params={
            "client_id": client_id,
            "format": "json",
            "limit": 10,
            "tags": mood,
            "include": "licenses",
            "ccsa": "false",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    print(f"      [debug] Jamendo returned {len(results)} track(s) for mood '{mood}'")

    for track in results:
        license_ccurl = track.get("license_ccurl", "").lower()

        is_safe = (
            "publicdomain" in license_ccurl
            or "/by/" in license_ccurl
        ) and "nc" not in license_ccurl and "nd" not in license_ccurl and "sa" not in license_ccurl

        if not is_safe:
            continue

        audio_url = track.get("audio")
        if not audio_url:
            continue

        try:
            audio_response = requests.get(audio_url, timeout=20)
            audio_response.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(audio_response.content)

            print(f"      [debug] Using track: '{track.get('name')}' by {track.get('artist_name')} ({license_ccurl})")
            return save_path
        except Exception as e:
            print(f"      [debug] Failed to download track: {e}")
            continue

    return None


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing music search: 'dark ambient'")
    path = find_background_music("dark ambient")
    print(f"Result: {path}")