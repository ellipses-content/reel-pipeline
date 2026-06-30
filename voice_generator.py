"""
VOICE GENERATOR
----------------
What this file does, in plain English:
    Takes the script text (from script_writer.py) and turns it into an
    actual spoken audio file - a robot reading the script out loud,
    saved as an .mp3.

How it fits in the pipeline:
    This is STEP 2. It takes step 1's output (text) and produces audio,
    which gets handed to video_assembler.py next.

What you need for this to work:
    Nothing paid! This uses "edge-tts" - a free tool that uses the same
    voices Microsoft Edge's "Read Aloud" feature uses. No API key needed.
    Quality is genuinely decent for this kind of content, not robotic-90s.
"""

import asyncio
import re
import edge_tts


# A few good free voices to choose from. You can hear samples by searching
# "edge-tts voice list" - these are just a curated starting set.
VOICES = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-AriaNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_us_v2": "en-US-AndrewMultilingualNeural",
    "female_us_v2": "en-US-EmmaMultilingualNeural",
    "female_us_warm": "en-US-AvaMultilingualNeural",
}


# --- Horror tuning -----------------------------------------------------------
# These shape edge-tts delivery so it sounds like a tense late-night story
# instead of a flat read-aloud. Tweak by ear if a voice sounds off:
#   RATE  - speaking speed. Negative = slower/more deliberate (more dramatic).
#   PITCH - voice pitch in Hz. Negative = deeper/more ominous. Keep it subtle;
#           large shifts sound unnatural or "demonic".
RATE = "-8%"
PITCH = "-4Hz"


# A short sentence (this many words or fewer) is treated as a punchy beat
# and gets a weightier pause after it. Longer narrative sentences keep their
# natural pacing so the whole thing doesn't drag.
PUNCHY_MAX_WORDS = 5


def _add_dramatic_pauses(text: str) -> str:
    """
    Inserts short silent beats so the narration breathes at tense moments.

    edge-tts can't take SSML <break> tags, but it DOES pause on punctuation -
    and an ellipsis produces a longer, weightier pause than a period. We add
    those pauses only where drama lives: right after the opening hook, and
    after short punchy sentences (the scary one-liners). Normal-length
    sentences are left alone so the pacing doesn't drag. Ellipses are silent,
    so Whisper caption sync (which transcribes spoken words) is unaffected.
    """
    text = text.strip()
    if not text:
        return text

    # Split into sentences only at real boundaries: terminal punctuation
    # followed by whitespace and a capital letter. This deliberately does NOT
    # split inside abbreviations like "a.m.", "U.S.", or "Dr." because those
    # periods aren't followed by a space + capital.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return text

    out = []
    for i, body in enumerate(sentences):
        is_hook = (i == 0)
        is_punchy = len(body.split()) <= PUNCHY_MAX_WORDS
        is_last = (i == len(sentences) - 1)

        # Hook and punchy one-liners get a dramatic trailing pause; others
        # keep their normal punctuation. Never trail the final sentence.
        if (is_hook or is_punchy) and not is_last:
            out.append(re.sub(r"[.!?]+$", "...", body) if re.search(r"[.!?]$", body) else body + "...")
        else:
            out.append(body)

    text = " ".join(out)
    # Collapse any accidental run of dots (e.g. "....") to a clean ellipsis.
    text = re.sub(r"\.{4,}", "...", text)
    return text


async def _generate(text: str, voice: str, output_path: str):
    """
    The actual work happens here. This is 'async' (asynchronous) because
    edge-tts talks to a free Microsoft service over the internet, and
    waiting on network requests is what async code is good at.
    You don't need to understand async deeply - just know that
    generate_voiceover() below handles starting/stopping it for you.
    """
    communicator = edge_tts.Communicate(text, voice, rate=RATE, pitch=PITCH)
    await communicator.save(output_path)


def generate_voiceover(text: str, output_path: str, voice: str = "male_us") -> str:
    """
    Turns script text into a spoken .mp3 file.

    Inputs:
        text         - the script text to be spoken (from script_writer.py)
        output_path  - where to save the resulting .mp3, e.g. "temp/voice.mp3"
        voice        - which voice to use, picked from the VOICES dict above

    Output:
        The output_path string, so the next step knows where to find the file.
    """
    voice_id = VOICES.get(voice, VOICES["male_us"])
    spoken_text = _add_dramatic_pauses(text)
    asyncio.run(_generate(spoken_text, voice_id, output_path))
    return output_path


# Test block - only runs if you execute this file directly.
if __name__ == "__main__":
    sample_text = (
        "Did you know the ocean's deepest point is deeper than Everest is tall? "
        "The Mariana Trench plunges nearly seven miles down, into total darkness "
        "where the pressure could crush a car like a soda can."
    )
    print("Generating test voiceover...")
    path = generate_voiceover(sample_text, "temp/test_voice.mp3")
    print(f"Saved to: {path}")
