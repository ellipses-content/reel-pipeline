"""
SCRIPT HISTORY
---------------
What this file does, in plain English:
    Keeps a record of every script ever generated, organized by topic.
    This is what lets us tell Claude "here's what you already said
    about this topic - cover something different this time" whenever
    a topic comes up again.

How it fits in the pipeline:
    Called from script_writer.py. Before writing a new script, it
    checks history for past scripts on this topic. After writing a
    new script, it saves that script to history for next time.
"""

import json
import os

HISTORY_FILE = "script_history.json"


def get_past_scripts(topic: str) -> list:
    """
    Returns a list of past scripts written for this exact topic
    (case-insensitive match), most recent first. Returns an empty
    list if this topic has never been used before.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)

    topic_key = topic.strip().lower()
    entries = history.get(topic_key, [])

    return [entry["script"] for entry in reversed(entries)]


def save_script(topic: str, script: str):
    """
    Records a newly generated script under its topic, so future runs
    on the same topic can avoid repeating it.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {}

    topic_key = topic.strip().lower()
    if topic_key not in history:
        history[topic_key] = []

    history[topic_key].append({"script": script})
    history[topic_key] = history[topic_key][-5:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)