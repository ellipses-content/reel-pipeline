"""
NOTIFIER (ntfy)
----------------
What this file does, in plain English:
    Sends a push notification to your phone when a video is ready for
    you to review and approve, using ntfy.sh - a free notification
    service with no signup required.

How it fits in the pipeline:
    Called after a video has been generated and uploaded to YouTube as
    PRIVATE. This notifies you it's ready to watch, but does NOT make
    anything public by itself - approval is a separate step (approve.py).

Why approval is a separate script, not a button in the notification:
    ntfy's free hosted topics aren't fully private - anyone who knows
    your topic name could theoretically see notifications sent to it.
    To keep "make this video public" safely under your control, that
    action requires running a script on your own computer.

What you need for this to work:
    Nothing to sign up for! Just the free ntfy phone app, subscribed
    to a topic name of your choosing, saved in .env as NTFY_TOPIC.
"""

import os
import requests

NTFY_BASE = "https://ntfy.sh"


def notify_video_ready(video_title: str, video_url: str, video_id: str):
    """
    Sends a push notification that a video is ready for review.
    """
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print("      [debug] No NTFY_TOPIC set in .env - skipping notification")
        return

    message = (
        f"\"{video_title}\" is ready to review.\n\n"
        f"Watch: {video_url}\n\n"
        f"To approve and publish, run:\n"
        f"python approve.py {video_id}"
    )

    try:
        requests.post(
            f"{NTFY_BASE}/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": "Video ready for approval",
                "Priority": "default",
                "Tags": "movie_camera",
            },
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