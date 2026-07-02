"""
REJECT
------
What this file does, in plain English:
    Takes a YouTube video that's currently PRIVATE (uploaded by the
    pipeline pending your review) and DELETES it, because you decided
    not to publish it. This keeps rejected videos from piling up on
    your channel.

Usage:
    python reject.py <video_id>

    The video_id is shown in the notification you receive, and is
    also the last part of the YouTube URL
    (youtube.com/shorts/THIS_PART_HERE).

How it's normally triggered:
    You tap "Reject & Delete" in the phone notification, which fires a
    GitHub repository_dispatch event that runs this in the cloud.
"""

import sys
from dotenv import load_dotenv

from youtube_uploader import _get_authenticated_service


def reject_video(video_id: str):
    """
    Permanently deletes a (private) YouTube video by its ID.
    """
    youtube = _get_authenticated_service()

    youtube.videos().delete(id=video_id).execute()

    print(f"Video {video_id} was rejected and deleted.")


if __name__ == "__main__":
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python reject.py <video_id>")
        sys.exit(1)

    reject_video(sys.argv[1])
