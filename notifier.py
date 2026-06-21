"""
NOTIFIER (ntfy)
----------------
What this file does, in plain English:
    Sends a push notification to your phone when a video is ready for
    you to review and approve, using ntfy.sh - a free notification
    service with no signup required. The notification includes a real,
    tappable "Approve & Publish" button.

How it fits in the pipeline:
    Called after a video has been generated and uploaded to YouTube as
    PRIVATE. You watch the video, and if you're happy with it, tap the
    button right in the notification - no computer needed.

How the approve button actually works:
    Tapping it sends an HTTP request directly from your phone to
    GitHub's API (a "repository_dispatch" event), which triggers the
    separate "Approve and Publish Video" workflow to run in the cloud.
    That workflow does the actual work of switching the video from
    private to public - your phone never talks to your computer at all.

What you need for this to work:
    - The free ntfy phone app, subscribed to a topic name of your
      choosing, saved in .env as NTFY_TOPIC
    - A GitHub Personal Access Token with "repo" scope, saved in .env
      as APPROVE_TRIGGER_TOKEN
"""

import os
import requests

NTFY_BASE = "https://ntfy.sh"
GITHUB_REPO = "ellipses-content/reel-pipeline"
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"


def notify_video_ready(video_title: str, video_url: str, video_id: str):
    """
    Sends a push notification that a video is ready for review, with a
    real tap-to-approve action button.
    """
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print("      [debug] No NTFY_TOPIC set in .env - skipping notification")
        return

    github_token = os.environ.get("APPROVE_TRIGGER_TOKEN")

    message = (
        f"\"{video_title}\" is ready to review.\n\n"
        f"Watch: {video_url}"
    )

    headers = {
        "Title": "Video ready for approval",
        "Priority": "default",
        "Tags": "movie_camera",
        "Click": video_url,
    }

    if github_token:
        action_body = (
            f'{{"event_type":"approve_video",'
            f'"client_payload":{{"video_id":"{video_id}"}}}}'
        )
        headers["Actions"] = (
            f"http, Approve & Publish, {GITHUB_DISPATCH_URL}, "
            f"method=POST, "
            f'headers.Authorization="Bearer {github_token}", '
            f"headers.Accept=application/vnd.github+json, "
            f'body=\'{action_body}\', clear=true'
        )
    else:
        message += (
            f"\n\nTo approve and publish, run:\n"
            f"python approve.py {video_id}"
        )

    try:
        requests.post(
            f"{NTFY_BASE}/{topic}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
        print(f"      Notification sent to your phone")
    except Exception as e:
        print(f"      [debug] Failed to send notification: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Sending a test notification...")
    notify_video_ready(
        "Test Video Title",
        "https://youtube.com/shorts/test123",
        "test123",
    )
    print("Check your phone!")
