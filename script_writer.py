"""
SCRIPT WRITER
-------------
What this file does, in plain English:
    Takes a topic and asks Claude to write a short video script, plus
    helper functions that auto-suggest a visual search term, a music
    mood, and a narration voice.

How it fits in the pipeline:
    This is STEP 1. write_script's output gets handed to
    voice_generator.py next.

What you need for this to work:
    An Anthropic API key, saved in .env as ANTHROPIC_API_KEY.
"""

import os
import anthropic
from dotenv import load_dotenv
from script_history import get_past_scripts, save_script

load_dotenv()


def write_script(topic: str, target_seconds: int = 35) -> str:
    """
    Asks Claude to write a short narration script for a faceless video.

    Duplicate-content avoidance:
        Before writing, this checks script_history.py for any past
        scripts on this exact topic. If found, it tells Claude what's
        already been covered and asks for a different angle, so a
        topic that comes up again doesn't produce a near-identical
        video to one already posted.
    """

    target_words = int(target_seconds * 2.5)

    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    past_scripts = get_past_scripts(topic)

    if past_scripts:
        past_context = "\n\n---\n\n".join(past_scripts[:2])
        history_instructions = f"""

IMPORTANT: This topic has been covered before. Here are the most recent
script(s) already used - do NOT repeat the same facts, hook, or angle.
Find different specific facts, a different opening hook, and a different
overall angle on the topic:

{past_context}

---
"""
    else:
        history_instructions = ""

    prompt = f"""Write a short-form video narration script about: {topic}
{history_instructions}
Rules:
- Around {target_words} words total (this is a {target_seconds}-second video)
- Strong hook in the first sentence - something that makes someone stop scrolling
- Punchy, simple sentences. This will be read aloud by a text-to-speech voice.
- No stage directions, no scene labels, no emojis, no hashtags.
- Just return the narration text itself, nothing else.
- End with a small punchy closing line, not a generic summary.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    script_text = message.content[0].text.strip()

    save_script(topic, script_text)

    return script_text


def suggest_visual_search_term(topic: str) -> str:
    """
    Asks Claude for a short, visual, stock-footage-friendly search term
    for a given topic.
    """
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    prompt = f"""A short video is being made about this topic: {topic}

I need a search term to find background stock footage on a site like
Pexels. The topic itself might not have literal matching footage
(e.g. "bigfoot" has no real video of bigfoot) - in that case, suggest
a real, filmable visual that captures the mood or setting instead
(e.g. "foggy forest" or "dark woods").

If the topic DOES have literal real footage available (e.g. "ocean
facts", "volcanoes", "space"), just suggest a simple, direct search
term for that.

Rules:
- Respond with ONLY the search term itself, 1-4 words
- No punctuation, no explanation, no quotes
- It must describe something that genuinely exists as filmable stock footage
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )

    search_term = message.content[0].text.strip()
    return search_term


def suggest_music_mood(topic: str) -> str:
    """
    Asks Claude for a mood/genre keyword to search background music
    for, based on the video's topic.
    """
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    allowed_moods = [
        "dark", "ambient", "mysterious", "epic", "cinematic", "calm",
        "relaxing", "upbeat", "energetic", "dramatic", "suspense",
        "happy", "sad", "chill", "dreamy", "intense", "playful",
        "emotional", "inspiring", "horror", "eerie", "peaceful",
    ]

    prompt = f"""A short video is being made about this topic: {topic}

Pick the ONE word from this exact list that best fits the mood for
background music on this video:

{", ".join(allowed_moods)}

Rules:
- Respond with ONLY one word from that list, nothing else
- No punctuation, no explanation, no quotes
- Pick exactly one word, even if several could fit
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )

    mood = message.content[0].text.strip().lower()

    if mood not in allowed_moods:
        mood = "ambient"

    return mood


def suggest_voice(topic: str) -> str:
    """
    Asks Claude which narration voice fits the topic best, picked from
    our actual available voices.
    """
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    allowed_voices = [
        "male_us", "female_us", "male_uk", "female_uk",
        "male_us_v2", "female_us_v2", "female_us_warm",
    ]

    prompt = f"""A short narrated video is being made about this topic: {topic}

Pick the ONE voice option from this exact list that best fits the tone
of this video:

{", ".join(allowed_voices)}

Guidance on the options:
- male_us / female_us: standard, neutral American voices
- male_uk / female_uk: standard, neutral British voices
- male_us_v2 / female_us_v2: newer, more natural/expressive American voices
- female_us_warm: a warmer, friendlier American voice

Consider the topic's mood - e.g. a serious or eerie topic might suit a
calmer, more deliberate voice; a fun or upbeat topic might suit a
warmer or more energetic one.

Rules:
- Respond with ONLY one option from that list, nothing else
- No punctuation, no explanation, no quotes
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )

    voice = message.content[0].text.strip()

    if voice not in allowed_voices:
        voice = "male_us_v2"

    return voice


if __name__ == "__main__":
    test_topic = "weird ocean facts"
    print(f"Writing a script about: {test_topic}\n")
    result = write_script(test_topic)
    print("--- SCRIPT ---")
    print(result)