"""
TEST UPLOAD
-----------
A one-off script to test uploading a single, already-made video to
YouTube, separate from the main pipeline.

Usage:
    python test_upload.py
"""

from dotenv import load_dotenv
load_dotenv()

from youtube_uploader import upload_short

VIDEO_PATH = "output/bigfoot.mp4"
TITLE = "The Truth About Bigfoot"
DESCRIPTION = "The legend, the sightings, and the mystery that won't go away."

print(f"Uploading {VIDEO_PATH} to YouTube...")
url = upload_short(VIDEO_PATH, TITLE, DESCRIPTION)
print(f"\nDone! Your video is live at: {url}")