"""
SCRIPT WRITER
-------------
Takes a topic and asks Claude to write a scary, engaging narration
script for a cryptid/horror YouTube Short.
"""

import os
import anthropic
from dotenv import load_dotenv
from script_history import get_past_scripts, save_script

load_dotenv()


def write_script(topic: str, target_seconds: int = 60) -> str:
    target_words = int(target_seconds * 2.5)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    past_scripts = get_past_scripts(topic)

    if past_scripts:
        past_context = "\n\n---\n\n".join(past_scripts[:2])
        history_instructions = (
            "\n\nIMPORTANT: This topic has been covered before. Here are the most recent "
            "script(s) already used - do NOT repeat the same facts, hook, or angle. "
            "Find different specific facts, a different opening hook, and a different "
            "overall angle on the topic:\n\n"
            + past_context
            + "\n\n---\n"
        )
    else:
        history_instructions = ""

    prompt = (
        "You are writing a script for a horror and cryptozoology YouTube Shorts channel.\n"
        f"The topic is: {topic}\n"
        + history_instructions +
        "\nYour job is to write a script that feels like a late-night campfire story "
        "told by someone who actually believes it. Think Joe Rogan meets unsolved mysteries. "
        "Conversational, tense, and genuinely unsettling.\n\n"
        "STRUCTURE (follow this exactly):\n"
        "1. HOOK (first 1-2 sentences): Start mid-story or with a shocking specific detail "
        "that stops someone scrolling. NOT 'Have you heard of X?' - that's boring. "
        "Instead drop them INTO the story. "
        "Example: 'In 1966, a man drove home from work and saw something standing in the road. It had wings.'\n"
        "2. HISTORY & CONTEXT (middle section): Give real historical background - when it was first reported, "
        "where, what witnesses actually described. Include specific dates, places, and details. "
        "This is what makes it credible and interesting.\n"
        "3. ESCALATION: Build the tension - spread of sightings, patterns, what makes this creature unique and terrifying.\n"
        "4. CLOSING HOOK: End with an unresolved question or unsettling thought that makes them want to comment or rewatch. "
        "NOT a summary - a chill down the spine.\n\n"
        "WRITING RULES:\n"
        f"- Around {target_words} words total ({target_seconds} seconds when spoken)\n"
        "- Vary your sentence length - mix short punchy sentences with longer flowing ones for rhythm\n"
        "- Use sensory details - what did it smell like, sound like, feel like\n"
        "- Speak directly to the viewer occasionally ('imagine driving that road tonight')\n"
        "- NO stage directions, NO scene labels, NO emojis, NO hashtags\n"
        "- Return ONLY the narration text, nothing else\n"
        "- Make it genuinely scary and interesting - this should make someone's skin crawl\n"
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    script_text = message.content[0].text.strip()
    save_script(topic, script_text)
    return script_text


def suggest_visual_search_term(topic: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = (
        f"A short horror/cryptid video is being made about: {topic}\n\n"
        "I need a search term to find dark, atmospheric background stock footage on Pexels. "
        "The topic itself won't have literal matching footage - suggest a real, filmable "
        "visual that captures the mood or setting instead.\n\n"
        "Good examples:\n"
        "- Mothman -> foggy bridge night\n"
        "- Chupacabra -> dark desert night\n"
        "- Bigfoot -> misty forest\n"
        "- Sea Serpent -> stormy ocean waves\n\n"
        "Rules:\n"
        "- Respond with ONLY the search term itself, 1-4 words\n"
        "- No punctuation, no explanation, no quotes\n"
        "- Must be dark and atmospheric - this is a horror channel\n"
        "- It must describe something that genuinely exists as filmable stock footage\n"
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def suggest_music_mood(topic: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    allowed_moods = [
        "dark", "ambient", "mysterious", "epic", "cinematic", "calm",
        "relaxing", "upbeat", "energetic", "dramatic", "suspense",
        "happy", "sad", "chill", "dreamy", "intense", "playful",
        "emotional", "inspiring", "horror", "eerie", "peaceful",
    ]

    prompt = (
        f"A short horror/cryptid video is being made about: {topic}\n\n"
        "Pick the ONE word from this exact list that best fits the mood for background music:\n\n"
        + ", ".join(allowed_moods) +
        "\n\nRules:\n"
        "- Respond with ONLY one word from that list, nothing else\n"
        "- No punctuation, no explanation, no quotes\n"
        "- Pick exactly one word, even if several could fit\n"
        "- For cryptid/horror topics, prefer: dark, eerie, horror, mysterious, suspense\n"
    )

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
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    allowed_voices = [
        "male_us", "female_us", "male_uk", "female_uk",
        "male_us_v2", "female_us_v2", "female_us_warm",
    ]

    prompt = (
        f"A short horror/cryptid narrated video is being made about: {topic}\n\n"
        "Pick the ONE voice option from this exact list that best fits the tone:\n\n"
        + ", ".join(allowed_voices) +
        "\n\nGuidance:\n"
        "- male_us / female_us: standard, neutral American voices\n"
        "- male_uk / female_uk: standard, neutral British voices (great for serious/eerie content)\n"
        "- male_us_v2 / female_us_v2: newer, more natural/expressive American voices\n"
        "- female_us_warm: warmer, friendlier American voice\n\n"
        "For horror/cryptid content, prefer male_us_v2 or male_uk for a serious, authoritative tone.\n\n"
        "Rules:\n"
        "- Respond with ONLY one option from that list, nothing else\n"
        "- No punctuation, no explanation, no quotes\n"
    )

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
    test_topic = "Mothman"
    print(f"Writing a script about: {test_topic}\n")
    result = write_script(test_topic)
    print("--- SCRIPT ---")
    print(result)