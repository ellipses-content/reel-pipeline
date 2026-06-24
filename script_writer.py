"""
SCRIPT WRITER
-------------
What this file does, in plain English:
    Takes a topic (like "Mothman") and asks Claude to write a
    scary, engaging narration script for a cryptid/horror YouTube Short.

How it fits in the pipeline:
    This is STEP 1. Its output (a short block of text) gets handed to
    voice_generator.py next, which turns it into spoken audio.

What you need for this to work:
    An Anthropic API key (from console.anthropic.com), saved in a file
    called .env. This is the only paid piece in the whole pipeline,
    but a single script costs a fraction of a cent.
"""

import os
import anthropic
from dotenv import load_dotenv
from script_history import get_past_scripts, save_script

load_dotenv()


def write_script(topic: str, target_seconds: int = 60) -> str:
    """
    Asks Claude to write a short narration script for a faceless video.
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

    prompt = f"""You are writing a script for a horror and cryptozoology YouTube Shorts channel.
The topic is: {topic}
{history_instructions}
Your job is to write a script that feels like a late-night campfire story told by someone who actually believes it.
Think Joe Rogan meets unsolved mysteries. Conversational, tense, and genuinely unsettling.

STRUCTURE (follow this exactly):
1. HOOK (first 1-2 sentences): Start mid-story or with a shocking specific detail that stops someone scrolling.
   NOT "Have you heard of X?" - that's boring. Instead drop them INTO the story.
   Example: "In 1966, a man drove home from work and saw something standing in the road. It had wings."
2. HISTORY & CONTEXT (middle section): Give real historical background - when it was first reported,
   where, what witnesses actually described. Include specific dates, places, and details.
   This is what makes it credible and interesting.
3. ESCALATION: Build the tension - spread of sightings, patterns, what makes this creature unique and terrifying.
4. CLOSING HOOK: End with an unresolved question or unsettling thought that makes them want to comment or rewatch.
   NOT a summary - a chill down the spine.

WRITING RULES:
- Around {target_words} words total ({target_seconds} seconds when spoken)
- Vary your sentence length - mix short punchy sentences with longer flowing ones for rhythm
- Use sensory details - what did it smell like, sound like, feel like
- Speak directly to the viewer occasionally ("imagine driving that road tonight")
- NO stage directions, NO scene labels, NO emojis, NO hashtags
- Return ONLY the narration text, nothing else
- Make it genuinely scary and interesting - this should make someone's skin crawl
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    script_text = message.content[0].text.strip()

    save_script(topic, script_text)

    return script_text


def suggest_visual_search_term(topic: str) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    prompt = f"""A short horror/cryptid video is being made about: {topic}

I need a search term to find dark, atmospheric background stock footage on Pexels.
The topic itself won't have literal matching footage - suggest a real, filmable
visual that captures the mood or setting instead.

Good examples:
- Mothman -> "foggy bridge night"
- Chupacabra -> "dark desert night"
- Bigfoot -> "misty forest"
- Sea Serpent -> "stormy ocean waves"

Rules:
- Respond with ONLY the search term itself, 1-4 words
- No punctuation, no explanation, no quotes
- Must be dark and atmospheric - this is a horror channel
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
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    allowed_moods = [
        "dark", "ambient", "mysterious", "epic", "cinematic", "calm",
        "relaxing", "upbeat", "energetic", "dramatic", "suspense",
        "happy", "sad", "chill", "dreamy", "intense", "playful",
        "emotional", "inspiring", "horror", "eerie", "peaceful",
    ]

    prompt = f"""A short horror/cryptid video is being made about: {topic}

Pick the ONE word from this exact list that best fits the mood for background music:

{", ".join(allowed_moods)}

Rules:
- Respond with ONLY one word from that list, nothing else
- No punctuation, no explanation, no quotes
- Pick exactly one word, even if several could fit
- For cryptid/horror topics, prefer: dark, eerie, horror, mysterious,