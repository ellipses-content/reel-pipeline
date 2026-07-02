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


def _dispatch_action(label: str, event_type: str, video_id: str, github_token: str) -> dict:
    """
    Builds one ntfy 'http' action button that fires a GitHub
    repository_dispatch event (which triggers a workflow to act on the video).
    """
    return {
        "action": "http",
        "label": label,
        "url": GITHUB_DISPATCH_URL,
        "method": "POST",
        "headers": {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        },
        "body": (
            f'{{"event_type":"{event_type}",'
            f'"client_payload":{{"video_id":"{video_id}"}}}}'
        ),
        "clear": True,
    }


def notify_video_ready(video_title: str, video_url: str, video_id: str):
    """
    Sends a push notification that a video is ready for review, with real
    tap-to-act buttons: Approve & Publish (private -> public) and Reject
    (delete the private video).
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

    # ntfy is published as JSON so the notification can carry multiple action
    # buttons (the header form only reliably handles one complex http action).
    payload = {
        "topic": topic,
        "title": "Video ready for approval",
        "message": message,
        "priority": 3,
        "tags": ["movie_camera"],
        "click": video_url,
    }

    if github_token:
        payload["actions"] = [
            _dispatch_action("Approve & Publish", "approve_video", video_id, github_token),
            _dispatch_action("Reject & Delete", "reject_video", video_id, github_token),
        ]
    else:
        payload["message"] += (
            f"\n\nTo approve:  python approve.py {video_id}"
            f"\nTo reject:   python reject.py {video_id}"
        )

    try:
        requests.post(NTFY_BASE, json=payload, timeout=10)
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
