"""
VIDEO ASSEMBLER
----------------
What this file does, in plain English:
    Takes the voiceover audio + the background clips + the script text
    + optional background music, and stitches them into one finished
    vertical video with captions burned in, precisely synced to the
    actual audio using OpenAI's Whisper for word-level timestamps.

What you need for this to work:
    - moviepy (free, installed via pip)
    - ffmpeg (free, must be installed separately on your system)
    - openai-whisper (free, installed via pip) - used for caption sync
"""

import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
)

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


def _fit_to_frame(clip):
    clip_resized = clip.resize(height=TARGET_HEIGHT)
    if clip_resized.w < TARGET_WIDTH:
        clip_resized = clip.resize(width=TARGET_WIDTH)
    x_center = clip_resized.w / 2
    return clip_resized.crop(
        x1=x_center - TARGET_WIDTH / 2,
        x2=x_center + TARGET_WIDTH / 2,
        y1=0,
        y2=TARGET_HEIGHT,
    )


def _load_sources(video_paths: list, image_paths: list):
    sources = []
    for path in video_paths:
        clip = VideoFileClip(path)
        sources.append(_fit_to_frame(clip))
    for path in image_paths:
        clip = ImageClip(path, duration=10)
        sources.append(_fit_to_frame(clip))
    return sources


def _prepare_background(
    video_paths: list,
    image_paths: list,
    target_duration: float,
    cut_duration: float = 2.5,
):
    fitted_sources = _load_sources(video_paths, image_paths)

    if not fitted_sources:
        raise ValueError(
            "No background sources available - both video clips and "
            "images came back empty. Check your Pexels API key and "
            "internet connection."
        )

    num_segments = int(target_duration // cut_duration) + 1
    segments = []

    for i in range(num_segments):
        source = fitted_sources[i % len(fitted_sources)]
        reuse_count = i // len(fitted_sources)
        max_start = max(source.duration - cut_duration, 0)
        start_point = (reuse_count * 1.7) % (max_start + 0.01) if max_start > 0 else 0
        end_point = min(start_point + cut_duration, source.duration)
        segment = source.subclip(start_point, end_point)

        # Static zoom - dynamic resize lambdas cause 2D grayscale frame
        # crashes in MoviePy 1.0.3 during compositing, so we use a fixed
        # 5% zoom and crop instead.
        segment = segment.resize(1.05)
        segment = segment.crop(
            x_center=segment.w / 2,
            y_center=segment.h / 2,
            width=TARGET_WIDTH,
            height=TARGET_HEIGHT,
        )
        segments.append(segment)

    background = concatenate_videoclips(segments, method="compose")
    background = background.subclip(0, target_duration)
    return background


def _draw_caption_image(text: str, width: int) -> np.ndarray:
    font_size = 70
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, font_size)
            break
    if font is None:
        font = ImageFont.load_default()

    words = text.split()
    lines = []
    current_line = ""
    dummy_img = Image.new("RGBA", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy_img)

    for word in words:
        test_line = (current_line + " " + word).strip()
        bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width > width - 80 and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    line_height = font_size + 20
    img_height = line_height * len(lines) + 40
    img = Image.new("RGBA", (width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) / 2
        y = i * line_height + 20

        stroke_width = 3
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))

    return np.array(img.convert("RGB"))


def _get_word_timestamps(voiceover_path: str, script_text: str) -> list:
    try:
        import whisper
        print("      [captions] Running Whisper for precise caption sync...")
        model = whisper.load_model("base")
        result = model.transcribe(
            voiceover_path,
            word_timestamps=True,
            condition_on_previous_text=False,
        )

        words = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                word = word_info.get("word", "").strip()
                if word:
                    words.append({
                        "word": word,
                        "start": word_info["start"],
                        "end": word_info["end"],
                    })

        if words:
            print(f"      [captions] Got timestamps for {len(words)} words")
            return words

    except Exception as e:
        print(f"      [captions] Whisper failed ({e}), falling back to word-count estimate")

    return []


def _make_captions_from_timestamps(word_timestamps: list, max_words: int = 8):
    if not word_timestamps:
        return []

    caption_clips = []
    chunk_words = []
    chunk_start = None

    for i, wt in enumerate(word_timestamps):
        word = wt["word"]
        start = wt["start"]
        end = wt["end"]

        if chunk_start is None:
            chunk_start = start

        chunk_words.append(word)

        ends_sentence = any(p in word for p in [".", "!", "?", ","])
        is_last = i == len(word_timestamps) - 1
        at_max = len(chunk_words) >= max_words

        if ends_sentence or is_last or at_max:
            text = " ".join(chunk_words).strip()
            duration = max(end - chunk_start, 0.1)

            caption_image = _draw_caption_image(text, TARGET_WIDTH - 100)
            caption = (
                ImageClip(caption_image)
                .set_position(("center", "center"))
                .set_start(chunk_start)
                .set_duration(duration)
            )
            caption_clips.append(caption)
            chunk_words = []
            chunk_start = None

    return caption_clips


def _make_captions_fallback(script_text: str, target_duration: float):
    raw_pieces = re.split(r'(?<=[.!?,])\s+', script_text.strip())
    raw_pieces = [p.strip() for p in raw_pieces if p.strip()]

    chunks = []
    for piece in raw_pieces:
        words = piece.split()
        if len(words) <= 10:
            chunks.append(piece)
        else:
            for i in range(0, len(words), 10):
                chunks.append(" ".join(words[i:i + 10]))

    word_counts = [len(chunk.split()) for chunk in chunks]
    total_words = sum(word_counts)
    seconds_per_word = target_duration / total_words

    caption_clips = []
    current_time = 0.0
    for chunk, count in zip(chunks, word_counts):
        chunk_duration = count * seconds_per_word
        caption_image = _draw_caption_image(chunk, TARGET_WIDTH - 100)
        caption = (
            ImageClip(caption_image)
            .set_position(("center", "center"))
            .set_start(current_time)
            .set_duration(chunk_duration)
        )
        caption_clips.append(caption)
        current_time += chunk_duration

    return caption_clips


def assemble_video(
    voiceover_path: str,
    video_paths: list,
    script_text: str,
    output_path: str,
    image_paths: list = None,
    music_path: str = None,
) -> str:
    image_paths = image_paths or []

    voiceover = AudioFileClip(voiceover_path)
    duration = voiceover.duration

    background = _prepare_background(video_paths, image_paths, duration)

    word_timestamps = _get_word_timestamps(voiceover_path, script_text)
    if word_timestamps:
        captions = _make_captions_from_timestamps(word_timestamps)
    else:
        captions = _make_captions_fallback(script_text, duration)

    final_audio = voiceover
    if music_path and os.path.exists(music_path):
        music = AudioFileClip(music_path).volumex(0.12)
        if music.duration < duration:
            loops_needed = int(duration // music.duration) + 1
            music = concatenate_audioclips([music] * loops_needed)
        music = music.subclip(0, duration)
        final_audio = CompositeAudioClip([music, voiceover])

    final = CompositeVideoClip([background, *captions])
    final = final.set_audio(final_audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
    )

    return output_path