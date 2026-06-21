"""
APPROVE
-------
What this file does, in plain English:
    Takes a YouTube video that's currently PRIVATE (uploaded by the
    pipeline pending your review) and switches it to PUBLIC, making it
    actually visible to everyone.

Usage:
    python approve.py <video_id>

    The video_id is shown in the notification you receive, and is
    also the last part of the YouTube URL
    (youtube.com/shorts/THIS_PART_HERE).
"""

import sys
from dotenv import load_dotenv

from youtube_uploader import _get_authenticated_service


def approve_video(video_id: str):
    """
    Switches a YouTube video from private to public.
    """
    youtube = _get_authenticated_service()

    youtube.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": "public",
            },
        },
    ).execute()

    print(f"Video {video_id} is now public!")
    print(f"https://youtube.com/shorts/{video_id}")


if __name__ == "__main__":
    load_dotenv()

    if len(sys.argv) != 2:
        print("Usage: python approve.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    approve_video(video_id)