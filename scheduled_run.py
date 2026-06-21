"""
SCHEDULED RUN
--------------
What this file does, in plain English:
    This is the file Windows Task Scheduler will run automatically,
    twice a day. Each time it runs, it:
      1. Reads topics.txt
      2. Looks at topics_progress.txt to see which topic it used last
      3. Picks the NEXT topic in the list
      4. Runs the full pipeline on that topic
      5. Updates topics_progress.txt

What happens when the list runs out:
    Once all 60 topics have been used, it loops back to the start.

Usage (also runnable manually to test):
    python scheduled_run.py
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from make_reel import make_reel

TOPICS_FILE = "topics.txt"
PROGRESS_FILE = "topics_progress.txt"
LOG_FILE = "scheduled_run_log.txt"


def _load_topics() -> list:
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    topics = [
        line.strip() for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]
    return topics


def _get_next_topic_index(total_topics: int) -> int:
    if not os.path.exists(PROGRESS_FILE):
        return 0

    with open(PROGRESS_FILE, "r") as f:
        last_index = int(f.read().strip())

    next_index = (last_index + 1) % total_topics
    return next_index


def _save_progress(index: int):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))


def _log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def run_next_scheduled_video():
    load_dotenv()

    topics = _load_topics()
    if not topics:
        _log("ERROR: topics.txt is empty or missing - nothing to generate")
        return

    index = _get_next_topic_index(len(topics))
    topic = topics[index]

    _log(f"Starting scheduled run - topic #{index + 1}/{len(topics)}: '{topic}'")

    try:
        make_reel(topic)
        _save_progress(index)
        _log(f"Completed successfully: '{topic}'")
    except Exception as e:
        _log(f"FAILED on topic '{topic}': {e}")
        raise


if __name__ == "__main__":
    run_next_scheduled_video()