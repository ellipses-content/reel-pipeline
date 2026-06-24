"""
REAL IMAGE FINDER - Disabled
--------------------------------
Openverse was returning irrelevant images (memes, toys, random photos)
that didn't fit the cryptid horror theme. We now use only Pexels video
clips for visuals, which look much more atmospheric and cinematic.
"""

def find_real_images(topic: str, max_images: int = 6) -> list:
    """Returns empty list - Openverse disabled, using Pexels video only."""
    print("      [images] Skipping stock photos - using video clips only")
    return []