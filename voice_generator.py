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


async def _generate(text: str, voice: str, output_path: str):
    """
    The actual work happens here. This is 'async' (asynchronous) because
    edge-tts talks to a free Microsoft service over the internet, and
    waiting on network requests is what async code is good at.
    You don't need to understand async deeply - just know that
    generate_voiceover() below handles starting/stopping it for you.
    """
    communicator = edge_tts.Communicate(text, voice)
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
    asyncio.run(_generate(text, voice_id, output_path))
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
